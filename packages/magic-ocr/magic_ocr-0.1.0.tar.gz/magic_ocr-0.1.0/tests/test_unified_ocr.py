"""Tests for unified OCR tool."""

import pytest
from unittest.mock import AsyncMock, patch
from magic_ocr.utils import detect_image_input_type
from magic_ocr.mcp.tools import ocr_image


class TestDetectImageInputType:
    def test_http_https_detection(self):
        assert detect_image_input_type("http://example.invalid/image.jpg") == "url"
        assert detect_image_input_type("https://example.invalid/image.jpg") == "url"

    def test_data_uri_and_base64_detection(self):
        assert detect_image_input_type("data:image/png;base64,iVBORw0KGgo=") == "base64"
        import base64
        valid_base64 = base64.b64encode(b"fake image data").decode()
        assert detect_image_input_type(valid_base64) == "base64"

    def test_file_path_detection(self, tmp_path):
        p = tmp_path / "t.png"
        p.write_bytes(b"img")
        assert detect_image_input_type(str(p)) == "file_path"

    def test_empty_or_invalid_input(self):
        with pytest.raises(ValueError):
            detect_image_input_type("")
        with pytest.raises(ValueError):
            detect_image_input_type("not-a-valid-input-!@#")


class TestOCRHappyPaths:
    @pytest.fixture
    def mock_file_ocr(self):
        with patch('magic_ocr.mcp.tools.detect_image_input_type') as mock_detect, \
             patch('magic_ocr.mcp.tools.read_image_file') as mock_read, \
             patch('magic_ocr.mcp.tools.get_config') as _mock_config, \
             patch('magic_ocr.mcp.tools.get_ocr_client') as mock_client:
            mock_detect.return_value = 'file_path'
            mock_read.return_value = (b'bytes', 'image/png')
            ocr = AsyncMock()
            ocr.extract_text = AsyncMock(return_value="ok-file")
            ocr.provider_name = "Test"
            ocr.model_name = "m"
            mock_client.return_value = ocr
            yield {"client": mock_client, "ocr": ocr}

    @pytest.mark.asyncio
    async def test_file_path(self, mock_file_ocr):
        out = await ocr_image("/p/img.png")
        assert out == "ok-file"

    @pytest.fixture
    def mock_base64_ocr(self):
        with patch('magic_ocr.mcp.tools.detect_image_input_type') as mock_detect, \
             patch('magic_ocr.mcp.tools.decode_base64_image') as mock_decode, \
             patch('magic_ocr.mcp.tools.get_config') as _mock_config, \
             patch('magic_ocr.mcp.tools.get_ocr_client') as mock_client:
            mock_detect.return_value = 'base64'
            mock_decode.return_value = (b'bytes', 'image/jpeg')
            ocr = AsyncMock()
            ocr.extract_text = AsyncMock(return_value="ok-b64")
            mock_client.return_value = ocr
            yield {"client": mock_client, "ocr": ocr}

    @pytest.mark.asyncio
    async def test_base64(self, mock_base64_ocr):
        out = await ocr_image("iVBORw0KGgoAAA==")
        assert out == "ok-b64"

    @pytest.fixture
    def mock_url_ocr(self):
        with patch('magic_ocr.mcp.tools.detect_image_input_type') as mock_detect, \
             patch('magic_ocr.mcp.tools.get_config') as _mock_config, \
             patch('magic_ocr.mcp.tools.get_ocr_client') as mock_client:
            mock_detect.return_value = 'url'
            ocr = AsyncMock()
            ocr.extract_text_from_url = AsyncMock(return_value="ok-url")
            mock_client.return_value = ocr
            yield {"client": mock_client, "ocr": ocr}

    @pytest.mark.asyncio
    async def test_url(self, mock_url_ocr):
        out = await ocr_image("https://example.invalid/img.jpg")
        assert out == "ok-url"


class TestParamsForwarding:
    @pytest.mark.asyncio
    async def test_provider_pass_through(self):
        with patch('magic_ocr.mcp.tools.detect_image_input_type') as mock_detect, \
             patch('magic_ocr.mcp.tools.read_image_file') as mock_read, \
             patch('magic_ocr.mcp.tools.get_config') as _mock_config, \
             patch('magic_ocr.mcp.tools.get_ocr_client') as mock_client:
            mock_detect.return_value = 'file_path'
            mock_read.return_value = (b'bytes', 'image/png')
            ocr = AsyncMock()
            ocr.extract_text = AsyncMock(return_value="ok")
            mock_client.return_value = ocr
            await ocr_image("/p/im.png", provider="gemini")
            assert mock_client.call_args.kwargs["provider"] == "gemini"

    @pytest.mark.asyncio
    async def test_model_pass_through_for_gcp(self):
        with patch('magic_ocr.mcp.tools.detect_image_input_type') as mock_detect, \
             patch('magic_ocr.mcp.tools.read_image_file') as mock_read, \
             patch('magic_ocr.mcp.tools.get_config') as _mock_config, \
             patch('magic_ocr.mcp.tools.get_ocr_client') as mock_client:
            mock_detect.return_value = 'file_path'
            mock_read.return_value = (b'bytes', 'image/png')
            ocr = AsyncMock()
            ocr.extract_text = AsyncMock(return_value="ok")
            mock_client.return_value = ocr
            await ocr_image("/p/im.png", provider="gcp", model="document")
            assert mock_client.call_args.kwargs["model"] == "document"


class TestErrorPath:
    @pytest.mark.asyncio
    async def test_invalid_input_raises(self):
        with patch('magic_ocr.mcp.tools.detect_image_input_type') as mock_detect:
            mock_detect.side_effect = ValueError("Unable to determine type")
            with pytest.raises(ValueError):
                await ocr_image("bad")

    @pytest.mark.asyncio
    async def test_ocr_error_propagates(self):
        with patch('magic_ocr.mcp.tools.detect_image_input_type') as mock_detect, \
             patch('magic_ocr.mcp.tools.read_image_file') as mock_read, \
             patch('magic_ocr.mcp.tools.get_config') as _mock_config, \
             patch('magic_ocr.mcp.tools.get_ocr_client') as mock_client:
            mock_detect.return_value = 'file_path'
            mock_read.return_value = (b'bytes', 'image/png')
            from magic_ocr.base import OCRClientError
            ocr = AsyncMock()
            ocr.extract_text = AsyncMock(side_effect=OCRClientError("API error"))
            mock_client.return_value = ocr
            with pytest.raises(OCRClientError):
                await ocr_image("/p/im.png")
