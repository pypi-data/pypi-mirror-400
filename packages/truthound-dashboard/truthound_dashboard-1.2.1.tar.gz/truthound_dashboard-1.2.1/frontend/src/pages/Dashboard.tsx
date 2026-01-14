import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { useIntlayer } from '@/providers'
import {
  Database,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowRight,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { listSources, type Source } from '@/api/client'
import { formatDate } from '@/lib/utils'
import { AnimatedNumber } from '@/components/AnimatedNumber'
import { GlassCard } from '@/components/GlassCard'

export default function Dashboard() {
  const nav = useIntlayer('nav')
  const dashboard = useIntlayer('dashboard')
  const common = useIntlayer('common')
  const validation = useIntlayer('validation')
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  // Create a helper to get validation status labels
  const getValidationLabel = useMemo(() => {
    return (status: string | null | undefined) => {
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
  }, [validation])

  useEffect(() => {
    loadSources()
  }, [])

  async function loadSources() {
    try {
      setLoading(true)
      const response = await listSources({ limit: 10 })
      setSources(response.data)
    } catch (err) {
      setError(err as Error)
    } finally {
      setLoading(false)
    }
  }

  // Calculate stats
  // Backend validation status values: 'success' | 'failed' | 'error' | 'pending' | 'running' | null
  const totalSources = sources.length
  const passedSources = sources.filter(
    (s) => s.latest_validation_status === 'success'
  ).length
  const failedSources = sources.filter(
    (s) => s.latest_validation_status === 'failed' || s.latest_validation_status === 'error'
  ).length
  const pendingSources = sources.filter(
    (s) => !s.latest_validation_status || s.latest_validation_status === 'pending' || s.latest_validation_status === 'running'
  ).length

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <XCircle className="h-12 w-12 text-destructive" />
        <p className="text-muted-foreground">{dashboard.loadError}</p>
        <Button onClick={loadSources}>{common.retry}</Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">{nav.dashboard}</h1>
        <p className="text-muted-foreground">
          {dashboard.subtitle}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <GlassCard
          className="bg-gradient-to-br from-primary/10 via-primary/5 to-transparent border-primary/20"
          glowColor="#fd9e4b"
        >
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-primary/10 blur-2xl" />
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-xl bg-primary/20 flex items-center justify-center">
                <Database className="h-7 w-7 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">{dashboard.totalSources}</p>
                <p className="text-3xl font-bold">
                  <AnimatedNumber value={totalSources} duration={1200} />
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {dashboard.configuredSources}
                </p>
              </div>
            </div>
          </CardContent>
        </GlassCard>

        <GlassCard
          className="bg-gradient-to-br from-green-500/10 via-green-500/5 to-transparent border-green-500/20"
          glowColor="#22c55e"
        >
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-green-500/10 blur-2xl" />
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-xl bg-green-500/20 flex items-center justify-center">
                <CheckCircle2 className="h-7 w-7 text-green-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">{dashboard.passed}</p>
                <p className="text-3xl font-bold text-green-500">
                  <AnimatedNumber value={passedSources} duration={1200} />
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {dashboard.validationPassed}
                </p>
              </div>
            </div>
          </CardContent>
        </GlassCard>

        <GlassCard
          className="bg-gradient-to-br from-red-500/10 via-red-500/5 to-transparent border-red-500/20"
          glowColor="#ef4444"
        >
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-red-500/10 blur-2xl" />
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-xl bg-red-500/20 flex items-center justify-center">
                <XCircle className="h-7 w-7 text-red-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">{dashboard.failed}</p>
                <p className="text-3xl font-bold text-red-500">
                  <AnimatedNumber value={failedSources} duration={1200} />
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {dashboard.validationFailed}
                </p>
              </div>
            </div>
          </CardContent>
        </GlassCard>

        <GlassCard
          className="bg-gradient-to-br from-yellow-500/10 via-yellow-500/5 to-transparent border-yellow-500/20"
          glowColor="#eab308"
        >
          <div className="absolute top-0 right-0 -mt-4 -mr-4 h-24 w-24 rounded-full bg-yellow-500/10 blur-2xl" />
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-xl bg-yellow-500/20 flex items-center justify-center">
                <AlertTriangle className="h-7 w-7 text-yellow-500" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">{dashboard.pending}</p>
                <p className="text-3xl font-bold text-yellow-500">
                  <AnimatedNumber value={pendingSources} duration={1200} />
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {dashboard.notValidated}
                </p>
              </div>
            </div>
          </CardContent>
        </GlassCard>
      </div>

      {/* Recent Sources */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>{dashboard.recentSources}</CardTitle>
            <p className="text-sm text-muted-foreground">
              {dashboard.recentSourcesDesc}
            </p>
          </div>
          <Button asChild variant="outline" size="sm">
            <Link to="/sources">
              {dashboard.viewAll}
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          {sources.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center">
              <Database className="h-12 w-12 text-muted-foreground/50 mb-4" />
              <p className="text-muted-foreground mb-4">
                {dashboard.noSources}
              </p>
              <Button asChild>
                <Link to="/sources">{dashboard.addFirstSource}</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {sources.slice(0, 5).map((source) => (
                <Link
                  key={source.id}
                  to={`/sources/${source.id}`}
                  className="flex items-center justify-between p-4 rounded-lg border hover:bg-accent transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <Database className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{source.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {source.type} • {dashboard.lastValidated}:{' '}
                        {formatDate(source.last_validated_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {source.latest_validation_status && (
                      <Badge
                        variant={
                          source.latest_validation_status === 'success'
                            ? 'success'
                            : source.latest_validation_status === 'failed' || source.latest_validation_status === 'error'
                            ? 'destructive'
                            : source.latest_validation_status === 'pending' || source.latest_validation_status === 'running'
                            ? 'warning'
                            : 'secondary'
                        }
                      >
                        {getValidationLabel(source.latest_validation_status)}
                      </Badge>
                    )}
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
