"""
Some utility functions...
"""

import io

def dumps(entry):
    """
    Format bibtex entry as string
    """
    import textwrap

    if not isinstance(entry, dict):
        return dumps(entry.get_entry_list()[0])
    islow = lambda s: s[0].islower()
    labels = list(filter(islow, entry.keys()))
    width = 3 + max(map(len, labels))
    indent = "\n" + " " * (width + 4)
    formatter = ",\n  %%-%ds %%s" % width
    s = "@%s{%s" % (entry["ENTRYTYPE"], entry["ID"])
    line = lambda l: l if "\n" in l else indent.join(textwrap.wrap(l, 80 - width))
    form = lambda s: formatter % (s + " = ", '{%s}' % line(entry[s]))
    entry['author'] = entry['author'].replace("\n", " ")
    entry['author'] = entry['author'].replace("and ", "and" + indent)
    s = s + form('title') + form('author')
    labels = set(labels) - set(['title', 'author'])
    for l in labels:
        s = s + form(l)
    return s + "\n}\n\n"

