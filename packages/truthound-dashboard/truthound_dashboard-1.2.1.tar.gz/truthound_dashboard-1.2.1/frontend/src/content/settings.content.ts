/**
 * Settings page translations.
 *
 * Contains translations for the settings page.
 */
import { t, type Dictionary } from 'intlayer'

const settingsContent = {
  key: 'settings',
  content: {
    title: t({ en: 'Settings', ko: '설정',
  }),
    general: t({ en: 'General', ko: '일반',
  }),
    appearance: t({ en: 'Appearance', ko: '외관',
  }),
    theme: t({ en: 'Theme', ko: '테마',
  }),
    language: t({ en: 'Language', ko: '언어',
  }),
    light: t({ en: 'Light', ko: '라이트',
  }),
    dark: t({ en: 'Dark', ko: '다크',
  }),
    system: t({ en: 'System', ko: '시스템',
  }),
  },
} satisfies Dictionary

export default settingsContent
