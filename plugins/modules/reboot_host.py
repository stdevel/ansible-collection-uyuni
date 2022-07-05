#!/usr/bin/env python
"""
Ansible Module for rebooting a managed host
"""

from ansible.module_utils.basic import AnsibleModule
from ..module_utils.exceptions import EmptySetException, SSLCertVerificationError
from ..module_utils.helper_functions import _configure_connection, get_host_id

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: reboot_host
short_description: Reboot a managed host
description:
  - Reboot a managed host
author:
  - "Christian Stankowic (info@cstan.io)"
extends_documentation_fragment:
  - stdevel.uyuni.uyuni_auth
options:
  name:
    description: Name or profile ID of the managed host
    required: True
'''

EXAMPLES = '''
- name: Reboot host
    stdevel.uyuni.reboot_host:
    uyuni_host: 192.168.1.1
    uyuni_user: admin
    uyuni_password: admin
    name: server.localdomain.loc
'''

def _reboot_host(module, api_instance):
    """
    Reboots the host
    """
    try:
        api_instance.plain_reboot_host(
            get_host_id(
                module.params.get('name'),
                api_instance
            )
        )
        module.exit_json(changed=True)
    except SSLCertVerificationError:
        module.fail_json(msg="Failed to verify SSL certificate")
    except EmptySetException as err:
        module.fail_json(msg=f"Exception when calling UyuniAPI->reboot_host: {err}")


def _main():
    argument_spec = dict(
        uyuni_host=dict(required=True, default=None),
        uyuni_user=dict(required=True, default=None),
        uyuni_password=dict(required=True, default=None, no_log=True),
        uyuni_port=dict(default=443, type=int),
        uyuni_verify_ssl=dict(default=True, type=bool),
        name=dict(required=True, default=None)
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
    _reboot_host(module, api_instance)


if __name__ == '__main__':
    _main()
