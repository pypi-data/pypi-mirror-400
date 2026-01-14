import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { getValidationHistory, getSource, type HistoryResponse, type Source } from '@/api/client'
import { formatDate } from '@/lib/utils'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { ArrowLeft, TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react'

export default function History() {
  const { id: sourceId } = useParams<{ id: string }>()
  const [source, setSource] = useState<Source | null>(null)
  const [historyData, setHistoryData] = useState<HistoryResponse['data'] | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [period, setPeriod] = useState<'7d' | '30d' | '90d'>('30d')
  const [granularity, setGranularity] = useState<'hourly' | 'daily' | 'weekly'>('daily')

  useEffect(() => {
    if (!sourceId) return

    async function fetchData() {
      try {
        setLoading(true)
        const [sourceData, historyRes] = await Promise.all([
          getSource(sourceId!),
          getValidationHistory(sourceId!, { period, granularity }),
        ])
        setSource(sourceData)
        setHistoryData(historyRes.data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load history')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [sourceId, period, granularity])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-destructive/10 border border-destructive rounded-lg p-4">
          <p className="text-destructive">{error}</p>
        </div>
      </div>
    )
  }

  if (!source || !historyData) {
    return <div className="p-6">Source not found</div>
  }

  const { summary, trend, failure_frequency, recent_validations } = historyData

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link to={`/sources/${sourceId}`}>
            <Button variant="ghost" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold">{source.name} - History</h1>
            <p className="text-muted-foreground">Validation trends and analytics</p>
          </div>
        </div>

        {/* Period & Granularity Selectors */}
        <div className="flex gap-2">
          <Select value={period} onValueChange={(v) => setPeriod(v as typeof period)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>

          <Select value={granularity} onValueChange={(v) => setGranularity(v as typeof granularity)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="hourly">Hourly</SelectItem>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Runs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summary.total_runs}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Passed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-2xl font-bold text-green-600">{summary.passed_runs}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Failed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <span className="text-2xl font-bold text-red-600">{summary.failed_runs}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Success Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {summary.success_rate >= 80 ? (
                <TrendingUp className="h-5 w-5 text-green-500" />
              ) : (
                <TrendingDown className="h-5 w-5 text-red-500" />
              )}
              <span
                className={`text-2xl font-bold ${
                  summary.success_rate >= 80 ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {summary.success_rate}%
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Success Rate Trend</CardTitle>
          <CardDescription>Validation success rate over time</CardDescription>
        </CardHeader>
        <CardContent>
          {trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="success_rate"
                  stroke="#fd9e4b"
                  strokeWidth={2}
                  name="Success Rate (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-64 text-muted-foreground">
              No data for the selected period
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Failure Frequency */}
        <Card>
          <CardHeader>
            <CardTitle>Top Failure Types</CardTitle>
            <CardDescription>Most common validation issues</CardDescription>
          </CardHeader>
          <CardContent>
            {failure_frequency.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={failure_frequency} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis type="category" dataKey="issue" width={150} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#fd9e4b" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-48 text-muted-foreground">
                No failures recorded
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Validations */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Validations</CardTitle>
            <CardDescription>Latest validation runs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recent_validations.length > 0 ? (
                recent_validations.map((v) => (
                  <Link
                    key={v.id}
                    to={`/validations/${v.id}`}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      {v.passed ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <AlertTriangle className="h-4 w-4 text-red-500" />
                      )}
                      <div>
                        <div className="font-medium">
                          {v.passed ? 'Passed' : 'Failed'}
                          {v.has_critical && (
                            <Badge variant="destructive" className="ml-2">
                              Critical
                            </Badge>
                          )}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {formatDate(v.created_at)}
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline">{v.total_issues} issues</Badge>
                  </Link>
                ))
              ) : (
                <div className="text-center text-muted-foreground py-8">
                  No validations yet
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
