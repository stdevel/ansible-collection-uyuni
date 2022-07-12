#!/usr/bin/python
"""
Ansible Module for installing upgrades on a managed host

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
from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import EmptySetException, SSLCertVerificationError
from ..module_utils.helper_functions import _configure_connection, get_host_id, is_blocklisted

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: install_upgrades
short_description: Install upgrades
description:
  - Install upgrades (that aren't part of an patch) on a managed host
author:
  - "Christian Stankowic (@stdevel)"
extends_documentation_fragment:
  - stdevel.uyuni.uyuni_auth
options:
  name:
    description: Name or profile ID of the managed host
    required: True
    type: str
  include_upgrades:
    description: List of package names to install
    type: list
    elements: str
  exclude_upgrades:
    description: List of package names to exclude from installation
    type: list
    elements: str
'''

EXAMPLES = '''
- name: Reboot host
  stdevel.uyuni.install_upgrades:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: server.localdomain.loc
    exclude_upgrades:
      - kernel-default
'''

RETURN = '''
entity:
  description: State whether package installation was scheduled successfully
  returned: success
'''


def _install_upgrades(module, api_instance):
    """
    Installs upgrades on the host
    """
    # get parameters
    host = get_host_id(module.params.get('name'), api_instance)
    include_upgrades = module.params.get('include_upgrades')
    exclude_upgrades = module.params.get('exclude_upgrades')

    # bail out if both include/exclude patches is selected
    if include_upgrades and exclude_upgrades:
        module.fail_json(msg="Only supply include_upgrades OR exclude_upgrades")

    upgrades = []
    try:
        # get _all_ the upgrades
        all_upgrades = api_instance.get_host_upgrades(host)

        # exclude or include upgrades if defined
        if exclude_upgrades:
            for upgrade in all_upgrades:
                if not is_blocklisted(upgrade["name"], exclude_upgrades):
                    try:
                        upgrades.append(upgrade["package_id"])
                    except KeyError:
                        upgrades.append(upgrade["to_package_id"])

        elif include_upgrades:
            for upgrade in all_upgrades:
                # ignore the misleading function name here pls
                if is_blocklisted(upgrade["name"], include_upgrades):
                    try:
                        upgrades.append(upgrade["package_id"])
                    except KeyError:
                        upgrades.append(upgrade["to_package_id"])
        else:
            try:
                upgrades = [x["package_id"] for x in all_upgrades]
            except KeyError:
                upgrades = [x["to_package_id"] for x in all_upgrades]

        # install upgrades
        api_instance.install_upgrades(
            get_host_id(
                module.params.get('name'),
                api_instance
            ),
            upgrades
        )
        module.exit_json(changed=True)
    except EmptySetException as err:
        # exit if no upgrades available
        if not upgrades:
            module.exit_json(changed=False)
        # exit if invalid upgrade
        module.fail_json(msg=f"Upgrade(s) not found or applicable: {err}")
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")


def _main():
    argument_spec = dict(
        uyuni_host=dict(required=True),
        uyuni_user=dict(required=True),
        uyuni_password=dict(required=True, no_log=True),
        uyuni_port=dict(default=443, type='int'),
        uyuni_verify_ssl=dict(default=True, type='bool'),
        name=dict(required=True),
        include_upgrades=dict(type='list', elements='str'),
        exclude_upgrades=dict(type='list', elements='str')
    )

    module = AnsibleModule(argument_spec=argument_spec)

    module_params = dict(
        host=module.params.get('uyuni_host'),
        username=module.params.get('uyuni_user'),
        password=module.params.get('uyuni_password'),
        port=module.params.get('uyuni_port'),
        verify_ssl=module.params.get('uyuni_verify_ssl'),
        include_upgrades=module.params.get('include_upgrades'),
        exclude_upgrades=module.params.get('exclude_upgrades')
    )

    api_instance = _configure_connection(module_params)
    _install_upgrades(module, api_instance)


if __name__ == '__main__':
    _main()
