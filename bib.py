"""
Some utility functions...
"""
def tex2utf8(s):
    repls = [('{\\\"o}', 'ö'),
             ('{\\\"a}', 'ä'),
             ('{\\\"u}', 'ü'),
             ('{\\`a}',  'à')]
    for o, n in repls:
        s = s.replace(o, n)
    return s

def utf82e(s):
    s = s.replace('ö', 'oe')
    s = s.replace('ä', 'ae')
    s = s.replace('ü', 'ue')
    s = s.replace('ß', 'ss')
    return s

def lastname(name):
    """Compute the last name of full name n"""
    p = name.split(",")
    if len(p) >= 2:
        return p[0].strip()
    else:
        p = name.split(" ")
        return p[-1].strip()


def setid(entry):
    authors = entry["author"].split("and")
    if len(authors) > 3:
        bid = lastname(authors[0]) + "EtAl"
    else:
        bid = "".join(map(lastname, authors))
    entry['ID'] = utf82e(bid + ":" + str(entry["year"]))


def pdfloc(entry, pdf_dir):
    """Return the location of the corresponding PDF file"""
    pdfout = entry['ID'].replace(':', '_') + '.pdf'
    out_dir = pdf_dir
    if 'dir' in entry:
        out_dir = out_dir + entry['dir'].replace('/', '') + '/'
    return out_dir + pdfout


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

