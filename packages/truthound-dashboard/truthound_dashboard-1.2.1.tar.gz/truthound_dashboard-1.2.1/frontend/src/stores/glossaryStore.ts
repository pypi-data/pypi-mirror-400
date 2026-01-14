/**
 * Glossary store using Zustand for global state management.
 *
 * Manages business glossary terms, categories, and their relationships.
 */

import { create } from 'zustand'
import {
  getTerms,
  getTerm,
  createTerm as apiCreateTerm,
  updateTerm as apiUpdateTerm,
  deleteTerm as apiDeleteTerm,
  getCategories,
  createCategory as apiCreateCategory,
  updateCategory as apiUpdateCategory,
  deleteCategory as apiDeleteCategory,
  type GlossaryTerm,
  type GlossaryCategory,
  type TermCreate,
  type TermUpdate,
  type CategoryCreate,
  type CategoryUpdate,
} from '@/api/client'

interface GlossaryState {
  terms: GlossaryTerm[]
  categories: GlossaryCategory[]
  selectedTerm: GlossaryTerm | null
  loading: boolean
  error: string | null

  // Term actions
  fetchTerms: (params?: {
    search?: string
    category_id?: string
    status?: string
  }) => Promise<void>
  fetchTerm: (id: string) => Promise<void>
  createTerm: (data: TermCreate) => Promise<GlossaryTerm>
  updateTerm: (id: string, data: TermUpdate) => Promise<GlossaryTerm>
  deleteTerm: (id: string) => Promise<void>
  clearSelectedTerm: () => void

  // Category actions
  fetchCategories: () => Promise<void>
  createCategory: (data: CategoryCreate) => Promise<GlossaryCategory>
  updateCategory: (id: string, data: CategoryUpdate) => Promise<GlossaryCategory>
  deleteCategory: (id: string) => Promise<void>

  // Utility
  clearError: () => void
}

export const useGlossaryStore = create<GlossaryState>((set) => ({
  terms: [],
  categories: [],
  selectedTerm: null,
  loading: false,
  error: null,

  fetchTerms: async (params) => {
    set({ loading: true, error: null })
    try {
      const terms = await getTerms(params)
      set({ terms, loading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch terms'
      set({ error: message, loading: false })
    }
  },

  fetchTerm: async (id) => {
    set({ loading: true, error: null })
    try {
      const term = await getTerm(id)
      set({ selectedTerm: term, loading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch term'
      set({ error: message, loading: false })
    }
  },

  createTerm: async (data) => {
    set({ loading: true, error: null })
    try {
      const term = await apiCreateTerm(data)
      set((state) => ({
        terms: [term, ...state.terms],
        loading: false,
      }))
      return term
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create term'
      set({ error: message, loading: false })
      throw err
    }
  },

  updateTerm: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const term = await apiUpdateTerm(id, data)
      set((state) => ({
        terms: state.terms.map((t) => (t.id === id ? term : t)),
        selectedTerm: state.selectedTerm?.id === id ? term : state.selectedTerm,
        loading: false,
      }))
      return term
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update term'
      set({ error: message, loading: false })
      throw err
    }
  },

  deleteTerm: async (id) => {
    set({ loading: true, error: null })
    try {
      await apiDeleteTerm(id)
      set((state) => ({
        terms: state.terms.filter((t) => t.id !== id),
        selectedTerm: state.selectedTerm?.id === id ? null : state.selectedTerm,
        loading: false,
      }))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete term'
      set({ error: message, loading: false })
      throw err
    }
  },

  clearSelectedTerm: () => set({ selectedTerm: null }),

  fetchCategories: async () => {
    try {
      const categories = await getCategories()
      set({ categories })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch categories'
      set({ error: message })
    }
  },

  createCategory: async (data) => {
    try {
      const category = await apiCreateCategory(data)
      set((state) => ({
        categories: [...state.categories, category],
      }))
      return category
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create category'
      set({ error: message })
      throw err
    }
  },

  updateCategory: async (id, data) => {
    try {
      const category = await apiUpdateCategory(id, data)
      set((state) => ({
        categories: state.categories.map((c) => (c.id === id ? category : c)),
      }))
      return category
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update category'
      set({ error: message })
      throw err
    }
  },

  deleteCategory: async (id) => {
    try {
      await apiDeleteCategory(id)
      set((state) => ({
        categories: state.categories.filter((c) => c.id !== id),
      }))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete category'
      set({ error: message })
      throw err
    }
  },

  clearError: () => set({ error: null }),
}))
