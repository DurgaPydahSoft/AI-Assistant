import { ref } from 'vue'

export function useChat() {
  const messages = ref([])
  const isStreaming = ref(false)
  const isLoading = ref(false)
  const suggestions = ref([])
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  // --- UI Context Scraper ---
  const getUIContext = () => {
    // 1. Identify interactive elements (links, buttons, items with click listeners)
    // We targeting standard navigation components
    const selectors = [
      'nav a', 'aside a', 'header a',
      'button', '.btn', '.tab', '[role="tab"]', '[role="button"]',
      'a[href^="#"]', 'a[href^="/"]'
    ]
    
    const elements = document.querySelectorAll(selectors.join(','))
    const context = []
    
    elements.forEach((el, index) => {
      // Skip elements inside the chatbot itself
      if (el.closest('.floating-wrapper') || el.closest('ai-chatbot')) return
      
      // Basic visibility check
      const rect = el.getBoundingClientRect()
      if (rect.width === 0 || rect.height === 0 || getComputedStyle(el).display === 'none') return
      
      // Extract identifying info
      const label = (el.innerText || el.getAttribute('aria-label') || el.title || '').trim().substring(0, 50)
      if (!label) return
      
      // Generate a stable selector
      let selector = el.id ? `#${el.id}` : ''
      if (!selector) {
        // Try to find a unique attribute
        const ariaLabel = el.getAttribute('aria-label')
        const title = el.getAttribute('title')
        const classes = Array.from(el.classList).filter(c => !c.includes('active') && !c.includes('hover'))
        
        if (ariaLabel) {
          selector = `${el.tagName.toLowerCase()}[aria-label="${ariaLabel}"]`
        } else if (title) {
          selector = `${el.tagName.toLowerCase()}[title="${title}"]`
        } else if (classes.length > 0) {
          selector = `${el.tagName.toLowerCase()}.${classes[0]}`
        } else {
          selector = el.tagName.toLowerCase()
        }
        
        // Final uniqueness check: if still not unique, add a text-contains or index-based-path approach
        // For simplicity in Stage 1, we use a slightly more specific path or the current selector.
        if (document.querySelectorAll(selector).length > 1) {
           // We can't easily use :contains in querySelector, so we'll just try to make it more specific
           const parentItem = el.parentElement ? el.parentElement.tagName.toLowerCase() : ''
           selector = `${parentItem} > ${selector}`
        }
      }
      
      context.push({
        label,
        selector,
        type: el.tagName.toLowerCase(),
        role: el.getAttribute('role') || 'element'
      })
    })
    
    // Deduplicate and limit to keep prompt size manageable
    const uniqueContext = Array.from(new Map(context.map(item => [item.label + item.selector, item])).values())
    return JSON.stringify(uniqueContext.slice(0, 20))
  }

  // --- DOM Action Executor ---
  const executeDOMAction = async (action) => {
    console.log('[Agent] Executing DOM Action:', action)

    const el = document.querySelector(action.target)
    if (!el) {
      console.warn(`[Agent] Element not found: ${action.target}`)
      return
    }

    // 0. Visual "Targeting" Highlight
    const originalTransition = el.style.transition
    const originalShadow = el.style.boxShadow
    el.style.transition = 'all 0.3s ease'
    el.style.boxShadow = '0 0 15px 5px rgba(99, 102, 241, 0.6)'
    
    setTimeout(() => {
       el.style.boxShadow = originalShadow
    }, 1000)

    if (action.type === 'click') {
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
    } else if (action.type === 'type') {
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

  const sendMessage = async (userMsg) => {
    if (!userMsg.trim()) return

    messages.value.push({ role: 'user', content: userMsg })
    suggestions.value = [] // Clear previous suggestions
    isStreaming.value = true
    isLoading.value = true

    // History context (simplified for prototype)
    const history = messages.value.slice(-6).map(m => ({
      role: m.role,
      content: m.content
    }))

    // Get Dynamic UI Context
    const uiContext = getUIContext()
    console.log('[Agent] Sending UI Context:', JSON.parse(uiContext))

    let aiMessageStarted = false

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMsg, 
          history,
          ui_context: uiContext 
        })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        if (!aiMessageStarted) {
          isLoading.value = false
          messages.value.push({ role: 'assistant', content: '' })
          aiMessageStarted = true
        }

        const chunk = decoder.decode(value, { stream: true })
        buffer += chunk

        // Step 1: Clean buffer and extract structured tags
        buffer = buffer.replace('[Cached Answer]', '')

        // DOM Actions Parsing
        let domMatch
        while ((domMatch = buffer.match(/\[DOM_ACTION\](.*?)\[\/DOM_ACTION\]/is))) {
          try {
            const action = JSON.parse(domMatch[1])
            executeDOMAction(action)
          } catch (e) { console.error('Parsed error (DOM):', e) }
          buffer = buffer.replace(domMatch[0], '')
        }

        // Suggestions Parsing
        let sugMatch
        while ((sugMatch = buffer.match(/\[SUGGESTIONS\](.*?)\[\/SUGGESTIONS\]/is))) {
          try {
            suggestions.value = JSON.parse(sugMatch[1])
            console.log('[Agent] suggestions updated:', suggestions.value)
          } catch (e) { 
            console.error('Parsed error (Suggestions):', e) 
            // If partial or invalid JSON, we might be hitting an edge case.
          }
          buffer = buffer.replace(sugMatch[0], '')
        }

        // Step 2: Filter out partial tags from display to prevent "leakage"
        let displayContent = buffer
          .replace(/\[DOM_ACTION\].*?$/is, '')
          .replace(/\[SUGGESTIONS\].*?$/is, '')

        // Update UI
        const currentMsgIndex = messages.value.length - 1
        if (currentMsgIndex >= 0) {
          messages.value[currentMsgIndex].content = displayContent.trim()
        }
      }
    } catch (e) {
      console.error('Streaming error:', e)
      isLoading.value = false
      if (!aiMessageStarted) {
        messages.value.push({ role: 'assistant', content: `Error: ${e.message}` })
      } else {
        const currentMsgIndex = messages.value.length - 1
        messages.value[currentMsgIndex].content += `\n[System Error: ${e.message}]`
      }
    } finally {
      isStreaming.value = false
      isLoading.value = false
      console.log('[Agent] Stream complete. Final suggestions:', suggestions.value)
    }
  }

  return {
    messages,
    isStreaming,
    isLoading,
    suggestions,
    sendMessage
  }
}
