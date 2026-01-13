import logging
from typing import Any
from typing import Literal
from typing import overload

import aiohttp
from playwright.async_api import Locator
from playwright.async_api import Page
from pydantic import BaseModel

from intuned_browser.ai.extract_structured_data_using_ai import extract_structured_data_using_ai
from intuned_browser.ai.types import ContentItem
from intuned_browser.ai.types import ImageObject
from intuned_browser.ai.utils import compress_string_spaces
from intuned_browser.ai.utils.build_images import build_images_from_page_or_handle
from intuned_browser.ai.utils.matching.matching import create_xpath_mapping
from intuned_browser.ai.utils.matching.matching import validate_xpath_mapping
from intuned_browser.ai.utils.validate_schema import check_all_types_are_strings
from intuned_browser.ai.utils.validate_schema import validate_schema
from intuned_browser.common.hash_object import hash_object
from intuned_browser.helpers.extract_markdown import extract_markdown
from intuned_browser.helpers.utils.get_simplified_html import get_simplified_html
from intuned_browser.intuned_services import cache

logger = logging.getLogger(__name__)


# Overload for page/locator-based extraction
@overload
async def extract_structured_data(
    *,
    source: Page | Locator,
    data_schema: type[BaseModel] | dict[str, Any],
    prompt: str | None = None,
    strategy: Literal["IMAGE", "MARKDOWN", "HTML"] = "HTML",
    model: str = "claude-haiku-4-5-20251001",
    api_key: str | None = None,
    enable_dom_matching: bool | None = False,
    enable_cache: bool | None = True,
    max_retries: int | None = 3,
) -> Any:
    """
    Extracts structured data from web pages using AI-powered content analysis.

    This function provides intelligent data extraction from web pages using various strategies
    including HTML parsing, image analysis, and Markdown conversion. Or by using Text or Image Content.
    It supports extraction from entire pages or specific elements, with built-in caching and retry mechanisms.

    Overload:
        Extract From Page or Locator

        Extract data from web pages or specific elements using HTML, IMAGE, or MARKDOWN strategies with DOM matching support.

        ## Features and limitations
        **Features:**
        - **Smart Caching:** Hashes inputs and uses [KV Cache](https://docs.intunedhq.com/docs/01-learn/recipes/kv-cache) for persistent storage
        - **DOM Matching:** With `enable_dom_matching=True`, values match DOM elements for smart caching
        - **Multiple Strategies:** HTML, IMAGE, or MARKDOWN based on content type
        - **Flexible Models:** Use any up-to-date model from anthropic, openai or google based on your needs.

        **Limitations:**
        - **Model Variability:** Quality varies by model - experiment to find the best fit
        - **DOM Complexity:** Dynamic structures can affect caching and matching
        - **IMAGE Constraints:** Cannot capture truncated or off-screen content
        - **Schema Design:** Complex schemas may reduce accuracy
    Args:
        source (Page | Locator): Playwright Page object to extract data from the entire page or Locator object to extract data from a specific element.
        data_schema (type[BaseModel] | dict[str, Any]): Schema defining the structure of the data to extract. Can be either a Pydantic BaseModel class or a JSON Schema dictionary.
        prompt (optional[str]): Optional prompt to guide the extraction process and provide more context. Defaults to None.
        strategy (optional[Literal['IMAGE', 'MARKDOWN', 'HTML']]): Type of extraction strategy:
        - **"HTML"** (default) - Best for text-heavy pages with structured content
        - **"IMAGE"** - Best for visual content, charts, or complex layouts
        - **"MARKDOWN"** - Best for article-style content with semantic structure
        enable_dom_matching (optional[bool]): Whether to enable DOM element matching during extraction. When enabled, all types in the schema must be strings to match with the DOM elements. Extraction results are mapped to their corresponding DOM elements and returned with matched results. These results are intelligently cached, allowing subsequent extractions with minor DOM changes to utilize the cached data for improved performance. Defaults to False.
        enable_cache (optional[bool]): Whether to enable caching of extraction results. Defaults to True.
        max_retries (optional[int]): Maximum number of retry attempts on failures. Failures can be validation errors, API errors, output errors, etc. Defaults to 3.
        model (optional[str]): AI model to use for extraction. Defaults to "claude-haiku-4-5-20251001".
        api_key (optional[str]): Optional API key for AI extraction (if provided, will not be billed to your account). Defaults to None.

    Returns:
        Any: The extracted structured data conforming to the provided schema.

    Examples:
        ```python Extract book details
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser.ai import extract_structured_data
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto('https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html')
            # This will extract the book details from the page, using the HTML strategy with the gpt-4o model.
            # The data_schema is a JSON Schema dictionary that defines the structure of the data to extract.
            # You can also use a Pydantic BaseModel instead of a JSON Schema dictionary.
            book = await extract_structured_data(
                source=page,
                strategy="HTML",  # The HTML strategy is the default strategy and will be used if no strategy is provided.
                model="gpt-4o",
                data_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "string"},
                        "description": {"type": "string"},
                        "in_stock": {"type": "string"}, # Must be string because we enabled DOM matching
                        "rating": {"type": "string"}
                    },
                    "required": ["name", "price"]
                },
                prompt="Extract book details from this page",
                enable_cache=True,  # since this is True, the method will call AI for the first time, and then whenever you call this method it will return cached results as long as the DOM is the same.
                enable_dom_matching=True,  # since this is True, the method will return the results mapped to the DOM elements, you MUST enable cache for this to work.
                max_retries=3
            )

            print(f"Found book: {book['name']} - {book['price']}")
        ```

        ```python Extract all books listings
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser.ai import extract_structured_data
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            await page.goto('https://books.toscrape.com/')
            # This will extract all the books listings from the page, using the HTML strategy with the claude-3-7-sonnet-latest model.
            # The data_schema is a JSON Schema dictionary that defines the structure of the data to extract.
            # You can also use a Pydantic BaseModel instead of a JSON Schema dictionary.
            books = await extract_structured_data(
                source=page,
                strategy="HTML",
                model="claude-3-7-sonnet-latest",
                data_schema={
                    "type": "object",
                    "properties": {
                        "products": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "price": {"type": "string"},
                                    "availability": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                prompt="Extract all book listings",
                enable_cache=False,  # In this example, we don't want to cache the extracted data, we want to extract the data every time.
            )

            for book in books['products']:
                print(f"{book['title']}: {book['price']}")
        ```
    """
    ...


