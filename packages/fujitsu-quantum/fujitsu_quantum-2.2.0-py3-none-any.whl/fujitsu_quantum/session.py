import os
import threading
from functools import lru_cache
from http import HTTPStatus

from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from fujitsu_quantum.auth import AuthType, FQCAuthBoto3
from fujitsu_quantum.config import Config

_RETRY_STATUS_FORCE_LIST = [429, 500, 502, 503, 504]


# requests.Session is not process-safe and not thread-safe.
# To create a process/thread-local session object, this function is decorated by lru_cache.
@lru_cache
def _get_session(pid: int, thread_id: int, auth_type: AuthType) -> Session:
    session = Session()

    # TODO allow users to change the retry parameters via the config file
    # The values of backoff_max and backoff_factor are consistent with the boto3 standard retry mode
    retries = Retry(total=Config.retry_max_attempts, backoff_factor=0.5, backoff_max=20,
                    allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "POST"],
                    status_forcelist=_RETRY_STATUS_FORCE_LIST,
                    raise_on_status=False)
    session.mount('https://', HTTPAdapter(max_retries=retries))

    if auth_type == AuthType.FQC:
        auth = FQCAuthBoto3()
        session.auth = auth

        def _refresh_auth_hook(r: Response, *args, **kwargs):
            if r.status_code == HTTPStatus.UNAUTHORIZED:
                auth.refresh_auth()
                auth.update_authorization_header(r.request)

                # Because session.send(...) does not respect the environment variables, we need to manually merge it.
                # https://requests.readthedocs.io/en/latest/user/advanced/#prepared-requests
                settings = session.merge_environment_settings(r.request.url,
                                                              proxies={}, stream=None, verify=None, cert=None)
                r = session.send(r.request, **settings)

            return r

        session.hooks['response'].append(_refresh_auth_hook)

    return session


def get_session(auth_type: AuthType = AuthType.NONE) -> Session:
    return _get_session(os.getpid(), threading.get_ident(), auth_type)
