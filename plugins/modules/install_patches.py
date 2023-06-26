#!/usr/bin/python
"""
Ansible Module for installing patches on a managed host

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
module: install_patches
short_description: Install patches
description:
  - Install patches on a managed host
author:
  - "Christian Stankowic (@stdevel)"
extends_documentation_fragment:
  - stdevel.uyuni.uyuni_auth
options:
  name:
    description: Name or profile ID of the managed host
    required: True
    type: str
  include_patches:
    description: List of patch names or IDs to install
    type: list
    elements: str
  exclude_patches:
    description: List of patch names or IDs to exclude from installation
    type: list
    elements: str
'''

EXAMPLES = '''
- name: Install patches
  stdevel.uyuni.install_patches:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: server.localdomain.loc
    exclude_patches:
      - openSUSE-2022-10013
      - openSUSE-SLE-15.3-2022-2118
'''

RETURN = '''
entity:
  description: State whether patch installation was scheduled successfully
  returned: success
  type: bool
'''

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import EmptySetException, SSLCertVerificationError
from ..module_utils.helper_functions import _configure_connection, get_host_id, get_patch_id, patch_already_installed


def _install_patches(module, api_instance):
    """
    Installs patches on the host
    """
    # get parameters
    host = get_host_id(module.params.get('name'), api_instance)
    try:
        include_patches = [get_patch_id(x, api_instance)["id"] for x in module.params.get('include_patches')]
    except (UnboundLocalError, TypeError):
        include_patches = None
    except EmptySetException:
        module.fail_json(msg="Patch not found or applicable")

    try:
        exclude_patches = [get_patch_id(x, api_instance)["id"] for x in module.params.get('exclude_patches')]
    except (UnboundLocalError, TypeError):
        exclude_patches = None
    except EmptySetException:
        module.fail_json(msg="Patch not found or applicable")

    try:
        # get _all_ the patches
        all_patches = api_instance.get_host_patches(host)
        # exclude or include patches if defined
        if exclude_patches:
            patches = [x["id"] for x in all_patches if x["id"] not in exclude_patches]
        elif include_patches:
            patches = [x["id"] for x in all_patches if x["id"] in include_patches]
        else:
            patches = [x["id"] for x in all_patches]

        # install patches
        api_instance.install_patches(
            get_host_id(
                module.params.get('name'),
                api_instance
            ),
            patches
        )
        module.exit_json(changed=True)
    except EmptySetException:
        # check if already installed
        if patch_already_installed(
            get_host_id(
                module.params.get('name'),
                api_instance
            ),
            patches,
            api_instance
        ):
            module.exit_json(changed=False)
        module.fail_json(msg="Patch(es) not found or applicable")
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")


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
        include_patches=dict(type='list', elements='str', required=False),
        exclude_patches=dict(type='list', elements='str', required=False)
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=[('include_patches', 'exclude_patches')],
        supports_check_mode=False
    )

    module_params = dict(
        host=module.params.get('uyuni_host'),
        username=module.params.get('uyuni_user'),
        password=module.params.get('uyuni_password'),
        port=module.params.get('uyuni_port'),
        verify_ssl=module.params.get('uyuni_verify_ssl'),
        include_patches=module.params.get('include_patches'),
        exclude_patches=module.params.get('exclude_patches')
    )

    api_instance = _configure_connection(module_params)
    _install_patches(module, api_instance)


if __name__ == '__main__':
    main()
