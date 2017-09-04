#!/usr/bin/env python
"""
Extract a bibtex entry of an arXiv paper
"""

from __future__ import print_function, with_statement
import sys
from grab import *
from bibtexparser.bparser import BibTexParser
from grab import getxml, find1, readurl
from bib import create_entry
# from bibtexparser import dumps


def fetch_entry(url):
    xml = getxml(url)
    pdfurl = find1(xml, "//x:meta[@name = 'citation_pdf_url']/@content")
    biburl = find1(xml, "//x:a[contains(text(), 'BibTeX (.BIB)')]/@href")
    bibtex = readurl(biburl).decode('utf-8').replace("﻿", "")
    return create_entry(bibtex, pdfurl)


def bibentry(url):
    return dumps(fetch_entry(url))


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: %s <spring-url>" % sys.argv[0], file=sys.stderr)
        exit(1)

    print(bibentry(sys.argv[1]))
