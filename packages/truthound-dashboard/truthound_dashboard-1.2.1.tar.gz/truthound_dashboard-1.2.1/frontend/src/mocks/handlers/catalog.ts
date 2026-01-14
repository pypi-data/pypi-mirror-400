/**
 * Catalog API handlers
 */

import { http, HttpResponse, delay } from 'msw'
import type { CatalogAsset, AssetColumn, AssetType, SensitivityLevel } from '@/api/client'
import {
  getStore,
  getAll,
  getById,
  create,
  update,
  remove,
} from '../data/store'
import { createId } from '../factories'

const API_BASE = '/api/v1'

export const catalogHandlers = [
  // ========== Assets ==========

  // List assets
  http.get(`${API_BASE}/catalog/assets`, async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const assetType = url.searchParams.get('asset_type')
    const sourceId = url.searchParams.get('source_id')
    const skip = parseInt(url.searchParams.get('skip') ?? '0')
    const limit = parseInt(url.searchParams.get('limit') ?? '50')

    let assets = getAll(getStore().catalogAssets)

    // Apply filters
    if (search) {
      const searchLower = search.toLowerCase()
      assets = assets.filter(
        (a) =>
          a.name.toLowerCase().includes(searchLower) ||
          a.description?.toLowerCase().includes(searchLower)
      )
    }
    if (assetType) {
      assets = assets.filter((a) => a.asset_type === assetType)
    }
    if (sourceId) {
      assets = assets.filter((a) => a.source_id === sourceId)
    }

    // Sort by updated_at desc
    assets.sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())

    // Transform to list items
    const listItems = assets.map((asset) => {
      const columns = getAll(getStore().assetColumns).filter((c) => c.asset_id === asset.id)
      const tags = getAll(getStore().assetTags).filter((t) => t.asset_id === asset.id)
      const source = asset.source_id ? getById(getStore().sources, asset.source_id) : undefined

      return {
        id: asset.id,
        name: asset.name,
        asset_type: asset.asset_type,
        source_id: asset.source_id,
        source_name: source?.name,
        quality_score: asset.quality_score,
        tag_count: tags.length,
        column_count: columns.length,
        updated_at: asset.updated_at,
      }
    })

    // Paginate
    const paginated = listItems.slice(skip, skip + limit)

    return HttpResponse.json(paginated)
  }),

  // Get asset by ID
  http.get(`${API_BASE}/catalog/assets/:id`, async ({ params }) => {
    await delay(150)

    const asset = getById(getStore().catalogAssets, params.id as string)

    if (!asset) {
      return HttpResponse.json({ detail: 'Asset not found' }, { status: 404 })
    }

    // Get columns with term info
    const columns = getAll(getStore().assetColumns)
      .filter((c) => c.asset_id === asset.id)
      .map((col) => ({
        ...col,
        term: col.term_id
          ? (() => {
              const term = getById(getStore().glossaryTerms, col.term_id)
              return term
                ? { id: term.id, name: term.name, definition: term.definition }
                : undefined
            })()
          : undefined,
      }))

    // Get tags
    const tags = getAll(getStore().assetTags).filter((t) => t.asset_id === asset.id)

    // Get source info
    const source = asset.source_id ? getById(getStore().sources, asset.source_id) : undefined

    const enrichedAsset = {
      ...asset,
      columns,
      tags,
      source: source
        ? { id: source.id, name: source.name, type: source.type }
        : undefined,
    }

    return HttpResponse.json(enrichedAsset)
  }),

  // Create asset
  http.post(`${API_BASE}/catalog/assets`, async ({ request }) => {
    await delay(300)

    let body: {
      name: string
      asset_type: string
      source_id?: string
      description?: string
      owner_id?: string
    }

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const now = new Date().toISOString()
    const newAsset: CatalogAsset = {
      id: createId(),
      name: body.name,
      asset_type: body.asset_type as AssetType,
      source_id: body.source_id,
      description: body.description,
      owner_id: body.owner_id,
      quality_score: undefined,
      created_at: now,
      updated_at: now,
      columns: [],
      tags: [],
    }

    create(getStore().catalogAssets, newAsset)

    // Get source info
    const source = body.source_id ? getById(getStore().sources, body.source_id) : undefined

    return HttpResponse.json(
      {
        ...newAsset,
        columns: [],
        tags: [],
        source: source
          ? { id: source.id, name: source.name, type: source.type }
          : undefined,
      },
      { status: 201 }
    )
  }),

  // Update asset
  http.put(`${API_BASE}/catalog/assets/:id`, async ({ params, request }) => {
    await delay(250)

    let body: Partial<{
      name: string
      asset_type: AssetType
      source_id: string
      description: string
      owner_id: string
      quality_score: number
    }>

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const updated = update(getStore().catalogAssets, params.id as string, body)

    if (!updated) {
      return HttpResponse.json({ detail: 'Asset not found' }, { status: 404 })
    }

    // Get enriched data
    const columns = getAll(getStore().assetColumns).filter((c) => c.asset_id === updated.id)
    const tags = getAll(getStore().assetTags).filter((t) => t.asset_id === updated.id)
    const source = updated.source_id ? getById(getStore().sources, updated.source_id) : undefined

    return HttpResponse.json({
      ...updated,
      columns,
      tags,
      source: source
        ? { id: source.id, name: source.name, type: source.type }
        : undefined,
    })
  }),

  // Delete asset
  http.delete(`${API_BASE}/catalog/assets/:id`, async ({ params }) => {
    await delay(200)

    const deleted = remove(getStore().catalogAssets, params.id as string)

    if (!deleted) {
      return HttpResponse.json({ detail: 'Asset not found' }, { status: 404 })
    }

    // Clean up columns and tags
    getAll(getStore().assetColumns)
      .filter((c) => c.asset_id === params.id)
      .forEach((c) => remove(getStore().assetColumns, c.id))

    getAll(getStore().assetTags)
      .filter((t) => t.asset_id === params.id)
      .forEach((t) => remove(getStore().assetTags, t.id))

    return HttpResponse.json({ ok: true })
  }),

  // ========== Columns ==========

  // List columns for asset
  http.get(`${API_BASE}/catalog/assets/:assetId/columns`, async ({ params }) => {
    await delay(150)

    const columns = getAll(getStore().assetColumns)
      .filter((c) => c.asset_id === params.assetId)
      .map((col) => ({
        ...col,
        term: col.term_id
          ? (() => {
              const term = getById(getStore().glossaryTerms, col.term_id)
              return term
                ? { id: term.id, name: term.name, definition: term.definition }
                : undefined
            })()
          : undefined,
      }))

    return HttpResponse.json(columns)
  }),

  // Create column
  http.post(`${API_BASE}/catalog/assets/:assetId/columns`, async ({ params, request }) => {
    await delay(200)

    let body: {
      name: string
      data_type?: string
      description?: string
      is_nullable?: boolean
      is_primary_key?: boolean
      sensitivity_level?: string
    }

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const newColumn: AssetColumn = {
      id: createId(),
      asset_id: params.assetId as string,
      name: body.name,
      data_type: body.data_type,
      description: body.description,
      is_nullable: body.is_nullable ?? true,
      is_primary_key: body.is_primary_key ?? false,
      term_id: undefined,
      sensitivity_level: body.sensitivity_level as SensitivityLevel | undefined,
      created_at: new Date().toISOString(),
    }

    create(getStore().assetColumns, newColumn)

    return HttpResponse.json(newColumn, { status: 201 })
  }),

  // Update column
  http.put(`${API_BASE}/catalog/columns/:id`, async ({ params, request }) => {
    await delay(200)

    let body: Partial<{
      name: string
      data_type: string
      description: string
      is_nullable: boolean
      is_primary_key: boolean
      sensitivity_level: SensitivityLevel
    }>

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const updated = update(getStore().assetColumns, params.id as string, body)

    if (!updated) {
      return HttpResponse.json({ detail: 'Column not found' }, { status: 404 })
    }

    return HttpResponse.json(updated)
  }),

  // Delete column
  http.delete(`${API_BASE}/catalog/columns/:id`, async ({ params }) => {
    await delay(150)

    const deleted = remove(getStore().assetColumns, params.id as string)

    if (!deleted) {
      return HttpResponse.json({ detail: 'Column not found' }, { status: 404 })
    }

    return HttpResponse.json({ ok: true })
  }),

  // Map column to term
  http.put(`${API_BASE}/catalog/columns/:id/term`, async ({ params, request }) => {
    await delay(200)

    let body: { term_id: string }

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const term = getById(getStore().glossaryTerms, body.term_id)
    if (!term) {
      return HttpResponse.json({ detail: 'Term not found' }, { status: 404 })
    }

    const updated = update(getStore().assetColumns, params.id as string, {
      term_id: body.term_id,
    })

    if (!updated) {
      return HttpResponse.json({ detail: 'Column not found' }, { status: 404 })
    }

    return HttpResponse.json({
      ...updated,
      term: { id: term.id, name: term.name, definition: term.definition },
    })
  }),

  // Unmap column from term
  http.delete(`${API_BASE}/catalog/columns/:id/term`, async ({ params }) => {
    await delay(150)

    const updated = update(getStore().assetColumns, params.id as string, {
      term_id: undefined,
    })

    if (!updated) {
      return HttpResponse.json({ detail: 'Column not found' }, { status: 404 })
    }

    return HttpResponse.json({ ...updated, term: undefined })
  }),

  // ========== Tags ==========

  // List tags for asset
  http.get(`${API_BASE}/catalog/assets/:assetId/tags`, async ({ params }) => {
    await delay(100)

    const tags = getAll(getStore().assetTags).filter((t) => t.asset_id === params.assetId)

    return HttpResponse.json(tags)
  }),

  // Add tag
  http.post(`${API_BASE}/catalog/assets/:assetId/tags`, async ({ params, request }) => {
    await delay(150)

    let body: {
      tag_name: string
      tag_value?: string
    }

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const newTag = {
      id: createId(),
      asset_id: params.assetId as string,
      tag_name: body.tag_name,
      tag_value: body.tag_value,
      created_at: new Date().toISOString(),
    }

    create(getStore().assetTags, newTag)

    return HttpResponse.json(newTag, { status: 201 })
  }),

  // Remove tag
  http.delete(`${API_BASE}/catalog/tags/:id`, async ({ params }) => {
    await delay(100)

    const deleted = remove(getStore().assetTags, params.id as string)

    if (!deleted) {
      return HttpResponse.json({ detail: 'Tag not found' }, { status: 404 })
    }

    return HttpResponse.json({ ok: true })
  }),
]
