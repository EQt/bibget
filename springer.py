#!/usr/bin/env python
"""
Find citation for a website https://link.springer.com/*
"""
import sys
import argparse
import re
from grab import readurl
from bib import create_entry, dumps


def fetch_entry(url):
    m = re.match('http.*article/(\d.+)', url)
    assert m is not None
    pref = m.group(1)
    pdfurl = 'https://link.springer.com/content/pdf/{}.pdf'.\
             format(pref.replace('/', '%2F'))
    biburl = 'https://citation-needed.springer.com/v2/references/' + \
             pref + '?format=bibtex&flavour=citation'
    bibtex = readurl(biburl).decode('utf-8').replace("﻿", "")
    return create_entry(bibtex, pdfurl)


def bibentry(url):
    return dumps(fetch_entry(url))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('url', type=str, help='URL to the abstract')
    args = p.parse_args()

    print(bibentry(args.url))
