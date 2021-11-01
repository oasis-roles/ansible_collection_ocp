![Github CI Status](https://github.com/oasis-roles/index_href/workflows/Role%20CI/badge.svg)

index_href
===========

Provides a lookup plugin that can parse links in a web directory index
to get the URLs for a specific file that can then be used in later tasks.

Only URLs contained in anchor (the `a` tag) href properties are searched.

This plugin does not access the internet. It is intended to be used with
existing ansible mechanisms where possible. To get HTML content to parse
with this plugin, the builtin `url` lookup plugin or the builtin `uri`
module is recommended. To download hrefs returned by this plugin, the
builtin `uri` module is recommended.

Requirements
------------

Ansible 2.5 or higher

Red Hat Enterprise Linux 7 or equivalent

Valid Red Hat Subscriptions

Dependencies
------------

None

Usage
-----

`query` function signature for the lookup plugin provided by this role:

```yaml
query('index_href', html_content, match_str, [regex=False, base_url=''])
```

Positional arguments are required, keyword argument defaults are shown.

- **`html_content`** - HTML content to be parsed by the `index_href` lookup plugin.
  Can be a list like the one returned when querying with the `url` plugin, or a
  string of HTML from any source. *Required.*
- **`match_str`** - A substring to match against hrefs discovered in `html_content`.
  The first href containing the substring is returned. Behavior changes if `refex`
  is `True`.
- **`regex`** - If True, process `match_str` as a regular expression for more specific
  string matching. *Optional, default `false`*
- **`base_url`** - If set, will attempt to join the matching href with this base URL.
  For joining to work correctly with relative links in the parsed HTML, the `base_url`
  should include a trailing forward slash (`/`).

This plugin is only tested with the `query` function. Its behavior
when using `lookup` is undefined.

Example
-------

A basic play.

```yaml
- hosts: index_href-servers
  roles:
    # The lookup plugin is not loaded unless this role is included
    # at some point in the playbook, ideally before the plugin is used.
    - role: oasis_roles.index_href
  vars:
    # This var will also be used for base_url, note the trailing slash.
    index_url: http://hostname/path/to/directory/index/
    index_content: "{{ query('url', index_url) }}"
    target_substring: target.img
    image_destination: /path/to/downloaded/image
  tasks:
    - name: Search for target href in directory index using index_href query
      set_fact:
        # Calls to this plugin can result in some pretty long lines,
        # but the call can be broken up across multiple lines if
        # necessary using yaml block scalar syntax, as shown here.
        target_href: >
          {{ query('index_href', index_content, target_substring,
             base_url=index_url) }}
    - name: Simple example to use the target href with the uri module
      uri:
        url: "{{ target_href }}"
        path: "{{ image_destination }}"
        creates: "{{ image_destination }}"
```

License
-------

GPLv3

Author Information
------------------

Sean Myers <sean.myers@redhat.com>
