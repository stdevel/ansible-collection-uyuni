# molecule

This folder contains molecule configuration and tests.

## Preparation

Ensure to the following installed:

- [Vagrant](https://vagrantup.com)
- [Oracle VirtualBox](https://virtualbox.org)
- Python modules
  - [`molecule`](https://pypi.org/project/molecule/)
  - [`molecule-vagrant`](https://pypi.org/project/molecule-vagrant/)
  - [`python-vagrant`](https://pypi.org/project/python-vagrant/)

## Environment

The test environment consists of one test scenario:

- `default` - default scenario with VM running openSUSE Leap 15.x

## Usage

In order to create the test environment execute the following command:

```shell
$ molecule create
```

Edit [`client_default/converge.yml`](client_default/converge.yml) and enter a valid Uyuni server:

```yaml
...
  roles:
    - role: stdevel.uyuni.client
      uyuni_server: uyuni.evilcorp.lan
```

Run the Ansible role:

```shell
$ molecule converge
```

Finally, run the tests:

```shell
$ molecule verify
```
