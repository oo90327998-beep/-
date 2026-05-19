import { ref } from 'vue';

export interface Toast {
  id: number;
  type: 'success' | 'error' | 'info';
  message: string;
}

let _id = 0;
const toasts = ref<Toast[]>([]);
const MAX_TOASTS = 5;

function add(type: Toast['type'], message: string) {
  const id = ++_id;
  toasts.value = [...toasts.value.slice(-(MAX_TOASTS - 1)), { id, type, message }];
  setTimeout(() => dismiss(id), 3000);
}

function dismiss(id: number) {
  toasts.value = toasts.value.filter(t => t.id !== id);
}

export const toast = {
  success: (msg: string) => add('success', msg),
  error: (msg: string) => add('error', msg),
  info: (msg: string) => add('info', msg),
};

export function useToast() {
  return { toasts, dismiss };
}
