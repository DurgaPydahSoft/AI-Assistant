<script setup>
import { ref, onMounted, onUnmounted, onUpdated, nextTick, computed, watch } from 'vue'
import { Send, Bot, User, Sparkles, X, MessageSquare, Sun, Moon } from 'lucide-vue-next'
import { DotLottieVue } from '@lottiefiles/dotlottie-vue'
import { parse } from 'marked'

const props = defineProps(['messages', 'isStreaming', 'isLoading', 'suggestions', 'initialTheme', 'themes'])
const emit = defineEmits(['send'])

const availableThemes = computed(() => {
  let themesArr = []
  if (typeof props.themes === 'string') {
    try {
      themesArr = JSON.parse(props.themes)
    } catch (e) {
      console.error('Failed to parse themes prop:', e)
      themesArr = []
    }
  } else {
    themesArr = props.themes || []
  }

  if (themesArr.length === 0) {
    themesArr = [
      { id: 'emerald', color: '#10b981' },
      { id: 'cyan', color: '#06b6d4' },
      { id: 'indigo', color: '#6366f1' },
      { id: 'slate', color: '#334155' }
    ]
  }

  // Ensure every theme has an ID (use color if missing) and preserve options
  return themesArr.map(t => ({
    ...t,
    id: t.id || t.color,
    color: t.color
  }))
})
const isOpen = ref(false)
const input = ref('')
const scrollRef = ref(null)
const isDarkMode = ref(false)
const selectedTheme = ref(props.initialTheme || null)
const showMascot = ref(false)
const mascotText = ref('Hi! 👋')
const isMobile = ref(false)
let mascotTimer = null

const mascotMessages = [
  'Hi! 👋',
  'Need help? 🤖',
  'Ask me anything! ✨',
  "I'm here! 💬"
]

// The fallback theme to use if no initial theme is provided and user hasn't selected one yet.
// This is the "default colour" defined in the code.
const SYSTEM_DEFAULT_THEME = { id: 'emerald', color: '#10b981' }

const isAtRightSide = computed(() => {
  return position.value.x > window.innerWidth / 2
})

const DEFAULT_WIDTH = 350
const DEFAULT_HEIGHT = 500
const MIN_WIDTH = 300
const MIN_HEIGHT = 400

const getInitialDims = () => {
  const saved = localStorage.getItem('chatbot_dimensions')
  if (saved) {
    try { return JSON.parse(saved) } catch(e) {}
  }
  return { width: DEFAULT_WIDTH, height: DEFAULT_HEIGHT }
}

const chatDimensions = ref(getInitialDims())
const isResizing = ref(false)
const resizeDir = ref('')
const startResizePos = ref({ x: 0, y: 0 })
const startResizeDims = ref({ width: 0, height: 0 })
const startResizeWinPos = ref({ x: 0, y: 0 })

const isAtTopSide = computed(() => {
  return position.value.y < 100
})

const selectedThemeObject = computed(() => {
  // 1. If user explicitly selected a theme (or passed initial-theme prop), try to match it in their list
  if (selectedTheme.value) {
    const found = availableThemes.value.find(t => t.id === selectedTheme.value)
    if (found) return found
    
    // If not found in list but was initial-theme, maybe it's a direct color value? 
    // Return a temp object for it so it renders
    return { id: selectedTheme.value, color: selectedTheme.value }
  }
  
  // 2. If NO selection made yet, use the SYSTEM_DEFAULT_THEME (Rose) defined here in code.
  // This ensures the site starts with "our default colour" until the user manually changes it.
  return SYSTEM_DEFAULT_THEME
})

const accentColor = computed(() => {
  return selectedThemeObject.value?.color || SYSTEM_DEFAULT_THEME.color
})

const renderMarkdown = (text) => {
  if (!text) return ''
  return parse(text)
}

// Color Utility Functions
const getColorData = (colorInput) => {
  let r = 0, g = 0, b = 0
  let hex = colorInput

  // 1. Robust parsing using browser capability
  // Create a dummy element to let the browser parse color names/formats
  const div = document.createElement('div')
  div.style.color = colorInput
  document.body.appendChild(div)
  const computedColor = window.getComputedStyle(div).color
  document.body.removeChild(div)

  // Parse "rgb(r, g, b)"
  const rgbMatch = computedColor.match(/\d+/g)
  if (rgbMatch && rgbMatch.length >= 3) {
    r = parseInt(rgbMatch[0])
    g = parseInt(rgbMatch[1])
    b = parseInt(rgbMatch[2])
  }
  
  // 2. RGB to HSL
  const rNorm = r / 255; 
  const gNorm = g / 255; 
  const bNorm = b / 255;
  const max = Math.max(rNorm, gNorm, bNorm), min = Math.min(rNorm, gNorm, bNorm);
  let h, s, l = (max + min) / 2;

  if (max === min) { h = s = 0; } 
  else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
    switch (max) {
      case rNorm: h = (gNorm - bNorm) / d + (gNorm < bNorm ? 6 : 0); break;
      case gNorm: h = (bNorm - rNorm) / d + 2; break;
      case bNorm: h = (rNorm - gNorm) / d + 4; break;
    }
    h /= 6;
  }
  
  return { h: h * 360, s: s * 100, l: l * 100, r, g, b }
}

