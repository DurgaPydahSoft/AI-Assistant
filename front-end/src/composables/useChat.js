import { ref } from 'vue'

export function useChat() {
  const messages = ref([])
  const isStreaming = ref(false)
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  // --- DOM Action Executor ---
  const executeDOMAction = async (action) => {
    console.log('[Agent] Executing DOM Action:', action)

    if (action.type === 'click') {
      const el = document.querySelector(action.target)
      if (el) {
        // 1. Visual Cursor Effect
        const cursor = document.createElement('div')
        cursor.className = 'agent-cursor'
        cursor.innerHTML = '👆' // Cursor icon
        Object.assign(cursor.style, {
          position: 'fixed',
          left: '50%',
          top: '50%',
          transform: 'translate(-50%, -50%)',
          fontSize: '2rem',
          zIndex: '9999',
          transition: 'all 0.8s cubic-bezier(0.22, 1, 0.36, 1)',
          pointerEvents: 'none'
        })
        document.body.appendChild(cursor)

        // Get coordinates
        const rect = el.getBoundingClientRect()
        const targetX = rect.left + rect.width / 2
        const targetY = rect.top + rect.height / 2

        // Move cursor
        setTimeout(() => {
          cursor.style.left = `${targetX}px`
          cursor.style.top = `${targetY}px`
        }, 50)

        // Click and Remove
        setTimeout(() => {
          cursor.style.transform = 'translate(-50%, -50%) scale(0.8)' // Press effect
          el.click()
        }, 850)

        setTimeout(() => {
          cursor.remove()
        }, 1500)
      } else {
        console.warn(`[Agent] Element not found: ${action.target}`)
      }
    } else if (action.type === 'type') {
      const el = document.querySelector(action.target)
      if (el) {
        // 1. Highlight Element
        const originalBorder = el.style.borderColor
        el.style.borderColor = '#6366f1' // Active color
        el.focus()

        // 2. Type Simulation
        const value = action.value || ''
        let i = 0

        const typeChar = () => {
          if (i < value.length) {
            // Programmatically set value for Vue/React reactivity
            el.value = value.substring(0, i + 1)
            el.dispatchEvent(new Event('input', { bubbles: true })) // Critical for v-model
            i++
            setTimeout(typeChar, 50 + Math.random() * 50) // Random typing speed
          } else {
            // Restore style
            setTimeout(() => {
              el.style.borderColor = originalBorder
            }, 500)
          }
        }

        typeChar()
      }
    }
  }

  const sendMessage = async (userMsg) => {
    if (!userMsg.trim()) return

    messages.value.push({ role: 'user', content: userMsg })

    // History context (simplified for prototype)
    const history = messages.value.slice(-6).map(m => ({
      role: m.role,
      content: m.content
    }))

    const aiMessageIndex = messages.value.length
    // Don't push empty message yet to avoid double loading indicators
    // messages.value.push({ role: 'assistant', content: '' }) 
    isStreaming.value = true
    let aiMessageStarted = false

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, history })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        // On first chunk of data, initialize the message in UI
        if (!aiMessageStarted) {
          isStreaming.value = false // Hide loading dots
          messages.value.push({ role: 'assistant', content: '' })
          aiMessageStarted = true
        }

        const chunk = decoder.decode(value, { stream: true })
        buffer += chunk

        // Remove [Cached Answer] tag if present
        buffer = buffer.replace('[Cached Answer]', '')

        // Check for DOM hooks like [DOM_ACTION]{...}[/DOM_ACTION]
        let match
        while ((match = buffer.match(/\[DOM_ACTION\](.*?)\[\/DOM_ACTION\]/s))) {
          const jsonStr = match[1]
          try {
            const action = JSON.parse(jsonStr)
            executeDOMAction(action)
            buffer = buffer.replace(match[0], '')
          } catch (e) {
            console.error('Failed to parse DOM action', e)
            buffer = buffer.replace(match[0], '')
          }
        }

        // Update UI with the clean buffer
        const currentMsgIndex = messages.value.length - 1
        if (currentMsgIndex >= 0) {
          messages.value[currentMsgIndex].content = buffer
        }
      }
    } catch (e) {
      if (!aiMessageStarted) {
        messages.value.push({ role: 'assistant', content: `Error: ${e.message}` })
      } else {
        const currentMsgIndex = messages.value.length - 1
        messages.value[currentMsgIndex].content += `\n[Error: ${e.message}]`
      }
    } finally {
      isStreaming.value = false
    }
  }

  return {
    messages,
    isStreaming,
    sendMessage
  }
}
