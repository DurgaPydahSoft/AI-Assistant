import { defineCustomElement } from 'vue'
import './style.css'
import App from './App.vue'

// Import styles to inject them into shadow DOM
// Note: In Vite + Vue 3 Custom Elements, styles are handled differently.
// For now, we rely on the fact that standard CSS import in main.js might not auto-inject into Shadow DOM
// unless we use the .ce.vue extension or specific loader config.
// However, a simple workaround for this prototype is to inject global styles or use style injection.

const ChatbotElement = defineCustomElement(App)

customElements.define('ai-chatbot', ChatbotElement)
