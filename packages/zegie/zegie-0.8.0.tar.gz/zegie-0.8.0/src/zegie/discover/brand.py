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

from typing import List, Optional, Dict, Any


class Brand:
    """Represents brand information for content discovery and generation."""

    def __init__(
        self,
        name: str,
        industry: str,
        description: str,
        website_url: str,
        links: Optional[List[str]] = None,
    ):
        """
        Initialize a Brand instance.

        Args:
            name: Brand name.
            industry: Industry the brand operates in.
            description: Brand description.
            website_url: Main website URL.
            links: List of URLs from the website to scrape (can be extended).
        """
        self.name = name
        self.industry = industry
        self.description = description
        self.website_url = website_url
        self.links = links or []

    def add_link(self, link: str) -> None:
        """
        Add a new link to the brand's link list.

        Args:
            link: URL to add.
        """
        if link not in self.links:
            self.links.append(link)

    def add_links(self, links: List[str]) -> None:
        """
        Add multiple links to the brand's link list.

        Args:
            links: List of URLs to add.
        """
        for link in links:
            self.add_link(link)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert brand information to a dictionary.

        Returns:
            Dictionary containing brand information.
        """
        return {
            "name": self.name,
            "industry": self.industry,
            "description": self.description,
            "website_url": self.website_url,
            "links": self.links,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Brand":
        """
        Create a Brand instance from a dictionary.

        Args:
            data: Dictionary containing brand information.

        Returns:
            Brand instance.
        """
        return cls(
            name=data["name"],
            industry=data["industry"],
            description=data["description"],
            website_url=data["website_url"],
            links=data.get("links", []),
        )
