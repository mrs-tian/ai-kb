import request from './request'
import type { AiUsageTrendItem, ApiTrendItem, ChatTrendItem, SettingsData, StatsOverview } from '@/types'

export function fetchStatsOverview() {
  return request.get<never, StatsOverview>('/api/admin/stats/overview')
}

export function fetchChatTrend(days = 7) {
  return request.get<never, { items: ChatTrendItem[] }>('/api/admin/stats/chat-trend', {
    params: { days },
  })
}

export function fetchApiTrend(days = 7) {
  return request.get<never, { items: ApiTrendItem[] }>('/api/admin/stats/api-trend', {
    params: { days },
  })
}

export function fetchAiTrend(days = 7) {
  return request.get<never, { items: AiUsageTrendItem[] }>('/api/admin/stats/ai-trend', {
    params: { days },
  })
}

export function fetchSettings() {
  return request.get<never, SettingsData>('/api/admin/settings')
}
