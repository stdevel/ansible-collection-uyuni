"""
Molecule unit tests
"""
import os
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
        "file=molecule/default/vars/main.yml"
    )
    # check dependencies and Uyuni packages
    for pkg in ansible_vars["ansible_facts"]["uyuni_storage_packages"] + \
            ansible_vars["ansible_facts"]["uyuni_packages"]:
        assert host.package(pkg).is_installed


def test_lvm(host):
    """
    test if storage was set-up correctly
    """
    # get variables from file
    ansible_vars = host.ansible(
        "include_vars",
        "file=molecule/default/vars/main.yml"
    )
    # check file systems
    for filesys in ansible_vars["ansible_facts"]["uyuni_filesystems"]:
        assert host.mount_point(filesys["mountpoint"]).exists
        assert host.mount_point(
            filesys["mountpoint"]
            ).filesystem == filesys["type"]
