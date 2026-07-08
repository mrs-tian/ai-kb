<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchPublicKbList } from '@/api/kb'
import type { PublicKbItem } from '@/types'

const loading = ref(false)
const items = ref<PublicKbItem[]>([])

async function loadList() {
  loading.value = true
  try {
    const data = await fetchPublicKbList()
    items.value = data.items
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

function openChat(item: PublicKbItem) {
  uni.navigateTo({
    url: `/pages/chat/chat?kbId=${item.id}&kbName=${encodeURIComponent(item.name)}`,
  })
}

onMounted(loadList)
</script>

<template>
  <view class="page">
    <view class="hero">
      <text class="hero-title">智问 · AI 知识库</text>
      <text class="hero-sub">选择知识库，开始智能问答</text>
    </view>

    <view v-if="loading" class="state">加载中...</view>
    <view v-else-if="!items.length" class="state">暂无公开知识库</view>

    <view v-else class="list">
      <view v-for="item in items" :key="item.id" class="card" @click="openChat(item)">
        <view class="card-head">
          <text class="name">{{ item.name }}</text>
          <text class="arrow">›</text>
        </view>
        <text v-if="item.description" class="desc">{{ item.description }}</text>
        <text v-else class="desc muted">暂无描述</text>
      </view>
    </view>
  </view>
</template>

<style scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef4ff 0%, #f5f7fa 240rpx);
  padding: 24rpx;
}
.hero {
  padding: 32rpx 8rpx 24rpx;
}
.hero-title {
  display: block;
  font-size: 40rpx;
  font-weight: 700;
  color: #1a1a2e;
}
.hero-sub {
  display: block;
  margin-top: 8rpx;
  font-size: 26rpx;
  color: #909399;
}
.state {
  text-align: center;
  color: #909399;
  padding: 80rpx 0;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}
.card {
  background: #fff;
  border-radius: 20rpx;
  padding: 28rpx;
  box-shadow: 0 8rpx 24rpx rgba(64, 158, 255, 0.08);
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.name {
  font-size: 32rpx;
  font-weight: 600;
  color: #303133;
}
.arrow {
  font-size: 40rpx;
  color: #c0c4cc;
}
.desc {
  display: block;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: #606266;
  line-height: 1.5;
}
.muted {
  color: #c0c4cc;
}
</style>
