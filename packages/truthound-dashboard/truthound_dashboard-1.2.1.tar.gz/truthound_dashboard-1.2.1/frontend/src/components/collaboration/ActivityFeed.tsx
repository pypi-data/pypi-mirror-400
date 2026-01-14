import { useIntlayer } from '@/providers'
import { Link } from 'react-router-dom'
import {
  Plus,
  Edit,
  Trash2,
  MessageSquare,
  BookOpen,
  Database,
  Columns,
} from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import type { Activity, ActivityAction } from '@/api/client'
import { formatDate } from '@/lib/utils'

interface ActivityFeedProps {
  activities: Activity[]
  showResourceLinks?: boolean
}

export function ActivityFeed({ activities, showResourceLinks = true }: ActivityFeedProps) {
  const collab = useIntlayer('collaboration')

  const getActionIcon = (action: ActivityAction) => {
    switch (action) {
      case 'created':
        return Plus
      case 'updated':
        return Edit
      case 'deleted':
        return Trash2
      case 'commented':
        return MessageSquare
      default:
        return Edit
    }
  }

  const getActionColor = (action: ActivityAction) => {
    switch (action) {
      case 'created':
        return 'text-green-600 bg-green-100 dark:bg-green-900/30'
      case 'deleted':
        return 'text-red-600 bg-red-100 dark:bg-red-900/30'
      case 'commented':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/30'
      default:
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30'
    }
  }

  const getResourceIcon = (resourceType: string) => {
    switch (resourceType) {
      case 'term':
        return BookOpen
      case 'asset':
        return Database
      case 'column':
        return Columns
      default:
        return Database
    }
  }

  const getResourceLink = (resourceType: string, resourceId: string) => {
    switch (resourceType) {
      case 'term':
        return `/glossary/${resourceId}`
      case 'asset':
        return `/catalog/${resourceId}`
      default:
        return null
    }
  }

  const getActionLabel = (action: ActivityAction) => {
    switch (action) {
      case 'created':
        return collab.actions.created
      case 'updated':
        return collab.actions.updated
      case 'deleted':
        return collab.actions.deleted
      case 'commented':
        return collab.actions.commented
      default:
        return action
    }
  }

  const getResourceTypeLabel = (resourceType: string) => {
    switch (resourceType) {
      case 'term':
        return collab.resourceTypes.term
      case 'asset':
        return collab.resourceTypes.asset
      case 'column':
        return collab.resourceTypes.column
      default:
        return resourceType
    }
  }

  if (activities.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">{collab.noActivity}</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {activities.map((activity) => {
        const ActionIcon = getActionIcon(activity.action)
        const ResourceIcon = getResourceIcon(activity.resource_type)
        const link = showResourceLinks
          ? getResourceLink(activity.resource_type, activity.resource_id)
          : null

        return (
          <div
            key={activity.id}
            className="flex items-start gap-3 p-3 rounded-lg border"
          >
            <div
              className={`h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 ${getActionColor(activity.action)}`}
            >
              <ActionIcon className="h-4 w-4" />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="font-medium">{activity.actor_id || 'System'}</span>
                <span className="text-muted-foreground">
                  {getActionLabel(activity.action)}
                </span>
                <Badge variant="outline" className="flex items-center gap-1">
                  <ResourceIcon className="h-3 w-3" />
                  {getResourceTypeLabel(activity.resource_type)}
                </Badge>
              </div>

              {activity.description && (
                <p className="text-sm text-muted-foreground mt-1">
                  {activity.description}
                </p>
              )}

              <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                <span>{formatDate(activity.created_at)}</span>
                {link && (
                  <>
                    <span>·</span>
                    <Link
                      to={link}
                      className="text-primary hover:underline"
                    >
                      View {activity.resource_type}
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
