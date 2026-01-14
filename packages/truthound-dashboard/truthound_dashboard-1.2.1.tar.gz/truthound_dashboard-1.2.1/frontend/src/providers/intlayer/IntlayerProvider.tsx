/**
 * Intlayer Provider Wrapper
 *
 * Wraps the react-intlayer IntlayerProvider with additional features:
 * - Locale persistence to localStorage
 * - Browser locale detection
 * - Type-safe locale management
 */
import { type ReactNode, useEffect, useState, useCallback } from 'react'
import { IntlayerProvider as BaseIntlayerProvider } from 'react-intlayer'
import {
  DEFAULT_LOCALE,
  LOCALE_STORAGE_KEY,
  getBrowserLocale,
  isSupportedLocale,
  type SupportedLocale,
} from './config'

export interface IntlayerProviderProps {
  children: ReactNode
  /**
   * Override the default/stored locale
   * Useful for testing or server-side rendering
   */
  forcedLocale?: SupportedLocale
  /**
   * Custom storage key for locale persistence
   * @default 'truthound-locale'
   */
  storageKey?: string
  /**
   * Whether to detect browser locale on first visit
   * @default true
   */
  detectBrowserLocale?: boolean
}

/**
 * Get the initial locale from storage or browser detection
 */
function getInitialLocale(
  storageKey: string,
  detectBrowser: boolean
): SupportedLocale {
  // Try to get from localStorage first
  if (typeof window !== 'undefined') {
    const storedLocale = localStorage.getItem(storageKey)
    if (storedLocale && isSupportedLocale(storedLocale)) {
      return storedLocale
    }
  }

  // Fall back to browser detection or default
  if (detectBrowser) {
    return getBrowserLocale()
  }

  return DEFAULT_LOCALE
}

/**
 * Enhanced Intlayer Provider with persistence and browser detection
 *
 * @example
 * ```tsx
 * // Basic usage
 * <IntlayerProviderWrapper>
 *   <App />
 * </IntlayerProviderWrapper>
 *
 * // With forced locale (useful for testing)
 * <IntlayerProviderWrapper forcedLocale={Locales.KOREAN}>
 *   <App />
 * </IntlayerProviderWrapper>
 * ```
 */
export function IntlayerProviderWrapper({
  children,
  forcedLocale,
  storageKey = LOCALE_STORAGE_KEY,
  detectBrowserLocale = true,
}: IntlayerProviderProps) {
  const [locale, setLocaleState] = useState<SupportedLocale>(() =>
    forcedLocale ?? getInitialLocale(storageKey, detectBrowserLocale)
  )

  // Persist locale changes to localStorage
  // Note: We accept 'string' to match react-intlayer's setLocale callback type
  const handleLocaleChange = useCallback(
    (newLocale: string) => {
      if (isSupportedLocale(newLocale)) {
        setLocaleState(newLocale)
        if (typeof window !== 'undefined') {
          localStorage.setItem(storageKey, newLocale)
        }
      }
    },
    [storageKey]
  )

  // Sync with forcedLocale prop changes
  useEffect(() => {
    if (forcedLocale && forcedLocale !== locale) {
      handleLocaleChange(forcedLocale)
    }
  }, [forcedLocale, locale, handleLocaleChange])

  // Update document lang attribute for accessibility
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.lang = locale
    }
  }, [locale])

  return (
    <BaseIntlayerProvider locale={locale} setLocale={handleLocaleChange}>
      {children}
    </BaseIntlayerProvider>
  )
}

export default IntlayerProviderWrapper
