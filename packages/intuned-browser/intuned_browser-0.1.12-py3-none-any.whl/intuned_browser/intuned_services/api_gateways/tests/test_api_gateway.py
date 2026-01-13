import os
from unittest.mock import patch

import pytest
from runtime.context.context import IntunedContext

from intuned_browser.intuned_services.api_gateways.ai_api_gateway import APIGateway


class TestAPIGateway:
    @pytest.fixture
    def env_vars(self):
        """Set up environment variables for testing"""
        with patch.dict(
            os.environ,
            {
                "FUNCTIONS_DOMAIN": "https://functions.example.com",
                "INTUNED_WORKSPACE_ID": "workspace123",
                "INTUNED_INTEGRATION_ID": "integration456",
            },
        ):
            yield

    def test_init_with_api_key(self):
        gateway = APIGateway(model="gpt-4", api_key="sk-test123")
        assert gateway.model == "gpt-4"
        assert gateway.api_key == "sk-test123"
        assert gateway.use_gateway is False
        assert gateway._is_initialized is False

    def test_init_without_api_key(self):
        gateway = APIGateway(model="gpt-4")
        assert gateway.model == "gpt-4"
        assert gateway.api_key is None
        assert gateway.config is None

    def test_detect_provider_openai_models(self):
        gateway = APIGateway(model="gpt-4")
        assert gateway._detect_provider("gpt-4") == "openai"
        assert gateway._detect_provider("gpt-3.5-turbo") == "openai"
        assert gateway._detect_provider("o1-preview") == "openai"
        assert gateway._detect_provider("o3-mini") == "openai"
        assert gateway._detect_provider("gpt-4o") == "openai"
        assert gateway._detect_provider("o4-model") == "openai"

    def test_detect_provider_anthropic_models(self):
        gateway = APIGateway(model="claude-3-sonnet")
        assert gateway._detect_provider("claude-3-sonnet") == "anthropic"
        assert gateway._detect_provider("claude-3-haiku") == "anthropic"
        assert gateway._detect_provider("CLAUDE-3-OPUS") == "anthropic"  # case insensitive

    def test_detect_provider_google_models(self):
        gateway = APIGateway(model="gemini-pro")
        assert gateway._detect_provider("gemini-pro") == "google_vertexai"
        assert gateway._detect_provider("gemini-1.5-pro") == "google_vertexai"

    def test_detect_provider_unknown_models(self):
        gateway = APIGateway(model="unknown-model")
        assert gateway._detect_provider("unknown-model") == "unknown"
        assert gateway._detect_provider("llama-2") == "unknown"
        assert gateway._detect_provider("mistral-7b") == "unknown"

    def test_ensure_initialized_with_api_key(self):
        gateway = APIGateway(model="gpt-4", api_key="sk-test123")
        gateway._ensure_initialized()

        assert gateway.use_gateway is False
        assert gateway.api_key == "sk-test123"
        assert gateway._is_initialized is True

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-env-key"})
    def test_ensure_initialized_with_env_api_key(self):
        gateway = APIGateway(model="gpt-4")
        gateway._ensure_initialized()

        assert gateway.use_gateway is False
        assert gateway.api_key == "sk-env-key"
        assert gateway._is_initialized is True

    def test_ensure_initialized_without_api_key_not_in_context_raises_error(self):
        gateway = APIGateway(model="gpt-4")

        with pytest.raises(ValueError, match="No API key provided and not running in Intuned context"):
            gateway._ensure_initialized()

    def test_build_gateway_url_success(self, env_vars):
        with IntunedContext():
            gateway = APIGateway(model="claude-3-sonnet")
            gateway._ensure_initialized()

            result = gateway._build_gateway_url("anthropic")
            expected = "https://functions.example.com/api/workspace123/functions/integration456/anthropic"
            assert result == expected

    def test_get_model_config_direct_mode(self):
        # Direct mode when API key is provided
        gateway = APIGateway(model="claude-3-sonnet", api_key="sk-test123")
        gateway._ensure_initialized()
        config = gateway._get_model_config(extra_headers={"Custom-Header": "value"})

        assert config.model == "claude-3-sonnet"
        assert config.api_key == "sk-test123"
        assert config.extra_headers == {"Custom-Header": "value"}
        assert config.base_url is None

    def test_get_model_config_gateway_mode(self, env_vars):
        with IntunedContext():
            gateway = APIGateway(model="claude-3-sonnet")
            gateway._ensure_initialized()
            config = gateway._get_model_config(extra_headers={"Custom-Header": "value"})

            assert config.model == "claude-3-sonnet"
            assert config.api_key == "--THIS_VALUE_WILL_BE_REPLACED_BY_INTUNED_BE--"
            assert (
                config.base_url == "https://functions.example.com/api/workspace123/functions/integration456/anthropic"
            )

    @patch("intuned_browser.intuned_services.api_gateways.ai_api_gateway.acompletion")
    @pytest.mark.asyncio
    async def test_acompletion_direct_mode(self, mock_acompletion):
        gateway = APIGateway(model="claude-3-sonnet", api_key="sk-test123")
        mock_response = {"choices": [{"message": {"content": "test response"}}]}
        mock_acompletion.return_value = mock_response

        result = await gateway.acompletion(messages=[{"role": "user", "content": "test"}])

        assert result == mock_response
        mock_acompletion.assert_called_once()
        call_kwargs = mock_acompletion.call_args[1]
        assert call_kwargs["model"] == "claude-3-sonnet"
        assert call_kwargs["api_key"] == "sk-test123"
        assert call_kwargs["messages"] == [{"role": "user", "content": "test"}]

    @patch("intuned_browser.intuned_services.api_gateways.ai_api_gateway.acompletion")
    @pytest.mark.asyncio
    async def test_acompletion_gateway_mode(self, mock_acompletion, env_vars):
        with IntunedContext():
            gateway = APIGateway(model="claude-3-sonnet")
            mock_response = {"choices": [{"message": {"content": "test response"}}]}
            mock_acompletion.return_value = mock_response

            result = await gateway.acompletion(messages=[{"role": "user", "content": "test"}])

            assert result == mock_response
            mock_acompletion.assert_called_once()
            call_kwargs = mock_acompletion.call_args[1]
            assert call_kwargs["model"] == "claude-3-sonnet"
            assert call_kwargs["api_key"] == "--THIS_VALUE_WILL_BE_REPLACED_BY_INTUNED_BE--"
            assert (
                call_kwargs["base_url"]
                == "https://functions.example.com/api/workspace123/functions/integration456/anthropic"
            )

    @patch("intuned_browser.intuned_services.api_gateways.ai_api_gateway.acompletion")
    @pytest.mark.asyncio
    async def test_acompletion_with_extra_headers(self, mock_acompletion):
        gateway = APIGateway(model="claude-3-sonnet", api_key="sk-test123")
        mock_acompletion.return_value = {"test": "response"}

        await gateway.acompletion(
            messages=[{"role": "user", "content": "test"}], extra_headers={"Custom-Header": "value"}
        )

        mock_acompletion.assert_called_once()
        call_kwargs = mock_acompletion.call_args[1]
        assert call_kwargs["extra_headers"]["Custom-Header"] == "value"
