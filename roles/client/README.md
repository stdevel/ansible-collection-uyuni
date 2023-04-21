# client

This role bootstraps [Uyuni](https://uyuni-project.org) and [SUSE Manager](https://www.suse.com/products/suse-manager/) clients.

It requires that you have a **valid bootstrap script** placed at `/srv/www/htdocs/pub/bootstrap` containing an **activation key**. By default, this role searches for a bootstrap script including the appropriate Linux distribution and version, e.g. `bootstrap-debian11.sh` or `bootstrap-opensuse_leap15.4.sh`.

## Requirements

No requirements.

## Role Variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `uyuni_server` | **empty** | Uyuni server hostname or FQDN |
| `uyuni_bootstrap_filename` | `(distro)(version).sh` | Bootstrap file to download |
| `uyuni_bootstrap_folder` | `/opt` | Bootstrap file download folder |
| `uyuni_client_state` | `present` | Bootstrap (`present`) or remove (`absent`) client |

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

To remove `salt-minion` and managed software repositories, set `uyuni_client_state` to `absent`:

```yaml
---
- hosts: clients
  roles:
    - role: stdevel.uyuni.client
      uyuni_client_state: absent
```

**NOTE**: This will **not** remove the appropriate system profile from Uyuni/SUSE Manager.

## License

GPL 3.0

## Author Information

Christian Stankowic (info@cstan.io)
