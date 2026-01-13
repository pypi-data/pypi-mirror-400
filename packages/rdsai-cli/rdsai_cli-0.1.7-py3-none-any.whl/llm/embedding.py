"""Embedding service for generating text embeddings."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Optional

from config import USER_AGENT
from config.app import Config
from config.llm import LLMModel, LLMProvider
from utils.aiohttp import new_client_session
from utils.logging import logger

import aiohttp


class EmbeddingAdapter(ABC):
    """Base class for embedding provider adapters."""

    @abstractmethod
    def build_endpoint(self, base_url: str) -> str:
        """Build the API endpoint URL.

        Args:
            base_url: Base URL of the provider

        Returns:
            Complete endpoint URL
        """
        pass

    @abstractmethod
    def build_payload(self, texts: list[str], model: str) -> dict:
        """Build the request payload.

        Args:
            texts: List of texts to embed
            model: Model name

        Returns:
            Request payload dictionary
        """
        pass

    @abstractmethod
    def build_headers(self, provider: LLMProvider) -> dict:
        """Build request headers including authentication.

        Args:
            provider: LLM provider configuration

        Returns:
            Headers dictionary
        """
        pass

    @abstractmethod
    def parse_response(self, response: dict) -> list[list[float]]:
        """Parse the API response to extract embeddings.

        Args:
            response: JSON response from API

        Returns:
            List of embedding vectors (each is a list of floats)

        Raises:
            ValueError: If response format is invalid
        """
        pass


# ============================================================================
# Concrete Adapter Implementations
# ============================================================================


class _OpenAIEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for OpenAI official embedding API."""

    def build_endpoint(self, base_url: str) -> str:
        base_url = base_url.rstrip("/")
        return f"{base_url}/embeddings"

    def build_payload(self, texts: list[str], model: str) -> dict:
        return {
            "model": model,
            "input": texts if len(texts) > 1 else texts[0],
        }

    def build_headers(self, provider: LLMProvider) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {provider.api_key.get_secret_value()}",
        }
        if provider.custom_headers:
            headers.update(provider.custom_headers)
        return headers

    def parse_response(self, response: dict) -> list[list[float]]:
        if "data" not in response:
            raise ValueError(f"Invalid OpenAI embedding response format: {list(response.keys())}")

        embeddings = []
        for item in response["data"]:
            if "embedding" not in item:
                raise ValueError("Invalid embedding response format: missing 'embedding' field")
            embeddings.append(item["embedding"])
        return embeddings


class _OpenAICompatibleEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for OpenAI-compatible embedding APIs (third-party providers)."""

    def build_endpoint(self, base_url: str) -> str:
        base_url = base_url.rstrip("/")
        return f"{base_url}/embeddings"

    def build_payload(self, texts: list[str], model: str) -> dict:
        return {
            "model": model,
            "input": texts if len(texts) > 1 else texts[0],
        }

    def build_headers(self, provider: LLMProvider) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {provider.api_key.get_secret_value()}",
        }
        if provider.custom_headers:
            headers.update(provider.custom_headers)
        return headers

    def parse_response(self, response: dict) -> list[list[float]]:
        if "data" in response:
            # Standard OpenAI-compatible format
            embeddings = []
            for item in response["data"]:
                if "embedding" not in item:
                    raise ValueError("Invalid embedding response format: missing 'embedding' field")
                embeddings.append(item["embedding"])
            return embeddings
        else:
            raise ValueError(f"Unsupported embedding response format: {list(response.keys())}")


class _QwenEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for Qwen (DashScope) embedding API."""

    def build_endpoint(self, base_url: str) -> str:
        base_url = base_url.rstrip("/")
        return f"{base_url}/embeddings"

    def build_payload(self, texts: list[str], model: str) -> dict:
        return {
            "model": model,
            "input": texts if len(texts) > 1 else texts[0],
        }

    def build_headers(self, provider: LLMProvider) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {provider.api_key.get_secret_value()}",
        }
        if provider.custom_headers:
            headers.update(provider.custom_headers)
        return headers

    def parse_response(self, response: dict) -> list[list[float]]:
        # Qwen supports both OpenAI-compatible format and its own format
        if "data" in response:
            # OpenAI-compatible format
            embeddings = []
            for item in response["data"]:
                if "embedding" not in item:
                    raise ValueError("Invalid embedding response format: missing 'embedding' field")
                embeddings.append(item["embedding"])
            return embeddings
        elif "output" in response and "embeddings" in response["output"]:
            # Qwen-specific format
            return response["output"]["embeddings"]
        else:
            raise ValueError(f"Unsupported Qwen embedding response format: {list(response.keys())}")


