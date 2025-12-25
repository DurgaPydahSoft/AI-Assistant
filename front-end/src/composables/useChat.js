import { ref, onMounted } from 'vue'

export function useChat() {
  const messages = ref([
    { role: 'assistant', content: 'Hello! I am your MongoDB AI Assistant. How can I help you today?' }
  ])
  const collections = ref([])
  const isStreaming = ref(false)
  const isConnected = ref(false)
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const fetchCollections = async () => {
    try {
      const res = await fetch(`${API_URL}/collections`)
      const data = await res.json()
      collections.value = data.collections
      isConnected.value = true
    } catch (e) {
      console.error('Failed to fetch collections:', e)
      isConnected.value = false
    }
  }

  const sendMessage = async (userMsg) => {
    if (!userMsg.trim()) return
    
    // Add user message to UI
    messages.value.push({ role: 'user', content: userMsg })
    
    // Create history for API
    const history = messages.value.slice(0, -1).map(m => ({
      role: m.role,
      content: m.content
    }))

    // Add placeholder for AI response
    const aiMessageIndex = messages.value.length
    messages.value.push({ role: 'assistant', content: '' })
    isStreaming.value = true

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, history })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value, { stream: true })
        messages.value[aiMessageIndex].content += chunk
      }
    } catch (e) {
      messages.value[aiMessageIndex].content = `Error: ${e.message}`
    } finally {
      isStreaming.value = false
    }
  }

  onMounted(fetchCollections)

  return {
    messages,
    collections,
    isStreaming,
    isConnected,
    sendMessage
  }
}