const complementaryInfo = computed(() => {
  // 1. Check for custom config in the theme object
  if (selectedThemeObject.value) {
    if (isDarkMode.value && selectedThemeObject.value.dark) return selectedThemeObject.value.dark
    if (!isDarkMode.value && selectedThemeObject.value.light) return selectedThemeObject.value.light
  }

  // 2. Dynamic Calculation
  const { h, s, l, r, g, b } = getColorData(accentColor.value)
  

  
  // Use Analogous/Monochromatic for Background (cleaner look)
  // instead of complementary which can be jarring.
  const bgH = h 
  
  // Calculate Contrast YIQ for Text on Accent (Black or White)
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000
  const onAccent = yiq >= 128 ? '#000000' : '#ffffff'

  // Calculate Readable Accent (for outlines/icons on background)
  let readableAccent = accentColor.value
  if (!isDarkMode.value && l > 45) {
    readableAccent = `hsl(${h}, ${Math.min(s, 90)}%, 35%)`
  } else if (isDarkMode.value && l < 50) {
    readableAccent = `hsl(${h}, ${Math.min(s, 90)}%, 65%)`
  }

  if (isDarkMode.value) {
    // Dark Mode Params
    return {
      bg: `hsl(${bgH}, 20%, 10%)`,
      text: `hsl(${h}, 80%, 95%)`,
      onAccent,
      readableAccent
    }
  } else {
    // Light Mode Params
    return {
      bg: `hsl(${bgH}, 30%, 97%)`, // Very light tint of main color
      text: `hsl(${h}, 40%, 20%)`,
      onAccent,
      readableAccent
    }
  }
})


const lottieFilter = computed(() => {
  const { h } = getColorData(accentColor.value)
  // The original robot is Blue (approx 220deg).
  // We rotate from 220 to target 'h'.
  const rotation = h - 220
  return {
    filter: `hue-rotate(${rotation}deg)`
  }
})

// Draggable Logic
const ICON_SIZE = 60
const MARGIN = 20

const getInitialPos = () => {
  const saved = localStorage.getItem('chatbot_position')
  if (saved) {
    try { return JSON.parse(saved) } catch(e) {}
  }
  // Default to bottom right
  return { 
    x: window.innerWidth - ICON_SIZE - MARGIN, 
    y: window.innerHeight - ICON_SIZE - MARGIN 
  }
}

const position = ref(getInitialPos())
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })
const hasMoved = ref(false)
const isLoaded = ref(false)

const wrapperStyle = computed(() => {
  const style = {}
  
  if (!isMobile.value) {
    style.left = `${position.value.x}px`
    style.top = `${position.value.y}px`
  }

  if (!isDragging.value && isLoaded.value) {
    style.transition = 'all 0.5s cubic-bezier(0.19, 1, 0.22, 1)'
  }
  return style
})

const startDrag = (e) => {
  if (isResizing.value) return
  hasMoved.value = false
  // Only drag from the toggle button or header
  if (!e.target.closest('.toggle-btn') && !e.target.closest('.header')) return

  // Prevent dragging when interacting with header controls (theme picker, buttons, close btn)
  // BUT allow dragging if it's the main toggle button (when chat is closed)
  if (e.target.closest('.header-actions') || e.target.closest('.theme-picker') || (isOpen.value && e.target.closest('button'))) return
  
  isDragging.value = true
  const event = e.type === 'touchstart' ? e.touches[0] : e
  
  dragOffset.value = {
    x: event.clientX - position.value.x,
    y: event.clientY - position.value.y
  }
  
  window.addEventListener('mousemove', onDrag)
  window.addEventListener('mouseup', stopDrag)
  window.addEventListener('touchmove', onDrag, { passive: false })
  window.addEventListener('touchend', stopDrag)
}

