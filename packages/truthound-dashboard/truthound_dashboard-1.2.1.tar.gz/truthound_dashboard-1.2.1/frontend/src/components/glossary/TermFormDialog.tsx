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
import { useGlossaryStore } from '@/stores/glossaryStore'
import { getTerm, type GlossaryCategory } from '@/api/client'
import { str } from '@/lib/intlayer-utils'
import { useToast } from '@/hooks/use-toast'

interface TermFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  termId?: string | null
  categories: GlossaryCategory[]
  onSuccess?: () => void
}

export function TermFormDialog({
  open,
  onOpenChange,
  termId,
  categories,
  onSuccess,
}: TermFormDialogProps) {
  const glossary = useIntlayer('glossary')
  const common = useIntlayer('common')
  const { createTerm, updateTerm } = useGlossaryStore()
  const { toast } = useToast()

  const [loading, setLoading] = useState(false)
  const [name, setName] = useState('')
  const [definition, setDefinition] = useState('')
  const [categoryId, setCategoryId] = useState<string>('')
  const [status, setStatus] = useState<'draft' | 'approved' | 'deprecated'>('draft')
  const [ownerId, setOwnerId] = useState('')

  const isEditing = !!termId

  useEffect(() => {
    if (open && termId) {
      // Load term data for editing
      getTerm(termId).then((term) => {
        setName(term.name)
        setDefinition(term.definition)
        setCategoryId(term.category_id || '')
        setStatus(term.status)
        setOwnerId(term.owner_id || '')
      })
    } else if (open) {
      // Reset form for new term
      setName('')
      setDefinition('')
      setCategoryId('')
      setStatus('draft')
      setOwnerId('')
    }
  }, [open, termId])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || !definition.trim()) return

    setLoading(true)
    try {
      if (isEditing && termId) {
        await updateTerm(termId, {
          name,
          definition,
          category_id: categoryId || undefined,
          status,
          owner_id: ownerId || undefined,
        })
        toast({
          title: str(common.success),
          description: str(glossary.updateSuccess),
        })
      } else {
        await createTerm({
          name,
          definition,
          category_id: categoryId || undefined,
          status,
          owner_id: ownerId || undefined,
        })
        toast({
          title: str(common.success),
          description: str(glossary.createSuccess),
        })
      }
      onSuccess?.()
    } catch {
      toast({
        title: str(common.error),
        description: str(isEditing ? glossary.updateError : glossary.createError),
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
            {isEditing ? glossary.editTerm : glossary.addTerm}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">{glossary.termName}</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Customer Lifetime Value"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="definition">{glossary.definition}</Label>
            <textarea
              id="definition"
              value={definition}
              onChange={(e) => setDefinition(e.target.value)}
              placeholder="The total revenue a business can expect..."
              className="w-full min-h-[100px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>{glossary.category}</Label>
              <Select value={categoryId} onValueChange={setCategoryId}>
                <SelectTrigger>
                  <SelectValue placeholder={str(glossary.selectCategory)} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">{glossary.noCategory}</SelectItem>
                  {categories.map((cat) => (
                    <SelectItem key={cat.id} value={cat.id}>
                      {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>{glossary.status.label}</Label>
              <Select value={status} onValueChange={(v) => setStatus(v as typeof status)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="draft">{glossary.status.draft}</SelectItem>
                  <SelectItem value="approved">{glossary.status.approved}</SelectItem>
                  <SelectItem value="deprecated">{glossary.status.deprecated}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="owner">{glossary.owner}</Label>
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
