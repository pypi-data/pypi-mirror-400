import { useEffect, useState } from 'react'
import { useIntlayer } from '@/providers'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useCatalogStore } from '@/stores/catalogStore'
import { getAsset, type Source, type AssetType } from '@/api/client'
import { str } from '@/lib/intlayer-utils'
import { useToast } from '@/hooks/use-toast'

interface AssetFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  assetId?: string | null
  sources: Source[]
  onSuccess?: () => void
}

export function AssetFormDialog({
  open,
  onOpenChange,
  assetId,
  sources,
  onSuccess,
}: AssetFormDialogProps) {
  const catalog = useIntlayer('catalog')
  const common = useIntlayer('common')
  const { createAsset, updateAsset } = useCatalogStore()
  const { toast } = useToast()

  const [loading, setLoading] = useState(false)
  const [name, setName] = useState('')
  const [assetType, setAssetType] = useState<AssetType>('table')
  const [sourceId, setSourceId] = useState<string>('')
  const [description, setDescription] = useState('')
  const [ownerId, setOwnerId] = useState('')

  const isEditing = !!assetId

  useEffect(() => {
    if (open && assetId) {
      // Load asset data for editing
      getAsset(assetId).then((asset) => {
        setName(asset.name)
        setAssetType(asset.asset_type)
        setSourceId(asset.source_id || '')
        setDescription(asset.description || '')
        setOwnerId(asset.owner_id || '')
      })
    } else if (open) {
      // Reset form for new asset
      setName('')
      setAssetType('table')
      setSourceId('')
      setDescription('')
      setOwnerId('')
    }
  }, [open, assetId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return

    setLoading(true)
    try {
      if (isEditing && assetId) {
        await updateAsset(assetId, {
          name,
          asset_type: assetType,
          source_id: sourceId || undefined,
          description: description || undefined,
          owner_id: ownerId || undefined,
        })
        toast({
          title: str(common.success),
          description: str(catalog.updateSuccess),
        })
      } else {
        await createAsset({
          name,
          asset_type: assetType,
          source_id: sourceId || undefined,
          description: description || undefined,
          owner_id: ownerId || undefined,
        })
        toast({
          title: str(common.success),
          description: str(catalog.createSuccess),
        })
      }
      onSuccess?.()
    } catch {
      toast({
        title: str(common.error),
        description: str(isEditing ? catalog.updateError : catalog.createError),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {isEditing ? catalog.editAsset : catalog.addAsset}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">{catalog.assetName}</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="customers, orders, transactions..."
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>{catalog.assetType}</Label>
              <Select value={assetType} onValueChange={(v) => setAssetType(v as AssetType)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="table">{catalog.assetTypes.table}</SelectItem>
                  <SelectItem value="file">{catalog.assetTypes.file}</SelectItem>
                  <SelectItem value="api">{catalog.assetTypes.api}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>{catalog.dataSource}</Label>
              <Select value={sourceId} onValueChange={setSourceId}>
                <SelectTrigger>
                  <SelectValue placeholder={str(catalog.selectSource)} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">{catalog.noSource}</SelectItem>
                  {sources.map((source) => (
                    <SelectItem key={source.id} value={source.id}>
                      {source.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">{catalog.description}</Label>
            <textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe this data asset..."
              className="w-full min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="owner">{catalog.owner}</Label>
            <Input
              id="owner"
              value={ownerId}
              onChange={(e) => setOwnerId(e.target.value)}
              placeholder="John Doe"
            />
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              {common.cancel}
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? common.saving : common.save}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
