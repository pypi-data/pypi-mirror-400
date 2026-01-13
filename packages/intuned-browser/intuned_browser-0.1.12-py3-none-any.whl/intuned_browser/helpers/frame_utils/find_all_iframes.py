import asyncio
import logging
from dataclasses import dataclass

from playwright.async_api import Frame
from playwright.async_api import Locator
from playwright.async_api import Page

from .check_frame_allows_async_script import check_frame_allows_async_scripts
from .constants import ALL_IFRAMES_CSS_SELECTOR

logger = logging.getLogger(__name__)


@dataclass
class IframeNode:
    """Represents an iframe in a tree structure.

    Attributes:
        frame: The Playwright Frame object for this iframe
        nested_iframes: List of nested iframe nodes within this iframe
        allows_async_scripts: Whether this iframe allows asynchronous script operations.
            Synchronous code (e.g., via frame.evaluate()) can still execute even when this is False.
            However, when False, asynchronous operations like event listeners, callbacks,
            setTimeout, and promises do not work at all in the iframe.
    """

    frame: Frame
    nested_iframes: list["IframeNode"]
    allows_async_scripts: bool


async def find_all_iframes(
    root: Page | Frame | Locator,
    iframe_timeout: float = 10.0,
) -> list[IframeNode]:
    """
    Recursively get all iframes from a root as a tree structure.
    Skips iframes that hang due to problematic sources (see test_get_all_iframes_with_problematic_srcs).
    Using this function is safer than manually fetching iframes since it handles the hanging issue.

    Args:
        root: The Playwright root element to start the search from
        iframe_timeout: Timeout in seconds for accessing iframe element, since it might hang due to problematic iframe sources

    Returns:
        Returns a list of top-level iframe nodes, where each node contains its locator and any nested iframes.
    """
    processed: set[Page | Frame | Locator] = set()
    return await _process_frame_recursive(
        root=root,
        processed_roots=processed,
        iframe_timeout=iframe_timeout,
    )


async def find_all_iframes_list(
    root: Page | Frame | Locator,
    iframe_timeout: float = 10.0,
) -> list[IframeNode]:
    """
    Same as find_all_iframes, but returns a flat list of all iframe nodes (including nested ones).
    This is useful for when you want to iterate over all iframes in a single loop.
    """
    iframe_nodes = await find_all_iframes(root, iframe_timeout)
    return _flatten_iframe_tree(iframe_nodes)


async def _process_frame_recursive(
    root: Page | Frame | Locator,
    processed_roots: set[Page | Frame | Locator],
    iframe_timeout: float,
) -> list[IframeNode]:
    if root in processed_roots:
        return []

    processed_roots.add(root)
    iframe_nodes: list[IframeNode] = []

    # In every operation that accesses an iframe, we wrap it in a timeout
    # to avoid hanging due to problematic iframe sources (see test_get_all_iframes_with_problematic_srcs)

    try:
        iframe_locator = root.locator(ALL_IFRAMES_CSS_SELECTOR)

        try:
            iframe_count = await asyncio.wait_for(
                iframe_locator.count(),
                timeout=iframe_timeout,
            )
        except TimeoutError:
            logger.error("Timeout counting iframes in context, skipping")
            return []

        for i in range(iframe_count):
            try:

                async def process_single_iframe(index: int):
                    iframe_element_locator = iframe_locator.nth(index)

                    iframe_element = await iframe_element_locator.element_handle()
                    if not iframe_element:
                        logger.error(f"Could not get element handle for iframe: {iframe_element}")
                        return None

                    content_frame = await iframe_element.content_frame()
                    if not content_frame:
                        logger.error(f"Could not access content_frame for iframe: {iframe_element}")
                        return None

                    allows_async_scripts = await check_frame_allows_async_scripts(iframe_element)

                    nested_iframes = await _process_frame_recursive(
                        root=content_frame,
                        processed_roots=processed_roots,
                        iframe_timeout=iframe_timeout,
                    )

                    return IframeNode(
                        frame=content_frame,
                        nested_iframes=nested_iframes,
                        allows_async_scripts=allows_async_scripts,
                    )

                iframe_node = await asyncio.wait_for(
                    process_single_iframe(i),
                    timeout=iframe_timeout,
                )

                if iframe_node is not None:
                    iframe_nodes.append(iframe_node)

            except TimeoutError:
                logger.error(f"Timeout processing iframe {i} in context, skipping")
                continue
            except Exception as e:
                logger.error(f"Error processing individual iframe: {e}", exc_info=False)
                continue

    except Exception as e:
        logger.error(f"Error processing frames in context: {e}", exc_info=True)

    return iframe_nodes


def _flatten_iframe_tree(iframe_nodes: list[IframeNode]) -> list[IframeNode]:
    """
    Flatten a tree of iframe nodes into a list.

    Args:
        iframe_nodes: List of top-level iframe nodes

    Returns:
        A flat list of all iframe nodes (including nested ones)
    """
    flattened: list[IframeNode] = []

    def _flatten_recursive(nodes: list[IframeNode]):
        for node in nodes:
            flattened.append(node)
            if node.nested_iframes:
                _flatten_recursive(node.nested_iframes)

    _flatten_recursive(iframe_nodes)
    return flattened
