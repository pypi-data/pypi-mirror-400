import { useEffect, useState, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { useIntlayer } from '@/providers'
import {
  BookOpen,
  Plus,
  Search,
  Filter,
  Trash2,
  Edit,
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
import { useGlossaryStore } from '@/stores/glossaryStore'
import { str } from '@/lib/intlayer-utils'
import { useToast } from '@/hooks/use-toast'
import { useConfirm } from '@/components/ConfirmDialog'
import { TermFormDialog } from '@/components/glossary/TermFormDialog'

export default function Glossary() {
  const nav = useIntlayer('nav')
  const glossary = useIntlayer('glossary')
  const common = useIntlayer('common')
  const {
    terms,
    categories,
    loading,
    fetchTerms,
    fetchCategories,
    deleteTerm,
  } = useGlossaryStore()
  const { toast } = useToast()
  const { confirm, ConfirmDialog } = useConfirm()

  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editingTerm, setEditingTerm] = useState<string | null>(null)

  const loadData = useCallback(async () => {
    await Promise.all([
      fetchTerms({
        search: search || undefined,
        category_id: categoryFilter || undefined,
        status: statusFilter || undefined,
      }),
      fetchCategories(),
    ])
  }, [fetchTerms, fetchCategories, search, categoryFilter, statusFilter])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleDelete = async (id: string) => {
    const confirmed = await confirm({
      title: str(glossary.deleteTerm),
      description: str(glossary.confirmDelete),
      confirmText: str(common.delete),
      variant: 'destructive',
    })
    if (!confirmed) return

    try {
      await deleteTerm(id)
      toast({
        title: str(common.success),
        description: str(glossary.deleteSuccess),
      })
    } catch {
      toast({
        title: str(common.error),
        description: str(glossary.deleteError),
        variant: 'destructive',
      })
    }
  }

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

  if (loading && terms.length === 0) {
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
          <h1 className="text-3xl font-bold">{nav.glossary}</h1>
          <p className="text-muted-foreground">{glossary.subtitle}</p>
        </div>
        <Button onClick={() => setDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          {glossary.addTerm}
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder={str(glossary.searchTerms)}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[200px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder={str(glossary.filterByCategory)} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">{glossary.allCategories}</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat.id} value={cat.id}>
                {cat.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder={str(glossary.filterByStatus)} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">{glossary.allStatuses}</SelectItem>
            <SelectItem value="draft">{glossary.status.draft}</SelectItem>
            <SelectItem value="approved">{glossary.status.approved}</SelectItem>
            <SelectItem value="deprecated">{glossary.status.deprecated}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Terms List */}
      {terms.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <BookOpen className="h-16 w-16 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-semibold mb-2">{glossary.noTermsYet}</h3>
            <p className="text-muted-foreground text-center mb-4">
              {glossary.noTermsDesc}
            </p>
            <Button onClick={() => setDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              {glossary.addFirstTerm}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {terms.map((term) => (
            <Card key={term.id}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4 flex-1">
                    <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <BookOpen className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <Link
                        to={`/glossary/${term.id}`}
                        className="font-semibold hover:text-primary transition-colors"
                      >
                        {term.name}
                      </Link>
                      <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                        {term.definition}
                      </p>
                      <div className="flex items-center gap-2 mt-2 flex-wrap">
                        <Badge variant={getStatusBadgeVariant(term.status)}>
                          {getStatusLabel(term.status)}
                        </Badge>
                        {term.category && (
                          <Badge variant="outline">{term.category.name}</Badge>
                        )}
                        {term.owner_id && (
                          <span className="text-xs text-muted-foreground">
                            {glossary.owner}: {term.owner_id}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-4">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setEditingTerm(term.id)
                        setDialogOpen(true)
                      }}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDelete(term.id)}
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

      {/* Dialogs */}
      <TermFormDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          setDialogOpen(open)
          if (!open) setEditingTerm(null)
        }}
        termId={editingTerm}
        categories={categories}
        onSuccess={() => {
          loadData()
          setDialogOpen(false)
          setEditingTerm(null)
        }}
      />
      <ConfirmDialog />
    </div>
  )
}
