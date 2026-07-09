const TOKEN_KEY = 'access_token'
const USER_KEY = 'user_profile'

export interface StoredUser {
  id: number
  username: string
  nickname?: string | null
  role: string
}

export function getToken(): string {
  return uni.getStorageSync(TOKEN_KEY) || ''
}

export function setToken(token: string) {
  uni.setStorageSync(TOKEN_KEY, token)
}

export function clearAuth() {
  uni.removeStorageSync(TOKEN_KEY)
  uni.removeStorageSync(USER_KEY)
}

export function getStoredUser(): StoredUser | null {
  const raw = uni.getStorageSync(USER_KEY)
  return raw || null
}

export function setStoredUser(user: StoredUser) {
  uni.setStorageSync(USER_KEY, user)
}

export function isLoggedIn(): boolean {
  return Boolean(getToken())
}

export function requireAuth(): boolean {
  if (isLoggedIn()) return true
  uni.showToast({ title: '请先登录', icon: 'none' })
  setTimeout(() => {
    uni.navigateTo({ url: '/pages/login/login' })
  }, 300)
  return false
}

export function goKbList() {
  uni.navigateTo({ url: '/pages/kb/list' })
}

export function goHome() {
  uni.reLaunch({ url: '/pages/home/home' })
}

export function logout() {
  clearAuth()
  goHome()
}
