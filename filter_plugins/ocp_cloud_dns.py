def zonedot(value, dot_required=True):
    # value must be a string
    # adds a trailing 'dot' for a DNS record by default,
    # ensures no trailing 'dot' if dot_required is False
    if dot_required and not value.endswith('.'):
        value += '.'
    if not dot_required:
        value = value.rstrip('.')
    return value


class FilterModule(object):
    def filters(self):
        return {
            'zonedot': zonedot
        }
