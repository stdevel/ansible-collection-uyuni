# server

This role prepares, installs and configures [Uyuni](https://uyuni-project.org) and [SUSE Manager](https://www.suse.com/products/suse-manager/).

## Requirements

Make sure to install the `jmespath` and `xml` Python modules.

The system needs access to the internet. Also, you will need an openSUSE Leap 15.x or SUSE Linux Enterprise Server 15.x installation.

## Role Variables

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `uyuni_check_requirements` | `true` | Check for hardware requirements |
| `uyuni_suma_release` | `5.0` | SUSE Manager release to install |
| `uyuni_suma_airgapped` | `false` | Whether to get container image from RPM instead of online registry |
| `uyuni_release` | *empty* | Uyuni release to install (*e.g. `2024.08`*) |
| `uyuni_scc_url` | `https://scc.suse.com` | [SUSE Customer Center](https://scc.suse.com) URL to use (*may be different for some hyperscalers*) |
| `uyuni_scc_reg_code` | - | [SUSE Customer Center](https://scc.suse.com) registration code (*received after trial registration or purchase*) |
| `uyuni_scc_mail` | - | SUSE Customer Center mail address |
| `uyuni_scc_check_registration` | `true` | Register system if unregistered |
| `uyuni_scc_check_modules` | `true` | Activate required modules if not already enabled |
| `uyuni_slm_modules` | (*Modules required for SUSE Manager 4.x*) | Modules to enable before installation |
| `uyuni_mail` | `root@localhost` | Web server administrator mail |
| `uyuni_cert_city` | `Darmstadt` | Certificate city |
| `uyuni_cert_country` | `DE` | Certificate country |
| `uyuni_cert_mail` | `root@localhost` | Certificate mail |
| `uyuni_cert_o` | `Darmstadt` | Certificate organization |
| `uyuni_cert_ou` | `Darmstadt` | Certificate organization unit |
| `uyuni_cert_state` | `Hessen` | Certificate state |
| `uyuni_cert_pass` | `uyuni` | Certificate password |
| `uyuni_org_name` | `Demo` | Organization name |
| `uyuni_org_login` | `admin` | Organization administrator username |
| `uyuni_org_password` | `admin` | Organization administrator password |
| `uyuni_org_mail` | `root@localhost` | Organization administrator mail |
| `uyuni_org_first_name`| `Anton` | Organization administrator first name |
| `uyuni_org_last_name`| `Administrator` | Organization administrator last name |
| `uyuni_channels`| *empty* | Common channels to synchronize (*e.g. `almalinux9` and `epel9`*) |
| `uyuni_enable_monitoring` | `false` | Flag whether integrated monitoring stack should be enabled |

When supplying channels to create in `channels`, ensure passing a list with dicts like this:

```yaml
- name: almalinux9
  arch: x86_64
- name: almalinux9-appstream
  arch: x86_64
- name: almalinux9-uyuni-client
  arch: x86_64
```

For available channels and architectures, see the `spacewalk-common-channels.ini` installed by the `spacewalk-utils` package. There is also [an online version](https://github.com/uyuni-project/uyuni/blob/master/utils/spacewalk-common-channels.ini) on GitHub.

## Dependencies

No dependencies.

## Example Playbook

Refer to the following example:

```yaml
- hosts: servers
  roles:
    - stdevel.uyuni.server
```

Set variables if required, e.g.:

```yaml
---
- hosts: uyuni.giertz.loc
  remote_user: root
  roles:
    - role: stdevel.uyuni.server
      uyuni_channels:
        - name: almalinux9
          arch: x86_64
        - name: almalinux9-appstream
          arch: x86_64
        - name: almalinux9-uyuni-client
          arch: x86_64
```

Don't forget setting SUSE-related variables when deploying SUSE Manager:

```yaml
- hosts: servers
  roles:
    - role: stdevel.uyuni.server
      uyuni_scc_reg_code: DERP1337LULZ
      uyuni_scc_mail: bla@foo.bar
```

If you plan to bootstrap older Uyuni versions, set the Uyuni release:

```yaml
---
- hosts: retro.giertz.loc
  remote_user: root
  roles:
    - role: stdevel.uyuni.server
      uyuni_release: '2024.07'
```

## Development

You'll need an customized openSUSE Tumbleweed podman container (with systemd and other utilities) for testing purposes:

```command
$ podman build -t opensuse-tumbleweed .
```

Use `molecule` for running the code:

```command
$ molecule create
$ molecule converge
$ molecule verify
```

## License

GPL 3.0

## Author information

Christian Stankowic (info@cstan.io)
