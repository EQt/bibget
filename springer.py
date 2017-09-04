#!/usr/bin/env python
"""
Find citation for a website https://link.springer.com/*
"""

from __future__ import print_function, with_statement
import sys
import argparse
from grab import *
from bibtexparser.bparser import BibTexParser
from grab import getxml, find1, readurl
from bib import create_entry, dumps


def fetch_entry(url):
    xml = getxml(url)
    pdfurl = find1(xml, "//x:meta[@name = 'citation_pdf_url']/@content")
    biburl = find1(xml, "//x:a[contains(text(), 'BibTeX (.BIB)')]/@href")
    bibtex = readurl(biburl).decode('utf-8').replace("﻿", "")
    return create_entry(bibtex, pdfurl)


def bibentry(url):
    return dumps(fetch_entry(url))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('url', type=str, help='URL to the abstract')
    args = p.parse_args()

    print(bibentry(args.url))
