<script setup>
import { ref } from 'vue'
import ChatWindow from './components/ChatWindow.vue'
import InputBar from './components/InputBar.vue'
import MemoryPanel from './components/MemoryPanel.vue'

const showMemory = ref(false)
const chatRef = ref(null)

function toggleMemory() {
  showMemory.value = !showMemory.value
}

function onSend(msg) {
  chatRef.value?.sendMessage(msg)
}
</script>

<template>
  <div class="app">
    <header class="header">
      <div class="logo">
        <span class="logo-icon">M</span>
        <span class="logo-text">Memento</span>
      </div>
      <div class="header-actions">
        <button class="btn" @click="toggleMemory">
          {{ showMemory ? '隐藏记忆' : '查看记忆' }}
        </button>
      </div>
    </header>
    <div class="main">
      <div class="chat-area">
        <ChatWindow ref="chatRef" />
        <InputBar @send="onSend" />
      </div>
      <MemoryPanel v-if="showMemory" />
    </div>
  </div>
</template>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #0f0f1a;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: #1a1a2e;
  border-bottom: 1px solid #2a2a4a;
  flex-shrink: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #e94560, #c23152);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  color: white;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.btn {
  padding: 6px 16px;
  border: 1px solid #3a3a5c;
  background: #1a1a2e;
  color: #ccc;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.btn:hover {
  background: #2a2a4a;
  border-color: #e94560;
  color: #fff;
}

.main {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
</style>
