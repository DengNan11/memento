<script setup>
import { ref, onMounted } from 'vue'
import { getMemory, clearMemory, manualExtract } from '../api/chat.js'

const entries = ref([])
const meta = ref({})

const categoryColors = {
  identity: '#4fc3f7',
  preference: '#81c784',
  opinion: '#ffb74d',
  project: '#ba68c8',
  behavior: '#4db6ac',
  relationship: '#f06292',
  event: '#90a4ae',
}

const categoryLabels = {
  identity: '身份',
  preference: '偏好',
  opinion: '观点',
  project: '项目',
  behavior: '行为',
  relationship: '关系',
  event: '事件',
}

async function loadMemory() {
  const data = await getMemory()
  entries.value = data.entries || []
  meta.value = data.meta || {}
}

async function handleClear() {
  if (!confirm('确定要清空所有记忆吗？')) return
  await clearMemory()
  entries.value = []
}

async function handleExtract() {
  const data = await manualExtract()
  alert(`提取完成：${data.extracted} 条`)
  await loadMemory()
}

onMounted(loadMemory)
</script>

<template>
  <div class="memory-panel">
    <div class="panel-header">
      <h3>记忆库</h3>
      <span class="count">{{ entries.length }} 条</span>
    </div>

    <div class="panel-actions">
      <button class="btn-sm" @click="loadMemory">刷新</button>
      <button class="btn-sm" @click="handleExtract">手动提取</button>
      <button class="btn-sm danger" @click="handleClear">清空</button>
    </div>

    <div class="entries">
      <div v-if="entries.length === 0" class="empty">暂无记忆</div>
      <div v-for="entry in entries" :key="entry.id" class="entry">
        <div class="entry-header">
          <span
            class="tag"
            :style="{ background: categoryColors[entry.category] || '#666' }"
          >
            {{ categoryLabels[entry.category] || entry.category }}
          </span>
          <span class="confidence">{{ (entry.confidence * 100).toFixed(0) }}%</span>
        </div>
        <div class="entry-content">{{ entry.content }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.memory-panel {
  width: 320px;
  background: #1a1a2e;
  border-left: 1px solid #2a2a4a;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #2a2a4a;
}

.panel-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}

.count {
  font-size: 12px;
  color: #888;
  background: #2a2a4a;
  padding: 2px 8px;
  border-radius: 10px;
}

.panel-actions {
  display: flex;
  gap: 8px;
  padding: 12px 20px;
  border-bottom: 1px solid #2a2a4a;
}

.btn-sm {
  padding: 4px 10px;
  border: 1px solid #3a3a5c;
  background: transparent;
  color: #aaa;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.btn-sm:hover {
  background: #2a2a4a;
  color: #fff;
}

.btn-sm.danger:hover {
  border-color: #e94560;
  color: #e94560;
}

.entries {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.empty {
  text-align: center;
  color: #555;
  padding: 40px 0;
  font-size: 13px;
}

.entry {
  background: #12122a;
  border: 1px solid #2a2a4a;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 8px;
}

.entry-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
}

.confidence {
  font-size: 11px;
  color: #666;
}

.entry-content {
  font-size: 13px;
  line-height: 1.5;
  color: #ccc;
}
</style>