const onDrag = (e) => {
  if (!isDragging.value) return
  hasMoved.value = true
  const event = e.type === 'touchmove' ? e.touches[0] : e
  
  let newX = event.clientX - dragOffset.value.x
  let newY = event.clientY - dragOffset.value.y
  
  // Boundary checks (stay within screen)
  const windowW = window.innerWidth
  const windowH = window.innerHeight
  const elementW = isOpen.value ? chatDimensions.value.width : ICON_SIZE
  const elementH = isOpen.value ? chatDimensions.value.height : ICON_SIZE

  newX = Math.max(0, Math.min(newX, windowW - elementW))
  newY = Math.max(0, Math.min(newY, windowH - elementH))
  
  position.value = { x: newX, y: newY }
  
  if (e.type === 'touchmove') e.preventDefault()
}

const savePosition = () => {
  localStorage.setItem('chatbot_position', JSON.stringify(position.value))
}

const snapToEdges = () => {
  if (isOpen.value) return

  const windowW = window.innerWidth
  if (position.value.x < windowW / 2) {
    position.value.x = MARGIN
  } else {
    position.value.x = windowW - ICON_SIZE - MARGIN
  }
  savePosition()
}

const stopDrag = () => {
  if (!isDragging.value) return
  isDragging.value = false
  
  window.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
  window.removeEventListener('touchmove', onDrag)
  window.removeEventListener('touchend', stopDrag)
  
  snapToEdges()
}

const handleToggle = () => {
  if (hasMoved.value) return
  
  const wasOpen = isOpen.value
  isOpen.value = !isOpen.value
  
  const CHAT_W = chatDimensions.value.width
  const CHAT_H = chatDimensions.value.height
  
  if (wasOpen) {
    position.value.y = position.value.y + CHAT_H - ICON_SIZE
    position.value.x = position.value.x + CHAT_W - ICON_SIZE

    nextTick(() => {
      snapToEdges()
    })
  } else {
    position.value.y = position.value.y - (CHAT_H - ICON_SIZE)
    position.value.x = position.value.x - (CHAT_W - ICON_SIZE)
    
    // Boundary checks to ensure it doesn't go off-screen
    const windowW = window.innerWidth
    const windowH = window.innerHeight
    
    nextTick(() => {
      if (position.value.x < MARGIN) position.value.x = MARGIN
      if (position.value.y < MARGIN) position.value.y = MARGIN
      if (position.value.x + CHAT_W > windowW - MARGIN) position.value.x = windowW - CHAT_W - MARGIN
      if (position.value.y + CHAT_H > windowH - MARGIN) position.value.y = windowH - CHAT_H - MARGIN
      savePosition()
    })
  }
}

// Resizing Logic
const startResize = (e, direction) => {
  e.stopPropagation()
  e.preventDefault()
  
  isResizing.value = true
  resizeDir.value = direction
  
  const event = e.type === 'touchstart' ? e.touches[0] : e
  startResizePos.value = { x: event.clientX, y: event.clientY }
  startResizeDims.value = { ...chatDimensions.value }
  startResizeWinPos.value = { ...position.value }
  
  window.addEventListener('mousemove', onResize)
  window.addEventListener('mouseup', stopResize)
  window.addEventListener('touchmove', onResize, { passive: false })
  window.addEventListener('touchend', stopResize)
}

const onResize = (e) => {
  if (!isResizing.value) return
  const event = e.type === 'touchmove' ? e.touches[0] : e
  
  const dx = event.clientX - startResizePos.value.x
  const dy = event.clientY - startResizePos.value.y
  
  let newWidth = startResizeDims.value.width
  let newHeight = startResizeDims.value.height
  let newX = startResizeWinPos.value.x
  let newY = startResizeWinPos.value.y

  // Handle different corners
  if (resizeDir.value.includes('e')) {
    newWidth = Math.max(MIN_WIDTH, startResizeDims.value.width + dx)
  }
  if (resizeDir.value.includes('w')) {
    const maxWidth = startResizeWinPos.value.x + startResizeDims.value.width - MARGIN
    newWidth = Math.max(MIN_WIDTH, Math.min(maxWidth, startResizeDims.value.width - dx))
    newX = startResizeWinPos.value.x + (startResizeDims.value.width - newWidth)
  }
  if (resizeDir.value.includes('s')) {
    newHeight = Math.max(MIN_HEIGHT, startResizeDims.value.height + dy)
  }
  if (resizeDir.value.includes('n')) {
    const maxHeight = startResizeWinPos.value.y + startResizeDims.value.height - MARGIN
    newHeight = Math.max(MIN_HEIGHT, Math.min(maxHeight, startResizeDims.value.height - dy))
    newY = startResizeWinPos.value.y + (startResizeDims.value.height - newHeight)
  }

  // Screen boundaries
  const windowW = window.innerWidth
  const windowH = window.innerHeight
  
  if (newX + newWidth > windowW - MARGIN) newWidth = windowW - MARGIN - newX
  if (newY + newHeight > windowH - MARGIN) newHeight = windowH - MARGIN - newY
  if (newX < MARGIN) {
    const diff = MARGIN - newX
    newX = MARGIN
    newWidth -= diff
  }
  if (newY < MARGIN) {
    const diff = MARGIN - newY
    newY = MARGIN
    newHeight -= diff
  }

  chatDimensions.value = { width: newWidth, height: newHeight }
  position.value = { x: newX, y: newY }
  
  if (e.type === 'touchmove') e.preventDefault()
}

