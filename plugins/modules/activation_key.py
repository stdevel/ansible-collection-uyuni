#!/usr/bin/python
"""
Ansible Module for managing activation keys

2023 Christian Stankowic

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: activation_key
short_description: Manage activation key
description:
  - Manage activation key
author:
  - "Christian Stankowic (@stdevel)"
extends_documentation_fragment:
  - stdevel.uyuni.uyuni_auth
options:
  name:
    description: Name of the activation key
    required: True
    type: str
  description:
    description: Description of the activation key
    required: True
    type: str
  base_channel:
    description: Software base channel to assign
    required: True
    type: str
  child_channels:
    description: Child channels to assign
    required: False
    type: list
    elements: str
  contact_method:
    description: System contact method
    required: True
    type: str
    default: default
    choices:
      - default
      - ssh-push
      - ssh-push-tunnel
  config_channels:
    description: Configuration channels to assign
    required: False
    type: list
    elements: str
  entitlements:
    description: Entitlements to assign
    required: False
    type: list
    elements: str
    choices:
      - container_build_host
      - monitoring_entitled
      - osimage_build_host
      - virtualization_host
      - ansible_control_node
  packages:
    description: Packages to install
    required: False
    type: list
    elements: str
  hostgroups:
    description: Hostgroups to assign
    required: False
    type: list
    elements: str
  limit:
    description: Usage limit
    required: False
    type: int
  universal_default:
    description: Define as universal default
    required: False
    type: bool
'''

EXAMPLES = '''
- name: Create activation key
  stdevel.uyuni.activation_key:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: 1-ak-debian11
    base_channel: debian-11-pool-amd64-uyuni
    child_channels:
      - debian-11-amd64-main-updates-uyuni
      - debian-11-amd64-main-security-uyuni
      - debian-11-amd64-uyuni-client
    packages: neofetch
    hostgroups:
      - Debian
      - Test
'''

RETURN = '''
entity:
  description: State whether activation key was created, updated or removed
  returned: success
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import EmptySetException, SSLCertVerificationError
from ..module_utils.helper_functions import _configure_connection, get_host_id


# def _reboot_host(module, api_instance):
#     """
#     Reboots the host
#     """
#     try:
#         api_instance.reboot_host(
#             get_host_id(
#                 module.params.get('name'),
#                 api_instance
#             )
#         )
#         module.exit_json(changed=True)
#     except SSLCertVerificationError:
#         module.fail_json(msg="Failed to verify SSL certificate")
#     except EmptySetException as err:
#         module.fail_json(msg=f"Exception when calling UyuniAPI->reboot_host: {err}")


def main():
    argument_spec = dict(
        uyuni_host=dict(required=True),
        uyuni_user=dict(required=True),
        uyuni_password=dict(required=True, no_log=True),
        uyuni_port=dict(default=443, type='int'),
        uyuni_verify_ssl=dict(default=True, type='bool'),
        name=dict(required=True),
        description=dict(required=True),
        base_channel=dict(required=True),
        child_channels=dict(required=False, type='list', elements='str'),
        contact_method=dict(required=True, type='str', choices=['default', 'ssh-push', 'ssh-push-tunnel']),
        config_channels=dict(required=False, type='list', elements='str'),
        entitlements=dict(required=False, type='list', elements='str', choices=['container_build_host', 'monitoring_entitled', 'osimage_build_host', 'virtualization_host', 'ansible_control_node']),
        packages=dict(required=False, type='list', elements='str'),
        hostgroups=dict(required=False, type='list', elements='str'),
        limit=dict(required=False, type='int'),
        universal_default=dict(required=False, type='bool')
    )

    module = AnsibleModule(
      argument_spec=argument_spec,
      supports_check_mode=False
    )

    connection_params = dict(
        host=module.params.get('uyuni_host'),
        username=module.params.get('uyuni_user'),
        password=module.params.get('uyuni_password'),
        port=module.params.get('uyuni_port'),
        verify_ssl=module.params.get('uyuni_verify_ssl')
    )

    api_instance = _configure_connection(connection_params)
    # TODO: create, update or remove activation key
    #_create_activationkey(module, api_instance)
    #_update_activationkey(module, api_instance)
    #_remove_activationkey(module, api_instance)


if __name__ == '__main__':
    main()
