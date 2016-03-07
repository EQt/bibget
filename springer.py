#!/usr/bin/env python
"""
Extract a bibtex entry of an arXiv paper
"""

from __future__ import print_function, with_statement
import sys
from grab import *
from bibtexparser.bparser import BibTexParser
from grab import getxml
from bib import *
# from bibtexparser import dumps


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
