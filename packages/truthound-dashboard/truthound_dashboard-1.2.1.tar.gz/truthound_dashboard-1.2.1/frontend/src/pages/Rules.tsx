import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft,
  Plus,
  Save,
  Trash2,
  FileCode,
  AlertCircle,
  Loader2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/api/client'

interface Rule {
  id: string
  source_id: string
  name: string
  description: string | null
  rules_yaml: string
  rules_json: Record<string, unknown> | null
  is_active: boolean
  version: string | null
  column_count: number
  created_at: string
  updated_at: string
}

interface RuleListItem {
  id: string
  source_id: string
  name: string
  description: string | null
  is_active: boolean
  version: string | null
  column_count: number
  created_at: string
  updated_at: string
}

interface Source {
  id: string
  name: string
  type: string
}

const DEFAULT_RULES_YAML = `# Validation Rules
# Define column-level and table-level validation rules

columns:
  # Example: user_id must be not null and unique
  # user_id:
  #   not_null: true
  #   unique: true

  # Example: email must match a pattern
  # email:
  #   pattern: "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\\\.[a-zA-Z0-9-.]+$"

  # Example: age must be between 0 and 150
  # age:
  #   min: 0
  #   max: 150

# table:
#   min_rows: 1
#   max_rows: 1000000
`

