import request from './request'
import type {
  AskResponse,
  ChatMessage,
  ChatSession,
  PaginatedData,
} from '@/types'

export function fetchChatSessions(params: {
  page?: number
  page_size?: number
  kb_id?: number
  keyword?: string
}) {
  return request.get<never, PaginatedData<ChatSession>>('/api/admin/chats/sessions', { params })
}

export function fetchChatMessages(sessionId: string) {
  return request.get<
    never,
    { session: { id: string; kb_id: number; title?: string }; messages: ChatMessage[] }
  >(`/api/admin/chats/sessions/${sessionId}/messages`)
}

export function askQuestion(data: {
  kb_id: number
  question: string
  session_id?: string
}) {
  return request.post<never, AskResponse>('/api/admin/chats/ask', data)
}
