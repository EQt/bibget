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


def fetch_entry(url):
    xml = getxml(url)

    pdfurl = findx(xml, "//x:meta[@name = 'citation_pdf_url']/@content")[0]
    biburl = findx(xml, "//x:a[contains(text(), 'BibTeX (.BIB)')]/@href")[0]
    bibtex = readurl(biburl).decode('utf-8').replace("﻿", "")

    return create_entry(bibtex, pdfurl)


def fetch_acs(url):
    import requests
    s = requests.Session()
    pdfurl = url.replace('/abs/', '/pdf/')
    action = 'http://pubs.acs.org/action/downloadCitation'
    # POST DATA
    data = {
        'direct': 'true',
        'doi': doi,
        'downloadFileName': 'achs_ancham84_2622',
        'format': 'bibtex',
        'include': 'cit',
        'submit': 'Download+Citation(s)'
    }


def bibentry(url):
    return dumps(fetch_entry(url))


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: %s <spring-url>" % sys.argv[0], file=sys.stderr)
        exit(1)

    print(bibentry(sys.argv[1]))
