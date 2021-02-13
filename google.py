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

    query = scholarly.search_pubs(args.title)
    pub = next(query)
    print(scholarly.bibtex(pub))
