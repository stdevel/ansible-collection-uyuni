"""
Uyuni XMLRPC API client
"""

from __future__ import (absolute_import, division, print_function)
import logging
import ssl
import base64
from datetime import datetime, timedelta
from xmlrpc.client import DateTime, Fault, ServerProxy

from .utilities import split_rpm_filename
from .exceptions import (
    APILevelNotSupportedException,
    EmptySetException,
    InvalidCredentialsException,
    SessionException,
    SSLCertVerificationError,
    CustomVariableExistsException
)

__metaclass__ = type


class UyuniAPIClient:
    """
    Class for communicating with the Uyuni API

    .. class:: UyuniAPIClient
    """

    LOGGER = logging.getLogger("UyuniAPIClient")
    """
    logging: Logger instance
    """
    API_MIN = 24
    """
    int: Minimum supported API version.
    """
    HEADERS = {"User-Agent": "katprep (https://github.com/stdevel/katprep)"}
    """
    dict: Default headers set for every HTTP request
    """

    def __init__(
            self, log_level, hostname, username, password,
            port=443, verify=True
    ):
        """
        Constructor creating the class. It requires specifying a
        hostname, username and password to access the API. After
        initialization, a connected is established.

        :param log_level: log level
        :type log_level: logging
        :param username: API username
        :type username: str
        :param password: corresponding password
        :type password: str
        :param hostname: Uyuni host
        :type hostname: str
        :param port: HTTPS port
        :type port: int
        :param verify: SSL verification
        :type verify: bool
        """
        # set logging
        self.LOGGER.setLevel(log_level)
        self.LOGGER.debug(
            "About to create Uyuni client '%s'@'%s'",
            username, hostname
        )

        # set connection information
        self.LOGGER.debug("Set hostname to '%s'", hostname)
        self.url = f"https://{hostname}:{port}/rpc/api"
        self.verify = verify

        # start session and check API version if Uyuni API
        self._api_key = None
        self._username = username
        self._password = password
        self._session = None
        self._connect()
        self.validate_api_support()

    def _connect(self):
        """
        This function establishes a connection to Uyuni
        """
        # set API session and key
        try:
            if not self.verify:
                context = ssl._create_unverified_context()
            else:
                context = ssl.create_default_context()

            self._session = ServerProxy(self.url, context=context)
            self._api_key = self._session.auth.login(
                self._username, self._password
            )
        except ssl.SSLCertVerificationError as err:
            self.LOGGER.error(err)
            raise SSLCertVerificationError(str(err)) from err
        except Fault as err:
            if err.faultCode == 2950:
                raise InvalidCredentialsException(
                    f"Wrong credentials supplied: {err.faultString!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def validate_api_support(self):
        """
        Checks whether the API version on the Uyuni server is supported.
        Using older versions than API_MIN is not recommended. In this case, an
        exception will be thrown.

        :raises: APILevelNotSupportedException
        """
        try:
            # check whether API is supported
            api_level = self._session.api.getVersion()
            if float(api_level) < self.API_MIN:
                raise APILevelNotSupportedException(
                    f"Your API version ({api_level!r}) doesn't support"
                    "required calls."
                    f"You'll need API version ({self.API_MIN!r}) or higher!"
                )
            self.LOGGER.info("Supported API version %s found.", api_level)
        except ValueError as err:
            self.LOGGER.error(err)
            raise APILevelNotSupportedException(
                "Unable to verify API version"
            ) from err

    def get_hosts(self):
        """
        Returns all system IDs
        """
        try:
            hosts = self._session.system.listSystems(
                self._api_key
            )
            if hosts:
                return [x["id"] for x in hosts]
            raise EmptySetException(
                "No systems found"
            )
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_all_hosts(self):
        """
        Returns all system names and IDs
        """
        try:
            hosts = self._session.system.listSystems(
                self._api_key
            )
            if hosts:
                return hosts
            raise EmptySetException(
                "No systems found"
            )
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_all_hostgroups(self):
        """
        Returns all hostgroups
        """
        try:
            groups = self._session.systemgroup.listAllGroups(
                self._api_key
            )
            if groups:
                return [x["name"] for x in groups]
            raise EmptySetException(
                "No groups found"
            )
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_hostgroups_by_host(self, system_id):
        """
        Returns all groups for a specific host
        """
        try:
            groups = self._session.system.listGroups(
                self._api_key, system_id
            )
            if groups:
                return [x["system_group_name"] for x in groups if x["subscribed"] == 1]
            raise EmptySetException(
                "No groups found"
            )
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_hosts_by_organization(self, organization):
        """
        Returns all systems by organisation
        """
        # filter not implemented by Uyuni API
        # simply return _all_ the hosts
        self.LOGGER.debug(
            "Just printing %s so that pylint shuts up",
            organization
        )
        return self.get_hosts()

    def get_hosts_by_location(self, location):
        """
        Returns all systems by location
        """
        # filter not implemented by Uyuni API
        # simply return _all_ the hosts
        self.LOGGER.debug(
            "Just printing %s so that pylint shuts up",
            location
        )
        return self.get_hosts()

    def get_hosts_by_hostgroup(self, hostgroup):
        """
        Returns all systems by hostgroup
        """
        try:
            hosts = self._session.systemgroup.listSystems(
                self._api_key, hostgroup
            )
            if hosts:
                return [x["id"] for x in hosts]
            raise EmptySetException(
                "No systems found"
            )
        except Fault as err:
            if "unable to locate" in err.faultString.lower():
                raise EmptySetException(
                    "No systems found"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_hosts_by_required_reboot(self):
        """
        Returns all systems requiring a reboot
        """
        try:
            hosts = self._session.system.listSuggestedReboot(
                self._api_key
            )

            if hosts:
                return [x["name"] for x in hosts]
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_id(self, hostname):
        """
        Returns the profile ID of a particular system

        :param hostname: system hostname
        :type hostname: str
        """
        try:
            host_id = self._session.system.getId(
                self._api_key, hostname
            )
            if host_id:
                return host_id[0]["id"]
            raise EmptySetException(
                f"System not found: {hostname!r}"
            )
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise EmptySetException(
                    f"System not found: {hostname!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_hostname_by_id(self, system_id):
        """
        Returns the hostname of a particular system

        :param system_id: profile ID
        :type system_id: int
        """
        try:
            host = self._session.system.getName(
                self._api_key, system_id
            )
            return host["name"]
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise EmptySetException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_params(self, system_id):
        """
        Returns the parameters of a particular system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            params = self._session.system.getCustomValues(
                self._api_key, system_id
            )
            return params
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_owner(self, system_id):
        """
        Returns the host owner

        :param system_id: profile ID
        :type system_id: int
        """
        host_params = self.get_host_params(system_id)
        try:
            return host_params['katprep_owner']
        except KeyError as err:
            raise SessionException(
                f"Owner not found for {system_id!r}"
            ) from err

    def get_host_custom_variables(self, system_id):
        """
        Returns host custom variables (custom info key values)

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            values = self._session.system.getCustomValues(
                self._api_key, system_id
            )
            return values
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_patches(self, system_id):
        """
        Returns available patches for a particular system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            errata = self._session.system.getRelevantErrata(
                self._api_key, system_id
            )
            return errata
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_patch_by_name(self, patch_name):
        """
        Returns a patch by name

        :param patch_name: Patch name (e.g. openSUSE-2020-1001)
        :type patch_name: str
        """
        try:
            patch = self._session.errata.getDetails(
                self._api_key, patch_name
            )
            return patch
        except Fault as err:
            def missing_patch(error_message):
                message = error_message.lower()
                if (
                    "no such patch" in message or
                    ("the patch" in message and "cannot be found" in message)
                ):
                    return True

                return False

            if missing_patch(err.faultString):
                raise EmptySetException(
                    f"Patch not found: {patch_name!r}"
                ) from err

            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_package_by_file_name(self, file_name):
        """
        Returns a package by file name

        :param file_name: file name (e.g. foo-1.0-1.i386.rpm)
        :type file_name: str
        """
        package_nvrea = split_rpm_filename(file_name)

        try:
            package = self._session.packages.findByNvrea(
                self._api_key,
                package_nvrea.name,
                package_nvrea.version,
                package_nvrea.release,
                package_nvrea.epoch,
                package_nvrea.architecture
            )
            return package
        except Fault as err:
            if "no such package" in err.faultString.lower():
                raise EmptySetException(
                    f"Package not found: {file_name!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_upgrades(self, system_id):
        """
        Returns available package upgrades

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            packages = self._session.system.listLatestUpgradablePackages(
                self._api_key, system_id
            )
            _packages = []
            for pkg in packages:
                # exclude if it part of an errata
                erratum = self._session.packages.listProvidingErrata(
                    self._api_key, pkg["to_package_id"]
                )
                if not erratum:
                    _packages.append(pkg)

            self.LOGGER.debug("Found %i upgrades for %s: %s", len(_packages), system_id, _packages)
            return _packages
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_groups(self, system_id):
        """
        Returns groups for a given system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            groups = self._session.system.listGroups(
                self._api_key, system_id
            )
            return groups
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_details(self, system_id):
        """
        Returns details for a given system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            details = self._session.system.getDetails(
                self._api_key, system_id
            )
            return details
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_network(self, system_id):
        """
        Returns network information for a given system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            details = self._session.system.getNetwork(
                self._api_key, system_id
            )
            return details
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def install_patches(self, system_id, patches=None):
        """
        Install patches on a given system

        :param system_id: profile ID
        :type system_id: int
        :param patches: If given only installs the given patches.
        :type patches: list
        """

        try:
            action_id = self._session.system.scheduleApplyErrata(
                self._api_key, system_id, patches
            )
            return action_id
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            if "no errata to apply" in err.faultString.lower():
                raise EmptySetException(
                    f"No applicable errata to apply: {err.faultString!r}"
                ) from err
            if "invalid errata" in err.faultString.lower():
                raise EmptySetException(
                    f"Errata not found: {err.faultString!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def install_upgrades(self, system_id, upgrades=None):
        """
        Install package upgrades on a given system

        :param system_id: profile ID
        :type system_id: int
        :param upgrades: Specific upgrade IDs to install
        :type upgrades: list with ints
        """
        if not upgrades:
            self.LOGGER.debug("No upgrades for %s", system_id)
            raise EmptySetException("No patches supplied")

        earliest_execution = DateTime(datetime.now().timetuple())

        try:
            action_id = self._session.system.schedulePackageInstall(
                self._api_key, system_id, upgrades, earliest_execution
            )

            # returning an array to be consistent with install_patches
            return [action_id]
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            if "cannot find package" in err.faultString.lower():
                raise EmptySetException(
                    f"Upgrade not found: {err.faultString!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def reboot_host(self, system_id):
        """
        Reboots a system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                f"No system found - use system profile IDs {system_id}"
            )

        earliest_execution = DateTime(datetime.now().timetuple())
        try:
            action_id = self._session.system.scheduleReboot(
                self._api_key, system_id, earliest_execution
            )
            return action_id
        except Fault as err:
            if "could not find server" in err.faultString.lower():
                raise EmptySetException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_action(self, system_id, action_id):
        """
        Retrieves information about a particular host action

        :param system_id: profile ID
        :type system_id: int
        :param action_id: task ID
        :type action_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )
        if not isinstance(action_id, int):
            raise EmptySetException(
                "No task found - use task IDs"
            )

        try:
            # return particular action
            actions = self.get_host_actions(system_id)
            action = [x for x in actions if x['id'] == action_id]
            if not action:
                raise EmptySetException("Action not found")
            return action
        except Fault as err:
            if "action not found" in err.faultString.lower():
                raise EmptySetException(
                    f"Action not found: {action_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_host_actions(self, system_id):
        """
        Returns actions for a given system

        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            actions = self._session.system.listSystemEvents(
                self._api_key, system_id
            )
            return actions
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_user(self, user_name):
        """
        Retrieves information about a particular user

        :param user_name: username
        :type user_name: str
        """
        if not isinstance(user_name, str):
            raise EmptySetException(
                "No user found - use user name"
            )

        try:
            # return user information
            user_info = self._session.user.getDetails(
                self._api_key, user_name
            )
            return user_info
        except Fault as err:
            if "could not find user" in err.faultString.lower():
                raise EmptySetException(
                    f"User not found: {user_name!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_organization(self):
        """
        Retrieves current organization
        """
        return self.get_user(self._username)['org_name']

    def get_location(self):
        """
        Retrieves current location
        """
        # simply return the organization as Uyuni
        # does not support any kind of locations
        return self.get_organization()

    def is_reboot_required(self, system_id):
        """
        Checks whether a particular host requires a reboot

        :param system_id: profile ID
        :type system_id: int
        """
        try:
            systems = self._session.system.listSuggestedReboot(
                self._api_key
            )

            return any(system["id"] == system_id for system in systems)
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_action_by_type(self, system_id, action_type):
        """
        Gets host action by specific type

        :param system_id: profile ID
        :type system_id: int
        :param action_type: action type
        :type action_type: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            actions = self._session.system.listSystemEvents(
                self._api_key, system_id, action_type
            )
            return actions
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_errata_task_status(self, system_id):
        """
        Get the status of errata installations for the given host

        :param system_id: profile ID
        :type system_id: int
        """
        return self.get_action_by_type(system_id, 'Patch Update')

    def get_upgrade_task_status(self, system_id):
        """
        Get the status of package upgrades for the given host

        :param system_id: profile ID
        :type system_id: int
        """
        return self.get_action_by_type(system_id, 'Package Install')

    def get_script_task_status(self, system_id):
        """
        Get the status of script executions for the given host

        :param system_id: profile ID
        :type system_id: int
        """
        return self.get_action_by_type(system_id, 'Run an arbitrary script')

    def get_custom_variables(self):
        """
        Returns all defines custom variables (custom info keys)
        """
        try:
            _variables = self._session.system.custominfo.listAllKeys(
                self._api_key
            )
            variables = {x['label']: x['description'] for x in _variables}
            return variables
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def create_custom_variable(self, label, description):
        """
        Creates a custom variable (custom info keys)

        :param label: variable label
        :type label: str
        :param description: variable description
        :type label: str
        """
        try:
            self._session.system.custominfo.createKey(
                self._api_key, label, description
            )
        except Fault as err:
            if "already exists" in err.faultString.lower():
                raise CustomVariableExistsException(
                    f"Key already exists: {label!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def update_custom_variable(self, label, description):
        """
        Updates a custom variable's description (custom info keys)

        :param label: variable label
        :type label: str
        :param description: variable description
        :type label: str
        """
        try:
            self._session.system.custominfo.updateKey(
                self._api_key, label, description
            )
        except Fault as err:
            if "does not exist" in err.faultString.lower():
                raise EmptySetException(
                    f"Key does not exist: {label!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def delete_custom_variable(self, label):
        """
        Deletes a custom variable (custom info keys)

        :param label: variable label
        :type label: str
        """
        try:
            self._session.system.custominfo.deleteKey(
                self._api_key, label
            )
        except Fault as err:
            if "does not exist" in err.faultString.lower():
                raise EmptySetException(
                    f"Key does not exist: {label!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def host_add_custom_variable(self, system_id, label, value):
        """
        Adds a custom variable to a host

        :param system_id: profile ID
        :type system_id: int
        :param label: variable label
        :type label: str
        :param value: variable value
        :type value: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            self._session.system.setCustomValues(
                self._api_key, system_id,
                {label: value}
            )
        except Fault as err:
            if "was not defined" in err.faultString.lower():
                raise EmptySetException(
                    f"Custom Variable does not exist: {label!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def host_update_custom_variable(self, system_id, label, value):
        """
        Updates a custom variable for a host

        :param system_id: profile ID
        :type system_id: int
        :param label: variable label
        :type label: str
        :param value: variable value
        :type value: str
        """
        self.host_add_custom_variable(system_id, label, value)

    def host_delete_custom_variable(self, system_id, label):
        """
        Deletes a custom variable from a host

        :param system_id: profile ID
        :type system_id: int
        :param label: variable label
        :type label: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            self._session.system.deleteCustomValues(
                self._api_key, system_id,
                [label]
            )
        except Fault as err:
            if "was not defined" in err.faultString.lower():
                raise EmptySetException(
                    f"Custom Variable does not exist: {label!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def host_run_command(self, system_id, command, user="root", group="root"):
        """
        Runs a particular command on a host

        :param system_id: profile ID
        :type system_id: int
        :param command: command
        :type command: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        earliest_execution = DateTime(datetime.now().timetuple())
        # add shebang if not found
        if not command.startswith("#!/"):
            command = f'#!/bin/sh\n{command}'

        try:
            return self._session.system.scheduleScriptRun(
                self._api_key,
                system_id,
                user,
                group,
                600,
                command,
                earliest_execution
            )
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise EmptySetException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_actionchains(self):
        """
        Returns all defined action chains
        """
        try:
            return self._session.actionchain.listChains(
                self._api_key
            )
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def get_actionchain_actions(self, chain_label):
        """
        Returns actions of a particular action chain

        :param chain_label: chain label
        :type chain_label: str
        """
        try:
            actions = self._session.actionchain.listChainActions(
                self._api_key, chain_label
            )
            if len(actions) == 0:
                raise EmptySetException("Action chain is empty")
            return actions
        except Fault as err:
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def add_actionchain(self, label):
        """
        Creates a new action chain

        :param label: action chain label
        :type label: str
        """
        try:
            chain_id = self._session.actionchain.createChain(
                self._api_key, label
            )
            return chain_id
        except Fault as err:
            if "is missing" in err.faultString.lower():
                raise EmptySetException(
                    "Label missing"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def run_actionchain(self, chain_label):
        """
        Runs a particular action chain

        :param chain_label: chain label
        :type chain_label: str
        """
        try:
            earliest_execution = DateTime(datetime.now().timetuple())
            chain_id = self._session.actionchain.scheduleChain(
                self._api_key, chain_label, earliest_execution
            )
            return chain_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def delete_actionchain(self, chain_label):
        """
        Removes a particular action chain

        :param chain_label: chain label
        :type chain_label: str
        """
        try:
            self._session.actionchain.deleteChain(
                self._api_key, chain_label
            )
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def actionchain_add_patches(self, chain_label, system_id, patches):
        """
        Adds patch installation to an action chain

        :param chain_label: chain label
        :type chain_label: str
        :param system_id: profile ID
        :type system_id: int
        :param patches: patch IDs
        :type patches: int array
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            action_id = self._session.actionchain.addErrataUpdate(
                self._api_key, system_id, patches, chain_label
            )
            return action_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                ) from err
            if "could not find errata" in err.faultString.lower():
                raise EmptySetException(
                    f"At least one patch not found: {patches!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def actionchain_add_upgrades(self, chain_label, system_id, upgrades):
        """
        Adds package upgrad to an action chain

        :param chain_label: chain label
        :type chain_label: str
        :param system_id: profile ID
        :type system_id: int
        :param upgrades: upgrade IDs
        :type upgrades: int array
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        if not upgrades:
            raise EmptySetException(
                "No upgrades defined"
            )

        try:
            action_id = self._session.actionchain.addPackageUpgrade(
                self._api_key, system_id, upgrades, chain_label
            )
            return action_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                ) from err
            if "invalid package" in err.faultString.lower():
                raise EmptySetException(
                    f"At least one package upgrade not found: {upgrades!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def actionchain_add_command(self, chain_label, system_id, command, user="root", group="root"):
        """
        :param chain_label: chain label
        :type chain_label: str
        :param system_id: profile ID
        :type system_id: int
        :param command: command
        :type command: str
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )
        if len(command) == 0:
            raise EmptySetException(
                "Command is empty"
            )
        # add shebang if not found
        if not command.startswith("#!/"):
            command = f'#!/bin/sh\n{command}'

        try:
            action_id = self._session.actionchain.addScriptRun(
                self._api_key,
                system_id,
                chain_label,
                user,
                group,
                600,
                str(
                    base64.b64encode(command.encode("utf-8")),
                    "utf-8"
                )
            )
            return action_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def actionchain_add_reboot(self, chain_label, system_id):
        """
        :param chain_label: chain label
        :type chain_label: str
        :param system_id: profile ID
        :type system_id: int
        """
        if not isinstance(system_id, int):
            raise EmptySetException(
                "No system found - use system profile IDs"
            )

        try:
            action_id = self._session.actionchain.addSystemReboot(
                self._api_key,
                system_id,
                chain_label,
            )
            return action_id
        except Fault as err:
            if "no such action chain" in err.faultString.lower():
                raise EmptySetException(
                    f"Action chain not found: {chain_label!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def schedule_openscap_run(self, system_id, document, arguments=None):
        """
        Install patches on a given system

        :param system_id: profile ID
        :type system_id: int
        :param document: document path
        :type document: str
        :param arguments: If given appends command-line arguments
        :type patches: str
        """
        if not isinstance(system_id, list):
            system_id = [system_id]
        if not arguments:
            arguments = ""

        try:
            action_id = self._session.system.scap.scheduleXccdfScan(
                self._api_key, system_id, document, arguments
            )
            return action_id
        except Fault as err:
            if "no such system" in err.faultString.lower():
                raise SessionException(
                    f"System not found: {system_id!r}"
                ) from err
            raise SessionException(
                f"Generic remote communication error: {err.faultString!r}"
            ) from err

    def wait_for_action(self, action_id, system_id, timeout=3600, interval=30):
        """
        Waits for the action to complete.
    
        :param api_instance: The API instance to use for checking the action status.
        :param action_id: The ID of the action to wait for.
        :param timeout: The maximum time to wait for the action to complete (in seconds).
        :param interval: The interval between status checks (in seconds).
        """
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=timeout)
        while datetime.now() < end_time:
            status = self.get_host_action(system_id, action_id)
            if status[0]['successful_count'] + status[0]['failed_count'] > 0:
                return status
            next_check = datetime.now() + timedelta(seconds=interval)
            while datetime.now() < next_check:
                pass
        raise TimeoutError(f"Action {action_id} did not complete within {timeout} seconds")
