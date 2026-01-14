/**
 * Catalog store using Zustand for global state management.
 *
 * Manages data catalog assets, columns, and tags.
 */

import { create } from 'zustand'
import {
  getAssets,
  getAsset,
  createAsset as apiCreateAsset,
  updateAsset as apiUpdateAsset,
  deleteAsset as apiDeleteAsset,
  mapColumnToTerm as apiMapColumnToTerm,
  unmapColumnFromTerm as apiUnmapColumnFromTerm,
  type AssetListItem,
  type CatalogAsset,
  type AssetCreate,
  type AssetUpdate,
} from '@/api/client'

interface CatalogState {
  assets: AssetListItem[]
  selectedAsset: CatalogAsset | null
  loading: boolean
  error: string | null

  // Asset actions
  fetchAssets: (params?: {
    search?: string
    asset_type?: string
    source_id?: string
  }) => Promise<void>
  fetchAsset: (id: string) => Promise<void>
  createAsset: (data: AssetCreate) => Promise<CatalogAsset>
  updateAsset: (id: string, data: AssetUpdate) => Promise<CatalogAsset>
  deleteAsset: (id: string) => Promise<void>
  clearSelectedAsset: () => void

  // Column-Term mapping
  mapColumnToTerm: (columnId: string, termId: string) => Promise<void>
  unmapColumnFromTerm: (columnId: string) => Promise<void>

  // Utility
  clearError: () => void
}

export const useCatalogStore = create<CatalogState>((set, get) => ({
  assets: [],
  selectedAsset: null,
  loading: false,
  error: null,

  fetchAssets: async (params) => {
    set({ loading: true, error: null })
    try {
      const assets = await getAssets(params)
      set({ assets, loading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch assets'
      set({ error: message, loading: false })
    }
  },

  fetchAsset: async (id) => {
    set({ loading: true, error: null })
    try {
      const asset = await getAsset(id)
      set({ selectedAsset: asset, loading: false })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch asset'
      set({ error: message, loading: false })
    }
  },

  createAsset: async (data) => {
    set({ loading: true, error: null })
    try {
      const asset = await apiCreateAsset(data)
      // Refetch assets list to get updated list view data
      await get().fetchAssets()
      set({ loading: false })
      return asset
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to create asset'
      set({ error: message, loading: false })
      throw err
    }
  },

  updateAsset: async (id, data) => {
    set({ loading: true, error: null })
    try {
      const asset = await apiUpdateAsset(id, data)
      set((state) => ({
        assets: state.assets.map((a) =>
          a.id === id
            ? {
                ...a,
                name: asset.name,
                asset_type: asset.asset_type,
                source_id: asset.source_id,
                quality_score: asset.quality_score,
                updated_at: asset.updated_at,
              }
            : a
        ),
        selectedAsset: state.selectedAsset?.id === id ? asset : state.selectedAsset,
        loading: false,
      }))
      return asset
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update asset'
      set({ error: message, loading: false })
      throw err
    }
  },

  deleteAsset: async (id) => {
    set({ loading: true, error: null })
    try {
      await apiDeleteAsset(id)
      set((state) => ({
        assets: state.assets.filter((a) => a.id !== id),
        selectedAsset: state.selectedAsset?.id === id ? null : state.selectedAsset,
        loading: false,
      }))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete asset'
      set({ error: message, loading: false })
      throw err
    }
  },

  clearSelectedAsset: () => set({ selectedAsset: null }),

  mapColumnToTerm: async (columnId, termId) => {
    try {
      const updatedColumn = await apiMapColumnToTerm(columnId, termId)
      set((state) => {
        if (!state.selectedAsset) return state
        return {
          selectedAsset: {
            ...state.selectedAsset,
            columns: state.selectedAsset.columns.map((c) =>
              c.id === columnId ? updatedColumn : c
            ),
          },
        }
      })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to map column to term'
      set({ error: message })
      throw err
    }
  },

  unmapColumnFromTerm: async (columnId) => {
    try {
      const updatedColumn = await apiUnmapColumnFromTerm(columnId)
      set((state) => {
        if (!state.selectedAsset) return state
        return {
          selectedAsset: {
            ...state.selectedAsset,
            columns: state.selectedAsset.columns.map((c) =>
              c.id === columnId ? updatedColumn : c
            ),
          },
        }
      })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to unmap column from term'
      set({ error: message })
      throw err
    }
  },

  clearError: () => set({ error: null }),
}))
