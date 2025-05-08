#!/usr/bin/python
"""
Ansible Module to perform full package update on a managed host

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
module: full_pkg_update
short_description: Perform full package update
description:
  - Perform full package update on a managed host without any exceptions!
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
- name: Perform full package update
  stdevel.uyuni.full_pkg_update:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: server.localdomain.loc
'''

RETURN = '''
entity:
  description: State whether package installation was scheduled successfully
  returned: success
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import EmptySetException, SSLCertVerificationError
from ..module_utils.helper_functions import _configure_connection, get_host_id, get_outdated_pkgs

def _full_pkg_update(module, api_instance):
    """
    Performs full package update on host
    """
    # get host id
    host = get_host_id(module.params.get('name'), api_instance)
    # is reboot required
    reboot_req = api_instance.is_reboot_required(host)
    if reboot_req is True:
        module.fail_json(msg="Cannot install updates. Host must be rebooted first.")
    # get number of outdated packages
    upgrades = get_outdated_pkgs(module.params.get('name'), api_instance)
    if upgrades == 0:
        module.exit_json(changed=False)
    try:
        # install upgrades
        action_id = api_instance.full_pkg_update(
            get_host_id(
                module.params.get('name'),
                api_instance
                )
      )
        # wait for all packages to be updated
        api_instance.wait_for_action(action_id, host)
        module.exit_json(changed=True, installed_updates=upgrades)
    except EmptySetException as err:
        # exit if no upgrades available
        if not upgrades:
            module.exit_json(changed=False)
        # exit if invalid upgrade
        module.fail_json(msg=f"Upgrade(s) not found or applicable: {err}")
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

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False
    )

    module_params = dict(
        host=module.params.get('uyuni_host'),
        username=module.params.get('uyuni_user'),
        password=module.params.get('uyuni_password'),
        port=module.params.get('uyuni_port'),
        verify_ssl=module.params.get('uyuni_verify_ssl')
    )

    api_instance = _configure_connection(module_params)
    _full_pkg_update(module, api_instance)

if __name__ == '__main__':
    main()
