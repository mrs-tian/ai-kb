import request from './request'
import type { DocumentItem, PaginatedData } from '@/types'

export function fetchDocuments(kbId: number, params?: { page?: number; page_size?: number }) {
  return request.get<never, PaginatedData<DocumentItem>>(`/api/admin/kb/${kbId}/documents`, {
    params,
  })
}

export function uploadDocument(kbId: number, file: File) {
  const form = new FormData()
  form.append('file', file)
  return request.post<never, DocumentItem>(`/api/admin/kb/${kbId}/documents`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
}

export function deleteDocument(id: number) {
  return request.delete(`/api/admin/documents/${id}`)
}

export function reparseDocument(id: number) {
  return request.post<never, DocumentItem>(`/api/admin/documents/${id}/reparse`)
}
