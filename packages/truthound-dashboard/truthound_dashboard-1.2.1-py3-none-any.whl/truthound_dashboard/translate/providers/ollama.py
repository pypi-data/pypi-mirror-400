"""Ollama provider for translation.

This module implements the Ollama translation provider for local LLM
translation without requiring API keys.
"""

from __future__ import annotations

import httpx

from truthound_dashboard.translate.exceptions import (
    OllamaNotRunningError,
    TranslationAPIError,
)
from truthound_dashboard.translate.providers.base import (
    AIProvider,
    ProviderConfig,
    TranslationRequest,
    TranslationResponse,
)


class OllamaProvider(AIProvider):
    """Ollama translation provider for local LLM.

    Uses locally running Ollama models for translation.
    No API key required.

    Requirements:
        - Ollama installed and running (ollama serve)
        - A model pulled (e.g., ollama pull llama2)

    Example:
        provider = OllamaProvider()
        response = await provider.translate(
            TranslationRequest(text="Hello", source_lang="en", target_lang="ja")
        )
    """

    name = "ollama"
    display_name = "Ollama (Local)"
    env_var = None  # No API key needed
    default_model = "llama3.2"
    supported_models = [
        "llama3.2",
        "llama3.1",
        "llama2",
        "mistral",
        "mixtral",
        "qwen2.5",
        "gemma2",
        "phi3",
    ]

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, config: ProviderConfig | None = None) -> None:
        if config is None:
            config = ProviderConfig(model=self.default_model)
        super().__init__(config)
        self.base_url = self.config.base_url or self.DEFAULT_BASE_URL

    @property
    def requires_api_key(self) -> bool:
        """Ollama doesn't require an API key."""
        return False

    async def translate(self, request: TranslationRequest) -> TranslationResponse:
        """Translate text using Ollama API.

        Args:
            request: Translation request

        Returns:
            Translation response with translated text

        Raises:
            OllamaNotRunningError: If Ollama is not running
            TranslationAPIError: If API call fails
        """
        # First check if Ollama is running
        if not await self.is_available():
            raise OllamaNotRunningError()

        prompt = self.get_translation_prompt(request)

        async with httpx.AsyncClient(timeout=self.config.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 4096,
                        },
                    },
                )

                if response.status_code == 404:
                    raise TranslationAPIError(
                        provider_name=self.name,
                        message=(
                            f"Model '{self.model}' not found. "
                            f"Please pull it first: ollama pull {self.model}"
                        ),
                        status_code=404,
                    )

                if response.status_code != 200:
                    raise TranslationAPIError(
                        provider_name=self.name,
                        message=f"API request failed: {response.text}",
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                data = response.json()
                translated_text = data.get("response", "").strip()

                # Clean up common artifacts from local models
                translated_text = self._clean_response(translated_text)

                return TranslationResponse(
                    translated_text=translated_text,
                    source_lang=request.source_lang,
                    target_lang=request.target_lang,
                    model=self.model,
                    provider=self.name,
                    usage=None,  # Ollama doesn't provide token usage
                )

            except httpx.ConnectError as e:
                raise OllamaNotRunningError() from e
            except httpx.TimeoutException as e:
                raise TranslationAPIError(
                    provider_name=self.name,
                    message=f"Request timed out after {self.config.timeout}s",
                ) from e
            except httpx.RequestError as e:
                raise TranslationAPIError(
                    provider_name=self.name,
                    message=f"Request failed: {e}",
                ) from e

    def _clean_response(self, text: str) -> str:
        """Clean up common artifacts from local model responses.

        Args:
            text: Raw response text

        Returns:
            Cleaned text
        """
        # Remove common prefixes that models might add
        prefixes_to_remove = [
            "Here is the translation:",
            "Translation:",
            "Translated text:",
            "Here's the translation:",
        ]
        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()

        # Remove quotes if the entire response is quoted
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]

        return text.strip()

    async def is_available(self) -> bool:
        """Check if Ollama is running locally.

        Returns:
            True if Ollama server is responding
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """List available models in Ollama.

        Returns:
            List of model names
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
        except Exception:
            pass
        return []

    def get_translation_prompt(self, request: TranslationRequest) -> str:
        """Generate a prompt optimized for local models.

        Local models sometimes need more explicit instructions.

        Args:
            request: Translation request

        Returns:
            Formatted prompt string
        """
        context_part = ""
        if request.context:
            context_part = f"\nContext: {request.context}"

        return f"""You are a professional translator. Translate the following text from {request.source_lang} to {request.target_lang}.

IMPORTANT: Only output the translated text. Do not include any explanations, notes, or the original text.{context_part}

Text: {request.text}

Translation:"""
