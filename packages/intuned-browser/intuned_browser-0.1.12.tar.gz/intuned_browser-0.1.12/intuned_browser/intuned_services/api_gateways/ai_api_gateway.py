import os
from typing import Any

from litellm import acompletion

from intuned_browser.intuned_services.api_gateways.models import get_model_provider
from intuned_browser.intuned_services.api_gateways.types import GatewayConfig
from intuned_browser.intuned_services.api_gateways.types import ModelConfig


class APIGateway:
    """
    Unified gateway for LLM API calls that handles both direct and gateway routing.
    Works seamlessly with litellm.
    """

    def __init__(self, model: str, api_key: str | None = None):
        """
        Initialize the API Gateway.

        Args:
            model: The model identifier (e.g., "gpt-4o", "claude-haiku-4-5-20251001")
            api_key: Optional API key for direct mode
        """
        self.model = model
        self.api_key = api_key
        self.config: GatewayConfig | None = None
        self.use_gateway = False
        self._is_initialized = False

    def _get_api_key_from_env(self, provider: str) -> str | None:
        """Get API key from environment variables based on provider."""
        if provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif provider == "google_vertexai":
            return os.getenv("GOOGLE_API_KEY")
        return None

    def _validate_intuned_context(self) -> None:
        """Validate that we're running in an Intuned context."""
        try:
            from runtime.context.context import IntunedContext

            current_context = IntunedContext.current()
            if not current_context:
                raise ValueError(
                    "No API key provided and not running in Intuned context. "
                    "Please provide an API key or ensure you're running within an Intuned workflow."
                )
        except ImportError as e:
            raise ValueError(
                "No API key provided and not running in Intuned context. "
                "Please provide an API key or ensure the Intuned Runtime SDK is installed "
                "and you're running within an Intuned workflow."
            ) from e
        except LookupError as e:
            raise ValueError(
                "No API key provided and not running in Intuned context. "
                "Please provide an API key or ensure you're running within an Intuned workflow."
            ) from e

    def _validate_gateway_config(self, config: GatewayConfig) -> None:
        """Validate that all required gateway configuration is present."""
        missing_vars = []

        if not config.functions_domain:
            missing_vars.append("FUNCTIONS_DOMAIN")
        if not config.workspace_id:
            missing_vars.append("INTUNED_WORKSPACE_ID")
        if not config.project_id:
            missing_vars.append("INTUNED_PROJECT_ID")

        if missing_vars:
            raise ValueError(
                f"Gateway configuration is incomplete. Missing environment variables: {', '.join(missing_vars)}. "
                "These are required when running in Intuned context without an API key."
            )

    def _load_gateway_config(self) -> GatewayConfig:
        """Load gateway configuration from environment variables."""
        try:
            from runtime.env import get_functions_domain
            from runtime.env import get_project_id
            from runtime.env import get_workspace_id

            return GatewayConfig(
                functions_domain=get_functions_domain(),
                workspace_id=get_workspace_id(),
                project_id=get_project_id(),
            )
        except ImportError as e:
            raise ValueError(
                "Failed to load gateway configuration. " "Ensure the Intuned Runtime SDK is installed."
            ) from e

    def _ensure_initialized(self) -> None:
        """Ensure the gateway is initialized with proper configuration."""
        if self._is_initialized:
            return

        provider = self._detect_provider(self.model)

        # If apiKey is provided, use direct mode
        if self.api_key:
            self.use_gateway = False
            self._is_initialized = True
            return

        # Try to find API key in environment variables
        env_api_key = self._get_api_key_from_env(provider)
        if env_api_key:
            self.api_key = env_api_key
            self.use_gateway = False
            self._is_initialized = True
            return

        # No API key found, need to use gateway - validate intuned context
        self._validate_intuned_context()

        # Load gateway config from environment
        self.config = self._load_gateway_config()
        self._validate_gateway_config(self.config)
        self.use_gateway = True
        self._is_initialized = True

    def _detect_provider(self, model: str) -> str:
        """Detect the provider from the model name"""
        model_lower = model.lower()
        return get_model_provider(model_lower) or "unknown"

    def _build_gateway_url(self, provider: str) -> str:
        """Build the gateway URL for a specific provider"""
        if not self.config:
            raise ValueError("Gateway configuration not initialized")

        base_domain = str(self.config.functions_domain).rstrip("/")
        return f"{base_domain}/api/{self.config.workspace_id}/functions/{self.config.project_id}/{provider}"

    def _get_model_config(self, extra_headers: dict[str, Any] | None = None) -> ModelConfig:
        """
        Get the configuration for the model, determining whether to use direct or gateway mode.

        Args:
            extra_headers: Optional extra headers

        Returns:
            ModelConfig with appropriate settings for litellm
        """
        provider = self._detect_provider(self.model)

        # Direct mode - use the API key directly
        if not self.use_gateway and self.api_key:
            return ModelConfig(model=self.model, api_key=self.api_key, extra_headers=extra_headers, base_url=None)

        # Gateway mode - build the gateway URL and add auth headers
        base_url = self._build_gateway_url(provider)

        try:
            from runtime.context.context import IntunedContext
            from runtime.env import get_api_key

            extra_headers = extra_headers or {}
            current_context = IntunedContext.current()
            if current_context and current_context.functions_token:
                extra_headers["Authorization"] = f"Bearer {current_context.functions_token}"
            intuned_api_key = get_api_key()
            if intuned_api_key:
                extra_headers["x-api-key"] = intuned_api_key

            return ModelConfig(
                model=self.model,
                api_key=intuned_api_key or "--THIS_VALUE_WILL_BE_REPLACED_BY_INTUNED_BE--",
                extra_headers=extra_headers,
                base_url=base_url,
            )
        except (ImportError, LookupError) as e:
            raise ValueError(
                "Failed to configure gateway mode. "
                "Ensure the Intuned Runtime SDK is installed and you're running within an Intuned workflow."
            ) from e

    async def acompletion(self, **kwargs) -> Any:
        """
        Wrapper around litellm.acompletion that handles gateway routing.

        This method ensures proper initialization and configuration before
        calling litellm with the appropriate settings.
        """
        # Ensure gateway is initialized
        self._ensure_initialized()

        # Extract extra headers if provided
        extra_headers = kwargs.get("extra_headers", {})

        # Get the model configuration
        config = self._get_model_config(extra_headers)

        # Update kwargs with gateway configuration
        kwargs["model"] = config.model
        kwargs["api_key"] = config.api_key
        if config.base_url:
            kwargs["base_url"] = config.base_url
        if config.extra_headers:
            kwargs["extra_headers"] = {
                **extra_headers,
                **config.extra_headers,
            }

        # Call litellm
        return await acompletion(**kwargs)
