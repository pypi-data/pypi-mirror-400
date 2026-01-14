/**
 * Glossary store tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useGlossaryStore } from './glossaryStore'

// Mock the API client
vi.mock('@/api/client', () => ({
  getTerms: vi.fn(),
  getTerm: vi.fn(),
  createTerm: vi.fn(),
  updateTerm: vi.fn(),
  deleteTerm: vi.fn(),
  getCategories: vi.fn(),
  createCategory: vi.fn(),
  updateCategory: vi.fn(),
  deleteCategory: vi.fn(),
}))

import {
  getTerms,
  getTerm,
  createTerm,
  updateTerm,
  deleteTerm,
  getCategories,
  createCategory,
  updateCategory,
  deleteCategory,
} from '@/api/client'

const mockGetTerms = vi.mocked(getTerms)
const mockGetTerm = vi.mocked(getTerm)
const mockCreateTerm = vi.mocked(createTerm)
const mockUpdateTerm = vi.mocked(updateTerm)
const mockDeleteTerm = vi.mocked(deleteTerm)
const mockGetCategories = vi.mocked(getCategories)
const mockCreateCategory = vi.mocked(createCategory)
const mockUpdateCategory = vi.mocked(updateCategory)
const mockDeleteCategory = vi.mocked(deleteCategory)

describe('GlossaryStore', () => {
  beforeEach(() => {
    // Reset store state
    useGlossaryStore.setState({
      terms: [],
      categories: [],
      selectedTerm: null,
      loading: false,
      error: null,
    })
    // Clear all mocks
    vi.clearAllMocks()
  })

  describe('fetchTerms', () => {
    it('fetches and stores terms', async () => {
      const mockTerms = [
        { id: '1', name: 'Term 1', definition: 'Def 1', status: 'draft' },
        { id: '2', name: 'Term 2', definition: 'Def 2', status: 'approved' },
      ]
      mockGetTerms.mockResolvedValue(mockTerms as any)

      await useGlossaryStore.getState().fetchTerms()

      expect(useGlossaryStore.getState().terms).toEqual(mockTerms)
      expect(useGlossaryStore.getState().loading).toBe(false)
    })

    it('handles fetch error', async () => {
      mockGetTerms.mockRejectedValue(new Error('Network error'))

      await useGlossaryStore.getState().fetchTerms()

      expect(useGlossaryStore.getState().error).toBe('Network error')
      expect(useGlossaryStore.getState().loading).toBe(false)
    })

    it('passes search params', async () => {
      mockGetTerms.mockResolvedValue([])

      await useGlossaryStore.getState().fetchTerms({
        search: 'test',
        category_id: 'cat-1',
        status: 'approved',
      })

      expect(mockGetTerms).toHaveBeenCalledWith({
        search: 'test',
        category_id: 'cat-1',
        status: 'approved',
      })
    })
  })

  describe('fetchTerm', () => {
    it('fetches and stores selected term', async () => {
      const mockTerm = {
        id: '1',
        name: 'Term 1',
        definition: 'Def 1',
        status: 'draft',
      }
      mockGetTerm.mockResolvedValue(mockTerm as any)

      await useGlossaryStore.getState().fetchTerm('1')

      expect(useGlossaryStore.getState().selectedTerm).toEqual(mockTerm)
    })
  })

  describe('createTerm', () => {
    it('creates term and adds to list', async () => {
      const newTerm = {
        id: '1',
        name: 'New Term',
        definition: 'New Def',
        status: 'draft',
      }
      mockCreateTerm.mockResolvedValue(newTerm as any)

      const result = await useGlossaryStore.getState().createTerm({
        name: 'New Term',
        definition: 'New Def',
      })

      expect(result).toEqual(newTerm)
      expect(useGlossaryStore.getState().terms).toContainEqual(newTerm)
    })
  })

  describe('updateTerm', () => {
    it('updates term in list', async () => {
      const existingTerm = {
        id: '1',
        name: 'Original',
        definition: 'Def',
        status: 'draft',
      }
      const updatedTerm = { ...existingTerm, name: 'Updated' }

      useGlossaryStore.setState({ terms: [existingTerm as any] })
      mockUpdateTerm.mockResolvedValue(updatedTerm as any)

      await useGlossaryStore.getState().updateTerm('1', { name: 'Updated' })

      expect(useGlossaryStore.getState().terms[0].name).toBe('Updated')
    })

    it('updates selected term if matching', async () => {
      const term = {
        id: '1',
        name: 'Original',
        definition: 'Def',
        status: 'draft',
      }
      const updatedTerm = { ...term, name: 'Updated' }

      useGlossaryStore.setState({
        terms: [term as any],
        selectedTerm: term as any,
      })
      mockUpdateTerm.mockResolvedValue(updatedTerm as any)

      await useGlossaryStore.getState().updateTerm('1', { name: 'Updated' })

      expect(useGlossaryStore.getState().selectedTerm?.name).toBe('Updated')
    })
  })

  describe('deleteTerm', () => {
    it('removes term from list', async () => {
      const terms = [
        { id: '1', name: 'Term 1' },
        { id: '2', name: 'Term 2' },
      ]
      useGlossaryStore.setState({ terms: terms as any })
      mockDeleteTerm.mockResolvedValue({ ok: true })

      await useGlossaryStore.getState().deleteTerm('1')

      expect(useGlossaryStore.getState().terms).toHaveLength(1)
      expect(useGlossaryStore.getState().terms[0].id).toBe('2')
    })

    it('clears selected term if deleted', async () => {
      const term = { id: '1', name: 'Term 1' }
      useGlossaryStore.setState({
        terms: [term as any],
        selectedTerm: term as any,
      })
      mockDeleteTerm.mockResolvedValue({ ok: true })

      await useGlossaryStore.getState().deleteTerm('1')

      expect(useGlossaryStore.getState().selectedTerm).toBeNull()
    })
  })

  describe('fetchCategories', () => {
    it('fetches and stores categories', async () => {
      const mockCategories = [
        { id: '1', name: 'Category 1' },
        { id: '2', name: 'Category 2' },
      ]
      mockGetCategories.mockResolvedValue(mockCategories as any)

      await useGlossaryStore.getState().fetchCategories()

      expect(useGlossaryStore.getState().categories).toEqual(mockCategories)
    })
  })

  describe('createCategory', () => {
    it('creates and adds category', async () => {
      const newCategory = { id: '1', name: 'New Category' }
      mockCreateCategory.mockResolvedValue(newCategory as any)

      const result = await useGlossaryStore.getState().createCategory({
        name: 'New Category',
      })

      expect(result).toEqual(newCategory)
      expect(useGlossaryStore.getState().categories).toContainEqual(newCategory)
    })
  })

  describe('updateCategory', () => {
    it('updates category in list', async () => {
      const category = { id: '1', name: 'Original' }
      const updated = { ...category, name: 'Updated' }

      useGlossaryStore.setState({ categories: [category as any] })
      mockUpdateCategory.mockResolvedValue(updated as any)

      await useGlossaryStore.getState().updateCategory('1', { name: 'Updated' })

      expect(useGlossaryStore.getState().categories[0].name).toBe('Updated')
    })
  })

  describe('deleteCategory', () => {
    it('removes category from list', async () => {
      const categories = [
        { id: '1', name: 'Cat 1' },
        { id: '2', name: 'Cat 2' },
      ]
      useGlossaryStore.setState({ categories: categories as any })
      mockDeleteCategory.mockResolvedValue({ ok: true })

      await useGlossaryStore.getState().deleteCategory('1')

      expect(useGlossaryStore.getState().categories).toHaveLength(1)
    })
  })

  describe('clearSelectedTerm', () => {
    it('clears selected term', () => {
      useGlossaryStore.setState({
        selectedTerm: { id: '1', name: 'Term' } as any,
      })

      useGlossaryStore.getState().clearSelectedTerm()

      expect(useGlossaryStore.getState().selectedTerm).toBeNull()
    })
  })

  describe('clearError', () => {
    it('clears error', () => {
      useGlossaryStore.setState({ error: 'Some error' })

      useGlossaryStore.getState().clearError()

      expect(useGlossaryStore.getState().error).toBeNull()
    })
  })
})
