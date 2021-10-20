from ansible.plugins.filter import core as ansible_filter
from jinja2 import filters as jinja_filter

mandatory_msg = "Mandatory ocp_install template var {} is not defined."


def indent_json(value, mandatory=False):
    '''Format a datastructure as json for us in the OCP install-config.yaml'''
    return indent(value, 'json', mandatory)


def indent_yaml(value, mandatory=False):
    '''Format a datastructure as yaml for us in the OCP install-config.yaml'''
    return indent(value, 'yaml', mandatory)


def indent(value, out_fmt, mandatory):
    indent = 2
    fmt_filter = getattr(ansible_filter, 'to_nice_{}'.format(out_fmt))

    if mandatory:
        value = ansible_filter.mandatory(value, msg=mandatory_msg)
    value = fmt_filter(value, indent=indent)
    value = jinja_filter.do_trim(value)
    value = jinja_filter.do_indent(value, width=indent, first=False)
    return value


class FilterModule(object):
    def filters(self):
        return {
            'ocp_install_json': indent_json,
            'ocp_install_yaml': indent_yaml
        }
