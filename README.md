# ansible-collection-uyuni

Ansible Collection for managing Uyuni / SUSE Manager installations and ressources.

## Roles

- [`storage`](roles/storage) - Prepares LVM storage for Uyuni or SUSE Manager
- [`server`](roles/server) - Prepares, installs and configures Uyuni or SUSE Manager
- [`client`](roles/client) - Bootstraps Uyuni or SUSE Manager clients

## Plugins

- [`inventory`](plugins/inventory/inventory.py) - Dynamic inventory
- [`install_patches`](plugins/modules/install_patches.py) - Installs patches on managed hosts
- [`install_upgrades`](plugins/modules/install_upgrades.py) - Installs package upgrades on managed hosts
- [`openscap_run`](plugins/modules/openscap_run.py) - Schedules OpenSCAP runson managed hosts
- [`reboot_host`](plugins/modules/reboot_host.py) - Reboots a managed hosts

Check-out [issues](https://github.com/stdevel/ansible-collection-uyuni/issues) for known issues, missing and upcoming functionality.

## Demonstration

See [the following GitHub repository](https://github.com/stdevel/susecon-suma-aap-demo) for a demonstration of using this collection with AWX.
