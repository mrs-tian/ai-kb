<script setup lang="ts">
import type { ReferenceItem } from '@/types'

defineProps<{
  items: ReferenceItem[]
}>()
</script>

<template>
  <view v-if="items.length" class="refs">
    <text class="title">参考来源</text>
    <view v-for="item in items" :key="item.chunk_id" class="ref-item">
      <text class="doc-name">{{ item.doc_name }}</text>
      <text class="snippet">{{ item.snippet }}</text>
    </view>
  </view>
</template>

<style scoped>
.refs {
  margin: 8rpx 0 24rpx;
  padding: 20rpx;
  background: #f5f7fa;
  border-radius: 16rpx;
}
.title {
  display: block;
  font-size: 24rpx;
  color: #909399;
  margin-bottom: 12rpx;
}
.ref-item {
  margin-bottom: 12rpx;
}
.doc-name {
  display: block;
  font-size: 24rpx;
  color: #409eff;
  margin-bottom: 4rpx;
}
.snippet {
  font-size: 24rpx;
  color: #606266;
  line-height: 1.5;
}
</style>
