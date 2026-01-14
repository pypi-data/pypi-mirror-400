import { useRef, useState, type ReactNode, type MouseEvent } from 'react'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface GlassCardProps {
  children: ReactNode
  className?: string
  glowColor?: string
}

export function GlassCard({ children, className, glowColor = 'white' }: GlassCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [isHovering, setIsHovering] = useState(false)

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return

    const rect = cardRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    setMousePosition({ x, y })
  }

  const handleMouseEnter = () => setIsHovering(true)
  const handleMouseLeave = () => setIsHovering(false)

  return (
    <Card
      ref={cardRef}
      className={cn('relative overflow-hidden transition-all duration-300', className)}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{
        transform: isHovering ? 'translateY(-2px)' : 'translateY(0)',
      }}
    >
      {/* Shine effect overlay */}
      <div
        className="pointer-events-none absolute inset-0 z-10 transition-opacity duration-300"
        style={{
          opacity: isHovering ? 1 : 0,
          background: `radial-gradient(
            350px circle at ${mousePosition.x}px ${mousePosition.y}px,
            ${glowColor}15 0%,
            ${glowColor}08 25%,
            transparent 50%
          )`,
        }}
      />

      {/* Border glow effect */}
      <div
        className="pointer-events-none absolute inset-0 z-10 rounded-lg transition-opacity duration-300"
        style={{
          opacity: isHovering ? 1 : 0,
          background: `radial-gradient(
            200px circle at ${mousePosition.x}px ${mousePosition.y}px,
            ${glowColor}20 0%,
            transparent 70%
          )`,
          mask: 'linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)',
          maskComposite: 'xor',
          WebkitMaskComposite: 'xor',
          padding: '1px',
        }}
      />

      {/* Sparkle line effect */}
      <div
        className="pointer-events-none absolute inset-0 z-10 transition-opacity duration-500"
        style={{
          opacity: isHovering ? 0.6 : 0,
          background: `linear-gradient(
            105deg,
            transparent 40%,
            ${glowColor}10 45%,
            ${glowColor}25 50%,
            ${glowColor}10 55%,
            transparent 60%
          )`,
          backgroundSize: '200% 100%',
          backgroundPosition: isHovering ? '100% 0' : '-100% 0',
          transition: 'background-position 0.8s ease, opacity 0.3s ease',
        }}
      />

      {children}
    </Card>
  )
}
