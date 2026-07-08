import request from './request'
import type { AiConfig, AiProviderOption, PaginatedData } from '@/types'

export function fetchAiConfig() {
  return request.get<never, AiConfig>('/api/admin/auth/ai-config')
}

export function updateAiConfig(payload: { ai_provider: string; api_key: string }) {
  return request.put<never, AiConfig>('/api/admin/auth/ai-config', payload)
}

export function fetchAiProviders() {
  return request.get<never, AiProviderOption[]>('/api/admin/auth/ai-providers')
}
