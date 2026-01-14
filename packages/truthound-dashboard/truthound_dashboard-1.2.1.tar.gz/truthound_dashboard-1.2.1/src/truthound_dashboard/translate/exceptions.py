"""Custom exceptions for the translation module."""

from __future__ import annotations


class TranslationError(Exception):
    """Base exception for translation-related errors."""

    pass


class ProviderNotFoundError(TranslationError):
    """Raised when a requested AI provider is not found or not supported."""

    def __init__(self, provider_name: str, available: list[str] | None = None) -> None:
        self.provider_name = provider_name
        self.available = available or []
        message = f"Provider '{provider_name}' not found."
        if self.available:
            message += f" Available providers: {', '.join(self.available)}"
        super().__init__(message)


class APIKeyNotFoundError(TranslationError):
    """Raised when required API key is not set in environment."""

    def __init__(self, provider_name: str, env_var: str) -> None:
        self.provider_name = provider_name
        self.env_var = env_var
        message = (
            f"API key not found for provider '{provider_name}'. "
            f"Please set the {env_var} environment variable."
        )
        super().__init__(message)


class TranslationAPIError(TranslationError):
    """Raised when AI provider API call fails."""

    def __init__(
        self,
        provider_name: str,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        self.provider_name = provider_name
        self.status_code = status_code
        self.response_body = response_body
        full_message = f"API error from '{provider_name}': {message}"
        if status_code:
            full_message += f" (status: {status_code})"
        super().__init__(full_message)


class ContentParseError(TranslationError):
    """Raised when content file parsing fails."""

    def __init__(self, file_path: str, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        message = f"Failed to parse content file '{file_path}': {reason}"
        super().__init__(message)


class ConfigUpdateError(TranslationError):
    """Raised when intlayer config update fails."""

    def __init__(self, config_path: str, reason: str) -> None:
        self.config_path = config_path
        self.reason = reason
        message = f"Failed to update config '{config_path}': {reason}"
        super().__init__(message)


class NodejsNotFoundError(TranslationError):
    """Raised when Node.js is not installed or version is too old."""

    def __init__(self, required_version: str = "18.0.0") -> None:
        self.required_version = required_version
        message = (
            f"Node.js {required_version}+ is required for translation. "
            "Please install from https://nodejs.org/"
        )
        super().__init__(message)


class OllamaNotRunningError(TranslationError):
    """Raised when Ollama is not running for local LLM translation."""

    def __init__(self) -> None:
        message = (
            "Ollama is not running. Please start Ollama first:\n"
            "  1. Install: https://ollama.ai/download\n"
            "  2. Start: ollama serve\n"
            "  3. Pull a model: ollama pull llama2"
        )
        super().__init__(message)
