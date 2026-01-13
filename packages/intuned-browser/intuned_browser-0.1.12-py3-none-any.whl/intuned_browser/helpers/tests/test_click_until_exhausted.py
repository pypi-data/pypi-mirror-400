import pytest
from runtime import launch_chromium

from intuned_browser.helpers.click_until_exhausted import click_button_and_wait
from intuned_browser.helpers.click_until_exhausted import click_until_exhausted

# HTML for testing basic button clicking with content loading
basic_click_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial; }
        .item { height: 80px; margin: 10px; background: #e0e0e0; padding: 15px; border: 1px solid #999; }
        #load-more { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        #content { margin-top: 20px; }
    </style>
</head>
<body>
    <button id="load-more">Load More</button>
    <div id="content">
        <div class="item">Item 1</div>
        <div class="item">Item 2</div>
        <div class="item">Item 3</div>
    </div>
    <script>
        let itemCount = 3;
        let maxItems = 10;

        document.getElementById('load-more').addEventListener('click', () => {
            if (itemCount >= maxItems) return;

            itemCount++;
            const newItem = document.createElement('div');
            newItem.className = 'item';
            newItem.textContent = 'Item ' + itemCount;
            document.getElementById('content').appendChild(newItem);
        });
    </script>
</body>
</html>
"""

# HTML for testing button that becomes disabled after certain clicks
button_becomes_disabled_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial; }
        .item { height: 80px; margin: 10px; background: #e0e0e0; padding: 15px; border: 1px solid #999; }
        #load-more { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        #load-more:disabled { opacity: 0.5; cursor: not-allowed; }
        #content { margin-top: 20px; }
    </style>
</head>
<body>
    <button id="load-more">Load More</button>
    <div id="content">
        <div class="item">Item 1</div>
    </div>
    <script>
        let itemCount = 1;
        let maxItems = 5;
        const button = document.getElementById('load-more');

        button.addEventListener('click', () => {
            if (itemCount >= maxItems) {
                button.disabled = true;
                return;
            }

            itemCount++;
            const newItem = document.createElement('div');
            newItem.className = 'item';
            newItem.textContent = 'Item ' + itemCount;
            document.getElementById('content').appendChild(newItem);

            if (itemCount >= maxItems) {
                button.disabled = true;
            }
        });
    </script>
</body>
</html>
"""

# HTML for testing button that becomes invisible after certain clicks
button_becomes_invisible_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial; }
        .item { height: 80px; margin: 10px; background: #e0e0e0; padding: 15px; border: 1px solid #999; }
        #load-more { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        #content { margin-top: 20px; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <button id="load-more">Load More</button>
    <div id="content">
        <div class="item">Item 1</div>
    </div>
    <script>
        let itemCount = 1;
        let maxItems = 5;
        const button = document.getElementById('load-more');
        button.addEventListener('click', () => {
            if (itemCount >= maxItems) {
                button.classList.add('hidden');
                return;
            }

            itemCount++;
            const newItem = document.createElement('div');
            newItem.className = 'item';
            newItem.textContent = 'Item ' + itemCount;
            document.getElementById('content').appendChild(newItem);

            if (itemCount >= maxItems) {
                button.classList.add('hidden');
            }
        });
    </script>
</body>
</html>
"""

# HTML for testing with a specific container
container_tracking_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial; }
        #container {
            border: 2px solid #333;
            padding: 10px;
            min-height: 200px;
            margin-top: 20px;
        }
        .container-item {
            height: 60px;
            margin: 10px;
            background: #aaf;
            padding: 10px;
            border: 1px solid #006;
        }
        #load-more { padding: 10px 20px; font-size: 16px; cursor: pointer; }
    </style>
</head>
<body>
    <button id="load-more">Load More</button>
    <div id="container">
        <div class="container-item">Container Item 1</div>
        <div class="container-item">Container Item 2</div>
    </div>
    <script>
        let itemCount = 2;
        let maxItems = 8;

        document.getElementById('load-more').addEventListener('click', () => {
            if (itemCount >= maxItems) return;

            itemCount++;
            const newItem = document.createElement('div');
            newItem.className = 'container-item';
            newItem.textContent = 'Container Item ' + itemCount;
            document.getElementById('container').appendChild(newItem);
        });
    </script>
</body>
</html>
"""

# HTML for testing button that stops producing changes after some clicks
no_change_threshold_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 20px; font-family: Arial; }
        .item { height: 80px; margin: 10px; background: #e0e0e0; padding: 15px; border: 1px solid #999; }
        #load-more { padding: 10px 20px; font-size: 16px; cursor: pointer; }
        #content { margin-top: 20px; }
    </style>
</head>
<body>
    <button id="load-more">Load More</button>
    <div id="content">
        <div class="item">Item 1</div>
    </div>
    <script>
        let itemCount = 1;
        let clickCount = 0;
        let maxItems = 5;

        document.getElementById('load-more').addEventListener('click', () => {
            clickCount++;
            // Only add items for first 5 clicks, then stop adding
            if (clickCount <= 5 && itemCount < maxItems) {
                itemCount++;
                const newItem = document.createElement('div');
                newItem.className = 'item';
                newItem.textContent = 'Item ' + itemCount;
                document.getElementById('content').appendChild(newItem);
            }
            // After 5 clicks, button still works but doesn't add content
        });
    </script>
</body>
</html>
"""


@pytest.mark.asyncio
async def test_click_button_and_wait_basic():
    """Test basic button click functionality."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(basic_click_html)

        # Get initial item count
        initial_count = await page.locator(".item").count()
        assert initial_count == 3

        # Click button once
        button_locator = page.locator("#load-more")
        await click_button_and_wait(page, button_locator, click_delay=0.1)

        # Verify one more item was loaded
        final_count = await page.locator(".item").count()
        assert final_count == 4


@pytest.mark.asyncio
async def test_click_until_exhausted_default_params():
    """Test clicking button until max items loaded with default parameters."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(basic_click_html)

        # Get initial item count
        initial_count = await page.locator(".item").count()
        assert initial_count == 3

        # Click button until exhausted
        button_locator = page.locator("#load-more")
        await click_until_exhausted(page, button_locator)

        # Verify all items were loaded
        final_count = await page.locator(".item").count()
        assert final_count == 10  # Max items defined in HTML


@pytest.mark.asyncio
async def test_click_until_exhausted_with_max_clicks():
    """Test that max_clicks parameter limits the number of clicks."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(basic_click_html)

        initial_count = await page.locator(".item").count()
        assert initial_count == 3

        # Click button with limited max_clicks
        button_locator = page.locator("#load-more")
        await click_until_exhausted(page, button_locator, max_clicks=3, click_delay=0.05)

        # Verify only 3 more items were loaded
        final_count = await page.locator(".item").count()
        assert final_count == 6  # 3 initial + 3 clicks


@pytest.mark.asyncio
async def test_click_until_exhausted_with_heartbeat():
    """Test that heartbeat callback is called after each click."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(basic_click_html)

        # Track heartbeat calls
        heartbeat_calls = []

        def on_heartbeat():
            heartbeat_calls.append(1)

        # Click button with heartbeat callback
        button_locator = page.locator("#load-more")
        await click_until_exhausted(page, button_locator, heartbeat=on_heartbeat, max_clicks=5, click_delay=0.05)

        # Verify heartbeat was called
        assert len(heartbeat_calls) == 5


@pytest.mark.asyncio
async def test_click_button_stops_when_disabled():
    """Test that clicking stops when button becomes disabled."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(button_becomes_disabled_html)

        initial_count = await page.locator(".item").count()
        assert initial_count == 1

        # Click button until it becomes disabled
        button_locator = page.locator("#load-more")
        await click_until_exhausted(
            page,
            button_locator,
            max_clicks=20,  # More than needed
            click_delay=0.05,
        )

        # Verify it stopped at max items (5)
        final_count = await page.locator(".item").count()
        assert final_count == 5

        # Verify button is disabled
        is_disabled = await page.evaluate("document.getElementById('load-more').disabled")
        assert is_disabled is True


@pytest.mark.asyncio
async def test_click_button_stops_when_invisible():
    """Test that clicking stops when button becomes invisible."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(button_becomes_invisible_html)

        initial_count = await page.locator(".item").count()
        assert initial_count == 1

        # Click button until it becomes invisible
        button_locator = page.locator("#load-more")
        await click_until_exhausted(
            page,
            button_locator,
            max_clicks=20,  # More than needed
            click_delay=0.05,
        )

        # Verify it stopped at max items (5)
        final_count = await page.locator(".item").count()
        assert final_count == 5

        # Verify button is invisible
        is_visible = await button_locator.is_visible()
        assert is_visible is False


@pytest.mark.asyncio
async def test_click_button_with_container_tracking():
    """Test clicking with container_locator to track content changes."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(container_tracking_html)

        initial_count = await page.locator(".container-item").count()
        assert initial_count == 2

        # Click button with container tracking
        button_locator = page.locator("#load-more")
        container_locator = page.locator("#container")

        await click_until_exhausted(
            page, button_locator, container_locator=container_locator, max_clicks=10, click_delay=0.05
        )

        # Verify all items were loaded
        final_count = await page.locator(".container-item").count()
        assert final_count == 8  # Max items defined in HTML


@pytest.mark.asyncio
async def test_click_button_with_no_change_threshold():
    """Test that clicking stops when content stops changing."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(no_change_threshold_html)

        initial_count = await page.locator(".item").count()
        assert initial_count == 1

        # Click button with container tracking and no_change_threshold
        button_locator = page.locator("#load-more")
        container_locator = page.locator("#content")

        await click_until_exhausted(
            page,
            button_locator,
            container_locator=container_locator,
            max_clicks=20,  # More than needed
            click_delay=0.05,
            no_change_threshold=0,  # Stop immediately when no change detected
        )

        # Should have loaded 5 items (1 initial + 4 from clicks)
        # Then stopped when no more content was added
        final_count = await page.locator(".item").count()
        assert final_count == 5


@pytest.mark.asyncio
async def test_click_button_with_custom_click_delay():
    """Test clicking with custom click delay."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(basic_click_html)

        initial_count = await page.locator(".item").count()

        # Click button with longer delay
        button_locator = page.locator("#load-more")
        await click_until_exhausted(
            page,
            button_locator,
            max_clicks=3,
            click_delay=0.2,  # Longer delay
        )

        # Verify items were loaded
        final_count = await page.locator(".item").count()
        assert final_count > initial_count


@pytest.mark.asyncio
async def test_click_button_with_all_custom_params():
    """Test clicking with all custom parameters combined."""
    async with launch_chromium(headless=True) as (_, page):
        await page.set_content(container_tracking_html)

        # Track heartbeat calls
        heartbeat_calls = []

        def on_heartbeat():
            heartbeat_calls.append(1)

        # Click with all custom parameters
        button_locator = page.locator("#load-more")
        container_locator = page.locator("#container")

        await click_until_exhausted(
            page,
            button_locator,
            heartbeat=on_heartbeat,
            container_locator=container_locator,
            max_clicks=4,
            click_delay=0.1,
            no_change_threshold=0,
        )

        # Verify items were loaded (2 initial + 4 clicks = 6)
        final_count = await page.locator(".container-item").count()
        assert final_count == 6

        # Verify heartbeat was called 4 times
        assert len(heartbeat_calls) == 4
