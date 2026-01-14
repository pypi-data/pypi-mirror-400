import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes with clsx
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a date string to locale format
 */
export function formatDate(date: string | Date | null | undefined): string {
  if (!date) return '-'
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format a number with commas
 */
export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '-'
  return num.toLocaleString()
}

/**
 * Format duration in milliseconds to human readable
 */
export function formatDuration(ms: number | null | undefined): string {
  if (ms === null || ms === undefined) return '-'
  if (ms < 1000) return `${ms}ms`
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`
  return `${(ms / 60000).toFixed(1)}m`
}

/**
 * Format bytes to human readable size
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

/**
 * Get severity color class
 */
export function getSeverityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'text-red-600 dark:text-red-400'
    case 'high':
      return 'text-orange-600 dark:text-orange-400'
    case 'medium':
      return 'text-yellow-600 dark:text-yellow-400'
    case 'low':
      return 'text-green-600 dark:text-green-400'
    default:
      return 'text-muted-foreground'
  }
}

/**
 * Get status color class
 */
export function getStatusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'success':
      return 'text-green-600 dark:text-green-400'
    case 'failed':
      return 'text-red-600 dark:text-red-400'
    case 'running':
      return 'text-blue-600 dark:text-blue-400'
    case 'pending':
      return 'text-gray-500'
    case 'error':
      return 'text-red-600 dark:text-red-400'
    default:
      return 'text-muted-foreground'
  }
}

/**
 * Get status badge variant
 */
export function getStatusBadgeVariant(
  status: string
): 'default' | 'secondary' | 'destructive' | 'outline' {
  switch (status.toLowerCase()) {
    case 'success':
      return 'default'
    case 'failed':
    case 'error':
      return 'destructive'
    case 'running':
    case 'pending':
      return 'secondary'
    default:
      return 'outline'
  }
}
