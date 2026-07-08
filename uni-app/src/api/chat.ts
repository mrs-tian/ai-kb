import { request } from '@/api/request'
import type { ChatAskResponse, ChatMessageItem } from '@/types'

export function askQuestion(payload: {
  kb_id: number
  question: string
  session_id?: string
}) {
  return request<ChatAskResponse>('/api/public/chat', {
    method: 'POST',
    data: payload,
  })
}

export function fetchSessionMessages(sessionId: string) {
  return request<{
    session_id: string
    kb_id: number
    messages: ChatMessageItem[]
  }>(`/api/public/chat/sessions/${sessionId}/messages`)
}

export function getStoredSessionId(kbId: number): string {
  return uni.getStorageSync(`session_${kbId}`) || ''
}

export function saveSessionId(kbId: number, sessionId: string) {
  uni.setStorageSync(`session_${kbId}`, sessionId)
}
