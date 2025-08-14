#!/usr/bin/python
"""
Ansible Module for applying a host's highstate

2025 Christian Stankowic

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
module: apply_highstate
short_description: Apply a host's highstate
description:
  - Apply a host's highstate
author:
  - "Christian Stankowic (@stdevel)"
extends_documentation_fragment:
  - stdevel.uyuni.uyuni_auth
options:
  name:
    description: Name or profile ID of the managed host
    required: True
    type: str
  test_mode:
    description: Only simulate applying the highstate
    required: False
    type: bool
    default: False
'''

EXAMPLES = '''
- name: Apply highstate
  stdevel.uyuni.apply_highstate:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: server.localdomain.loc

- name: Simulate applying highstate
  stdevel.uyuni.apply_highstate:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: server.localdomain.loc
    test_mode: true
'''

RETURN = '''
entity:
  description: State whether highstate was scheduled successfully
  returned: success
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import EmptySetException, SSLCertVerificationError
from ..module_utils.helper_functions import _configure_connection, get_host_id


def _apply_highstate(module, api_instance):
    """
    Applies a host's highstate
    """
    try:
        action_id = api_instance.apply_highstate(
            get_host_id(
                module.params.get('name'),
                api_instance
            ),
            module.params.get('test_mode')
        )
        module.exit_json(changed=True, action_id=action_id)
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")
    except EmptySetException as err:
        module.fail_json(msg=f"Exception when calling UyuniAPI->apply_highstate: {err}")


def main():
    """
    Default function, calls module
    """
    argument_spec = dict(
        uyuni_host=dict(required=True),
        uyuni_user=dict(required=True),
        uyuni_password=dict(required=True, no_log=True),
        uyuni_port=dict(default=443, type='int'),
        uyuni_verify_ssl=dict(default=True, type='bool'),
        name=dict(required=True),
        test_mode=dict(default=False, type='bool')
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
    _apply_highstate(module, api_instance)


if __name__ == '__main__':
    main()
