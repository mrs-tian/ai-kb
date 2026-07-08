<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const collapsed = ref(false)

const activeMenu = computed(() => route.path)
const asideWidth = computed(() => (collapsed.value ? '64px' : '220px'))

onMounted(() => {
  userStore.fetchProfile()
})

function handleLogout() {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout">
    <el-aside :width="asideWidth" class="aside">
      <div class="logo">{{ collapsed ? '智' : '智问知识库' }}</div>
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        router
        background-color="#001529"
        text-color="#fff"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/kb">
          <el-icon><Collection /></el-icon>
          <span>知识库</span>
        </el-menu-item>
        <el-menu-item index="/chats">
          <el-icon><ChatDotRound /></el-icon>
          <span>对话记录</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>AI 配置</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/logs">
          <el-icon><Document /></el-icon>
          <span>接口日志</span>
        </el-menu-item>
        <el-menu-item v-if="userStore.isAdmin" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-wrap" :style="{ marginLeft: asideWidth }">
      <el-header class="header">
        <el-button text @click="collapsed = !collapsed">
          <el-icon><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
        </el-button>
        <div class="header-right">
          <el-tag v-if="userStore.isAdmin" type="danger" size="small">管理员</el-tag>
          <span class="username">{{ userStore.user?.nickname || userStore.user?.username }}</span>
          <el-button type="primary" link @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout {
  height: 100vh;
  overflow: hidden;
}
.aside {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  background: #001529;
  transition: width 0.2s;
  overflow-x: hidden;
  overflow-y: auto;
}
.logo {
  height: 56px;
  line-height: 56px;
  text-align: center;
  color: #fff;
  font-weight: 600;
  font-size: 16px;
}
.main-wrap {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: margin-left 0.2s;
}
.header {
  flex-shrink: 0;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #eee;
  background: #fff;
  z-index: 10;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.username {
  color: #606266;
}
.main {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  background: #f5f7fa;
  padding: 16px;
}
</style>
