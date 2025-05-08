# Changelog

## 0.3.0 (xx.09.2024)

- added support for Podman-based deployments
- **Breaking Changes**
  - removed RPM-based deployment support
  - removed firewalld support
  - removed CEFS support
  - removed option `uyuni_sync_channels` as Uyuni will automatically sync channels
  - `uyuni_sles_modules` renamed to `uyuni_slm_modules`
  - removed option `uyuni_bootstrap_repos` as Uyuni will automatically update bootstrap repositories
  - various variables removed:
    - `uyuni_db_name`
    - `uyuni_db_user`
    - `uyuni_db_pass`
    - `uyuni_cert_mail`
    - `uyuni_install_monitoring_formulas`

## 0.2.1 (02.05.2024)

- modules will now report the appropriate action ID

## 0.2.0 (07.03.2024)

- inventory plugin: add environment variable passthrough

## 0.1.0 (15.04.2023)

- initial release
- added dynamic inventory, `install_patches`, `install_upgrades`, `openscap_run` and `reboot_host` modules
- splitted former `stdevel.uyuni` Ansible role in `stdevel.uyuni.storage` and `stdevel.uyuni.server` roles
