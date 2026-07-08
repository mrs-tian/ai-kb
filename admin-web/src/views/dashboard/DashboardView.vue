<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import StatCard from '@/components/StatCard.vue'
import { fetchAiTrend, fetchApiTrend, fetchChatTrend, fetchStatsOverview } from '@/api/stats'
import type { StatsOverview } from '@/types'

const router = useRouter()
const loading = ref(false)
const overview = ref<StatsOverview | null>(null)
const chatChartRef = ref<HTMLDivElement>()
const apiChartRef = ref<HTMLDivElement>()
const aiChartRef = ref<HTMLDivElement>()
const gaugeChartRef = ref<HTMLDivElement>()
let chatChart: echarts.ECharts | null = null
let apiChart: echarts.ECharts | null = null
let aiChart: echarts.ECharts | null = null
let gaugeChart: echarts.ECharts | null = null

const aiCostText = computed(() => {
  const cost = overview.value?.ai_estimated_cost ?? 0
  return cost < 0.01 && cost > 0 ? '< ¥0.01' : `¥${cost.toFixed(2)}`
})

const aiTokensText = computed(() => {
  const tokens = overview.value?.ai_estimated_tokens ?? 0
  if (tokens >= 10000) return `${(tokens / 10000).toFixed(1)}万`
  return tokens.toLocaleString()
})

function formatRate(rate?: number) {
  return `${(rate ?? 100).toFixed(1)}%`
}

function resizeCharts() {
  chatChart?.resize()
  apiChart?.resize()
  aiChart?.resize()
  gaugeChart?.resize()
}

async function loadData() {
  loading.value = true
  try {
    overview.value = await fetchStatsOverview()
    const [chatTrend, apiTrend, aiTrend] = await Promise.all([
      fetchChatTrend(7),
      fetchApiTrend(7),
      fetchAiTrend(7),
    ])

    if (gaugeChartRef.value) {
      gaugeChart ??= echarts.init(gaugeChartRef.value)
      const rate = overview.value.api_success_rate
      gaugeChart.setOption({
        series: [
          {
            type: 'gauge',
            startAngle: 200,
            endAngle: -20,
            min: 0,
            max: 100,
            splitNumber: 5,
            radius: '90%',
            axisLine: {
              lineStyle: {
                width: 14,
                color: [
                  [0.6, '#f56c6c'],
                  [0.85, '#e6a23c'],
                  [1, '#67c23a'],
                ],
              },
            },
            pointer: { show: true, length: '55%', width: 5 },
            detail: {
              valueAnimation: true,
              formatter: '{value}%',
              fontSize: 28,
              fontWeight: 700,
              color: '#303133',
              offsetCenter: [0, '20%'],
            },
            data: [{ value: rate }],
          },
        ],
      })
    }

    if (chatChartRef.value) {
      chatChart ??= echarts.init(chatChartRef.value)
      chatChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 48, right: 24, top: 32, bottom: 32 },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: chatTrend.items.map((item) => item.date.slice(5)),
          axisLine: { lineStyle: { color: '#dcdfe6' } },
        },
        yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { type: 'dashed' } } },
        series: [
          {
            name: '提问数',
            type: 'line',
            smooth: true,
            symbol: 'circle',
            symbolSize: 8,
            data: chatTrend.items.map((item) => item.count),
            lineStyle: { width: 3, color: '#409eff' },
            itemStyle: { color: '#409eff' },
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(64,158,255,0.35)' },
                { offset: 1, color: 'rgba(64,158,255,0.02)' },
              ]),
            },
          },
        ],
      })
    }

    if (apiChartRef.value) {
      apiChart ??= echarts.init(apiChartRef.value)
      apiChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 48, right: 24, top: 32, bottom: 32 },
        xAxis: {
          type: 'category',
          data: apiTrend.items.map((item) => item.date.slice(5)),
        },
        yAxis: {
          type: 'value',
          min: 0,
          max: 100,
          axisLabel: { formatter: '{value}%' },
        },
        series: [
          {
            name: '成功率',
            type: 'bar',
            barWidth: 18,
            data: apiTrend.items.map((item) => item.success_rate),
            itemStyle: {
              borderRadius: [6, 6, 0, 0],
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: '#67c23a' },
                { offset: 1, color: '#95d475' },
              ]),
            },
          },
        ],
      })
    }

    if (aiChartRef.value) {
      aiChart ??= echarts.init(aiChartRef.value)
      aiChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 48, right: 24, top: 32, bottom: 32 },
        xAxis: {
          type: 'category',
          data: aiTrend.items.map((item) => item.date.slice(5)),
        },
        yAxis: { type: 'value' },
        series: [
          {
            name: 'AI 耗费(元)',
            type: 'line',
            smooth: true,
            data: aiTrend.items.map((item) => item.estimated_cost),
            lineStyle: { width: 3, color: '#9b59b6' },
            itemStyle: { color: '#9b59b6' },
            areaStyle: { opacity: 0.12, color: '#9b59b6' },
          },
        ],
      })
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  chatChart?.dispose()
  apiChart?.dispose()
  aiChart?.dispose()
  gaugeChart?.dispose()
})
</script>

