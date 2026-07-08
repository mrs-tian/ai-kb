<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { fetchChatMessages } from '@/api/chat'
import ChatBubble from '@/components/ChatBubble.vue'
import type { ChatMessage } from '@/types'

const route = useRoute()
const sessionId = route.params.sessionId as string
const loading = ref(false)
const title = ref('')
const messages = ref<ChatMessage[]>([])

async function loadMessages() {
  loading.value = true
  try {
    const data = await fetchChatMessages(sessionId)
    title.value = data.session.title || '对话详情'
    messages.value = data.messages
  } finally {
    loading.value = false
  }
}

onMounted(loadMessages)
</script>

<template>
  <el-card v-loading="loading">
    <template #header>{{ title }}</template>
    <el-empty v-if="!messages.length" description="暂无消息" />
    <ChatBubble
      v-for="msg in messages"
      :key="msg.id"
      :role="msg.role"
      :content="msg.content"
      :references="msg.references_json"
      :latency-ms="msg.latency_ms"
      :created-at="msg.created_at"
    />
  </el-card>
</template>
