/**
 * Theme store using Zustand for global state management.
 *
 * This provides an alternative to the context-based ThemeProvider
 * for cases where you need to access theme outside of React components.
 *
 * Features:
 * - Persistent storage in localStorage
 * - System theme detection
 * - Real-time theme switching
 * - Resolved theme computation
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Theme = 'light' | 'dark' | 'system'
export type ResolvedTheme = 'light' | 'dark'

interface ThemeState {
  /**
   * Current theme setting (may be 'system')
   */
  theme: Theme

  /**
   * Resolved theme after applying system preference
   */
  resolvedTheme: ResolvedTheme

  /**
   * Set the theme
   */
  setTheme: (theme: Theme) => void

  /**
   * Toggle between light and dark
   */
  toggleTheme: () => void

  /**
   * Check if dark mode is active
   */
  isDark: () => boolean
}

/**
 * Get the system's preferred color scheme
 */
function getSystemTheme(): ResolvedTheme {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

/**
 * Resolve a theme setting to an actual theme
 */
function resolveTheme(theme: Theme): ResolvedTheme {
  if (theme === 'system') {
    return getSystemTheme()
  }
  return theme
}

/**
 * Apply theme to the document
 */
function applyTheme(theme: ResolvedTheme): void {
  if (typeof window === 'undefined') return

  const root = document.documentElement
  root.classList.remove('light', 'dark')
  root.classList.add(theme)

  // Also set color-scheme for native elements
  root.style.colorScheme = theme
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: 'system',
      resolvedTheme: 'light',

      setTheme: (theme: Theme) => {
        const resolved = resolveTheme(theme)
        applyTheme(resolved)
        set({ theme, resolvedTheme: resolved })
      },

      toggleTheme: () => {
        const current = get().resolvedTheme
        const newTheme: Theme = current === 'dark' ? 'light' : 'dark'
        get().setTheme(newTheme)
      },

      isDark: () => get().resolvedTheme === 'dark',
    }),
    {
      name: 'truthound-theme-storage',
      onRehydrateStorage: () => (state) => {
        // Apply theme on rehydration
        if (state) {
          const resolved = resolveTheme(state.theme)
          applyTheme(resolved)
          state.resolvedTheme = resolved
        }
      },
    }
  )
)

// Initialize theme on load
if (typeof window !== 'undefined') {
  const stored = localStorage.getItem('truthound-theme-storage')
  if (stored) {
    try {
      const parsed = JSON.parse(stored)
      const theme = parsed.state?.theme || 'system'
      const resolved = resolveTheme(theme)
      applyTheme(resolved)
    } catch {
      // If parsing fails, apply system theme
      applyTheme(getSystemTheme())
    }
  } else {
    // No stored preference, use system
    applyTheme(getSystemTheme())
  }

  // Listen for system theme changes
  window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', (e) => {
      const state = useThemeStore.getState()
      if (state.theme === 'system') {
        const resolved = e.matches ? 'dark' : 'light'
        applyTheme(resolved)
        useThemeStore.setState({ resolvedTheme: resolved })
      }
    })
}
