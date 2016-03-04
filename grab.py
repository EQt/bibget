from lxml import etree
from io import BytesIO
import subprocess as sp

try:
    from urllib.request import urlopen
    def readurl(url):
        return urlopen(url).readall()
except ImportError:
    from urllib2 import urlopen
    def readurl(url):
        return urlopen(url).read()

try:
    from subprocess import DEVNULL  # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')
try:
    from urllib.parse import urlencode  # py3k
except ImportError:
    from urllib import urlencode

def tidy_html(html):
    """
    Although there is a lib for it (https://pypi.python.org/pypi/pytidylib),
    I prefer to call tidy myself.
    """
    html = html.replace(b"&nbsp;", b" ")
    opts = {"stdout": sp.PIPE,
            "stderr": DEVNULL,
            "stdin": sp.PIPE}
    proc = sp.Popen("tidy -asxhtml -utf8 -q".split(), **opts)
    out, err = proc.communicate(input=html)
    return out

def getxml(url):
    html = readurl(url)
    xml = tidy_html(html)
    return etree.parse(BytesIO(xml))

def findx(xml, path):
    ns = {'x': 'http://www.w3.org/1999/xhtml'}
    return xml.xpath(path, namespaces=ns)
