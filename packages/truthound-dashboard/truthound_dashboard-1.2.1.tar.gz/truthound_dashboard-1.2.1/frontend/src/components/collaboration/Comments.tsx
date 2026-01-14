import { useEffect, useState, useCallback } from 'react'
import { useIntlayer } from '@/providers'
import { MessageSquare, Send, Reply, Trash2, Edit } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  getComments,
  createComment,
  updateComment,
  deleteComment,
  type Comment as CommentType,
  type ResourceType,
} from '@/api/client'
import { formatDate } from '@/lib/utils'
import { str } from '@/lib/intlayer-utils'
import { useToast } from '@/hooks/use-toast'
import { useConfirm } from '@/components/ConfirmDialog'

interface CommentsProps {
  resourceType: ResourceType
  resourceId: string
}

export function Comments({ resourceType, resourceId }: CommentsProps) {
  const collab = useIntlayer('collaboration')
  const common = useIntlayer('common')
  const { toast } = useToast()
  const { confirm, ConfirmDialog } = useConfirm()

  const [comments, setComments] = useState<CommentType[]>([])
  const [loading, setLoading] = useState(true)
  const [newComment, setNewComment] = useState('')
  const [replyTo, setReplyTo] = useState<string | null>(null)
  const [replyContent, setReplyContent] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editContent, setEditContent] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const loadComments = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getComments(resourceType, resourceId)
      setComments(data)
    } catch {
      toast({
        title: str(common.error),
        description: str(collab.commentError),
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [resourceType, resourceId, toast, common, collab])

  useEffect(() => {
    loadComments()
  }, [loadComments])

  const handleSubmit = async () => {
    if (!newComment.trim()) return

    setSubmitting(true)
    try {
      const comment = await createComment({
        resource_type: resourceType,
        resource_id: resourceId,
        content: newComment.trim(),
      })
      setComments([{ ...comment, replies: [] }, ...comments])
      setNewComment('')
      toast({
        title: str(common.success),
        description: str(collab.commentPosted),
      })
    } catch {
      toast({
        title: str(common.error),
        description: str(collab.commentError),
        variant: 'destructive',
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleReply = async () => {
    if (!replyTo || !replyContent.trim()) return

    setSubmitting(true)
    try {
      const reply = await createComment({
        resource_type: resourceType,
        resource_id: resourceId,
        content: replyContent.trim(),
        parent_id: replyTo,
      })
      setComments(
        comments.map((c) =>
          c.id === replyTo
            ? { ...c, replies: [...c.replies, { ...reply, replies: [] }] }
            : c
        )
      )
      setReplyTo(null)
      setReplyContent('')
      toast({
        title: str(common.success),
        description: str(collab.commentPosted),
      })
    } catch {
      toast({
        title: str(common.error),
        description: str(collab.commentError),
        variant: 'destructive',
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleUpdate = async () => {
    if (!editingId || !editContent.trim()) return

    setSubmitting(true)
    try {
      await updateComment(editingId, { content: editContent.trim() })
      setComments(
        comments.map((c) => {
          if (c.id === editingId) {
            return { ...c, content: editContent.trim() }
          }
          return {
            ...c,
            replies: c.replies.map((r) =>
              r.id === editingId ? { ...r, content: editContent.trim() } : r
            ),
          }
        })
      )
      setEditingId(null)
      setEditContent('')
      toast({
        title: str(common.success),
        description: str(collab.commentUpdated),
      })
    } catch {
      toast({
        title: str(common.error),
        description: str(collab.commentError),
        variant: 'destructive',
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: string) => {
    const confirmed = await confirm({
      title: str(collab.deleteComment),
      description: str(collab.confirmDeleteComment),
      confirmText: str(common.delete),
      variant: 'destructive',
    })
    if (!confirmed) return

    try {
      await deleteComment(id)
      setComments(
        comments
          .filter((c) => c.id !== id)
          .map((c) => ({
            ...c,
            replies: c.replies.filter((r) => r.id !== id),
          }))
      )
      toast({
        title: str(common.success),
        description: str(collab.commentDeleted),
      })
    } catch {
      toast({
        title: str(common.error),
        description: str(collab.commentError),
        variant: 'destructive',
      })
    }
  }

  const startEdit = (comment: CommentType) => {
    setEditingId(comment.id)
    setEditContent(comment.content)
    setReplyTo(null)
  }

  const renderComment = (comment: CommentType, isReply = false) => {
    const isEditing = editingId === comment.id

    return (
      <div
        key={comment.id}
        className={`${isReply ? 'ml-8 border-l-2 pl-4' : ''}`}
      >
        <div className="p-3 rounded-lg border bg-card">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 text-sm">
                <span className="font-medium">{comment.author_id || 'Anonymous'}</span>
                <span className="text-muted-foreground">·</span>
                <span className="text-muted-foreground">
                  {formatDate(comment.created_at)}
                </span>
              </div>
              {isEditing ? (
                <div className="mt-2 space-y-2">
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="w-full min-h-[60px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                    autoFocus
                  />
                  <div className="flex gap-2">
                    <Button size="sm" onClick={handleUpdate} disabled={submitting}>
                      {common.save}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        setEditingId(null)
                        setEditContent('')
                      }}
                    >
                      {common.cancel}
                    </Button>
                  </div>
                </div>
              ) : (
                <p className="mt-1 text-sm">{comment.content}</p>
              )}
            </div>
            {!isEditing && (
              <div className="flex items-center gap-1 ml-2">
                {!isReply && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-7 w-7"
                    onClick={() => {
                      setReplyTo(comment.id)
                      setEditingId(null)
                    }}
                  >
                    <Reply className="h-3 w-3" />
                  </Button>
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => startEdit(comment)}
                >
                  <Edit className="h-3 w-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={() => handleDelete(comment.id)}
                >
                  <Trash2 className="h-3 w-3 text-destructive" />
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* Reply input */}
        {replyTo === comment.id && (
          <div className="ml-8 mt-2 space-y-2">
            <textarea
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              placeholder={str(collab.replyTo)}
              className="w-full min-h-[60px] rounded-md border border-input bg-background px-3 py-2 text-sm"
              autoFocus
            />
            <div className="flex gap-2">
              <Button size="sm" onClick={handleReply} disabled={submitting}>
                {collab.reply}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => {
                  setReplyTo(null)
                  setReplyContent('')
                }}
              >
                {collab.cancelReply}
              </Button>
            </div>
          </div>
        )}

        {/* Replies */}
        {comment.replies.length > 0 && (
          <div className="mt-2 space-y-2">
            {comment.replies.map((reply) => renderComment(reply, true))}
          </div>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* New comment input */}
      <div className="space-y-2">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder={str(collab.writeComment)}
          className="w-full min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        />
        <div className="flex justify-end">
          <Button onClick={handleSubmit} disabled={submitting || !newComment.trim()}>
            <Send className="mr-2 h-4 w-4" />
            {collab.postComment}
          </Button>
        </div>
      </div>

      {/* Comments list */}
      {comments.length === 0 ? (
        <div className="text-center py-8">
          <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground/50 mb-2" />
          <p className="text-muted-foreground">{collab.noComments}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {comments.map((comment) => renderComment(comment))}
        </div>
      )}

      <ConfirmDialog />
    </div>
  )
}
