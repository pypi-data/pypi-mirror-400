/**
 * Notifications management page.
 *
 * Features:
 * - Channel management (Slack, Email, Webhook)
 * - Rule configuration
 * - Delivery log viewing
 */

import { useState } from 'react'
import { useIntlayer } from '@/providers'
import {
  Bell,
  Plus,
  Trash2,
  Edit2,
  Send,
  CheckCircle,
  XCircle,
  Clock,
  MessageSquare,
  Mail,
  Webhook,
  RefreshCw,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { useApi, useMutation } from '@/hooks/use-api'
import { useConfirm } from '@/components/ConfirmDialog'
import {
  listNotificationChannels,
  listNotificationRules,
  listNotificationLogs,
  getNotificationStats,
  testNotificationChannel,
  deleteNotificationChannel,
  deleteNotificationRule,
  updateNotificationChannel,
  updateNotificationRule,
  type NotificationChannel,
  type NotificationRule,
} from '@/api/client'
import { formatDate } from '@/lib/utils'
import { str } from '@/lib/intlayer-utils'

function getChannelIcon(type: string) {
  switch (type) {
    case 'slack':
      return <MessageSquare className="h-4 w-4" />
    case 'email':
      return <Mail className="h-4 w-4" />
    case 'webhook':
      return <Webhook className="h-4 w-4" />
    default:
      return <Bell className="h-4 w-4" />
  }
}

function getStatusBadge(status: string) {
  switch (status) {
    case 'sent':
      return (
        <Badge className="bg-green-500/10 text-green-500 border-green-500/20">
          <CheckCircle className="h-3 w-3 mr-1" />
          Sent
        </Badge>
      )
    case 'failed':
      return (
        <Badge className="bg-red-500/10 text-red-500 border-red-500/20">
          <XCircle className="h-3 w-3 mr-1" />
          Failed
        </Badge>
      )
    default:
      return (
        <Badge className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">
          <Clock className="h-3 w-3 mr-1" />
          Pending
        </Badge>
      )
  }
}

function getConditionLabel(condition: string): string {
  const labels: Record<string, string> = {
    validation_failed: 'Validation Failed',
    critical_issues: 'Critical Issues',
    high_issues: 'High Issues',
    schedule_failed: 'Schedule Failed',
    drift_detected: 'Drift Detected',
  }
  return labels[condition] || condition
}

export default function Notifications() {
  const notifications_t = useIntlayer('notifications')
  const common = useIntlayer('common')
  const { toast } = useToast()
  const { confirm, ConfirmDialog } = useConfirm()
  const [activeTab, setActiveTab] = useState('channels')

  // Fetch data
  const {
    data: channelsData,
    loading: channelsLoading,
    refetch: refetchChannels,
  } = useApi(() => listNotificationChannels(), [])

  const {
    data: rulesData,
    loading: rulesLoading,
    refetch: refetchRules,
  } = useApi(() => listNotificationRules(), [])

  const {
    data: logsData,
    loading: logsLoading,
    refetch: refetchLogs,
  } = useApi(() => listNotificationLogs({ limit: 50 }), [])

  const { data: statsData } = useApi(
    () => getNotificationStats({ hours: 24 }),
    []
  )

  // Mutations
  const testChannelMutation = useMutation(testNotificationChannel)
  const deleteChannelMutation = useMutation(deleteNotificationChannel)
  const deleteRuleMutation = useMutation(deleteNotificationRule)

  const channels = channelsData?.data || []
  const rules = rulesData?.data || []
  const logs = logsData?.data || []
  const stats = statsData?.data

  const handleTestChannel = async (channelId: string) => {
    try {
      const result = await testChannelMutation.mutate(channelId)
      if (result.success) {
        toast({
          title: str(notifications_t.testSuccess),
          variant: 'default',
        })
      } else {
        toast({
          title: str(notifications_t.testFailed),
          description: result.error,
          variant: 'destructive',
        })
      }
    } catch {
      toast({
        title: str(notifications_t.testFailed),
        variant: 'destructive',
      })
    }
  }

  const handleDeleteChannel = async (channelId: string) => {
    const confirmed = await confirm({
      title: str(notifications_t.deleteChannel),
      description: str(notifications_t.deleteChannelConfirm),
      confirmText: str(common.delete),
      variant: 'destructive',
    })
    if (!confirmed) return

    try {
      await deleteChannelMutation.mutate(channelId)
      toast({ title: str(notifications_t.channelDeleted) })
      refetchChannels()
    } catch {
      toast({ title: str(notifications_t.deleteChannelFailed), variant: 'destructive' })
    }
  }

  const handleToggleChannel = async (channel: NotificationChannel) => {
    try {
      await updateNotificationChannel(channel.id, {
        is_active: !channel.is_active,
      })
      refetchChannels()
    } catch {
      toast({ title: 'Failed to update channel', variant: 'destructive' })
    }
  }

  const handleDeleteRule = async (ruleId: string) => {
    const confirmed = await confirm({
      title: str(notifications_t.deleteRule),
      description: str(notifications_t.deleteRuleConfirm),
      confirmText: str(common.delete),
      variant: 'destructive',
    })
    if (!confirmed) return

    try {
      await deleteRuleMutation.mutate(ruleId)
      toast({ title: str(notifications_t.ruleDeleted) })
      refetchRules()
    } catch {
      toast({ title: str(notifications_t.deleteRuleFailed), variant: 'destructive' })
    }
  }

  const handleToggleRule = async (rule: NotificationRule) => {
    try {
      await updateNotificationRule(rule.id, {
        is_active: !rule.is_active,
      })
      refetchRules()
    } catch {
      toast({ title: 'Failed to update rule', variant: 'destructive' })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{notifications_t.title}</h1>
          <p className="text-muted-foreground">
            {notifications_t.subtitle}
          </p>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total (24h)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Success Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.success_rate}%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {notifications_t.sent}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-500">
                {stats.by_status?.sent || 0}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {notifications_t.failed}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">
                {stats.by_status?.failed || 0}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="channels">
            {notifications_t.channels} ({channels.length})
          </TabsTrigger>
          <TabsTrigger value="rules">
            {notifications_t.rules} ({rules.length})
          </TabsTrigger>
          <TabsTrigger value="logs">
            {notifications_t.logs} ({logs.length})
          </TabsTrigger>
        </TabsList>

        {/* Channels Tab */}
        <TabsContent value="channels" className="space-y-4">
          <div className="flex justify-between">
            <Button variant="outline" size="sm" onClick={() => refetchChannels()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              {common.refresh}
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              {notifications_t.addChannel}
            </Button>
          </div>

          {channelsLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              {common.loading}
            </div>
          ) : channels.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                {notifications_t.noChannels}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{common.name}</TableHead>
                    <TableHead>{common.type}</TableHead>
                    <TableHead>Config</TableHead>
                    <TableHead>{common.status}</TableHead>
                    <TableHead className="text-right">{common.actions}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {channels.map((channel) => (
                    <TableRow key={channel.id}>
                      <TableCell className="font-medium">{channel.name}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getChannelIcon(channel.type)}
                          <span className="capitalize">{channel.type}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm">
                        {channel.config_summary}
                      </TableCell>
                      <TableCell>
                        <Switch
                          checked={channel.is_active}
                          onCheckedChange={() => handleToggleChannel(channel)}
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleTestChannel(channel.id)}
                            disabled={testChannelMutation.loading}
                          >
                            <Send className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteChannel(channel.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          )}
        </TabsContent>

        {/* Rules Tab */}
        <TabsContent value="rules" className="space-y-4">
          <div className="flex justify-between">
            <Button variant="outline" size="sm" onClick={() => refetchRules()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              {common.refresh}
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              {notifications_t.addRule}
            </Button>
          </div>

          {rulesLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              {common.loading}
            </div>
          ) : rules.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                {notifications_t.noRules}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{common.name}</TableHead>
                    <TableHead>Condition</TableHead>
                    <TableHead>Channels</TableHead>
                    <TableHead>{common.status}</TableHead>
                    <TableHead className="text-right">{common.actions}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {rules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell className="font-medium">{rule.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {getConditionLabel(rule.condition)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-muted-foreground">
                          {rule.channel_ids.length} channel(s)
                        </span>
                      </TableCell>
                      <TableCell>
                        <Switch
                          checked={rule.is_active}
                          onCheckedChange={() => handleToggleRule(rule)}
                        />
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-2">
                          <Button variant="ghost" size="sm">
                            <Edit2 className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteRule(rule.id)}
                          >
                            <Trash2 className="h-4 w-4 text-red-500" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          )}
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="space-y-4">
          <div className="flex justify-between">
            <Button variant="outline" size="sm" onClick={() => refetchLogs()}>
              <RefreshCw className="h-4 w-4 mr-2" />
              {common.refresh}
            </Button>
          </div>

          {logsLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              {common.loading}
            </div>
          ) : logs.length === 0 ? (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                {notifications_t.noLogs}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{common.status}</TableHead>
                    <TableHead>Event</TableHead>
                    <TableHead>Message</TableHead>
                    <TableHead>Time</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>{getStatusBadge(log.status)}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{log.event_type}</Badge>
                      </TableCell>
                      <TableCell className="max-w-xs truncate text-muted-foreground">
                        {log.message_preview}
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm">
                        {formatDate(log.created_at)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      <ConfirmDialog />
    </div>
  )
}
