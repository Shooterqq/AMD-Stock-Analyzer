import requests

from core.constants import headers
from utils.analyzer import analyze_spm


class Edgar:
    def __init__(self, cik: int):
        self.cik = cik
        self.recent = None

    def load(self):
        url = f"https://data.sec.gov/submissions/CIK{self.cik}.json"
        self.recent = requests.get(url, headers=headers).json()["filings"]["recent"]

    def filings(self, limit: int = 20):
        if self.recent is None:
            self.load()

        return list(zip(
            self.recent["form"][:limit],
            self.recent["filingDate"][:limit],
            self.recent["accessionNumber"][:limit],
            self.recent["primaryDocument"][:limit],
        ))