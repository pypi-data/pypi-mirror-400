import { useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useIntlayer } from '@/providers'
import {
  BookOpen,
  ArrowLeft,
  Edit,
  Link2,
  History,
  MessageSquare,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useGlossaryStore } from '@/stores/glossaryStore'
import { getTermHistory, getTermRelationships, type TermHistory, type TermRelationship } from '@/api/client'
import { formatDate } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'
import { Comments } from '@/components/collaboration/Comments'
import { useState } from 'react'

export default function GlossaryDetail() {
  const { id } = useParams<{ id: string }>()
  const glossary = useIntlayer('glossary')
  const common = useIntlayer('common')
  const {
    selectedTerm,
    loading,
    fetchTerm,
    fetchCategories,
    clearSelectedTerm,
  } = useGlossaryStore()
  const { toast } = useToast()

  const [history, setHistory] = useState<TermHistory[]>([])
  const [relationships, setRelationships] = useState<TermRelationship[]>([])
  const [, setLoadingExtra] = useState(false)

  const loadData = useCallback(async () => {
    if (!id) return
    try {
      await Promise.all([fetchTerm(id), fetchCategories()])

      setLoadingExtra(true)
      const [historyData, relationshipsData] = await Promise.all([
        getTermHistory(id),
        getTermRelationships(id),
      ])
      setHistory(historyData)
      setRelationships(relationshipsData)
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to load term details',
        variant: 'destructive',
      })
    } finally {
      setLoadingExtra(false)
    }
  }, [id, fetchTerm, fetchCategories, toast])

  useEffect(() => {
    loadData()
    return () => clearSelectedTerm()
  }, [loadData, clearSelectedTerm])

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'approved':
        return 'success'
      case 'deprecated':
        return 'destructive'
      default:
        return 'secondary'
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'approved':
        return glossary.status.approved
      case 'deprecated':
        return glossary.status.deprecated
      default:
        return glossary.status.draft
    }
  }

  if (loading || !selectedTerm) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  const synonyms = relationships.filter((r) => r.relationship_type === 'synonym')
  const relatedTerms = relationships.filter((r) => r.relationship_type === 'related')

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        to="/glossary"
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        {common.back}
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-lg bg-primary/10 flex items-center justify-center">
            <BookOpen className="h-7 w-7 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">{selectedTerm.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant={getStatusBadgeVariant(selectedTerm.status)}>
                {getStatusLabel(selectedTerm.status)}
              </Badge>
              {selectedTerm.category && (
                <Badge variant="outline">{selectedTerm.category.name}</Badge>
              )}
            </div>
          </div>
        </div>

        <Button variant="outline" asChild>
          <Link to={`/glossary/${id}/edit`}>
            <Edit className="mr-2 h-4 w-4" />
            {common.edit}
          </Link>
        </Button>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">{glossary.tabs.overview}</TabsTrigger>
          <TabsTrigger value="relationships">{glossary.tabs.relationships}</TabsTrigger>
          <TabsTrigger value="history">{glossary.tabs.history}</TabsTrigger>
          <TabsTrigger value="comments">{glossary.tabs.comments}</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{glossary.definition}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{selectedTerm.definition}</p>
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">{glossary.category}</CardTitle>
              </CardHeader>
              <CardContent>
                <p>{selectedTerm.category?.name || glossary.noCategory}</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">{glossary.owner}</CardTitle>
              </CardHeader>
              <CardContent>
                <p>{selectedTerm.owner_id || '-'}</p>
              </CardContent>
            </Card>
          </div>

          {/* Quick Relationships */}
          {(synonyms.length > 0 || relatedTerms.length > 0) && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Link2 className="h-5 w-5" />
                  {glossary.relationships}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {synonyms.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">{glossary.synonyms}</h4>
                    <div className="flex flex-wrap gap-2">
                      {synonyms.map((r) => (
                        <Link key={r.id} to={`/glossary/${r.target_term.id}`}>
                          <Badge variant="outline" className="cursor-pointer hover:bg-accent">
                            {r.target_term.name}
                          </Badge>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
                {relatedTerms.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">{glossary.relatedTerms}</h4>
                    <div className="flex flex-wrap gap-2">
                      {relatedTerms.map((r) => (
                        <Link key={r.id} to={`/glossary/${r.target_term.id}`}>
                          <Badge variant="outline" className="cursor-pointer hover:bg-accent">
                            {r.target_term.name}
                          </Badge>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Relationships Tab */}
        <TabsContent value="relationships" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Link2 className="h-5 w-5" />
                {glossary.synonyms}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {synonyms.length === 0 ? (
                <p className="text-muted-foreground text-sm">-</p>
              ) : (
                <div className="space-y-2">
                  {synonyms.map((r) => (
                    <Link
                      key={r.id}
                      to={`/glossary/${r.target_term.id}`}
                      className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent transition-colors"
                    >
                      <div>
                        <p className="font-medium">{r.target_term.name}</p>
                        <p className="text-sm text-muted-foreground line-clamp-1">
                          {r.target_term.definition}
                        </p>
                      </div>
                      <Badge variant="secondary">
                        {glossary.relationshipTypes.synonym}
                      </Badge>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Link2 className="h-5 w-5" />
                {glossary.relatedTerms}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {relatedTerms.length === 0 ? (
                <p className="text-muted-foreground text-sm">-</p>
              ) : (
                <div className="space-y-2">
                  {relatedTerms.map((r) => (
                    <Link
                      key={r.id}
                      to={`/glossary/${r.target_term.id}`}
                      className="flex items-center justify-between p-3 rounded-lg border hover:bg-accent transition-colors"
                    >
                      <div>
                        <p className="font-medium">{r.target_term.name}</p>
                        <p className="text-sm text-muted-foreground line-clamp-1">
                          {r.target_term.definition}
                        </p>
                      </div>
                      <Badge variant="secondary">
                        {glossary.relationshipTypes.related}
                      </Badge>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                {glossary.history}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {history.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  {glossary.noHistory}
                </p>
              ) : (
                <div className="space-y-3">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-start gap-4 p-3 rounded-lg border"
                    >
                      <div className="flex-1">
                        <p className="font-medium">
                          {item.field_name} updated
                        </p>
                        <div className="text-sm text-muted-foreground mt-1">
                          <span>{glossary.changedFrom}: {item.old_value || '-'}</span>
                          <span className="mx-2">→</span>
                          <span>{glossary.changedTo}: {item.new_value || '-'}</span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          {glossary.changedBy}: {item.changed_by} · {formatDate(item.changed_at)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Comments Tab */}
        <TabsContent value="comments">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                {glossary.tabs.comments}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Comments resourceType="term" resourceId={id!} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
