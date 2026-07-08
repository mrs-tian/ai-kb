import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getMe, login as loginApi } from '@/api/auth'
import { TOKEN_KEY } from '@/api/request'
import type { AdminUser } from '@/types'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref<AdminUser | null>(null)

  const isAdmin = computed(() => user.value?.role === 'admin')

  async function login(username: string, password: string) {
    const data = await loginApi(username, password)
    token.value = data.access_token
    localStorage.setItem(TOKEN_KEY, data.access_token)
    await fetchProfile()
  }

  async function fetchProfile() {
    if (!token.value) return
    user.value = await getMe()
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return { token, user, isAdmin, login, fetchProfile, logout }
})
