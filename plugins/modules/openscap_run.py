#!/usr/bin/python
"""
Ansible Module for scheduling OpenSCAP runs

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
module: openscap_run
short_description: Schedule OpenSCAP runs
description:
  - Schedule OpenSCAP runs
author:
  - "Christian Stankowic (@stdevel)"
extends_documentation_fragment:
  - stdevel.uyuni.uyuni_auth
options:
  name:
    description: Name or profile ID of the managed host
    required: True
    type: str
  document:
    description: XCCDF document path
    required: True
    type: str
  arguments:
    description: Command-line arguments
    type: str
'''

EXAMPLES = '''
- name: Check compliance
  stdevel.uyuni.openscap_run:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    document: /usr/share/openscap/scap-yast2sec-xccdf.xml
    arguments: --profile Default
'''

RETURN = '''
entity:
  description: State whether project was scheduled successfully
  returned: success
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import EmptySetException, SSLCertVerificationError
from ..module_utils.helper_functions import _configure_connection, get_host_id


def _schedule_openscap_run(module, api_instance):
    """
    Schedules an OpenSCAP run
    """
    try:
        # module.fail_json(msg="About to schedule OpenSCAP run")
        action_id = api_instance.schedule_openscap_run(
            get_host_id(
                module.params.get('name'),
                api_instance
            ),
            module.params.get('document'),
            module.params.get('arguments')
        )
        module.exit_json(changed=True, action_id=action_id)
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")
    except EmptySetException as err:
        module.fail_json(msg=f"Exception when calling UyuniAPI->schedule_openscap_run: {err}")


def main():
    """
    Main function
    """
    argument_spec = dict(
        uyuni_host=dict(required=True),
        uyuni_user=dict(required=True),
        uyuni_password=dict(required=True, no_log=True),
        uyuni_port=dict(default=443, type='int'),
        uyuni_verify_ssl=dict(default=True, type='bool'),
        name=dict(required=True),
        document=dict(type='str', required=True),
        arguments=dict(type='str')
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
    _schedule_openscap_run(module, api_instance)


if __name__ == '__main__':
    main()
