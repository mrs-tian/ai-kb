import request from './request'
import type { ApiLogItem, PaginatedData } from '@/types'

export interface LogQueryParams {
  page?: number
  page_size?: number
  username?: string
  path_keyword?: string
  start_time?: string
  end_time?: string
}

export function fetchApiLogs(params: LogQueryParams) {
  return request.get<never, PaginatedData<ApiLogItem>>('/api/admin/logs', { params })
}

export function clearApiLogs(params: Omit<LogQueryParams, 'page' | 'page_size'>) {
  return request.delete<never, { deleted_count: number }>('/api/admin/logs', { params })
}
