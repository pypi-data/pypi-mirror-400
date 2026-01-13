"""
LLM Provider Factory for XuguDB MCP Server.

Creates LLM provider instances based on configuration.
"""
from typing import Optional

from .base import BaseLLMProvider, LLMConfig
from .claude import ClaudeProvider
from .openai import OpenAIProvider
from .zhipu import ZhipuProvider
from .local import LocalProvider


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    # Supported providers
    PROVIDERS = {
        "claude": ClaudeProvider,
        "anthropic": ClaudeProvider,
        "openai": OpenAIProvider,
        "zai": ZhipuProvider,
        "zhipu": ZhipuProvider,
        "zhipuai": ZhipuProvider,
        "local": LocalProvider,
        "ollama": LocalProvider,
    }

    @classmethod
    def create(
        cls,
        provider: str,
        api_key: str,
        model: str,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        timeout: int = 60,
        base_url: Optional[str] = None,
    ) -> BaseLLMProvider:
        """Create an LLM provider instance.

        Args:
            provider: Provider name (claude, openai, zai, local)
            api_key: API key for the provider
            model: Model name/identifier
            temperature: Generation temperature (0.0 - 1.0)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            base_url: Optional custom base URL

        Returns:
            BaseLLMProvider instance

        Raises:
            ValueError: If provider is not supported
        """
        provider_lower = provider.lower()

        if provider_lower not in cls.PROVIDERS:
            supported = ", ".join(cls.PROVIDERS.keys())
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: {supported}"
            )

        provider_class = cls.PROVIDERS[provider_lower]

        config = LLMConfig(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            base_url=base_url,
        )

        return provider_class(config)

    @classmethod
    def create_from_dict(cls, config: dict) -> BaseLLMProvider:
        """Create provider from configuration dictionary.

        Args:
            config: Dictionary with keys:
                - provider: str (required)
                - api_key: str (required)
                - model: str (required)
                - temperature: float (optional)
                - max_tokens: int (optional)
                - timeout: int (optional)
                - base_url: str (optional)

        Returns:
            BaseLLMProvider instance
        """
        return cls.create(
            provider=config.get("provider", "openai"),
            api_key=config.get("api_key", ""),
            model=config.get("model", "gpt-3.5-turbo"),
            temperature=config.get("temperature", 0.0),
            max_tokens=config.get("max_tokens", 4096),
            timeout=config.get("timeout", 60),
            base_url=config.get("base_url"),
        )

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """Get list of supported provider names.

        Returns:
            List of provider names
        """
        return list(cls.PROVIDERS.keys())

    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """Get default model for a provider.

        Args:
            provider: Provider name

        Returns:
            Default model name
        """
        defaults = {
            "claude": "claude-3-5-sonnet",
            "anthropic": "claude-3-5-sonnet",
            "openai": "gpt-4o-mini",
            "zai": "glm-4",
            "zhipu": "glm-4",
            "zhipuai": "glm-4",
            "local": "llama3.2",
            "ollama": "llama3.2",
        }
        return defaults.get(provider.lower(), "gpt-3.5-turbo")
