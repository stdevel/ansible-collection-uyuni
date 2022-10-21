# -*- coding: utf-8 -*-
"""
Ansible inventory module for Uyuni

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

DOCUMENTATION = '''
    name: inventory
    short_description: Uyuni inventory source
    author:
        - Christian Stankowic (@stdevel)
    description:
        - Get inventory hosts from the Uyuni API.
        - "Uses a configuration file as an inventory source, it must end in
          C(.uyuni.yml) or C(.uyuni.yaml)."
    options:
      plugin:
        description: Name of the plugin.
        required: true
        type: string
        choices: ['stdevel.uyuni.inventory']
      host:
        description: Hostname/IP address of the Uyuni server.
        type: string
        required: true
      user:
        description: Username to query the API.
        type: string
        required: true
      port:
        description: API port
        type: int
        default: 443
      password:
        description: Password to query the API.
        type: string
        required: true
      verify_ssl:
        description: Enables or disables SSL certificate verification.
        type: boolean
        default: true
      only_powered_on:
        description: Only shows powered-on hosts.
        type: boolean
        default: true
      ipv6_only:
        description: Use IPv6 addresses only
        type: boolean
        default: false
      show_custom_values:
        description: Lists defined custom parameters and values
        type: boolean
        default: false
      groups:
        description: Limits to specific names groups
        type: list
        required: false
      pending_reboot_only:
        description: Limits to systems requiring a reboot only
        type: boolean
        default: false
'''

EXAMPLES = r'''
---
# my.uyuni.yml
plugin: stdevel.uyuni.uyuni_inventory
host: 192.168.180.1
user: admin
password: admin
verify_ssl: false
show_custom_values: true
ipv6_only: true
groups:
  - dev
  - demo
'''

from ansible.plugins.inventory import (
    BaseInventoryPlugin, Constructable, Cacheable
)
from ..module_utils.helper_functions import _configure_connection


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    """
    Host inventory parser for ansible using Uyuni
    """

    NAME = 'stdevel.uyuni.uyuni_inventory'

    def __init__(self):
        """
        Initializes the inventory plugin
        """
        super(InventoryModule, self).__init__()

        # clear config
        self.api_instance = None
        self.host = None
        self.user = None
        self.password = None
        self.port = None
        self.verify_ssl = None

    def verify_file(self, path):
        """
        Verifies the configuration file
        """
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('uyuni.yaml', 'uyuni.yml')):
                valid = True
            else:
                self.display.vvv(
                    'Skipping due to inventory source not ending in "uyuni.yml" nor "uyuni.yaml"'   # noqa: E501
                )
        return valid

    def _api_connect(self):
        """
        Connects to the Uyuni API
        """
        self.api_instance = _configure_connection(
            dict(
                host=str(self.get_option('host')),
                username=str(self.get_option('user')),
                password=str(self.get_option('password')),
                port=str(self.get_option('port')),
                verify_ssl=self.get_option('verify_ssl')
            )
        )

    def _populate(self):
        # get groups and hosts
        all_groups = self.api_instance.get_all_hostgroups()
        hosts = self.api_instance.get_all_hosts()

        if self.get_option('groups'):
            # limit to group selection
            groups = [x for x in all_groups if x in self.get_option('groups')]
        else:
            # all groups
            groups = all_groups

        for group in groups:
            # add selected/all groups
            self.inventory.add_group(group)

        # get systems requiring reboot
        _reboot = self.api_instance.get_hosts_by_required_reboot()

        # add _all_ the hosts
        for host in hosts:
            # get host groups
            _groups = self.api_instance.get_hostgroups_by_host(int(host['id']))

            if self.get_option('groups'):
                # only add if host is filtered groups
                if not any(x in _groups for x in self.get_option('groups')):
                    continue

            # check if reboot required
            if self.get_option('pending_reboot_only'):
                try:
                    if host not in _reboot:
                        continue
                except TypeError:
                    continue

            # add host
            self.inventory.add_host(host['name'])

            # get IP address
            _network = self.api_instance.get_host_network(int(host['id']))
            if self.get_option('ipv6_only'):
                self.inventory.set_variable(
                    host['name'], 'ansible_host', _network['ip6']
                )
            else:
                self.inventory.set_variable(
                    host['name'], 'ansible_host', _network['ip']
                )

            # add parameters
            if self.get_option('show_custom_values'):
                _params = self.api_instance.get_host_params(int(host['id']))
                for param in _params:
                    self.inventory.set_variable(
                        host['name'], param, _params[param]
                    )

            # add hostgroups
            for _group in _groups:
                if _group in groups:
                    self.inventory.add_child(_group, host['name'])

    def parse(self, inventory, loader, path, cache=True):
        """
        Parses the inventory
        """
        super(InventoryModule, self).parse(inventory, loader, path)

        # read config from file, this sets 'options'
        self._read_config_data(path)

        # create API instance
        self._api_connect()

        # create inventory
        self._populate()
