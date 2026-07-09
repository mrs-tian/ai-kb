<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import ChatBubble from '@/components/ChatBubble.vue'
import ReferenceList from '@/components/ReferenceList.vue'
import {
  askQuestion,
  fetchSessionMessages,
  getStoredSessionId,
  saveSessionId,
} from '@/api/chat'
import { requireAuth } from '@/utils/auth'
import type { ChatUiMessage, ReferenceItem } from '@/types'

const kbId = ref(0)
const kbName = ref('')
const input = ref('')
const sending = ref(false)
const scrollTop = ref(0)
const messages = ref<ChatUiMessage[]>([])
const sessionId = ref('')

function bumpScroll() {
  nextTick(() => {
    scrollTop.value = scrollTop.value + 9999
  })
}

async function loadHistory() {
  if (!sessionId.value) return
  try {
    const data = await fetchSessionMessages(sessionId.value)
    messages.value = data.messages.map((item, index) => ({
      id: `${item.role}-${index}`,
      role: item.role as 'user' | 'assistant',
      content: item.content,
      references: item.references,
    }))
    bumpScroll()
  } catch {
    // ignore invalid session
  }
}

onLoad((query) => {
  if (!requireAuth()) return
  kbId.value = Number(query?.kbId || 0)
  kbName.value = decodeURIComponent(String(query?.kbName || '知识库'))
  uni.setNavigationBarTitle({ title: kbName.value })
  sessionId.value = getStoredSessionId(kbId.value)
  loadHistory()
})

async function handleSend() {
  const question = input.value.trim()
  if (!question || sending.value || !kbId.value) return

  messages.value.push({
    id: `user-${Date.now()}`,
    role: 'user',
    content: question,
  })
  input.value = ''
  bumpScroll()

  const loadingId = `assistant-loading-${Date.now()}`
  messages.value.push({
    id: loadingId,
    role: 'assistant',
    content: '',
    loading: true,
  })
  bumpScroll()

  sending.value = true
  try {
    const data = await askQuestion({
      kb_id: kbId.value,
      question,
      session_id: sessionId.value || undefined,
    })
    sessionId.value = data.session_id
    saveSessionId(kbId.value, data.session_id)

    const index = messages.value.findIndex((item) => item.id === loadingId)
    if (index >= 0) {
      messages.value[index] = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: data.answer,
        references: data.references,
      }
    }
  } catch {
    const index = messages.value.findIndex((item) => item.id === loadingId)
    if (index >= 0) {
      messages.value[index] = {
        id: `assistant-error-${Date.now()}`,
        role: 'assistant',
        content: '抱歉，暂时无法回答，请稍后重试。',
      }
    }
  } finally {
    sending.value = false
    bumpScroll()
  }
}

function showRefs(refs?: ReferenceItem[]) {
  return refs && refs.length > 0
}
</script>

<template>
  <view class="page">
    <scroll-view class="chat-scroll" scroll-y :scroll-top="scrollTop" scroll-with-animation>
      <view v-if="!messages.length" class="empty">
        <text class="empty-title">开始提问吧</text>
        <text class="empty-sub">我会基于「{{ kbName }}」中的文档回答</text>
      </view>

      <view v-for="item in messages" :key="item.id" class="msg-block">
        <ChatBubble :role="item.role" :content="item.content" :loading="item.loading" />
        <ReferenceList v-if="showRefs(item.references)" :items="item.references || []" />
      </view>
    </scroll-view>

    <view class="input-bar">
      <input
        v-model="input"
        class="input"
        type="text"
        confirm-type="send"
        placeholder="输入你的问题..."
        :disabled="sending"
        @confirm="handleSend"
      />
      <button class="send-btn" :loading="sending" :disabled="sending" @click="handleSend">
        发送
      </button>
    </view>
  </view>
</template>

<style scoped>
.page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}
.chat-scroll {
  flex: 1;
  padding: 24rpx;
  box-sizing: border-box;
}
.empty {
  padding: 120rpx 40rpx;
  text-align: center;
}
.empty-title {
  display: block;
  font-size: 34rpx;
  color: #303133;
  font-weight: 600;
}
.empty-sub {
  display: block;
  margin-top: 12rpx;
  font-size: 26rpx;
  color: #909399;
}
.msg-block {
  margin-bottom: 8rpx;
}
.input-bar {
  display: flex;
  gap: 16rpx;
  padding: 16rpx 20rpx calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #ebeef5;
}
.input {
  flex: 1;
  height: 72rpx;
  padding: 0 24rpx;
  background: #f5f7fa;
  border-radius: 36rpx;
  font-size: 28rpx;
}
.send-btn {
  width: 140rpx;
  height: 72rpx;
  line-height: 72rpx;
  padding: 0;
  margin: 0;
  background: #409eff;
  color: #fff;
  font-size: 28rpx;
  border-radius: 36rpx;
}
.send-btn[disabled] {
  opacity: 0.6;
}
</style>
