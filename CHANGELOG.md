# Changelog

## 0.3.0 (xx.xx.2025)

- added support for containerized setups (SUMA 5.0+ and Uyuni 2024.10+)
- **Breaking change**: removed support for legacy installations (SUMA 4.x and Uyuni up to 2024.08)
- **Breaking change**:removed Ansible role `stdevel.uyuni.storage` as it's not needed anymore for containerized setups

## 0.2.1 (02.05.2024)

- modules will now report the appropriate action ID

## 0.2.0 (07.03.2024)

- inventory plugin: add environment variable passthrough

## 0.1.0 (15.04.2023)

- initial release
- added dynamic inventory, `install_patches`, `install_upgrades`, `openscap_run` and `reboot_host` modules
- splitted former `stdevel.uyuni` Ansible role in `stdevel.uyuni.storage` and `stdevel.uyuni.server` roles
