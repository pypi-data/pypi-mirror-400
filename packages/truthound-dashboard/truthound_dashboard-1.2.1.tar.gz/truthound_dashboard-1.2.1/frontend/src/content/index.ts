/**
 * Content module index.
 *
 * Re-exports all content dictionaries for type-safe access.
 * Note: Content files are auto-detected by Intlayer, so this index
 * is primarily for documentation and IDE convenience.
 */

// Common translations
export { default as commonContent } from './common.content'
export { default as navContent } from './nav.content'
export { default as errorsContent } from './errors.content'

// Page-specific translations
export { default as dashboardContent } from './dashboard.content'
export { default as sourcesContent } from './sources.content'
export { default as validationContent } from './validation.content'
export { default as schedulesContent } from './schedules.content'
export { default as notificationsContent } from './notifications.content'
export { default as driftContent } from './drift.content'
export { default as settingsContent } from './settings.content'

// Component-specific translations
export { default as demoContent } from './demo.content'
