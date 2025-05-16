"""
Molecule unit tests
"""

import os
import configparser
import testinfra.utils.ansible_runner

TESTINFRA_HOSTS = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


def test_packages(host):
    """
    check if packages are installed
    """
    # get variables from file
    ansible_vars = host.ansible("include_vars", "file=main.yml")
    # check dependencies and proxy packages
    for pkg in ansible_vars["ansible_facts"]["proxy_pkgs"]:
        assert host.package(pkg).is_installed


def test_setup_complete(host):
    """
    check if installation files exist
    """
    with host.sudo():
        for state_file in [
            "/var/lib/containers/storage/volumes/uyuni-proxy-squid-cache/_data",
            "/var/lib/containers/storage/volumes/uyuni-proxy-rhn-cache/_data",
            "/var/lib/containers/storage/volumes/uyuni-proxy-tftpboot/_data"
        ]:
            assert host.file(state_file).exists


def test_ports_listen(host):
    """
    check if ports are listening
    """
    for port in [443, 4505, 4506]:
        assert host.socket("tcp://0.0.0.0:%s" % port).is_listening
