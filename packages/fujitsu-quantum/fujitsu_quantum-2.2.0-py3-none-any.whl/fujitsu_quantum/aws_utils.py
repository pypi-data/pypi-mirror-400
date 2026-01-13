# (C) 2024 Fujitsu Limited

import os
from typing import Any, Dict

import boto3
from botocore.client import BaseClient
from botocore.config import Config

from fujitsu_quantum.config import Config as FQCConfig


def add_aws_link_local_address_to_no_proxy():
    # AWS SDK tries to connect http://169.254.169.254/** to retrieve metadata.
    # 169.254.169.254 is a link-local address and must be accessed with no proxies.
    # https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-proxy.html#cli-configure-proxy-ec2
    aws_link_local_address = '169.254.169.254'

    original_no_proxy = None
    env_name_is_lowercase = True
    if 'no_proxy' in os.environ:
        original_no_proxy = os.environ['no_proxy']
    elif 'NO_PROXY' in os.environ:
        original_no_proxy = os.environ['NO_PROXY']
        env_name_is_lowercase = False

    if original_no_proxy is None:
        os.environ['no_proxy'] = aws_link_local_address
    else:
        no_proxies = [address.strip() for address in original_no_proxy.split(',')]
        if aws_link_local_address not in no_proxies:
            if env_name_is_lowercase:
                os.environ['no_proxy'] = f'{original_no_proxy},{aws_link_local_address}'
            else:
                os.environ['NO_PROXY'] = f'{original_no_proxy},{aws_link_local_address}'

    return {'original_no_proxy': original_no_proxy, 'env_name_is_lowercase': env_name_is_lowercase}


def restore_no_proxy(original_no_proxy_config: Dict[str, Any]) -> None:
    original_no_proxy = original_no_proxy_config['original_no_proxy']
    env_name_is_lowercase = original_no_proxy_config['env_name_is_lowercase']
    if original_no_proxy is None:
        del os.environ['no_proxy']
    else:
        if env_name_is_lowercase:
            os.environ['no_proxy'] = original_no_proxy
        else:
            os.environ['NO_PROXY'] = original_no_proxy


def get_client(*args, **kwargs) -> BaseClient:
    # AWS SDK requires a special setting of 'no_proxy'
    add_aws_link_local_address_to_no_proxy()

    if 'config' in kwargs:
        raise ValueError('get_client(...) does not allow to specify the "config" parameter.')

    config = Config(
        connect_timeout=FQCConfig.connect_timeout,
        read_timeout=FQCConfig.read_timeout,
        retries={
            'max_attempts': FQCConfig.retry_max_attempts,
            'mode': 'standard'
        }
    )
    client = boto3.client(*args, **kwargs, config=config)
    return client
