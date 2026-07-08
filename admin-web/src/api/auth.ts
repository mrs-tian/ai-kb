import request from './request'
import type { AdminUser, LoginResponse } from '@/types'

export function login(username: string, password: string) {
  return request.post<never, LoginResponse>('/api/admin/auth/login', {
    username,
    password,
  })
}

export function getMe() {
  return request.get<never, AdminUser>('/api/admin/auth/me')
}
