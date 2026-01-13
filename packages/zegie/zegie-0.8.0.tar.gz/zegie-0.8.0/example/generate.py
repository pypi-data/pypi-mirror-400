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

import os
from zegie.post import PostFromLink
from zegie.post import PostFromTopic
from zegie.scraper import WebScraper


def main():
    generator_from_link = PostFromLink(
        scraper=WebScraper(
            scraper_url="http://127.0.0.1:8000",
            api_key="xkey",
        ),
        api_key=os.getenv("COHERE_API_KEY"),
        model="command-r7b-12-2024",
        temperature=0.7,
        base_url="https://api.cohere.ai/compatibility/v1",
        max_content_length=8000,
    )
    result = generator_from_link.generate(
        "https://ziee.io",
        "give me a casual post for twitter about team plan pricing",
    )
    print(result["content"])
    if result["token_usage"]:
        print(f"\nToken Usage:")
        print(f"  Prompt tokens: {result['token_usage']['prompt_tokens']}")
        print(f"  Completion tokens: {result['token_usage']['completion_tokens']}")
        print(f"  Total tokens: {result['token_usage']['total_tokens']}")

    generator_from_topic = PostFromTopic(
        api_key=os.getenv("COHERE_API_KEY"),
        model="command-r7b-12-2024",
        temperature=0.7,
        base_url="https://api.cohere.ai/compatibility/v1",
    )
    result = generator_from_topic.generate(
        "generate a casual post for twitter with a limit 100 characters about cloud computing"
    )
    print(result["content"])
    if result["token_usage"]:
        print(f"\nToken Usage:")
        print(f"  Prompt tokens: {result['token_usage']['prompt_tokens']}")
        print(f"  Completion tokens: {result['token_usage']['completion_tokens']}")
        print(f"  Total tokens: {result['token_usage']['total_tokens']}")


if __name__ == "__main__":
    main()
