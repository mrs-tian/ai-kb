<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchAiConfig, fetchAiProviders, updateAiConfig } from '@/api/ai-config'
import { fetchSettings } from '@/api/stats'
import type { AiConfig, AiProviderOption, SettingsData } from '@/types'

const loading = ref(false)
const saving = ref(false)
const settings = ref<SettingsData | null>(null)
const aiConfig = ref<AiConfig | null>(null)
const providers = ref<AiProviderOption[]>([])

const form = reactive({
  ai_provider: 'deepseek',
  api_key: '',
})

async function loadData() {
  loading.value = true
  try {
    const [settingsData, config, providerList] = await Promise.all([
      fetchSettings(),
      fetchAiConfig(),
      fetchAiProviders(),
    ])
    settings.value = settingsData
    aiConfig.value = config
    providers.value = providerList
    form.ai_provider = config.ai_provider || 'deepseek'
    form.api_key = ''
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!form.api_key.trim()) {
    ElMessage.warning('请输入 API Key')
    return
  }
  saving.value = true
  try {
    aiConfig.value = await updateAiConfig({
      ai_provider: form.ai_provider,
      api_key: form.api_key.trim(),
    })
    form.api_key = ''
    ElMessage.success('AI 配置已保存')
  } finally {
    saving.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <div v-loading="loading" class="settings-page">
    <el-card class="card">
      <template #header>AI 模型配置</template>
      <el-form label-width="120px" class="ai-form">
        <el-form-item label="模型提供商">
          <el-select v-model="form.ai_provider" style="width: 240px">
            <el-option
              v-for="item in providers"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="API Key">
          <el-input
            v-model="form.api_key"
            type="password"
            show-password
            placeholder="请输入您的 API Key"
            style="width: 360px"
          />
        </el-form-item>
        <el-form-item v-if="aiConfig?.api_key_configured" label="当前 Key">
          <el-input
            :model-value="aiConfig.api_key_masked || ''"
            readonly
            style="width: 360px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存配置</el-button>
        </el-form-item>
      </el-form>
      <el-alert
        type="info"
        :closable="false"
        title="API Key 由您自行填写并加密存储，保存后中间字符将以星号显示。"
      />
    </el-card>

    <el-card v-if="settings" class="card">
      <template #header>系统参数（只读）</template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="RAG Top K">{{ settings.rag_top_k }}</el-descriptions-item>
        <el-descriptions-item label="存储类型">{{ settings.storage_type }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.ai-form {
  max-width: 560px;
}
</style>
