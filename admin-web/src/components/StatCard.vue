<script setup lang="ts">
defineProps<{
  title: string
  value: number | string
  subtitle?: string
  color?: string
  icon?: string
  variant?: 'default' | 'gradient-blue' | 'gradient-green' | 'gradient-orange' | 'gradient-purple' | 'gradient-red'
}>()
</script>

<template>
  <div class="stat-card" :class="variant || 'default'">
    <div class="card-inner">
      <div class="top-row">
        <div v-if="$slots.icon" class="icon-wrap">
          <slot name="icon" />
        </div>
        <div class="label">{{ title }}</div>
      </div>
      <div class="value" :style="variant === 'default' ? { color: color || '#409eff' } : undefined">
        {{ value }}
      </div>
      <div v-if="subtitle" class="subtitle">{{ subtitle }}</div>
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  border-radius: 14px;
  padding: 20px;
  color: #fff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
}
.default {
  background: #fff;
  color: inherit;
  border: 1px solid #ebeef5;
}
.default .label {
  color: #909399;
}
.default .subtitle {
  color: #909399;
}
.gradient-blue {
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
}
.gradient-green {
  background: linear-gradient(135deg, #67c23a 0%, #529b2e 100%);
}
.gradient-orange {
  background: linear-gradient(135deg, #e6a23c 0%, #cf9236 100%);
}
.gradient-purple {
  background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
}
.gradient-red {
  background: linear-gradient(135deg, #f56c6c 0%, #e45656 100%);
}
.top-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}
.default .icon-wrap {
  background: #ecf5ff;
  color: #409eff;
}
.label {
  font-size: 14px;
  opacity: 0.92;
}
.value {
  font-size: 30px;
  font-weight: 700;
  line-height: 1.2;
}
.subtitle {
  margin-top: 8px;
  font-size: 12px;
  opacity: 0.85;
}
</style>
