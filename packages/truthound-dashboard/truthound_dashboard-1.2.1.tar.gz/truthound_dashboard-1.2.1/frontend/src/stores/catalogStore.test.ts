/**
 * Catalog store tests
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useCatalogStore } from './catalogStore'

// Mock the API client
vi.mock('@/api/client', () => ({
  getAssets: vi.fn(),
  getAsset: vi.fn(),
  createAsset: vi.fn(),
  updateAsset: vi.fn(),
  deleteAsset: vi.fn(),
  mapColumnToTerm: vi.fn(),
  unmapColumnFromTerm: vi.fn(),
}))

import {
  getAssets,
  getAsset,
  createAsset,
  updateAsset,
  deleteAsset,
  mapColumnToTerm,
  unmapColumnFromTerm,
} from '@/api/client'

const mockGetAssets = vi.mocked(getAssets)
const mockGetAsset = vi.mocked(getAsset)
const mockCreateAsset = vi.mocked(createAsset)
const mockUpdateAsset = vi.mocked(updateAsset)
const mockDeleteAsset = vi.mocked(deleteAsset)
const mockMapColumnToTerm = vi.mocked(mapColumnToTerm)
const mockUnmapColumnFromTerm = vi.mocked(unmapColumnFromTerm)

describe('CatalogStore', () => {
  beforeEach(() => {
    // Reset store state
    useCatalogStore.setState({
      assets: [],
      selectedAsset: null,
      loading: false,
      error: null,
    })
    // Clear all mocks
    vi.clearAllMocks()
  })

  describe('fetchAssets', () => {
    it('fetches and stores assets', async () => {
      const mockAssets = [
        { id: '1', name: 'asset1', asset_type: 'table' },
        { id: '2', name: 'asset2', asset_type: 'file' },
      ]
      mockGetAssets.mockResolvedValue(mockAssets as any)

      await useCatalogStore.getState().fetchAssets()

      expect(useCatalogStore.getState().assets).toEqual(mockAssets)
      expect(useCatalogStore.getState().loading).toBe(false)
    })

    it('handles fetch error', async () => {
      mockGetAssets.mockRejectedValue(new Error('Network error'))

      await useCatalogStore.getState().fetchAssets()

      expect(useCatalogStore.getState().error).toBe('Network error')
      expect(useCatalogStore.getState().loading).toBe(false)
    })

    it('passes filter params', async () => {
      mockGetAssets.mockResolvedValue([])

      await useCatalogStore.getState().fetchAssets({
        search: 'test',
        asset_type: 'table',
        source_id: 'src-1',
      })

      expect(mockGetAssets).toHaveBeenCalledWith({
        search: 'test',
        asset_type: 'table',
        source_id: 'src-1',
      })
    })
  })

  describe('fetchAsset', () => {
    it('fetches and stores selected asset', async () => {
      const mockAsset = {
        id: '1',
        name: 'asset1',
        asset_type: 'table',
        columns: [],
        tags: [],
      }
      mockGetAsset.mockResolvedValue(mockAsset as any)

      await useCatalogStore.getState().fetchAsset('1')

      expect(useCatalogStore.getState().selectedAsset).toEqual(mockAsset)
    })
  })

  describe('createAsset', () => {
    it('creates asset and refreshes list', async () => {
      const newAsset = {
        id: '1',
        name: 'new_asset',
        asset_type: 'table',
        columns: [],
        tags: [],
      }
      mockCreateAsset.mockResolvedValue(newAsset as any)
      mockGetAssets.mockResolvedValue([{ id: '1', name: 'new_asset' }] as any)

      const result = await useCatalogStore.getState().createAsset({
        name: 'new_asset',
        asset_type: 'table',
      })

      expect(result).toEqual(newAsset)
      expect(mockGetAssets).toHaveBeenCalled()
    })
  })

  describe('updateAsset', () => {
    it('updates asset in list', async () => {
      const existingAsset = {
        id: '1',
        name: 'original',
        asset_type: 'table',
      }
      const updatedAsset = {
        ...existingAsset,
        name: 'updated',
        columns: [],
        tags: [],
      }

      useCatalogStore.setState({ assets: [existingAsset as any] })
      mockUpdateAsset.mockResolvedValue(updatedAsset as any)

      await useCatalogStore.getState().updateAsset('1', { name: 'updated' })

      expect(useCatalogStore.getState().assets[0].name).toBe('updated')
    })

    it('updates selected asset if matching', async () => {
      const asset = {
        id: '1',
        name: 'original',
        asset_type: 'table',
        columns: [],
        tags: [],
      }
      const updatedAsset = { ...asset, name: 'updated' }

      useCatalogStore.setState({
        assets: [asset as any],
        selectedAsset: asset as any,
      })
      mockUpdateAsset.mockResolvedValue(updatedAsset as any)

      await useCatalogStore.getState().updateAsset('1', { name: 'updated' })

      expect(useCatalogStore.getState().selectedAsset?.name).toBe('updated')
    })
  })

  describe('deleteAsset', () => {
    it('removes asset from list', async () => {
      const assets = [
        { id: '1', name: 'asset1' },
        { id: '2', name: 'asset2' },
      ]
      useCatalogStore.setState({ assets: assets as any })
      mockDeleteAsset.mockResolvedValue({ ok: true })

      await useCatalogStore.getState().deleteAsset('1')

      expect(useCatalogStore.getState().assets).toHaveLength(1)
      expect(useCatalogStore.getState().assets[0].id).toBe('2')
    })

    it('clears selected asset if deleted', async () => {
      const asset = { id: '1', name: 'asset1' }
      useCatalogStore.setState({
        assets: [asset as any],
        selectedAsset: asset as any,
      })
      mockDeleteAsset.mockResolvedValue({ ok: true })

      await useCatalogStore.getState().deleteAsset('1')

      expect(useCatalogStore.getState().selectedAsset).toBeNull()
    })
  })

  describe('mapColumnToTerm', () => {
    it('updates column with term mapping', async () => {
      const column = { id: 'col-1', name: 'user_id', term_id: null }
      const updatedColumn = { ...column, term_id: 'term-1' }

      useCatalogStore.setState({
        selectedAsset: {
          id: '1',
          name: 'users',
          columns: [column],
          tags: [],
        } as any,
      })
      mockMapColumnToTerm.mockResolvedValue(updatedColumn as any)

      await useCatalogStore.getState().mapColumnToTerm('col-1', 'term-1')

      const columns = useCatalogStore.getState().selectedAsset?.columns
      expect(columns?.[0].term_id).toBe('term-1')
    })

    it('does nothing if no selected asset', async () => {
      useCatalogStore.setState({ selectedAsset: null })
      mockMapColumnToTerm.mockResolvedValue({} as any)

      await useCatalogStore.getState().mapColumnToTerm('col-1', 'term-1')

      expect(useCatalogStore.getState().selectedAsset).toBeNull()
    })
  })

  describe('unmapColumnFromTerm', () => {
    it('removes term mapping from column', async () => {
      const column = { id: 'col-1', name: 'user_id', term_id: 'term-1' }
      const updatedColumn = { ...column, term_id: undefined }

      useCatalogStore.setState({
        selectedAsset: {
          id: '1',
          name: 'users',
          columns: [column],
          tags: [],
        } as any,
      })
      mockUnmapColumnFromTerm.mockResolvedValue(updatedColumn as any)

      await useCatalogStore.getState().unmapColumnFromTerm('col-1')

      const columns = useCatalogStore.getState().selectedAsset?.columns
      expect(columns?.[0].term_id).toBeUndefined()
    })
  })

  describe('clearSelectedAsset', () => {
    it('clears selected asset', () => {
      useCatalogStore.setState({
        selectedAsset: { id: '1', name: 'asset' } as any,
      })

      useCatalogStore.getState().clearSelectedAsset()

      expect(useCatalogStore.getState().selectedAsset).toBeNull()
    })
  })

  describe('clearError', () => {
    it('clears error', () => {
      useCatalogStore.setState({ error: 'Some error' })

      useCatalogStore.getState().clearError()

      expect(useCatalogStore.getState().error).toBeNull()
    })
  })
})
