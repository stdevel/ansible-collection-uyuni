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
    # check dependencies and Uyuni packages
    for pkg in ansible_vars["ansible_facts"]["server_pkgs"]:
        assert host.package(pkg).is_installed


def test_setup_complete(host):
    """
    check if installation files exist
    """
    with host.sudo():
        for state_file in [
            "/var/lib/containers/storage/volumes/var-pgsql/_data",
            "/root/.MANAGER_INITIALIZATION_COMPLETE",
        ]:
            assert host.file(state_file).exists


def test_ports_listen(host):
    """
    check if ports are listening
    """
    for port in [80, 443, 4505, 4506]:
        assert host.socket("tcp://0.0.0.0:%s" % port).is_listening


def test_org(host):
    """
    check if organization is accessible
    """
    # get variables from file
    ansible_vars = host.ansible("include_vars", "file=main.yml")
    # check if organization exists
    cmd_org = host.run(
        "mgrctl exec 'spacecmd -q -u %s -p %s org_list'",
        ansible_vars["ansible_facts"]["server_org_login"],
        ansible_vars["ansible_facts"]["server_org_password"],
    )
    assert (
        cmd_org.stdout.strip() == ansible_vars["ansible_facts"]["server_org_name"]
    )  # noqa: 204


def test_channels(host):
    """
    check if supplied channels were created
    """
    # get variables from file
    ansible_vars = host.ansible("include_vars", "file=main.yml")
    # check channels if defined
    if (
        "server_channels" in ansible_vars["ansible_facts"]
        and len(ansible_vars["ansible_facts"]["server_channels"]) > 0
    ):
        # get spacewalk-common-channels definitions from client
        with host.sudo():
            definition_file = host.file(
                "/var/lib/containers/storage/volumes/etc-rhn/_data/spacewalk-common-channels.ini"
            ).content_string
        definitions = configparser.RawConfigParser(allow_no_value=True)
        definitions.read_string(definition_file)

        # get all repositories
        with host.sudo():
            cmd_channels = host.run(
                "mgrctl exec 'spacecmd -q -u %s -p %s repo_list'",
                ansible_vars["ansible_facts"]["server_org_login"],
                ansible_vars["ansible_facts"]["server_org_password"],
            )
        for channel in ansible_vars["ansible_facts"]["server_channels"]:
            # get repository name (it ain't nice, but it's honest work)
            repo_name = definitions[channel["name"]]["name"]
            repo_name = "External - %s" % repo_name.replace("%(arch)s", channel["arch"])
            # ensure that repository exists
            assert repo_name in cmd_channels.stdout.strip().split("\n")


def test_monitoring_enabled(host):
    """
    check if monitoring is enabled
    """
    # get variables from file
    ansible_vars = host.ansible("include_vars", "file=main.yml")
    # check configuration
    if ansible_vars["ansible_facts"]["server_enable_monitoring"]:
        with host.sudo():
            rhn_cfg = host.file(
                "/var/lib/containers/storage/volumes/etc-rhn/_data/rhn.conf"
            )
            assert rhn_cfg.contains("prometheus_monitoring_enabled")
    # check status
    with host.sudo():
        mon_status = host.run("mgrctl exec 'mgr-monitoring-ctl status'")
        assert "error" not in mon_status.stderr.strip().lower()
