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

- `default` - default scenario with VM running openSUSE Leap 15.2
- `suma` - SUSE Manager 4.x scenario with VM running SUSE Linux Enterprise Server 15 SP1 or SP2

### SUSE hints

In order to run tests against SUSE Manager 4.x you will either require a valid subscription or a trial license.
You can request a [60-day trial on the SUSE website.](https://www.suse.com/products/suse-manager/download/)
For this, you will need to create a [SUSE Customer Center](https://scc.suse.com) account - you will **not** be able to request an additional trial for the same release after the 60 days have expired.

When using SLES, alter ``suma/converge.yml`` like this:

```yml
---
- name: Converge machines
  hosts: all
  roles:
    - role: ansible-uyuni
      scc_reg_code: <insert code here>
      scc_mail: <insert SCC mail here>
...
```

Also, you will need a SLES Vagrant box. As the [SUSE End-user license agreement](https://www.suse.com/licensing/eula/download/sles/sles15sp1-en-us.pdf) for SLES 15 SP1 does not allow re-distributing binary releases, I'm unable to provide you a Vagrant box.
You might want to have a look at these sites in order to find out how to create SLE 15 Vagrant boxes:

- [https://github.com/lavabit/robox](https://github.com/lavabit/robox)
- [https://github.com/chef/bento/tree/master/packer_templates/sles](https://github.com/chef/bento/tree/master/packer_templates/sles)

For SLE 15 SP2 and SP3, SUSE shipped Vagrantboxes again. To import it, use the following command:

```shell
$ vagrant box add sles15-sp3 SLES15-SP3-Vagrant.x86_64-15.2-<provider>-*.vagrant.<provider>.box
```

Replace `<provider>` with `virtualbox` or `libvirt`.

In SLE 15 SP4, Vagrantboxes were removed, again. See [the following blog post](https://cstan.io/post/2023/02/sles-15-sp4-vagrantbox/) to see how to update an existing SP3 Vagrantbox.

## Usage

In order to create the test environment execute the following command:

```shell
$ molecule create
```

**Double-check** the VM settings! Sometimes Molecule doesn't change the CPU count and memory size. The result is a crashing installation.

Also ensure that all available updates have been installed

```shell
$ molecule login --host opensuse-leap15
$ sudo zypper update -y ; exit
$ molecule login --host suma4
$ sudo zypper update -y ; exit
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

For running tests in the `suma` scenario context, run the commands above with the `-s suma` parameter.

When creating your own Vagrantbox, you will need to edit `suma/molecule/molecule.yml` and change the name.
