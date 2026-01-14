import { useEffect, useCallback, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useIntlayer } from '@/providers'
import {
  ArrowLeft,
  Edit,
  Table,
  Tag,
  MessageSquare,
  FileText,
  Globe,
  Link2,
  Shield,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useCatalogStore } from '@/stores/catalogStore'
import { useGlossaryStore } from '@/stores/glossaryStore'
import { useToast } from '@/hooks/use-toast'
import { str } from '@/lib/intlayer-utils'
import { Comments } from '@/components/collaboration/Comments'
import { ColumnMappingDialog } from '@/components/catalog/ColumnMappingDialog'

export default function CatalogDetail() {
  const { id } = useParams<{ id: string }>()
  const catalog = useIntlayer('catalog')
  const common = useIntlayer('common')
  const {
    selectedAsset,
    loading,
    fetchAsset,
    clearSelectedAsset,
    mapColumnToTerm,
    unmapColumnFromTerm,
  } = useCatalogStore()
  const { terms, fetchTerms } = useGlossaryStore()
  const { toast } = useToast()

  const [mappingDialogOpen, setMappingDialogOpen] = useState(false)
  const [selectedColumnId, setSelectedColumnId] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    if (!id) return
    try {
      await Promise.all([fetchAsset(id), fetchTerms()])
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to load asset details',
        variant: 'destructive',
      })
    }
  }, [id, fetchAsset, fetchTerms, toast])

  useEffect(() => {
    loadData()
    return () => clearSelectedAsset()
  }, [loadData, clearSelectedAsset])

  const getAssetIcon = (type: string) => {
    switch (type) {
      case 'table':
        return Table
      case 'api':
        return Globe
      default:
        return FileText
    }
  }

  const getAssetTypeLabel = (type: string) => {
    switch (type) {
      case 'table':
        return catalog.assetTypes.table
      case 'file':
        return catalog.assetTypes.file
      case 'api':
        return catalog.assetTypes.api
      default:
        return type
    }
  }

  const getSensitivityBadgeVariant = (level?: string) => {
    switch (level) {
      case 'restricted':
        return 'destructive'
      case 'confidential':
        return 'high'
      case 'internal':
        return 'warning'
      default:
        return 'secondary'
    }
  }

  const getSensitivityLabel = (level?: string) => {
    switch (level) {
      case 'restricted':
        return catalog.sensitivity.restricted
      case 'confidential':
        return catalog.sensitivity.confidential
      case 'internal':
        return catalog.sensitivity.internal
      default:
        return catalog.sensitivity.public
    }
  }

  const handleMapColumn = async (columnId: string, termId: string) => {
    try {
      await mapColumnToTerm(columnId, termId)
      toast({
        title: str(common.success),
        description: str(catalog.mappingSuccess),
      })
      setMappingDialogOpen(false)
      setSelectedColumnId(null)
    } catch {
      toast({
        title: str(common.error),
        description: str(catalog.mappingError),
        variant: 'destructive',
      })
    }
  }

  const handleUnmapColumn = async (columnId: string) => {
    try {
      await unmapColumnFromTerm(columnId)
      toast({
        title: str(common.success),
        description: str(catalog.unmappingSuccess),
      })
    } catch {
      toast({
        title: str(common.error),
        description: str(catalog.mappingError),
        variant: 'destructive',
      })
    }
  }

  if (loading || !selectedAsset) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  const Icon = getAssetIcon(selectedAsset.asset_type)

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        to="/catalog"
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        {common.back}
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-lg bg-primary/10 flex items-center justify-center">
            <Icon className="h-7 w-7 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">{selectedAsset.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="outline">
                {getAssetTypeLabel(selectedAsset.asset_type)}
              </Badge>
              {selectedAsset.source && (
                <Badge variant="secondary">{selectedAsset.source.name}</Badge>
              )}
              {selectedAsset.quality_score !== undefined && (
                <Badge
                  variant={
                    selectedAsset.quality_score >= 80
                      ? 'success'
                      : selectedAsset.quality_score >= 60
                      ? 'warning'
                      : 'destructive'
                  }
                >
                  {catalog.qualityScore}: {selectedAsset.quality_score.toFixed(1)}%
                </Badge>
              )}
            </div>
          </div>
        </div>

        <Button variant="outline">
          <Edit className="mr-2 h-4 w-4" />
          {common.edit}
        </Button>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">{catalog.tabs.overview}</TabsTrigger>
          <TabsTrigger value="columns">{catalog.tabs.columns}</TabsTrigger>
          <TabsTrigger value="tags">{catalog.tabs.tags}</TabsTrigger>
          <TabsTrigger value="comments">{catalog.tabs.comments}</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          {selectedAsset.description && (
            <Card>
              <CardHeader>
                <CardTitle>{catalog.description}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{selectedAsset.description}</p>
              </CardContent>
            </Card>
          )}

          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">{catalog.columns}</p>
                <p className="text-2xl font-bold mt-1">{selectedAsset.columns.length}</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">{catalog.tags}</p>
                <p className="text-2xl font-bold mt-1">{selectedAsset.tags.length}</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <p className="text-sm text-muted-foreground">{catalog.owner}</p>
                <p className="text-lg font-medium mt-1">{selectedAsset.owner_id || '-'}</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Columns Tab */}
        <TabsContent value="columns">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Table className="h-5 w-5" />
                {catalog.columns} ({selectedAsset.columns.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedAsset.columns.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  {catalog.noColumns}
                </p>
              ) : (
                <div className="space-y-2">
                  {selectedAsset.columns.map((column) => (
                    <div
                      key={column.id}
                      className="flex items-center justify-between p-4 rounded-lg border"
                    >
                      <div className="flex items-center gap-4">
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-medium">{column.name}</p>
                            {column.is_primary_key && (
                              <Badge variant="outline" className="text-xs">PK</Badge>
                            )}
                            {!column.is_nullable && (
                              <Badge variant="outline" className="text-xs">NOT NULL</Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-sm text-muted-foreground">
                              {column.data_type || 'unknown'}
                            </span>
                            {column.sensitivity_level && (
                              <Badge
                                variant={getSensitivityBadgeVariant(column.sensitivity_level)}
                                className="text-xs"
                              >
                                <Shield className="h-3 w-3 mr-1" />
                                {getSensitivityLabel(column.sensitivity_level)}
                              </Badge>
                            )}
                          </div>
                          {column.description && (
                            <p className="text-sm text-muted-foreground mt-1">
                              {column.description}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        {column.term ? (
                          <div className="flex items-center gap-2">
                            <Link
                              to={`/glossary/${column.term.id}`}
                              className="flex items-center gap-1 text-sm text-primary hover:underline"
                            >
                              <Link2 className="h-3 w-3" />
                              {column.term.name}
                            </Link>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleUnmapColumn(column.id)}
                            >
                              {catalog.unmapTerm}
                            </Button>
                          </div>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedColumnId(column.id)
                              setMappingDialogOpen(true)
                            }}
                          >
                            <Link2 className="h-4 w-4 mr-1" />
                            {catalog.mapToTerm}
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tags Tab */}
        <TabsContent value="tags">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Tag className="h-5 w-5" />
                {catalog.tags} ({selectedAsset.tags.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {selectedAsset.tags.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  {catalog.noTags}
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {selectedAsset.tags.map((tag) => (
                    <Badge key={tag.id} variant="secondary">
                      {tag.tag_name}
                      {tag.tag_value && `: ${tag.tag_value}`}
                    </Badge>
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
                {catalog.tabs.comments}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Comments resourceType="asset" resourceId={id!} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Column Mapping Dialog */}
      <ColumnMappingDialog
        open={mappingDialogOpen}
        onOpenChange={setMappingDialogOpen}
        columnId={selectedColumnId}
        terms={terms}
        onMap={handleMapColumn}
      />
    </div>
  )
}
