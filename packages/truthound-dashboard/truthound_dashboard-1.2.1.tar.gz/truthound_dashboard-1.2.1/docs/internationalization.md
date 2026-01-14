# Internationalization (i18n)

Truthound Dashboard provides type-safe internationalization powered by [Intlayer](https://intlayer.org). This guide covers how to use the built-in translations, add new languages via AI translation, and contribute translations.

## Overview

| Feature | Description |
|---------|-------------|
| **Library** | Intlayer + react-intlayer |
| **Default Languages** | English (en), Korean (ko) |
| **Type Safety** | Full TypeScript support with auto-generated types |
| **AI Translation** | Translate to any language using OpenAI, Anthropic, Ollama, or Mistral |
| **Content Location** | Co-located with components (`*.content.ts`) |

---

## Built-in Languages

The dashboard includes translations for:

- **English** (`en`) - Default
- **Korean** (`ko`)

The language is automatically detected from your browser settings, or you can manually switch using the language selector in the header.

---

## Adding New Languages with AI Translation

You can add support for additional languages using the `truthound translate` CLI command. This leverages AI providers to translate all UI content.

### Prerequisites

1. **Node.js** (v18 or higher) must be installed
2. **API Key** for your chosen AI provider (except Ollama)

### Supported AI Providers

| Provider | API Key Environment Variable | Notes |
|----------|------------------------------|-------|
| OpenAI | `OPENAI_API_KEY` | GPT-4, GPT-3.5 |
| Anthropic | `ANTHROPIC_API_KEY` | Claude models |
| Mistral | `MISTRAL_API_KEY` | Mistral models |
| Ollama | Not required | Local LLM, no API key needed |

### Basic Usage

```bash
# Translate to French using OpenAI
export OPENAI_API_KEY=sk-your-api-key
truthound translate -l fr -p openai

# Translate to multiple languages
truthound translate -l fr,de,ja,zh -p openai

# Use Anthropic (Claude)
export ANTHROPIC_API_KEY=sk-ant-your-api-key
truthound translate -l fr -p anthropic

# Use local Ollama (no API key required)
truthound translate -l fr -p ollama

# Auto-detect provider from available API keys
truthound translate -l fr
```

### CLI Options

```bash
truthound translate [OPTIONS]

Options:
  -l, --languages TEXT    Target language codes (comma-separated)
                          Example: fr,de,ja,zh,es
  -p, --provider TEXT     AI provider: openai, anthropic, ollama, mistral
                          Default: auto-detect from environment
  --model TEXT            Specific model to use (optional)
                          Example: gpt-4, claude-3-opus
  --dry-run               Preview without making changes
  --list-providers        Show available AI providers
  --list-languages        Show supported language codes
  --help                  Show help message
```

### Example: Adding French (fr) Support

This example walks through adding French language support step by step.

#### Step 1: Set up API Key

```bash
# Using OpenAI
export OPENAI_API_KEY=sk-proj-xxxxx

# Or using Anthropic
export ANTHROPIC_API_KEY=sk-ant-xxxxx

# Or using local Ollama (no key needed)
ollama pull llama3
```

#### Step 2: Run Translation

```bash
truthound translate -l fr -p openai
```

**Expected Output:**
```
Translating to: fr
Provider: openai (gpt-4)

Translating content files...
  ✓ common.content.ts (45 keys)
  ✓ dashboard.content.ts (22 keys)
  ✓ sources.content.ts (38 keys)
  ✓ schedules.content.ts (31 keys)
  ✓ notifications.content.ts (28 keys)
  ✓ drift.content.ts (35 keys)
  ✓ validation.content.ts (24 keys)
  ✓ demo.content.ts (3 keys)
  ✓ nav.content.ts (11 keys)

Translation complete!
  Languages added: fr
  Total keys translated: 237

Rebuilding frontend...
  ✓ Build complete

French (fr) is now available in the dashboard.
```

#### Step 3: Verify Translation

Start the dashboard and switch to French:

```bash
truthound serve
```

Navigate to the language selector in the header and select "Français".

#### Step 4: Review Generated Content

After translation, your content files will include French:

```typescript
// frontend/src/content/common.content.ts
import { t, type Dictionary } from "intlayer";

const commonContent = {
  key: "common",
  content: {
    save: t({
      en: "Save",
      ko: "저장",
      fr: "Enregistrer",  // Added by AI translation
    }),
    cancel: t({
      en: "Cancel",
      ko: "취소",
      fr: "Annuler",  // Added by AI translation
    }),
    delete: t({
      en: "Delete",
      ko: "삭제",
      fr: "Supprimer",  // Added by AI translation
    }),
    // ... more translations
  },
} satisfies Dictionary;

export default commonContent;
```

### Dry Run Mode

Preview translations without modifying files:

```bash
truthound translate -l fr --dry-run
```

**Output:**
```
[DRY RUN] Would translate to: fr
Provider: openai (gpt-4)

Files that would be modified:
  - frontend/src/content/common.content.ts
  - frontend/src/content/dashboard.content.ts
  - frontend/src/content/sources.content.ts
  - frontend/src/content/schedules.content.ts
  - frontend/src/content/notifications.content.ts
  - frontend/src/content/drift.content.ts
  - frontend/src/content/validation.content.ts
  - frontend/src/components/demo.content.ts
  - frontend/src/content/nav.content.ts

Sample translations (common.content.ts):
  save: "Save" → "Enregistrer"
  cancel: "Cancel" → "Annuler"
  delete: "Delete" → "Supprimer"

No files were modified. Remove --dry-run to apply changes.
```

---

## Supported Language Codes

Use `truthound translate --list-languages` to see all supported codes:

| Code | Language | Native Name |
|------|----------|-------------|
| `en` | English | English |
| `ko` | Korean | 한국어 |
| `fr` | French | Français |
| `de` | German | Deutsch |
| `es` | Spanish | Español |
| `it` | Italian | Italiano |
| `pt` | Portuguese | Português |
| `ja` | Japanese | 日本語 |
| `zh` | Chinese (Simplified) | 简体中文 |
| `zh-TW` | Chinese (Traditional) | 繁體中文 |
| `ru` | Russian | Русский |
| `ar` | Arabic | العربية |
| `hi` | Hindi | हिन्दी |
| `th` | Thai | ไทย |
| `vi` | Vietnamese | Tiếng Việt |
| `nl` | Dutch | Nederlands |
| `pl` | Polish | Polski |
| `tr` | Turkish | Türkçe |
| `uk` | Ukrainian | Українська |
| `sv` | Swedish | Svenska |

---

## Content File Structure

Translation content is organized in TypeScript files alongside components:

```
frontend/src/
├── content/                    # Shared content
│   ├── common.content.ts       # Common UI text (Save, Cancel, etc.)
│   ├── nav.content.ts          # Navigation labels
│   ├── validation.content.ts   # Validation-related text
│   ├── settings.content.ts     # Settings page
│   └── errors.content.ts       # Error messages
├── pages/
│   ├── Dashboard.tsx
│   ├── dashboard.content.ts    # Dashboard-specific text
│   ├── Sources.tsx
│   ├── sources.content.ts      # Sources page text
│   ├── Schedules.tsx
│   ├── schedules.content.ts    # Schedules page text
│   ├── Notifications.tsx
│   ├── notifications.content.ts # Notifications page text
│   ├── Drift.tsx
│   └── drift.content.ts        # Drift detection text
└── components/
    ├── DemoBanner.tsx
    └── demo.content.ts         # Demo banner text
```

---

## Writing Content Files

### Basic Structure

```typescript
// my-component.content.ts
import { t, type Dictionary } from "intlayer";

const myContent = {
  key: "myComponent",  // Unique identifier
  content: {
    title: t({
      en: "My Title",
      ko: "내 제목",
      fr: "Mon Titre",
    }),
    description: t({
      en: "A description of this component",
      ko: "이 컴포넌트에 대한 설명",
      fr: "Une description de ce composant",
    }),
  },
} satisfies Dictionary;

export default myContent;
```

### Nested Content

```typescript
const sourcesContent = {
  key: "sources",
  content: {
    title: t({ en: "Data Sources", ko: "데이터 소스", fr: "Sources de données" }),

    // Nested object for source types
    types: {
      file: t({ en: "File", ko: "파일", fr: "Fichier" }),
      csv: t({ en: "CSV File", ko: "CSV 파일", fr: "Fichier CSV" }),
      database: t({ en: "Database", ko: "데이터베이스", fr: "Base de données" }),
      postgresql: t({ en: "PostgreSQL", ko: "PostgreSQL", fr: "PostgreSQL" }),
    },

    // Actions
    actions: {
      add: t({ en: "Add Source", ko: "소스 추가", fr: "Ajouter une source" }),
      edit: t({ en: "Edit Source", ko: "소스 편집", fr: "Modifier la source" }),
      delete: t({ en: "Delete Source", ko: "소스 삭제", fr: "Supprimer la source" }),
    },
  },
} satisfies Dictionary;
```

---

## Using Translations in Components

### Basic Usage

```typescript
import { useIntlayer } from "react-intlayer";

function Dashboard() {
  const dashboard = useIntlayer("dashboard");
  const common = useIntlayer("common");

  return (
    <div>
      <h1>{dashboard.title}</h1>
      <button>{common.save}</button>
    </div>
  );
}
```

### With Nested Content

```typescript
function SourceTypeSelector() {
  const { types } = useIntlayer("sources");

  return (
    <select>
      <option value="csv">{types.csv}</option>
      <option value="postgresql">{types.postgresql}</option>
    </select>
  );
}
```

### String Conversion for Non-JSX Contexts

`useIntlayer()` returns `IntlayerNode` objects that work directly in JSX. For contexts requiring plain strings (toast notifications, aria-labels, etc.), use the `str()` helper:

```typescript
import { useIntlayer } from "react-intlayer";
import { str } from "@/lib/intlayer-utils";
import { toast } from "@/hooks/use-toast";

function SourceActions() {
  const common = useIntlayer("common");
  const sources = useIntlayer("sources");

  const handleDelete = () => {
    // Use str() for toast messages
    toast({
      title: str(common.success),
      description: str(sources.deleteSuccess),
    });
  };

  return (
    <button
      onClick={handleDelete}
      aria-label={str(sources.actions.delete)}  // Use str() for aria-label
    >
      {sources.actions.delete}  {/* Direct use in JSX is fine */}
    </button>
  );
}
```

---

## Language Switching

### Programmatic Language Change

```typescript
import { useLocale } from "react-intlayer";

function LanguageSelector() {
  const { locale, setLocale } = useLocale();

  return (
    <select
      value={locale}
      onChange={(e) => setLocale(e.target.value)}
    >
      <option value="en">English</option>
      <option value="ko">한국어</option>
      <option value="fr">Français</option>
    </select>
  );
}
```

### Getting Current Locale

```typescript
import { useLocale } from "react-intlayer";

function LocaleInfo() {
  const { locale } = useLocale();

  return <span>Current: {locale}</span>;
}
```

---

## Configuration

### Intlayer Configuration

Located at `frontend/intlayer.config.ts`:

```typescript
import { Locales, type IntlayerConfig } from "intlayer";

const config: IntlayerConfig = {
  internationalization: {
    locales: [
      Locales.ENGLISH,
      Locales.KOREAN,
      // Add new locales here after translation
      // Locales.FRENCH,
      // Locales.GERMAN,
    ],
    defaultLocale: Locales.ENGLISH,
  },
  content: {
    fileExtensions: [".content.ts", ".content.tsx"],
    contentDir: ["./src"],
  },
  middleware: {
    cookieName: "truthound-locale",
  },
};

export default config;
```

### Adding a New Locale Manually

After running AI translation, update the config:

```typescript
// frontend/intlayer.config.ts
import { Locales, type IntlayerConfig } from "intlayer";

const config: IntlayerConfig = {
  internationalization: {
    locales: [
      Locales.ENGLISH,
      Locales.KOREAN,
      Locales.FRENCH,  // Add new locale
    ],
    defaultLocale: Locales.ENGLISH,
  },
  // ...
};
```

---

## Manual Translation Contribution

To contribute translations without using AI:

### Step 1: Fork and Clone

```bash
git clone https://github.com/your-username/truthound-dashboard
cd truthound-dashboard/frontend
npm install
```

### Step 2: Add Translations to Content Files

Edit each `*.content.ts` file and add your language:

```typescript
// frontend/src/content/common.content.ts
const commonContent = {
  key: "common",
  content: {
    save: t({
      en: "Save",
      ko: "저장",
      fr: "Enregistrer",  // Add French
    }),
    cancel: t({
      en: "Cancel",
      ko: "취소",
      fr: "Annuler",  // Add French
    }),
    // Add translations to all keys...
  },
} satisfies Dictionary;
```

### Step 3: Update Configuration

Add the new locale to `intlayer.config.ts`:

```typescript
locales: [Locales.ENGLISH, Locales.KOREAN, Locales.FRENCH],
```

### Step 4: Test

```bash
npm run dev
# Switch to your language in the UI
```

### Step 5: Submit Pull Request

```bash
git add .
git commit -m "feat(i18n): add French translations"
git push origin feature/french-translations
# Create PR on GitHub
```

---

## Troubleshooting

### Translation Not Appearing

1. Ensure the locale is added to `intlayer.config.ts`
2. Rebuild the types: `npx intlayer build`
3. Restart the dev server: `npm run dev`

### TypeScript Errors After Adding Language

```bash
cd frontend
npx intlayer build
npm run dev
```

### AI Translation Fails

1. Verify your API key is set correctly:
   ```bash
   echo $OPENAI_API_KEY
   ```

2. Check Node.js is installed:
   ```bash
   node --version  # Should be v18+
   ```

3. Try a different provider:
   ```bash
   truthound translate -l fr -p anthropic
   ```

### Missing Translations for Some Keys

AI translation may occasionally miss keys. Check the output and manually add any missing translations:

```typescript
myKey: t({
  en: "Original text",
  ko: "한국어 텍스트",
  fr: "Texte français",  // Add manually if missing
}),
```

---

## Best Practices

1. **Keep translations concise** - UI space is limited
2. **Test RTL languages** - Arabic, Hebrew require RTL layout
3. **Use placeholders consistently** - Keep `{variable}` syntax
4. **Review AI translations** - AI may make context errors
5. **Update all languages together** - Avoid partial translations

---

## Security Note

When using the `truthound translate` command:

- API keys are only used locally for the translation request
- Keys are never stored in files or sent to our servers
- Translation results (not keys) are saved to content files
- No sensitive data is included in the translated content

---

## References

- [Intlayer Documentation](https://intlayer.org/doc)
- [Vite + React Integration](https://intlayer.org/doc/environment/vite-and-react)
- [Content Declaration Guide](https://intlayer.org/doc/concept/content-declaration)
- [Intlayer GitHub](https://github.com/aymericzip/intlayer)
