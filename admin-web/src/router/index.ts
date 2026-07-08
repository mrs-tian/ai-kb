import { createRouter, createWebHistory } from 'vue-router'
import { TOKEN_KEY } from '@/api/request'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
          meta: { title: '仪表盘' },
        },
        {
          path: 'kb',
          name: 'kb-list',
          component: () => import('@/views/kb/KbListView.vue'),
          meta: { title: '知识库' },
        },
        {
          path: 'kb/:id',
          name: 'kb-detail',
          component: () => import('@/views/kb/KbDetailView.vue'),
          meta: { title: '知识库详情' },
        },
        {
          path: 'chats',
          name: 'chat-list',
          component: () => import('@/views/chat/ChatListView.vue'),
          meta: { title: '对话记录' },
        },
        {
          path: 'chats/:sessionId',
          name: 'chat-detail',
          component: () => import('@/views/chat/ChatDetailView.vue'),
          meta: { title: '对话详情' },
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/settings/SettingsView.vue'),
          meta: { title: 'AI 配置' },
        },
        {
          path: 'logs',
          name: 'logs',
          component: () => import('@/views/admin/LogsView.vue'),
          meta: { title: '接口日志', requiresAdmin: true },
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('@/views/admin/UsersView.vue'),
          meta: { title: '用户管理', requiresAdmin: true },
        },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (!to.meta.public && !token) {
    return '/login'
  }
  if (to.path === '/login' && token) {
    return '/dashboard'
  }

  if (to.meta.requiresAdmin) {
    const userStore = useUserStore()
    if (!userStore.user) {
      await userStore.fetchProfile()
    }
    if (userStore.user?.role !== 'admin') {
      return '/dashboard'
    }
  }
})

export default router