export default function Rules() {
  const { id: sourceId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()

  const [source, setSource] = useState<Source | null>(null)
  const [rules, setRules] = useState<RuleListItem[]>([])
  const [activeRule, setActiveRule] = useState<Rule | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [yamlContent, setYamlContent] = useState('')
  const [ruleName, setRuleName] = useState('')
  const [ruleDescription, setRuleDescription] = useState('')
  const [hasChanges, setHasChanges] = useState(false)

  const fetchSource = useCallback(async () => {
    if (!sourceId) return
    try {
      const data = await apiClient.get<Source>(`/sources/${sourceId}`)
      setSource(data)
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to load source',
        variant: 'destructive',
      })
    }
  }, [sourceId, toast])

  const fetchRules = useCallback(async () => {
    if (!sourceId) return
    try {
      const data = await apiClient.get<{ data: RuleListItem[] }>(
        `/sources/${sourceId}/rules`
      )
      setRules(data.data)
    } catch {
      toast({
        title: 'Error',
        description: 'Failed to load rules',
        variant: 'destructive',
      })
    }
  }, [sourceId, toast])

  const fetchActiveRule = useCallback(async () => {
    if (!sourceId) return
    try {
      const data = await apiClient.get<Rule | null>(
        `/sources/${sourceId}/rules/active`
      )
      if (data) {
        setActiveRule(data)
        setYamlContent(data.rules_yaml)
        setRuleName(data.name)
        setRuleDescription(data.description || '')
      } else {
        setActiveRule(null)
        setYamlContent(DEFAULT_RULES_YAML)
        setRuleName('Default Rules')
        setRuleDescription('')
      }
    } catch {
      setActiveRule(null)
      setYamlContent(DEFAULT_RULES_YAML)
      setRuleName('Default Rules')
      setRuleDescription('')
    }
  }, [sourceId])

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true)
      await Promise.all([fetchSource(), fetchRules(), fetchActiveRule()])
      setIsLoading(false)
    }
    loadData()
  }, [fetchSource, fetchRules, fetchActiveRule])

  const handleYamlChange = (value: string) => {
    setYamlContent(value)
    setHasChanges(true)
  }

  const handleSave = async () => {
    if (!sourceId) return

    setIsSaving(true)
    try {
      if (activeRule) {
        // Update existing rule
        await apiClient.put<Rule>(`/rules/${activeRule.id}`, {
          name: ruleName,
          description: ruleDescription || null,
          rules_yaml: yamlContent,
        })
        toast({
          title: 'Saved',
          description: 'Rules updated successfully',
        })
      } else {
        // Create new rule
        await apiClient.post<Rule>(`/sources/${sourceId}/rules?activate=true`, {
          name: ruleName,
          description: ruleDescription || null,
          rules_yaml: yamlContent,
        })
        toast({
          title: 'Created',
          description: 'Rules created successfully',
        })
      }
      setHasChanges(false)
      await Promise.all([fetchRules(), fetchActiveRule()])
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to save rules',
        variant: 'destructive',
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleCreateNew = async () => {
    if (!sourceId) return

    setIsCreating(true)
    try {
      await apiClient.post<Rule>(`/sources/${sourceId}/rules?activate=true`, {
        name: 'New Rules',
        description: null,
        rules_yaml: DEFAULT_RULES_YAML,
      })
      toast({
        title: 'Created',
        description: 'New rule created successfully',
      })
      await Promise.all([fetchRules(), fetchActiveRule()])
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to create rule',
        variant: 'destructive',
      })
    } finally {
      setIsCreating(false)
    }
  }

  const handleActivateRule = async (ruleId: string) => {
    try {
      await apiClient.post<Rule>(`/rules/${ruleId}/activate`, {})
      toast({
        title: 'Activated',
        description: 'Rule activated successfully',
      })
      await Promise.all([fetchRules(), fetchActiveRule()])
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to activate rule',
        variant: 'destructive',
      })
    }
  }

  const handleDeleteRule = async (ruleId: string) => {
    if (!confirm('Are you sure you want to delete this rule?')) return

    try {
      await apiClient.delete(`/rules/${ruleId}`)
      toast({
        title: 'Deleted',
        description: 'Rule deleted successfully',
      })
      await Promise.all([fetchRules(), fetchActiveRule()])
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to delete rule',
        variant: 'destructive',
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate(`/sources/${sourceId}`)}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-semibold">Validation Rules</h1>
          {source && (
            <p className="text-muted-foreground">
              {source.name} ({source.type})
            </p>
          )}
        </div>
        <Button
          onClick={handleCreateNew}
          disabled={isCreating}
          variant="outline"
        >
          {isCreating ? (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          ) : (
            <Plus className="mr-2 h-4 w-4" />
          )}
          New Rule
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Rules List */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Rule History</CardTitle>
              <CardDescription className="text-xs">
                {rules.length} rule{rules.length !== 1 ? 's' : ''} defined
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {rules.length === 0 ? (
                <div className="text-center py-4 text-sm text-muted-foreground">
                  No rules defined yet
                </div>
              ) : (
                rules.map((rule) => (
                  <div
                    key={rule.id}
                    className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                      activeRule?.id === rule.id
                        ? 'border-primary bg-primary/5'
                        : 'hover:bg-accent'
                    }`}
                    onClick={() => {
                      if (activeRule?.id !== rule.id) {
                        handleActivateRule(rule.id)
                      }
                    }}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <FileCode className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium text-sm truncate">
                            {rule.name}
                          </span>
                          {rule.is_active && (
                            <Badge variant="default" className="text-xs">
                              Active
                            </Badge>
                          )}
                        </div>
                        <div className="mt-1 text-xs text-muted-foreground">
                          {rule.column_count} column rule{rule.column_count !== 1 ? 's' : ''}
                          {rule.version && ` - v${rule.version}`}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-7 w-7"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteRule(rule.id)
                        }}
                      >
                        <Trash2 className="h-3.5 w-3.5 text-muted-foreground hover:text-destructive" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </div>

        {/* Editor */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-sm font-medium">
                    Rule Editor
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Define validation rules in YAML format
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  {hasChanges && (
                    <Badge variant="outline" className="text-xs">
                      <AlertCircle className="mr-1 h-3 w-3" />
                      Unsaved changes
                    </Badge>
                  )}
                  <Button
                    size="sm"
                    onClick={handleSave}
                    disabled={isSaving || !hasChanges}
                  >
                    {isSaving ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="mr-2 h-4 w-4" />
                    )}
                    Save
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Rule metadata */}
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium">Rule Name</label>
                  <input
                    type="text"
                    value={ruleName}
                    onChange={(e) => {
                      setRuleName(e.target.value)
                      setHasChanges(true)
                    }}
                    className="w-full px-3 py-2 text-sm rounded-md border bg-background"
                    placeholder="Enter rule name"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-medium">Description</label>
                  <input
                    type="text"
                    value={ruleDescription}
                    onChange={(e) => {
                      setRuleDescription(e.target.value)
                      setHasChanges(true)
                    }}
                    className="w-full px-3 py-2 text-sm rounded-md border bg-background"
                    placeholder="Optional description"
                  />
                </div>
              </div>

              {/* YAML Editor */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium">Rules YAML</label>
                <textarea
                  value={yamlContent}
                  onChange={(e) => handleYamlChange(e.target.value)}
                  className="w-full h-96 px-3 py-2 text-sm font-mono rounded-md border bg-background resize-none"
                  placeholder="Enter validation rules in YAML format..."
                  spellCheck={false}
                />
              </div>
            </CardContent>
          </Card>

          {/* Help Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium">Quick Reference</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 sm:grid-cols-2 text-xs">
                <div className="space-y-2">
                  <h4 className="font-medium">Column Constraints</h4>
                  <ul className="space-y-1 text-muted-foreground">
                    <li><code className="text-primary">not_null: true</code> - No nulls allowed</li>
                    <li><code className="text-primary">unique: true</code> - Values must be unique</li>
                    <li><code className="text-primary">min: 0</code> - Minimum value</li>
                    <li><code className="text-primary">max: 100</code> - Maximum value</li>
                  </ul>
                </div>
                <div className="space-y-2">
                  <h4 className="font-medium">String Constraints</h4>
                  <ul className="space-y-1 text-muted-foreground">
                    <li><code className="text-primary">pattern: "regex"</code> - Match pattern</li>
                    <li><code className="text-primary">min_length: 1</code> - Min string length</li>
                    <li><code className="text-primary">max_length: 255</code> - Max string length</li>
                    <li><code className="text-primary">allowed_values: [a, b]</code> - Enum</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
