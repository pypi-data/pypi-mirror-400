/**
 * Demo banner translations.
 *
 * Contains translations for the demo mode banner shown in mock mode.
 */
import { t, type Dictionary } from 'intlayer'

const demoContent = {
  key: 'demo',
  content: {
    title: t({ en: 'Demo Mode', ko: '데모 모드',
  }),
    description: t({
      en: 'This is a demo with simulated data. No backend required.',
      ko: '시뮬레이션 데이터로 실행 중입니다. 백엔드가 필요하지 않습니다.',
  }),
    dismiss: t({ en: 'Dismiss banner', ko: '배너 닫기',
  }),
  },
} satisfies Dictionary

export default demoContent
