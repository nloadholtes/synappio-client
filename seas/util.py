import re

re_wildcard = re.compile(r'(\{[a-zA-Z][^\}]*\})')


def pattern_for(path):
    '''Convert a swagger path spec to a url'''
    if not path.startswith('/'):
        path = '/' + path
    parts = re_wildcard.split(path)
    pattern_parts = []
    for part in parts:
        if re_wildcard.match(part):
            pattern_parts.append('(.*)')
        else:
            pattern_parts.append(re.escape(part))
    return re.compile(''.join(pattern_parts) + '$')

