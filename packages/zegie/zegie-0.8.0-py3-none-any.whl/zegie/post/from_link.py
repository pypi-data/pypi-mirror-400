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

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from zegie.scraper import Scraper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


class PostFromLink:
    """Generate posts from URL by extracting content and using AI to create a post."""

    def __init__(
        self,
        scraper: Scraper,
        api_key: str,
        model: str = "gpt-5.2",
        temperature: float = 0.7,
        base_url: str = "https://api.openai.com/v1",
        max_content_length: int = 8000,
    ):
        """
        Initialize the PostFromLink.

        Args:
            scraper: Scraper instance to use for scraping URLs.
            api_key: API key (OpenAI or Cohere).
            model: Model name to use for generation.
            temperature: Temperature for generation (0.0 to 2.0).
            base_url: Base URL for the API.
            max_content_length: Maximum content length to use from scraped page (in characters).
                               Content exceeding this limit will be truncated. Default: 8000.
        """
        kwargs = {
            "openai_api_key": api_key,
            "model": model,
            "temperature": temperature,
            "base_url": base_url,
        }
        self.llm = ChatOpenAI(**kwargs)
        self.scraper = scraper
        self.max_content_length = max_content_length

    def generate(self, url: str, user_prompt: str) -> Dict[str, Any]:
        """
        Generate a post from a URL based on a user's natural language prompt.

        Args:
            url: The URL to extract content from.
            user_prompt: A natural language prompt describing what to generate
                        (e.g., "create a professional post highlighting the key features")

        Returns:
            Dictionary with 'content' (str) and 'token_usage' (dict with 'prompt_tokens',
            'completion_tokens', 'total_tokens').
        """
        content = self.scraper.scrape(url)

        if len(content) > self.max_content_length:
            content = content[: self.max_content_length] + "..."

        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="You are a skilled content creator who specializes in creating engaging social media posts from web content."
                ),
                HumanMessage(
                    content=f"""Based on the following content extracted from a webpage, follow the user's instructions to create a post.
Content from webpage:
{content}
User Request: {user_prompt}
Generate the post according to the user's specifications:
IMPORTANT: Return ONLY the post content itself. Do NOT include any introductory text, explanations, or quotes around the content. Return the post text directly without any wrapper text."""
                ),
            ]
        )

        messages = prompt.format_messages()
        response = self.llm.invoke(messages)

        token_usage_dict = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

        if hasattr(response, "response_metadata") and response.response_metadata:
            token_usage = response.response_metadata.get("token_usage", {})
            token_usage_dict = {
                "prompt_tokens": token_usage.get("prompt_tokens", 0),
                "completion_tokens": token_usage.get("completion_tokens", 0),
                "total_tokens": token_usage.get("total_tokens", 0),
            }

        return {"content": response.content, "token_usage": token_usage_dict}
