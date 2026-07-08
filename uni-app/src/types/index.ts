export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PublicKbItem {
  id: number
  name: string
  description?: string
}

export interface PublicKbDetail extends PublicKbItem {
  doc_count: number
}

export interface ReferenceItem {
  doc_id: number
  doc_name: string
  chunk_id: number
  snippet: string
  score: number
}

export interface ChatAskResponse {
  session_id: string
  answer: string
  references: ReferenceItem[]
  latency_ms: number
}

export interface ChatMessageItem {
  role: 'user' | 'assistant'
  content: string
  references?: ReferenceItem[]
  created_at?: string
}

export interface ChatUiMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  references?: ReferenceItem[]
  loading?: boolean
}
