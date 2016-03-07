from lxml import etree
from io import BytesIO
import subprocess as sp
import os
import re
import sys
import json

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
    from urllib.parse import urlencode, unquote  # py3k
except ImportError:
    from urllib import urlencode, unquote

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
    raise "not implemented, yet..."


def error(msg):
    raise RuntimeError(msg)


def import_pdf(fname, open_browser=True):
    """
    Run pdfgrep and search for DOI.
    If one is found, redirect to the publishers website.
    If open_browser, show the corresponding web page.
    """
    try:
        dois = sp.check_output(['pdfgrep', '-i', 'DOI', fname]).decode('utf-8')
        DOI_REGEX = ".*doi.+(10\\.\d{4,6}/[^\"'&<% \t\n\r\f\v]+).*"
        m = re.match(DOI_REGEX, dois, flags=re.I) or error('Could not find DOI')
        doi = m.group(1)
        print("DOI : " + doi, file=sys.stderr)
        info = readurl("http://doi.org/api/handles/{0}".format(doi)).decode('utf-8')
        info = json.loads(info)
        url = info['values'][0]['data']['value']
    except sp.CalledProcessError:
        print(os.getcwd())
        pass
