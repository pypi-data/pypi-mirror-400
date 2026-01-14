/**
 * Glossary API handlers
 */

import { http, HttpResponse, delay } from 'msw'
import type { GlossaryTerm, TermHistory } from '@/api/client'
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

export const glossaryHandlers = [
  // ========== Terms ==========

  // List terms
  http.get(`${API_BASE}/glossary/terms`, async ({ request }) => {
    await delay(200)

    const url = new URL(request.url)
    const search = url.searchParams.get('search')
    const categoryId = url.searchParams.get('category_id')
    const status = url.searchParams.get('status')
    const skip = parseInt(url.searchParams.get('skip') ?? '0')
    const limit = parseInt(url.searchParams.get('limit') ?? '50')

    let terms = getAll(getStore().glossaryTerms)

    // Apply filters
    if (search) {
      const searchLower = search.toLowerCase()
      terms = terms.filter(
        (t) =>
          t.name.toLowerCase().includes(searchLower) ||
          t.definition.toLowerCase().includes(searchLower)
      )
    }
    if (categoryId) {
      terms = terms.filter((t) => t.category_id === categoryId)
    }
    if (status) {
      terms = terms.filter((t) => t.status === status)
    }

    // Sort by name
    terms.sort((a, b) => a.name.localeCompare(b.name))

    // Enrich with category
    const enrichedTerms = terms.map((term) => ({
      ...term,
      category: term.category_id
        ? getById(getStore().glossaryCategories, term.category_id)
        : undefined,
    }))

    // Paginate
    const paginated = enrichedTerms.slice(skip, skip + limit)

    return HttpResponse.json(paginated)
  }),

  // Get term by ID
  http.get(`${API_BASE}/glossary/terms/:id`, async ({ params }) => {
    await delay(150)

    const term = getById(getStore().glossaryTerms, params.id as string)

    if (!term) {
      return HttpResponse.json({ detail: 'Term not found' }, { status: 404 })
    }

    // Enrich with category and relationships
    const relationships = getAll(getStore().termRelationships).filter(
      (r) => r.source_term_id === term.id || r.target_term_id === term.id
    )

    const synonyms = relationships
      .filter((r) => r.relationship_type === 'synonym' && r.source_term_id === term.id)
      .map((r) => r.target_term)

    const relatedTerms = relationships
      .filter((r) => r.relationship_type === 'related' && r.source_term_id === term.id)
      .map((r) => r.target_term)

    const enrichedTerm = {
      ...term,
      category: term.category_id
        ? getById(getStore().glossaryCategories, term.category_id)
        : undefined,
      synonyms,
      related_terms: relatedTerms,
    }

    return HttpResponse.json(enrichedTerm)
  }),

  // Create term
  http.post(`${API_BASE}/glossary/terms`, async ({ request }) => {
    await delay(300)

    let body: {
      name: string
      definition: string
      category_id?: string
      status?: string
      owner_id?: string
    }

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const now = new Date().toISOString()
    const newTerm: GlossaryTerm = {
      id: createId(),
      name: body.name,
      definition: body.definition,
      category_id: body.category_id,
      status: (body.status ?? 'draft') as 'draft' | 'approved' | 'deprecated',
      owner_id: body.owner_id,
      created_at: now,
      updated_at: now,
      synonyms: [],
      related_terms: [],
    }

    create(getStore().glossaryTerms, newTerm)

    return HttpResponse.json(newTerm, { status: 201 })
  }),

  // Update term
  http.put(`${API_BASE}/glossary/terms/:id`, async ({ params, request }) => {
    await delay(250)

    let body: Partial<{
      name: string
      definition: string
      category_id: string
      status: 'draft' | 'approved' | 'deprecated'
      owner_id: string
    }>

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const existing = getById(getStore().glossaryTerms, params.id as string)
    if (!existing) {
      return HttpResponse.json({ detail: 'Term not found' }, { status: 404 })
    }

    // Record history for changed fields
    const now = new Date().toISOString()
    Object.entries(body).forEach(([field, newValue]) => {
      const oldValue = existing[field as keyof typeof existing]
      if (oldValue !== newValue) {
        const historyEntry: TermHistory = {
          id: createId(),
          term_id: params.id as string,
          field_name: field,
          old_value: oldValue?.toString() ?? '',
          new_value: newValue?.toString() ?? '',
          changed_by: 'current_user',
          changed_at: now,
        }
        create(getStore().termHistory, historyEntry)
      }
    })

    const updated = update(getStore().glossaryTerms, params.id as string, body)

    return HttpResponse.json({
      ...updated,
      synonyms: [],
      related_terms: [],
    })
  }),

  // Delete term
  http.delete(`${API_BASE}/glossary/terms/:id`, async ({ params }) => {
    await delay(200)

    const deleted = remove(getStore().glossaryTerms, params.id as string)

    if (!deleted) {
      return HttpResponse.json({ detail: 'Term not found' }, { status: 404 })
    }

    // Clean up relationships
    const relationships = getAll(getStore().termRelationships)
    relationships.forEach((r) => {
      if (r.source_term_id === params.id || r.target_term_id === params.id) {
        remove(getStore().termRelationships, r.id)
      }
    })

    return HttpResponse.json({ ok: true })
  }),

  // Get term history
  http.get(`${API_BASE}/glossary/terms/:id/history`, async ({ params }) => {
    await delay(150)

    const history = getAll(getStore().termHistory)
      .filter((h) => h.term_id === params.id)
      .sort((a, b) => new Date(b.changed_at).getTime() - new Date(a.changed_at).getTime())

    return HttpResponse.json(history)
  }),

  // Get term relationships
  http.get(`${API_BASE}/glossary/terms/:id/relationships`, async ({ params }) => {
    await delay(150)

    const relationships = getAll(getStore().termRelationships).filter(
      (r) => r.source_term_id === params.id || r.target_term_id === params.id
    )

    return HttpResponse.json(relationships)
  }),

  // ========== Categories ==========

  // List categories
  http.get(`${API_BASE}/glossary/categories`, async () => {
    await delay(150)

    const categories = getAll(getStore().glossaryCategories)
      .filter((c) => !c.parent_id) // Only root categories
      .sort((a, b) => a.name.localeCompare(b.name))

    return HttpResponse.json(categories)
  }),

  // Create category
  http.post(`${API_BASE}/glossary/categories`, async ({ request }) => {
    await delay(250)

    let body: {
      name: string
      description?: string
      parent_id?: string
    }

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const now = new Date().toISOString()
    const newCategory = {
      id: createId(),
      name: body.name,
      description: body.description,
      parent_id: body.parent_id,
      created_at: now,
      updated_at: now,
      children: [],
    }

    create(getStore().glossaryCategories, newCategory)

    return HttpResponse.json(newCategory, { status: 201 })
  }),

  // Update category
  http.put(`${API_BASE}/glossary/categories/:id`, async ({ params, request }) => {
    await delay(200)

    let body: Partial<{
      name: string
      description: string
      parent_id: string
    }>

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const updated = update(getStore().glossaryCategories, params.id as string, body)

    if (!updated) {
      return HttpResponse.json({ detail: 'Category not found' }, { status: 404 })
    }

    return HttpResponse.json(updated)
  }),

  // Delete category
  http.delete(`${API_BASE}/glossary/categories/:id`, async ({ params }) => {
    await delay(200)

    // Unlink terms from this category
    const terms = getAll(getStore().glossaryTerms)
    terms.forEach((term) => {
      if (term.category_id === params.id) {
        update(getStore().glossaryTerms, term.id, { category_id: undefined })
      }
    })

    const deleted = remove(getStore().glossaryCategories, params.id as string)

    if (!deleted) {
      return HttpResponse.json({ detail: 'Category not found' }, { status: 404 })
    }

    return HttpResponse.json({ ok: true })
  }),

  // ========== Relationships ==========

  // Create relationship
  http.post(`${API_BASE}/glossary/relationships`, async ({ request }) => {
    await delay(200)

    let body: {
      source_term_id: string
      target_term_id: string
      relationship_type: string
    }

    try {
      body = (await request.json()) as typeof body
    } catch {
      return HttpResponse.json({ detail: 'Invalid JSON' }, { status: 400 })
    }

    const sourceTerm = getById(getStore().glossaryTerms, body.source_term_id)
    const targetTerm = getById(getStore().glossaryTerms, body.target_term_id)

    if (!sourceTerm || !targetTerm) {
      return HttpResponse.json({ detail: 'Term not found' }, { status: 404 })
    }

    const newRelationship = {
      id: createId(),
      source_term_id: body.source_term_id,
      target_term_id: body.target_term_id,
      relationship_type: body.relationship_type,
      created_at: new Date().toISOString(),
      source_term: {
        id: sourceTerm.id,
        name: sourceTerm.name,
        definition: sourceTerm.definition,
      },
      target_term: {
        id: targetTerm.id,
        name: targetTerm.name,
        definition: targetTerm.definition,
      },
    }

    create(getStore().termRelationships, newRelationship)

    return HttpResponse.json(newRelationship, { status: 201 })
  }),

  // Delete relationship
  http.delete(`${API_BASE}/glossary/relationships/:id`, async ({ params }) => {
    await delay(150)

    const deleted = remove(getStore().termRelationships, params.id as string)

    if (!deleted) {
      return HttpResponse.json({ detail: 'Relationship not found' }, { status: 404 })
    }

    return HttpResponse.json({ ok: true })
  }),
]
