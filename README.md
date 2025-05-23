# ansible-collection-uyuni

Ansible Collection for managing Uyuni / SUSE Manager installations and ressources.

## Roles

- [`server`](roles/server) - Prepares, installs and configures Uyuni or SUSE Manager
- [`client`](roles/client) - Bootstraps Uyuni or SUSE Manager clients

## Plugins

- [`inventory`](plugins/inventory/inventory.py) - Dynamic inventory
- [`install_patches`](plugins/modules/install_patches.py) - Installs patches on managed hosts
- [`install_upgrades`](plugins/modules/install_upgrades.py) - Installs package upgrades on managed hosts
- [`openscap_run`](plugins/modules/openscap_run.py) - Schedules OpenSCAP runson managed hosts
- [`reboot_host`](plugins/modules/reboot_host.py) - Reboots a managed hosts

### Event-driven Ansible

- [`requires_reboot`](extensions/eda/plugins/event_source/requires_reboot.py) - Checks whether a particular system requires a reboot

Check-out [issues](https://github.com/stdevel/ansible-collection-uyuni/issues) for known issues, missing and upcoming functionality.

## Notes

When using SLES or SL(E) Micro for using this collection you will most likely have to install an additional Python interpreter - the system-wide installation (3.6) is way too old.

## Demonstration

See [the following GitHub repository](https://github.com/stdevel/susecon-suma-aap-demo) for a demonstration of using this collection with AWX.
