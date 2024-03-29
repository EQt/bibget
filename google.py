#!/usr/bin/env python3
"""
Print Google Scholar entry in BibTeX
"""
from scholarly import scholarly


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("title", type=str)
    args = p.parse_args()

    title = args.title
    query = scholarly.search_pubs(title)
    pub = next(query)
    if 'eprint_url' in pub:
        print(f"# pdf = {pub['eprint_url']}")
        pub['pdf'] = pub['eprint_url']
    bib = pub['bib']
    bib['year'] = bib['pub_year']
    del bib['pub_year']
    out = scholarly.bibtex(pub)
    print(out)
    with open("bibentry.bib", "w") as io:
        print(out, file=io)
        
