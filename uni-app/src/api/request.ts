import { API_BASE_URL, getClientType } from '@/config/env'
import type { ApiResponse } from '@/types'

type HttpMethod = 'GET' | 'POST'

interface RequestOptions {
  method?: HttpMethod
  data?: Record<string, unknown>
}

export function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', data } = options

  return new Promise((resolve, reject) => {
    uni.request({
      url: `${API_BASE_URL}${path}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'X-Client-Type': getClientType(),
      },
      success(res) {
        const payload = res.data as ApiResponse<T>
        if (!payload || payload.code !== 0) {
          uni.showToast({
            title: payload?.message || '请求失败',
            icon: 'none',
          })
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
