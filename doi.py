import webbrowser

"""
TODO: Think about https://pypi.python.org/pypi/mechanize/
"""

def browser_open(doi):
    """
    See also 
    https://github.com/torfbolt/DOI-finder/blob/master/src/doi_finder.py
    """
    webbrowser.open_new_tab("http://dx.doi.org/{0}".format(doi))

