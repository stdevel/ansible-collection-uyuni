#!/usr/bin/env python
"""
Ansible Module for installing patches on a managed host
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import EmptySetException, SSLCertVerificationError
from ..module_utils.helper_functions import _configure_connection, get_host_id, get_patch_id

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
  - "Christian Stankowic (info@cstan.io)"
extends_documentation_fragment:
  - stdevel.uyuni.uyuni_auth
options:
  name:
    description: Name or profile ID of the managed host
    required: True
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
- name: Reboot host
    stdevel.uyuni.install_patches:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: server.localdomain.loc
    exclude_patches:
      - openSUSE-2022-10013
      - openSUSE-SLE-15.3-2022-2118
'''

def _install_patches(module, api_instance):
    """
    Installs patches on the host
    """
    # get parameters
    host =  get_host_id(module.params.get('name'), api_instance)
    try:
        include_patches = [get_patch_id(x, api_instance)["id"] for x in module.params.get('include_patches')]
    except UnboundLocalError:
        include_patches = None
    except TypeError:
        include_patches = None

    try:
        exclude_patches = [get_patch_id(x, api_instance)["id"] for x in module.params.get('exclude_patches')]
    except UnboundLocalError:
        exclude_patches = None
    except TypeError:
        exclude_patches = None

    # bail out if both include/exclude patches is selected
    if include_patches and exclude_patches:
        module.fail_json(msg="Only supply include_patches OR exclude_patches")

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
        module.fail_json(msg="Patch(es) not found")
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")
    except EmptySetException as err:
        module.fail_json(msg=f"Exception when calling UyuniAPI->install_patches: {err}")


def _main():
    argument_spec = dict(
        uyuni_host=dict(required=True, default=None),
        uyuni_user=dict(required=True, default=None),
        uyuni_password=dict(required=True, default=None, no_log=True),
        uyuni_port=dict(default=443, type=int),
        uyuni_verify_ssl=dict(default=True, type=bool),
        name=dict(required=True, default=None),
        include_patches=dict(default=None, type=list),
        exclude_patches=dict(default=None, type=list)
    )

    module = AnsibleModule(argument_spec=argument_spec)

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
    _main()
