"""
Role testing files using testinfra
__metaclass__ = type"""


def test_hosts_file(host):
    """
    Validate /etc/hosts file
    """
    f = host.file("/etc/hosts")

    assert f.exists
    assert f.user == "root"
    assert f.group == "root"
