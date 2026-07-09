import { request } from '@/api/request'
import { setStoredUser, setToken, type StoredUser } from '@/utils/auth'

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export function login(username: string, password: string) {
  return request<LoginResponse>('/api/admin/auth/login', {
    method: 'POST',
    data: { username, password },
    skipAuth: true,
  }).then((data) => {
    setToken(data.access_token)
    return data
  })
}

export function fetchMe() {
  return request<StoredUser>('/api/admin/auth/me')
}

export async function loginAndFetchProfile(username: string, password: string) {
  await login(username, password)
  const profile = await fetchMe()
  setStoredUser(profile)
  return profile
}
