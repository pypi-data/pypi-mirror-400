import { useEffect, useState, useCallback } from 'react'
import { useIntlayer } from '@/providers'
import { Activity as ActivityIcon, Filter } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { getActivities, type Activity as ActivityType } from '@/api/client'
import { useToast } from '@/hooks/use-toast'
import { str } from '@/lib/intlayer-utils'
import { ActivityFeed } from '@/components/collaboration/ActivityFeed'

export default function Activity() {
  const nav = useIntlayer('nav')
  const collab = useIntlayer('collaboration')
  const common = useIntlayer('common')
  const { toast } = useToast()

  const [activities, setActivities] = useState<ActivityType[]>([])
  const [loading, setLoading] = useState(true)
  const [resourceFilter, setResourceFilter] = useState<string>('')
  const [hasMore, setHasMore] = useState(true)
  const [skip, setSkip] = useState(0)
  const LIMIT = 20

  const loadActivities = useCallback(async (reset = false) => {
    try {
      setLoading(true)
      const currentSkip = reset ? 0 : skip
      const data = await getActivities({
        resource_type: resourceFilter || undefined,
        skip: currentSkip,
        limit: LIMIT,
      })

      if (reset) {
        setActivities(data)
        setSkip(LIMIT)
      } else {
        setActivities((prev) => [...prev, ...data])
        setSkip((prev) => prev + LIMIT)
      }

      setHasMore(data.length === LIMIT)
    } catch {
      toast({
        title: str(common.error),
        description: 'Failed to load activities',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [resourceFilter, skip, toast, common])

  useEffect(() => {
    loadActivities(true)
  }, [resourceFilter])

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      loadActivities(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">{nav.activity}</h1>
          <p className="text-muted-foreground">{collab.recentActivity}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select value={resourceFilter} onValueChange={setResourceFilter}>
          <SelectTrigger className="w-[200px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder={str(collab.filterByResource)} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">{collab.allResources}</SelectItem>
            <SelectItem value="term">{collab.resourceTypes.term}</SelectItem>
            <SelectItem value="asset">{collab.resourceTypes.asset}</SelectItem>
            <SelectItem value="column">{collab.resourceTypes.column}</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Activity Feed */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ActivityIcon className="h-5 w-5" />
            {collab.allActivity}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading && activities.length === 0 ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
            </div>
          ) : (
            <>
              <ActivityFeed activities={activities} />

              {hasMore && (
                <div className="flex justify-center mt-4">
                  <Button
                    variant="outline"
                    onClick={handleLoadMore}
                    disabled={loading}
                  >
                    {loading ? common.loading : collab.loadMore}
                  </Button>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
