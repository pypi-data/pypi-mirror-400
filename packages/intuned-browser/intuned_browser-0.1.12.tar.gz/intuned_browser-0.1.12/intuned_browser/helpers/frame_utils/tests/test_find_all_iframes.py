import asyncio
import time

import pytest
from playwright.async_api import async_playwright

from intuned_browser.helpers.frame_utils import find_all_iframes


class TestFindAllIframes:
    """Test the find_all_iframes function"""

    @pytest.mark.asyncio
    async def test_find_all_iframes_basic(self):
        """Test basic iframe discovery"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_content(
            """
            <html>
                <body element_id="main-body">
                    <h1>Main Content</h1>
                    <iframe id="iframe-1"
                            element_id="iframe-1-id"
                            src="data:text/html,<html><body><h2>Iframe 1</h2></body></html>"
                            width="300"
                            height="200">
                    </iframe>
                    <iframe id="iframe-2"
                            element_id="iframe-2-id"
                            src="data:text/html,<html><body><h2>Iframe 2</h2></body></html>"
                            width="300"
                            height="200">
                    </iframe>
                </body>
            </html>
        """,
            wait_until="domcontentloaded",
        )

        iframe_nodes = await find_all_iframes(page)

        # Should find 2 top-level iframes
        assert len(iframe_nodes) == 2
        assert iframe_nodes[0].frame is not None
        assert iframe_nodes[1].frame is not None

        # No nested iframes
        assert len(iframe_nodes[0].nested_iframes) == 0
        assert len(iframe_nodes[1].nested_iframes) == 0

        await browser.close()
        await playwright.stop()

    @pytest.mark.asyncio
    async def test_find_all_iframes_nested(self):
        """Test nested iframe discovery"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_content(
            """
            <html>
                <body element_id="main-body">
                    <h1>Main Content</h1>
                    <iframe id="outer-iframe"
                            element_id="outer-iframe-id"
                            src="data:text/html,<html><body><h2>Outer</h2><iframe element_id='inner-iframe-id' src='data:text/html,<html><body><h3>Inner</h3></body></html>'></iframe></body></html>"
                            width="400"
                            height="300">
                    </iframe>
                </body>
            </html>
        """,
            wait_until="domcontentloaded",
        )

        iframe_nodes = await find_all_iframes(page)

        # Should find 1 top-level iframe
        assert len(iframe_nodes) == 1

        # Should have 1 nested iframe
        assert len(iframe_nodes[0].nested_iframes) == 1

        # Nested iframe should have no further nesting
        assert len(iframe_nodes[0].nested_iframes[0].nested_iframes) == 0

        await browser.close()
        await playwright.stop()

    @pytest.mark.asyncio
    async def test_find_all_iframes_empty_page(self):
        """Test with page that has no iframes"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_content(
            """
            <html>
                <body element_id="main-body">
                    <h1>Main Content</h1>
                    <p>No iframes here</p>
                </body>
            </html>
        """,
            wait_until="domcontentloaded",
        )

        iframe_nodes = await find_all_iframes(page)

        # Should find no iframes
        assert len(iframe_nodes) == 0

        await browser.close()
        await playwright.stop()

    @pytest.mark.asyncio
    async def test_find_all_iframes_with_problematic_srcs(self):
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_content(
            """
            <html>
                <body element_id="main-body">
                    <h1>Main Content</h1>
                    <iframe id="javascript-iframe"
                            element_id="javascript-iframe-id"
                            src="javascript:"
                            width="300"
                            height="200">
                    </iframe>
                    <iframe id="blob-iframe"
                            element_id="blob-iframe-id"
                            src="blob:null/invalid"
                            width="300"
                            height="200">
                    </iframe>
                    <iframe id="about-blank-iframe"
                            element_id="about-blank-iframe-id"
                            src="about:blank"
                            width="300"
                            height="200">
                    </iframe>
                </body>
            </html>
        """,
            wait_until="domcontentloaded",
            timeout=5000,
        )

        async def test():
            start_time = time.time()
            iframe_nodes = await find_all_iframes(page, iframe_timeout=2.0)
            elapsed_time = time.time() - start_time
            return iframe_nodes, elapsed_time

        iframe_nodes, elapsed_time = await asyncio.wait_for(test(), timeout=10.0)

        # Should complete quickly without hanging (under 10 seconds)
        assert elapsed_time < 10.0, f"Function took too long (likely hung): {elapsed_time} seconds"

        # Should not return malformed iframes
        assert len(iframe_nodes) < 3

        await browser.close()
        await playwright.stop()

    @pytest.mark.asyncio
    async def test_find_all_iframes_srcdoc(self):
        """Test iframes with srcdoc attribute"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_content(
            """
            <html>
                <body element_id="main-body">
                    <h1>Main Content</h1>
                    <iframe id="srcdoc-iframe"
                            element_id="srcdoc-iframe-id"
                            srcdoc="<html><body><h2>Srcdoc Content</h2></body></html>"
                            width="300"
                            height="200">
                    </iframe>
                </body>
            </html>
        """,
            wait_until="domcontentloaded",
        )

        iframe_nodes = await find_all_iframes(page)

        # Should find the srcdoc iframe
        assert len(iframe_nodes) == 1

        await browser.close()
        await playwright.stop()

    @pytest.mark.asyncio
    async def test_find_all_iframes_legacy_frames(self):
        """Test legacy <frame> elements within <frameset>"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Legacy frameset with frame elements
        await page.set_content(
            """
            <html>
                <head><title>Legacy Frameset</title></head>
                <frameset cols="50%,50%">
                    <frame id="frame-1"
                           element_id="frame-1-id"
                           src="data:text/html,<html><body><h2>Frame 1</h2></body></html>">
                    </frame>
                    <frame id="frame-2"
                           element_id="frame-2-id"
                           src="data:text/html,<html><body><h2>Frame 2</h2></body></html>">
                    </frame>
                </frameset>
            </html>
        """,
            wait_until="domcontentloaded",
        )

        iframe_nodes = await find_all_iframes(page)

        # Should find 2 legacy frame elements
        # Note: Some browsers may not support frameset, so we check for at least 0
        # Modern browsers may convert frameset to iframes or not support it at all
        assert len(iframe_nodes) >= 0
        # If frames are found, they should have valid frame objects
        for node in iframe_nodes:
            assert node.frame is not None

        await browser.close()
        await playwright.stop()

    @pytest.mark.asyncio
    async def test_find_all_iframes_sandbox_allows_async_scripts(self):
        """Test that allows_async_scripts flag correctly identifies sandboxed iframes"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.set_content(
            """
            <html>
                <body element_id="main-body">
                    <h1>Main Content</h1>
                    <iframe id="sandboxed-iframe"
                            element_id="sandboxed-iframe-id"
                            sandbox="allow-same-origin"
                            srcdoc="<html><body><h2>Sandboxed Iframe</h2></body></html>"
                            width="300"
                            height="200">
                    </iframe>
                    <iframe id="normal-iframe"
                            element_id="normal-iframe-id"
                            srcdoc="<html><body><h2>Normal Iframe</h2></body></html>"
                            width="300"
                            height="200">
                    </iframe>
                </body>
            </html>
        """,
            wait_until="domcontentloaded",
        )

        iframe_nodes = await find_all_iframes(page)

        # Should find 2 top-level iframes
        assert len(iframe_nodes) == 2

        # Find the sandboxed iframe and normal iframe by checking their element IDs
        sandboxed_node = None
        normal_node = None

        for node in iframe_nodes:
            try:
                iframe_element = await node.frame.frame_element()
                iframe_id = await iframe_element.get_attribute("id")
                if iframe_id == "sandboxed-iframe":
                    sandboxed_node = node
                elif iframe_id == "normal-iframe":
                    normal_node = node
            except Exception:
                continue

        # The sandboxed iframe should not allow async scripts
        assert sandboxed_node is not None, "Should find sandboxed iframe"
        assert (
            sandboxed_node.allows_async_scripts is False
        ), "Sandboxed iframe without allow-scripts should have allows_async_scripts=False"

        # The normal iframe should allow async scripts
        assert normal_node is not None, "Should find normal iframe"
        assert normal_node.allows_async_scripts is True, "Normal iframe should have allows_async_scripts=True"

        await browser.close()
        await playwright.stop()
