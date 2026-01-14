"""Intlayer configuration updater.

This module handles updating intlayer.config.ts and related frontend
configuration files when new languages are added.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from truthound_dashboard.translate.exceptions import ConfigUpdateError


@dataclass
class LocaleMapping:
    """Mapping between language codes and Intlayer locale constants."""

    code: str  # ISO 639-1 code (e.g., 'ja', 'zh')
    intlayer_const: str  # Intlayer constant (e.g., 'JAPANESE', 'CHINESE')
    name: str  # English name
    native_name: str  # Native name
    flag: str  # Flag emoji

    @classmethod
    def from_code(cls, code: str) -> "LocaleMapping":
        """Create a LocaleMapping from a language code.

        Args:
            code: ISO 639-1 language code

        Returns:
            LocaleMapping instance

        Raises:
            ValueError: If language code is not supported
        """
        code = code.lower()
        if code not in LOCALE_MAPPINGS:
            supported = ", ".join(sorted(LOCALE_MAPPINGS.keys()))
            raise ValueError(
                f"Unsupported language code: '{code}'. "
                f"Supported codes: {supported}"
            )
        return LOCALE_MAPPINGS[code]


# Mapping of ISO 639-1 codes to Intlayer locale info
LOCALE_MAPPINGS: dict[str, LocaleMapping] = {
    "en": LocaleMapping("en", "ENGLISH", "English", "English", "🇺🇸"),
    "ko": LocaleMapping("ko", "KOREAN", "Korean", "한국어", "🇰🇷"),
    "ja": LocaleMapping("ja", "JAPANESE", "Japanese", "日本語", "🇯🇵"),
    "zh": LocaleMapping("zh", "CHINESE", "Chinese", "中文", "🇨🇳"),
    "de": LocaleMapping("de", "GERMAN", "German", "Deutsch", "🇩🇪"),
    "fr": LocaleMapping("fr", "FRENCH", "French", "Français", "🇫🇷"),
    "es": LocaleMapping("es", "SPANISH", "Spanish", "Español", "🇪🇸"),
    "pt": LocaleMapping("pt", "PORTUGUESE", "Portuguese", "Português", "🇵🇹"),
    "it": LocaleMapping("it", "ITALIAN", "Italian", "Italiano", "🇮🇹"),
    "ru": LocaleMapping("ru", "RUSSIAN", "Russian", "Русский", "🇷🇺"),
    "ar": LocaleMapping("ar", "ARABIC", "Arabic", "العربية", "🇸🇦"),
    "hi": LocaleMapping("hi", "HINDI", "Hindi", "हिन्दी", "🇮🇳"),
    "th": LocaleMapping("th", "THAI", "Thai", "ไทย", "🇹🇭"),
    "vi": LocaleMapping("vi", "VIETNAMESE", "Vietnamese", "Tiếng Việt", "🇻🇳"),
    "nl": LocaleMapping("nl", "DUTCH", "Dutch", "Nederlands", "🇳🇱"),
    "pl": LocaleMapping("pl", "POLISH", "Polish", "Polski", "🇵🇱"),
    "tr": LocaleMapping("tr", "TURKISH", "Turkish", "Türkçe", "🇹🇷"),
    "sv": LocaleMapping("sv", "SWEDISH", "Swedish", "Svenska", "🇸🇪"),
    "da": LocaleMapping("da", "DANISH", "Danish", "Dansk", "🇩🇰"),
    "no": LocaleMapping("no", "NORWEGIAN", "Norwegian", "Norsk", "🇳🇴"),
    "fi": LocaleMapping("fi", "FINNISH", "Finnish", "Suomi", "🇫🇮"),
    "cs": LocaleMapping("cs", "CZECH", "Czech", "Čeština", "🇨🇿"),
    "hu": LocaleMapping("hu", "HUNGARIAN", "Hungarian", "Magyar", "🇭🇺"),
    "el": LocaleMapping("el", "GREEK", "Greek", "Ελληνικά", "🇬🇷"),
    "he": LocaleMapping("he", "HEBREW", "Hebrew", "עברית", "🇮🇱"),
    "id": LocaleMapping("id", "INDONESIAN", "Indonesian", "Bahasa Indonesia", "🇮🇩"),
    "ms": LocaleMapping("ms", "MALAY", "Malay", "Bahasa Melayu", "🇲🇾"),
    "uk": LocaleMapping("uk", "UKRAINIAN", "Ukrainian", "Українська", "🇺🇦"),
    "ro": LocaleMapping("ro", "ROMANIAN", "Romanian", "Română", "🇷🇴"),
    "bg": LocaleMapping("bg", "BULGARIAN", "Bulgarian", "Български", "🇧🇬"),
    "hr": LocaleMapping("hr", "CROATIAN", "Croatian", "Hrvatski", "🇭🇷"),
    "sk": LocaleMapping("sk", "SLOVAK", "Slovak", "Slovenčina", "🇸🇰"),
    "sl": LocaleMapping("sl", "SLOVENIAN", "Slovenian", "Slovenščina", "🇸🇮"),
    "et": LocaleMapping("et", "ESTONIAN", "Estonian", "Eesti", "🇪🇪"),
    "lv": LocaleMapping("lv", "LATVIAN", "Latvian", "Latviešu", "🇱🇻"),
    "lt": LocaleMapping("lt", "LITHUANIAN", "Lithuanian", "Lietuvių", "🇱🇹"),
}


class IntlayerConfigUpdater:
    """Updates Intlayer configuration files with new languages.

    This class handles:
    1. intlayer.config.ts - Add new locales to the locales array
    2. providers/intlayer/config.ts - Add locale info for UI

    Example:
        updater = IntlayerConfigUpdater(frontend_dir)
        updater.add_languages(["ja", "zh", "de"])
    """

    def __init__(self, frontend_dir: Path | str) -> None:
        """Initialize the config updater.

        Args:
            frontend_dir: Path to the frontend directory
        """
        self.frontend_dir = Path(frontend_dir)
        self.intlayer_config = self.frontend_dir / "intlayer.config.ts"
        self.provider_config = (
            self.frontend_dir / "src" / "providers" / "intlayer" / "config.ts"
        )

    def get_current_locales(self) -> list[str]:
        """Get currently configured locales from intlayer.config.ts.

        Returns:
            List of language codes currently configured
        """
        if not self.intlayer_config.exists():
            return []

        content = self.intlayer_config.read_text()

        # Parse locales array: [Locales.ENGLISH, Locales.KOREAN]
        pattern = r"locales:\s*\[([\s\S]*?)\]"
        match = re.search(pattern, content)
        if not match:
            return []

        locales_str = match.group(1)
        locales = []

        for const_name in re.findall(r"Locales\.(\w+)", locales_str):
            for code, mapping in LOCALE_MAPPINGS.items():
                if mapping.intlayer_const == const_name:
                    locales.append(code)
                    break

        return locales

    def add_languages(self, language_codes: list[str]) -> list[str]:
        """Add new languages to the configuration.

        Args:
            language_codes: List of ISO 639-1 language codes to add

        Returns:
            List of actually added language codes (excluding already existing)

        Raises:
            ConfigUpdateError: If configuration update fails
        """
        # Validate all language codes first
        mappings = []
        for code in language_codes:
            try:
                mappings.append(LocaleMapping.from_code(code))
            except ValueError as e:
                raise ConfigUpdateError(str(self.intlayer_config), str(e)) from e

        # Get current locales
        current_locales = self.get_current_locales()
        new_codes = [m.code for m in mappings if m.code not in current_locales]

        if not new_codes:
            return []

        # Update intlayer.config.ts
        self._update_intlayer_config(mappings)

        # Update provider config.ts
        self._update_provider_config(mappings)

        return new_codes

    def _update_intlayer_config(self, mappings: list[LocaleMapping]) -> None:
        """Update intlayer.config.ts with new locales.

        Args:
            mappings: List of LocaleMapping objects to add
        """
        if not self.intlayer_config.exists():
            raise ConfigUpdateError(
                str(self.intlayer_config),
                "File does not exist",
            )

        content = self.intlayer_config.read_text()
        current_locales = self.get_current_locales()

        # Build new locales array
        all_locales = current_locales.copy()
        for mapping in mappings:
            if mapping.code not in all_locales:
                all_locales.append(mapping.code)

        # Generate locales string
        locales_entries = []
        for code in all_locales:
            mapping = LOCALE_MAPPINGS[code]
            locales_entries.append(f"Locales.{mapping.intlayer_const}")

        new_locales_str = ", ".join(locales_entries)

        # Replace locales array
        pattern = r"(locales:\s*\[)[\s\S]*?(\])"
        replacement = f"\\g<1>{new_locales_str}\\g<2>"
        new_content = re.sub(pattern, replacement, content)

        self.intlayer_config.write_text(new_content)

    def _update_provider_config(self, mappings: list[LocaleMapping]) -> None:
        """Update providers/intlayer/config.ts with new locale info.

        Args:
            mappings: List of LocaleMapping objects to add
        """
        if not self.provider_config.exists():
            raise ConfigUpdateError(
                str(self.provider_config),
                "File does not exist",
            )

        content = self.provider_config.read_text()
        current_locales = self.get_current_locales()

        # Update SUPPORTED_LOCALES array
        all_locales = current_locales.copy()
        for mapping in mappings:
            if mapping.code not in all_locales:
                all_locales.append(mapping.code)

        # Generate SUPPORTED_LOCALES entries
        locales_entries = []
        for code in all_locales:
            mapping = LOCALE_MAPPINGS[code]
            locales_entries.append(f"Locales.{mapping.intlayer_const}")

        new_supported_str = ", ".join(locales_entries)

        # Replace SUPPORTED_LOCALES
        pattern = r"(export const SUPPORTED_LOCALES = \[)[\s\S]*?(\] as const)"
        replacement = f"\\g<1>{new_supported_str}\\g<2>"
        new_content = re.sub(pattern, replacement, content)

        # Update LOCALE_INFO array
        locale_info_entries = []
        for code in all_locales:
            mapping = LOCALE_MAPPINGS[code]
            entry = (
                f"  {{\n"
                f"    code: Locales.{mapping.intlayer_const},\n"
                f"    name: '{mapping.name}',\n"
                f"    nativeName: '{mapping.native_name}',\n"
                f"    flag: '{mapping.flag}',\n"
                f"  }}"
            )
            locale_info_entries.append(entry)

        new_locale_info_str = ",\n".join(locale_info_entries)

        # Replace LOCALE_INFO array
        pattern = r"(export const LOCALE_INFO: readonly LocaleInfo\[\] = \[)\n[\s\S]*?(\n\] as const)"
        replacement = f"\\g<1>\n{new_locale_info_str},\\g<2>"
        new_content = re.sub(pattern, replacement, new_content)

        # Update getBrowserLocale function
        self._update_browser_locale_function(new_content, all_locales)

        self.provider_config.write_text(new_content)

    def _update_browser_locale_function(
        self,
        content: str,
        all_locales: list[str],
    ) -> str:
        """Update getBrowserLocale function with new language mappings.

        This is a simplified approach - for complex cases, consider
        using a proper AST parser.

        Args:
            content: Current file content
            all_locales: List of all locale codes

        Returns:
            Updated content
        """
        # For now, we keep the basic structure and just ensure
        # the function exists. Full implementation would require
        # AST manipulation for clean results.
        return content

    def validate_config(self) -> bool:
        """Validate that configuration files exist and are valid.

        Returns:
            True if all configurations are valid
        """
        if not self.intlayer_config.exists():
            return False
        if not self.provider_config.exists():
            return False

        try:
            self.get_current_locales()
            return True
        except Exception:
            return False


def get_supported_languages() -> list[dict[str, str]]:
    """Get list of all supported languages for translation.

    Returns:
        List of dicts with language info
    """
    return [
        {
            "code": mapping.code,
            "name": mapping.name,
            "native_name": mapping.native_name,
            "flag": mapping.flag,
        }
        for mapping in LOCALE_MAPPINGS.values()
    ]
