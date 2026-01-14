import { useState, useEffect, useCallback } from 'react'
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  getSource,
  profileSource,
  learnSchema,
  type Source,
  type ProfileResult,
  type Schema,
} from '@/api/client'
import { formatNumber } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'
import {
  ArrowLeft,
  BarChart3,
  FileCode,
  Database,
  RefreshCw,
  Copy,
  Check,
  AlertCircle,
  Hash,
  Type,
  Percent,
  ArrowUpDown,
} from 'lucide-react'

// Column sorting types
type SortKey = 'name' | 'dtype' | 'null_pct' | 'unique_pct'
type SortDirection = 'asc' | 'desc'

interface SortConfig {
  key: SortKey
  direction: SortDirection
}

// Helper to parse percentage string to number
function parsePercentage(value: string | undefined): number {
  if (!value) return 0
  return parseFloat(value.replace('%', '')) || 0
}

// Helper to format bytes
function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

// Get badge variant based on null percentage
function getNullBadgeVariant(nullPct: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  const pct = parsePercentage(nullPct)
  if (pct === 0) return 'outline'
  if (pct < 5) return 'secondary'
  if (pct < 20) return 'default'
  return 'destructive'
}

// Get badge variant based on unique percentage
function getUniqueBadgeVariant(uniquePct: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  const pct = parsePercentage(uniquePct)
  if (pct >= 99) return 'outline' // Likely primary key
  if (pct >= 80) return 'secondary'
  if (pct >= 20) return 'default'
  return 'destructive' // Low cardinality
}

