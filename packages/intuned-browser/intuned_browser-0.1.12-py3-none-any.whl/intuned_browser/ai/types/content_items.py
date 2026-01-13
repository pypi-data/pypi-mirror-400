"""Content item types for extract_structured_data content-based extraction."""

from typing import Literal

from typing_extensions import TypedDict


class TextContentItem(TypedDict):
    """
    Text content item for content-based extraction.

    Attributes:
        type (str): The type of the content item, which is always "text".
        data (str): The text data to extract from.
    """

    type: Literal["text"]
    data: str


class ImageBufferContentItem(TypedDict):
    """
    Image buffer content item for content-based extraction.

    Attributes:
        type (str): The type of the content item, which is always "image-buffer".
        image_type (str): The image format (e.g., "png", "jpeg", "gif", "webp").
        data (bytes): The buffer containing the raw image data.
    """

    type: Literal["image-buffer"]
    image_type: Literal["png", "jpeg", "gif", "webp"]
    data: bytes


class ImageUrlContentItem(TypedDict):
    """
    Image URL content item for content-based extraction.

    Attributes:
        type (str): The type of the content item, which is always "image-url".
        image_type (str): The image format (e.g., "png", "jpeg", "gif", "webp").
        data (str): The URL of the image.
    """

    type: Literal["image-url"]
    image_type: Literal["png", "jpeg", "gif", "webp"]
    data: str


type ContentItem = TextContentItem | ImageBufferContentItem | ImageUrlContentItem
"""
A union type representing content items for AI data extraction from various content types.

This type alias defines the complete set of content types supported by the content-based
extract_structured_data function for extracting data from text, image buffers, or image URLs
without requiring a page source.

Type variants:
    - `TextContentItem`: [TextContentItem](../type-references/TextContentItem) for text data extraction
    - `ImageBufferContentItem`: [ImageBufferContentItem](../type-references/ImageBufferContentItem) for image data stored as bytes buffer
    - `ImageUrlContentItem`: [ImageUrlContentItem](../type-references/ImageUrlContentItem) for image data accessible via URL

Examples:
    ```python Text Content
    from intuned_browser.ai import TextContentItem
    async def automation(page, params, **_kwargs):
        text_content: TextContentItem = {
            "type": "text",
            "data": "John Doe, age 30, works as a Software Engineer at Tech Corp"
        }
    ```

    ```python Image Buffer Content
    from intuned_browser.ai import ImageBufferContentItem
    async def automation(page, params, **_kwargs):
        # Assuming you have image data as bytes
        with open("image.png", "rb") as f:
            image_data = f.read()

        image_content: ImageBufferContentItem = {
            "type": "image-buffer",
            "image_type": "png",
            "data": image_data
        }
    ```

    ```python Image URL Content
    from intuned_browser.ai import ImageUrlContentItem
    async def automation(page, params, **_kwargs):
        image_content: ImageUrlContentItem = {
            "type": "image-url",
            "image_type": "jpeg",
            "data": "https://example.com/image.jpg"
        }
    ```
"""


class ImageObject(TypedDict):
    """Image object for AI processing.

    Attributes:
        image_type: The image format (e.g., "png", "jpeg", "gif", "webp").
        data: The image data as bytes.
    """

    image_type: Literal["png", "jpeg", "gif", "webp"]
    data: bytes
