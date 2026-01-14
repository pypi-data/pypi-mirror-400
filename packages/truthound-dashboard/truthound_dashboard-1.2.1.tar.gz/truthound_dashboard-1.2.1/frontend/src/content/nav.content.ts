/**
 * Navigation translations.
 *
 * Contains all sidebar and header navigation labels.
 */
import { t, type Dictionary } from 'intlayer'

const navContent = {
  key: 'nav',
  content: {
    dashboard: t({ en: 'Dashboard', ko: '대시보드' }),
    sources: t({ en: 'Data Sources', ko: '데이터 소스' }),
    catalog: t({ en: 'Catalog', ko: '카탈로그' }),
    glossary: t({ en: 'Glossary', ko: '용어집' }),
    rules: t({ en: 'Rules', ko: '규칙' }),
    validations: t({ en: 'Validations', ko: '검증' }),
    history: t({ en: 'History', ko: '히스토리' }),
    schedules: t({ en: 'Schedules', ko: '스케줄' }),
    activity: t({ en: 'Activity', ko: '활동' }),
    notifications: t({ en: 'Notifications', ko: '알림' }),
    profile: t({ en: 'Profile', ko: '프로필' }),
    drift: t({ en: 'Drift', ko: '드리프트' }),
    settings: t({ en: 'Settings', ko: '설정' }),
  },
} satisfies Dictionary

export default navContent
