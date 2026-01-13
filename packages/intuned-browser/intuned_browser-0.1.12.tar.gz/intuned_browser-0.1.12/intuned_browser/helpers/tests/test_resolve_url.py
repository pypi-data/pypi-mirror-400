from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest
from playwright.async_api import Locator

from intuned_browser import resolve_url


class TestResolveUrl:
    """Tests for the resolve_url function."""

    @pytest.mark.asyncio
    async def test_relative_url_simple_path(self):
        """Test converting a simple relative path with string base URL."""
        result = await resolve_url(url="/path/to/page", base_url="https://example.com")
        assert result == "https://example.com/path/to/page"

    @pytest.mark.asyncio
    async def test_relative_url_with_query(self):
        """Test converting relative URL with query parameters."""
        result = await resolve_url(url="/search?q=test&page=1", base_url="https://example.com")
        assert result == "https://example.com/search?q=test&page=1"

    @pytest.mark.asyncio
    async def test_relative_url_with_fragment(self):
        """Test converting relative URL with fragment."""
        result = await resolve_url(url="/page#section1", base_url="https://example.com")
        assert result == "https://example.com/page#section1"

    @pytest.mark.asyncio
    async def test_relative_url_with_special_characters(self):
        """Test URL encoding of special characters."""
        result = await resolve_url(url="/path with spaces/file.html", base_url="https://example.com")
        assert result == "https://example.com/path%20with%20spaces/file.html"

    @pytest.mark.asyncio
    async def test_relative_url_with_encoded_characters(self):
        """Test that already encoded characters are not double-encoded."""
        result = await resolve_url(url="/path%20with%20spaces/file.html", base_url="https://example.com")
        assert result == "https://example.com/path%20with%20spaces/file.html"

    @pytest.mark.asyncio
    async def test_already_full_url(self):
        """Test that full URLs are returned unchanged."""
        full_url = "https://other-site.com/path/to/page"
        result = await resolve_url(url=full_url, base_url="https://example.com")
        assert result == full_url

    @pytest.mark.asyncio
    async def test_relative_url_current_directory(self):
        """Test relative URL starting with dot."""
        result = await resolve_url(url="./page.html", base_url="https://example.com/folder/")
        assert result == "https://example.com/folder/page.html"

    @pytest.mark.asyncio
    async def test_relative_url_parent_directory(self):
        """Test relative URL going to parent directory."""
        result = await resolve_url(url="../other/page.html", base_url="https://example.com/folder/subfolder/")
        assert result == "https://example.com/folder/other/page.html"

    @pytest.mark.asyncio
    async def test_query_parameter_encoding(self):
        """Test that query parameters are properly encoded."""
        result = await resolve_url(url="/search?q=hello world&filter=a+b", base_url="https://example.com")
        print("RESULT: ", result)
        assert result == "https://example.com/search?q=hello%20world&filter=a%2Bb"

    @pytest.mark.asyncio
    async def test_relative_url_with_page_basic(self):
        """Test converting relative URL using Page object as base."""
        # Mock Page object
        mock_page = MagicMock()
        mock_page.url = "https://example.com/current/page"

        result = await resolve_url(url="/new/path", page=mock_page)
        assert result == "https://example.com/new/path"

    @pytest.mark.asyncio
    async def test_already_full_url_with_page(self):
        """Test that full URLs are returned unchanged even with Page object."""
        # Mock Page object
        mock_page = MagicMock()
        mock_page.url = "https://example.com/current/page"

        full_url = "https://other-site.com/different/path"
        result = await resolve_url(url=full_url, page=mock_page)
        assert result == full_url

    @pytest.mark.asyncio
    async def test_page_with_query_and_fragment(self):
        """Test using Page object with complex URL structure."""
        # Mock Page object with complex URL
        mock_page = MagicMock()
        mock_page.url = "https://example.com/path?query=value#section"

        result = await resolve_url(url="/new/path", page=mock_page)
        # Should use only scheme and netloc from page URL
        assert result == "https://example.com/new/path"


class TestGetAnchorHref:
    """Tests for the get_anchor_href function."""

    @pytest.mark.asyncio
    async def test_get_anchor_href_basic(self):
        """Test getting href from a basic anchor element."""
        # Mock Locator with spec to pass isinstance check
        mock_locator = MagicMock(spec=Locator)
        mock_locator.evaluate = AsyncMock(
            side_effect=[
                "A",  # First call returns tag name
                "https://example.com/test/path",  # Second call returns href
            ]
        )

        result = await resolve_url(url=mock_locator)
        assert result == "https://example.com/test/path"

    @pytest.mark.asyncio
    async def test_get_anchor_href_full_url(self):
        """Test getting href from anchor with full URL."""
        # Mock Locator with spec to pass isinstance check
        mock_locator = MagicMock(spec=Locator)
        mock_locator.evaluate = AsyncMock(
            side_effect=[
                "A",  # Tag name
                "https://other-site.com/page",  # Href
            ]
        )

        result = await resolve_url(url=mock_locator)
        assert result == "https://other-site.com/page"

    @pytest.mark.asyncio
    async def test_get_anchor_href_with_query_and_fragment(self):
        """Test getting href from anchor with query parameters and fragment."""
        # Mock Locator with spec to pass isinstance check
        mock_locator = MagicMock(spec=Locator)
        mock_locator.evaluate = AsyncMock(
            side_effect=[
                "A",  # Tag name
                "https://example.com/search?q=test&page=1#results",  # Href
            ]
        )

        result = await resolve_url(url=mock_locator)
        assert result == "https://example.com/search?q=test&page=1#results"

    @pytest.mark.asyncio
    async def test_get_anchor_href_non_anchor_element_error(self):
        """Test that non-anchor elements raise ValueError."""
        # Mock Locator for a div element with spec to pass isinstance check
        mock_locator = MagicMock(spec=Locator)
        mock_locator.evaluate = AsyncMock(return_value="DIV")

        with pytest.raises(ValueError, match="Expected an anchor element, got DIV"):
            await resolve_url(url=mock_locator)

    @pytest.mark.asyncio
    async def test_get_anchor_href_button_element_error(self):
        """Test that button elements raise ValueError."""
        # Mock Locator for a button element with spec to pass isinstance check
        mock_locator = MagicMock(spec=Locator)
        mock_locator.evaluate = AsyncMock(return_value="BUTTON")

        with pytest.raises(ValueError, match="Expected an anchor element, got BUTTON"):
            await resolve_url(url=mock_locator)

    @pytest.mark.asyncio
    async def test_get_anchor_href_empty_href(self):
        """Test getting href from anchor with empty href attribute."""
        # Mock Locator - empty href resolves to current page URL in browser
        mock_locator = MagicMock(spec=Locator)
        mock_locator.evaluate = AsyncMock(
            side_effect=[
                "A",  # Tag name
                "https://example.com/",  # Browser resolves empty href to current page
            ]
        )

        result = await resolve_url(url=mock_locator)
        assert result == "https://example.com/"

    @pytest.mark.asyncio
    async def test_get_anchor_href_hash_only(self):
        """Test getting href from anchor with hash-only href."""
        # Mock Locator - hash-only href resolves to current page + hash
        mock_locator = MagicMock(spec=Locator)
        mock_locator.evaluate = AsyncMock(
            side_effect=[
                "A",  # Tag name
                "https://example.com/#section1",  # Browser resolves hash to full URL
            ]
        )

        result = await resolve_url(url=mock_locator)
        assert result == "https://example.com/#section1"
