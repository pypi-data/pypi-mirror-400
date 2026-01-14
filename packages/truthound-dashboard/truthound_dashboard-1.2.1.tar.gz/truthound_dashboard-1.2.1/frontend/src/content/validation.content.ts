/**
 * Validation related translations.
 *
 * Contains translations for validation status, results, and severity levels.
 */
import { t, type Dictionary } from 'intlayer'

const validationContent = {
  key: 'validation',
  content: {
    title: t({ en: 'Validations', ko: '검증',
  }),
    run: t({ en: 'Run Validation', ko: '검증 실행',
  }),
    running: t({ en: 'Running...', ko: '실행 중...',
  }),

    // Status
    passed: t({ en: 'Passed', ko: '통과',
  }),
    failed: t({ en: 'Failed', ko: '실패',
  }),
    error: t({ en: 'Error', ko: '오류',
  }),
    pending: t({ en: 'Pending', ko: '대기 중',
  }),
    success: t({ en: 'Passed', ko: '통과',
  }),
    warning: t({ en: 'Warning', ko: '경고',
  }),

    // Stats
    passRate: t({ en: 'Pass Rate', ko: '통과율',
  }),
    totalRules: t({ en: 'Total Rules', ko: '전체 규칙',
  }),
    duration: t({ en: 'Duration', ko: '소요 시간',
  }),

    // Issues
    totalIssues: t({ en: 'Total Issues', ko: '전체 이슈',
  }),
    criticalIssues: t({ en: 'Critical Issues', ko: '심각한 이슈',
  }),
    highIssues: t({ en: 'High Issues', ko: '높은 이슈',
  }),
    mediumIssues: t({ en: 'Medium Issues', ko: '중간 이슈',
  }),
    lowIssues: t({ en: 'Low Issues', ko: '낮은 이슈',
  }),
    noIssues: t({ en: 'No issues found', ko: '발견된 이슈가 없습니다',
  }),
    viewDetails: t({ en: 'View Details', ko: '상세 보기',
  }),

    // Severity levels
    severity: {
      critical: t({ en: 'Critical', ko: '심각',
  }),
      high: t({ en: 'High', ko: '높음',
  }),
      medium: t({ en: 'Medium', ko: '중간',
  }),
      low: t({ en: 'Low', ko: '낮음',
  }),
    },
  },
} satisfies Dictionary

export default validationContent