const stopResize = () => {
  isResizing.value = false
  window.removeEventListener('mousemove', onResize)
  window.removeEventListener('mouseup', stopResize)
  window.removeEventListener('touchmove', onResize)
  window.removeEventListener('touchend', stopResize)
  
  localStorage.setItem('chatbot_dimensions', JSON.stringify(chatDimensions.value))
}


const handleSend = () => {
  if (!input.value.trim()) return
  emit('send', input.value)
  input.value = ''
}

const selectSuggestion = (text) => {
  emit('send', text)
}

const toggleTheme = (e) => {
  e.stopPropagation()
  isDarkMode.value = !isDarkMode.value
}

const handleResize = () => {
  isMobile.value = window.innerWidth <= 480
  if (!isMobile.value) {
    snapToEdges()
  }
}



// Persistence & Initialization
onMounted(() => {
  window.addEventListener('resize', handleResize)
  
  // Snap to edges on load if it was saved in a middle position (e.g. while open)
  nextTick(() => {
    handleResize()
    // Small delay before enabling transitions to prevent the "jump" being animated
    setTimeout(() => {
      isLoaded.value = true
    }, 100)
  })

  // Load saved preferences
  const savedTheme = localStorage.getItem('chatbot_theme')
  const savedMode = localStorage.getItem('chatbot_dark_mode')
  
  if (savedTheme) {
    selectedTheme.value = savedTheme
  }
  
  if (savedMode !== null) {
    isDarkMode.value = savedMode === 'true'
  }

  // Mascot Animation Logic
  const runMascotCycle = () => {
    if (!isOpen.value) {
      // Pick a random message
      const randomIndex = Math.floor(Math.random() * mascotMessages.length)
      mascotText.value = mascotMessages[randomIndex]
      
      showMascot.value = true
      setTimeout(() => {
        showMascot.value = false
      }, 5000) // Show for 5 seconds
    }
  }

  // Run immediately
  runMascotCycle()

  // Repeat every 10 seconds (5s active + 5s quiet)
  mascotTimer = setInterval(runMascotCycle, 10000)
})

watch(selectedTheme, (newVal) => {
  if (newVal) localStorage.setItem('chatbot_theme', newVal)
})

watch(isDarkMode, (newVal) => {
  localStorage.setItem('chatbot_dark_mode', newVal)
})

watch(isOpen, (val) => {
  if (val) showMascot.value = false
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (mascotTimer) clearInterval(mascotTimer)
})

onUpdated(async () => {
  await nextTick()
  if (scrollRef.value) {
    scrollRef.value.scrollTop = scrollRef.value.scrollHeight
  }
})
</script>

