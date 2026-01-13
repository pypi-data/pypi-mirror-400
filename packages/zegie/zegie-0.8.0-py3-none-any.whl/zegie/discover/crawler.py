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

import asyncio
from typing import List
from .brand import Brand
from zegie.scraper import Scraper
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Crawler:
    """Crawler to scrape links and extract text content from websites."""

    def __init__(
        self,
        webbase_scraper: Scraper,
        timeout: int = 30,
        max_chunk_length: int = 50000,
        chunk_size: int = 2000,
        chunk_overlap: int = 400,
    ):
        """
        Initialize the Crawler.

        Args:
            webbase_scraper: Scraper instance to use for scraping URLs.
            timeout: Request timeout in seconds. Default: 30.
            max_chunk_length: Maximum content length to extract per page before truncation.
                             Higher values allow more content but use more memory.
                             Default: 50000 characters (~10-15 pages of text).
            chunk_size: Maximum size of chunks to split text into (in characters).
                        Recommended range: 1500-3000 for most LLM embeddings.
                        Default: 2000 characters for better context preservation.
            chunk_overlap: Overlap between chunks to maintain context (in characters).
                           Typically 15-25% of chunk_size. Prevents losing context
                           at chunk boundaries. Default: 400 characters (20% of chunk_size).
        """
        self.webbase_scraper = webbase_scraper
        self.timeout = timeout
        self.max_chunk_length = max_chunk_length
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def crawl(self, brand: Brand) -> List[str]:
        """
        Crawl the brand's website and extract the content.

        Args:
            brand: Brand instance containing website URL and links to crawl.

        Returns:
            List of semantically meaningful content chunks.
        """
        return asyncio.run(self._async_crawl(brand))

    async def _async_crawl(self, brand: Brand) -> List[str]:
        """
        Async implementation of the crawl method.

        Args:
            brand: Brand instance containing website URL and links to crawl.

        Returns:
            List of semantically meaningful content chunks.
        """
        urls = [brand.website_url]
        if brand.links:
            urls.extend(brand.links)

        chunks = []
        tasks = [self._load_document(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if result and not isinstance(result, Exception):
                chunks.extend(self._chunk_content(result))

        return chunks

    async def _load_document(self, url: str) -> str:
        """
        Load a document from a URL using Webbase scraper.

        Args:
            url: URL to load.

        Returns:
            Extracted text content from the page.
        """
        try:
            content = await asyncio.wait_for(
                asyncio.to_thread(self.webbase_scraper.scrape, url),
                timeout=self.timeout,
            )
            return content
        except Exception:
            return ""

    def _chunk_content(self, content: str) -> List[str]:
        """
        Split content into semantically meaningful chunks.

        Args:
            content: Raw text content to chunk.

        Returns:
            List of content chunks.
        """
        if not content or content == "":
            return []

        if len(content) > self.max_chunk_length:
            content = content[: self.max_chunk_length]

        return self.text_splitter.split_text(content)
