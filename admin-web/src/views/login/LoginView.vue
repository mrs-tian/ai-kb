<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const appTitle = import.meta.env.VITE_APP_TITLE || '智问 · AI 知识库'

const form = reactive({
  username: '',
  password: '',
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleSubmit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-bg" />
    <el-card class="login-card" shadow="always">
      <div class="brand">
        <div class="brand-icon">智</div>
        <div>
          <h1>{{ appTitle }}</h1>
          <p>登录后管理知识库与 AI 问答</p>
        </div>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleSubmit">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            prefix-icon="User"
            autocomplete="username"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            show-password
            autocomplete="current-password"
            @keyup.enter="handleSubmit"
          />
        </el-form-item>
        <el-button type="primary" class="submit-btn" size="large" :loading="loading" native-type="submit">
          登录
        </el-button>
      </el-form>

      <p class="hint">Demo 默认管理员：admin / demo123456</p>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: #0f172a;
}
.login-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 20% 20%, rgba(64, 158, 255, 0.35), transparent 40%),
    radial-gradient(circle at 80% 80%, rgba(118, 75, 162, 0.35), transparent 40%);
}
.login-card {
  width: 420px;
  padding: 8px 8px 16px;
  position: relative;
  z-index: 1;
  border: none;
}
.brand {
  display: flex;
  gap: 14px;
  align-items: center;
  margin-bottom: 28px;
}
.brand-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409eff, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
}
h1 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}
.brand p {
  margin: 4px 0 0;
  color: #909399;
  font-size: 13px;
}
.submit-btn {
  width: 100%;
  margin-top: 4px;
}
.hint {
  margin: 16px 0 0;
  text-align: center;
  color: #909399;
  font-size: 12px;
}
</style>
