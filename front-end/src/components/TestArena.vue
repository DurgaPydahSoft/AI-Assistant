<script setup>
import { ref } from 'vue'

const buttonStates = ref({
  btn1: 'neutral',
  btn2: 'neutral',
  btn3: 'neutral'
})

const handleAction = (id) => {
  buttonStates.value[id] = 'active'
  setTimeout(() => {
    buttonStates.value[id] = 'neutral'
  }, 2000)
}

const formData = ref({
  name: '',
  email: '',
  bio: ''
})

const isSubmitting = ref(false)

const submitForm = async () => {
  if (!formData.value.name) return
  
  isSubmitting.value = true
  try {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    await fetch(`${API_URL}/users`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData.value)
    })
    
    // Reset form
    formData.value = { name: '', email: '', bio: '' }
    alert('User Registered Successfully!')
  } catch (e) {
    console.error(e)
    alert('Failed to register user')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="arena-container">
    <h1 class="title">Autonomous Agent Test Arena</h1>
    <p class="subtitle">Ask the agent to click these buttons.</p>
    
    <div class="button-grid">
      <button 
        id="btn-1"
        class="arena-btn" 
        :class="buttonStates.btn1"
        @click="handleAction('btn1')"
      >
        <div class="btn-content">
          <span class="icon">🚀</span>
          <span>Launch Sequence</span>
        </div>
        <div class="status-indicator"></div>
      </button>

      <button 
        id="btn-2"
        class="arena-btn" 
        :class="buttonStates.btn2"
        @click="handleAction('btn2')"
      >
        <div class="btn-content">
          <span class="icon">🛡️</span>
          <span>Toggle Shields</span>
        </div>
        <div class="status-indicator"></div>
      </button>

      <button 
        id="btn-3"
        class="arena-btn critical" 
        :class="buttonStates.btn3"
        @click="handleAction('btn3')"
      >
        <div class="btn-content">
          <span class="icon">⚠️</span>
          <span>Emergency Vent</span>
        </div>
        <div class="status-indicator"></div>
      </button>
    </div>

    <!-- User Form Section -->
    <div class="form-section">
      <h2 class="section-title">User Registration</h2>
      <div class="form-card glass-panel">
        <div class="form-group">
          <label>Full Name</label>
          <input id="input-name" v-model="formData.name" type="text" placeholder="e.g. John Doe" />
        </div>
        
        <div class="form-group">
          <label>Email Address</label>
          <input id="input-email" v-model="formData.email" type="email" placeholder="e.g. john@example.com" />
        </div>

        <div class="form-group">
          <label>Bio / Note</label>
          <textarea id="input-bio" v-model="formData.bio" placeholder="Tell us about yourself..."></textarea>
        </div>

        <button id="btn-submit" @click="submitForm" class="submit-btn" :disabled="isSubmitting">
          {{ isSubmitting ? 'Saving...' : 'Register User' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ... existing styles ... */
.form-section {
  margin-top: 4rem;
  width: 100%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  font-size: 1.5rem;
  color: #e2e8f0;
  text-align: center;
}

.glass-panel {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  text-align: left;
}

label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

input, textarea {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid #334155;
  border-radius: 8px;
  padding: 0.75rem;
  color: white;
  font-family: inherit;
  transition: border-color 0.2s;
}

input:focus, textarea:focus {
  outline: none;
  border-color: #6366f1;
}

textarea {
  min-height: 100px;
  resize: vertical;
}

.submit-btn {
  background: #6366f1;
  color: white;
  border: none;
  padding: 1rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 0.5rem;
}

.submit-btn:hover {
  background: #4f46e5;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: wait;
}

.arena-container {
  min-height: 100vh;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 4rem 1rem;
  color: white;
  font-family: 'Inter', sans-serif;
}

.title {
  font-size: 3rem;
  font-weight: 800;
  background: linear-gradient(to right, #6366f1, #a855f7);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin-bottom: 1rem;
}

.subtitle {
  color: #94a3b8;
  margin-bottom: 4rem;
  font-size: 1.2rem;
}

.button-grid {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  justify-content: center;
}

.arena-btn {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 16px;
  padding: 2rem;
  width: 200px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.arena-btn:hover {
  transform: translateY(-4px);
  border-color: #6366f1;
  box-shadow: 0 10px 30px -10px rgba(99, 102, 241, 0.3);
}

.arena-btn:active {
  transform: scale(0.95);
}

.btn-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  z-index: 10;
  position: relative;
}

.icon {
  font-size: 2.5rem;
}

.arena-btn span:last-child {
  font-weight: 600;
  color: #e2e8f0;
}

/* Active States */
.arena-btn.active {
  background: #10b981;
  border-color: #059669;
}

.arena-btn.critical.active {
  background: #ef4444;
  border-color: #b91c1c;
}

.status-indicator {
  position: absolute;
  top: 1rem;
  right: 1rem;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #334155;
  transition: background 0.3s;
}

.arena-btn:hover .status-indicator {
  background: #6366f1;
}

.arena-btn.active .status-indicator {
  background: white;
  box-shadow: 0 0 10px white;
}
</style>
