import { defineCustomElement } from 'vue'
import styles from './style.css?inline'
import App from './App.vue'

// Inject styles into the shadow DOM of the custom element
App.styles = [styles]

const ChatbotElement = defineCustomElement(App)

customElements.define('ai-chatbot', ChatbotElement)
