/**
 * Dashboard page translations.
 *
 * Contains translations for the main dashboard overview page.
 */
import { t, type Dictionary } from 'intlayer'

const dashboardContent = {
  key: 'dashboard',
  content: {
    title: t({ en: 'Data Health Overview', ko: '데이터 품질 현황',
  }),
    subtitle: t({
      en: 'Data quality overview and monitoring',
      ko: '데이터 품질 개요 및 모니터링',
  }),

    // Stats cards
    totalSources: t({ en: 'Total Sources', ko: '전체 소스',
  }),
    configuredSources: t({
      en: 'Configured data sources',
      ko: '설정된 데이터 소스',
  }),
    passed: t({ en: 'Passed', ko: '통과',
  }),
    validationPassed: t({ en: 'Validation passed', ko: '검증 통과',
  }),
    failed: t({ en: 'Failed', ko: '실패',
  }),
    validationFailed: t({ en: 'Validation failed', ko: '검증 실패',
  }),
    pending: t({ en: 'Pending', ko: '대기 중',
  }),
    notValidated: t({ en: 'Not yet validated', ko: '검증 전',
  }),

    // Recent sources section
    recentSources: t({ en: 'Recent Sources', ko: '최근 소스',
  }),
    recentSourcesDesc: t({
      en: 'Your configured data sources',
      ko: '설정된 데이터 소스 목록',
  }),
    viewAll: t({ en: 'View All', ko: '전체 보기',
  }),
    noSources: t({
      en: 'No data sources configured yet',
      ko: '설정된 데이터 소스가 없습니다',
  }),
    addFirstSource: t({
      en: 'Add Your First Source',
      ko: '첫 번째 소스 추가하기',
  }),
    lastValidated: t({ en: 'Last validated', ko: '마지막 검증',
  }),
    loadError: t({
      en: 'Failed to load dashboard data',
      ko: '대시보드 데이터를 불러오지 못했습니다',
  }),

    // Additional stats
    sources: t({ en: 'Data Sources', ko: '데이터 소스',
  }),
    passRate: t({ en: 'Pass Rate', ko: '통과율',
  }),
    failedToday: t({ en: 'Failed Today', ko: '오늘 실패',
  }),
    scheduled: t({ en: 'Scheduled', ko: '스케줄됨',
  }),
    recentFailures: t({ en: 'Recent Failures', ko: '최근 실패',
  }),
    upcomingSchedules: t({ en: 'Upcoming Schedules', ko: '예정된 스케줄',
  }),
    noFailures: t({ en: 'No recent failures', ko: '최근 실패가 없습니다',
  }),
    noSchedules: t({
      en: 'No upcoming schedules',
      ko: '예정된 스케줄이 없습니다',
  }),
  },
} satisfies Dictionary

export default dashboardContent
