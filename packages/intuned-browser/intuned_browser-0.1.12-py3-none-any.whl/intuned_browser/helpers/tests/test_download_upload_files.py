import os

import pytest
from dotenv import load_dotenv
from playwright._impl._errors import Error
from playwright.async_api import Download
from runtime import launch_chromium

from intuned_browser.helpers import download_file
from intuned_browser.helpers import upload_file_to_s3

load_dotenv(override=True)
content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Fixture Page</title>
</head>
<body>
    <h1>Test Fixture Page</h1>
    <p>This is a simple HTML page used for testing purposes.</p>
    <div>
        <h3>Downloadable Image</h3>
        <p>Image for download:</p>
        <img src="https://cdn11.bigcommerce.com/s-scmrv6kkrz/images/stencil/1280x1280/products/192719/166712/1891-clear-14-vdc-miniature-lb93__16581.1568390384.jpg?c=2" alt="Sample placeholder image" width="400" height="300">
        <br>
        <a href="https://cdn11.bigcommerce.com/s-scmrv6kkrz/images/stencil/1280x1280/products/192719/166712/1891-clear-14-vdc-miniature-lb93__16581.1568390384.jpg?c=2" download="sample-image.png">Download Image</a>
    </div>
    <div>
        <h3>Download normal file</h3>
        <a href="https://intuned-docs-public-images.s3.amazonaws.com/32UP83A_ENG_US.pdf" download="sample-file.txt">Download Text File</a>
    </div>

    <div>
        <h3>Large PDF Download</h3>
        <a href="https://intuned-docs-public-images.s3.us-west-2.amazonaws.com/large_pdf.pdf">Download Text File</a>
    </div>

    <div>
        <h3>Print Dialog Download</h3>
        <button id="print-button">Print Document</button>
        <script>
            document.getElementById('print-button').addEventListener('click', function() {
                window.print();
            });
        </script>
    </div>

    <div>
        <h3>Invalid URL that triggers download</h3>
        <a id="invalid-url-link" href="#" download="manual.pdf">Download with Invalid URL</a>
        <script>
            // Set href with spaces (fails validators.url but browser handles it)
            document.getElementById('invalid-url-link').href = 'https://intuned-docs-public-images.s3.amazonaws.com/27UP600_27UP650_ENG_US.pdf';
        </script>
    </div>

