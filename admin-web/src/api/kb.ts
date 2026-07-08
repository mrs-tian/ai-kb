import request from './request'
import type { KnowledgeBase, PaginatedData } from '@/types'

export function fetchKbList(params: {
  page?: number
  page_size?: number
  keyword?: string
}) {
  return request.get<never, PaginatedData<KnowledgeBase>>('/api/admin/kb', { params })
}

export function fetchKbDetail(id: number) {
  return request.get<never, KnowledgeBase>(`/api/admin/kb/${id}`)
}

export function createKb(data: {
  name: string
  description?: string
  is_public?: boolean
}) {
  return request.post<never, KnowledgeBase>('/api/admin/kb', data)
}

export function updateKb(
  id: number,
  data: Partial<{
    name: string
    description: string
    status: string
    is_public: boolean
  }>,
) {
  return request.put<never, KnowledgeBase>(`/api/admin/kb/${id}`, data)
}

export function deleteKb(id: number) {
  return request.delete(`/api/admin/kb/${id}`)
}
