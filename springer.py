#!/usr/bin/env python
"""
Extract a bibtex entry of an arXiv paper
"""

from __future__ import print_function, with_statement
import sys
from grab import *
from bibtexparser.bparser import BibTexParser
import textwrap
# from bibtexparser import dumps

def tex2utf8(s):
    s = s.replace('{\\\"o}', 'ö')
    s = s.replace('{\\\"a}', 'ä')
    s = s.replace('{\\\"u}', 'ü')
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


def bibid(entry):
    authors = entry["author"].split("and")
    if len(authors) > 3:
        bid = lastname(authors[0]) + "EtAl"
    else:
        bid = "".join(map(lastname, authors))
    entry['ID'] = utf82e(bid + ":" + str(entry["year"]))


def dumps(entry):
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


def bibentry(url):
    xml = getxml(url)

    pdfurl  = findx(xml, "//x:meta[@name = 'citation_pdf_url']/@content")[0]
    biburl  = findx(xml, "//x:a[contains(text(), 'BibTeX (.BIB)')]/@href")[0]
    bibtex = readurl(biburl).decode('utf-8').replace("﻿", "")

    bp = BibTexParser(bibtex)
    entry = bp.get_entry_list()[0]

    entry.pop("abstract", None)
    entry.pop("url", None)
    entry["pdf"] = pdfurl
    entry["author"] = tex2utf8(entry["author"])
    bibid(entry)

    return dumps(bp)



if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: %s <spring-url>" % sys.argv[0], file=sys.stderr)
        exit(1)

    print(bibentry(sys.argv[1]))