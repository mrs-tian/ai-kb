<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchChatSessions } from '@/api/chat'
import { fetchKbList } from '@/api/kb'
import type { ChatSession, KnowledgeBase } from '@/types'

const router = useRouter()
const loading = ref(false)
const tableData = ref<ChatSession[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const kbId = ref<number | undefined>()
const kbOptions = ref<KnowledgeBase[]>([])

async function loadKbOptions() {
  const data = await fetchKbList({ page: 1, page_size: 100 })
  kbOptions.value = data.items
}

async function loadList() {
  loading.value = true
  try {
    const data = await fetchChatSessions({
      page: page.value,
      page_size: pageSize.value,
      kb_id: kbId.value,
      keyword: keyword.value || undefined,
    })
    tableData.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadKbOptions()
  loadList()
})
</script>

<template>
  <el-card>
    <div class="toolbar">
      <el-select v-model="kbId" placeholder="知识库" clearable style="width: 200px">
        <el-option
          v-for="kb in kbOptions"
          :key="kb.id"
          :label="kb.name"
          :value="kb.id"
        />
      </el-select>
      <el-input
        v-model="keyword"
        placeholder="搜索标题/内容"
        clearable
        style="width: 240px"
        @keyup.enter="loadList"
      />
      <el-button type="primary" @click="loadList">搜索</el-button>
    </div>

    <el-table v-loading="loading" :data="tableData" stripe>
      <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
      <el-table-column prop="kb_name" label="知识库" width="160" />
      <el-table-column prop="client_type" label="来源" width="100">
        <template #default="{ row }">{{ row.client_type || '-' }}</template>
      </el-table-column>
      <el-table-column prop="message_count" label="消息数" width="90" />
      <el-table-column prop="created_at" label="时间" width="180" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="router.push(`/chats/${row.id}`)">
            查看
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="page"
      v-model:page-size="pageSize"
      class="pager"
      layout="total, prev, pager, next"
      :total="total"
      @change="loadList"
    />
  </el-card>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.pager {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
