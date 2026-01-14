/**
 * Reusable confirmation dialog component and hook.
 *
 * Usage:
 *   const { confirm, ConfirmDialog } = useConfirm()
 *
 *   const handleDelete = async () => {
 *     const confirmed = await confirm({
 *       title: 'Delete item?',
 *       description: 'This action cannot be undone.',
 *       confirmText: 'Delete',
 *       variant: 'destructive',
 *     })
 *     if (confirmed) {
 *       // proceed with deletion
 *     }
 *   }
 *
 *   return (
 *     <>
 *       <button onClick={handleDelete}>Delete</button>
 *       <ConfirmDialog />
 *     </>
 *   )
 */

import { useState, useCallback } from 'react'
import { useIntlayer } from '@/providers'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { cn } from '@/lib/utils'
import { buttonVariants } from '@/components/ui/button'
import { str } from '@/lib/intlayer-utils'

export interface ConfirmOptions {
  title: string
  description?: string
  confirmText?: string
  cancelText?: string
  variant?: 'default' | 'destructive'
}

interface ConfirmState extends ConfirmOptions {
  isOpen: boolean
  resolve: ((value: boolean) => void) | null
}

export function useConfirm() {
  const common = useIntlayer('common')
  const [state, setState] = useState<ConfirmState>({
    isOpen: false,
    title: '',
    description: '',
    confirmText: '',
    cancelText: '',
    variant: 'default',
    resolve: null,
  })

  const confirm = useCallback(
    (options: ConfirmOptions): Promise<boolean> => {
      return new Promise((resolve) => {
        setState({
          isOpen: true,
          title: options.title,
          description: options.description,
          confirmText: options.confirmText || str(common.confirm),
          cancelText: options.cancelText || str(common.cancel),
          variant: options.variant || 'default',
          resolve,
        })
      })
    },
    [common]
  )

  const handleConfirm = useCallback(() => {
    state.resolve?.(true)
    setState((prev) => ({ ...prev, isOpen: false, resolve: null }))
  }, [state.resolve])

  const handleCancel = useCallback(() => {
    state.resolve?.(false)
    setState((prev) => ({ ...prev, isOpen: false, resolve: null }))
  }, [state.resolve])

  const ConfirmDialogComponent = useCallback(
    () => (
      <AlertDialog open={state.isOpen} onOpenChange={(open) => !open && handleCancel()}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{state.title}</AlertDialogTitle>
            {state.description && (
              <AlertDialogDescription>{state.description}</AlertDialogDescription>
            )}
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleCancel}>
              {state.cancelText}
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirm}
              className={cn(
                state.variant === 'destructive' &&
                  buttonVariants({ variant: 'destructive' })
              )}
            >
              {state.confirmText}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    ),
    [state, handleConfirm, handleCancel]
  )

  return {
    confirm,
    ConfirmDialog: ConfirmDialogComponent,
  }
}

export default useConfirm
