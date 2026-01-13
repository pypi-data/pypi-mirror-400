# (C) 2024 Fujitsu Limited

import dataclasses
import os
from pathlib import Path
from typing import Optional

import pyjson5


@dataclasses.dataclass
class _Config:
    config_dir: str
    config_file_name: str
    auth_pool_id: str
    auth_sdk_client_id: str
    api_base: str
    result_polling_interval: float
    retry_max_attempts: int
    connect_timeout: float
    read_timeout: float
    in_hybrid_env: bool
    internal_api_server: Optional[str]
    internal_api_token: Optional[str]
    local_storage_dir: Optional[str]
    hybrid_task_id: Optional[str]


def load_config() -> _Config:
    env_home = os.environ.get('FUJITSU_QUANTUM_HOME', None)
    if env_home is None:
        config_dir = Path.home() / '.fujitsu-quantum'
    else:
        config_dir = Path(env_home).absolute()

    config_file_path = config_dir / 'config.json'

    if config_file_path.exists():
        with open(config_file_path, "r", encoding='utf-8') as f:
            conf_data = pyjson5.decode_io(f)

        if not isinstance(conf_data, dict):
            raise ValueError(f"Invalid config file: {config_file_path}")

        conf = conf_data
    else:
        conf = {}

    available_keys = {'authPoolId', 'authSdkClientId', 'apiBase', 'resultPollingInterval', 'retryMaxAttempts',
                      'connectTimeout', 'readTimeout'}
    invalid_keys = conf.keys() - available_keys
    if invalid_keys:
        raise ValueError(f'Invalid parameter names in config.json: {invalid_keys}\n'
                         f'config.json path: {config_file_path}')

    # validate the config values
    result_polling_interval = conf.get('resultPollingInterval', 1.0)
    if (not isinstance(result_polling_interval, (int, float))) or (result_polling_interval < 1):
        raise ValueError('Invalid value in config.json: '
                         'resultPollingInterval must be a real number greater than or equal to 1, '
                         f'but {result_polling_interval} is specified.\n'
                         f'config.json path: {config_file_path}')
    result_polling_interval = float(result_polling_interval)

    retry_max_attempts = conf.get('retryMaxAttempts', 5)
    if (not isinstance(retry_max_attempts, int)) or (retry_max_attempts < 0):
        raise ValueError('Invalid value in config.json: '
                         'retryMaxAttempts must be a positive integer, '
                         f'but {retry_max_attempts} is specified.\n'
                         f'config.json path: {config_file_path}')

    connect_timeout = conf.get('connectTimeout', 5.0)
    if (not isinstance(connect_timeout, (int, float))) or (connect_timeout < 0):
        raise ValueError('Invalid value in config.json: '
                         'connectTimeout must be a positive floating-point number, '
                         f'but {connect_timeout} is specified.\n'
                         f'config.json path: {config_file_path}')

    read_timeout = conf.get('readTimeout', 5.0)
    if (not isinstance(read_timeout, (int, float))) or (read_timeout < 0):
        raise ValueError('Invalid value in config.json: '
                         'read_timeout must be a positive floating-point number, '
                         f'but {read_timeout} is specified.\n'
                         f'config.json path: {config_file_path}')

    hybrid_config_file = config_dir / 'hybrid-config.json'
    if hybrid_config_file.exists():
        in_hybrid_env = True
        with open(hybrid_config_file, "r") as f:
            hybrid_config = pyjson5.load(f)
    else:
        in_hybrid_env = False
        hybrid_config = {}

    return _Config(
        config_dir=str(config_dir),
        config_file_name=config_file_path.name,
        auth_pool_id=conf.get('authPoolId', 'ap-northeast-1_oUVGkT61e'),
        auth_sdk_client_id=conf.get('authSdkClientId', '66l8iadggtteljctngjepi8du0'),
        api_base=conf.get('apiBase', 'https://api.quantum.global.fujitsu.com'),
        result_polling_interval=result_polling_interval,
        retry_max_attempts=retry_max_attempts,
        connect_timeout=connect_timeout,
        read_timeout=read_timeout,
        in_hybrid_env=in_hybrid_env,
        internal_api_server=hybrid_config.get('internalAPIServer', None),
        internal_api_token=hybrid_config.get('internalAPIToken', None),
        local_storage_dir=hybrid_config.get('localStorageDir', None),
        hybrid_task_id=hybrid_config.get('hybridTaskId', None),
    )


Config = load_config()
