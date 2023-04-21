"""
Molecule unit tests
"""
import os
import testinfra.utils.ansible_runner

TESTINFRA_HOSTS = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_salt(host):
    """
    Test if salt-minion is running
    """
    minion = host.process.filter(comm="salt-minion")
    minion_venv = host.process.filter(
        comm="/usr/lib/venv-salt-minion/bin/python.original"
    )
    assert minion or minion_venv

def test_repo(host):
    """
    Test if repository was created
    """
    # get OS family
    os = host.ansible("setup")["ansible_facts"]["ansible_os_family"].lower()
    if os == "debian":
        repo_file = host.file("/etc/apt/sources.list.d/susemanager:channels.list")
    elif os == "redhat":
        repo_file = host.file("/etc/yum.repos.d/susemanager:channels.repo")
    elif os == "suse":
        repo_file = host.file("/etc/zypp/repos.d/susemanager:channels.repo")
    assert repo_file.exists
    assert repo_file.size > 100
