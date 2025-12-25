<script setup>
import { Database, Server, RefreshCw } from 'lucide-vue-next'

const props = defineProps(['collections', 'isConnected'])
</script>

<template>
  <aside class="sidebar glass">
    <div class="sidebar-header">
      <div class="logo-area">
        <div class="logo-icon glass">
          <Database class="icon accent" :size="20" />
        </div>
        <div>
          <h2 class="gradient-text">MongoAI</h2>
          <span class="status" :class="{ connected: isConnected }">
            {{ isConnected ? 'Online' : 'Offline' }}
          </span>
        </div>
      </div>
    </div>

    <div class="sidebar-section">
      <div class="section-label">
        <Server :size="14" />
        <span>COLLECTIONS</span>
      </div>
      <div class="collection-list">
        <div v-for="col in collections" :key="col" class="collection-item glass-card">
          <span class="dot"></span>
          {{ col }}
        </div>
        <div v-if="collections.length === 0" class="empty-state">
          No collections found
        </div>
      </div>
    </div>

    <div class="sidebar-footer glass">
      <button class="glass-btn">
        <RefreshCw :size="16" />
        Sync DB
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--glass-border);
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid var(--glass-border);
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.status.connected::before {
  content: '';
  width: 6px;
  height: 6px;
  background: var(--success);
  border-radius: 50%;
  box-shadow: 0 0 8px var(--success);
}

.sidebar-section {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 16px;
  letter-spacing: 1px;
}

.collection-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.collection-item {
  padding: 10px 14px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.dot {
  width: 6px;
  height: 6px;
  background: var(--accent-primary);
  border-radius: 50%;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid var(--glass-border);
}

.glass-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  padding: 10px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  cursor: pointer;
}

.empty-state {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: center;
  padding: 20px;
}
</style>
