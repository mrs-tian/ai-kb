<script setup lang="ts">
defineProps<{
  role: 'user' | 'assistant'
  content: string
  loading?: boolean
}>()
</script>

<template>
  <view class="bubble-row" :class="role">
    <view class="bubble">
      <text v-if="loading" class="loading-text">思考中...</text>
      <text v-else class="content">{{ content }}</text>
    </view>
  </view>
</template>

<style scoped>
.bubble-row {
  display: flex;
  margin-bottom: 24rpx;
}
.bubble-row.user {
  justify-content: flex-end;
}
.bubble-row.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 78%;
  padding: 20rpx 24rpx;
  border-radius: 20rpx;
  line-height: 1.6;
  font-size: 28rpx;
}
.user .bubble {
  background: #409eff;
  color: #fff;
  border-bottom-right-radius: 6rpx;
}
.assistant .bubble {
  background: #fff;
  color: #303133;
  border-bottom-left-radius: 6rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);
}
.loading-text {
  color: #909399;
}
.content {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
