<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createKb, deleteKb, fetchKbList, updateKb } from '@/api/kb'
import type { KnowledgeBase } from '@/types'

const router = useRouter()
const loading = ref(false)
const tableData = ref<KnowledgeBase[]>([])
const total = ref(0)
const keyword = ref('')
const page = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const editingId = ref<number | null>(null)

const form = reactive({
  name: '',
  description: '',
  is_public: true,
  status: 'active' as 'active' | 'disabled',
})

async function loadList() {
  loading.value = true
  try {
    const data = await fetchKbList({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || undefined,
    })
    tableData.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.name = ''
  form.description = ''
  form.is_public = true
  form.status = 'active'
  dialogVisible.value = true
}

function openEdit(row: KnowledgeBase) {
  editingId.value = row.id
  form.name = row.name
  form.description = row.description || ''
  form.is_public = row.is_public
  form.status = row.status
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.name.trim()) {
    ElMessage.warning('请输入名称')
    return
  }
  if (editingId.value) {
    await updateKb(editingId.value, form)
    ElMessage.success('更新成功')
  } else {
    await createKb(form)
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
  loadList()
}

async function handleDelete(row: KnowledgeBase) {
  await ElMessageBox.confirm(`确定删除知识库「${row.name}」？`, '提示', { type: 'warning' })
  await deleteKb(row.id)
  ElMessage.success('删除成功')
  loadList()
}

onMounted(loadList)
</script>

<template>
  <el-card>
    <div class="toolbar">
      <el-input
        v-model="keyword"
        placeholder="搜索名称"
        clearable
        style="width: 240px"
        @keyup.enter="loadList"
      />
      <el-button type="primary" @click="loadList">搜索</el-button>
      <el-button type="primary" @click="openCreate">新建知识库</el-button>
    </div>

    <el-table v-loading="loading" :data="tableData" stripe>
      <el-table-column prop="name" label="名称" min-width="160" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="doc_count" label="文档数" width="90" />
      <el-table-column prop="chunk_count" label="分块数" width="90" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="C端可见" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_public ? 'primary' : 'info'">
            {{ row.is_public ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="router.push(`/kb/${row.id}`)">详情</el-button>
          <el-button link @click="openEdit(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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

  <el-dialog v-model="dialogVisible" :title="editingId ? '编辑知识库' : '新建知识库'" width="480px">
    <el-form label-width="90px">
      <el-form-item label="名称" required>
        <el-input v-model="form.name" />
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item v-if="editingId" label="状态">
        <el-select v-model="form.status">
          <el-option label="启用" value="active" />
          <el-option label="禁用" value="disabled" />
        </el-select>
      </el-form-item>
      <el-form-item label="C端可见">
        <el-switch v-model="form.is_public" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit">保存</el-button>
    </template>
  </el-dialog>
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
