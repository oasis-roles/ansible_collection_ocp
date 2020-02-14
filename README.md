[![Build Status](https://travis-ci.com/oasis-roles/ocp_install.svg?branch=master)](https://travis-ci.com/oasis-roles/ocp_client_install)

ocp_install
==================

Download and run the `openshift-install` binary for installing OpenShift Container
Platform 4.x, according to the official Red Hat OCP 4 installation documentation.

Requirements
------------

Ansible 2.9 or higher

Red Hat Enterprise Linux 7 or equivalent

Valid Red Hat Subscriptions

Role Variables
--------------

Currently the following variables are supported:

### General

* `ocp_install_url` - Required, http(s) URL to the OCP Installer archive. A recipe for
  setting this automatically is included in the examples below.
* `ocp_install_path` - Default: `/usr/local/bin/`. Destination directory for installed
  `openshift-installer` binary.
* `ocp_install_tmp_dir` - Default: `/tmp/ocp_install`. Directory on the target host
   where downloaded `openshift-install` archive will be extracted.
* `ocp_install_clean_tmp_dir` - Default: `false`. For the purposes of idempotence,
  the `ocp_install_tmp_dir` directory is not removed by this role by default.
  Set this to `true` to cause this role to clean up the `ocp_install_dir`.
* `ocp_install_log_level` - Default: `info`. Log level used when calling `openshift-installer`
  commands. Valid log levels include `debug`, `info`, `warn`, and `error`.

### `install-config.yaml` Generation

This role can generate an `install-config.yaml`, if requested, placing it in the
provided `ocp_install_config_dir`.

* `ocp_install_generate_config` - Default: `false`. Whether or not to generate an
  `install-config.yaml` in the `ocp_install_config_dir`. Forced to `true` if
  `ocp_install_create_cluster` is `true`.
* `ocp_install_config_dir` - Default: `~/ocp_install`. Directory in which to download
  the OCP Client archive and store files used during the installation,
  including the install config.
* `ocp_install_config_template` - Custom template to use for `install-config.yaml`,
  if [the default template] is insufficient.

The following vars are used when generating `install-config.yaml` with the default
template, and each one corresponds to the similarly-named `install-config.yaml`
entries and sections of the same name. For example, `ocp_install_api_version`
corresponds to the `apiVersion` configuration key in `install-config.yaml`.

* `ocp_install_additional_trust_bundle`
* `ocp_install_api_version`
* `ocp_install_base_domain`
* `ocp_install_compute`
* `ocp_install_control_plane`
* `ocp_install_fips`
* `ocp_install_image_content_sources`
* `ocp_install_metadata`
* `ocp_install_networking`
* `ocp_install_platform`
* `ocp_install_proxy`
* `ocp_install_publish`
* `ocp_install_pull_secrets`
* `ocp_install_ssh_pubkey`

If using the default template, this role will raise an error if any required variables
are not defined.

See some detailed usage of these vars in the [Examples] section below. More information
about them can also be found in the [openshift-install customization] docs.

**Note**: If using a pre-made `install-config.yaml`, set `ocp_install_config_template`
to the location of the pre-made file on the Ansible control machine. Ansible templating
will still be done using this file, but if no `{{ vars }}` are referenced in the file,
no replacement will be done.

### Create Cluster

A basic version of the `openshift-install create cluster` subcommand is supported
by this role. The following vars are supported for these purpose:

* `ocp_install_create_cluster` - Default: `false`. If `true`, the `openshift-install
  create cluster` subcommand will be run as described below.
* `ocp_install_destroy_cluster_on_failure`: Default `false`. If `true`, the role will
  run `openshift-install destroy cluster` to clean up created resources before exiting.

Specifically, this documented invocation in the OSP 4.x installation documentation
will be run if `ocp_install_create_cluster` is set to `true`:

```
openshift-install create cluster --dir=<ocp_install_config_dir> \
    --log-level=<ocp_install_log_level>
```

### Destroy Cluster

In addition to creating a cluster, `openshift-install destroy cluster` is also
supported.

* `ocp_install_destroy_cluster` - Default: `false`. If `true`, the `openshift-install
  destroy cluster` subcommand will be run.

This command should only be run in an `ocp_install_config_dir` where an installation has
already been attempted, and is included here for use in automation, where a created
cluster is expected to be destroyed at the end of a test run.

To automatically destroy a cluster if creation fails, set
`ocp_install_destroy_cluster_on_failure` to `true` as described in the previous section.

### async

Because both the `create cluster` and `destroy cluster` commands take a while to run, and
in particular may take longer than the underlying connection timeout, async polling is used
on these processes. By default, this role will wait 3600 seconds (one hour) for these commands
to complete, polling every 10 seconds. These values can be changed as-needed with the following
role variables:

* `ocp_install_async_timeout` - Total number of seconds to wait for an async command to complete,
  default `3600` seconds.
* `ocp_install_async_poll` - How frequently to poll an async command for completion, default `10`
  seconds.

### Privilege Escalation

Escalation is not required for this role, but can be done using these vars
if needed:

* `ocp_install_become` - Default: false. If this role needs administrator
  privileges, then use the Ansible become functionality (based off sudo).
* `ocp_install_become_user` - Default: root. If the role uses the become
  functionality for privilege escalation, then this is the name of the target
  user to change to.

Dependencies
------------

None

Example Playbooks
-----------------

### Basic Example

Directly download with absolute URL to archive, and install `openshift-install` binary
to default PATH dir (defined in `ocp_install_path`)

```yaml
- hosts: ocp_install
  vars:
    ocp_install_url: 'https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/openshift-install-linux-4.2.4.tar.gz'
  roles:
    - role: oasis_roles.ocp_install
```

### Using `index_href`

Use the [index_href] role to automatically determine latest OCP Client archive URL:

```yaml
- hosts: ocp_install
  vars:
    # trailing slash is important here
    ocp_installers_index_url: https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/
    ocp_installers_index: "{{ query('url', ocp_installers_index_url) }}"
    ocp_install_url: >-
        {{ query('index_href', ocp_installers_index, 'install-linux',
           base_url=ocp_installers_index_url) }}
  roles:
    - oasis_roles.ocp_install
    - oasis_roles.index_href
```

**Note**: This example is subject to change if the file naming scheme used in the
OCP Clients download index changes.

### Generating the install config and running `create cluster`

If generating the `install-config.yaml` using this role, the following example
playbook demonstrates the expected data structures for template vars used in
[the default template] provided by this role. This example also demonstrates
running `openshift-install create cluster`, gathering pull secrets with the
[ocp_pull_secrets] role, and writing its output in a play task using the
`ocp_install_create_cluster_cmd` registered fact.

```yaml
- hosts: ocp_install
  vars:
    # see ocp_pull_secrets docs for how to get this token
    ocp_pull_secrets_offline_token: "{{ lookup('env', 'OCP_PULL_SECRETS_OFFLINE_TOKEN') }}"
    # determine install url from mirror.openshift.com clients index
    # don't forget the url trailing slash
    ocp_installers_index_url: https://mirror.openshift.com/pub/openshift-v4/clients/ocp/latest/
    ocp_installers_index: "{{ query('url', ocp_installers_index_url) }}"
    ocp_install_url: >-
        {{ query('index_href', ocp_installers_index, 'install-linux',
           base_url=ocp_installers_index_url) }}
    # generate a config and attempt to create a cluster
    ocp_install_generate_config: true
    ocp_install_create_cluster: true
    # mandatory template vars when using default template
    ocp_install_api_version: v1
    ocp_install_base_domain: example.com
    ocp_install_compute:
      - hyperthreading: Enabled
        name: worker
        replicas: 0
    ocp_install_control_plane:
      hyperthreading: Enabled
      name: master
      replicas: 3
    ocp_install_metadata:
      name: test
    ocp_install_networking:
      clusterNetwork:
        - cidr: 10.128.0.0/14
          hostPrefix: 23
      networkType: OpenShiftSDN
      serviceNetwork:
        - 172.30.0.0./16
    ocp_install_platform:
      none: {}
    ocp_install_pull_secrets: "{{ ocp_pull_secrets }}"
    ocp_install_config_dir: '/path/to/ocp_install/config_dir'
    ocp_install_ssh_pubkey: 'AAAAFakePubkey=='
  roles:
    - oasis_roles.ocp_pull_secrets
    - oasis_roles.ocp_install
  tasks:
    - name: Write out create cluster logs
      delegate_to: localhost
      # will write `openshift-install create cluster` stdout
      # and stderr to separate files on the ansible control system
      copy:
        content: "{{ ocp_install_create_cluster_cmd[item] }}"
        dest: "/path/to/log_dir/openshift-install-{{ item }}.log"
      loop:
        - stdout
        - stderr
```

License
-------

GPLv3

Author Information
------------------

Sean Myers <semyers@redhat.com>

[the default template]: https://github.com/oasis-roles/ocp_install/blob/master/templates/ocp_install_default_config.yaml
[Examples]: #example-playbooks
[openshift-install customization]: https://github.com/openshift/installer/blob/master/docs/user/customization.md#platform-customization
[index_href]: https://github.com/oasis-roles/index_href
[ocp_pull_secrets]: https://github.com/oasis-roles/ocp_pull_secrets
