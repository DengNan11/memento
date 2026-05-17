<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { sendMessage as apiSendMessage } from '../api/chat.js'

const messages = ref([])
const loading = ref(false)
const messagesRef = ref(null)

defineExpose({ sendMessage })

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    content: '你好！我是 Memento，你的个人记忆助手。有什么想聊的？',
  })
})

async function sendMessage(text) {
  if (!text.trim() || loading.value) return

  messages.value.push({ role: 'user', content: text })
  loading.value = true
  scrollToBottom()

  try {
    const data = await apiSendMessage(text)
    messages.value.push({ role: 'assistant', content: data.reply })

    if (data.auto_extract) {
      messages.value.push({
        role: 'system',
        content: `[自动提取到 ${data.auto_extract.extracted} 条记忆]`,
      })
    }
  } catch (e) {
    messages.value.push({
      role: 'system',
      content: `[请求失败: ${e.message}]`,
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

function formatContent(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}
</script>

<template>
  <div class="chat-window" ref="messagesRef">
    <div class="messages">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="message"
        :class="[msg.role]"
      >
        <div class="bubble" v-html="formatContent(msg.content)"></div>
      </div>
      <div v-if="loading" class="message assistant">
        <div class="bubble typing">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.message {
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message.system {
  justify-content: center;
}

.bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.message.user .bubble {
  background: linear-gradient(135deg, #e94560, #c23152);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.assistant .bubble {
  background: #1e1e36;
  color: #e0e0e0;
  border-bottom-left-radius: 4px;
}

.message.system .bubble {
  background: transparent;
  color: #666;
  font-size: 12px;
  padding: 4px 12px;
}

.typing {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 16px 20px;
}

.typing span {
  width: 6px;
  height: 6px;
  background: #666;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing span:nth-child(1) { animation-delay: -0.32s; }
.typing span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>
