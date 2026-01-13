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

import logging
from zegie.discover import Brand, Crawler
from zegie.scraper import Webbase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def main():
    brand = Brand(
        name="Clivern",
        industry="Technology",
        description="Software Engineer and Occasional Writer. I write about Web APIs, PHP, Python, Go, Java, Rust, Elixir, Software Architecture, Resilience, Automation, AI, DevOps ... etc",
        website_url="https://clivern.com/",
        links=[
            "https://clivern.com/about/",
            "https://clivern.com/sponsor/",
            "https://clivern.com/privacy-policy/",
        ],
    )
    brand.add_link("https://clivern.com/contact/")
    brand.add_links(
        [
            "https://clivern.com/how-to-internationalize-your-wordpress-plugin/",
            "https://clivern.com/how-to-make-http-requests-with-wordpress/",
            "https://clivern.com/laravel-routing/",
            "https://clivern.com/working-with-wordpress-shortcodes/",
            "https://clivern.com/how-to-schedule-events-using-wordpress-cron/",
            "https://clivern.com/docker-in-a-nutshell/",
            "https://clivern.com/kubernetes-deployment-in-a-nutshell/",
            "https://clivern.com/building-my-own-rag-with-openai-qdrant-and-langchain/",
            "https://clivern.com/understanding-opentelemetry-distributed-tracing/",
            "https://clivern.com/load-testing-with-k6/",
            "https://clivern.com/tools-calling-with-langchain/",
            "https://clivern.com/langgraph-in-action/",
            "https://clivern.com/project/gauntlet/",
            "https://clivern.com/project/cattle/",
            "https://clivern.com/project/cygnus-x1/",
        ]
    )

    print("Brand Information:")
    print(f"  Name: {brand.name}")
    print(f"  Industry: {brand.industry}")
    print(f"  Description: {brand.description}")
    print(f"  Website URL: {brand.website_url}")
    print(f"  Links to crawl: {len(brand.links)}")
    for i, link in enumerate(brand.links, 1):
        print(f"    {i}. {link}")
    print()

    brand_dict = brand.to_dict()
    print("Brand as dictionary:")
    print(f"  {brand_dict}")
    print()

    crawler = Crawler(
        webbase=Webbase(
            scraper_url="http://127.0.0.1:8000",
            api_key="xkey",
        ),
        timeout=30,
        max_chunk_length=100000,
    )

    print("Crawling brand website...")
    print("This may take a moment depending on the number of URLs...")
    print()

    try:
        content_chunks = crawler.crawl(brand)

        print(f"Successfully crawled {len(content_chunks)} content chunk(s)")
        print()

        for i, chunk in enumerate(content_chunks, 1):
            print(f"Content Chunk {i}:")
            print("-" * 80)
            print(chunk)
            print("-" * 80)
            print()

    except Exception as e:
        print(f"Error during crawling: {e}")
        print("Note: This example uses example.com which may not be accessible.")
        print("Replace with a real website URL to see actual crawling results.")


if __name__ == "__main__":
    main()
