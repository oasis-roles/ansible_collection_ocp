[![Build Status](https://travis-ci.com/oasis-roles/ocp_cloud_dns.svg?branch=master)](https://travis-ci.com/oasis-roles/ocp_cloud_dns)

ocp_cloud_dns
=============

Role to set up DNS records for OpenShift Container Platform 4.x in a cloud DNS zone.

Currently only GCP is supported, but AWS and Azure support are coming soon.

Requirements
------------

Ansible 2.9 or higher

Red Hat Enterprise Linux or equivalent

Valid Red Hat Subscriptions

Role Variables
--------------

Currently the following variables are supported by all cloud DNS providers,
and provider-specific variables can be found below.

### General

- `ocp_cloud_dns_domain` - The domain in which DNS records will be created. Required.
- `ocp_cloud_dns_state` - One of `present` or `absent`, decides whether to create resource records
  (`present`), or whether to destroy resource records (`absent`), default `present`.
- `ocp_cloud_dns_create_zone` - When `true` and `ocp_cloud_dns_state` is `present`, create the DNS zone
  in the cloud provider for `ocp_cloud_dns_domain`. Leave set to the default `false` to add records to
  an existing zone.
- `ocp_cloud_dns_destroy_zone` - When `true` and `ocp_cloud_dns_state` is `absent`, destroy the DNS zone
  in the cloud provider for `ocp_cloud_dns_domain`. Leave set to the default `false` to only clean up
  records in an existing zone.
- `ocp_cloud_dns_parent_domain` - If set, NS records delegating authority to `ocp_cloud_dns_domain` zone
  will be added/updated in this parent zone.

### Resource Records

- `ocp_cloud_dns_lb_hosts_v4` - A mapping of domain names, relative to `ocp_cloud_dns_domain`, to the
  address records to create for each domain name. The mapping key is expected to be one of the load
  balancer names, and the value is expected to be a single IPv4 address, or an array of them, for each
  load balancer host's `A` record set. Note that due to the asterisk, the `*.apps` load balancer key
  must be quotes.
- `ocp_cloud_dns_lb_hosts_v6` - Exactly the same as `ocp_cloud_dns_lb_hosts_v4`, but `AAAA` record sets
  are generated for IPv6 addresses.
- `ocp_cloud_dns_etcd_hosts_v4` - A mapping of domain names, relative to `ocp_cloud_dns_domain`, to
  the IPv4 `A` records to create for each etcd host in the ocp cluster. Unlike in the `lb_hosts` mappings,
  values in this mapping must be single address strings, not arrays. In addition to creating the `A` address
  records for the etcd hosts, these hosts will be automatically be combined into the correct etcd `SRV`
  records needed by the OCP 4 cluster.
- `ocp_cloud_dns_etcd_hosts_v6` - Exactly the same as `ocp_cloud_dns_etcd_hosts_v4`, but `AAAA` record sets
  are generated for IPv6 addresses.

### GCP

#### Authentication

All tasks that interact with GCP support all authentication parameters common to all GCP Ansible
modules, expected to be defined in the `ocp_cloud_dns_gcp` mapping. Which ones you use (including
None, if you are using environment variables to configure Ansible) are specific to your implementation,
all possible params are listed here:

```yaml
# accepted params for ocp_cloud_dns_gcp
ocp_cloud_dns_gcp:
  auth_kind:
  env_type:
  project:
  scopes:
  service_account_contents:
  service_account_email:
  service_account_file:
```

#### Zone creation configuration

If creating the `ocp_cloud_dns_domain` zone with `ocp_cloud_dns_create_zone` set to true, the
`ocp_cloud_dns_gcp_zone` mapping is used. GCP requires `name` and `description` to create that zone,
and all other params accepted by the [gcp_dns_managed_zone] Ansible module can be used in the
`ocp_cloud_dns_gcp_zone` dictionary.

```yaml
ocp_cloud_dns_gcp_zone:
  # required to create a gcp zone
  name: zone-resource-name
  description: sadly required
  # optional zone params
  dnssec_config:
  labels:
  name_server_set: 
  private_visibility_config:
  visibility:
```


Dependencies
------------

The python libraries required by the cloud DNS Ansible modules being used must be installed.

Example Playbook
----------------

### GCP

Create a new zone, "oasis.parentzone.example.com", and also create NS records in the parent
zone to delegate authority to the new zone.

```yaml
- hosts: ocp_cloud_dns-servers
  roles:
    - role: oasis_roles.ocp_cloud_dns
  vars:
    ocp_cloud_dns_state: present
    ocp_cloud_dns_create_zone: true
    ocp_cloud_dns_domain: parentzone.example.com
    ocp_cloud_dns_parent_domain: oasis.parentzone.example.com
    ocp_cloud_dns_no_log: false
    ocp_cloud_dns_lb_hosts_v4:
      # single strings work
      '*.apps': 127.0.0.2
      api: 127.0.0.1
      api-int: 127.0.1.1
    ocp_cloud_dns_lb_hosts_v6:
      # arrays also work
      '*.apps':
        - ::2
      api:
        - ::1
      api-int:
        - ::1:1
    # do not use array values with etcd hosts
    ocp_cloud_dns_etcd_hosts_v4:
      etcd0: 127.0.1.2
    ocp_cloud_dns_etcd_hosts_v6:
      etcd0: ::1:2
    # gcp-specific auth using a serviceAccount
    ocp_cloud_dns_gcp:
      project: project-12345
      auth_kind: serviceaccount
      service_account_file: "/path/to/serviceAccount.json"
    # required name and description for created zone
    ocp_cloud_dns_gcp_zone:
      name: gcpdnszone-molecule
      description: Test zone for gcp_dns_zone role default molecule scenario
  roles:
    - role: ocp_cloud_dns
```

License
-------

GPLv3

Author Information
------------------

Sean Myers <sean.myers@redhat.com>

[gcp_dns_managed_zone]: https://docs.ansible.com/ansible/latest/modules/gcp_dns_managed_zone_module.html
