"""
Role testing files using testinfra
"""
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


def test_hosts_file(host):
    """
    Validate /etc/hosts file
    """
    f = host.file("/etc/hosts")

    assert f.exists
    assert f.user == "root"
    assert f.group == "root"
