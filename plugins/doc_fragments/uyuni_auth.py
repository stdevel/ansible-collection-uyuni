"""
Uyuni authentication module snippet
"""
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''
options:
  uyuni_host:
    description: Uyuni API endpoint URL
    required: True
    type: str
  uyuni_port:
    description: Uyuni API endpoint port
    default: 443
    type: int
  uyuni_verify_ssl:
    description: Verify SSL certificate
    default: True
    type: bool
  uyuni_user:
    description: Uyuni login user
    required: True
    type: str
  uyuni_password:
    description: Uyuni login password
    required: True
    type: str
'''