# Overload for content-based extraction
@overload
async def extract_structured_data(
    *,
    content: list[ContentItem] | ContentItem,
    data_schema: type[BaseModel] | dict[str, Any],
    prompt: str | None = None,
    max_retries: int | None = 3,
    enable_cache: bool | None = True,
    model: str = "claude-haiku-4-5-20251001",
    api_key: str | None = None,
) -> Any:
    """
    Extracts structured data from web pages using AI-powered content analysis.

    This function provides intelligent data extraction from web pages using various strategies
    including HTML parsing, image analysis, and Markdown conversion. Or by using Text or Image Content.
    It supports extraction from entire pages or specific elements, with built-in caching and retry mechanisms.

    Overload:
        Extract From Content

        Extract data from text, image buffers, or image URLs without requiring a page source.

        ## Features and limitations
        **Features:**
        - **Smart Caching:** Hashes content and uses [KV Cache](https://docs.intunedhq.com/docs/01-learn/recipes/kv-cache) for persistent storage
        - **Multiple Content Items:** Combine text, images (buffer or URL) for comprehensive extraction
        - **Flexible Models:** Use any up-to-date model from anthropic, openai or google based on your needs.

        **Limitations:**
        - **Model Variability:** Quality varies by model - experiment to find the best fit
        - **Schema Design:** Complex schemas may reduce accuracy
        - **Content Quality:** Requires meaningful, contextual content for accurate extraction - sparse or ambiguous content produces poor results
    Args:
        content (list[ContentItem] | ContentItem): Content to extract data from - can be a single content item or array of [ContentItem](../type-references/ContentItem).
        data_schema (type[BaseModel] | dict[str, Any]): Schema defining the expected structure of the extracted data. Can be either a Pydantic BaseModel class or a JSON Schema dictionary.
        prompt (optional[str]): Optional prompt to guide the extraction process and provide more context. Defaults to None.
        max_retries (optional[int]): Maximum number of retry attempts on failures. Failures can be validation errors, API errors, output errors, etc. Defaults to 3.
        enable_cache (optional[bool]): Whether to enable caching of the extracted data. Defaults to True.
        model (optional[str]): AI model to use for extraction. Defaults to "claude-haiku-4-5-20251001".
        api_key (optional[str]): Optional API key for AI extraction (if provided, will not be billed to your account). Defaults to None.

    Returns:
        Any: The extracted structured data conforming to the provided schema.

    Examples:
        ```python Basic Text Content Extraction
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser.ai import extract_structured_data, TextContentItem
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            # This will extract the person information from the text, using the gpt-4o model.
            text_content: TextContentItem = {
                "type": "text",
                "data": "John Doe, age 30, works as a Software Engineer at Tech Corp"
            }

            person = await extract_structured_data(
                content=text_content,
                model="gpt-4o",
                data_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "number"},
                        "occupation": {"type": "string"},
                        "company": {"type": "string"}
                    },
                    "required": ["name"]
                },
                prompt="Extract person information from the text"
            )

            print(f"Found person: {person['name']}, {person['age']} years old")
        ```

        ```python List Extraction from Text Content
        from typing import TypedDict
        from playwright.async_api import Page
        from intuned_browser.ai import extract_structured_data, TextContentItem
        class Params(TypedDict):
            pass
        async def automation(page: Page, params: Params, **_kwargs):
            text_content: TextContentItem = {
                "type": "text",
                "data": "iPhone 15 - $999, Samsung Galaxy - $899, Pixel 8 - $699"
            }

            products = await extract_structured_data(
                content=text_content,
                model="gpt-4o",
                data_schema={
                    "type": "object",
                    "properties": {
                        "products": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "price": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                prompt="Extract all products"
            )

            for product in products['products']:
                print(f"{product['name']}: {product['price']}")
        ```
    """
    ...


