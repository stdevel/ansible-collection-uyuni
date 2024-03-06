# client

This role bootstraps [Uyuni](https://uyuni-project.org) and [SUSE Manager](https://www.suse.com/products/suse-manager/) clients.

It requires that you have a **valid bootstrap script** placed at `/srv/www/htdocs/pub/bootstrap` containing an **activation key**. By default, this role searches for a bootstrap script including the appropriate Linux distribution and version, e.g. `bootstrap-debian11.sh` or `bootstrap-opensuse_leap15.4.sh`.

## Requirements

No requirements.

## Role Variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `uyuni_server` | **empty** | Uyuni server hostname or FQDN |
| `uyuni_username` | **empty** | Uyuni username with Org-Admin Role to accept and delete Systems (Optional) |
| `uyuni_password` | **empty** | Password for Uyuni Admin User (Optional) |
| `uyuni_bootstrap_filename` | `(distro)(version).sh` | Bootstrap file to download |
| `uyuni_bootstrap_folder` | `/opt` | Bootstrap file download folder |
| `uyuni_bootstrap_accept_minion_key` | False | If the Minion Key should be accepted while Bootstrapping  |
| `uyuni_client_state` | `present` | Bootstrap (`present`) or remove (`absent`) client |
| `uyuni_removal_cleanup_minion` | False | If the Host should be deleted from Uyuni when client_stat is absent  |

## Dependencies

Ansible Collection:
  Name: Community.General
  Reason: Json Query while Accessing Uyuni API when Bootstrapping or deleting Minions
  https://docs.ansible.com/ansible/latest/collections/community/general/index.html

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

You can also accept the salt Minion Keys on the Uyuni server like this and add Uyuni Admin Credentials:

```yaml
---
- hosts: clients
  roles:
    - role: stdevel.uyuni.client
      uyuni_server: uyuni01.evilcorp.lan
      uyuni_bootstrap_filename: bootstrap-dummy.sh
      uyuni_bootstrap_folder: /tmp
      uyuni_bootstrap_accept_minion_key: True
      uyuni_username: admin
      uyuni_password: password
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

If the System should be removed from Uyuni Server as well, set `uyuni_removal_cleanup_minion` to `True` and add Uyuni Admin Credentials:

```yaml
---
- hosts: clients
  roles:
    - role: stdevel.uyuni.client
      uyuni_client_state: absent
      uyuni_removal_cleanup_minion: True
      uyuni_server: uyuni01.evilcorp.lan
      uyuni_username: admin
      uyuni_password: password
```

## License

GPL 3.0

## Author Information

Christian Stankowic (info@cstan.io)
