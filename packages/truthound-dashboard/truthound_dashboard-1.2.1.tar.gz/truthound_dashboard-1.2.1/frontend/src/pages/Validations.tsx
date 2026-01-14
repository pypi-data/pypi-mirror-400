import { useEffect, useState, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Columns,
  Rows3,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { getValidation, type Validation } from '@/api/client'
import { formatDate, formatDuration, formatNumber } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'

export default function Validations() {
  const { id } = useParams<{ id: string }>()
  const [validation, setValidation] = useState<Validation | null>(null)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  const loadValidation = useCallback(async () => {
    if (!id) return
    try {
      setLoading(true)
      const data = await getValidation(id)
      setValidation(data)
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to load validation details',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [id, toast])

  useEffect(() => {
    loadValidation()
  }, [loadValidation])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  if (!validation) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <XCircle className="h-12 w-12 text-destructive mb-4" />
        <p className="text-muted-foreground">Validation not found</p>
        <Button asChild className="mt-4">
          <Link to="/">Back to Dashboard</Link>
        </Button>
      </div>
    )
  }

  // Group issues by severity
  const issuesBySeverity = {
    critical: validation.issues.filter((i) => i.severity === 'critical'),
    high: validation.issues.filter((i) => i.severity === 'high'),
    medium: validation.issues.filter((i) => i.severity === 'medium'),
    low: validation.issues.filter((i) => i.severity === 'low'),
  }

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        to={`/sources/${validation.source_id}`}
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Source
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-3">
            {validation.passed ? (
              <CheckCircle2 className="h-8 w-8 text-green-600" />
            ) : (
              <XCircle className="h-8 w-8 text-red-600" />
            )}
            <h1 className="text-3xl font-bold">
              Validation {validation.passed ? 'Passed' : 'Failed'}
            </h1>
          </div>
          <p className="text-muted-foreground mt-2">
            {formatDate(validation.created_at)}
          </p>
        </div>
        <Badge
          variant={validation.passed ? 'success' : 'destructive'}
          className="text-lg px-4 py-1"
        >
          {validation.status}
        </Badge>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <AlertTriangle className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Total Issues</p>
                <p className="text-2xl font-bold">{validation.total_issues}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Rows3 className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Rows</p>
                <p className="text-2xl font-bold">
                  {formatNumber(validation.row_count)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Columns className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Columns</p>
                <p className="text-2xl font-bold">
                  {formatNumber(validation.column_count)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Clock className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Duration</p>
                <p className="text-2xl font-bold">
                  {formatDuration(validation.duration_ms)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Issue Summary */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-red-200 dark:border-red-900">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Critical</span>
              <Badge variant="critical">{validation.critical_issues}</Badge>
            </div>
          </CardContent>
        </Card>
        <Card className="border-orange-200 dark:border-orange-900">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">High</span>
              <Badge variant="high">{validation.high_issues}</Badge>
            </div>
          </CardContent>
        </Card>
        <Card className="border-yellow-200 dark:border-yellow-900">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Medium</span>
              <Badge variant="medium">{validation.medium_issues}</Badge>
            </div>
          </CardContent>
        </Card>
        <Card className="border-green-200 dark:border-green-900">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Low</span>
              <Badge variant="low">{validation.low_issues}</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Issues Detail */}
      {validation.issues.length > 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Issues Detail</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {['critical', 'high', 'medium', 'low'].map((severity) => {
                const issues =
                  issuesBySeverity[severity as keyof typeof issuesBySeverity]
                if (issues.length === 0) return null

                return (
                  <div key={severity}>
                    <h3 className="font-semibold capitalize mb-2 flex items-center gap-2">
                      <Badge
                        variant={severity as 'critical' | 'high' | 'medium' | 'low'}
                      >
                        {severity}
                      </Badge>
                      <span className="text-muted-foreground">
                        ({issues.length})
                      </span>
                    </h3>
                    <div className="space-y-2">
                      {issues.map((issue, index) => (
                        <div
                          key={index}
                          className="p-4 rounded-lg border bg-card"
                        >
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-medium">
                                <span className="text-primary">{issue.column}</span>
                                {' - '}
                                {issue.issue_type}
                              </p>
                              {issue.details && (
                                <p className="text-sm text-muted-foreground mt-1">
                                  {issue.details}
                                </p>
                              )}
                              {(issue.expected !== undefined || issue.actual !== undefined) && (
                                <div className="flex gap-4 mt-2 text-sm">
                                  {issue.expected !== undefined && (
                                    <span>
                                      Expected:{' '}
                                      <code className="bg-muted px-1 rounded">
                                        {String(issue.expected)}
                                      </code>
                                    </span>
                                  )}
                                  {issue.actual !== undefined && (
                                    <span>
                                      Actual:{' '}
                                      <code className="bg-muted px-1 rounded">
                                        {String(issue.actual)}
                                      </code>
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                            <span className="text-sm text-muted-foreground whitespace-nowrap">
                              {formatNumber(issue.count)} occurrences
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-16 flex flex-col items-center justify-center">
            <CheckCircle2 className="h-16 w-16 text-green-600 mb-4" />
            <h3 className="text-lg font-semibold">No Issues Found</h3>
            <p className="text-muted-foreground">
              All validation checks passed successfully.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Error Message */}
      {validation.error_message && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="text-sm text-destructive whitespace-pre-wrap">
              {validation.error_message}
            </pre>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
