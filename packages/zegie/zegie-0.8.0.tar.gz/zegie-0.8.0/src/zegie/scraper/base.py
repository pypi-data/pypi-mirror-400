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

from abc import ABC, abstractmethod


class Scraper(ABC):
    """
    Abstract base class defining the contract for all scrapers.

    All scraper implementations must inherit from this class and
    implement the scrape method.
    """

    @abstractmethod
    def scrape(self, url: str) -> str:
        """
        Scrape a URL and return the content.

        Args:
            url: The URL to scrape.

        Returns:
            The scraped content as a string.

        Raises:
            Exception: If scraping fails for any reason.
        """
        pass
