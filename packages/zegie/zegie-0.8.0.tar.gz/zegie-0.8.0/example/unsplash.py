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
from zegie.images import Unsplash


def main():
    # Initialize Unsplash with your API access key
    # Get your access key from https://unsplash.com/developers
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")

    if not access_key:
        print("Error: UNSPLASH_ACCESS_KEY environment variable is not set.")
        print("Please set it with your Unsplash API access key.")
        print("Get one at https://unsplash.com/developers")
        return

    unsplash = Unsplash(access_key=access_key)

    print("=" * 80)
    print("Example 1: Search for images with full information")
    print("=" * 80)
    print()

    # Search for images and get full information
    try:
        images = unsplash.search("feet", per_page=3)
        print(f"Found {len(images)} image(s) for 'nature':\n")

        for i, image in enumerate(images, 1):
            print(f"Image {i}:")
            print(f"  ID: {image.get('id')}")
            print(f"  Description: {image.get('description', 'N/A')}")
            print(f"  Alt Description: {image.get('alt_description', 'N/A')}")
            print(f"  Dimensions: {image.get('width')}x{image.get('height')} pixels")
            print(f"  Color: {image.get('color', 'N/A')}")
            if image.get("user"):
                print(f"  Photographer: {image['user'].get('name', 'N/A')}")
            print(f"  Regular URL: {image.get('urls', {}).get('regular', 'N/A')}")
            print()
    except Exception as e:
        print(f"Error searching images: {e}")
        print()

    print("=" * 80)
    print("Example 2: Get just image URLs (showing different sizes)")
    print("=" * 80)
    print()

    # Get just the image URLs with different sizes
    try:
        # Show that different sizes have different widths in URLs
        print("Note: The 'w=' parameter in URLs shows the requested size width:")
        print("  - thumb: 200px")
        print("  - small: 400px")
        print("  - regular: 1080px (default)")
        print("  - full: original dimensions (varies)")
        print("  - raw: original dimensions (varies)")
        print()

        # Get full image info to show actual dimensions
        images = unsplash.search("mountains", per_page=3)
        print(f"Found {len(images)} image(s) for 'mountains':\n")
        for i, image in enumerate(images, 1):
            print(f"Image {i}:")
            print(
                f"  Actual dimensions: {image.get('width')}x{image.get('height')} pixels"
            )
            print(f"  Thumb URL (200px): {image.get('urls', {}).get('thumb', 'N/A')}")
            print(f"  Small URL (400px): {image.get('urls', {}).get('small', 'N/A')}")
            print(
                f"  Regular URL (1080px): {image.get('urls', {}).get('regular', 'N/A')}"
            )
            print(f"  Full URL (original): {image.get('urls', {}).get('full', 'N/A')}")
            print()
    except Exception as e:
        print(f"Error getting image URLs: {e}")
        print()

    print("=" * 80)
    print("Example 3: Search with filters (landscape orientation)")
    print("=" * 80)
    print()

    # Search with orientation filter
    try:
        landscape_images = unsplash.search(
            "sunset", per_page=3, orientation="landscape", order_by="popular"
        )
        print(f"Found {len(landscape_images)} landscape image(s) for 'sunset':\n")
        for i, image in enumerate(landscape_images, 1):
            print(f"Image {i}:")
            print(f"  URL: {image.get('urls', {}).get('regular', 'N/A')}")
            description = image.get('description') or image.get('alt_description') or 'N/A'
            if description != 'N/A':
                description = description[:60] + '...' if len(description) > 60 else description
            print(f"  Description: {description}")
            print()
    except Exception as e:
        print(f"Error searching with filters: {e}")
        print()


if __name__ == "__main__":
    main()
