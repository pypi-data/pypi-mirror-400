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

from typing import List, Dict, Any, Optional
import requests


class Unsplash:
    """Unsplash image finder."""

    def __init__(self, access_key: str):
        """
        Initialize the Unsplash image finder.

        Args:
            access_key: Unsplash API access key (Client ID).
                       Get one at https://unsplash.com/developers
        """
        self.access_key = access_key
        self.base_url = "https://api.unsplash.com"

    def search(
        self,
        query: str,
        per_page: int = 10,
        page: int = 1,
        orientation: Optional[str] = None,
        order_by: str = "relevant",
    ) -> List[Dict[str, Any]]:
        """
        Search for images on Unsplash based on search terms.

        Args:
            query: Search terms/keywords to find images.
            per_page: Number of images per page (1-30). Default: 10.
            page: Page number to retrieve. Default: 1.
            orientation: Filter by orientation. Options: "landscape", "portrait", "squarish".
                        Default: None (all orientations).
            order_by: How to sort the results. Options: "latest", "oldest", "popular", "relevant".
                     Default: "relevant".

        Returns:
            List of dictionaries containing image information. Each dictionary includes:
            - id: Image ID
            - urls: Dictionary with different image sizes (raw, full, regular, small, thumb)
            - description: Image description
            - alt_description: Alt text description
            - width: Image width in pixels
            - height: Image height in pixels
            - color: Dominant color hex code
            - user: Photographer information
            - links: Related links (html, download, download_location)

        Raises:
            Exception: If the API request fails.
        """
        url = f"{self.base_url}/search/photos"
        headers = {"Authorization": f"Client-ID {self.access_key}"}
        params = {
            "query": query,
            "per_page": min(max(1, per_page), 30),  # Clamp between 1 and 30
            "page": max(1, page),
            "order_by": order_by,
        }

        if orientation:
            params["orientation"] = orientation

        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            return data.get("results", [])
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to search Unsplash images: {str(e)}")
