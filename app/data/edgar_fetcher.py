import requests
import pandas as pd

headers = {"User-Agent": "piotr.wiski1@gmail.com"}

companyTickers = requests.get(
    "https://www.sec.gov/files/company_tickers.json",
    headers = headers
    )

def get_company_facts(cik: str):
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

    res = requests.get(url, headers=headers)
    res.raise_for_status()

    return res.json()


def extract_revenue(data):
    try:
        revenues = data["facts"]["us-gaap"]["Revenues"]["units"]["USD"]

        # bierzemy ostatnie wartości
        return [
            {
                "value": item["val"],
                "year": item.get("fy"),
                "form": item.get("form")
            }
            for item in revenues[-10:]
        ]
    except KeyError:
        return []

def get_filings(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    res = requests.get(url, headers=headers)
    return res.json()

cik = "0000002488"  # AMD

data = get_company_facts(cik)
revenues = extract_revenue(data)

for r in revenues:
    print(r)