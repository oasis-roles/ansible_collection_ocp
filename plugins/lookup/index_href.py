# Copyright 2019 Red Hat, Inc.
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re

from ansible.errors import AnsibleError, AnsibleLookupError
from ansible.module_utils.six import string_types
from ansible.plugins.lookup import LookupBase

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin

# this pattern is here so that we don't have to bring in something
# like beautiful soup as an additional dependency.
# this should match:
#  <a href="link">
#  <a href='link'>
#  <a href =   "link">
#  <a class="someclass" href="link" id="someid">
# this will not match:
#  <a href=unquoted>
#  <a id="nohref">
href_pattern = re.compile(r'''(?i)<a.*?href\s*?=\s*?['"](.+?)['"].*?>''')


class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        if len(terms) != 2:
            raise AnsibleError(
                'index_href expects two positional arguments')

        if not all(map(lambda s: isinstance(s, string_types), terms[0])):
            raise AnsibleError(
                'index_href first positional argument must be a string'
                ' or list of strings')

        if not isinstance(terms[1], string_types):
            raise AnsibleError(
                'index_href second positional argument must be a string')

        # content is intended to be from the output of a 'url' lookup,
        # which by default returns a list, but can also be a string.
        # for simplicity's sake below, collapse content down to a single string
        content = ''.join(terms[0])
        match_str = terms[1]
        regex = bool(kwargs.get('regex'))
        base_url = kwargs.get('base_url')

        hrefs = href_pattern.findall(content)

        if regex:
            # might as well compile this since it gets used
            # for each entry in the hrefs loop
            pattern = re.compile(match_str)

        for href in hrefs:
            if regex:
                if pattern.search(href):
                    break
            else:
                if match_str in href:
                    break
        else:
            raise AnsibleLookupError('No matching hrefs found')

        if base_url is not None:
            href = urljoin(base_url, href)

        return href
