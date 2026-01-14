/**
 * Drift detection page translations.
 *
 * Contains translations for the drift detection and comparison page.
 */
import { t, type Dictionary } from 'intlayer'

const driftContent = {
  key: 'drift',
  content: {
    title: t({ en: 'Drift Detection', ko: '드리프트 감지',
  }),
    subtitle: t({
      en: 'Compare datasets to detect data drift',
      ko: '데이터셋을 비교하여 데이터 드리프트 감지',
  }),

    // Actions
    compare: t({ en: 'Compare', ko: '비교',
  }),
    comparing: t({ en: 'Comparing...', ko: '비교 중...',
  }),
    newComparison: t({ en: 'New Comparison', ko: '새 비교',
  }),
    compareDatasets: t({ en: 'Compare Datasets', ko: '데이터셋 비교',
  }),
    compareDescription: t({
      en: 'Select baseline and current datasets to compare for drift',
      ko: '드리프트 비교를 위한 기준 및 현재 데이터셋을 선택하세요',
  }),

    // Source selection
    baseline: t({ en: 'Baseline', ko: '기준',
  }),
    current: t({ en: 'Current', ko: '현재',
  }),
    selectSource: t({ en: 'Select source', ko: '소스 선택',
  }),
    baselineSource: t({ en: 'Baseline Source', ko: '기준 소스',
  }),
    currentSource: t({ en: 'Current Source', ko: '현재 소스',
  }),
    selectBaseline: t({ en: 'Select baseline...', ko: '기준 선택...',
  }),
    selectCurrent: t({ en: 'Select current...', ko: '현재 선택...',
  }),
    detectionMethod: t({ en: 'Detection Method', ko: '감지 방법',
  }),

    // Validation
    selectBothSources: t({
      en: 'Please select both baseline and current sources',
      ko: '기준 소스와 현재 소스를 모두 선택하세요',
  }),
    mustBeDifferent: t({
      en: 'Baseline and current sources must be different',
      ko: '기준 소스와 현재 소스가 서로 달라야 합니다',
  }),

    // Results
    comparisonComplete: t({ en: 'Comparison complete', ko: '비교 완료',
  }),
    comparisonFailed: t({ en: 'Comparison failed', ko: '비교 실패',
  }),
    noDriftDetected: t({
      en: 'No significant drift detected',
      ko: '유의미한 드리프트가 감지되지 않았습니다',
  }),

    // Empty states
    noComparisonsYet: t({ en: 'No comparisons yet', ko: '비교 기록 없음',
  }),
    noComparisonsDesc: t({
      en: 'Compare two datasets to detect data drift',
      ko: '두 데이터셋을 비교하여 데이터 드리프트를 감지하세요',
  }),

    // Drift status
    highDrift: t({ en: 'High Drift', ko: '높은 드리프트',
  }),
    driftDetected: t({ en: 'Drift Detected', ko: '드리프트 감지됨',
  }),
    noDrift: t({ en: 'No Drift', ko: '드리프트 없음',
  }),

    // Stats
    columnsCompared: t({ en: 'Columns Compared', ko: '비교된 컬럼',
  }),
    driftedColumns: t({ en: 'Drifted Columns', ko: '드리프트 컬럼',
  }),
    driftPercentage: t({ en: 'Drift Percentage', ko: '드리프트 비율',
  }),
    columnDetails: t({ en: 'Column Details', ko: '컬럼 상세',
  }),

    // Detection methods
    methods: {
      auto: t({ en: 'Auto (recommended)', ko: '자동 (권장)',
  }),
      ks: t({ en: 'Kolmogorov-Smirnov', ko: '콜모고로프-스미르노프',
  }),
      psi: t({ en: 'Population Stability Index', ko: '모집단 안정성 지수',
  }),
      chi2: t({ en: 'Chi-Square', ko: '카이제곱',
  }),
      js: t({ en: 'Jensen-Shannon', ko: '젠슨-샤논',
  }),
    },

    // Changes
    noChanges: t({ en: 'No changes detected', ko: '변경 사항이 없습니다',
  }),
    columnAdded: t({ en: 'Column Added', ko: '컬럼 추가됨',
  }),
    columnRemoved: t({ en: 'Column Removed', ko: '컬럼 제거됨',
  }),
    typeChanged: t({ en: 'Type Changed', ko: '타입 변경됨',
  }),
    statsChanged: t({ en: 'Statistics Changed', ko: '통계 변경됨',
  }),
  },
} satisfies Dictionary

export default driftContent
