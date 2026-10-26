"""
Download NIKE, Inc.'s reported financial figures from the SEC's XBRL API.

The "company facts" endpoint returns every figure NIKE has tagged in its
filings, going back years. It is free, needs no API key and no registration -
the only requirement is a User-Agent header identifying who is making the
request, which the SEC asks for in its fair-access policy.

Output: data/raw/nike_companyfacts.json  (about 3 MB)

NIKE's CIK (the SEC's company identifier) is 0000320187. You can find any
company's CIK at https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany

Usage: python scripts/00_download_data.py
"""

import urllib.request
from pathlib import Path

CIK = "0000320187"              # NIKE, Inc.
URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json".format(CIK)

# The SEC asks for a contact address in the User-Agent. Put your own in here.
USER_AGENT = "Fergus Barrie portfolio project (fergusjbarrie@gmail.com)"

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "raw" / "nike_companyfacts.json"


def main():
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    if TARGET.exists():
        print("Already downloaded:", TARGET)
        return

    print("Requesting", URL)
    request = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        TARGET.write_bytes(response.read())

    print("Wrote", TARGET, "({:.1f} MB)".format(TARGET.stat().st_size / 1_048_576))
    print("Next step: python scripts/01_extract_financials.py")


if __name__ == "__main__":
    main()
