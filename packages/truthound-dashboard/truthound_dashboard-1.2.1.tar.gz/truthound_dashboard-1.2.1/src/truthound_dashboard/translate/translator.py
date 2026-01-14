"""Content file translator for Intlayer.

This module handles parsing and translating Intlayer content files
(*.content.ts) using AI providers.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from truthound_dashboard.translate.config_updater import LOCALE_MAPPINGS
from truthound_dashboard.translate.exceptions import ContentParseError
from truthound_dashboard.translate.providers.base import (
    AIProvider,
    TranslationRequest,
)


@dataclass
class TranslationEntry:
    """A single translation entry from a content file.

    Attributes:
        key_path: Dot-separated path to this entry (e.g., "common.save")
        source_text: The source text to translate (typically English)
        source_lang: Source language code
        translations: Dict of language code to translated text
        line_number: Line number in the source file
    """

    key_path: str
    source_text: str
    source_lang: str
    translations: dict[str, str] = field(default_factory=dict)
    line_number: int = 0


@dataclass
class TranslationResult:
    """Result of a translation operation.

    Attributes:
        file_path: Path to the translated file
        entries_translated: Number of entries translated
        entries_skipped: Number of entries skipped (already translated)
        errors: List of errors encountered
        languages_added: List of new language codes added
    """

    file_path: str
    entries_translated: int = 0
    entries_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    languages_added: list[str] = field(default_factory=list)


class ContentFileParser:
    """Parser for Intlayer content files.

    Parses *.content.ts files to extract translation entries.
    """

    # Pattern to match t({ en: "...", ko: "..." })
    T_FUNCTION_PATTERN = re.compile(
        r't\(\s*\{\s*([\s\S]*?)\}\s*\)',
        re.MULTILINE,
    )

    # Pattern to match language entries: en: "text" or en: 'text'
    LANG_ENTRY_PATTERN = re.compile(
        r"(\w+):\s*['\"](.+?)['\"]",
        re.MULTILINE,
    )

    def __init__(self, file_path: Path | str) -> None:
        """Initialize the parser.

        Args:
            file_path: Path to the content file
        """
        self.file_path = Path(file_path)
        self.content = ""
        self._entries: list[TranslationEntry] = []

    def parse(self) -> list[TranslationEntry]:
        """Parse the content file and extract translation entries.

        Returns:
            List of TranslationEntry objects

        Raises:
            ContentParseError: If parsing fails
        """
        if not self.file_path.exists():
            raise ContentParseError(str(self.file_path), "File does not exist")

        try:
            self.content = self.file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ContentParseError(str(self.file_path), f"Failed to read: {e}") from e

        self._entries = []
        self._parse_t_functions()

        return self._entries

    def _parse_t_functions(self) -> None:
        """Parse all t() function calls in the content."""
        # Find all t() function calls
        for match in self.T_FUNCTION_PATTERN.finditer(self.content):
            inner_content = match.group(1)
            line_number = self.content[: match.start()].count("\n") + 1

            # Extract language entries
            translations: dict[str, str] = {}
            for lang_match in self.LANG_ENTRY_PATTERN.finditer(inner_content):
                lang_code = lang_match.group(1)
                text = lang_match.group(2)
                translations[lang_code] = text

            if not translations:
                continue

            # Use English as source if available, otherwise first entry
            source_lang = "en" if "en" in translations else list(translations.keys())[0]
            source_text = translations[source_lang]

            entry = TranslationEntry(
                key_path=self._find_key_path(match.start()),
                source_text=source_text,
                source_lang=source_lang,
                translations=translations,
                line_number=line_number,
            )
            self._entries.append(entry)

    def _find_key_path(self, position: int) -> str:
        """Find the key path for a translation entry.

        This is a simplified implementation that looks for the
        nearest property name before the position.

        Args:
            position: Character position in the file

        Returns:
            Key path string
        """
        # Look backwards for property assignment
        before_content = self.content[:position]
        lines = before_content.split("\n")

        # Find the nearest property name
        for line in reversed(lines):
            line = line.strip()
            # Match patterns like "save:" or "title:"
            prop_match = re.match(r"(\w+):\s*$", line)
            if prop_match:
                return prop_match.group(1)

        return "unknown"


class ContentFileWriter:
    """Writer for updating Intlayer content files with translations."""

    def __init__(self, file_path: Path | str) -> None:
        """Initialize the writer.

        Args:
            file_path: Path to the content file
        """
        self.file_path = Path(file_path)

    def add_translations(
        self,
        entries: list[TranslationEntry],
        target_langs: list[str],
    ) -> None:
        """Add translations to the content file.

        Args:
            entries: List of TranslationEntry objects with translations
            target_langs: List of target language codes that were added

        Raises:
            ContentParseError: If file update fails
        """
        if not self.file_path.exists():
            raise ContentParseError(str(self.file_path), "File does not exist")

        content = self.file_path.read_text(encoding="utf-8")

        # Process each entry
        for entry in entries:
            # Find the t() call for this entry and add new translations
            content = self._update_t_function(content, entry, target_langs)

        self.file_path.write_text(content, encoding="utf-8")

    def _update_t_function(
        self,
        content: str,
        entry: TranslationEntry,
        target_langs: list[str],
    ) -> str:
        """Update a single t() function call with new translations.

        Args:
            content: Current file content
            entry: Translation entry with new translations
            target_langs: List of target language codes

        Returns:
            Updated content
        """
        # Pattern to find t() containing the specific source text
        # Use [^}]* instead of [\s\S]*? to avoid matching across multiple t() calls
        escaped_text = re.escape(entry.source_text)
        pattern = re.compile(
            rf"(t\(\s*\{{\s*)([^}}]*?{entry.source_lang}:\s*['\"]"
            + escaped_text
            + rf"['\"][^}}]*)(\}}\s*\))",
            re.MULTILINE,
        )

        def replacer(match: re.Match[str]) -> str:
            prefix = match.group(1)
            inner = match.group(2)
            suffix = match.group(3)

            # Add new language entries
            for lang in target_langs:
                if lang not in entry.translations:
                    continue

                # Check if language already exists
                if re.search(rf"\b{lang}:\s*['\"]", inner):
                    continue

                translated_text = entry.translations[lang]
                # Escape quotes in translated text
                translated_text = translated_text.replace("'", "\\'")

                # Add new entry before the closing brace
                # Find proper indentation
                indent_match = re.search(r"\n(\s+)\w+:", inner)
                indent = indent_match.group(1) if indent_match else "    "

                new_entry = f"{indent}{lang}: '{translated_text}',"
                inner = inner.rstrip()
                if not inner.endswith(","):
                    inner += ","
                inner += f"\n{new_entry}\n  "

            return f"{prefix}{inner}{suffix}"

        return pattern.sub(replacer, content, count=1)


class ContentTranslator:
    """Main translator class for Intlayer content files.

    Coordinates parsing, translation, and writing of content files.

    Example:
        translator = ContentTranslator(provider, frontend_dir)
        results = await translator.translate_all(["ja", "zh", "de"])
    """

    def __init__(
        self,
        provider: AIProvider,
        frontend_dir: Path | str,
        source_lang: str = "en",
    ) -> None:
        """Initialize the translator.

        Args:
            provider: AI provider for translation
            frontend_dir: Path to frontend directory
            source_lang: Source language code (default: 'en')
        """
        self.provider = provider
        self.frontend_dir = Path(frontend_dir)
        self.source_lang = source_lang
        self.content_dir = self.frontend_dir / "src"

    def find_content_files(self) -> list[Path]:
        """Find all content files in the frontend directory.

        Returns:
            List of paths to *.content.ts files
        """
        return list(self.content_dir.glob("**/*.content.ts"))

    async def translate_file(
        self,
        file_path: Path,
        target_langs: list[str],
        batch_size: int = 10,
    ) -> TranslationResult:
        """Translate a single content file.

        Args:
            file_path: Path to the content file
            target_langs: List of target language codes
            batch_size: Number of entries to translate in parallel

        Returns:
            TranslationResult with statistics
        """
        result = TranslationResult(
            file_path=str(file_path),
            languages_added=target_langs.copy(),
        )

        try:
            # Parse the file
            parser = ContentFileParser(file_path)
            entries = parser.parse()

            if not entries:
                return result

            # Translate entries
            await self._translate_entries(entries, target_langs, batch_size, result)

            # Write translations back
            writer = ContentFileWriter(file_path)
            writer.add_translations(entries, target_langs)

        except ContentParseError as e:
            result.errors.append(str(e))
        except Exception as e:
            result.errors.append(f"Unexpected error: {e}")

        return result

    async def _translate_entries(
        self,
        entries: list[TranslationEntry],
        target_langs: list[str],
        batch_size: int,
        result: TranslationResult,
    ) -> None:
        """Translate all entries for target languages.

        Args:
            entries: List of translation entries
            target_langs: Target language codes
            batch_size: Batch size for parallel translation
            result: TranslationResult to update
        """
        for entry in entries:
            for target_lang in target_langs:
                # Skip if already translated
                if target_lang in entry.translations:
                    result.entries_skipped += 1
                    continue

                try:
                    # Create translation request
                    request = TranslationRequest(
                        text=entry.source_text,
                        source_lang=self.source_lang,
                        target_lang=target_lang,
                        context=f"UI text for a data quality dashboard. Key: {entry.key_path}",
                    )

                    # Translate
                    response = await self.provider.translate(request)
                    entry.translations[target_lang] = response.translated_text
                    result.entries_translated += 1

                except Exception as e:
                    result.errors.append(
                        f"Failed to translate '{entry.key_path}' to {target_lang}: {e}"
                    )

    async def translate_all(
        self,
        target_langs: list[str],
        batch_size: int = 10,
        on_progress: Any = None,
    ) -> list[TranslationResult]:
        """Translate all content files.

        Args:
            target_langs: List of target language codes
            batch_size: Batch size for parallel translation
            on_progress: Optional callback for progress updates

        Returns:
            List of TranslationResult for each file
        """
        # Validate target languages
        for lang in target_langs:
            if lang not in LOCALE_MAPPINGS:
                raise ValueError(
                    f"Unsupported language: '{lang}'. "
                    f"Supported: {', '.join(sorted(LOCALE_MAPPINGS.keys()))}"
                )

        content_files = self.find_content_files()
        results = []

        for i, file_path in enumerate(content_files):
            if on_progress:
                on_progress(i + 1, len(content_files), file_path.name)

            result = await self.translate_file(file_path, target_langs, batch_size)
            results.append(result)

        return results

    def get_translation_stats(
        self,
        results: list[TranslationResult],
    ) -> dict[str, Any]:
        """Calculate aggregate statistics from translation results.

        Args:
            results: List of TranslationResult objects

        Returns:
            Dict with aggregate statistics
        """
        total_translated = sum(r.entries_translated for r in results)
        total_skipped = sum(r.entries_skipped for r in results)
        total_errors = sum(len(r.errors) for r in results)

        return {
            "files_processed": len(results),
            "entries_translated": total_translated,
            "entries_skipped": total_skipped,
            "total_errors": total_errors,
            "all_errors": [e for r in results for e in r.errors],
        }
