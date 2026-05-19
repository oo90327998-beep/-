<template>
  <div class="resume-list">
    <div class="list-header">
      <h3 class="list-title">历史简历</h3>
      <span v-if="totalRecords" class="list-count">共 {{ totalRecords }} 份</span>
    </div>

    <Teleport to="body">
      <div v-if="confirmDeleteId !== null" class="confirm-overlay" @click.self="confirmDeleteId = null">
        <div class="confirm-dialog">
          <h4>确认删除</h4>
          <p>删除后无法恢复，该简历的所有优化建议和 ATS 报告将一并删除。</p>
          <div class="confirm-actions">
            <button class="confirm-btn cancel" @click="confirmDeleteId = null">取消</button>
            <button class="confirm-btn danger" @click="confirmDelete">确认删除</button>
          </div>
        </div>
      </div>
    </Teleport>

    <div v-if="loading" class="list-loading">
      <div v-for="i in 3" :key="i" class="skeleton-card">
        <div class="skeleton-line w-60"></div>
        <div class="skeleton-line w-40"></div>
      </div>
    </div>

    <div v-else-if="!records || records.length === 0" class="list-empty">
      <span class="empty-icon">📄</span>
      <p>还没有上传过简历</p>
      <p class="empty-sub">上传你的第一份 PDF 简历开始 AI 优化</p>
    </div>

    <div v-else class="list-grid">
      <div
        v-for="r in records"
        :key="r.resumeId"
        class="record-card"
        :class="{ active: r.resumeId === activeId }"
        @click="$emit('select', r.resumeId)"
      >
        <div class="card-top">
          <span class="card-icon">📄</span>
          <div class="card-info">
            <span class="card-name">{{ r.filename }}</span>
            <span class="card-date">{{ formatDate(r.createdAt) }}</span>
          </div>
        </div>

        <div class="card-tags">
          <span v-if="r.hasContent" class="tag parsed">已解析</span>
          <span v-if="r.hasSuggestions" class="tag optimized">已优化</span>
        </div>

        <div class="card-actions">
          <button class="card-btn view" @click.stop="$emit('select', r.resumeId)">
            查看优化
          </button>
          <button class="card-btn del" @click.stop="confirmDeleteId = r.resumeId">
            删除
          </button>
        </div>
      </div>
    </div>

    <div v-if="totalRecords > pageSize" class="list-pagination">
      <button
        class="page-btn"
        :disabled="currentOffset === 0"
        @click="currentOffset = Math.max(0, currentOffset - pageSize); loadRecords()"
      >
        ← 上一页
      </button>
      <span class="page-info">{{ currentOffset + 1 }}-{{ Math.min(currentOffset + pageSize, totalRecords) }} / 共 {{ totalRecords }} 份</span>
      <button
        class="page-btn"
        :disabled="currentOffset + pageSize >= totalRecords"
        @click="currentOffset += pageSize; loadRecords()"
      >
        下一页 →
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { getResumes, deleteResume } from '../api/client';
import { toast } from '../composables/useToast';
import type { ResumeListItem } from '../types';

defineProps<{ activeId: number | null }>();
const emit = defineEmits<{
  select: [resumeId: number];
  refresh: [];
}>();

const records = ref<ResumeListItem[]>([]);
const loading = ref(true);
const totalRecords = ref(0);
const currentOffset = ref(0);
const pageSize = 12;
const confirmDeleteId = ref<number | null>(null);

async function loadRecords() {
  loading.value = true;
  try {
    const result = await getResumes(pageSize, currentOffset.value);
    records.value = Array.isArray(result.items) ? result.items : [];
    totalRecords.value = result.total || 0;
  } catch {
    toast.error('加载历史记录失败');
  } finally {
    loading.value = false;
  }
}

onMounted(loadRecords);

async function confirmDelete() {
  const id = confirmDeleteId.value;
  if (!id) return;
  try {
    await deleteResume(id);
    await loadRecords();
    toast.success('已删除');
    emit('refresh');
  } catch {
    toast.error('删除失败');
  } finally {
    confirmDeleteId.value = null;
  }
}

function formatDate(dateStr: string): string {
  try {
    return new Date(dateStr).toLocaleDateString('zh-CN');
  } catch {
    return dateStr;
  }
}
</script>

<style scoped>
.resume-list {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 24px;
}

.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.list-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--white);
}

.list-count {
  font-size: 12px;
  color: var(--slate-500);
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border-radius: 12px;
}

.list-empty {
  text-align: center;
  padding: 40px 20px;
  color: var(--slate-400);
}

.empty-icon {
  font-size: 36px;
  display: block;
  margin-bottom: 12px;
}

.empty-sub {
  font-size: 12px;
  color: var(--slate-500);
  margin-top: 4px;
}

.list-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 500px;
  overflow-y: auto;
}

.record-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 20px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.05);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.record-card:hover {
  border-color: rgba(16, 185, 129, 0.2);
  background: rgba(16, 185, 129, 0.05);
}

.record-card.active {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.08);
}

.card-top {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.card-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.card-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--white);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-date {
  font-size: 11px;
  color: var(--slate-500);
}

.card-tags {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.tag {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.tag.parsed {
  background: rgba(148, 163, 184, 0.1);
  color: var(--slate-400);
}

.tag.optimized {
  background: rgba(16, 185, 129, 0.1);
  color: var(--emerald-400);
}

.card-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.card-btn {
  padding: 8px 14px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.card-btn.view {
  background: rgba(16, 185, 129, 0.1);
  color: var(--emerald-400);
}

.card-btn.view:hover {
  background: rgba(16, 185, 129, 0.2);
}

.card-btn.del {
  background: transparent;
  color: var(--slate-500);
}

.card-btn.del:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.list-loading {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-card {
  padding: 16px 20px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  height: 12px;
  background: rgba(250, 250, 250, 0.05);
  border-radius: 4px;
  animation: pulse 1.5s ease-in-out infinite;
}

.w-60 { width: 60%; }
.w-40 { width: 40%; }

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.confirm-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  animation: fade-in 0.15s ease;
}

.confirm-dialog {
  background: var(--bg-elevated);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 28px;
  max-width: 380px;
  width: 90%;
}

.confirm-dialog h4 {
  font-size: 16px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 8px;
}

.confirm-dialog p {
  font-size: 13px;
  color: var(--slate-400);
  line-height: 1.6;
  margin-bottom: 20px;
}

.confirm-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.confirm-btn {
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.confirm-btn.cancel {
  background: var(--bg-tertiary);
  color: var(--slate-300);
}

.confirm-btn.cancel:hover {
  background: var(--bg-secondary);
}

.confirm-btn.danger {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.confirm-btn.danger:hover {
  background: rgba(239, 68, 68, 0.25);
}

.list-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(250, 250, 250, 0.05);
}

.page-btn {
  padding: 6px 14px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--slate-400);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.page-btn:hover:not(:disabled) {
  border-color: rgba(16, 185, 129, 0.3);
  color: var(--emerald-400);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-info {
  font-size: 12px;
  color: var(--slate-500);
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
