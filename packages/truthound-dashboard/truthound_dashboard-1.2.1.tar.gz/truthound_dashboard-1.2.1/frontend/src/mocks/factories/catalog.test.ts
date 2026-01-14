/**
 * Catalog factory tests
 */

import { describe, it, expect } from 'vitest'
import {
  createCatalogAsset,
  createAssetColumn,
  createAssetTag,
  createAssetListItem,
  createDiverseAssets,
} from './catalog'

describe('Catalog Factory', () => {
  describe('createCatalogAsset', () => {
    it('creates an asset with default values', () => {
      const asset = createCatalogAsset()

      expect(asset).toHaveProperty('id')
      expect(asset).toHaveProperty('name')
      expect(asset).toHaveProperty('asset_type')
      expect(asset).toHaveProperty('created_at')
      expect(asset).toHaveProperty('updated_at')
      expect(['table', 'file', 'api']).toContain(asset.asset_type)
    })

    it('creates an asset with custom values', () => {
      const asset = createCatalogAsset({
        name: 'customers',
        assetType: 'table',
        description: 'Customer data',
      })

      expect(asset.name).toBe('customers')
      expect(asset.asset_type).toBe('table')
      expect(asset.description).toBe('Customer data')
    })

    it('creates an asset with source', () => {
      const sourceId = 'src-123'
      const asset = createCatalogAsset({ sourceId })

      expect(asset.source_id).toBe(sourceId)
    })

    it('creates an asset with columns by default', () => {
      const asset = createCatalogAsset()

      expect(asset.columns).toBeDefined()
      expect(Array.isArray(asset.columns)).toBe(true)
      expect(asset.columns.length).toBeGreaterThan(0)
    })

    it('creates an asset without columns when specified', () => {
      const asset = createCatalogAsset({ withColumns: false })

      expect(asset.columns).toEqual([])
    })

    it('creates an asset with tags', () => {
      const asset = createCatalogAsset({ withTags: true })

      expect(asset.tags).toBeDefined()
      expect(Array.isArray(asset.tags)).toBe(true)
    })

    it('creates an asset with quality score', () => {
      const asset = createCatalogAsset({ qualityScore: 85.5 })

      expect(asset.quality_score).toBe(85.5)
    })
  })

  describe('createAssetColumn', () => {
    it('creates a column with default values', () => {
      const column = createAssetColumn()

      expect(column).toHaveProperty('id')
      expect(column).toHaveProperty('name')
      expect(column).toHaveProperty('data_type')
      expect(column).toHaveProperty('is_nullable')
      expect(column).toHaveProperty('is_primary_key')
    })

    it('creates a column with custom values', () => {
      const column = createAssetColumn({
        name: 'user_id',
        dataType: 'uuid',
        isPrimaryKey: true,
        isNullable: false,
      })

      expect(column.name).toBe('user_id')
      expect(column.data_type).toBe('uuid')
      expect(column.is_primary_key).toBe(true)
      expect(column.is_nullable).toBe(false)
    })

    it('creates a column with term mapping', () => {
      const termId = 'term-123'
      const column = createAssetColumn({ termId })

      expect(column.term_id).toBe(termId)
    })

    it('creates a column with sensitivity level', () => {
      const column = createAssetColumn({ sensitivityLevel: 'confidential' })

      expect(column.sensitivity_level).toBe('confidential')
    })
  })

  describe('createAssetTag', () => {
    it('creates a tag with default values', () => {
      const tag = createAssetTag()

      expect(tag).toHaveProperty('id')
      expect(tag).toHaveProperty('tag_name')
      expect(tag).toHaveProperty('created_at')
    })

    it('creates a tag with custom values', () => {
      const tag = createAssetTag({
        tagName: 'pii',
        tagValue: 'true',
      })

      expect(tag.tag_name).toBe('pii')
      expect(tag.tag_value).toBe('true')
    })

    it('creates a tag linked to an asset', () => {
      const assetId = 'asset-123'
      const tag = createAssetTag({ assetId })

      expect(tag.asset_id).toBe(assetId)
    })
  })

  describe('createAssetListItem', () => {
    it('creates a list item from an asset', () => {
      const asset = createCatalogAsset({
        name: 'test_table',
        assetType: 'table',
      })

      const listItem = createAssetListItem(asset)

      expect(listItem.id).toBe(asset.id)
      expect(listItem.name).toBe(asset.name)
      expect(listItem.asset_type).toBe(asset.asset_type)
      expect(listItem.column_count).toBe(asset.columns.length)
      expect(listItem.tag_count).toBe(asset.tags.length)
    })
  })

  describe('createDiverseAssets', () => {
    it('creates multiple diverse assets', () => {
      const sourceIds = ['src-1', 'src-2', 'src-3']
      const assets = createDiverseAssets(sourceIds)

      expect(assets.length).toBeGreaterThan(0)

      // Should have different asset types
      const types = new Set(assets.map((a) => a.asset_type))
      expect(types.size).toBeGreaterThanOrEqual(2)
    })

    it('creates assets with varying quality scores', () => {
      const assets = createDiverseAssets([])

      const scores = assets
        .map((a) => a.quality_score)
        .filter((s) => s !== undefined)

      // Should have some variety in quality scores
      expect(scores.length).toBeGreaterThan(0)
    })

    it('links assets to provided sources', () => {
      const sourceIds = ['src-1', 'src-2']
      const assets = createDiverseAssets(sourceIds)

      const linkedAssets = assets.filter((a) => a.source_id)
      expect(linkedAssets.length).toBeGreaterThan(0)

      // All linked source IDs should be from provided list
      linkedAssets.forEach((asset) => {
        expect(sourceIds).toContain(asset.source_id)
      })
    })
  })
})
