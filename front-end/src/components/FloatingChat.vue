<script setup>
import { ref, onUpdated, nextTick } from 'vue'
import { Send, Bot, User, Sparkles, X, MessageSquare, Sun, Moon } from 'lucide-vue-next'

const props = defineProps(['messages', 'isStreaming'])
const emit = defineEmits(['send'])

const isOpen = ref(true)
const input = ref('')
const scrollRef = ref(null)
const isDarkMode = ref(true)

const handleSend = () => {
  if (!input.value.trim()) return
  emit('send', input.value)
  input.value = ''
}

const toggleChat = () => isOpen.value = !isOpen.value
const toggleTheme = () => isDarkMode.value = !isDarkMode.value

onUpdated(async () => {
  await nextTick()
  if (scrollRef.value) {
    scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  }
})
</script>

<template>
  <div class="floating-wrapper" :class="{ 'dark': isDarkMode, 'light': !isDarkMode }">
    <!-- Toggle Button -->
    <button v-if="!isOpen" @click="toggleChat" class="toggle-btn">
      <Bot :size="24" />
      <span class="notification-dot" v-if="isStreaming"></span>
    </button>

    <!-- Chat Window -->
    <div v-else class="chat-window">
      <div class="header">
        <div class="agent-info">
          <div class="avatar-sm">
            <Bot :size="16" />
          </div>
          <span>Agent</span>
        </div>
        <div class="header-actions">
          <button @click="toggleTheme" class="theme-toggle">
            <Sun v-if="isDarkMode" :size="16" />
            <Moon v-else :size="16" />
          </button>
          <button @click="toggleChat" class="close-btn">
            <X :size="16" />
          </button>
        </div>
      </div>

      <div class="messages-area" ref="scrollRef">
        <div v-for="(msg, i) in messages" :key="i" 
             class="msg-row" :class="msg.role">
          <div v-if="msg.role === 'assistant'" class="avatar-xs">
            <Bot :size="14" />
          </div>
          <div class="bubble">
            {{ msg.content }}
          </div>
        </div>
        
        <div v-if="isStreaming" class="msg-row assistant">
          <div class="avatar-xs">
            <Sparkles :size="14" />
          </div>
          <div class="bubble loading">
            <span>•</span><span>•</span><span>•</span>
          </div>
        </div>
      </div>

      <div class="input-area">
        <input 
          v-model="input" 
          @keyup.enter="handleSend"
          :placeholder="isDarkMode ? 'Type a command...' : 'Ask me anything...'" 
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

/* Light Mode */
.floating-wrapper.light {
  --bg-primary: rgba(255, 255, 255, 0.95);
  --bg-secondary: rgba(249, 250, 251, 0.9);
  --bg-tertiary: rgba(243, 244, 246, 0.8);
  --text-primary: #111827;
  --text-secondary: #4b5563;
  --border-color: rgba(209, 213, 219, 0.5);
  --accent-color: #4f46e5;
  --accent-hover: #4338ca;
  --user-bubble: #4f46e5;
  --assistant-bubble: #f3f4f6;
  --shadow-color: rgba(0, 0, 0, 0.1);
  --shadow-strong: rgba(0, 0, 0, 0.15);
  --notification-dot: #ef4444;
}

/* Dark Mode */
.floating-wrapper.dark {
  --bg-primary: rgba(15, 23, 42, 0.95);
  --bg-secondary: rgba(30, 41, 59, 0.9);
  --bg-tertiary: rgba(51, 65, 85, 0.8);
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --border-color: rgba(255, 255, 255, 0.1);
  --accent-color: #6366f1;
  --accent-hover: #818cf8;
  --user-bubble: #6366f1;
  --assistant-bubble: rgba(255, 255, 255, 0.1);
  --shadow-color: rgba(0, 0, 0, 0.3);
  --shadow-strong: rgba(0, 0, 0, 0.5);
  --notification-dot: #f87171;
}

/* Toggle Button */
.toggle-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--bg-primary);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-color);
  color: var(--accent-color);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 30px var(--shadow-strong);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.toggle-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 15px 40px var(--shadow-strong);
}

.toggle-btn .notification-dot {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--notification-dot);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Chat Window */
.chat-window {
  width: 350px;
  height: 500px;
  background: var(--bg-primary);
  backdrop-filter: blur(16px);
  border: 1px solid var(--border-color);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 50px var(--shadow-strong);
  overflow: hidden;
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Header */
.header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.9rem;
}

.avatar-sm {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-hover));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.theme-toggle {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-toggle:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

/* Messages Area */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: var(--bg-primary);
}

.messages-area::-webkit-scrollbar {
  width: 6px;
}

.messages-area::-webkit-scrollbar-track {
  background: transparent;
}

.messages-area::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.messages-area::-webkit-scrollbar-thumb:hover {
  background: var(--accent-color);
}

.msg-row {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.avatar-xs {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  background: linear-gradient(135deg, var(--accent-color), var(--accent-hover));
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.bubble {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  max-width: 80%;
  font-size: 0.9rem;
  line-height: 1.5;
  transition: all 0.2s;
  word-wrap: break-word;
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg-row.assistant .bubble {
  background: var(--assistant-bubble);
  border-top-left-radius: 2px;
  color: var(--text-primary);
}

.msg-row.user .bubble {
  background: var(--user-bubble);
  color: white;
  border-bottom-right-radius: 2px;
}

/* Input Area */
.input-area {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 0.5rem;
  background: var(--bg-secondary);
}

input {
  flex: 1;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  outline: none;
  font-size: 0.9rem;
  transition: all 0.2s;
}

input::placeholder {
  color: var(--text-secondary);
}

input:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-area button {
  background: var(--accent-color);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.input-area button:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
}

.input-area button:active:not(:disabled) {
  transform: translateY(0);
}

.input-area button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading Animation */
.loading span {
  animation: bounce 1s infinite;
  display: inline-block;
}

.loading span:nth-child(2) { animation-delay: 0.2s; }
.loading span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

/* Responsive adjustments */
@media (max-width: 480px) {
  .floating-wrapper {
    bottom: 1rem;
    right: 1rem;
  }
  
  .chat-window {
    width: calc(100vw - 2rem);
    height: 400px;
    max-width: 350px;
  }
}
</style>