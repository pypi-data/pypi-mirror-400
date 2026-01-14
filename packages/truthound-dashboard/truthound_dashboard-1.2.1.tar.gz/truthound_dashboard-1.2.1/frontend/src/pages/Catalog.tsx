import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useIntlayer } from '@/providers'
import {
  Database,
  Plus,
  Search,
  Filter,
  Trash2,
  FileText,
  Table,
  Globe,
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useCatalogStore } from '@/stores/catalogStore'
import { listSources, type Source } from '@/api/client'
import { str } from '@/lib/intlayer-utils'
import { useToast } from '@/hooks/use-toast'
import { useConfirm } from '@/components/ConfirmDialog'
import { AssetFormDialog } from '@/components/catalog/AssetFormDialog'

export default function Catalog() {
  const nav = useIntlayer('nav')
  const catalog = useIntlayer('catalog')
  const common = useIntlayer('common')
  const {
    assets,
    loading,
    fetchAssets,
    deleteAsset,
  } = useCatalogStore()
  const { toast } = useToast()
  const { confirm, ConfirmDialog } = useConfirm()

  const [sources, setSources] = useState<Source[]>([])
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [sourceFilter, setSourceFilter] = useState<string>('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingAsset, setEditingAsset] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    await fetchAssets({
      search: search || undefined,
      asset_type: typeFilter || undefined,
      source_id: sourceFilter || undefined,
    })
  }, [fetchAssets, search, typeFilter, sourceFilter])

  useEffect(() => {
    loadData()
    // Load sources for filter
    listSources().then((res) => setSources(res.data))
  }, [loadData])

  const handleDelete = async (id: string) => {
    const confirmed = await confirm({
      title: str(catalog.deleteAsset),
      description: str(catalog.confirmDelete),
      confirmText: str(common.delete),
      variant: 'destructive',
    })
    if (!confirmed) return

    try {
      await deleteAsset(id)
      toast({
        title: str(common.success),
        description: str(catalog.deleteSuccess),
      })
    } catch {
      toast({
        title: str(common.error),
        description: str(catalog.deleteError),
        variant: 'destructive',
      })
    }
  }

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

  const getQualityScoreColor = (score?: number) => {
    if (!score) return 'text-muted-foreground'
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  if (loading && assets.length === 0) {
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
          <h1 className="text-3xl font-bold">{nav.catalog}</h1>
          <p className="text-muted-foreground">{catalog.subtitle}</p>
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          {catalog.addAsset}
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={str(catalog.searchAssets)}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[160px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder={str(catalog.filterByType)} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">{catalog.allTypes}</SelectItem>
            <SelectItem value="table">{catalog.assetTypes.table}</SelectItem>
            <SelectItem value="file">{catalog.assetTypes.file}</SelectItem>
            <SelectItem value="api">{catalog.assetTypes.api}</SelectItem>
          </SelectContent>
        </Select>
        <Select value={sourceFilter} onValueChange={setSourceFilter}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder={str(catalog.filterBySource)} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">{catalog.allSources}</SelectItem>
            {sources.map((source) => (
              <SelectItem key={source.id} value={source.id}>
                {source.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Assets List */}
      {assets.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <Database className="h-16 w-16 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-semibold mb-2">{catalog.noAssetsYet}</h3>
            <p className="text-muted-foreground text-center mb-4">
              {catalog.noAssetsDesc}
            </p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              {catalog.addFirstAsset}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {assets.map((asset) => {
            const Icon = getAssetIcon(asset.asset_type)
            return (
              <Card key={asset.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <Icon className="h-6 w-6 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <Link
                          to={`/catalog/${asset.id}`}
                          className="font-semibold hover:text-primary transition-colors"
                        >
                          {asset.name}
                        </Link>
                        <div className="flex items-center gap-2 mt-1 flex-wrap">
                          <Badge variant="outline">
                            {getAssetTypeLabel(asset.asset_type)}
                          </Badge>
                          {asset.source_name && (
                            <Badge variant="secondary">{asset.source_name}</Badge>
                          )}
                          <span className="text-xs text-muted-foreground">
                            {catalog.columns}: {asset.column_count}
                          </span>
                          {asset.tag_count > 0 && (
                            <span className="text-xs text-muted-foreground">
                              {catalog.tags}: {asset.tag_count}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 ml-4">
                      {asset.quality_score !== undefined && (
                        <div className="text-right">
                          <p className="text-xs text-muted-foreground">{catalog.qualityScore}</p>
                          <p className={`font-semibold ${getQualityScoreColor(asset.quality_score)}`}>
                            {asset.quality_score.toFixed(1)}%
                          </p>
                        </div>
                      )}
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(asset.id)}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Dialogs */}
      <AssetFormDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open)
          if (!open) setEditingAsset(null)
        }}
        assetId={editingAsset}
        sources={sources}
        onSuccess={() => {
          loadData()
          setDialogOpen(false)
          setEditingAsset(null)
        }}
      />
      <ConfirmDialog />
    </div>
  )
}
