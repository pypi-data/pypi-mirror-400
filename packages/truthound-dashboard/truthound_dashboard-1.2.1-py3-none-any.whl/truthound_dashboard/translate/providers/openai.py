"""OpenAI provider for translation.

This module implements the OpenAI translation provider using
GPT-4 and GPT-3.5 models.
"""

from __future__ import annotations

import asyncio

import httpx

from truthound_dashboard.translate.exceptions import TranslationAPIError
from truthound_dashboard.translate.providers.base import (
    AIProvider,
    ProviderConfig,
    TranslationRequest,
    TranslationResponse,
)


class OpenAIProvider(AIProvider):
    """OpenAI translation provider.

    Uses OpenAI's GPT models for translation.

    Environment:
        OPENAI_API_KEY: API key for authentication

    Example:
        provider = OpenAIProvider()
        response = await provider.translate(
            TranslationRequest(text="Hello", source_lang="en", target_lang="ja")
        )
    """

    name = "openai"
    display_name = "OpenAI"
    env_var = "OPENAI_API_KEY"
    default_model = "gpt-4o-mini"
    supported_models = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ]

    DEFAULT_BASE_URL = "https://api.openai.com/v1"

    def __init__(self, config: ProviderConfig | None = None) -> None:
        super().__init__(config)
        self.base_url = self.config.base_url or self.DEFAULT_BASE_URL

    async def translate(
        self,
        request: TranslationRequest,
        max_retries: int = 5,
        base_delay: float = 25.0,
    ) -> TranslationResponse:
        """Translate text using OpenAI API.

        Args:
            request: Translation request
            max_retries: Maximum number of retries for rate limit errors
            base_delay: Base delay in seconds for rate limit retries

        Returns:
            Translation response with translated text

        Raises:
            TranslationAPIError: If API call fails
        """
        prompt = self.get_translation_prompt(request)
        last_error = None

        for attempt in range(max_retries + 1):
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                try:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.config.api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": self.model,
                            "messages": [
                                {
                                    "role": "system",
                                    "content": (
                                        "You are a professional translator. "
                                        "Translate the given text accurately and naturally. "
                                        "Only output the translated text, nothing else."
                                    ),
                                },
                                {"role": "user", "content": prompt},
                            ],
                            "temperature": 0.3,
                            "max_tokens": 4096,
                        },
                    )

                    # Handle rate limit with retry
                    if response.status_code == 429:
                        if attempt < max_retries:
                            # Exponential backoff with jitter
                            delay = base_delay * (1.5**attempt)
                            await asyncio.sleep(delay)
                            continue
                        else:
                            raise TranslationAPIError(
                                provider_name=self.name,
                                message=f"Rate limit exceeded after {max_retries} retries",
                                status_code=response.status_code,
                                response_body=response.text,
                            )

                    if response.status_code != 200:
                        raise TranslationAPIError(
                            provider_name=self.name,
                            message=f"API request failed: {response.text}",
                            status_code=response.status_code,
                            response_body=response.text,
                        )

                    data = response.json()
                    translated_text = data["choices"][0]["message"]["content"].strip()

                    usage = None
                    if "usage" in data:
                        usage = {
                            "prompt_tokens": data["usage"].get("prompt_tokens", 0),
                            "completion_tokens": data["usage"].get("completion_tokens", 0),
                            "total_tokens": data["usage"].get("total_tokens", 0),
                        }

                    return TranslationResponse(
                        translated_text=translated_text,
                        source_lang=request.source_lang,
                        target_lang=request.target_lang,
                        model=self.model,
                        provider=self.name,
                        usage=usage,
                    )

                except httpx.TimeoutException as e:
                    last_error = TranslationAPIError(
                        provider_name=self.name,
                        message=f"Request timed out after {self.config.timeout}s",
                    )
                    if attempt < max_retries:
                        await asyncio.sleep(base_delay)
                        continue
                    raise last_error from e
                except httpx.RequestError as e:
                    raise TranslationAPIError(
                        provider_name=self.name,
                        message=f"Request failed: {e}",
                    ) from e

        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise TranslationAPIError(
            provider_name=self.name,
            message="Translation failed after all retries",
        )

    async def is_available(self) -> bool:
        """Check if OpenAI API is available.

        Returns:
            True if API key is set and valid
        """
        if not self.config.api_key:
            return False

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.config.api_key}"},
                )
                return response.status_code == 200
        except Exception:
            return False
