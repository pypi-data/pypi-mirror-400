/**
 * Loading Fallback Component
 *
 * Used as a Suspense fallback during lazy loading of components.
 * Provides a consistent loading experience across the application.
 */

interface LoadingFallbackProps {
  /**
   * Optional message to display
   * Note: This should be a plain string as i18n may not be available yet
   */
  message?: string
  /**
   * Whether to show fullscreen loading
   * @default true
   */
  fullScreen?: boolean
}

export function LoadingFallback({
  message = 'Loading...',
  fullScreen = true,
}: LoadingFallbackProps) {
  const containerClass = fullScreen
    ? 'flex items-center justify-center h-screen w-full'
    : 'flex items-center justify-center p-8'

  return (
    <div className={containerClass}>
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        <span className="text-sm text-muted-foreground">{message}</span>
      </div>
    </div>
  )
}

export default LoadingFallback
