# Changelog

## 0.3.6 (27.08.2025)

- `server` - added variable `server_fqdn` to set a custom FQDN if `ansible_fqdn` doesn't work for you

## 0.3.5 (14.08.2025)

- fixed mgrctl parameter (added missing --)
- added `apply_highstate` and `apply_states` modules
- **Breaking change**: `server` role variable names have changed
  - `uyuni_*` --> `server_*`
- **Breaking change**: `client` role variable names have changed
  - `uyuni_*` --> `client_*`
  - `uyuni_server` --> `client_uyuni_server`
- fixed linting, refactored code

## 0.3.4 (04.06.2025)

- fix a bug where local timezone was preferred over UTC timezone when scheduling actions

## 0.3.3 (28.05.2025)

- fixed a bug where installing SUSE Manager 5.0 wasn't supported on SLES 15 SP6

## 0.3.2 (16.05.2025)

- added `proxy` role for installing containerized proxy servers
- added note about using this collection on SLES or SL(E) Micro with outdated Python versions
- `server` - ensure that registration codes are always uppercase

## 0.3.0 (08.05.2025)

- added **support for containerized setups** (SUMA 5.0+ and Uyuni 2024.10+)
  - openSUSE Tumbleweed, Slowroll, Leap, Leap Micro, SUSE Linux Enterprise Server and SUSE Linux Enterprise Micro/SUSE Linux Micro are supported installation targets
- **Breaking change**: removed support for legacy installations (SUMA 4.x and Uyuni up to 2024.08)
- **Breaking change**: removed Ansible role `stdevel.uyuni.storage` as it's not needed anymore for containerized setups
  - see variables `uyuni_disk_volumes` and `uyuni_disk_database`
- `server`: added CPU architecture prerequisite check
- `server`: removed CEFS support as CentOS 7 reached EOL
- `server`: enabling SL(E) modules is now idempotent
- `server`: instead of VMs, containers are now used for development and testing
- `client`: client registration task now idempotent
- added `is_reboot_required` und `full_pkg_update` modules

## 0.2.1 (02.05.2024)

- modules will now report the appropriate action ID

## 0.2.0 (07.03.2024)

- inventory plugin: add environment variable passthrough

## 0.1.0 (15.04.2023)

- initial release
- added dynamic inventory, `install_patches`, `install_upgrades`, `openscap_run` and `reboot_host` modules
- splitted former `stdevel.uyuni` Ansible role in `stdevel.uyuni.storage` and `stdevel.uyuni.server` roles
