import { ref } from 'vue'

export function useChat() {
  const messages = ref([])
  const isStreaming = ref(false)
  const isLoading = ref(false)
  const suggestions = ref([])
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  // --- UI Context Scraper ---
  const getUIContext = () => {
    // 1. Target semantic elements and standard testing/accessibility attributes
    const selectors = [
      'nav a', 'aside a', 'header a', 'nav button',
      'button', '.btn', '.tab', '[role="tab"]', '[role="button"]',
      'a[href^="#"]', 'a[href^="/"]',
      '[data-testid]', '[data-qa]', '[data-cy]'
    ]
    
    const elements = document.querySelectorAll(selectors.join(','))
    const context = []
    
    elements.forEach((el) => {
      if (el.closest('.floating-wrapper') || el.closest('ai-chatbot')) return
      
      const rect = el.getBoundingClientRect()
      if (rect.width === 0 || rect.height === 0 || getComputedStyle(el).display === 'none') return
      
      const label = (
        el.innerText || 
        el.getAttribute('aria-label') || 
        el.getAttribute('data-testid') ||
        el.title || 
        ''
      ).trim().substring(0, 50)
      
      if (!label) return
      
      // Generate Robust Selectors (Priority: data-testid > aria-label > role > id > specific-class)
      let selector = ''
      const testId = el.getAttribute('data-testid') || el.getAttribute('data-qa') || el.getAttribute('data-cy')
      const ariaLabel = el.getAttribute('aria-label')
      const role = el.getAttribute('role')
      
      if (testId) {
        selector = `${el.tagName.toLowerCase()}[data-testid="${testId}"]`
        // Handle variations
        if (!el.getAttribute('data-testid')) {
          const attr = el.hasAttribute('data-qa') ? 'data-qa' : 'data-cy'
          selector = `${el.tagName.toLowerCase()}[${attr}="${testId}"]`
        }
      } else if (ariaLabel) {
        selector = `${el.tagName.toLowerCase()}[aria-label="${ariaLabel}"]`
      } else if (role && label) {
        selector = `${el.tagName.toLowerCase()}[role="${role}"]`
      } else if (el.id) {
        selector = `#${el.id}`
      } else {
        const classes = Array.from(el.classList).filter(c => !c.includes('active') && !c.includes('hover') && !c.includes('focus'))
        if (classes.length > 0) {
          selector = `${el.tagName.toLowerCase()}.${classes[0]}`
        } else {
          selector = el.tagName.toLowerCase()
        }
      }

      // Universal Child-Index Fallback for Uniqueness
      if (document.querySelectorAll(selector).length > 1) {
        // Find the index of this element among all elements matching the non-unique selector
        const matches = Array.from(document.querySelectorAll(selector))
        const index = matches.indexOf(el)
        if (index !== -1) {
          // Use :nth-of-type or just a specific index if the selector is tag-based
          // For absolute precision, we can use the index among matches
          // but CSS doesn't have a :match-index(n). So we'll use a more complex path.
          let path = []
          let temp = el
          while (temp && temp.nodeType === Node.ELEMENT_NODE && temp.tagName !== 'BODY') {
            let sibIndex = 1
            let prev = temp.previousElementSibling
            while (prev) {
              if (prev.tagName === temp.tagName) sibIndex++
              prev = prev.previousElementSibling
            }
            path.unshift(`${temp.tagName.toLowerCase()}:nth-of-type(${sibIndex})`)
            temp = temp.parentElement
          }
          selector = path.join(' > ')
        }
      }
      
      context.push({
        label,
        selector,
        type: el.tagName.toLowerCase(),
        role: role || 'element'
      })
    })
    
    const uniqueContext = Array.from(new Map(context.map(item => [item.label + item.selector, item])).values())
    return JSON.stringify(uniqueContext.slice(0, 25))
  }

  const actionQueue = []
  let isProcessingAction = false

  const processNextAction = async () => {
    if (isProcessingAction || actionQueue.length === 0) return
    isProcessingAction = true
    const action = actionQueue.shift()
    
    try {
      await performDOMAction(action)
    } finally {
      isProcessingAction = false
      setTimeout(processNextAction, 500) // Small gap between actions
    }
  }

  const performDOMAction = (action) => {
    return new Promise((resolve) => {
      console.log('[Agent] Performing DOM Action:', action)
      const el = document.querySelector(action.target)
      if (!el) {
        console.warn(`[Agent] Element not found: ${action.target}`)
        resolve()
        return
      }

      // 0. Visual "Targeting" Highlight
      const originalShadow = el.style.boxShadow
      el.style.transition = 'all 0.3s ease'
      el.style.boxShadow = '0 0 15px 5px rgba(99, 102, 241, 0.6)'
      
      if (action.type === 'click') {
        const cursor = document.createElement('div')
        cursor.className = 'agent-cursor'
        cursor.innerHTML = '👆'
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

        const rect = el.getBoundingClientRect()
        const targetX = rect.left + rect.width / 2
        const targetY = rect.top + rect.height / 2

        setTimeout(() => {
          cursor.style.left = `${targetX}px`
          cursor.style.top = `${targetY}px`
        }, 50)

        setTimeout(() => {
          cursor.style.transform = 'translate(-50%, -50%) scale(0.8)'
          el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
          el.click()
          el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true }))
          el.dispatchEvent(new MouseEvent('click', { bubbles: true }))
          
          setTimeout(() => {
            el.style.boxShadow = originalShadow
            cursor.remove()
            resolve()
          }, 600)
        }, 850)
      } else if (action.type === 'type') {
        el.focus()
        const value = action.value || ''
        let i = 0
        const typeChar = () => {
          if (i < value.length) {
            el.value = value.substring(0, i + 1)
            el.dispatchEvent(new Event('input', { bubbles: true }))
            el.dispatchEvent(new Event('change', { bubbles: true }))
            i++
            setTimeout(typeChar, 50 + Math.random() * 50)
          } else {
            el.blur()
            el.style.boxShadow = originalShadow
            resolve()
          }
        }
        typeChar()
      } else {
        resolve()
      }
    })
  }

  const executeDOMAction = (action) => {
    actionQueue.push(action)
    processNextAction()
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
