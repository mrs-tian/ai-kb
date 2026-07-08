export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface KnowledgeBase {
  id: number
  name: string
  description?: string
  status: 'active' | 'disabled'
  is_public: boolean
  doc_count: number
  chunk_count: number
  created_at: string
  updated_at: string
}

export type DocumentStatus =
  | 'pending'
  | 'parsing'
  | 'embedding'
  | 'ready'
  | 'failed'

export interface DocumentItem {
  id: number
  kb_id: number
  filename: string
  file_ext: string
  file_size: number
  char_count: number
  status: DocumentStatus
  error_message?: string
  created_at: string
}

export interface ChatSession {
  id: string
  kb_id: number
  kb_name?: string
  title?: string
  client_type?: string
  message_count?: number
  created_at: string
}

export interface Reference {
  doc_id: number
  doc_name: string
  chunk_id: number
  snippet: string
  score: number
}

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  references_json?: Reference[]
  latency_ms?: number
  created_at: string
}

export interface StatsOverview {
  kb_count: number
  document_count: number
  chunk_count: number
  chat_count: number
  today_chat_count: number
  ai_estimated_tokens: number
  ai_estimated_cost: number
  ai_llm_calls: number
  ai_embedding_tokens: number
  ai_llm_tokens: number
  ai_today_cost: number
  api_success_rate: number
  api_total_requests: number
  api_failed_requests: number
  api_today_success_rate: number
  api_today_requests: number
}

export interface ApiTrendItem {
  date: string
  success_rate: number
  total: number
}

export interface AiUsageTrendItem {
  date: string
  estimated_tokens: number
  estimated_cost: number
}

export interface ChatTrendItem {
  date: string
  count: number
}

export interface SettingsData {
  rag_top_k: number
  storage_type: string
}

export interface AiConfig {
  ai_provider: string | null
  ai_provider_label: string | null
  api_key_masked: string | null
  api_key_configured: boolean
}

export interface AiProviderOption {
  value: string
  label: string
}

export interface AdminUserItem {
  id: number
  username: string
  nickname?: string
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}

export interface ApiLogItem {
  id: number
  method: string
  path: string
  query_string?: string
  status_code: number
  response_body?: string
  user_id?: number
  username?: string
  client_ip?: string
  duration_ms: number
  is_authenticated: boolean
  created_at: string
}

export interface AskResponse {
  session_id: string
  answer: string
  references: Reference[]
  latency_ms: number
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface AdminUser {
  id: number
  username: string
  nickname?: string
  role: 'admin' | 'user'
}
