/**
 * Glossary factory tests
 */

import { describe, it, expect } from 'vitest'
import {
  createGlossaryTerm,
  createGlossaryCategory,
  createTermRelationship,
  createTermHistory,
  createDiverseTerms,
  createDiverseCategories,
} from './glossary'

describe('Glossary Factory', () => {
  describe('createGlossaryTerm', () => {
    it('creates a term with default values', () => {
      const term = createGlossaryTerm()

      expect(term).toHaveProperty('id')
      expect(term).toHaveProperty('name')
      expect(term).toHaveProperty('definition')
      expect(term).toHaveProperty('status')
      expect(term).toHaveProperty('created_at')
      expect(term).toHaveProperty('updated_at')
      expect(['draft', 'approved', 'deprecated']).toContain(term.status)
    })

    it('creates a term with custom values', () => {
      const term = createGlossaryTerm({
        name: 'Custom Term',
        definition: 'Custom definition',
        status: 'approved',
      })

      expect(term.name).toBe('Custom Term')
      expect(term.definition).toBe('Custom definition')
      expect(term.status).toBe('approved')
    })

    it('creates a term with category', () => {
      const categoryId = 'cat-123'
      const term = createGlossaryTerm({ categoryId })

      expect(term.category_id).toBe(categoryId)
    })
  })

  describe('createGlossaryCategory', () => {
    it('creates a category with default values', () => {
      const category = createGlossaryCategory()

      expect(category).toHaveProperty('id')
      expect(category).toHaveProperty('name')
      expect(category).toHaveProperty('created_at')
      expect(category).toHaveProperty('updated_at')
    })

    it('creates a category with custom values', () => {
      const category = createGlossaryCategory({
        name: 'Finance',
        description: 'Financial terms',
      })

      expect(category.name).toBe('Finance')
      expect(category.description).toBe('Financial terms')
    })

    it('creates a category with parent', () => {
      const parentId = 'parent-123'
      const category = createGlossaryCategory({ parentId })

      expect(category.parent_id).toBe(parentId)
    })
  })

  describe('createTermRelationship', () => {
    it('creates a relationship between terms', () => {
      const sourceTermId = 'term-1'
      const targetTermId = 'term-2'

      const relationship = createTermRelationship({
        sourceTermId,
        targetTermId,
        relationshipType: 'synonym',
      })

      expect(relationship.source_term_id).toBe(sourceTermId)
      expect(relationship.target_term_id).toBe(targetTermId)
      expect(relationship.relationship_type).toBe('synonym')
    })

    it('creates relationship with default type', () => {
      const relationship = createTermRelationship()

      expect(['synonym', 'related', 'parent', 'child']).toContain(
        relationship.relationship_type
      )
    })
  })

  describe('createTermHistory', () => {
    it('creates history entry for a term', () => {
      const termId = 'term-123'

      const history = createTermHistory({ termId })

      expect(history.term_id).toBe(termId)
      expect(history).toHaveProperty('field_name')
      expect(history).toHaveProperty('old_value')
      expect(history).toHaveProperty('new_value')
      expect(history).toHaveProperty('changed_at')
    })
  })

  describe('createDiverseTerms', () => {
    it('creates multiple diverse terms', () => {
      const categories = [
        createGlossaryCategory({ name: 'Cat 1' }),
        createGlossaryCategory({ name: 'Cat 2' }),
      ]

      const terms = createDiverseTerms(categories)

      expect(terms.length).toBeGreaterThan(0)
      // Should have terms with different statuses
      const statuses = new Set(terms.map((t) => t.status))
      expect(statuses.size).toBeGreaterThanOrEqual(2)
    })
  })

  describe('createDiverseCategories', () => {
    it('creates multiple diverse categories', () => {
      const categories = createDiverseCategories()

      expect(categories.length).toBeGreaterThan(0)
      // Each category should have unique name
      const names = categories.map((c) => c.name)
      const uniqueNames = new Set(names)
      expect(uniqueNames.size).toBe(names.length)
    })
  })
})
