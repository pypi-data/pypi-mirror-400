/**
 * Intlayer provider module
 *
 * Exports all intlayer-related utilities and components
 */

// Provider component
export {
  IntlayerProviderWrapper,
  type IntlayerProviderProps,
} from './IntlayerProvider'

// Configuration and utilities
export {
  SUPPORTED_LOCALES,
  DEFAULT_LOCALE,
  LOCALE_STORAGE_KEY,
  LOCALE_INFO,
  getLocaleInfo,
  isSupportedLocale,
  getBrowserLocale,
  type SupportedLocale,
  type LocaleInfo,
} from './config'

// Re-export commonly used hooks from react-intlayer for convenience
export { useIntlayer, useLocale } from 'react-intlayer'
