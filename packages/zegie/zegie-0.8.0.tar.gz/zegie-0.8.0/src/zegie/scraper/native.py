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

import mechanicalsoup
from .base import Scraper
from markdownify import markdownify as md


class NativeScraper(Scraper):
    """
    Native scraper using mechanicalsoup and markdownify.
    """

    def __init__(self):
        """
        Initialize the Native scraper.
        """
        self.browser = mechanicalsoup.StatefulBrowser()

    def scrape(self, url: str) -> str:
        """
        Scrape a URL and convert to Markdown.

        Args:
            url: The URL to scrape.

        Returns:
            The scraped content as Markdown.
        """
        try:
            # Open the page
            self.browser.open(url)

            # Get the HTML content
            html_content = str(self.browser.page)

            # Convert to Markdown
            markdown_text = md(html_content, heading_style="ATX")

            return markdown_text
        except Exception as e:
            raise Exception(f"Failed to scrape {url}: {str(e)}")
