/**
 * Notifications page translations.
 *
 * Contains translations for the notification management page.
 */
import { t, type Dictionary } from 'intlayer'

const notificationsContent = {
  key: 'notifications',
  content: {
    title: t({ en: 'Notifications', ko: '알림',
  }),
    subtitle: t({
      en: 'Configure notification channels and rules',
      ko: '알림 채널 및 규칙 설정',
  }),

    // Tabs
    channels: t({ en: 'Channels', ko: '채널',
  }),
    rules: t({ en: 'Rules', ko: '규칙',
  }),
    logs: t({ en: 'Logs', ko: '로그',
  }),

    // Actions
    addChannel: t({ en: 'Add Channel', ko: '채널 추가',
  }),
    addRule: t({ en: 'Add Rule', ko: '규칙 추가',
  }),
    editChannel: t({ en: 'Edit Channel', ko: '채널 편집',
  }),
    editRule: t({ en: 'Edit Rule', ko: '규칙 편집',
  }),
    testChannel: t({ en: 'Test', ko: '테스트',
  }),

    // Empty states
    noChannels: t({
      en: 'No notification channels configured',
      ko: '설정된 알림 채널이 없습니다',
  }),
    noRules: t({
      en: 'No notification rules configured',
      ko: '설정된 알림 규칙이 없습니다',
  }),
    noLogs: t({ en: 'No notification logs', ko: '알림 로그가 없습니다',
  }),

    // Channel types
    channelTypes: {
      slack: t({ en: 'Slack', ko: 'Slack',
  }),
      email: t({ en: 'Email', ko: '이메일',
  }),
      webhook: t({ en: 'Webhook', ko: '웹훅',
  }),
    },

    // Conditions
    conditions: {
      validation_failed: t({ en: 'Validation Failed', ko: '검증 실패',
  }),
      critical_issues: t({
        en: 'Critical Issues Detected',
        ko: '심각한 이슈 발견',
  }),
      high_issues: t({ en: 'High Severity Issues', ko: '높은 심각도 이슈',
  }),
      schedule_failed: t({ en: 'Schedule Failed', ko: '스케줄 실패',
  }),
      drift_detected: t({ en: 'Drift Detected', ko: '드리프트 감지',
  }),
    },

    // Status messages
    testSuccess: t({
      en: 'Test notification sent successfully',
      ko: '테스트 알림이 성공적으로 전송되었습니다',
  }),
    testFailed: t({
      en: 'Failed to send test notification',
      ko: '테스트 알림 전송에 실패했습니다',
  }),
    sent: t({ en: 'Sent', ko: '전송됨',
  }),
    failed: t({ en: 'Failed', ko: '실패',
  }),

    // Delete channel
    deleteChannel: t({ en: 'Delete Channel', ko: '채널 삭제',
  }),
    deleteChannelConfirm: t({
      en: 'Are you sure you want to delete this channel? This action cannot be undone.',
      ko: '이 채널을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.',
  }),
    channelDeleted: t({
      en: 'Channel deleted successfully',
      ko: '채널이 삭제되었습니다',
  }),
    deleteChannelFailed: t({
      en: 'Failed to delete channel',
      ko: '채널 삭제에 실패했습니다',
  }),

    // Delete rule
    deleteRule: t({ en: 'Delete Rule', ko: '규칙 삭제',
  }),
    deleteRuleConfirm: t({
      en: 'Are you sure you want to delete this rule? This action cannot be undone.',
      ko: '이 규칙을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.',
  }),
    ruleDeleted: t({
      en: 'Rule deleted successfully',
      ko: '규칙이 삭제되었습니다',
  }),
    deleteRuleFailed: t({
      en: 'Failed to delete rule',
      ko: '규칙 삭제에 실패했습니다',
  }),
  },
} satisfies Dictionary

export default notificationsContent
