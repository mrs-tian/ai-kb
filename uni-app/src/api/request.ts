import { API_BASE_URL, getClientType } from '@/config/env'
import { clearAuth, getToken } from '@/utils/auth'
import type { ApiResponse } from '@/types'

type HttpMethod = 'GET' | 'POST'

interface RequestOptions {
  method?: HttpMethod
  data?: Record<string, unknown>
  skipAuth?: boolean
}

export function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', data, skipAuth = false } = options
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'X-Client-Type': getClientType(),
  }
  const token = getToken()
  if (!skipAuth && token) {
    headers.Authorization = `Bearer ${token}`
  }

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}${path}`,
      method,
      data,
      header: headers,
      success(res) {
        const payload = res.data as ApiResponse<T>
        if (!payload || payload.code !== 0) {
          if (payload?.code === 40101) {
            clearAuth()
            uni.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
            setTimeout(() => {
              uni.navigateTo({ url: '/pages/login/login' })
            }, 400)
          } else if (payload?.code === 42901) {
            uni.showToast({ title: payload.message || '今日 AI 额度已用完', icon: 'none', duration: 3000 })
          } else {
            uni.showToast({
              title: payload?.message || '请求失败',
              icon: 'none',
            })
          }
          reject(payload)
          return
        }
        resolve(payload.data)
      },
      fail(err) {
        uni.showToast({ title: '网络错误', icon: 'none' })
        reject(err)
      },
    })
  })
}
