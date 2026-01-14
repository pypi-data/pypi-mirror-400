/**
 * Theme toggle component for switching between light/dark/system themes.
 *
 * Features:
 * - Three-way toggle (light, dark, system)
 * - Keyboard accessible
 * - Visual feedback for current selection
 * - Smooth transitions
 */

import { Moon, Sun, Monitor } from 'lucide-react'
import { useTheme } from './theme-provider'
import { cn } from '@/lib/utils'

interface ThemeToggleProps {
  /**
   * Additional CSS classes
   */
  className?: string

  /**
   * Show labels instead of icons only
   */
  showLabels?: boolean

  /**
   * Variant style
   */
  variant?: 'default' | 'compact' | 'dropdown'
}

export function ThemeToggle({
  className,
  showLabels = false,
  variant = 'default',
}: ThemeToggleProps) {
  const { theme, setTheme } = useTheme()

  if (variant === 'compact') {
    return (
      <button
        onClick={() => {
          const next = theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light'
          setTheme(next)
        }}
        className={cn(
          'p-2 rounded-md',
          'hover:bg-gray-100 dark:hover:bg-gray-800',
          'transition-colors duration-200',
          className
        )}
        title={`Current theme: ${theme}`}
      >
        {theme === 'light' && <Sun className="h-5 w-5" />}
        {theme === 'dark' && <Moon className="h-5 w-5" />}
        {theme === 'system' && <Monitor className="h-5 w-5" />}
      </button>
    )
  }

  const options = [
    { value: 'light' as const, icon: Sun, label: 'Light' },
    { value: 'dark' as const, icon: Moon, label: 'Dark' },
    { value: 'system' as const, icon: Monitor, label: 'System' },
  ]

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1 p-1 rounded-lg',
        'bg-gray-100 dark:bg-gray-800',
        className
      )}
      role="radiogroup"
      aria-label="Theme selection"
    >
      {options.map(({ value, icon: Icon, label }) => (
        <button
          key={value}
          onClick={() => setTheme(value)}
          className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-md',
            'transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
            theme === value
              ? 'bg-white dark:bg-gray-700 shadow-sm text-foreground'
              : 'text-muted-foreground hover:text-foreground hover:bg-gray-200/50 dark:hover:bg-gray-700/50'
          )}
          role="radio"
          aria-checked={theme === value}
          aria-label={label}
          title={label}
        >
          <Icon className="h-4 w-4" />
          {showLabels && <span className="text-sm font-medium">{label}</span>}
        </button>
      ))}
    </div>
  )
}

/**
 * Simple theme toggle button that cycles through themes
 */
export function ThemeToggleButton({ className }: { className?: string }) {
  const { theme, setTheme } = useTheme()

  const cycleTheme = () => {
    if (theme === 'light') setTheme('dark')
    else if (theme === 'dark') setTheme('system')
    else setTheme('light')
  }

  return (
    <button
      onClick={cycleTheme}
      className={cn(
        'relative p-2 rounded-md',
        'hover:bg-accent',
        'transition-colors duration-200',
        'focus:outline-none focus:ring-2 focus:ring-primary',
        className
      )}
      aria-label={`Current theme: ${theme}. Click to change.`}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-transform duration-300 dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute top-2 left-2 h-5 w-5 rotate-90 scale-0 transition-transform duration-300 dark:rotate-0 dark:scale-100" />
    </button>
  )
}

export default ThemeToggle
