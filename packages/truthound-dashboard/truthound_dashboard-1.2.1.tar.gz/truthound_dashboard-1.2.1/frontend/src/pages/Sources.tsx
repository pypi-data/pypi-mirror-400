import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useIntlayer } from '@/providers'
import {
  Database,
  Plus,
  Trash2,
  Play,
  FileText,
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  listSources,
  deleteSource,
  runValidation,
  type Source,
} from '@/api/client'
import { formatDate } from '@/lib/utils'
import { str } from '@/lib/intlayer-utils'
import { useToast } from '@/hooks/use-toast'
import { useConfirm } from '@/components/ConfirmDialog'

export default function Sources() {
  const nav = useIntlayer('nav')
  const sources_t = useIntlayer('sources')
  const common = useIntlayer('common')
  const validation = useIntlayer('validation')
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()
  const { confirm, ConfirmDialog } = useConfirm()

  // Helper to get validation status label
  const getValidationLabel = (status: string | null | undefined) => {
    if (!status) return null
    switch (status) {
      case 'passed': return validation.passed
      case 'success': return validation.success
      case 'failed': return validation.failed
      case 'error': return validation.error
      case 'pending': return validation.pending
      case 'warning': return validation.warning
      default: return status
    }
  }

  const loadSources = useCallback(async () => {
    try {
      setLoading(true)
      const response = await listSources()
      setSources(response.data)
    } catch {
      toast({
        title: str(common.error),
        description: str(sources_t.loadError),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [toast, common, sources_t])

  useEffect(() => {
    loadSources()
  }, [loadSources])

  async function handleDelete(id: string) {
    const confirmed = await confirm({
      title: str(sources_t.deleteSource),
      description: str(sources_t.confirmDelete),
      confirmText: str(common.delete),
      variant: 'destructive',
    })
    if (!confirmed) return

    try {
      await deleteSource(id)
      setSources((prev) => prev.filter((s) => s.id !== id))
      toast({
        title: str(common.success),
        description: str(sources_t.deleteSuccess),
      })
    } catch {
      toast({
        title: str(common.error),
        description: str(sources_t.deleteFailed),
        variant: 'destructive',
      })
    }
  }

  async function handleValidate(id: string) {
    try {
      toast({
        title: str(sources_t.validationStarted),
        description: str(sources_t.runningValidation),
      })
      const result = await runValidation(id, {})
      setSources((prev) =>
        prev.map((s) =>
          s.id === id
            ? { ...s, latest_validation_status: result.status }
            : s
        )
      )
      toast({
        title: str(result.passed ? sources_t.validationPassed : sources_t.validationFailed),
        description: `${result.total_issues} issues found`,
        variant: result.passed ? 'default' : 'destructive',
      })
    } catch {
      toast({
        title: str(common.error),
        description: str(sources_t.validationError),
        variant: 'destructive',
      })
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{nav.sources}</h1>
          <p className="text-muted-foreground">
            {sources_t.subtitle}
          </p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          {sources_t.addSource}
        </Button>
      </div>

      {/* Sources List */}
      {sources.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Database className="h-16 w-16 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-semibold mb-2">{sources_t.noSourcesYet}</h3>
            <p className="text-muted-foreground text-center mb-4">
              {sources_t.noSourcesDesc}
            </p>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              {sources_t.addFirstSource}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {sources.map((source) => (
            <Card key={source.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Database className="h-6 w-6 text-primary" />
                    </div>
                    <div>
                      <Link
                        to={`/sources/${source.id}`}
                        className="font-semibold hover:text-primary transition-colors"
                      >
                        {source.name}
                      </Link>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Badge variant="outline">{source.type}</Badge>
                        <span>•</span>
                        <span>
                          {sources_t.lastValidated}: {formatDate(source.last_validated_at)}
                        </span>
                      </div>
                      {source.description && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {source.description}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {source.latest_validation_status && (
                      <Badge
                        variant={
                          source.latest_validation_status === 'success' || source.latest_validation_status === 'passed'
                            ? 'success'
                            : source.latest_validation_status === 'failed'
                            ? 'destructive'
                            : source.latest_validation_status === 'warning'
                            ? 'warning'
                            : 'secondary'
                        }
                      >
                        {getValidationLabel(source.latest_validation_status)}
                      </Badge>
                    )}

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleValidate(source.id)}
                    >
                      <Play className="mr-2 h-4 w-4" />
                      {sources_t.validate}
                    </Button>

                    <Button variant="ghost" size="icon" asChild>
                      <Link to={`/sources/${source.id}`}>
                        <FileText className="h-4 w-4" />
                      </Link>
                    </Button>

                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(source.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <ConfirmDialog />
    </div>
  )
}
