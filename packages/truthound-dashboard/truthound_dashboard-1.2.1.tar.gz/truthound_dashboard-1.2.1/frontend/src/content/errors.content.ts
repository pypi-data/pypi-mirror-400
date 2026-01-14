/**
 * Error message translations.
 *
 * Centralized error messages for consistent error handling across the app.
 */
import { t, type Dictionary } from 'intlayer'

const errorsContent = {
  key: 'errors',
  content: {
    generic: t({
      en: 'An error occurred. Please try again.',
      ko: '오류가 발생했습니다. 다시 시도해 주세요.',
  }),
    notFound: t({
      en: 'The requested resource was not found.',
      ko: '요청한 리소스를 찾을 수 없습니다.',
  }),
    unauthorized: t({
      en: 'You are not authorized to perform this action.',
      ko: '이 작업을 수행할 권한이 없습니다.',
  }),
    validation: t({
      en: 'Please check your input and try again.',
      ko: '입력을 확인하고 다시 시도해 주세요.',
  }),
    network: t({
      en: 'Network error. Please check your connection.',
      ko: '네트워크 오류입니다. 연결을 확인해 주세요.',
  }),
    serverError: t({
      en: 'Server error. Please try again later.',
      ko: '서버 오류입니다. 나중에 다시 시도해 주세요.',
  }),
    loadFailed: t({
      en: 'Failed to load data',
      ko: '데이터를 불러오지 못했습니다',
  }),
  },
} satisfies Dictionary

export default errorsContent
