# storage

This role prepares and configures storage for [Uyuni](https://uyuni-project.org) and [SUSE Manager](https://www.suse.com/products/suse-manager/).

## Requirements

No requirements.

## Role Variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `uyuni_vg` | `uyuni` | LVM volume group to create for Docker data |
| `uyuni_pv` | `/dev/sdb` | Disk to use for LVM |
| `uyuni_filesystems` | see [defaults/main.yml](defaults/main.yml) | LVs, filesystems and mount points to create |

## Dependencies

No dependencies.

## Example Playbook

Refer to the following example:

```yaml
- hosts: servers
  roles:
    - stdevel.uyuni.storage
```

Set variables if required, e.g.:

```yaml
---
- hosts: uyuni.giertz.loc
  remote_user: root
  roles:
    - role: stdevel.uyuni.storage
      uyuni_vg: /dev/vdb
      uyuni_filesystems:
        - name: lv_uyuni
          type: xfs
          mountpoint: /var/spacewalk
          size: 10240
        - name: lv_pgsql
          type: xfs
          mountpoint: /var/lib/pgsql
          size: 10240
```

## License

GPL 3.0

## Author Information

Christian Stankowic (info@cstan.io)