</body>
</html>
"""


@pytest.mark.skip(reason="These tests upload files to S3.")
class TestNotInGeneration:
    @classmethod
    def setup_class(cls):
        os.environ["MODE"] = ""

    @pytest.mark.asyncio
    async def test_should_not_cancel_download(self):
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            download = await download_file(
                page=page, trigger="https://intuned-docs-public-images.s3.amazonaws.com/32UP83A_ENG_US.pdf"
            )
            download_path = (
                await download.path()
            )  # should not throw because it is not cancelled when not in generation mode
            assert download.suggested_filename is not None
            assert download_path is not None

    @pytest.mark.asyncio
    async def test_should_download_image_successfully(self):
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            downloaded_image = await download_file(
                page=page,
                trigger="https://cdn11.bigcommerce.com/s-scmrv6kkrz/images/stencil/1280x1280/products/192719/166712/1891-clear-14-vdc-miniature-lb93__16581.1568390384.jpg?c=2",
            )
            path = await downloaded_image.path()
            assert "/var/folders" in path.__str__()

    @pytest.mark.asyncio
    async def test_upload_image_to_s3(self):
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            downloaded_image = await download_file(
                page=page,
                trigger="https://cdn11.bigcommerce.com/s-scmrv6kkrz/images/stencil/1280x1280/products/192719/166712/1891-clear-14-vdc-miniature-lb93__16581.1568390384.jpg?c=2",
            )
            path = await downloaded_image.path()
            assert path is not None
            assert os.path.exists(path)  # noqa
            uploaded_file = await upload_file_to_s3(downloaded_image)
            assert not os.path.exists(path)  # should delete the file after upload #noqa
            assert uploaded_file.suggested_file_name is not None
            assert uploaded_file.bucket == os.environ.get("INTUNED_S3_BUCKET")

    @pytest.mark.asyncio
    async def test_upload_file_to_s3(self):
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            download = await download_file(
                page=page, trigger="https://intuned-docs-public-images.s3.amazonaws.com/32UP83A_ENG_US.pdf"
            )
            assert isinstance(download, Download)
            uploaded_file = await upload_file_to_s3(download)
            assert uploaded_file.suggested_file_name is not None
            assert uploaded_file.bucket == os.environ.get("INTUNED_S3_BUCKET")

    @pytest.mark.asyncio
    async def test_print_dialog_download(self):
        async with launch_chromium(headless=False) as (context, page):
            await page.set_content(content)
            print_button = page.locator("#print-button")
            download = await download_file(page=page, trigger=print_button)
            assert isinstance(download, Download)
            download_path = await download.path()
            assert download_path is not None
            assert download.suggested_filename.endswith(".pdf")

    @pytest.mark.asyncio
    async def test_invalid_url_triggers_download(self):
        """Test when validators.url fails but download still triggers"""
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            # URL with unencoded spaces - fails validators.url() but browser can handle it
            invalid_url = "https://intuned-docs-public-images.s3.amazonaws.com/27UP600_27UP650_ENG_US.pdf "
            # Verify it actually fails validation
            import validators

            assert not validators.url(invalid_url), "URL should fail validation"
            # But download should still work
            download = await download_file(page=page, trigger=invalid_url)
            assert download is not None


class TestInGeneration:
    @classmethod
    def setup_class(cls):
        os.environ["MODE"] = "generate_code"

    @pytest.mark.asyncio
    async def test_should_cancel_download(self):
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            large_pdf_locator = page.locator("xpath=//a[contains(@href, 'large_pdf.pdf')]")
            downloaded_file = await download_file(page=page, trigger=large_pdf_locator)
            with pytest.raises(Error) as err:
                await downloaded_file.path()
            assert "canceled" in str(err.value)

    @pytest.mark.asyncio
    async def test_should_download_image_successfully(self):
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            downloaded_image = await download_file(
                page=page,
                trigger="https://cdn11.bigcommerce.com/s-scmrv6kkrz/images/stencil/1280x1280/products/192719/166712/1891-clear-14-vdc-miniature-lb93__16581.1568390384.jpg?c=2",
            )
            cancelled = await downloaded_image.failure()
            assert cancelled is None or "canceled" in cancelled  # sometimes the download is too quick to be cancelled.

    @pytest.mark.asyncio
    async def test_upload_image_to_s3(self):
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            downloaded_image = await download_file(
                page=page,
                trigger="https://cdn11.bigcommerce.com/s-scmrv6kkrz/images/stencil/1280x1280/products/192719/166712/1891-clear-14-vdc-miniature-lb93__16581.1568390384.jpg?c=2",
            )
            uploaded_file = await upload_file_to_s3(downloaded_image)
            assert uploaded_file.suggested_file_name is not None
            assert uploaded_file.bucket == "testing_bucket"

    @pytest.mark.asyncio
    async def test_upload_file_to_s3(self):
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            download = await download_file(
                page=page, trigger="https://intuned-docs-public-images.s3.amazonaws.com/32UP83A_ENG_US.pdf"
            )
            assert isinstance(download, Download)
            uploaded_file = await upload_file_to_s3(download)
            assert uploaded_file.suggested_file_name is not None
            assert uploaded_file.bucket == "testing_bucket"
            assert uploaded_file.region == "testing_region"

    @pytest.mark.asyncio
    async def test_print_dialog_download(self):
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            print_button = page.locator("#print-button")
            download = await download_file(page=page, trigger=print_button)
            assert isinstance(download, Download)
            cancelled = await download.failure()
            assert cancelled is None or "canceled" in cancelled

    @pytest.mark.asyncio
    async def test_invalid_url_triggers_download(self):
        """Test when validators.url fails but download still triggers"""
        async with launch_chromium(headless=True) as (context, page):
            await page.set_content(content)
            # URL with trailing space - fails validators.url() but browser can handle it
            invalid_url = "https://intuned-docs-public-images.s3.amazonaws.com/27UP600_27UP650_ENG_US.pdf "
            # Verify it actually fails validation
            import validators

            assert not validators.url(invalid_url), "URL should fail validation"
            # But download should still work (and be cancelled in generate mode)
            download = await download_file(page=page, trigger=invalid_url)
            assert isinstance(download, Download)
            cancelled = await download.failure()
            assert cancelled is None or "canceled" in cancelled
