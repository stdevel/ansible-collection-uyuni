#!/usr/bin/python
"""
Ansible Module for managing system groups

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
module: system_group
short_description: Manage system group
description:
  - Manage system group
author:
  - "Christian Stankowic (@stdevel)"
extends_documentation_fragment:
  - stdevel.uyuni.uyuni_auth
options:
  name:
    description: Name of the system group
    required: True
    type: str
  description:
    description: Description of the system group
    required: True
    type: str
  admins:
    description: Admins to assign
    required: False
    type: list
    elements: str
  append_admins:
    description: Appends admins instead of replacing them
    type: bool
    default: False
  systems:
    description: Systems to assign
    required: False
    type: list
    elements: str
  append_systems:
    description: Appends systems instead of replacing them
    type: bool
    default: False
  config_channels:
    description: Defines configuration channels to use
    required: False
    type: list
    elements: str
  append_config_channels:
    description: Appends config channels instead of replacing them
    type: bool
    default: False
  state:
    description: Defines whether ressources should be created (present) or removed (absent)
    default: present
    choices:
      - present
      - absent
'''

EXAMPLES = '''
- name: Create system group
  stdevel.uyuni.system_group:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: debian-hosts
    description: Debian servers
    admins:
      - sgiertz
      - ppinkepank
    systems:
      - debsrv001
      - debsrv002
    config_channels:
      - base-configs

- name: Remove system group
  stdevel.uyuni.system_group:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: devuan-hosts
    state: absent
'''

RETURN = '''
entity:
  description: State whether system group was created, updated or removed
  returned: success
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import EmptySetException, SSLCertVerificationError, AlreadyExistsException
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

def _create_system_group(module, api_instance):
    """
    Creates a system group
    """
    try:
        api_instance.add_system_group(
          module.params.get('name'),
          module.params.get('description')
        )
        module.exit_json(changed=True)
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")
    except EmptySetException as err:
        module.fail_json(msg=f"Exception when calling UyuniAPI->create_system_group: {err}")

def _update_system_group(module, api_instance):
    """
    Update a system group
    """
    try:
        api_instance.update_system_group(
          module.params.get('name'),
          module.params.get('description')
        )
        module.exit_json(changed=True)
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")
    except EmptySetException as err:
        module.fail_json(msg=f"Exception when calling UyuniAPI->update_system_group: {err}")

def _remove_system_group(module, api_instance):
    """
    Removes a system group
    """
    try:
        api_instance.remove_system_group(
          module.params.get('name')
        )
        module.exit_json(changed=True)
    except EmptySetException:
      module.exit_json(changed=False)
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")
    except EmptySetException as err:
        module.fail_json(msg=f"Exception when calling UyuniAPI->remove_system_group: {err}")


def main():
    argument_spec = dict(
        uyuni_host=dict(required=True),
        uyuni_user=dict(required=True),
        uyuni_password=dict(required=True, no_log=True),
        uyuni_port=dict(default=443, type='int'),
        uyuni_verify_ssl=dict(default=True, type='bool'),
        name=dict(required=True),
        description=dict(required=True),
        admins=dict(required=False, type='list', elements='str'),
        append_admins=dict(default=False),
        systems=dict(required=False, type='list', elements='str'),
        append_systems=dict(default=False),
        config_channels=dict(required=False, type='list', elements='str'),
        append_config_channels=dict(default=False),
        state=dict(default='present', choices=['present', 'absent'])
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

    if module.params.get('state') == 'absent':
      # remove system group
      _remove_system_group(module, api_instance)

    # create/update system group
    try:
      _create_system_group(module, api_instance)
    except AlreadyExistsException:
      # update only if necessary
      _current = api_instance.get_system_group_details(
        module.params.get('name')
      )
      if _current['description'] != module.params.get('description'):
        _update_system_group(module, api_instance)

    # TODO: append/replace admins if requested
    # TODO: append/replace systems if requested
    # TODO: append/replace config channels if requested

    module.exit_json(changed=False)

if __name__ == '__main__':
    main()
