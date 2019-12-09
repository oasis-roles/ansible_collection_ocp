[![Build Status](https://travis-ci.com/oasis-roles/ocp_client_install.svg?branch=master)](https://travis-ci.com/oasis-roles/ocp_client_install)

ocp_client_install
==================

Download and install the `oc` and `kubectl` binaries to a specified directory.

This is intended to be used with the distributions of the `oc` and `kubectl` clients
used in installing OpenShift Contain Platform (OCP) 4.x, referenced in the official
Red Hat OCP 4 installation documentation.

Requirements
------------

Ansible 2.9 or higher

Red Hat Enterprise Linux 7 or equivalent

Valid Red Hat Subscriptions

Role Variables
--------------

Currently the following variables are supported:

### General

* `ocp_client_install_url` - Required, http(s) URL to the OCP Client archive. A recipe for
  setting this automatically is included in the examples below.
* `ocp_client_install_path` - Default: `/usr/local/bin/`. Destination directory for installed `oc`
   and `kubectl` binaries. This location should be in the system `PATH`.
* `ocp_client_install_tmpdir` - Default: `/tmp/ocp_client_install`. Direcotry in which to download
  the OCP Client archive.
* `ocp_client_install_cleanup` - Default: `false`. For the purposes of idempotence,
  the `ocp_client_install_tmpdir` directory is not removed by this role by default.
  Set this to `true` to cause this role to clean up the `ocp_client_install_tmpdir`.

### Privilege Escalation

* `ocp_client_install_become` - Default: true. If this role needs administrator
  privileges, then use the Ansible become functionality (based off sudo).
* `ocp_client_install_become_user` - Default: root. If the role uses the become
  functionality for privilege escalation, then this is the name of the target
  user to change to.

Dependencies
------------

None

Example Playbook
----------------

Directly download with absolute URL to archive

```yaml
- hosts: ocp_client_install
  roles:
    - role: oasis_roles.ocp_client_install
      ocp_client_install_url: 'https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-client-linux-4.2.4.tar.gz'

```

Use the [`index_href`](https://galaxy.ansible.com/oasis_roles/index_href) role
to automatically determine latest OCP Client archive URL:

```yaml
- hosts: ocp_client_install
  vars:
    # trailing slash is important here
    ocp_installers_index_url: https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/
    ocp_installers_index: "{{ query('url', ocp_installers_index_url) }}"
    ocp_client_install_url: >-
        {{ query('index_href', ocp_installers_index, 'client-linux',
           base_url=ocp_installers_index_url) }}
  roles:
    - oasis_roles.ocp_client_install
    - oasis_roles.index_href
```

Note that this example is subject to change if the file naming scheme used in the
OCP Clients download index changes.

License
-------

GPLv3

Author Information
------------------

Sean Myers <semyers@redhat.com>
