"""
Fetch citation from http://pubs.acs.org/
"""


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
