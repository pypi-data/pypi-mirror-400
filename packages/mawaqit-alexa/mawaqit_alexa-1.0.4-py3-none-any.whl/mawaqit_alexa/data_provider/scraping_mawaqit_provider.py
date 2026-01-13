import requests
from bs4 import BeautifulSoup


import json
import re

from mawaqit_alexa.data_provider.mawaqit_provider import MawaqitProvider
from mawaqit_alexa.exceptions.scraping_exception import ScrapingException
from mawaqit_alexa.models.types import MawaqitYearCalendar
from mawaqit_alexa.util.ttl_cache import persistent_ttl_cache

WEEK_IN_SECONDS = 604800

class ScrapingMawaqitProvider(MawaqitProvider):

    def __init__(self, masjid_url_or_endpoint: str):
        super().__init__()
        if masjid_url_or_endpoint.startswith("http"):
            self.masjid_url = masjid_url_or_endpoint
            self.masjid_endpoint = self.masjid_url.split("/")[-1]
        else:
            self.masjid_endpoint = masjid_url_or_endpoint
            self.masjid_url = f"https://mawaqit.net/en/{self.masjid_endpoint}"

    @staticmethod
    @persistent_ttl_cache(seconds=WEEK_IN_SECONDS, logger_callback=print)
    def _fetch_mawaqit(masjid_url: str):
        r = requests.get(masjid_url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')

            # 1. Broad Search: Find the script tag that definitely contains the variable definition
            # We look for "confData" followed optionally by whitespace and an equals sign
            script_tag = soup.find('script', string=re.compile(r'confData\s*='))

            if script_tag:
                # 2. Precise Extraction: Use a robust regex to capture the JSON object
                # Matches: (var OR let OR const) + whitespace + confData + whitespace + = + whitespace + {captured_json} + ;
                # re.DOTALL allows the (.) to match newlines, handling multi-line JSON
                match = re.search(r'(?:var|let|const)\s+confData\s*=\s*(\{.*?\});', script_tag.string, re.DOTALL)

                if match:
                    conf_data_json = match.group(1)
                    try:
                        conf_data = json.loads(conf_data_json)
                        return conf_data
                    except json.JSONDecodeError as e:
                        # Capture partial failure: Variable found, but data wasn't valid JSON
                        raise ScrapingException(
                            f"Found confData but failed to decode JSON for {masjid_url}. Error: {e}")
                else:
                    raise ScrapingException(
                        f"Script found, but regex failed to extract confData object for {masjid_url}")
            else:
                print("Script containing confData not found.")
                raise ScrapingException(f"Script containing confData not found for {masjid_url}")

        if r.status_code == 404:
            raise ScrapingException(f"{masjid_url} not found")
    @staticmethod
    def _get_calendar(masjid_url:str):
        confData = ScrapingMawaqitProvider._fetch_mawaqit(masjid_url)
        return confData["calendar"]

    def get_current_year_calendar(self) -> MawaqitYearCalendar:
        return ScrapingMawaqitProvider._get_calendar(self.masjid_url)
