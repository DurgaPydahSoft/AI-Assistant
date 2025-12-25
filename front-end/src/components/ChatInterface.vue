<script setup>
import { ref, onUpdated, nextTick } from 'vue'
import { Send, Bot, User, Sparkles } from 'lucide-vue-next'

const props = defineProps(['messages', 'isStreaming'])
const emit = defineEmits(['send'])

const input = ref('')
const scrollRef = ref(null)

const handleSend = () => {
  if (!input.value.trim()) return
  emit('send', input.value)
  input.value = ''
}

// Auto scroll to bottom
onUpdated(async () => {
  await nextTick()
  if (scrollRef.value) {
    scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  }
})
</script>

<template>
  <main class="chat-container">
    <div class="chat-messages" ref="scrollRef">
      <div v-for="(msg, i) in messages" :key="i" 
           class="msg-wrapper" :class="msg.role">
        <div class="avatar glass">
          <Bot v-if="msg.role === 'assistant'" :size="18" />
          <User v-else :size="18" />
        </div>
        <div class="msg-content glass-card">
          <div class="role-tag">{{ msg.role.toUpperCase() }}</div>
          <p class="text">{{ msg.content }}</p>
        </div>
      </div>
      
      <div v-if="isStreaming" class="msg-wrapper assistant">
        <div class="avatar glass streaming">
          <Sparkles :size="18" />
        </div>
        <div class="msg-content glass-card loading">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>

    <div class="input-area glass">
      <div class="input-wrapper glass-card">
        <input 
          v-model="input" 
          @keyup.enter="handleSend"
          placeholder="Ask something about your database..." 
          type="text"
        />
        <button @click="handleSend" class="send-btn" :disabled="!input.trim()">
          <Send :size="18" />
        </button>
      </div>
    </div>
  </main>
</template>

<style scoped>
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.chat-messages {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.msg-wrapper {
  display: flex;
  gap: 16px;
  max-width: 80%;
}

.msg-wrapper.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.avatar.streaming {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); }
  70% { box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); }
  100% { box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); }
}

.msg-content {
  padding: 16px 20px;
  position: relative;
}

.role-tag {
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 1px;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.text {
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.input-area {
  padding: 24px 40px 40px;
  border-top: 1px solid var(--glass-border);
}

.input-wrapper {
  display: flex;
  align-items: center;
  padding: 8px 12px 8px 24px;
  gap: 12px;
}

input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 15px;
  padding: 12px 0;
}

.send-btn {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: var(--accent-primary);
  border: none;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading Dots */
.loading {
  display: flex;
  gap: 4px;
  padding: 12px 20px;
}

.loading .dot {
  width: 4px;
  height: 4px;
  background: var(--text-secondary);
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.loading .dot:nth-child(1) { animation-delay: -0.32s; }
.loading .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}
</style>
