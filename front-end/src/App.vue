<script setup>
import FloatingChat from './components/FloatingChat.vue'
import { useChat } from './composables/useChat'

const props = defineProps(['initialTheme', 'themes'])
const { messages, isStreaming, isLoading, suggestions, sendMessage } = useChat()
</script>

<template>
  <FloatingChat 
    :messages="messages" 
    :isStreaming="isStreaming" 
    :isLoading="isLoading"
    :suggestions="suggestions"
    :initialTheme="initialTheme"
    :themes="themes"
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
