from lxml import etree
from io import BytesIO
import subprocess as sp
import os
import re
import sys
import json
from bib import pdfloc, dumps, entry_exists

try:
    from urllib.request import urlopen
    def readurl(url):
        return urlopen(unquote(url)).read()
except ImportError:
    from urllib2 import urlopen
    def readurl(url):
        return urlopen(unquote(url)).read()

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')
try:
    from urllib.parse import urlencode, unquote, urlparse  # py3k
except ImportError:
    from urllib import urlencode, unquote, urlparse

def tidy_html(html):
    """
    Although there is a lib for it (https://pypi.python.org/pypi/pytidylib),
    I prefer to call tidy myself.
    """
    opts = {"stdout": sp.PIPE,
            "stderr": DEVNULL,
            "stdin": sp.PIPE}
    proc = sp.Popen("tidy --force-output 1 -asxhtml -utf8 -q".split(), **opts)
    out, err = proc.communicate(input=html)
    return out.replace(b"&nbsp;", b" ")


def getxml(url):
    html = readurl(url)
    xml = tidy_html(html)
    return etree.parse(BytesIO(xml))

def findx(xml, path):
    ns = {'x': 'http://www.w3.org/1999/xhtml'}
    return xml.xpath(path, namespaces=ns)


def retrieve(url):
    return dumps(fetch_entry(url))

def fetch_entry(url):
    import springer
    urlp = urlparse(url)
    if urlp.netloc == 'link.springer.com':
        return springer.fetch_entry(url)
    raise RuntimeError("don't know how to handle %s" % url)


def error(msg):
    raise RuntimeError(msg)


def find_doi(fname):
    dois = sp.check_output(['pdfgrep', '-i', 'DOI', fname]).decode('utf-8')
    DOI_REGEX = ".*doi.+(10\\.\d{4,6}/[^\"'&<% \t\n\r\f\v]+).*"
    m = re.match(DOI_REGEX, dois, flags=re.I) or error('Could not find DOI')
    return m.group(1)
    

def doi2url(doi):
    info = readurl("http://doi.org/api/handles/{0}".format(doi)).decode('utf-8')
    info = json.loads(info)
    return info['values'][0]['data']['value']


def import_pdf(fname, PDF_DIR, BIBFILE, open_browser=False):
    """
    Run pdfgrep and search for DOI.
    If one is found, redirect to the publishers website.
    If open_browser, show the corresponding web page.
    """
    try:
        doi = find_doi(fname)
        print("DOI : " + doi, file=sys.stderr)
        url = doi2url(doi)
        print("URL : " + url, file=sys.stderr)
        if open_browser:
            from webbrowser import open_new_tab
            open_new_tab(url)
        entry = fetch_entry(url)
        print(BIBFILE)
        if entry_exists(BIBFILE, entry):
            print("Already have it")
        else:
            pdfout = pdfloc(entry, PDF_DIR)
            print(pdfout)
    except sp.CalledProcessError:
        print(os.getcwd())
        pass