<template>
  <div v-loading="loading" class="dashboard">
    <section class="hero">
      <div class="hero-content">
        <h2>智问 · 运营驾驶舱</h2>
        <p>知识库运行状态、AI 耗费与接口健康度一览</p>
      </div>
      <div class="hero-actions">
        <el-button type="primary" @click="router.push('/kb')">管理知识库</el-button>
        <el-button @click="router.push('/settings')">AI 配置</el-button>
      </div>
    </section>

    <el-row :gutter="16" class="stats-row">
      <el-col :xs="24" :sm="12" :lg="8" :xl="4">
        <StatCard
          variant="gradient-blue"
          title="知识库"
          :value="overview?.kb_count ?? 0"
          subtitle="活跃知识资产"
        >
          <template #icon><el-icon :size="20"><Collection /></el-icon></template>
        </StatCard>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8" :xl="4">
        <StatCard
          variant="gradient-green"
          title="文档"
          :value="overview?.document_count ?? 0"
          subtitle="已上传文档数"
        >
          <template #icon><el-icon :size="20"><Document /></el-icon></template>
        </StatCard>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8" :xl="4">
        <StatCard
          variant="gradient-orange"
          title="累计问答"
          :value="overview?.chat_count ?? 0"
          :subtitle="`今日 +${overview?.today_chat_count ?? 0}`"
        >
          <template #icon><el-icon :size="20"><ChatDotRound /></el-icon></template>
        </StatCard>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8" :xl="4">
        <StatCard
          variant="gradient-purple"
          title="AI 耗费"
          :value="aiCostText"
          :subtitle="`约 ${aiTokensText} tokens · ${overview?.ai_llm_calls ?? 0} 次调用`"
        >
          <template #icon><el-icon :size="20"><Coin /></el-icon></template>
        </StatCard>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8" :xl="4">
        <StatCard
          variant="gradient-red"
          title="接口成功率"
          :value="formatRate(overview?.api_success_rate)"
          :subtitle="`${overview?.api_total_requests ?? 0} 次请求 · ${overview?.api_failed_requests ?? 0} 次失败`"
        >
          <template #icon><el-icon :size="20"><CircleCheck /></el-icon></template>
        </StatCard>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="8" :xl="4">
        <StatCard
          variant="default"
          title="今日 AI 耗费"
          :value="`¥${(overview?.ai_today_cost ?? 0).toFixed(4)}`"
          :subtitle="`今日接口成功率 ${formatRate(overview?.api_today_success_rate)}`"
          color="#9b59b6"
        >
          <template #icon><el-icon :size="20"><TrendCharts /></el-icon></template>
        </StatCard>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="8">
        <el-card class="panel-card gauge-card" shadow="never">
          <template #header>
            <div class="panel-title">接口健康度</div>
          </template>
          <div ref="gaugeChartRef" class="gauge-chart" />
          <div class="gauge-meta">
            <span>今日 {{ overview?.api_today_requests ?? 0 }} 次请求</span>
            <span>失败 {{ overview?.api_failed_requests ?? 0 }} 次</span>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="16">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="panel-title">近 7 日提问趋势</div>
          </template>
          <div ref="chatChartRef" class="chart" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="chart-row">
      <el-col :xs="24" :lg="12">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="panel-title">近 7 日接口成功率</div>
          </template>
          <div ref="apiChartRef" class="chart" />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card class="panel-card" shadow="never">
          <template #header>
            <div class="panel-title">近 7 日 AI 耗费趋势</div>
          </template>
          <div ref="aiChartRef" class="chart" />
        </el-card>
      </el-col>
    </el-row>

    <el-card class="panel-card quick-card" shadow="never">
      <template #header>
        <div class="panel-title">快捷操作</div>
      </template>
      <el-space wrap>
        <el-button type="primary" @click="router.push('/kb')">新建知识库</el-button>
        <el-button @click="router.push('/chats')">查看对话记录</el-button>
        <el-button @click="router.push('/settings')">配置 AI Key</el-button>
      </el-space>
    </el-card>
  </div>
</template>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 28px 32px;
  border-radius: 16px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  color: #fff;
  box-shadow: 0 12px 40px rgba(15, 52, 96, 0.25);
}
.hero-content h2 {
  margin: 0 0 8px;
  font-size: 24px;
  font-weight: 700;
}
.hero-content p {
  margin: 0;
  opacity: 0.75;
  font-size: 14px;
}
.stats-row .el-col {
  margin-bottom: 16px;
}
.chart-row .el-col {
  margin-bottom: 16px;
}
.panel-card {
  border-radius: 14px;
  border: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}
.panel-card :deep(.el-card__header) {
  border-bottom: 1px solid #f0f2f5;
  padding: 16px 20px;
}
.panel-card :deep(.el-card__body) {
  padding: 12px 20px 20px;
}
.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}
.chart {
  height: 300px;
}
.gauge-chart {
  height: 260px;
}
.gauge-meta {
  display: flex;
  justify-content: space-around;
  padding-bottom: 8px;
  color: #909399;
  font-size: 13px;
}
.quick-card {
  margin-bottom: 8px;
}
@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
