# (C) 2024 Fujitsu Limited

import base64
import hashlib
import hmac
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Optional

import requests
from botocore.exceptions import ClientError
from filelock import BaseFileLock, FileLock
from requests.auth import AuthBase

from fujitsu_quantum import aws_utils
from fujitsu_quantum.config import Config
from fujitsu_quantum.utils import json_dumps


class AuthType(str, Enum):
    NONE = "NONE"
    """No authentication"""

    FQC = "FQC"
    """Authentication for the Fujitsu Quantum Cloud APIs with FQCAuth"""


class FQCAuthError(Exception):
    @property
    def msg(self) -> str:
        return self.args[0]


class FQCAuth(ABC, AuthBase):
    CREDENTIALS_DIR: str = Config.config_dir
    CREDENTIALS_FILE_NAME: str = "credentials.json"
    CREDENTIALS_FILE_PATH: Path = Path(f'{Config.config_dir}/{CREDENTIALS_FILE_NAME}')
    CREDENTIALS_FILE_LOCK_PATH: Path = CREDENTIALS_FILE_PATH.with_suffix(CREDENTIALS_FILE_PATH.suffix + ".lock")
    TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    def __init__(self) -> None:
        self._load_credentials()

    @staticmethod
    def store_credentials(client_id: str,
                          username: str,
                          access_token: str,
                          access_token_expiration_time: datetime,
                          refresh_token: str,
                          refresh_token_expiration_time: datetime,
                          device_key: Optional[str]) -> None:

        if not os.path.exists(FQCAuth.CREDENTIALS_DIR):
            os.makedirs(FQCAuth.CREDENTIALS_DIR)

        try:
            lock = FileLock(FQCAuth.CREDENTIALS_FILE_LOCK_PATH)
            with lock:
                with os.fdopen(
                    os.open(FQCAuth.CREDENTIALS_FILE_PATH, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w"
                ) as cred_json_file:
                    cred_json = {
                        "ClientId": client_id,
                        "Username": username,
                        "AccessToken": access_token,
                        "AccessTokenExpirationTime": access_token_expiration_time.strftime(FQCAuth.TIME_FORMAT),
                        "RefreshToken": refresh_token,
                        "RefreshTokenExpirationTime": refresh_token_expiration_time.strftime(FQCAuth.TIME_FORMAT),
                    }

                    if device_key is not None:
                        cred_json["DeviceKey"] = device_key

                    cred_json_file.write(json_dumps(cred_json, indent=4))
        except FileNotFoundError:
            raise FQCAuthError(f"Unable to open credentials file lock: {FQCAuth.CREDENTIALS_FILE_LOCK_PATH}")

    def _read_credential_file(self, parent_lock: Optional[BaseFileLock] = None) -> Dict[str, str]:
        try:
            lock = parent_lock
            if lock is None:
                lock = FileLock(FQCAuth.CREDENTIALS_FILE_LOCK_PATH)

            with lock:
                try:
                    with open(self.CREDENTIALS_FILE_PATH, 'r') as cred_json_file:
                        return json.load(cred_json_file)

                except FileNotFoundError:
                    raise FQCAuthError(
                        "Credentials not found."
                        " Please run `fujitsu-quantum login` to configure credentials.",
                    )

                except json.JSONDecodeError:
                    raise FQCAuthError("The credential data is corrupted."
                                       " Please run `fujitsu-quantum login` to configure credentials.")

        except FileNotFoundError:
            raise FQCAuthError(f"Unable to open credentials file lock: {FQCAuth.CREDENTIALS_FILE_LOCK_PATH}")

    def _load_credentials(self, parent_lock: Optional[BaseFileLock] = None) -> None:
        cred_json = self._read_credential_file(parent_lock)
        try:
            self._client_id: str = cred_json["ClientId"]
            self._username: str = cred_json["Username"]
            self._access_token: str = cred_json["AccessToken"]
            self._access_token_expiration_time: datetime = datetime.strptime(cred_json["AccessTokenExpirationTime"],
                                                                             FQCAuth.TIME_FORMAT)
            self._refresh_token: str = cred_json["RefreshToken"]
            self.refresh_token_expiration_time: datetime = datetime.strptime(cred_json["RefreshTokenExpirationTime"],
                                                                             FQCAuth.TIME_FORMAT)
            self._device_key: Optional[str] = cred_json.get("DeviceKey", None)
        except KeyError:
            raise FQCAuthError("The credentials are outdated."
                               " Please run `fujitsu-quantum login` to update the credentials.")

    @abstractmethod
    def refresh_auth(self, force: bool = False) -> None:
        raise NotImplementedError()

    def __call__(self, r: requests.PreparedRequest) -> requests.PreparedRequest:
        r.headers["authorization"] = "Bearer " + self._access_token
        return r

    def update_authorization_header(self, r: requests.PreparedRequest):
        r.headers["authorization"] = "Bearer " + self._access_token


class FQCAuthBoto3(FQCAuth):
    # TODO some error handling
    def refresh_auth(self, force: bool = False) -> None:
        """
        Refreshes the access token.
        If there is still time before the access token expires, this method does not refresh the access token to avoid
        excessive token refresh requests.
        """
        try:
            lock = FileLock(FQCAuth.CREDENTIALS_FILE_LOCK_PATH)
            with lock:
                if not force:
                    # Other threads or processes may have updated the credential file; it should reload the file.
                    self._load_credentials(lock)
                    if self._access_token_expiration_time - datetime.now() > timedelta(minutes=10):
                        return

                # refresh the access token with the refresh token
                client = aws_utils.get_client("cognito-idp", region_name="ap-northeast-1")

                new_hmac = hmac.new(bytes(self._username + self._client_id, "utf-8"),
                                    digestmod=hashlib.sha256).digest()
                secret_hash = base64.b64encode(new_hmac).decode()

                auth_params = {
                    "USERNAME": self._username,
                    "SECRET_HASH": secret_hash,
                    "REFRESH_TOKEN": self._refresh_token,
                }

                if self._device_key is not None:
                    auth_params["DEVICE_KEY"] = self._device_key

                try:
                    current_time = datetime.now()
                    response = client.initiate_auth(
                        ClientId=self._client_id,
                        AuthFlow="REFRESH_TOKEN_AUTH",
                        AuthParameters=auth_params,
                    )
                    self._access_token = response["AuthenticationResult"]["AccessToken"]
                    access_token_expires_in = response["AuthenticationResult"]["ExpiresIn"]
                    self._access_token_expiration_time = current_time + timedelta(seconds=access_token_expires_in)
                except ClientError as e:
                    if e.response["Error"]["Code"] == 'NotAuthorizedException':
                        raise FQCAuthError('The credentials have expired.'
                                           ' Please run `fujitsu-quantum login` to update the credentials.')
                    else:
                        raise e

                # update the credentials file
                cred_json = self._read_credential_file(lock)
                cred_json["AccessToken"] = self._access_token
                cred_json["AccessTokenExpirationTime"] = \
                    self._access_token_expiration_time.strftime(FQCAuth.TIME_FORMAT)
                with open(self.CREDENTIALS_FILE_PATH, "w") as cred_json_file:
                    cred_json_file.write(json_dumps(cred_json, indent=4))

        except FileNotFoundError:
            raise FQCAuthError(f"Unable to open credentials file lock: {FQCAuth.CREDENTIALS_FILE_LOCK_PATH}")

    def logout(self) -> None:
        client = aws_utils.get_client("cognito-idp", region_name="ap-northeast-1")
        client.revoke_token(Token=self._refresh_token, ClientId=self._client_id)
