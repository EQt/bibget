from __future__ import print_function
from lxml import etree
from io import BytesIO
import subprocess as sp
import os
import re
import sys
import json
from bib import pdfloc, dumps, entry_exists, prepend, create_entry, \
    bibstring, setid
from prompt import ask
import shutil

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
try:
    from urllib.parse import urlencode, unquote, urlparse  # py3k
except ImportError:
    from urllib import urlencode, unquote
    from urllib2 import urlparse


def readurl(url, expect_html=False):
    net = urlopen(unquote(url))
    if expect_html:
        from mimetypes import guess_extension
        ctype = net.info()["Content-Type"].split(";")[0]
        ex = guess_extension(ctype)
        if ex not in [".htm", ".xml", ".html"]:
            raise ValueError("Expted HTML (not {}, ie {}) for '{}'".
                             format(ex, ctype, url))
    return net.read()


try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')


def tidy_html(html):
    """
    Although there is a lib for it (https://pypi.python.org/pypi/pytidylib),
    I prefer to call tidy myself.
    """
    opts = {"stdout": sp.PIPE,
            "stderr": DEVNULL,
            "stdin": sp.PIPE}
    try:
        proc = sp.Popen("tidy --force-output 1 -asxhtml -utf8 -q".split(), **opts)
        out, err = proc.communicate(input=html)
        return out.replace(b"&nbsp;", b" ")
    except FileNotFoundError as e:
        if str(e).endswith("No such file or directory: 'tidy'"):
            print("ERRROR: Please install `tidy`.")
            exit(3)
        else:
            raise


def getxml(url):
    """
    Retrieve the html/xml document located at `url`,
    tidy it and return an XML tree
    """
    html = readurl(url, True)
    xml = tidy_html(html)
    return etree.parse(BytesIO(xml))


def findx(xml, path):
    """Search xpath in xml (prepend namespace 'x')"""
    ns = {'x': 'http://www.w3.org/1999/xhtml'}
    return xml.xpath(path, namespaces=ns)


def find1(xml, path):
    """Like `findx` but return unique element (assert that)"""
    findings = findx(xml, path)
    assert len(findings) == 1, "Found %d" % len(findings)
    return findings[0]


def retrieve(url, BIBFILE):
    """
    Retrieve a bibtex entry located at url, and return it formatted
    """
    # if re.match("https?://scholar.google.+"):
    return dumps(fetch_entry(url, BIBFILE))


def error(msg):
    raise RuntimeError(msg)


def find_arXiv_bib(url):
    """
    Return bibtex entry of given arXiv url (as str)
    """
    m = re.match("https?\://arxiv\.org/(abs|pdf)/(.+?)(\.pdf|\.html)?$", url)
    arXiv_url = "http://arxiv.org/abs/%s" % m.group(2)
    xml = getxml(arXiv_url)
    pdfurl = findx(xml, "//x:meta[@name = 'citation_pdf_url']/@content")[0]
    arXiv_id = findx(xml, "//x:meta[@name = 'citation_arxiv_id']/@content")[0]
    query = urlencode({'format': 'bibtex', 'q': arXiv_id})
    xml = getxml('https://arxiv2bibtex.org/?' + query)
    bibs = findx(xml, '//x:textarea[contains(text(), "Author =")]/text()')[0]
    entry = bibstring(bibs).get_entry_list()[0]
    entry["note"] = "Preprint on\narXiv:\href{%s}{%s}" % (pdfurl, arXiv_id)
    return entry, pdfurl


def fetch_entry(url, BIBFILE, doi=None):
    import springer
    urlp = urlparse(url)
    pdfurl = None
    if urlp.netloc == 'link.springer.com':
        entry = springer.fetch_entry(url)
    elif urlp.netloc == 'arxiv.org':
        entry, pdfurl = find_arXiv_bib(url)
    else:
        pdfurl = ask('PDF   ')
        url = ask('BIBTEX')
        if url == 'local':
            bibtex = open('local').read()
            if bibtex[0] == '\ufeff':
                bibtex = bibtex[1:]
            print(bibtex)
        else:
            bibtex = readurl(url).decode('utf-8')
        entry = create_entry(bibtex, pdfurl)
    if doi is not None:
        entry['doi'] = doi
    if pdfurl is not None:
        import_bib(None, None, BIBFILE, pdfurl=pdfurl, entry=entry)
    return entry


def find_doi(fname):
    dois = sp.check_output(['pdfgrep', '-i', 'DOI', fname]).decode('utf-8')
    DOI_REGEX = ".*doi.+(10\\.\d{4,6}/[^\"'&<% \t\n\r\f\v]+).*"
    m = re.match(DOI_REGEX, dois, flags=re.I) or error('Could not find DOI')
    doi = m.group(1)
    if doi[-1] == '.':
        doi = doi[0:-1]
    return doi


def doi2url(doi):
    info = readurl("http://doi.org/api/handles/{0}".
                   format(doi)).decode('utf-8')
    info = json.loads(info)
    return info['values'][0]['data']['value']


def import_pdf(fname, PDF_DIR, BIBFILE, open_browser=True):
    """
    Run pdfgrep and search for DOI.
    If one is found, redirect to the publishers website.
    If open_browser, show the corresponding web page.
    """
    try:
        print("PDF : " + fname, file=sys.stderr)
        doi = find_doi(fname)
        print("DOI : " + doi, file=sys.stderr)
        url = doi2url(doi)
        print("URL : " + url, file=sys.stderr)
        if open_browser:
            from webbrowser import open_new_tab
            open_new_tab(url)
        entry = fetch_entry(url, doi=doi)
        if entry_exists(BIBFILE, entry):
            print("Already have ID", file=sys.stderr)
        else:
            prepend(BIBFILE, dumps(entry))
        pdfout = pdfloc(entry, PDF_DIR)
        if not os.path.isfile(pdfout):
            shutil.copy(fname, pdfout)
            print(pdfout)

    except sp.CalledProcessError:
        print(os.getcwd())
        pass


def import_bib(fname, PDF_DIR, BIBFILE, pdfurl=None, entry=None):
    if fname is not None:
        print(fname)
    if entry is None:
        entry = open(fname).read()
    if isinstance(entry, dict):
        entry = dumps(entry)
    # print(entry)
    entry = create_entry(entry, pdfurl)
    if 'year' not in entry:
        entry["year"] = ask("Year")
        setid(entry)
    if 'pdf' not in entry:
        if pdfurl is None:
            entry["pdf"] = ask("PDF")
        else:
            entry["pdf"] = pdfurl
    direct = ask("DIR")
    entry["dir"] = direct
    while entry_exists(BIBFILE, entry):
        last = entry['ID'][-1]
        if not last.isalpha():
            last = chr(96)
            entry['ID'] += "x"
        entry['ID'] = entry['ID'][:-1] + chr(ord(last)+1)
        print("Already have ID. Renaming to %s" % entry['ID'], file=sys.stderr)
    entrys = dumps(entry)
    print(entrys)
    prepend(BIBFILE, entrys)
    if fname is not None:
        answer = ask('Delete "%s"? (yN)' % fname)
        if answer == 'y':
            os.remove(fname)
