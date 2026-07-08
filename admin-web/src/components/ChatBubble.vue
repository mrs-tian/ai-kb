<script setup lang="ts">
import type { Reference } from '@/types'

defineProps<{
  role: 'user' | 'assistant'
  content: string
  references?: Reference[]
  latencyMs?: number
  createdAt?: string
}>()
</script>

<template>
  <div class="bubble-row" :class="role">
    <div class="bubble">
      <div class="content">{{ content }}</div>
      <div v-if="role === 'assistant' && references?.length" class="refs">
        <el-collapse>
          <el-collapse-item title="引用来源" name="refs">
            <div v-for="(ref, idx) in references" :key="idx" class="ref-item">
              <div class="ref-title">{{ ref.doc_name }} (score: {{ ref.score }})</div>
              <div class="ref-snippet">{{ ref.snippet }}</div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
      <div v-if="latencyMs || createdAt" class="meta">
        <span v-if="latencyMs">{{ latencyMs }}ms</span>
        <span v-if="createdAt">{{ createdAt }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bubble-row {
  display: flex;
  margin-bottom: 16px;
}
.bubble-row.user {
  justify-content: flex-end;
}
.bubble-row.assistant {
  justify-content: flex-start;
}
.bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.user .bubble {
  background: #409eff;
  color: #fff;
}
.content {
  white-space: pre-wrap;
  line-height: 1.6;
}
.refs {
  margin-top: 8px;
}
.ref-item {
  margin-bottom: 8px;
}
.ref-title {
  font-weight: 600;
  font-size: 13px;
}
.ref-snippet {
  color: #606266;
  font-size: 12px;
}
.meta {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 12px;
}
.user .meta {
  color: rgba(255, 255, 255, 0.8);
}
</style>
