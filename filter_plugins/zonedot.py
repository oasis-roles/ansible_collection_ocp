def zonedot(value, dot_required=True):
    if dot_required and not value.endswith('.'):
        value += '.'
    if not dot_required and value.endswith('.'):
        value = value.rstrip('.')
    return value


class FilterModule(object):
    def filters(self):
        return {
            'zonedot': zonedot,
        }
