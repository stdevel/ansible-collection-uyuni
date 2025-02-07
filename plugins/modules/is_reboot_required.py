#!/usr/bin/python
"""
Ansible Module tp perform full package update on a managed host

2022 Christian Stankowic

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
module: is_reboot_required
short_description: Check if system requires reboot
description:
  - Check if a managed host needs to be rebooted!
author:
  - "Christian Stankowic (@stdevel)"
extends_documentation_fragment:
  - stdevel.uyuni.uyuni_auth
options:
  name:
    description: Name or profile ID of the managed host
    required: True
    type: str
'''

EXAMPLES = '''
- name: Check if system requires reboot
  stdevel.uyuni.is_reboot_required:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: server.localdomain.loc
'''

RETURN = '''
entity:
  description: State whether package host needs reboot or not
  returned: success
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import SSLCertVerificationError
from ..module_utils.helper_functions import _configure_connection, get_host_id

def _is_reboot_required(module, api_instance):
    """
    Check if host requires a reboot
    """
    try:
        # is reboot required
        reboot_required = api_instance.is_reboot_required(
            get_host_id(
                module.params.get('name'),
                api_instance
                )
      )
        if reboot_required is True:
            module.exit_json(changed=True, reboot_required=reboot_required)
        if reboot_required is False:
            module.exit_json(changed=False, reboot_required=reboot_required)
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")

def main():
    """
    Main functions
    """
    argument_spec = dict(
        uyuni_host=dict(required=True),
        uyuni_user=dict(required=True),
        uyuni_password=dict(required=True, no_log=True),
        uyuni_port=dict(default=443, type='int'),
        uyuni_verify_ssl=dict(default=True, type='bool'),
        name=dict(required=True)
    )

    module = AnsibleModule(argument_spec=argument_spec)

    connection_params = dict(
        host=module.params.get('uyuni_host'),
        username=module.params.get('uyuni_user'),
        password=module.params.get('uyuni_password'),
        port=module.params.get('uyuni_port'),
        verify_ssl=module.params.get('uyuni_verify_ssl')
    )

    api_instance = _configure_connection(connection_params)
    _is_reboot_required(module, api_instance)

if __name__ == '__main__':
    main()
