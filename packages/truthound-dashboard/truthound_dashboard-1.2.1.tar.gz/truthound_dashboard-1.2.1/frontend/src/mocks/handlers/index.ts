/**
 * MSW Handlers - centralized exports
 */

import { healthHandlers } from './health'
import { sourcesHandlers } from './sources'
import { validationsHandlers } from './validations'
import { schemasHandlers } from './schemas'
import { profileHandlers } from './profile'
import { historyHandlers } from './history'
import { driftHandlers } from './drift'
import { schedulesHandlers } from './schedules'
import { notificationsHandlers } from './notifications'
import { glossaryHandlers } from './glossary'
import { catalogHandlers } from './catalog'
import { collaborationHandlers } from './collaboration'

export const handlers = [
  ...healthHandlers,
  ...sourcesHandlers,
  ...validationsHandlers,
  ...schemasHandlers,
  ...profileHandlers,
  ...historyHandlers,
  ...driftHandlers,
  ...schedulesHandlers,
  ...notificationsHandlers,
  ...glossaryHandlers,
  ...catalogHandlers,
  ...collaborationHandlers,
]
