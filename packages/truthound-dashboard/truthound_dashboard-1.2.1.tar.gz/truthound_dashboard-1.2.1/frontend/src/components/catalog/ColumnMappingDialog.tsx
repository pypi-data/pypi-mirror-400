import { useState, useMemo } from 'react'
import { useIntlayer } from '@/providers'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, BookOpen } from 'lucide-react'
import type { GlossaryTerm } from '@/api/client'
import { str } from '@/lib/intlayer-utils'

interface ColumnMappingDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  columnId: string | null
  terms: GlossaryTerm[]
  onMap: (columnId: string, termId: string) => void
}

export function ColumnMappingDialog({
  open,
  onOpenChange,
  columnId,
  terms,
  onMap,
}: ColumnMappingDialogProps) {
  const catalog = useIntlayer('catalog')
  const common = useIntlayer('common')
  const [search, setSearch] = useState('')

  const filteredTerms = useMemo(() => {
    if (!search) return terms
    const searchLower = search.toLowerCase()
    return terms.filter(
      (t) =>
        t.name.toLowerCase().includes(searchLower) ||
        t.definition.toLowerCase().includes(searchLower)
    )
  }, [terms, search])

  const handleSelect = (termId: string) => {
    if (columnId) {
      onMap(columnId, termId)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{catalog.columnMapping}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder={str(catalog.searchTermToMap)}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>

          <div className="max-h-[300px] overflow-y-auto space-y-2">
            {filteredTerms.length === 0 ? (
              <p className="text-muted-foreground text-center py-4">
                {catalog.noTermSelected}
              </p>
            ) : (
              filteredTerms.map((term) => (
                <button
                  key={term.id}
                  onClick={() => handleSelect(term.id)}
                  className="w-full text-left p-3 rounded-lg border hover:bg-accent transition-colors"
                >
                  <div className="flex items-start gap-3">
                    <div className="h-8 w-8 rounded bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <BookOpen className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium">{term.name}</p>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {term.definition}
                      </p>
                    </div>
                  </div>
                </button>
              ))
            )}
          </div>

          <div className="flex justify-end">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              {common.cancel}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
