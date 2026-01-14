/**
 * Schedules page translations.
 *
 * Contains translations for the schedule management page.
 */
import { t, type Dictionary } from 'intlayer'

const schedulesContent = {
  key: 'schedules',
  content: {
    title: t({ en: 'Schedules', ko: '스케줄',
  }),
    subtitle: t({
      en: 'Manage scheduled validation runs',
      ko: '예약된 검증 실행 관리',
  }),

    // Actions
    addSchedule: t({ en: 'Add Schedule', ko: '스케줄 추가',
  }),
    newSchedule: t({ en: 'New Schedule', ko: '새 스케줄',
  }),
    editSchedule: t({ en: 'Edit Schedule', ko: '스케줄 편집',
  }),
    createSchedule: t({ en: 'Create Schedule', ko: '스케줄 생성',
  }),
    createScheduleDesc: t({
      en: 'Set up automated validation runs for a data source',
      ko: '데이터 소스의 자동 검증 실행 설정',
  }),

    // Empty states
    noSchedules: t({
      en: 'No schedules configured',
      ko: '설정된 스케줄이 없습니다',
  }),
    noSchedulesYet: t({ en: 'No schedules yet', ko: '스케줄이 없습니다',
  }),
    noSchedulesDesc: t({
      en: 'Create a schedule to automate validation runs',
      ko: '검증 자동화를 위해 스케줄을 생성하세요',
  }),

    // Cron
    cronExpression: t({ en: 'Cron Expression', ko: 'Cron 표현식',
  }),
    cronFormat: t({
      en: 'Format: minute hour day month weekday',
      ko: '형식: 분 시 일 월 요일',
  }),
    customCron: t({
      en: 'Custom cron expression',
      ko: '사용자 정의 Cron 표현식',
  }),
    selectSource: t({ en: 'Select source...', ko: '소스 선택...',
  }),

    // Status
    lastRun: t({ en: 'Last Run', ko: '마지막 실행',
  }),
    nextRun: t({ en: 'Next Run', ko: '다음 실행',
  }),
    notifyOnFailure: t({ en: 'Notify on Failure', ko: '실패 시 알림',
  }),
    pause: t({ en: 'Pause', ko: '일시정지',
  }),
    resume: t({ en: 'Resume', ko: '재개',
  }),
    runNow: t({ en: 'Run Now', ko: '지금 실행',
  }),
    paused: t({ en: 'Paused', ko: '일시정지됨',
  }),
    active: t({ en: 'Active', ko: '활성',
  }),

    // Toasts
    scheduleCreated: t({ en: 'Schedule created', ko: '스케줄 생성됨',
  }),
    createFailed: t({
      en: 'Failed to create schedule',
      ko: '스케줄 생성 실패',
  }),
    deleted: t({ en: 'Schedule deleted', ko: '스케줄 삭제됨',
  }),
    deleteFailed: t({ en: 'Failed to delete', ko: '삭제 실패',
  }),
    schedulePaused: t({ en: 'Schedule paused', ko: '스케줄 일시정지됨',
  }),
    pauseFailed: t({ en: 'Failed to pause', ko: '일시정지 실패',
  }),
    scheduleResumed: t({ en: 'Schedule resumed', ko: '스케줄 재개됨',
  }),
    resumeFailed: t({ en: 'Failed to resume', ko: '재개 실패',
  }),
    validationTriggered: t({ en: 'Validation triggered', ko: '검증 실행됨',
  }),
    runFailed: t({ en: 'Failed to run', ko: '실행 실패',
  }),
    fillRequired: t({
      en: 'Please fill in all required fields',
      ko: '필수 항목을 모두 입력해주세요',
  }),
    creating: t({ en: 'Creating...', ko: '생성 중...',
  }),

    // Cron presets
    cronPresets: {
      everyHour: t({ en: 'Every hour', ko: '매시간',
  }),
      every6Hours: t({ en: 'Every 6 hours', ko: '6시간마다',
  }),
      dailyMidnight: t({ en: 'Daily at midnight', ko: '매일 자정',
  }),
      daily8am: t({ en: 'Daily at 8 AM', ko: '매일 오전 8시',
  }),
      everyMonday: t({ en: 'Every Monday', ko: '매주 월요일',
  }),
      everyMonth: t({ en: 'Every month', ko: '매월',
  }),
    },
  },
} satisfies Dictionary

export default schedulesContent
