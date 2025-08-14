"""
Uyuni helper functions
"""

from __future__ import (absolute_import, division, print_function)
import logging
from .uyuni import UyuniAPIClient
from .exceptions import SSLCertVerificationError
__metaclass__ = type


def get_host_id(target, api_client):
    """
    Ensures that a host ID is returned
    """
    if isinstance(target, int) or target.isdigit():
        return int(target)
    return api_client.get_host_id(target)


def get_patch_id(patch, api_client):
    """
    Ensure that a patch ID is returned
    """
    if isinstance(patch, int) or patch.isdigit():
        return int(patch)
    return api_client.get_patch_by_name(patch)


def patch_already_installed(system_id, patches, api_client):
    """
    Checks whether specific patches are already installed
    """
    # get recently installed patches
    _installed = [x['id'] for x in get_recently_installed_patches(system_id, api_client)]
    # check if patches aren't installed
    for patch in patches:
        if patch not in _installed:
            return False
    return True


def get_recently_installed_patches(system_id, api_client):
    """
    Get all recently installed patches
    """
    # find already installed errata by searching actions
    actions = api_client.get_host_actions(
        system_id
    )
    errata = [
        x["additional_info"][0]["detail"].split(' ', 1)[0] for x in actions
        if ("name" in x
            and "patch update" in x["name"].lower()
            and x["successful_count"] == 1)
    ]
    # return errata IDs
    return [api_client.get_patch_by_name(x) for x in errata]


def is_blocklisted(upgrade: str, blacklist: list):
    """
    This function checks whether a patch is matched by an exclude pattern

    :param upgrade: Hostname
    :type upgrade: str
    :param blacklist: List of blacklisted terms
    :type blacklist: [str, ]
    """
    return any(entry in upgrade for entry in blacklist)


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
        raise BaseException(f"Failed to create API connection: {err}") from err
    return api_instance


def get_outdated_pkgs(target, api_client):
    """
    Ensures that a number of outdated packages is returned
    """
    if isinstance(target, int) or target.isdigit():
        return int(target)
    return api_client.get_outdated_pkgs(target)
