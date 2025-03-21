import requests
import os
import json

ADS_API_TOKEN = os.getenv("ADS_API_TOKEN")
HEADERS = {"Authorization": f"Bearer {ADS_API_TOKEN}"}

# Replace with your actual library ID from ADS (found in the URL of your library page)
LIBRARY_ID = "JrWTBTT0R_OM1UiDMzSQ7w"
ADS_API_URL = f"https://api.adsabs.harvard.edu/v1/biblib/libraries/{LIBRARY_ID}"
SEARCH_URL = "https://api.adsabs.harvard.edu/v1/search/query"

# Your name as it appears in ADS (used to detect first authorship)
YOUR_NAME = "Neufeld"


def get_bibcodes():
    res = requests.get(ADS_API_URL, headers=HEADERS)
    res.raise_for_status()
    return res.json()["library"]["documents"]


def fetch_paper_data(bibcodes):
    query = " OR ".join([f"bibcode:{b}" for b in bibcodes])
    params = {
        "q": query,
        "fl": "title,author,year,bibcode,abstract",
        "rows": len(bibcodes),
    }
    res = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    res.raise_for_status()
    return res.json()["response"]["docs"]


def is_first_author(authors):
    if not authors:
        return False
    first = authors[0].lower().replace(".", "").strip()
    return (
        "neufeld, c" in first or
        "chloe neufeld" in first or
        "neufeld, chloe" in first
    )


def main():
    bibcodes = get_bibcodes()
    papers = fetch_paper_data(bibcodes)

    first_author = []
    nth_author = []

    for paper in papers:
        entry = {
            "title": paper.get("title", ["No Title"])[0],
            "year": paper.get("year", "Unknown"),
            "authors": paper.get("author", []),
            "abstract": paper.get("abstract", ""),
            "bibcode": paper.get("bibcode")
        }

        if is_first_author(entry["authors"]):
            first_author.append(entry)
        else:
            nth_author.append(entry)

    with open("publications.json", "w") as f:
        json.dump({
            "first_author": first_author,
            "nth_author": nth_author
        }, f, indent=2)


if __name__ == "__main__":
    main()