<template>
  <div 
    class="floating-wrapper" 
    :class="{ 'dark': isDarkMode, 'light': !isDarkMode, 'dragging': isDragging }"
    :style="wrapperStyle"
    @mousedown="startDrag"
    @touchstart="startDrag"
  >
    <!-- Robot Avatar SVG Definition (Global) -->
    <svg width="0" height="0" style="position:absolute; pointer-events: none;">
      <defs>
        <linearGradient id="robo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color: #ffffff; stop-opacity: 0.9" />
          <stop offset="50%" style="stop-color: #a0aec0; stop-opacity: 0.2" />
          <stop offset="100%" style="stop-color: #1a202c; stop-opacity: 0.6" />
        </linearGradient>
        <filter id="robo-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="rgba(0,0,0,0.3)" />
        </filter>
      </defs>
    </svg>
    <!-- Toggle Button -->
    <button v-if="!isOpen" @click="handleToggle" class="toggle-btn">
      <svg viewBox="0 0 100 100" class="avatar-icon" style="width: 70%; height: 70%;">
        <!-- Head shape with 3D shadow -->
        <rect x="15" y="15" width="70" height="60" rx="16" fill="var(--accent-color)" stroke="rgba(255,255,255,0.4)" stroke-width="3" filter="url(#robo-shadow)" />
        <rect x="15" y="15" width="70" height="60" rx="16" fill="url(#robo-gradient)" style="mix-blend-mode: overlay;" />
        
        <!-- Screen/Face Area -->
        <rect x="25" y="25" width="50" height="36" rx="8" fill="rgba(0,0,0,0.2)" />
        
        <!-- Eyes -->
        <circle cx="38" cy="40" r="5" fill="#00ffcc" />
        <circle cx="62" cy="40" r="5" fill="#00ffcc" />
        
        <!-- Mouth -->
        <rect x="40" y="52" width="20" height="4" rx="2" fill="#00ffcc" opacity="0.6" />
        
        <!-- Antenna -->
        <line x1="50" y1="15" x2="50" y2="5" stroke="var(--accent-color)" stroke-width="4" stroke-linecap="round" />
        <circle cx="50" cy="5" r="5" fill="#ef4444" stroke="white" stroke-width="1" />
      </svg>
      <span class="notification-dot" v-if="isStreaming"></span>

      <!-- Mascot Animation -->
      <div 
        class="mascot-container" 
        :class="{ 
          'show': showMascot, 
          'on-right': isAtRightSide, 
          'on-left': !isAtRightSide,
          'on-top': isAtTopSide,
          'on-bottom': !isAtTopSide
        }"
      >
        <div class="mascot-content">
          <div v-if="!isAtTopSide" class="speech-bubble">
            <span class="shaking-text">{{ mascotText }}</span>
          </div>
          <div class="mascot-toy" style="font-size: 40px; display: flex; align-items: center; justify-content: center;">
            👋
          </div>
          <div v-if="isAtTopSide" class="speech-bubble">
            <span class="shaking-text">{{ mascotText }}</span>
          </div>
        </div>
      </div>
    </button>

    <!-- Chat Window -->
    <div v-else class="chat-window" 
         :class="{ resizing: isResizing }"
         :style="{ width: chatDimensions.width + 'px', height: chatDimensions.height + 'px' }">
      <!-- Resize Handles -->
      <div class="resize-handle resizer-nw" @mousedown="startResize($event, 'nw')" @touchstart="startResize($event, 'nw')"></div>
      <div class="resize-handle resizer-n" @mousedown="startResize($event, 'n')" @touchstart="startResize($event, 'n')"></div>
      <div class="resize-handle resizer-ne" @mousedown="startResize($event, 'ne')" @touchstart="startResize($event, 'ne')"></div>
      <div class="resize-handle resizer-w" @mousedown="startResize($event, 'w')" @touchstart="startResize($event, 'w')"></div>
      <div class="resize-handle resizer-e" @mousedown="startResize($event, 'e')" @touchstart="startResize($event, 'e')"></div>
      <div class="resize-handle resizer-sw" @mousedown="startResize($event, 'sw')" @touchstart="startResize($event, 'sw')"></div>
      <div class="resize-handle resizer-s" @mousedown="startResize($event, 's')" @touchstart="startResize($event, 's')"></div>
      <div class="resize-handle resizer-se" @mousedown="startResize($event, 'se')" @touchstart="startResize($event, 'se')"></div>

      <div class="header" @mousedown="startDrag">
        <div class="agent-info">
          <div class="avatar-sm" style="background: transparent;">
            <!-- 3D Robot Head Icon -->
            <svg viewBox="0 0 100 100" class="avatar-icon">
               <!-- Head shape with 3D shadow -->
              <rect x="15" y="15" width="70" height="60" rx="16" fill="var(--accent-color)" stroke="rgba(255,255,255,0.4)" stroke-width="3" />
              <rect x="15" y="15" width="70" height="60" rx="16" fill="url(#robo-gradient)" style="mix-blend-mode: overlay;" />
              
              <!-- Screen/Face Area -->
              <rect x="25" y="25" width="50" height="36" rx="8" fill="rgba(0,0,0,0.2)" />
              
              <!-- Eyes -->
              <circle cx="38" cy="40" r="5" fill="#00ffcc" />
              <circle cx="62" cy="40" r="5" fill="#00ffcc" />
              
              <!-- Mouth -->
              <rect x="40" y="52" width="20" height="4" rx="2" fill="#00ffcc" opacity="0.6" />
              
              <!-- Antenna -->
              <line x1="50" y1="15" x2="50" y2="5" stroke="var(--accent-color)" stroke-width="4" stroke-linecap="round" />
              <circle cx="50" cy="5" r="5" fill="#ef4444" stroke="white" stroke-width="1" />
            </svg>
          </div>
          <span>Agent</span>
        </div>
        <div class="header-actions">
          <div class="theme-picker">
            <button 
              v-for="theme in availableThemes" 
              :key="theme.id"
              class="theme-dot"
              :style="{ background: theme.color }"
              :class="{ active: selectedTheme === theme.id }"
              @click.stop="selectedTheme = theme.id"
            ></button>
          </div>
          <button @click="toggleTheme" class="theme-toggle">
            <Sun v-if="isDarkMode" :size="16" />
            <Moon v-else :size="16" />
          </button>
          <button @click.stop="handleToggle" class="close-btn">
            <X :size="16" />
          </button>
        </div>
      </div>

      <div class="messages-area" ref="scrollRef">
        <!-- Welcome Agent Mascot -->
        <div v-if="messages.length === 0" class="welcome-container">
          <div class="teddy-bear">
            <DotLottieVue
              style="height: 100%; width: 100%;"
              :style="lottieFilter"
              autoplay
              loop
              src="https://lottie.host/4a08fb37-38ef-47b7-b591-43fb1cd7348f/MYfDBkJFK6.lottie"
            />
          </div>
          <h3>Hi! I'm Agent</h3>
          <p>Your friendly AI assistant. How can I help you today?</p>
        </div>

        <div v-for="(msg, i) in messages" :key="i" 
             class="msg-row" :class="msg.role">
          <div v-if="msg.role === 'assistant'" class="avatar-xs">
            <!-- 3D Robot Head (Small) -->
             <svg viewBox="0 0 100 100" class="avatar-icon">
              <!-- Head shape with 3D shadow -->
              <rect x="20" y="20" width="60" height="50" rx="12" fill="var(--accent-color)" stroke="rgba(255,255,255,0.3)" stroke-width="2" />
              <rect x="20" y="20" width="60" height="50" rx="12" fill="url(#robo-gradient)" style="mix-blend-mode: overlay;" />
              <!-- Eyes -->
              <circle cx="35" cy="40" r="6" fill="#000" />
              <circle cx="35" cy="40" r="2" fill="#00ffcc" />
              <circle cx="65" cy="40" r="6" fill="#000" />
              <circle cx="65" cy="40" r="2" fill="#00ffcc" />
              <!-- Mouth -->
              <rect x="35" y="55" width="30" height="6" rx="3" fill="#333" />
              <!-- Antenna -->
              <line x1="50" y1="20" x2="50" y2="10" stroke="var(--accent-color)" stroke-width="3" />
              <circle cx="50" cy="8" r="4" fill="#ef4444" />
            </svg>
          </div>
          <div class="bubble markdown-content" v-html="renderMarkdown(msg.content)"></div>
        </div>
        
        <div v-if="isLoading" class="msg-row assistant">
          <div class="avatar-xs">
            <Sparkles :size="14" />
          </div>
          <div class="bubble loading">
            <span>•</span><span>•</span><span>•</span>
          </div>
        </div>
      </div>


      <div v-if="suggestions.length > 0 && !isStreaming" class="suggestions-container">
        <button 
          v-for="(sug, idx) in suggestions" 
          :key="idx" 
          class="suggestion-chip"
          @click="selectSuggestion(sug)"
          :style="{ animationDelay: (idx * 0.1) + 's' }"
        >
          <Sparkles :size="12" />
          {{ sug }}
        </button>
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
  z-index: 1000;
  font-family: 'Inter', sans-serif;
  touch-action: pan-y;
  user-select: none;
  --dynamic-accent: v-bind(accentColor);
  --dynamic-bg: v-bind('complementaryInfo.bg');
  --dynamic-text: v-bind('complementaryInfo.text');
  --on-accent: v-bind('complementaryInfo.onAccent');
  --readable-accent: v-bind('complementaryInfo.readableAccent');
}

