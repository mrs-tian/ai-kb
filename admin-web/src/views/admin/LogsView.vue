<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { clearApiLogs, fetchApiLogs, type LogQueryParams } from '@/api/logs'
import type { ApiLogItem } from '@/types'

const loading = ref(false)
const clearing = ref(false)
const items = ref<ApiLogItem[]>([])
const total = ref(0)
const dateRange = ref<[Date, Date] | null>(null)

const query = reactive({
  page: 1,
  page_size: 20,
  username: '',
  path_keyword: '',
})

function buildFilterParams(): Omit<LogQueryParams, 'page' | 'page_size'> {
  const params: Omit<LogQueryParams, 'page' | 'page_size'> = {}
  if (query.username.trim()) params.username = query.username.trim()
  if (query.path_keyword.trim()) params.path_keyword = query.path_keyword.trim()
  if (dateRange.value) {
    params.start_time = dateRange.value[0].toISOString()
    params.end_time = dateRange.value[1].toISOString()
  }
  return params
}

function hasActiveFilters() {
  return Boolean(
    query.username.trim() ||
      query.path_keyword.trim() ||
      dateRange.value,
  )
}

function filterSummary() {
  const parts: string[] = []
  if (query.username.trim()) parts.push(`用户名含「${query.username.trim()}」`)
  if (query.path_keyword.trim()) parts.push(`路径含「${query.path_keyword.trim()}」`)
  if (dateRange.value) {
    const [start, end] = dateRange.value
    parts.push(
      `时间 ${start.toLocaleString()} ~ ${end.toLocaleString()}`,
    )
  }
  return parts.length ? parts.join('；') : '全部日志'
}

async function loadLogs() {
  loading.value = true
  try {
    const data = await fetchApiLogs({
      page: query.page,
      page_size: query.page_size,
      ...buildFilterParams(),
    })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  loadLogs()
}

function handleReset() {
  query.username = ''
  query.path_keyword = ''
  dateRange.value = null
  query.page = 1
  loadLogs()
}

function handlePageChange(page: number) {
  query.page = page
  loadLogs()
}

async function handleClear() {
  const scope = hasActiveFilters()
    ? `将按当前筛选条件清除日志：${filterSummary()}`
    : '未设置筛选条件，将清除全部接口日志'

  await ElMessageBox.confirm(`${scope}。此操作不可恢复，是否继续？`, '清除日志', {
    type: 'warning',
    confirmButtonText: '确认清除',
    cancelButtonText: '取消',
  })

  clearing.value = true
  try {
    const result = await clearApiLogs(buildFilterParams())
    ElMessage.success(`已清除 ${result.deleted_count} 条日志`)
    query.page = 1
    await loadLogs()
  } finally {
    clearing.value = false
  }
}

onMounted(loadLogs)
</script>

<template>
  <el-card v-loading="loading">
    <template #header>
      <div class="header-row">
        <span>接口请求日志</span>
        <el-button type="danger" plain :loading="clearing" @click="handleClear">
          清除日志
        </el-button>
      </div>
    </template>

    <el-form inline class="filter-form" @submit.prevent="handleSearch">
      <el-form-item label="用户名">
        <el-input v-model="query.username" clearable placeholder="用户名" />
      </el-form-item>
      <el-form-item label="路径">
        <el-input v-model="query.path_keyword" clearable placeholder="接口路径关键词" />
      </el-form-item>
      <el-form-item label="时间段">
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          :default-time="[new Date(2000, 0, 1, 0, 0, 0), new Date(2000, 0, 1, 23, 59, 59)]"
          style="width: 360px"
        />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="items" stripe>
      <el-table-column prop="created_at" label="时间" width="180" />
      <el-table-column prop="method" label="方法" width="80" />
      <el-table-column prop="path" label="路径" min-width="200" show-overflow-tooltip />
      <el-table-column label="用户" width="120">
        <template #default="{ row }">
          <span v-if="row.username">{{ row.username }}</span>
          <el-tag v-else type="info" size="small">未登录</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status_code < 400 ? 'success' : 'danger'" size="small">
            {{ row.status_code }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="duration_ms" label="耗时(ms)" width="100" />
      <el-table-column prop="client_ip" label="IP" width="130" />
      <el-table-column label="响应摘要" min-width="240" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.response_body || '-' }}
        </template>
      </el-table-column>
    </el-table>

    <div class="pager">
      <el-pagination
        background
        layout="total, prev, pager, next"
        :total="total"
        :page-size="query.page_size"
        :current-page="query.page"
        @current-change="handlePageChange"
      />
    </div>
  </el-card>
</template>

<style scoped>
.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.filter-form {
  margin-bottom: 16px;
}
.pager {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
