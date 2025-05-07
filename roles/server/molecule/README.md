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

The test environment consists of two test scenarios:

- `default` - default scenario with a container running openSUSE Tumbleweed
- `mlm` - SUSE Manager 5.0 scenario with VM running SLE Micro 5.5

### SUSE hints

In order to run tests against SUSE Manager 5.x you will either require a valid subscription or a trial license.
You can request a [60-day trial on the SUSE website.](https://www.suse.com/products/suse-manager/download/)
For this, you will need to create a [SUSE Customer Center](https://scc.suse.com) account - you will **not** be able to request an additional trial for the same release after the 60 days have expired.

**NOTE:** You will need to setup this VM manually, set the IP address in [`molecule.yml`](molecule.yml) and add an `/etc/hosts` entry with `instance`. This will change once Multi-Linux Manager 5.1 is released.

## Usage

In order to create the test environment execute the following command:

```shell
$ molecule create
```

Run the Ansible role:

```shell
$ molecule converge
```

Finally, run the tests:

```shell
$ molecule verify
...
collected 8 items

    tests/test_default.py ........                                           [100%]

    ========================== 8 passed in 14.09 seconds ===========================
Verifier completed successfully.
```

For running tests in the `mlm` scenario context, run the commands above with the `-s mlm` parameter.

When creating your own Vagrantbox, you will need to edit `mlm/molecule/molecule.yml` and change the name.
