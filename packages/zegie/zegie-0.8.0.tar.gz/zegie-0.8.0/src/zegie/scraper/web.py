# Copyright 2025 Clivern
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
from .base import Scraper


class WebScraper(Scraper):
    """
    Web scraper.
    https://github.com/Zieeio/Scraper
    """

    def __init__(self, scraper_url: str, api_key: str):
        """
        Initialize the Web scraper.

        Args:
            scraper_url: The URL of the scraper.
            api_key: The API key to use for authentication.
        """
        self.api_key = api_key
        self.scraper_url = scraper_url

    def scrape(self, url: str) -> str:
        """
        Scrape a URL.

        Args:
            url: The URL to scrape.

        Returns:
            The scraped content.
        """
        response = requests.post(
            f"{self.scraper_url}/crawl",
            json={"url": url},
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
            },
        )

        if response.status_code != 200:
            raise Exception(f"Failed to scrape {url}: {response.status_code}")

        return response.text
