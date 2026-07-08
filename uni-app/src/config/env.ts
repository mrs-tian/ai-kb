export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

export function getClientType(): string {
  // #ifdef H5
  return 'h5'
  // #endif
  // #ifdef MP-WEIXIN
  return 'mp-weixin'
  // #endif
  return 'unknown'
}