export default function Profile() {
  const { id: sourceId } = useParams<{ id: string }>()
  const { toast } = useToast()

  // State
  const [source, setSource] = useState<Source | null>(null)
  const [profile, setProfile] = useState<ProfileResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [profiling, setProfiling] = useState(false)
  const [learningSchema, setLearningSchema] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Schema dialog
  const [schemaDialogOpen, setSchemaDialogOpen] = useState(false)
  const [learnedSchema, setLearnedSchema] = useState<Schema | null>(null)
  const [copied, setCopied] = useState(false)

  // Sorting
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'name', direction: 'asc' })

  // Filter by data type
  const [typeFilter, setTypeFilter] = useState<string>('all')

  // Load source data
  useEffect(() => {
    if (!sourceId) return

    async function fetchSource() {
      try {
        setLoading(true)
        const sourceData = await getSource(sourceId!)
        setSource(sourceData)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load source')
      } finally {
        setLoading(false)
      }
    }

    fetchSource()
  }, [sourceId])

  // Run profiling
  const handleProfile = useCallback(async () => {
    if (!sourceId) return

    try {
      setProfiling(true)
      const result = await profileSource(sourceId)
      setProfile(result)
      toast({
        title: 'Profile Complete',
        description: `Analyzed ${result.row_count.toLocaleString()} rows across ${result.column_count} columns`,
      })
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Profiling Failed',
        description: err instanceof Error ? err.message : 'Unknown error',
      })
    } finally {
      setProfiling(false)
    }
  }, [sourceId, toast])

  // Learn schema
  const handleLearnSchema = useCallback(async () => {
    if (!sourceId) return

    try {
      setLearningSchema(true)
      const result = await learnSchema(sourceId, { infer_constraints: true })
      setLearnedSchema(result)
      setSchemaDialogOpen(true)
      toast({
        title: 'Schema Generated',
        description: `Generated schema with ${result.column_count} columns`,
      })
    } catch (err) {
      toast({
        variant: 'destructive',
        title: 'Schema Generation Failed',
        description: err instanceof Error ? err.message : 'Unknown error',
      })
    } finally {
      setLearningSchema(false)
    }
  }, [sourceId, toast])

  // Copy schema to clipboard
  const handleCopySchema = useCallback(async () => {
    if (!learnedSchema?.schema_yaml) return

    try {
      await navigator.clipboard.writeText(learnedSchema.schema_yaml)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
      toast({
        title: 'Copied',
        description: 'Schema YAML copied to clipboard',
      })
    } catch {
      toast({
        variant: 'destructive',
        title: 'Copy Failed',
        description: 'Failed to copy to clipboard',
      })
    }
  }, [learnedSchema, toast])

  // Sort columns
  const handleSort = useCallback((key: SortKey) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }))
  }, [])

  // Get unique data types for filter
  const dataTypes = profile?.columns
    ? [...new Set(profile.columns.map((c) => c.dtype))].sort()
    : []

  // Filter and sort columns
  const sortedColumns = profile?.columns
    ? [...profile.columns]
        .filter((col) => typeFilter === 'all' || col.dtype === typeFilter)
        .sort((a, b) => {
          const { key, direction } = sortConfig
          let comparison = 0

          switch (key) {
            case 'name':
              comparison = a.name.localeCompare(b.name)
              break
            case 'dtype':
              comparison = a.dtype.localeCompare(b.dtype)
              break
            case 'null_pct':
              comparison = parsePercentage(a.null_pct) - parsePercentage(b.null_pct)
              break
            case 'unique_pct':
              comparison = parsePercentage(a.unique_pct) - parsePercentage(b.unique_pct)
              break
          }

          return direction === 'asc' ? comparison : -comparison
        })
    : []

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="p-6">
        <div className="bg-destructive/10 border border-destructive rounded-lg p-4 flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <p className="text-destructive">{error}</p>
        </div>
      </div>
    )
  }

  // Source not found
  if (!source) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-lg font-medium mb-2">Source not found</h2>
          <Button asChild>
            <Link to="/sources">Back to Sources</Link>
          </Button>
        </div>
      </div>
    )
  }

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
            <h1 className="text-2xl font-bold">{source.name} - Profile</h1>
            <p className="text-muted-foreground">Data profiling and schema generation</p>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={handleLearnSchema}
            disabled={learningSchema || profiling}
          >
            <FileCode className="h-4 w-4 mr-2" />
            {learningSchema ? 'Generating...' : 'Generate Schema'}
          </Button>
          <Button onClick={handleProfile} disabled={profiling || learningSchema}>
            {profiling ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Profiling...
              </>
            ) : (
              <>
                <BarChart3 className="h-4 w-4 mr-2" />
                Run Profile
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Profile not run yet */}
      {!profile && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <BarChart3 className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium mb-2">No Profile Data</h3>
            <p className="text-muted-foreground text-center mb-4 max-w-md">
              Run a profile to analyze your data structure, column types, null percentages, and
              unique value distributions.
            </p>
            <Button onClick={handleProfile} disabled={profiling}>
              {profiling ? 'Profiling...' : 'Run Profile'}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Profile Results */}
      {profile && (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Hash className="h-4 w-4" />
                  Rows
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatNumber(profile.row_count)}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Type className="h-4 w-4" />
                  Columns
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{profile.column_count}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  Size
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatBytes(profile.size_bytes)}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Percent className="h-4 w-4" />
                  Avg Null %
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {profile.columns.length > 0
                    ? (
                        profile.columns.reduce((sum, col) => sum + parsePercentage(col.null_pct), 0) /
                        profile.columns.length
                      ).toFixed(1)
                    : 0}
                  %
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Column Statistics Table */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Column Statistics</CardTitle>
                  <CardDescription>Detailed statistics for each column</CardDescription>
                </div>

                {/* Type Filter */}
                <Select value={typeFilter} onValueChange={setTypeFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Filter by type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {dataTypes.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 -ml-3 font-semibold"
                          onClick={() => handleSort('name')}
                        >
                          Column
                          <ArrowUpDown className="ml-2 h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 -ml-3 font-semibold"
                          onClick={() => handleSort('dtype')}
                        >
                          Type
                          <ArrowUpDown className="ml-2 h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 -ml-3 font-semibold"
                          onClick={() => handleSort('null_pct')}
                        >
                          Nulls
                          <ArrowUpDown className="ml-2 h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 -ml-3 font-semibold"
                          onClick={() => handleSort('unique_pct')}
                        >
                          Unique
                          <ArrowUpDown className="ml-2 h-3 w-3" />
                        </Button>
                      </TableHead>
                      <TableHead>Min</TableHead>
                      <TableHead>Max</TableHead>
                      <TableHead>Mean</TableHead>
                      <TableHead>Std</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortedColumns.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                          No columns match the filter
                        </TableCell>
                      </TableRow>
                    ) : (
                      sortedColumns.map((col) => (
                        <TableRow key={col.name}>
                          <TableCell className="font-mono text-sm font-medium">
                            {col.name}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{col.dtype}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={getNullBadgeVariant(col.null_pct)}>
                              {col.null_pct}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant={getUniqueBadgeVariant(col.unique_pct)}>
                              {col.unique_pct}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {col.min !== undefined && col.min !== null
                              ? String(col.min).length > 20
                                ? `${String(col.min).slice(0, 20)}...`
                                : String(col.min)
                              : '-'}
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {col.max !== undefined && col.max !== null
                              ? String(col.max).length > 20
                                ? `${String(col.max).slice(0, 20)}...`
                                : String(col.max)
                              : '-'}
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {col.mean !== undefined && col.mean !== null
                              ? typeof col.mean === 'number'
                                ? col.mean.toFixed(2)
                                : col.mean
                              : '-'}
                          </TableCell>
                          <TableCell className="font-mono text-sm">
                            {col.std !== undefined && col.std !== null
                              ? typeof col.std === 'number'
                                ? col.std.toFixed(2)
                                : col.std
                              : '-'}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>

              {/* Results summary */}
              <div className="mt-4 text-sm text-muted-foreground">
                Showing {sortedColumns.length} of {profile.columns.length} columns
                {typeFilter !== 'all' && ` (filtered by ${typeFilter})`}
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Schema Dialog */}
      <Dialog open={schemaDialogOpen} onOpenChange={setSchemaDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle>Generated Schema</DialogTitle>
            <DialogDescription>
              Auto-generated schema from {source.name}. You can copy this YAML to use with
              truthound validation.
            </DialogDescription>
          </DialogHeader>

          {learnedSchema && (
            <div className="space-y-4">
              {/* Schema stats */}
              <div className="flex gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Columns:</span>{' '}
                  <span className="font-medium">{learnedSchema.column_count}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Rows analyzed:</span>{' '}
                  <span className="font-medium">
                    {formatNumber(learnedSchema.row_count)}
                  </span>
                </div>
              </div>

              {/* Schema YAML */}
              <div className="relative">
                <pre className="bg-muted p-4 rounded-lg text-sm overflow-auto max-h-[400px] font-mono">
                  {learnedSchema.schema_yaml}
                </pre>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setSchemaDialogOpen(false)}>
              Close
            </Button>
            <Button onClick={handleCopySchema}>
              {copied ? (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4 mr-2" />
                  Copy YAML
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
