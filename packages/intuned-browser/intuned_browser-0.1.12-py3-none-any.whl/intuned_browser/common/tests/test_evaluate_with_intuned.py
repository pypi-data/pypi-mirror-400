import pytest

# Optional imports with warning
try:
    from runtime import launch_chromium
except ImportError:
    launch_chromium = None
    import logging

    logging.warning("Runtime dependencies are not available. Some test features will be disabled.")

from intuned_browser.common.evaluate_with_intuned import evaluate_with_intuned


@pytest.mark.asyncio
async def test_evaluate_with_intuned():
    """Test that evaluate_with_intuned injects scripts and executes functions in a single call."""
    if launch_chromium is None:
        pytest.skip("Runtime dependencies not available")

    async with launch_chromium() as (_, page):
        # Verify __INTUNED__ is not initially loaded
        has_intuned = await page.evaluate('() => typeof window.__INTUNED__ !== "undefined"')
        assert not has_intuned

        # Use evaluate_with_intuned to check if __INTUNED__ exists
        # This should inject the scripts and return the result
        result = await evaluate_with_intuned(page, "() => typeof window.__INTUNED__")

        # Verify it returns 'object' (meaning __INTUNED__ was injected)
        assert result == "object"

        # Verify __INTUNED__ is now available on subsequent calls
        has_intuned = await page.evaluate('() => typeof window.__INTUNED__ !== "undefined"')
        assert has_intuned


@pytest.mark.asyncio
async def test_evaluate_with_intuned_with_arg():
    """Test that evaluate_with_intuned works with arguments."""
    if launch_chromium is None:
        pytest.skip("Runtime dependencies not available")

    async with launch_chromium() as (_, page):
        # Navigate to a page with some content
        await page.set_content("<div>Test content</div>")

        # Get the div element
        div = await page.locator("div").element_handle()

        # Use evaluate_with_intuned to get the XPath of the element
        xpath = await evaluate_with_intuned(page, "el => window.__INTUNED__.getElementXPath(el)", div)

        # Verify we got a valid xpath (should be a string)
        assert isinstance(xpath, str)
        assert len(xpath) > 0


@pytest.mark.asyncio
async def test_evaluate_with_intuned_on_locator():
    """Test that evaluate_with_intuned works with Locator objects."""
    if launch_chromium is None:
        pytest.skip("Runtime dependencies not available")

    async with launch_chromium() as (_, page):
        # Navigate to a page with some content
        await page.set_content("<div>Test content</div>")

        # Get the div locator
        div_locator = page.locator("div")

        # Use evaluate_with_intuned on the locator to get XPath
        xpath = await evaluate_with_intuned(div_locator, "el => window.__INTUNED__.getElementXPath(el)")

        # Verify we got a valid xpath
        assert isinstance(xpath, str)
        assert len(xpath) > 0
