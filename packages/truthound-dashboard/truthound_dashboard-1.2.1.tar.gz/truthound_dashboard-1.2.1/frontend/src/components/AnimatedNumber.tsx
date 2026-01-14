import { useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/utils'

interface AnimatedNumberProps {
  value: number
  duration?: number
  className?: string
}

export function AnimatedNumber({
  value,
  duration = 1000,
  className,
}: AnimatedNumberProps) {
  const [displayValue, setDisplayValue] = useState(0)
  const [isAnimating, setIsAnimating] = useState(true)
  const animationRef = useRef<number | null>(null)
  const startTimeRef = useRef<number | null>(null)
  const hasAnimated = useRef(false)

  useEffect(() => {
    // Only animate on first load
    if (hasAnimated.current) {
      setDisplayValue(value)
      return
    }

    setIsAnimating(true)
    const startValue = 0
    const endValue = value

    // If value is 0, just show it
    if (endValue === 0) {
      setDisplayValue(0)
      setIsAnimating(false)
      hasAnimated.current = true
      return
    }

    const animate = (currentTime: number) => {
      if (startTimeRef.current === null) {
        startTimeRef.current = currentTime
      }

      const elapsed = currentTime - startTimeRef.current
      const progress = Math.min(elapsed / duration, 1)

      // Smooth ease-out-expo easing for more dramatic effect
      const easeOutExpo = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)

      const currentValue = startValue + (endValue - startValue) * easeOutExpo

      setDisplayValue(currentValue)

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate)
      } else {
        setDisplayValue(endValue)
        setIsAnimating(false)
        hasAnimated.current = true
      }
    }

    // Reset and start animation
    startTimeRef.current = null
    animationRef.current = requestAnimationFrame(animate)

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [value, duration])

  return (
    <span
      className={cn(
        'inline-block transition-all',
        isAnimating && 'animate-in fade-in zoom-in-50 duration-500',
        className
      )}
    >
      {Math.round(displayValue)}
    </span>
  )
}
