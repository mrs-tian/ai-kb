import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const TOKEN_KEY = 'token'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 60000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const payload = response.data
    if (payload?.code !== 0) {
      ElMessage.error(payload?.message || '请求失败')
      if (payload?.code === 40101) {
        localStorage.removeItem(TOKEN_KEY)
        router.push('/login')
      }
      return Promise.reject(payload)
    }
    return payload.data
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '网络错误'
    ElMessage.error(message)
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY)
      router.push('/login')
    }
    return Promise.reject(error)
  },
)

export { TOKEN_KEY }
export default request