async def extract_structured_data(
    *,
    content: list[ContentItem] | ContentItem | None = None,
    source: Page | Locator | None = None,
    data_schema: type[BaseModel] | dict[str, Any],
    prompt: str | None = None,
    strategy: Literal["IMAGE", "MARKDOWN", "HTML"] = "HTML",
    enable_dom_matching: bool | None = False,
    enable_cache: bool | None = True,
    max_retries: int | None = 3,
    model: str = "claude-haiku-4-5-20251001",
    api_key: str | None = None,
) -> Any:
    # Handle content-based extraction
    if content is not None and source is None:
        if data_schema is None:
            raise ValueError("data_schema is required for content-based extraction")
        return await _extract_structured_data_from_content(
            content=content,
            data_schema=data_schema,
            prompt=prompt,
            model=model,
            api_key=api_key,
            max_retries=max_retries,
            enable_cache=enable_cache,
        )

    # Handle page/locator-based extraction
    if source is None or data_schema is None:
        raise ValueError("source and data_schema are required for page/locator-based extraction")

    page_or_locator = source

    # Validate input using pydantic models
    try:
        # Convert TypedDict to Pydantic for validation
        parsed_schema = validate_schema(data_schema)
        if not parsed_schema:
            raise ValueError("Invalid data schema provided.")
    except Exception as e:
        raise ValueError(f"Invalid extract data input: {str(e)}") from e

    page_object = page_or_locator if isinstance(page_or_locator, Page) else page_or_locator.page

    # deny DOM matching if the schema is not valid
    if enable_dom_matching and not check_all_types_are_strings(parsed_schema):
        raise ValueError("For DOM matching, all types of the extraction fields must be STRINGS, to match with the DOM.")

    # We have 3 kind of extractions: image, html and markdown. These 3 strategies will call the same model, the only difference is what we pass to it.
    if strategy == "HTML":
        if not isinstance(page_or_locator, Page):
            container_handle = await page_or_locator.element_handle()
        else:
            container_handle = await page_or_locator.locator("html").element_handle()

        # Get simplified HTML
        simplified_html = await get_simplified_html(container_handle)
        cache_key = None
        # Create cache key
        if enable_cache:
            cache_key = hash_object(
                {
                    "pageUrl": page_object.url,
                    "data_schema": parsed_schema,
                    "model": model,
                    "strategy": strategy,
                    "prompt": prompt,
                    "search_region": str(page_or_locator) if isinstance(page_or_locator, Locator) else "",
                    **({"html": compress_string_spaces(simplified_html)} if not enable_dom_matching else {}),
                },
                treat_arrays_as_unsorted_lists=True,
            )

            # Check cache
            cached_result = await cache.get(cache_key)
            if cached_result:
                # dom matching is enabled and the result is cached, check if xpaths still have the matched text
                if enable_dom_matching and isinstance(cached_result, dict) and "matchesMapping" in cached_result:
                    # Validate DOM matches using XPath mapping
                    is_valid = await validate_xpath_mapping(page_object, cached_result["matchesMapping"])
                    if is_valid:
                        logger.info("Returning cached result with valid DOM matching")
                        return cached_result["result"]
                elif not enable_dom_matching:
                    logger.info("Returning cached result")
                    return cached_result

        # Extract using AI
        result = await extract_structured_data_using_ai(
            page=page_object,
            api_key=api_key,
            enable_dom_matching=enable_dom_matching if enable_dom_matching is not None else False,
            json_schema=parsed_schema,
            model=model,
            content=simplified_html,
            prompt=prompt if prompt is not None else "",
            images=[],
            max_retries=max_retries if max_retries is not None else 3,
        )
        if not result:
            raise Exception("No result found")

        if enable_cache and cache_key:
            # Cache result
            if not enable_dom_matching:
                await cache.set(cache_key, result.extracted_data)
            else:
                # Create XPath mapping for DOM validation
                dom_validation_hash = await create_xpath_mapping(page_object, result.extracted_data)  # type: ignore
                results_to_cache = {"result": result.extracted_data, "matchesMapping": dom_validation_hash}
                await cache.set(cache_key, results_to_cache)

        return result.extracted_data

    elif strategy == "IMAGE":
        # Get container handle
        container_handle = None
        if isinstance(page_or_locator, Locator):
            container_handle = await page_or_locator.element_handle()

        # Build images
        images = await build_images_from_page_or_handle(page_object, container_handle)

        # Create cache key
        cache_key = hash_object(
            {
                "pageUrl": page_object.url,
                "data_schema": parsed_schema,
                "model": model,
                "strategy": strategy,
                "prompt": prompt,
                "search_region": str(page_or_locator) if isinstance(page_or_locator, Locator) else "",
                **({"html": await page_object.locator("html").inner_html()} if not enable_dom_matching else {}),
            },
            treat_arrays_as_unsorted_lists=True,
        )

        # Check cache
        if enable_cache:
            cached_result = await cache.get(cache_key)
            if cached_result:
                if enable_dom_matching and isinstance(cached_result, dict) and "matchesMapping" in cached_result:
                    # Validate DOM matches using XPath mapping
                    is_valid = await validate_xpath_mapping(page_object, cached_result["matchesMapping"])
                    if is_valid:
                        logger.info("Returning cached result with valid DOM matching")
                        return cached_result["result"]
                elif not enable_dom_matching:
                    logger.info("Returning cached result")
                    return cached_result

        # Extract using AI
        result = await extract_structured_data_using_ai(
            page=page_object,
            api_key=api_key,
            enable_dom_matching=enable_dom_matching if enable_dom_matching is not None else False,
            json_schema=parsed_schema,
            model=model,
            content="Extract structured data from the following images.",
            prompt=prompt if prompt is not None else "",
            images=images if isinstance(images, list) else [],
            max_retries=max_retries if max_retries is not None else 3,
        )

        if not result:
            raise Exception("No result found")

        # Cache result
        if enable_cache:
            if not enable_dom_matching:
                await cache.set(cache_key, result.extracted_data)
            else:
                # Create XPath mapping for DOM validation
                dom_validation_hash = await create_xpath_mapping(page_object, result.extracted_data)  # type: ignore
                results_to_cache = {"result": result.extracted_data, "matchesMapping": dom_validation_hash}
                await cache.set(cache_key, results_to_cache)

        return result.extracted_data

    elif strategy == "MARKDOWN":
        # Get container handle
        container_handle = None
        if isinstance(page_or_locator, Locator):
            container_handle = await page_or_locator.element_handle()
        else:
            container_handle = await page_or_locator.locator("html").element_handle()

        # Convert HTML to markdown
        markdown_content = await extract_markdown(page_object)

        cache_key = hash_object(
            {
                "pageUrl": page_object.url,
                "data_schema": parsed_schema,
                "model": model,
                "strategy": strategy,
                "prompt": prompt,
                "search_region": str(page_or_locator) if isinstance(page_or_locator, Locator) else "",
                **(
                    {"html": await page_object.locator("html").inner_html(), "markdown": markdown_content}
                    if not enable_dom_matching
                    else {}
                ),
            },
            treat_arrays_as_unsorted_lists=True,
        )

        # Check cache
        if enable_cache:
            cached_result = await cache.get(cache_key)
            if cached_result:
                if enable_dom_matching and isinstance(cached_result, dict) and "matchesMapping" in cached_result:
                    # Validate DOM matches using XPath mapping
                    is_valid = await validate_xpath_mapping(page_object, cached_result["matchesMapping"])
                    if is_valid:
                        logger.info("Returning cached result with valid DOM matching")
                        return cached_result["result"]
                elif not enable_dom_matching:
                    logger.info("Returning cached result")
                    return cached_result

        # Extract using AI
        result = await extract_structured_data_using_ai(
            page=page_object,
            api_key=api_key,
            enable_dom_matching=enable_dom_matching if enable_dom_matching is not None else False,
            json_schema=parsed_schema,
            model=model,
            content=markdown_content,
            prompt=prompt if prompt is not None else "",
            images=[],
            max_retries=max_retries if max_retries is not None else 3,
        )
        if not result:
            raise Exception("No result found")

        # Cache result
        if enable_cache:
            if not enable_dom_matching:
                await cache.set(cache_key, result.extracted_data)
            else:
                # Create XPath mapping for DOM validation
                dom_validation_hash = await create_xpath_mapping(page_object, result.extracted_data)  # type: ignore
                results_to_cache = {"result": result.extracted_data, "matchesMapping": dom_validation_hash}
                await cache.set(cache_key, results_to_cache)

        return result.extracted_data


