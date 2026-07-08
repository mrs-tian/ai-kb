import request from './request'
import type { AdminUserItem, PaginatedData } from '@/types'

export function fetchUsers(params: { page?: number; page_size?: number; keyword?: string }) {
  return request.get<never, PaginatedData<AdminUserItem>>('/api/admin/users', { params })
}

export function createUser(payload: {
  username: string
  password: string
  nickname?: string
  role: 'admin' | 'user'
}) {
  return request.post<never, AdminUserItem>('/api/admin/users', payload)
}

export function resetUserPassword(userId: number, password: string) {
  return request.put<never, null>(`/api/admin/users/${userId}/password`, { password })
}
