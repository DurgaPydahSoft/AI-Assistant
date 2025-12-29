<script setup>
import { ref, onUpdated, nextTick } from 'vue'
import { Send, Bot, User, Sparkles, X, MessageSquare } from 'lucide-vue-next'

const props = defineProps(['messages', 'isStreaming'])
const emit = defineEmits(['send'])

const isOpen = ref(true)
const input = ref('')
const scrollRef = ref(null)

const handleSend = () => {
  if (!input.value.trim()) return
  emit('send', input.value)
  input.value = ''
}

const toggleChat = () => isOpen.value = !isOpen.value

onUpdated(async () => {
  await nextTick()
  if (scrollRef.value) {
    scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  }
})
</script>

<template>
  <div class="floating-wrapper">
    <!-- Toggle Button -->
    <button v-if="!isOpen" @click="toggleChat" class="toggle-btn glass">
      <Bot :size="24" />
      <span class="notification-dot" v-if="isStreaming"></span>
    </button>

    <!-- Chat Window -->
    <div v-else class="chat-window glass">
      <div class="header glass-header">
        <div class="agent-info">
          <div class="avatar-sm">
            <Bot :size="16" />
          </div>
          <span>Agent</span>
        </div>
        <button @click="toggleChat" class="close-btn">
          <X :size="16" />
        </button>
      </div>

      <div class="messages-area" ref="scrollRef">
        <div v-for="(msg, i) in messages" :key="i" 
             class="msg-row" :class="msg.role">
          <div v-if="msg.role === 'assistant'" class="avatar-xs">
            <Bot :size="14" />
          </div>
          <div class="bubble glass-bubble">
            {{ msg.content }}
          </div>
        </div>
        
        <div v-if="isStreaming" class="msg-row assistant">
          <div class="avatar-xs">
            <Sparkles :size="14" />
          </div>
          <div class="bubble glass-bubble loading">
            <span>•</span><span>•</span><span>•</span>
          </div>
        </div>
      </div>

      <div class="input-area">
        <input 
          v-model="input" 
          @keyup.enter="handleSend"
          placeholder="Type a command..." 
        />
        <button @click="handleSend" :disabled="!input.trim()">
          <Send :size="16" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.floating-wrapper {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
  font-family: 'Inter', sans-serif;
}

.toggle-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  transition: transform 0.2s;
}

.toggle-btn:hover {
  transform: scale(1.1);
}

.chat-window {
  width: 350px;
  height: 500px;
  background: rgba(15, 23, 42, 0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.header {
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
}

.close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.msg-row {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.bubble {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  max-width: 80%;
  font-size: 0.9rem;
  line-height: 1.5;
}

.msg-row.assistant .bubble {
  background: rgba(255, 255, 255, 0.1);
  border-top-left-radius: 2px;
  color: #e2e8f0;
}

.msg-row.user .bubble {
  background: #6366f1;
  color: white;
  border-bottom-right-radius: 2px;
}

.input-area {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 0.5rem;
}

input {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  color: white;
  outline: none;
}

input:focus {
  border-color: #6366f1;
}

.input-area button {
  background: #6366f1;
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.input-area button:disabled {
  opacity: 0.5;
}

.loading span {
  animation: bounce 1s infinite;
}

.loading span:nth-child(2) { animation-delay: 0.2s; }
.loading span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-3px); }
}
</style>
