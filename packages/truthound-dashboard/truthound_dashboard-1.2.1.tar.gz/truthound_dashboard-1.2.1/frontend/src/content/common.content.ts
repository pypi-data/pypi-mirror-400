/**
 * Common UI translations used across the application.
 *
 * This file contains shared translations for buttons, labels, status messages,
 * and other commonly used UI elements.
 */
import { t, type Dictionary } from 'intlayer'

const commonContent = {
  key: 'common',
  content: {
    // Actions
    save: t({ en: 'Save', ko: '저장',
  }),
    cancel: t({ en: 'Cancel', ko: '취소',
  }),
    delete: t({ en: 'Delete', ko: '삭제',
  }),
    edit: t({ en: 'Edit', ko: '편집',
  }),
    add: t({ en: 'Add', ko: '추가',
  }),
    create: t({ en: 'Create', ko: '생성',
  }),
    update: t({ en: 'Update', ko: '수정',
  }),
    close: t({ en: 'Close', ko: '닫기',
  }),
    confirm: t({ en: 'Confirm', ko: '확인',
  }),

    // Status
    loading: t({ en: 'Loading...', ko: '로딩 중...',
  }),
    error: t({ en: 'Error', ko: '오류',
  }),
    success: t({ en: 'Success', ko: '성공',
  }),
    warning: t({ en: 'Warning', ko: '경고',
  }),
    info: t({ en: 'Info', ko: '정보',
  }),

    // Navigation
    search: t({ en: 'Search', ko: '검색',
  }),
    filter: t({ en: 'Filter', ko: '필터',
  }),
    refresh: t({ en: 'Refresh', ko: '새로고침',
  }),
    back: t({ en: 'Back', ko: '뒤로',
  }),
    next: t({ en: 'Next', ko: '다음',
  }),
    previous: t({ en: 'Previous', ko: '이전',
  }),

    // Boolean
    yes: t({ en: 'Yes', ko: '예',
  }),
    no: t({ en: 'No', ko: '아니오',
  }),
    all: t({ en: 'All', ko: '전체',
  }),
    none: t({ en: 'None', ko: '없음',
  }),

    // Labels
    actions: t({ en: 'Actions', ko: '작업',
  }),
    status: t({ en: 'Status', ko: '상태',
  }),
    name: t({ en: 'Name', ko: '이름',
  }),
    type: t({ en: 'Type', ko: '유형',
  }),
    description: t({ en: 'Description', ko: '설명',
  }),
    createdAt: t({ en: 'Created At', ko: '생성일',
  }),
    updatedAt: t({ en: 'Updated At', ko: '수정일',
  }),

    // Toggle states
    active: t({ en: 'Active', ko: '활성',
  }),
    inactive: t({ en: 'Inactive', ko: '비활성',
  }),
    enabled: t({ en: 'Enabled', ko: '활성화됨',
  }),
    disabled: t({ en: 'Disabled', ko: '비활성화됨',
  }),

    // Empty states
    noData: t({ en: 'No data available', ko: '데이터가 없습니다',
  }),
    noResults: t({ en: 'No results found', ko: '검색 결과가 없습니다',
  }),

    // Other
    retry: t({ en: 'Retry', ko: '다시 시도' }),
    source: t({ en: 'Source', ko: '소스' }),
    schedule: t({ en: 'Schedule', ko: '스케줄' }),
    never: t({ en: 'Never', ko: '없음' }),
    saving: t({ en: 'Saving...', ko: '저장 중...' }),
  },
} satisfies Dictionary

export default commonContent