.floating-wrapper.dragging {
  cursor: grabbing;
}

/* Light Mode */
.floating-wrapper.light {
  --bg-primary: var(--dynamic-bg);
  --bg-secondary: rgba(255, 255, 255, 0.5);
  --bg-tertiary: rgba(0, 0, 0, 0.05);
  --text-primary: var(--dynamic-text);
  --text-secondary: #4b5563;
  --border-color: rgba(0, 0, 0, 0.1);
  --accent-color: var(--dynamic-accent);
  --accent-hover: var(--dynamic-accent);
  --user-bubble: var(--dynamic-accent);
  --assistant-bubble: rgba(0, 0, 0, 0.05);
  --shadow-color: rgba(0, 0, 0, 0.1);
  --shadow-strong: rgba(0, 0, 0, 0.15);
  --notification-dot: #ef4444;
}

/* Dark Mode */
.floating-wrapper.dark {
  --bg-primary: var(--dynamic-bg);
  --bg-secondary: rgba(0, 0, 0, 0.2);
  --bg-tertiary: rgba(255, 255, 255, 0.05);
  --text-primary: var(--dynamic-text);
  --text-secondary: #94a3b8;
  --border-color: rgba(255, 255, 255, 0.1);
  --accent-color: var(--dynamic-accent);
  --accent-hover: var(--dynamic-accent);
  --user-bubble: var(--dynamic-accent);
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
  color: var(--readable-accent);
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

/* Mascot Styles */
.mascot-container { position: absolute; opacity: 0; pointer-events: none; transition: opacity 0.4s ease, transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1); display: flex; flex-direction: column; z-index: -1; will-change: transform, opacity; }
.mascot-container.on-bottom { bottom: 100%; } .mascot-container.on-top { top: 100%; }
.mascot-container.on-right { right: 0; align-items: flex-end; } .mascot-container.on-left { left: 0; align-items: flex-start; }

