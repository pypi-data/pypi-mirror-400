/**
 * Demo mode banner - shown when running with mock API
 */

import { AlertTriangle, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useIntlayer } from '@/providers'
import { str } from '@/lib/intlayer-utils'

// Export banner height for layout calculations
export const DEMO_BANNER_HEIGHT = 40

export function useDemoBanner() {
  const [dismissed, setDismissed] = useState(false)
  const isVisible =
    import.meta.env.VITE_MOCK_API === 'true' && !dismissed
  return { isVisible, dismiss: () => setDismissed(true) }
}

export function DemoBanner() {
  const demo = useIntlayer('demo')
  const { isVisible, dismiss } = useDemoBanner()

  useEffect(() => {
    // Set CSS variable for banner height
    document.documentElement.style.setProperty(
      '--demo-banner-height',
      isVisible ? `${DEMO_BANNER_HEIGHT}px` : '0px'
    )
    return () => {
      document.documentElement.style.setProperty('--demo-banner-height', '0px')
    }
  }, [isVisible])

  if (!isVisible) {
    return null
  }

  return (
    <div
      className="fixed top-0 left-0 right-0 z-[100] bg-gradient-to-r from-amber-500/90 to-orange-500/90 text-white px-4 py-2 text-sm"
      style={{ height: DEMO_BANNER_HEIGHT }}
    >
      <div className="container mx-auto flex items-center justify-between h-full">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4" />
          <span>
            <strong>{demo.title}</strong> - {demo.description}
          </span>
        </div>
        <button
          onClick={dismiss}
          className="p-1 hover:bg-white/20 rounded transition-colors"
          aria-label={str(demo.dismiss)}
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
