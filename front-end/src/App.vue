<script setup>
import FloatingChat from './components/FloatingChat.vue'
import { useChat } from './composables/useChat'

const { messages, isStreaming, sendMessage } = useChat()
</script>

<template>
  <FloatingChat 
    :messages="messages" 
    :isStreaming="isStreaming" 
    @send="sendMessage" 
  />
</template>

<style>
/* Global styles */
body {
  margin: 0;
  overflow-y: auto;
}
</style>
