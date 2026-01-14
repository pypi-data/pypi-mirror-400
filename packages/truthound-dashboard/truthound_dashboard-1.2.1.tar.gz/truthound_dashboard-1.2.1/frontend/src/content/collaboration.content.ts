/**
 * Collaboration (Comments & Activity) translations.
 *
 * Contains translations for comments and activity feed components.
 */
import { t, type Dictionary } from 'intlayer'

const collaborationContent = {
  key: 'collaboration',
  content: {
    // Comments
    comments: t({ en: 'Comments', ko: '댓글' }),
    addComment: t({ en: 'Add Comment', ko: '댓글 추가' }),
    editComment: t({ en: 'Edit', ko: '수정' }),
    deleteComment: t({ en: 'Delete', ko: '삭제' }),
    noComments: t({ en: 'No comments yet', ko: '댓글이 없습니다' }),
    writeComment: t({ en: 'Write a comment...', ko: '댓글을 작성하세요...' }),
    reply: t({ en: 'Reply', ko: '답글' }),
    replyTo: t({ en: 'Reply to comment', ko: '답글 작성' }),
    cancelReply: t({ en: 'Cancel', ko: '취소' }),
    postComment: t({ en: 'Post', ko: '등록' }),
    commentPosted: t({ en: 'Comment posted', ko: '댓글이 등록되었습니다' }),
    commentUpdated: t({ en: 'Comment updated', ko: '댓글이 수정되었습니다' }),
    commentDeleted: t({ en: 'Comment deleted', ko: '댓글이 삭제되었습니다' }),
    commentError: t({ en: 'Failed to post comment', ko: '댓글 등록에 실패했습니다' }),
    confirmDeleteComment: t({
      en: 'Are you sure you want to delete this comment?',
      ko: '이 댓글을 삭제하시겠습니까?',
    }),

    // Activity
    activity: t({ en: 'Activity', ko: '활동' }),
    recentActivity: t({ en: 'Recent Activity', ko: '최근 활동' }),
    allActivity: t({ en: 'All Activity', ko: '모든 활동' }),
    noActivity: t({ en: 'No activity recorded', ko: '기록된 활동이 없습니다' }),
    loadMore: t({ en: 'Load more', ko: '더 보기' }),

    // Activity actions
    actions: {
      created: t({ en: 'created', ko: '생성됨' }),
      updated: t({ en: 'updated', ko: '수정됨' }),
      deleted: t({ en: 'deleted', ko: '삭제됨' }),
      commented: t({ en: 'commented on', ko: '댓글 작성' }),
    },

    // Resource types
    resourceTypes: {
      term: t({ en: 'term', ko: '용어' }),
      asset: t({ en: 'asset', ko: '자산' }),
      column: t({ en: 'column', ko: '컬럼' }),
    },

    // Time ago
    timeAgo: {
      justNow: t({ en: 'Just now', ko: '방금 전' }),
      minutesAgo: t({ en: '{count} minutes ago', ko: '{count}분 전' }),
      hoursAgo: t({ en: '{count} hours ago', ko: '{count}시간 전' }),
      daysAgo: t({ en: '{count} days ago', ko: '{count}일 전' }),
      weeksAgo: t({ en: '{count} weeks ago', ko: '{count}주 전' }),
      monthsAgo: t({ en: '{count} months ago', ko: '{count}개월 전' }),
    },

    // Filters
    filterByResource: t({ en: 'Filter by resource', ko: '리소스 필터' }),
    allResources: t({ en: 'All resources', ko: '모든 리소스' }),
  },
} satisfies Dictionary

export default collaborationContent
