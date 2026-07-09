const configured = import.meta.env.VITE_API_BASE_URL as string | undefined

export const API_BASE_URL =
  configured && configured.length > 0 ? configured : 'https://www.easytransfer.top'

export function getClientType(): string {
  // #ifdef H5
  return 'h5'
  // #endif
  // #ifdef MP-WEIXIN
  return 'mp-weixin'
  // #endif
  return 'unknown'
}
