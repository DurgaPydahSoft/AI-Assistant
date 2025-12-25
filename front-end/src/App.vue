<script setup>
import Sidebar from './components/Sidebar.vue'
import ChatInterface from './components/ChatInterface.vue'
import { useChat } from './composables/useChat'

const { messages, collections, isStreaming, isConnected, sendMessage } = useChat()
</script>

<template>
  <Sidebar :collections="collections" :isConnected="isConnected" />
  <ChatInterface 
    :messages="messages" 
    :isStreaming="isStreaming" 
    @send="sendMessage" 
  />
</template>

<style>
/* Global styles are in style.css */
</style>