/* Entry & Show States */
.mascot-container.on-bottom.on-right, .mascot-container.on-bottom.on-left { transform: translateY(15px) scale(0.9); }
.mascot-container.on-top.on-right, .mascot-container.on-top.on-left { transform: translateY(-15px) scale(0.9); }
.mascot-container.show { opacity: 1; }
.mascot-container.on-bottom.show { transform: translateY(-12px) scale(1); }
.mascot-container.on-top.show { transform: translateY(12px) scale(1); }

.mascot-content { display: flex; flex-direction: column; align-items: inherit; gap: 6px; }
.mascot-container.show .mascot-content { animation: mascot-float 3s ease-in-out infinite; }
.mascot-toy { width: 52px; height: 52px; filter: drop-shadow(0 6px 12px var(--shadow-strong)); margin: 0 4px; }
.toy-svg { width: 100%; height: 100%; }

.speech-bubble { background: var(--bg-primary); color: var(--text-primary); padding: 6px 12px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 4px 12px var(--shadow-strong); border: 1px solid var(--border-color); position: relative; white-space: nowrap; animation: bubble-pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
.shaking-text { display: inline-block; animation: text-shake 2s ease-in-out infinite; transform-origin: center; }

/* Dynamic Tail Positioning */
.mascot-container.on-right .speech-bubble { border-bottom-right-radius: 2px; }
.mascot-container.on-left .speech-bubble { border-bottom-left-radius: 2px; }
.speech-bubble::after { content: ''; position: absolute; top: 100%; border-width: 6px; border-style: solid; border-color: var(--bg-primary) transparent transparent transparent; }
.mascot-container.on-right .speech-bubble::after { right: 15px; } .mascot-container.on-left .speech-bubble::after { left: 15px; }
.mascot-container.on-top .speech-bubble { margin-top: 8px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; }
.mascot-container.on-top.on-right .speech-bubble { border-top-right-radius: 2px; } .mascot-container.on-top.on-left .speech-bubble { border-top-left-radius: 2px; }
.mascot-container.on-top .speech-bubble::after { top: auto; bottom: 100%; border-color: transparent transparent var(--bg-primary) transparent; }

/* Welcome Agent Styles */
.welcome-container { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; flex: 1; text-align: center; padding: 2rem; color: var(--text-secondary); animation: fadeIn 0.5s ease-out; }
.teddy-bear { width: 120px; height: 120px; position: relative; margin-bottom: 1rem; }

.welcome-container h3 { color: var(--text-primary); margin: 0.5rem 0; font-size: 1.2rem; }
.welcome-container p { font-size: 0.9rem; opacity: 0.8; max-width: 200px; }

@keyframes mascot-float { 0%, 100% { transform: translate3d(0, 0, 0); } 50% { transform: translate3d(0, -8px, 0); } }
@keyframes text-shake { 0%, 100% { transform: rotate(0deg); } 25% { transform: rotate(2deg); } 50% { transform: rotate(-2deg); } 75% { transform: rotate(1deg); } }
@keyframes bubble-pop { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }

/* Chat Window */
.chat-window { 
  background: var(--bg-primary); 
  backdrop-filter: blur(16px); 
  border: 1px solid var(--border-color); 
  border-radius: 20px; 
  display: flex; 
  flex-direction: column; 
  box-shadow: 0 20px 50px var(--shadow-strong); 
  overflow: hidden; 
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  /* Allow handles to be reached at the very edge */
  padding: 2px;
}

.chat-window.resizing {
  transition: none !important;
  user-select: none;
}

/* Resize Handles - Improved Hitbox and Visuals */
.resize-handle {
  position: absolute;
  z-index: 100;
  background: transparent;
  transition: background 0.2s;
}

/* Corner Handles (L-shaped hitboxes) */
.resizer-nw { top: 0; left: 0; width: 20px; height: 20px; cursor: nw-resize; }
.resizer-ne { top: 0; right: 0; width: 20px; height: 20px; cursor: ne-resize; }
.resizer-sw { bottom: 0; left: 0; width: 20px; height: 20px; cursor: sw-resize; }
.resizer-se { bottom: 0; right: 0; width: 20px; height: 20px; cursor: se-resize; }

/* Edge Handles */
.resizer-n { top: 0; left: 20px; right: 20px; height: 6px; cursor: n-resize; }
.resizer-s { bottom: 0; left: 20px; right: 20px; height: 6px; cursor: s-resize; }
.resizer-e { top: 20px; bottom: 20px; right: 0; width: 6px; cursor: e-resize; }
.resizer-w { top: 20px; bottom: 20px; left: 0; width: 6px; cursor: w-resize; }

/* Visual feedback on hover */
.resize-handle:hover {
  background: rgba(var(--dynamic-accent), 0.1);
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Header */
.header { padding: 1rem; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; color: var(--text-primary); background: var(--bg-secondary); cursor: grab; }
.header:active { cursor: grabbing; }

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
  color: var(--on-accent);
}

.avatar-icon {
  width: 80%;
  height: 80%;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.theme-picker {
  display: flex;
  gap: 0.5rem;
  background: rgba(128, 128, 128, 0.1);
  padding: 6px;
  border-radius: 99px;
  border: 1px solid var(--border-color);
  backdrop-filter: blur(4px);
  max-width: 120px;
  overflow-x: auto;
  scrollbar-width: none; /* Firefox */
  cursor: default; /* Override grab cursor */
}

.theme-picker::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.theme-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  padding: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  flex-shrink: 0;
}

.theme-dot:hover {
  transform: scale(1.1);
}

.theme-dot.active {
  transform: scale(1.2);
  border-color: var(--text-primary);
  box-shadow: 0 0 0 2px var(--bg-primary), 0 4px 6px rgba(0,0,0,0.2);
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
  color: var(--on-accent);
  flex-shrink: 0;
}

.bubble {
  padding: 0.75rem 1rem;
  border-radius: 12px;
  max-width: 85%;
  font-size: 0.9rem;
  line-height: 1.5;
  transition: all 0.2s;
  word-wrap: break-word;
  overflow-wrap: break-word;
  animation: fadeIn 0.3s ease-out;
}

/* Markdown Styling */
.markdown-content :deep(p) {
  margin: 0 0 0.5em 0;
}
.markdown-content :deep(p:last-child) {
  margin-bottom: 0;
}
.markdown-content :deep(ul), .markdown-content :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
  list-style: disc;
}
.markdown-content :deep(li) {
  margin-bottom: 0.25em;
}
.markdown-content :deep(strong) {
  font-weight: 600;
}
.markdown-content :deep(code) {
  background: rgba(127, 127, 127, 0.15); /* Slightly darker for visibility */
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.9em;
}
.markdown-content :deep(pre) {
  background: rgba(0,0,0,0.05);
  padding: 0.8rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 0.5em 0;
}
.markdown-content :deep(pre code) {
  background: transparent;
  padding: 0;
}
.markdown-content :deep(h1), .markdown-content :deep(h2), .markdown-content :deep(h3) {
  margin: 0.5em 0;
  font-size: 1.1em;
  font-weight: 700;
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
  color: var(--on-accent);
  border-bottom-right-radius: 2px;
}

