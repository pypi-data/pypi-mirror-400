/**
 * Data sources page translations.
 *
 * Contains translations for the data sources management page.
 */
import { t, type Dictionary } from 'intlayer'

const sourcesContent = {
  key: 'sources',
  content: {
    title: t({ en: 'Data Sources', ko: '데이터 소스',
  }),
    subtitle: t({
      en: 'Manage your data sources and validations',
      ko: '데이터 소스 및 검증 관리',
  }),

    // Actions
    addSource: t({ en: 'Add Source', ko: '소스 추가',
  }),
    addFirstSource: t({
      en: 'Add Your First Source',
      ko: '첫 번째 소스 추가하기',
  }),
    editSource: t({ en: 'Edit Source', ko: '소스 편집',
  }),
    deleteSource: t({ en: 'Delete Source', ko: '소스 삭제',
  }),

    // Empty states
    noSources: t({
      en: 'No data sources configured',
      ko: '설정된 데이터 소스가 없습니다',
  }),
    noSourcesYet: t({ en: 'No sources yet', ko: '소스가 없습니다',
  }),
    noSourcesDesc: t({
      en: 'Add your first data source to start monitoring data quality',
      ko: '데이터 품질 모니터링을 시작하려면 첫 번째 소스를 추가하세요',
  }),

    // Fields
    sourceName: t({ en: 'Source Name', ko: '소스 이름',
  }),
    sourceType: t({ en: 'Source Type', ko: '소스 유형',
  }),
    sourcePath: t({ en: 'Path / Connection', ko: '경로 / 연결',
  }),
    lastValidated: t({ en: 'Last validated', ko: '마지막 검증',
  }),
    never: t({ en: 'Never', ko: '없음',
  }),

    // Validation
    validate: t({ en: 'Validate', ko: '검증',
  }),
    loadError: t({ en: 'Failed to load sources', ko: '소스를 불러오지 못했습니다',
  }),
    deleteSuccess: t({
      en: 'Source deleted successfully',
      ko: '소스가 삭제되었습니다',
  }),
    deleteFailed: t({
      en: 'Failed to delete source',
      ko: '소스 삭제에 실패했습니다',
  }),
    validationStarted: t({ en: 'Validation Started', ko: '검증 시작',
  }),
    runningValidation: t({
      en: 'Running validation...',
      ko: '검증 실행 중...',
  }),
    validationPassed: t({ en: 'Validation Passed', ko: '검증 통과',
  }),
    validationFailed: t({ en: 'Validation Failed', ko: '검증 실패',
  }),
    validationError: t({
      en: 'Failed to run validation',
      ko: '검증 실행에 실패했습니다',
  }),

    // Confirmation
    confirmDelete: t({
      en: 'Are you sure you want to delete this source? This will also delete all related schemas, rules, and validations.',
      ko: '이 소스를 삭제하시겠습니까? 관련된 모든 스키마, 규칙, 검증 결과도 함께 삭제됩니다.',
  }),

    // Source types
    types: {
      file: t({ en: 'File', ko: '파일',
  }),
      csv: t({ en: 'CSV File', ko: 'CSV 파일',
  }),
      parquet: t({ en: 'Parquet File', ko: 'Parquet 파일',
  }),
      json: t({ en: 'JSON File', ko: 'JSON 파일',
  }),
      database: t({ en: 'Database', ko: '데이터베이스',
  }),
      postgresql: t({ en: 'PostgreSQL', ko: 'PostgreSQL',
  }),
      mysql: t({ en: 'MySQL', ko: 'MySQL',
  }),
      snowflake: t({ en: 'Snowflake', ko: 'Snowflake',
  }),
      bigquery: t({ en: 'BigQuery', ko: 'BigQuery',
  }),
    },
  },
} satisfies Dictionary

export default sourcesContent
