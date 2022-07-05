#!/usr/bin/env python
"""
Uyuni helper functions
"""

import logging
from .uyuni import UyuniAPIClient
from .exceptions import SSLCertVerificationError

def get_host_id(target, api_client):
    """
    Ensures that a host ID is returned
    """
    if isinstance(target, int) or target.isdigit():
        return int(target)
    return api_client.get_host_id(target)


def _configure_connection(connection_params):
    """
    Configures API connection
    """
    # try to create API instance
    try:
        api_instance = UyuniAPIClient(
            logging.ERROR,
            connection_params.get('host'),
            connection_params.get('username'),
            connection_params.get('password'),
            port=connection_params.get('port'),
            verify=connection_params.get('verify_ssl')
        )
        return api_instance
    except SSLCertVerificationError as err:
        raise BaseException("Failed to verify SSL certificate") from err
    except Exception as err:
        raise BaseException("Failed to create API connection") from err
    return api_instance
