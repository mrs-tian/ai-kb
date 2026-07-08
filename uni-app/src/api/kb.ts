import { request } from '@/api/request'
import type { PublicKbDetail, PublicKbItem } from '@/types'

export function fetchPublicKbList() {
  return request<{ items: PublicKbItem[] }>('/api/public/kb')
}

export function fetchPublicKbDetail(id: number) {
  return request<PublicKbDetail>(`/api/public/kb/${id}`)
}
