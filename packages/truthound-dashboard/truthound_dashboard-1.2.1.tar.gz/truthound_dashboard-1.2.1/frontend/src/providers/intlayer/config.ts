/**
 * Intlayer locale configuration
 *
 * Centralized configuration for supported locales and related settings.
 * This file serves as the single source of truth for locale-related constants.
 */
import { Locales } from 'intlayer'

/**
 * Supported locales in the application
 * Add new locales here when expanding language support
 */
export const SUPPORTED_LOCALES = [Locales.ENGLISH, Locales.KOREAN, Locales.FRENCH] as const

export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number]

/**
 * Default locale when no preference is detected
 */
export const DEFAULT_LOCALE: SupportedLocale = Locales.ENGLISH

/**
 * Storage key for persisting locale preference
 */
export const LOCALE_STORAGE_KEY = 'truthound-locale'

/**
 * Locale metadata for UI display
 */
export interface LocaleInfo {
  code: SupportedLocale
  name: string
  nativeName: string
  flag?: string
}

/**
 * Available locales with display information
 * Used for language selector UI components
 */
export const LOCALE_INFO: readonly LocaleInfo[] = [
  {
    code: Locales.ENGLISH,
    name: 'English',
    nativeName: 'English',
    flag: '🇺🇸',
  },
  {
    code: Locales.KOREAN,
    name: 'Korean',
    nativeName: '한국어',
    flag: '🇰🇷',
  },
  {
    code: Locales.FRENCH,
    name: 'French',
    nativeName: 'Français',
    flag: '🇫🇷',
  },
] as const

/**
 * Get locale info by code
 */
export function getLocaleInfo(locale: SupportedLocale): LocaleInfo | undefined {
  return LOCALE_INFO.find((info) => info.code === locale)
}

/**
 * Check if a locale is supported
 */
export function isSupportedLocale(locale: string): locale is SupportedLocale {
  return SUPPORTED_LOCALES.includes(locale as SupportedLocale)
}

/**
 * Get browser's preferred locale if supported, otherwise return default
 */
export function getBrowserLocale(): SupportedLocale {
  if (typeof navigator === 'undefined') {
    return DEFAULT_LOCALE
  }

  // Check navigator.languages first (preferred)
  const browserLocales = navigator.languages || [navigator.language]

  for (const browserLocale of browserLocales) {
    // Extract language code (e.g., 'en-US' -> 'en')
    const langCode = browserLocale.split('-')[0].toLowerCase()

    // Map common language codes to our supported locales
    if (langCode === 'ko') {
      return Locales.KOREAN
    }
    if (langCode === 'en') {
      return Locales.ENGLISH
    }
  }

  return DEFAULT_LOCALE
}
