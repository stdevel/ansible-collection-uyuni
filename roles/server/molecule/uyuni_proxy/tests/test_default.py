"""
Molecule unit tests
"""
import os
import configparser
import testinfra.utils.ansible_runner

TESTINFRA_HOSTS = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_packages(host):
    """
    check if packages are installed
    """
    # get variables from file
    ansible_vars = host.ansible(
        "include_vars",
        "file=molecule/uyuni_proxy/vars/main.yml"
    )
    # check dependencies and Uyuni packages
    for pkg in ansible_vars["ansible_facts"]["uyuni_core_packages"] + \
            ansible_vars["ansible_facts"]["uyuni_packages"]:
        assert host.package(pkg).is_installed


def test_ports_listen(host):
    """
    check if ports are listening
    """
    for port in [22, 80, 443, 4505, 4506]:
        assert host.socket("tcp://0.0.0.0:%s" % port).is_listening


def test_firewall(host):
    """
    check if firewall is configured properly
    """
    # get variables from file
    ansible_vars = host.ansible(
        "include_vars",
        "file=molecule/uyuni_proxy/vars/main.yml"
    )
    # check if services are enabled
    if ansible_vars["ansible_facts"]["uyuni_firewall_config"]:
        with host.sudo():
            cmd_fw = host.run("firewall-cmd --list-services")
            for srv in ansible_vars["ansible_facts"]["uyuni_firewall_services"]:    # noqa: 204
                assert srv in cmd_fw.stdout.strip()
