/**
 * Utility functions for working with Intlayer translations.
 *
 * These helpers solve type compatibility issues between IntlayerNode
 * and components that expect plain strings (e.g., toast, aria-label).
 */
import type { ReactNode } from 'react'

/**
 * IntlayerNode is ReactNode & { value: T }.
 * This type represents the structure for type-safe extraction.
 */
type IntlayerNodeLike<T = string> = ReactNode & { value?: T }

/**
 * Extracts the string value from an IntlayerNode for use in
 * contexts that require plain strings (toast titles, aria-labels, etc.)
 *
 * @example
 * const common = useIntlayer('common')
 * toast({ title: str(common.error) })
 *
 * @param node - IntlayerNode or string value
 * @returns The underlying string value
 */
export function str(node: IntlayerNodeLike<string> | string | undefined): string {
  if (node === undefined || node === null) {
    return ''
  }
  if (typeof node === 'string') {
    return node
  }
  // IntlayerNode has a value property containing the raw string
  if (typeof node === 'object' && 'value' in node && typeof node.value === 'string') {
    return node.value
  }
  // Fallback: convert to string
  return String(node)
}

/**
 * Type assertion helper for IntlayerNode to ReactNode.
 * Use when you know the value is safe to use as ReactNode but TypeScript complains.
 *
 * @example
 * <Badge>{asNode(validation.status)}</Badge>
 */
export function asNode(node: IntlayerNodeLike | string | undefined): ReactNode {
  return node as ReactNode
}
