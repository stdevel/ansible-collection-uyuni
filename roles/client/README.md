# client

This role bootstraps [Uyuni](https://uyuni-project.org) and [SUSE Manager](https://www.suse.com/products/suse-manager/) clients.

## Requirements

No requirements.

## Role Variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `uyuni_server` | **empty** | Uyuni server hostname or FQDN |
| `uyuni_bootstrap_filename` | `(distro)(version).sh` | Bootstrap file to download |
| `uyuni_bootstrap_folder` | `/opt` | Bootstrap file download folder |

## Dependencies

No dependencies.

## Example Playbook

Refer to the following example:

```yaml
- hosts: clients
  roles:
    - role: stdevel.uyuni.client
      uyuni_server: uyuni01.evilcorp.lan
```

Set variables if required, e.g.:

```yaml
---
- hosts: clients
  roles:
    - role: stdevel.uyuni.client
      uyuni_server: uyuni01.evilcorp.lan
      uyuni_bootstrap_filename: bootstrap-dummy.sh
      uyuni_bootstrap_folder: /tmp
```

## License

GPL 3.0

## Author Information

Christian Stankowic (info@cstan.io)