async def _extract_structured_data_from_content(
    content: list[ContentItem] | ContentItem,
    data_schema: type[BaseModel] | dict[str, Any],
    prompt: str | None = None,
    model: str = "claude-haiku-4-5-20251001",
    api_key: str | None = None,
    max_retries: int | None = 3,
    enable_cache: bool | None = True,
) -> Any:
    # Validate schema
    try:
        parsed_schema = validate_schema(data_schema)
        if not parsed_schema:
            raise ValueError("Invalid data schema provided.")
    except Exception as e:
        raise ValueError(f"Invalid extract data input: {str(e)}") from e

    # Normalize content to list
    content_list = content if isinstance(content, list) else [content]

    # Process images from buffers - create ImageObject format
    images_from_buffers: list[ImageObject] = [
        {
            "image_type": item["image_type"],
            "data": item["data"],
        }
        for item in content_list
        if item["type"] == "image-buffer"
    ]

    # Process images from URLs - create ImageObject format
    images_from_urls: list[ImageObject] = []
    for item in content_list:
        if item["type"] == "image-url":
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(item["data"]) as response:
                        if response.status == 200:
                            buffer = await response.read()
                            images_from_urls.append(
                                {
                                    "image_type": item["image_type"],
                                    "data": buffer,
                                }
                            )
                        else:
                            raise Exception(f"HTTP {response.status}")
            except Exception as e:
                raise ValueError(f"Fetching image from URL {item['data']} failed: {e}") from e

    # Combine all images as list[ImageObject]
    images = images_from_urls + images_from_buffers

    # Extract text content
    texts = [item["data"] for item in content_list if item["type"] == "text"]

    # Create cache key if caching is enabled
    cache_key = None
    if enable_cache:
        cache_key = hash_object(
            {
                "system_message": prompt,
                "images": [{"image_type": img["image_type"], "data": img["data"].hex()} for img in images],
                "json_schema": parsed_schema,
                "model": model,
                "text": texts,
            },
            treat_arrays_as_unsorted_lists=False,
        )

        # Check cache
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.info("Returning cached result")
            return cached_result

    # Extract using AI
    result = await extract_structured_data_using_ai(
        api_key=api_key,
        enable_dom_matching=False,
        json_schema=parsed_schema,
        model=model,
        content="\n".join(texts),
        prompt=prompt if prompt is not None else "",
        images=images,
        max_retries=max_retries if max_retries is not None else 3,
    )

    # Cache result if caching is enabled
    if enable_cache and cache_key:
        await cache.set(cache_key, result.extracted_data)
    if not result.extracted_data:
        logger.warning("No extracted data found, returning None")
    return result.extracted_data
