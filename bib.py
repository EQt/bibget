# -*- coding: utf-8 -*-
# -*- mode: python; -*-
"""
Some utility functions...
"""
from __future__ import unicode_literals, print_function
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import io


def bibstring(bibs):
    if bibs.startswith("\ufeff"):
        bibs = bibs[1:]
    return BibTexParser(bibs, customization=convert_to_unicode)

def bibparse(bibpath):
    with io.open(bibpath, 'r', encoding='utf-8') as bibfile:
        return bibstring(bibfile.read())

def create_entry(bibtex, pdfurl=None):
    bibtex = bibtex.replace("@Article", "@article")
    bp = bibstring(bibtex)
    delete = ["abstract", "url", "keyword", "keywords", "link"]
    try:
        entry = bp.get_entry_list()[0]
        for d in delete:
            entry.pop(d, None)
        if pdfurl is not None:
            entry["pdf"] = pdfurl
        entry["author"] = tex2utf8(entry["author"])
        if "year" not in entry: return entry
        setid(entry)
        return entry
    except:
        raise RuntimeError('Error processing ' + bibtex)
        pass


def tex2utf8(s):
    repls = [('{\\\"o}', 'ö'),
             ('{\\\"a}', 'ä'),
             ('{\\\"u}', 'ü'),
             ('{\\`a}',  'à'),
             (' AND ', ' and ')]
    for o, n in repls:
        s = s.replace(o, n)
    return s

def utf82e(s):
    s = s.replace('ö', 'oe')
    s = s.replace('ä', 'ae')
    s = s.replace('ü', 'ue')
    s = s.replace('ß', 'ss')
    s = s.replace('ó', 'o')
    s = s.replace('á', 'a')
    s = s.replace('à', 'a')
    s = s.replace('é', 'e')
    return s

def lastname(name):
    """Compute the last name of full name n"""
    p = name.strip().split(",")
    if len(p) >= 2:
        return p[0].strip()
    else:
        p = name.split(" ")
        return p[-1].strip()


def setid(entry):
    entry["author"] = entry["author"].replace("\n", " ")
    authors = entry["author"].split(" and ")
    authors = list(map(lambda s: s.strip(), authors))
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
    def line(l):
        if l.startswith("http://"): return l
        if "\n" in l:
            if indent in l: return l
            else:
                return l.replace("\n", indent)
        return indent.join(textwrap.wrap(l, 80 - width))
    form = lambda s: formatter % (s + " = ", '{%s}' % line(entry[s]))
    entry['author'] = entry['author'].replace("\n", " ")
    entry['author'] = entry['author'].replace("and ", "and" + indent)
    s = s + form('title') + form('author')
    labels = set(labels) - set(['title', 'author'])
    for l in labels:
        s = s + form(l)
    return s + "\n}\n\n"


def entry_exists(fname, entry):
    """
    Check whether the entry exists in bibtex file fname
    """
    if not isinstance(entry, dict):
        entry = BibTexParser(entry).get_entry_list()[0]
    entry_id = entry['ID']
    entries = bibparse(fname).get_entry_dict()
    return entry_id in entries.keys()


def prepend(fname, entry):
    """
    Prepend string entry if it does not exist in fname as bibtex entry
    """
    if entry_exists(fname, entry):
        print("There already exists an bibtex entry '%s'!" % entry_id,
              file=sys.stderr)
        return
    bibf = open(fname).read()
    with open(fname, "w") as b:
        b.write(entry)
        b.write(bibf)
