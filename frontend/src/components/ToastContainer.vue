<template>
  <Teleport to="body">
    <div class="toast-container" v-if="toasts.length">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast"
        :class="t.type"
        @click="dismiss(t.id)"
      >
        <span class="toast-icon">{{ icons[t.type] }}</span>
        <span class="toast-msg">{{ t.message }}</span>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { useToast } from '../composables/useToast';

const { toasts, dismiss } = useToast();
const icons = { success: '✓', error: '✕', info: 'ℹ' };
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 10000;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  pointer-events: auto;
  animation: slide-in 0.25s ease;
  backdrop-filter: blur(16px);
  min-width: 240px;
  max-width: 400px;
}

.toast.success {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
}

.toast.error {
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
}

.toast.info {
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #cbd5e1;
}

.toast-icon {
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.toast-msg {
  line-height: 1.4;
}

@keyframes slide-in {
  from {
    transform: translateX(120%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
