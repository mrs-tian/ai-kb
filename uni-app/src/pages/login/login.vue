<script setup lang="ts">
import { reactive, ref } from 'vue'
import { loginAndFetchProfile } from '@/api/auth'
import { goKbList } from '@/utils/auth'

const loading = ref(false)
const form = reactive({
  username: '',
  password: '',
})

async function handleSubmit() {
  if (!form.username.trim() || !form.password.trim()) {
    uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
    return
  }
  loading.value = true
  try {
    await loginAndFetchProfile(form.username.trim(), form.password)
    uni.showToast({ title: '登录成功', icon: 'success' })
    setTimeout(() => goKbList(), 400)
  } finally {
    loading.value = false
  }
}

function goBack() {
  uni.navigateBack()
}
</script>

<template>
  <view class="page">
    <view class="glow" />
    <view class="card">
      <view class="brand">
        <view class="logo">智</view>
        <view>
          <text class="title">欢迎回来</text>
          <text class="sub">使用后台账号登录，开启知识库问答</text>
        </view>
      </view>

      <view class="field">
        <text class="label">用户名</text>
        <input
          v-model="form.username"
          class="input"
          type="text"
          placeholder="请输入用户名"
          placeholder-class="placeholder"
        />
      </view>
      <view class="field">
        <text class="label">密码</text>
        <input
          v-model="form.password"
          class="input"
          type="password"
          password
          placeholder="请输入密码"
          placeholder-class="placeholder"
          @confirm="handleSubmit"
        />
      </view>

      <button class="submit" :loading="loading" :disabled="loading" @click="handleSubmit">
        登录
      </button>

      <text class="back" @click="goBack">返回首页</text>
    </view>
  </view>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(160deg, #0f0c29, #1a1a2e);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40rpx;
  position: relative;
}
.glow {
  position: absolute;
  width: 500rpx;
  height: 500rpx;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.35), transparent 70%);
  top: 10%;
  left: 50%;
  transform: translateX(-50%);
}
.card {
  width: 100%;
  max-width: 640rpx;
  background: rgba(255, 255, 255, 0.06);
  border: 1rpx solid rgba(255, 255, 255, 0.12);
  border-radius: 32rpx;
  padding: 48rpx 40rpx;
  backdrop-filter: blur(12px);
  position: relative;
  z-index: 1;
}
.brand {
  display: flex;
  gap: 24rpx;
  align-items: center;
  margin-bottom: 48rpx;
}
.logo {
  width: 88rpx;
  height: 88rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #7c3aed, #2563eb);
  color: #fff;
  font-size: 40rpx;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
}
.title {
  display: block;
  font-size: 36rpx;
  font-weight: 700;
  color: #f8fafc;
}
.sub {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #94a3b8;
}
.field {
  margin-bottom: 28rpx;
}
.label {
  display: block;
  font-size: 24rpx;
  color: #cbd5e1;
  margin-bottom: 12rpx;
}
.input {
  height: 88rpx;
  padding: 0 28rpx;
  border-radius: 20rpx;
  background: rgba(15, 12, 41, 0.6);
  border: 1rpx solid rgba(148, 163, 184, 0.25);
  color: #f8fafc;
  font-size: 28rpx;
}
.placeholder {
  color: #64748b;
}
.submit {
  margin-top: 12rpx;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 44rpx;
  background: linear-gradient(135deg, #7c3aed, #2563eb);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
}
.back {
  display: block;
  margin-top: 20rpx;
  text-align: center;
  font-size: 26rpx;
  color: #a5b4fc;
}
</style>
