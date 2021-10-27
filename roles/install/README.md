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
are not defined. Even if all variables are defined, it's still possible for the
`openshift-install` command to block on user input. It is recommended to run
`openshift-install create install-config` manually to ensure all of the potentially
blocking user prompts are answered before converting the generated `install-config.yaml`
to ansible vars for use with this role.

See some detailed usage of these vars in the [Examples] section below. More information
about them can also be found in the [openshift-install customization] docs.

**Note**: If using a pre-made `install-config.yaml`, set `ocp_install_config_template`
to the location of the pre-made file on the Ansible control machine. Ansible templating
will still be done using this file, but if no `{{ vars }}` are referenced in the file,
no replacement will be done.

### Create Cluster for Installer-Provisioned Infrastructure

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

### Generating manifests and ignition configs for User-Provisioned Infrastructure

* `ocp_install_create_manifests` - Default: `false`. If `true`, run
  `openshift-install create manifests`, writing manifests to `ocp_install_config_dir`.
* `ocp_install_create_ignition_configs` - Default: `false`. If `true`, run
  `openshift-install create ignition-configs`, writing the `.ign` files to
  `ocp_install_config_dir`.

While editing the manifests is not directly supported by this role, note that this
role can be invoked multiple times, if needed, to accomodate workflow customizations.

Here's basic playbook example of this sort of customization:

```yaml
- name: Generate manifests and customize them
  hosts: ocp_installers
  roles:
    - name: oasis_roles.ocp_install
      # this example assumes the install-config has already been generated
      ocp_install_create_manifests: true
  tasks:
    - name: Update cluster scheduler to prevent scheduling masters
      lineinfile:
        state: present
        path: "{{ ocp_install_config_dir }}/manifests/cluster-scheduler-02-config.yml"
        regexp: '(\s+mastersSchedulable:)'
        backrefs: yes
        # result should be a correctly-indented 'mastersSchedulable: false'
        line: '\1 false'

- name: Generate ignition configs
  hosts: ocp_installers
  roles:
    - name: oasis_roles.ocp_install
      # this example assumes the install-config has already been generated
      ocp_install_create_ignition_configs: true
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

### Credentials Installation

For each platform, `openshift-install` looks for that platform's credentials in a specific
and predictable location. Each platform's credentials file can be installed by naming a
file local to the Ansible control machine to use in that platform's corresponding
`ocp_install_*_creds_file` role variable. **Note that credentials files on the target
machine(s) will be overwritten when configured to do so with these variables.**

When not provided via the OpenShift Container Platform installation documentation,
example credentials files have been provided.

#### AWS

* `ocp_install_aws_creds_file` - Credentials file on Ansible control machine to copy to
  the host running `openshift-install` to allow the installer to access this platform,
  containing an AWS account access key pair.

Example Format:
```ini
; https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html
[default]
aws_access_key_id     = your_access_key_id_here
aws_secret_access_key = your_secret_access_key_here
```

#### Azure

* `ocp_install_azure_creds_file` - Credential file on Ansible control machine to copy to
  the host running `openshift-install` to allow the installer to access this platform,
  containing Azure Service Principal credentials.

Example Format:
```
{
    "subscriptionId": "put",
    "clientId": "your",
    "clientSecret": "credentials",
    "tenantId": "here"
}
```

#### GCP

* `ocp_install_gcp_creds_file` - Credential file on Ansible control machine to copy to
  the host running `openshift-install` to allow the installer to access this platform,
  containing GCP Service Account credentials.

Example Format:
```yaml
{
  "type": "service_account",
  "project_id": "project",
  "private_key_id": "0000000000000000000000000000000000000000",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n",
  "client_email": "your@project.iam.gserviceaccount.com",
  "client_id": "12345",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your%40project.iam.gserviceaccount.com"
}
```

#### OpenStack

* `ocp_install_openstack_creds_file` - Credential file on Ansible control machine to copy
  to the host running `openshift-install` to allow the install access to this platform,
  which is expected to be a working [clouds.yaml] file.

Splitting secrets is not supported by this role; only `clouds.yaml` is supported, not
`secure.yaml`. The cloud, or one of the clouds, defined in this file should match the
cloud named in the `ocp_install_platform`, and other `install-config.yaml` values that
reference OpenStack clouds by their defined name in `clouds.yaml`.

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

Idempotence and Usage
---------------------

The tool that this role wraps is not idempotent, and as a result this role is also not
written to be idempotent. This is mostly due to `openshift-install` being stateful
during operation, and also due to its consumption of any generated `install-config.yaml`
when creating clusters, manifests, or ignition configs.

Furthermore, for the sake of flexibility, this role does not enforce a given order of
operations; all steps should be run in the correct order if run in a single play, but
this role will not (for example) ensure that if you're using this role to `create
ignition-configs` that you aren't also attempting to run `create cluster`.

Finally, this role makes no attempt to prevent the `openshift-install` command from
blocking on user input. Manual verification of the desired configuration, by manually
invoking the `openshift-install create install-config` command, should be done to ensure
that all answers are given to `openshift-install` such that it does not prompt for user
input.

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

[the default template]: https://github.com/oasis-roles/ansible_collection_ocp/blob/main/roles/install/templates/ocp_install_default_config.yaml.j2
[Examples]: #example-playbooks
[openshift-install customization]: https://github.com/openshift/installer/blob/master/docs/user/customization.md#platform-customization
[ocp_pull_secrets]: https://github.com/oasis-roles/ocp_pull_secrets
[clouds.yaml]: https://access.redhat.com/documentation/en-us/openshift_container_platform/4.2/html/installing_on_openstack/installing-on-openstack#installation-osp-describing-cloud-parameters_installing-openstack-installer-custom
