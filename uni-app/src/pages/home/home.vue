<script setup lang="ts">
import { onShow } from '@dcloudio/uni-app'
import { onMounted, ref } from 'vue'
import { getStoredUser, goKbList, isLoggedIn } from '@/utils/auth'

const visible = ref(false)
const loggedIn = ref(isLoggedIn())
const user = ref(getStoredUser())

function refreshAuth() {
  loggedIn.value = isLoggedIn()
  user.value = getStoredUser()
}

onMounted(() => {
  setTimeout(() => {
    visible.value = true
  }, 80)
})

onShow(refreshAuth)

function handleStart() {
  if (loggedIn.value) {
    goKbList()
    return
  }
  uni.navigateTo({ url: '/pages/login/login' })
}

function handleLogin() {
  uni.navigateTo({ url: '/pages/login/login' })
}
</script>

<template>
  <view class="page">
    <view class="orb orb-a" />
    <view class="orb orb-b" />
    <view class="orb orb-c" />
    <view class="grid-overlay" />

    <view class="content" :class="{ show: visible }">
      <view class="badge fade-up delay-1">企业级 RAG 知识库</view>
      <text class="title fade-up delay-2">智问</text>
      <text class="subtitle fade-up delay-3">让文档会思考，让问答有依据</text>
      <text class="desc fade-up delay-4">
        上传企业文档，自动分块向量化；基于知识库精准问答，每条回答附带引用来源，可追溯、可信赖。
      </text>

      <view class="cta-row fade-up delay-5">
        <button class="btn-primary" @click="handleStart">
          {{ loggedIn ? '进入知识库' : '立即体验' }}
        </button>
        <button v-if="!loggedIn" class="btn-ghost" @click="handleLogin">登录账号</button>
      </view>

      <view v-if="user" class="welcome fade-up delay-5">
        欢迎回来，{{ user.nickname || user.username }}
      </view>

      <view class="stats fade-up delay-6">
        <view class="stat-card">
          <text class="stat-num">RAG</text>
          <text class="stat-label">检索增强</text>
        </view>
        <view class="stat-card">
          <text class="stat-num">AI</text>
          <text class="stat-label">智能问答</text>
        </view>
        <view class="stat-card">
          <text class="stat-num">引用</text>
          <text class="stat-label">来源可追溯</text>
        </view>
      </view>

      <view class="section fade-up delay-7">
        <text class="section-title">核心能力</text>
        <view class="feature-list">
          <view class="feature-item float-card" style="animation-delay: 0s">
            <view class="feature-icon fi-1">📚</view>
            <view class="feature-body">
              <text class="feature-name">多知识库管理</text>
              <text class="feature-text">产品手册、FAQ、制度文档分库管理，按需开放</text>
            </view>
          </view>
          <view class="feature-item float-card" style="animation-delay: 0.15s">
            <view class="feature-icon fi-2">🔍</view>
            <view class="feature-body">
              <text class="feature-name">语义检索</text>
              <text class="feature-text">向量相似度匹配最相关片段，告别关键词搜索</text>
            </view>
          </view>
          <view class="feature-item float-card" style="animation-delay: 0.3s">
            <view class="feature-icon fi-3">💬</view>
            <view class="feature-body">
              <text class="feature-name">有据问答</text>
              <text class="feature-text">大模型仅依据参考资料回答，附文档片段引用</text>
            </view>
          </view>
        </view>
      </view>

      <view class="footer fade-up delay-8">
        <text>智问 · AI 知识库助手 · Demo</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(160deg, #0f0c29 0%, #1a1a2e 40%, #24243e 100%);
  position: relative;
  overflow: hidden;
}
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60rpx);
  opacity: 0.55;
  animation: drift 8s ease-in-out infinite alternate;
}
.orb-a {
  width: 360rpx;
  height: 360rpx;
  background: #7c3aed;
  top: -80rpx;
  right: -60rpx;
}
.orb-b {
  width: 280rpx;
  height: 280rpx;
  background: #2563eb;
  bottom: 200rpx;
  left: -80rpx;
  animation-delay: 1.2s;
}
.orb-c {
  width: 200rpx;
  height: 200rpx;
  background: #06b6d4;
  top: 45%;
  right: 10%;
  animation-delay: 2s;
}
.grid-overlay {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 48rpx 48rpx;
  opacity: 0.35;
  pointer-events: none;
}
.content {
  position: relative;
  z-index: 1;
  padding: 120rpx 40rpx 80rpx;
  opacity: 0;
  transform: translateY(24rpx);
  transition: all 0.7s ease;
}
.content.show {
  opacity: 1;
  transform: translateY(0);
}
.badge {
  display: inline-block;
  padding: 10rpx 24rpx;
  border-radius: 999rpx;
  background: rgba(124, 58, 237, 0.25);
  border: 1rpx solid rgba(167, 139, 250, 0.45);
  color: #c4b5fd;
  font-size: 22rpx;
  letter-spacing: 2rpx;
}
.title {
  display: block;
  margin-top: 28rpx;
  font-size: 96rpx;
  font-weight: 800;
  line-height: 1.1;
  background: linear-gradient(120deg, #fff 0%, #a5b4fc 50%, #67e8f9 100%);
  -webkit-background-clip: text;
  color: transparent;
  letter-spacing: 8rpx;
}
.subtitle {
  display: block;
  margin-top: 16rpx;
  font-size: 34rpx;
  color: #e2e8f0;
  font-weight: 600;
}
.desc {
  display: block;
  margin-top: 24rpx;
  font-size: 26rpx;
  line-height: 1.7;
  color: #94a3b8;
}
.cta-row {
  display: flex;
  gap: 20rpx;
  margin-top: 48rpx;
  flex-wrap: wrap;
}
.btn-primary {
  margin: 0;
  padding: 0 48rpx;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 44rpx;
  background: linear-gradient(135deg, #7c3aed, #2563eb);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
  box-shadow: 0 16rpx 40rpx rgba(124, 58, 237, 0.45);
  animation: pulse 2.4s ease-in-out infinite;
}
.btn-ghost {
  margin: 0;
  padding: 0 40rpx;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 44rpx;
  background: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
  font-size: 28rpx;
  border: 1rpx solid rgba(255, 255, 255, 0.18);
}
.welcome {
  margin-top: 20rpx;
  font-size: 24rpx;
  color: #a5b4fc;
}
.stats {
  display: flex;
  gap: 16rpx;
  margin-top: 56rpx;
}
.stat-card {
  flex: 1;
  padding: 24rpx 16rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.06);
  border: 1rpx solid rgba(255, 255, 255, 0.1);
  text-align: center;
  backdrop-filter: blur(8px);
}
.stat-num {
  display: block;
  font-size: 32rpx;
  font-weight: 700;
  color: #f8fafc;
}
.stat-label {
  display: block;
  margin-top: 6rpx;
  font-size: 22rpx;
  color: #94a3b8;
}
.section {
  margin-top: 64rpx;
}
.section-title {
  display: block;
  font-size: 30rpx;
  font-weight: 700;
  color: #f1f5f9;
  margin-bottom: 24rpx;
}
.feature-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.feature-item {
  display: flex;
  gap: 20rpx;
  padding: 28rpx;
  border-radius: 24rpx;
  background: rgba(15, 12, 41, 0.55);
  border: 1rpx solid rgba(148, 163, 184, 0.15);
}
.feature-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  flex-shrink: 0;
}
.fi-1 {
  background: rgba(124, 58, 237, 0.25);
}
.fi-2 {
  background: rgba(37, 99, 235, 0.25);
}
.fi-3 {
  background: rgba(6, 182, 212, 0.25);
}
.feature-name {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  color: #f8fafc;
}
.feature-text {
  display: block;
  margin-top: 8rpx;
  font-size: 24rpx;
  color: #94a3b8;
  line-height: 1.5;
}
.footer {
  margin-top: 72rpx;
  text-align: center;
  font-size: 22rpx;
  color: #64748b;
}
.fade-up {
  opacity: 0;
  transform: translateY(30rpx);
  animation: fadeUp 0.8s ease forwards;
}
.delay-1 { animation-delay: 0.1s; }
.delay-2 { animation-delay: 0.2s; }
.delay-3 { animation-delay: 0.3s; }
.delay-4 { animation-delay: 0.4s; }
.delay-5 { animation-delay: 0.5s; }
.delay-6 { animation-delay: 0.6s; }
.delay-7 { animation-delay: 0.7s; }
.delay-8 { animation-delay: 0.8s; }
.float-card {
  animation: floatCard 4s ease-in-out infinite;
}
@keyframes drift {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(20rpx, -30rpx) scale(1.08); }
}
@keyframes fadeUp {
  to { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
  0%, 100% { box-shadow: 0 16rpx 40rpx rgba(124, 58, 237, 0.35); }
  50% { box-shadow: 0 20rpx 56rpx rgba(124, 58, 237, 0.65); }
}
@keyframes floatCard {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8rpx); }
}
</style>
