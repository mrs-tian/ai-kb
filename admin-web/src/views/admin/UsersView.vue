<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createUser, fetchUsers, resetUserPassword } from '@/api/users'
import type { AdminUserItem } from '@/types'

const loading = ref(false)
const items = ref<AdminUserItem[]>([])
const total = ref(0)
const createVisible = ref(false)
const resetVisible = ref(false)
const saving = ref(false)
const resetUserId = ref<number | null>(null)

const query = reactive({
  page: 1,
  page_size: 20,
  keyword: '',
})

const createForm = reactive({
  username: '',
  password: '',
  nickname: '',
  role: 'user' as 'admin' | 'user',
})

const resetForm = reactive({
  password: '',
})

async function loadUsers() {
  loading.value = true
  try {
    const data = await fetchUsers({
      page: query.page,
      page_size: query.page_size,
      keyword: query.keyword || undefined,
    })
    items.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  loadUsers()
}

function handlePageChange(page: number) {
  query.page = page
  loadUsers()
}

function openCreate() {
  createForm.username = ''
  createForm.password = ''
  createForm.nickname = ''
  createForm.role = 'user'
  createVisible.value = true
}

async function submitCreate() {
  if (!createForm.username.trim() || !createForm.password.trim()) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  saving.value = true
  try {
    await createUser({
      username: createForm.username.trim(),
      password: createForm.password,
      nickname: createForm.nickname.trim() || undefined,
      role: createForm.role,
    })
    createVisible.value = false
    ElMessage.success('用户已创建')
    loadUsers()
  } finally {
    saving.value = false
  }
}

function openReset(row: AdminUserItem) {
  resetUserId.value = row.id
  resetForm.password = ''
  resetVisible.value = true
}

async function submitReset() {
  if (!resetUserId.value || !resetForm.password.trim()) {
    ElMessage.warning('请输入新密码')
    return
  }
  saving.value = true
  try {
    await resetUserPassword(resetUserId.value, resetForm.password)
    resetVisible.value = false
    ElMessage.success('密码已重置')
  } finally {
    saving.value = false
  }
}

async function confirmReset(row: AdminUserItem) {
  await ElMessageBox.confirm(`确定重置用户「${row.username}」的密码？`, '提示', {
    type: 'warning',
  })
  openReset(row)
}

onMounted(loadUsers)
</script>

<template>
  <el-card v-loading="loading">
    <template #header>
      <div class="header-row">
        <span>用户管理</span>
        <el-button type="primary" @click="openCreate">新增用户</el-button>
      </div>
    </template>

    <el-form inline class="filter-form" @submit.prevent="handleSearch">
      <el-form-item label="关键词">
        <el-input v-model="query.keyword" clearable placeholder="用户名 / 昵称" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </el-form-item>
    </el-form>

    <el-table :data="items" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户名" />
      <el-table-column prop="nickname" label="昵称" />
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" size="small">
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
            {{ row.is_active ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="confirmReset(row)">重置密码</el-button>
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

  <el-dialog v-model="createVisible" title="新增用户" width="420px">
    <el-form label-width="80px">
      <el-form-item label="用户名" required>
        <el-input v-model="createForm.username" />
      </el-form-item>
      <el-form-item label="密码" required>
        <el-input v-model="createForm.password" type="password" show-password />
      </el-form-item>
      <el-form-item label="昵称">
        <el-input v-model="createForm.nickname" />
      </el-form-item>
      <el-form-item label="角色">
        <el-select v-model="createForm.role" style="width: 100%">
          <el-option label="普通用户" value="user" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="createVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitCreate">确定</el-button>
    </template>
  </el-dialog>

  <el-dialog v-model="resetVisible" title="重置密码" width="420px">
    <el-form label-width="80px">
      <el-form-item label="新密码" required>
        <el-input v-model="resetForm.password" type="password" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="resetVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submitReset">确定</el-button>
    </template>
  </el-dialog>
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
