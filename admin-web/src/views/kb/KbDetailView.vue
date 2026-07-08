<script setup lang="ts">
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadRequestOptions } from 'element-plus'
import { askQuestion } from '@/api/chat'
import { deleteDocument, fetchDocuments, reparseDocument, uploadDocument } from '@/api/document'
import { fetchKbDetail, updateKb } from '@/api/kb'
import ChatBubble from '@/components/ChatBubble.vue'
import type { DocumentItem, KnowledgeBase } from '@/types'

const route = useRoute()
const kbId = Number(route.params.id)
const loading = ref(false)
const kb = ref<KnowledgeBase | null>(null)
const documents = ref<DocumentItem[]>([])
const pollTimer = ref<number | null>(null)

const form = reactive({
  name: '',
  description: '',
  status: 'active' as 'active' | 'disabled',
  is_public: true,
})

const askPanel = ref(false)
const question = ref('')
const asking = ref(false)
const askResult = ref('')
const askRefs = ref<import('@/types').Reference[]>([])
const askSessionId = ref<string>()

const statusMap: Record<string, { label: string; type: string }> = {
  pending: { label: '待处理', type: 'info' },
  parsing: { label: '解析中', type: 'warning' },
  embedding: { label: '向量化', type: 'warning' },
  ready: { label: '就绪', type: 'success' },
  failed: { label: '失败', type: 'danger' },
}

function formatSize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

async function loadKb() {
  kb.value = await fetchKbDetail(kbId)
  form.name = kb.value.name
  form.description = kb.value.description || ''
  form.status = kb.value.status
  form.is_public = kb.value.is_public
}

async function loadDocuments() {
  const data = await fetchDocuments(kbId, { page: 1, page_size: 100 })
  documents.value = data.items
  const pending = data.items.some((doc) =>
    ['pending', 'parsing', 'embedding'].includes(doc.status),
  )
  if (pending && !pollTimer.value) {
    pollTimer.value = window.setInterval(loadDocuments, 3000)
    window.setTimeout(() => {
      if (pollTimer.value) {
        clearInterval(pollTimer.value)
        pollTimer.value = null
      }
    }, 120000)
  }
  if (!pending && pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

async function loadAll() {
  loading.value = true
  try {
    await Promise.all([loadKb(), loadDocuments()])
  } finally {
    loading.value = false
  }
}

async function saveKb() {
  await updateKb(kbId, form)
  ElMessage.success('保存成功')
  loadKb()
}

async function handleUpload(options: UploadRequestOptions) {
  await uploadDocument(kbId, options.file as File)
  ElMessage.success('上传成功')
  loadDocuments()
  loadKb()
}

async function handleDeleteDoc(row: DocumentItem) {
  await ElMessageBox.confirm(`确定删除文档「${row.filename}」？`, '提示', { type: 'warning' })
  await deleteDocument(row.id)
  ElMessage.success('删除成功')
  loadDocuments()
  loadKb()
}

async function handleReparse(row: DocumentItem) {
  await reparseDocument(row.id)
  ElMessage.success('已触发重新解析')
  loadDocuments()
}

async function handleAsk() {
  if (!question.value.trim()) return
  asking.value = true
  try {
    const data = await askQuestion({
      kb_id: kbId,
      question: question.value,
      session_id: askSessionId.value,
    })
    askSessionId.value = data.session_id
    askResult.value = data.answer
    askRefs.value = data.references
  } finally {
    asking.value = false
  }
}

onMounted(loadAll)
onUnmounted(() => {
  if (pollTimer.value) clearInterval(pollTimer.value)
})
</script>

<template>
  <div v-loading="loading">
    <el-card class="section">
      <template #header>基本信息</template>
      <el-form label-width="100px" style="max-width: 640px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="启用" value="active" />
            <el-option label="禁用" value="disabled" />
          </el-select>
        </el-form-item>
        <el-form-item label="C端可见">
          <el-switch v-model="form.is_public" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveKb">保存</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="section">
      <template #header>文档管理</template>
      <el-upload
        drag
        :show-file-list="false"
        accept=".txt,.md,.pdf"
        :http-request="handleUpload"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽或点击上传 txt / md / pdf</div>
      </el-upload>

      <el-table :data="documents" stripe class="doc-table">
        <el-table-column prop="filename" label="文件名" min-width="180" />
        <el-table-column label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="char_count" label="字符数" width="90" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="(statusMap[row.status]?.type as any) || 'info'">
              {{ statusMap[row.status]?.label || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="错误" min-width="160" show-overflow-tooltip>
          <template #default="{ row }">{{ row.error_message || '-' }}</template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="180" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'failed'"
              link
              type="primary"
              @click="handleReparse(row)"
            >
              重新解析
            </el-button>
            <el-button link type="danger" @click="handleDeleteDoc(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="section">
      <template #header>
        <div class="ask-header">
          <span>试问答</span>
          <el-button link type="primary" @click="askPanel = !askPanel">
            {{ askPanel ? '收起' : '展开' }}
          </el-button>
        </div>
      </template>
      <div v-show="askPanel">
        <el-input
          v-model="question"
          type="textarea"
          :rows="2"
          placeholder="输入问题，例如：如何重置密码？"
        />
        <el-button
          type="primary"
          class="ask-btn"
          :loading="asking"
          :disabled="!documents.some((d) => d.status === 'ready')"
          @click="handleAsk"
        >
          提问
        </el-button>
        <div v-if="askResult" class="ask-result">
          <ChatBubble role="assistant" :content="askResult" :references="askRefs" />
        </div>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.section {
  margin-bottom: 16px;
}
.doc-table {
  margin-top: 16px;
}
.ask-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ask-btn {
  margin-top: 12px;
}
.ask-result {
  margin-top: 16px;
}
</style>