/* Suggestions */
.suggestions-container {
  padding: 0.5rem 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  background: var(--bg-primary);
  border-top: 1px solid var(--border-color);
}

.suggestion-chip {
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 0.4rem 0.8rem;
  border-radius: 99px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  animation: chipEnter 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) both;
}

.suggestion-chip:hover {
  background: var(--accent-color);
  color: var(--on-accent);
  border-color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--shadow-color);
}

.suggestion-chip :deep(svg) {
  opacity: 0.7;
}

@keyframes chipEnter {
  from { opacity: 0; transform: translateY(10px) scale(0.9); }
  to { opacity: 1; transform: translateY(0) scale(1); }
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
  color: var(--on-accent);
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
    bottom: calc(16px + env(safe-area-inset-bottom, 0px)) !important;
    right: 16px !important;
    left: auto !important;
    top: auto !important;
    width: auto;
    height: auto;
  }
  
  .chat-window {
    position: fixed;
    bottom: calc(85px + env(safe-area-inset-bottom, 0px));
    right: 16px;
    width: calc(100vw - 32px);
    height: 65vh;
    max-height: 550px;
    left: 16px;
    margin: 0 auto;
    border-radius: 20px;
  }

  .toggle-btn {
    width: 56px;
    height: 56px;
  }

  .mascot-container {
    display: flex;
    right: 0 !important;
    bottom: 100% !important;
    top: auto !important;
    left: auto !important;
    align-items: flex-end !important;
  }

  .theme-picker {
    max-width: 80px;
  }
}
</style>