class _DeepSeekEmbeddingAdapter(EmbeddingAdapter):
    """Adapter for DeepSeek embedding API."""

    def build_endpoint(self, base_url: str) -> str:
        base_url = base_url.rstrip("/")
        return f"{base_url}/embeddings"

    def build_payload(self, texts: list[str], model: str) -> dict:
        return {
            "model": model,
            "input": texts if len(texts) > 1 else texts[0],
        }

    def build_headers(self, provider: LLMProvider) -> dict:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Authorization": f"Bearer {provider.api_key.get_secret_value()}",
        }
        if provider.custom_headers:
            headers.update(provider.custom_headers)
        return headers

    def parse_response(self, response: dict) -> list[list[float]]:
        if "data" not in response:
            raise ValueError(f"Invalid DeepSeek embedding response format: {list(response.keys())}")

        embeddings = []
        for item in response["data"]:
            if "embedding" not in item:
                raise ValueError("Invalid embedding response format: missing 'embedding' field")
            embeddings.append(item["embedding"])
        return embeddings


# ============================================================================
# Adapter Registry
# ============================================================================


_EMBEDDING_ADAPTERS: dict[str, type[EmbeddingAdapter]] = {}
"""Registry mapping provider types to their adapter classes."""


def _register_adapter(provider_type: str, adapter_class: type[EmbeddingAdapter]) -> None:
    """Register an adapter for a provider type.

    Args:
        provider_type: Provider type identifier
        adapter_class: Adapter class to register
    """
    _EMBEDDING_ADAPTERS[provider_type] = adapter_class


def _get_adapter(provider_type: str) -> EmbeddingAdapter:
    """Get adapter instance for provider type.

    Args:
        provider_type: Provider type identifier

    Returns:
        Adapter instance

    Raises:
        ValueError: If provider type is not supported
    """
    adapter_class = _EMBEDDING_ADAPTERS.get(provider_type)
    if adapter_class is None:
        raise ValueError(f"Unsupported provider type for embeddings: {provider_type}")
    return adapter_class()


# Register all adapters
_register_adapter("openai", _OpenAIEmbeddingAdapter)
_register_adapter("openai_compatible", _OpenAICompatibleEmbeddingAdapter)
_register_adapter("openai_legacy", _OpenAICompatibleEmbeddingAdapter)
_register_adapter("openai_responses", _OpenAICompatibleEmbeddingAdapter)
_register_adapter("qwen", _QwenEmbeddingAdapter)
_register_adapter("deepseek", _DeepSeekEmbeddingAdapter)


# ============================================================================
# Embedding Service
# ============================================================================


class EmbeddingService:
    """Service for generating text embeddings using various providers."""

    def __init__(
        self,
        provider: LLMProvider,
        model: LLMModel,
    ):
        """Initialize embedding service.

        Args:
            provider: LLM provider configuration
            model: LLM model configuration

        Raises:
            ValueError: If provider type is not supported
        """
        self._provider = provider
        self._model = model
        self._adapter = _get_adapter(provider.type)

    @classmethod
    def from_config(cls, config: Config) -> Optional[EmbeddingService]:
        """Create EmbeddingService from config.

        Args:
            config: Application configuration

        Returns:
            EmbeddingService instance if configured, None otherwise
        """
        if not config.default_embedding_model:
            return None

        if config.default_embedding_model not in config.embedding_models:
            logger.warning(
                "Default embedding model {model} not found in embedding_models",
                model=config.default_embedding_model,
            )
            return None

        embedding_model = config.embedding_models[config.default_embedding_model]

        if embedding_model.provider not in config.embedding_providers:
            logger.warning(
                "Embedding provider {provider} not found",
                provider=embedding_model.provider,
            )
            return None

        embedding_provider = config.embedding_providers[embedding_model.provider]

        return cls(embedding_provider, embedding_model)

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            List of float values representing the embedding vector

        Raises:
            ValueError: If embedding generation fails
        """
        embeddings = await self.generate_embeddings_batch([text])
        return embeddings[0]

    async def generate_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors (each is a list of floats)

        Raises:
            ValueError: If embedding generation fails
        """
        if not texts:
            return []

        # Use adapter to build request components
        endpoint = self._adapter.build_endpoint(self._provider.base_url)
        payload = self._adapter.build_payload(texts, self._model.model)
        headers = self._adapter.build_headers(self._provider)

        logger.debug(
            "Generating embeddings: provider={provider}, model={model}, texts={count}",
            provider=self._provider.type,
            model=self._model.model,
            count=len(texts),
        )

        try:
            async with (
                new_client_session() as session,
                session.post(
                    endpoint,
                    json=payload,
                    headers=headers,
                    raise_for_status=True,
                ) as response,
            ):
                result = await response.json()

            # Use adapter to parse response
            return self._adapter.parse_response(result)

        except aiohttp.ClientError as e:
            logger.error("Failed to generate embeddings: {error}", error=e)
            raise ValueError(f"Embedding API request failed: {e}") from e
        except json.JSONDecodeError as e:
            logger.error("Failed to parse embedding response: {error}", error=e)
            raise ValueError(f"Invalid embedding API response: {e}") from e
        except ValueError as e:
            # Re-raise ValueError from adapter parsing
            raise
        except Exception as e:
            logger.error("Unexpected error generating embeddings: {error}", error=e)
            raise ValueError(f"Unexpected error: {e}") from e
