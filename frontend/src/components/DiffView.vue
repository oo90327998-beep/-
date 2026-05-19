<template>
  <div class="diff-view">
    <div class="diff-header">
      <div class="header-left">
        <button class="back-btn" @click="$emit('back')" title="返回列表">
          <span>←</span>
          <span>返回</span>
        </button>
        <div>
          <h2 class="diff-title">AI 优化结果</h2>
          <p class="diff-subtitle">逐模块查看 AI 建议，一键应用改写或导出优化版简历</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="template-btn" @click="$emit('open-templates')">
          <span>▣</span>
          <span>模板库</span>
        </button>
        <div class="style-switcher">
          <select v-model="activeStyleId" @change="handleStyleSwitch" :disabled="styleSwitching">
            <option v-for="(info, key) in styles" :key="key" :value="key">{{ info.name }}</option>
          </select>
          <span v-if="styleSwitching" class="style-spinner"></span>
        </div>
        <div class="template-indicator">
          <span class="template-label">当前模板:</span>
          <span class="template-name">{{ templateDisplayName }}</span>
        </div>
        <div class="export-buttons">
          <button 
            class="export-btn original"
            @click="handleExport(false)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7,10 12,15 17,10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>导出原文</span>
          </button>
          <button 
            class="export-btn optimized"
            @click="handleExport(true)"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            <span>导出优化版</span>
          </button>
        </div>
        <div class="view-toggle">
          <button 
            class="toggle-btn"
            :class="{ active: viewMode === 'side' }"
            @click="viewMode = 'side'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="12" y1="3" x2="12" y2="21"/>
            </svg>
          </button>
          <button 
            class="toggle-btn"
            :class="{ active: viewMode === 'unified' }"
            @click="viewMode = 'unified'"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="3" y1="12" x2="21" y2="12"/>
              <line x1="3" y1="6" x2="21" y2="6"/>
              <line x1="3" y1="18" x2="21" y2="18"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div class="summary-banner">
      <div class="banner-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
        </svg>
      </div>
      <div class="banner-content">
        <div class="banner-label">AI 分析总结</div>
        <div class="banner-text">{{ suggestions?.overall_summary || '暂无总结' }}</div>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-value">{{ sections.length }}</div>
        <div class="stat-label">识别模块</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ totalIssues }}</div>
        <div class="stat-label">问题数量</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ totalSuggestions }}</div>
        <div class="stat-label">优化建议</div>
      </div>
      <div class="stat-card highlight">
        <div class="stat-value">{{ sectionsWithRewrite }}</div>
        <div class="stat-label">可优化模块</div>
      </div>
    </div>

    <div class="section-tabs">
      <button 
        v-for="(section, idx) in sections"
        :key="idx"
        class="section-tab"
        :class="{ active: activeSection === idx }"
        @click="activeSection = idx"
      >
        <span class="tab-index">{{ String(idx + 1).padStart(2, '0') }}</span>
        <span class="tab-name">{{ section.name }}</span>
        <span v-if="getSuggestionForSection(idx)?.rewrite_example" class="tab-badge">优化</span>
      </button>
    </div>

    <div v-if="currentSuggestion" class="diff-container" :class="viewMode">
      <div v-if="viewMode === 'side'" class="side-by-side">
        <div class="diff-panel original">
          <div class="panel-header">
            <div class="panel-label">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14,2 14,8 20,8"/>
              </svg>
              <span>原始内容</span>
            </div>
            <button class="panel-action" @click="copyOriginal">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
            </button>
          </div>
          <div class="panel-content">
            <div class="edit-wrapper">
              <textarea
                v-model="currentSection.content"
                class="content-text editable"
                @input="handleContentEdit($event.target.value)"
                placeholder="在此编辑内容..."
              ></textarea>
              <div class="edit-overlay">
                <div class="edit-hint">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                  <span>可编辑</span>
                </div>
                <div class="save-status" :class="saveStatus">
                  <svg v-if="saveStatus === 'saving'" class="spinner" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4 31.4" transform="rotate(0 12 12)"/>
                  </svg>
                  <svg v-else-if="saveStatus === 'saved'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                    <polyline points="22,4 12,14.01 9,11.01"/>
                  </svg>
                  <svg v-else-if="saveStatus === 'error'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="15" y1="9" x2="9" y2="15"/>
                    <line x1="9" y1="9" x2="15" y2="15"/>
                  </svg>
                  <span v-if="saveStatus === 'saving'">保存中...</span>
                  <span v-else-if="saveStatus === 'saved'">已保存</span>
                  <span v-else-if="saveStatus === 'error'">保存失败</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="diff-panel optimized">
          <div class="panel-header">
            <div class="panel-label optimized-label">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              <span>AI 优化建议</span>
            </div>
            <button 
              v-if="currentSuggestion.rewrite_example"
              class="panel-action primary"
              @click="applyRewrite"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9"/>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
              <span>应用改写</span>
            </button>
            <button 
              v-if="currentSuggestion.rewrite_example"
              class="panel-action"
              @click="copyRewrite"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
              </svg>
              <span>{{ copiedRewrite ? '已复制' : '复制' }}</span>
            </button>
          </div>
          <div class="panel-content">
            <div v-if="currentSuggestion.rewrite_example" class="rewrite-content">
              <div class="content-text optimized-text">{{ currentSuggestion.rewrite_example }}</div>
            </div>
            <div v-else class="no-rewrite">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
              <span>该模块暂无改写建议</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="unified-view">
        <div class="unified-block original-block">
          <div class="block-header">
            <span class="block-label">原始内容</span>
          </div>
          <div class="block-content">{{ currentSection?.content || '无内容' }}</div>
        </div>
        
        <div class="unified-arrow">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/>
            <polyline points="19,12 12,19 5,12"/>
          </svg>
        </div>
        
        <div class="unified-block optimized-block">
          <div class="block-header">
            <span class="block-label">AI 优化</span>
          </div>
          <div class="block-content">{{ currentSuggestion.rewrite_example || '暂无改写建议' }}</div>
        </div>
      </div>
    </div>

    <div v-if="currentSuggestion" class="analysis-panel">
      <div class="analysis-grid">
        <div class="analysis-card issues-card">
          <div class="card-header">
            <div class="card-icon issue-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </div>
            <h3 class="card-title">存在的问题</h3>
            <span class="card-count">{{ currentSuggestion.issues?.length || 0 }}</span>
          </div>
          <div class="card-body">
            <div v-if="currentSuggestion.issues?.length" class="tag-list">
              <span 
                v-for="(issue, idx) in currentSuggestion.issues" 
                :key="idx"
                class="issue-tag"
              >
                {{ issue }}
              </span>
            </div>
            <div v-else class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22,4 12,14.01 9,11.01"/>
              </svg>
              <span>该模块表现良好</span>
            </div>
          </div>
        </div>

        <div class="analysis-card suggestions-card">
          <div class="card-header">
            <div class="card-icon suggestion-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9"/>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
            </div>
            <h3 class="card-title">优化建议</h3>
            <span class="card-count">{{ currentSuggestion.recommendations?.length || 0 }}</span>
          </div>
          <div class="card-body">
            <ul v-if="currentSuggestion.recommendations?.length" class="suggestion-list">
              <li 
                v-for="(rec, idx) in currentSuggestion.recommendations" 
                :key="idx"
              >
                {{ rec }}
              </li>
            </ul>
            <div v-else class="empty-state">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              <span>暂无优化建议</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showPrintView" class="print-overlay" @click.self="showPrintView = false">
        <div class="print-modal">
          <div class="print-header">
            <h3>{{ printOptimized ? '优化版简历预览' : '原始简历预览' }}</h3>
            <div class="print-actions">
              <button class="print-btn print-action" @click="doPrint">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6 9 6 2 18 2 18 9"/>
                  <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
                  <rect x="6" y="14" width="12" height="8"/>
                </svg>
                打印
              </button>
              <button class="print-btn pdf-action" @click="exportAsPdf">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14,2 14,8 20,8"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
                导出PDF
              </button>
              <button class="close-btn" @click="showPrintView = false">关闭</button>
            </div>
          </div>
          <div class="print-body">
            <div class="resume-paper" id="resume-paper" v-html="fullTemplateHtml"></div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import html2pdf from 'html2pdf.js';
import { getStyles, transformStyle } from '../api/client';
import { toast } from '../composables/useToast';
import type { Section, SuggestionsResponse, SuggestionsItem, StyleInfo } from '../types';

const props = defineProps<{
  sections: Section[];
  suggestions: SuggestionsResponse | null;
  resumeId: number | null;
  selectedTemplate?: string;
  images?: string[];
}>();

const emit = defineEmits<{
  'style-changed': [sections: Section[]];
  'sections-updated': [sections: Section[]];
  'back': [];
  'open-templates': [];
}>();

const activeSection = ref(0);
const viewMode = ref<'side' | 'unified'>('side');
const copiedRewrite = ref(false);
const showPrintView = ref(false);
const printOptimized = ref(false);
const styles = ref<Record<string, StyleInfo>>({});
const activeStyleId = ref('');
const styleSwitching = ref(false);

onMounted(async () => {
  try {
    styles.value = await getStyles();
    activeStyleId.value = props.selectedTemplate || 'minimal-clean';
  } catch { /* styles unavailable */ }
});

async function handleStyleSwitch() {
  if (!props.resumeId || !activeStyleId.value) return;
  styleSwitching.value = true;
  try {
    const result = await transformStyle(props.resumeId, activeStyleId.value);
    emit('style-changed', result.sections);
  } catch {
    toast.error('风格切换失败');
  } finally {
    styleSwitching.value = false;
  }
}

const editedSections = ref<Section[]>([]);
const isEditing = ref(false);
const saveStatus = ref<'idle' | 'saving' | 'saved' | 'error'>('idle');
let saveTimeout: ReturnType<typeof setTimeout> | null = null;

watch(() => props.sections, (newSections) => {
  editedSections.value = JSON.parse(JSON.stringify(newSections));
}, { immediate: true, deep: true });

const currentSection = computed(() => editedSections.value[activeSection.value]);

const currentSuggestion = computed(() => {
  if (!props.suggestions?.items) return null;
  const section = currentSection.value;
  if (!section) return null;
  
  // 只按名称匹配，不匹配时返回null，避免错位
  const matched = props.suggestions.items.find(item => item.name === section.name);
  return matched || null;
});

const totalIssues = computed(() => {
  return props.suggestions?.items?.reduce((sum, item) => sum + (item.issues?.length || 0), 0) || 0;
});

const totalSuggestions = computed(() => {
  return props.suggestions?.items?.reduce((sum, item) => sum + (item.recommendations?.length || 0), 0) || 0;
});

const sectionsWithRewrite = computed(() => {
  return props.suggestions?.items?.filter(item => item.rewrite_example)?.length || 0;
});

const selectedTemplate = computed(() => props.selectedTemplate || 'minimal-clean');

const avatarImage = computed(() => {
  if (props.images && props.images.length > 0) {
    return props.images[0];
  }
  return null;
});

const templateDisplayName = computed(() => {
  const names: Record<string, string> = {
    'executive': '高管专业版',
    'modern-tech': '现代科技',
    'creative-design': '创意流程',
    'minimal-clean': '极简清新',
    'elegant': '优雅经典',
    'startup': '创业先锋',
    'modern-minimal': '现代简约'
  };
  return names[selectedTemplate.value] || '极简清新';
});

const templateAccentColors: Record<string, string> = {
  'executive': '#1e3a5f',
  'modern-tech': '#0369a1',
  'creative-design': '#86198f',
  'minimal-clean': '#374151',
  'elegant': '#92400e',
  'startup': '#047857',
  'modern-minimal': '#7c3aed'
};

const basicInfo = computed(() => {
  if (!props.sections || props.sections.length === 0) {
    return { name: '简历', contact: '' };
  }
  
  const basic = props.sections.find(s => /基本|个人|联系方式|信息/i.test(s.name));
  
  if (!basic) {
    const firstSection = props.sections[0];
    if (firstSection) {
      const lines = firstSection.content?.split('\n').filter(l => l.trim()) || [];
      return {
        name: lines[0] || '简历',
        contact: lines.slice(1, 4).join(' | ') || ''
      };
    }
    return { name: '简历', contact: '' };
  }
  
  const lines = basic.content?.split('\n').filter(l => l.trim()) || [];
  return {
    name: lines[0] || '简历',
    contact: lines.slice(1, 4).join(' | ') || ''
  };
});

const printSections = computed(() => {
  if (!editedSections.value || editedSections.value.length === 0) {
    return [];
  }
  
  const filteredSections = editedSections.value.filter(s => !/基本|个人|联系方式/i.test(s.name));
  
  const sectionsToUse = filteredSections.length > 0 ? filteredSections : editedSections.value;
  
  return sectionsToUse.map(section => {
    if (printOptimized.value && props.suggestions) {
      const item = props.suggestions.items?.find(i => i.name === section.name);
      if (item?.rewrite_example) {
        return { ...section, content: item.rewrite_example };
      }
    }
    return section;
  });
});

function handleContentEdit(newContent: string) {
  if (!currentSection.value) return;
  
  currentSection.value.content = newContent;
  
  if (saveTimeout) {
    clearTimeout(saveTimeout);
  }
  
  saveStatus.value = 'saving';
  
  saveTimeout = setTimeout(() => {
    autoSave();
  }, 1000);
}

async function autoSave() {
  try {
    emit('sections-updated', editedSections.value);
    saveStatus.value = 'saved';
    
    setTimeout(() => {
      saveStatus.value = 'idle';
    }, 2000);
  } catch (error) {
    console.error('保存失败:', error);
    saveStatus.value = 'error';
    
    setTimeout(() => {
      saveStatus.value = 'idle';
    }, 3000);
  }
}

function applyRewrite() {
  if (!currentSuggestion.value?.rewrite_example || !currentSection.value) return;
  
  currentSection.value.content = currentSuggestion.value.rewrite_example;
  handleContentEdit(currentSection.value.content);
}

function getSuggestionForSection(idx: number): SuggestionsItem | null {
  if (!props.suggestions?.items) return null;
  const section = editedSections.value[idx];
  if (!section) return null;
  // 只按名称匹配，不匹配时返回null，避免错位
  return props.suggestions.items.find(item => item.name === section.name) || null;
}

async function copyOriginal() {
  const text = currentSection.value?.content;
  if (!text) return;
  await navigator.clipboard.writeText(text);
}

async function copyRewrite() {
  const text = currentSuggestion.value?.rewrite_example;
  if (!text) return;
  await navigator.clipboard.writeText(text);
  copiedRewrite.value = true;
  setTimeout(() => { copiedRewrite.value = false; }, 2000);
}

function handleExport(useOptimized: boolean) {
  printOptimized.value = useOptimized;
  showPrintView.value = true;
}

function doPrint() {
  window.print();
}

function exportAsPdf() {
  const paper = document.getElementById('resume-paper');
  if (!paper) {
    toast.error('无法找到简历内容，请重试');
    return;
  }
  
  const content = paper.innerHTML;
  if (!content || content.trim() === '') {
    toast.error('简历内容为空，请先上传简历');
    return;
  }
  
  const opt = {
    margin: 10,
    filename: printOptimized.value ? 'resume_optimized.pdf' : 'resume.pdf',
    image: { type: 'jpeg', quality: 1 },
    html2canvas: { 
      scale: 2, 
      useCORS: true, 
      logging: false,
      allowTaint: true,
      scrollY: 0,
      imageTimeout: 0,
      removeContainer: true
    },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
  };
  
  html2pdf().set(opt).from(paper).save().catch((err) => {
    console.error('PDF export error:', err);
    toast.error('PDF导出失败，请重试');
  });
}

function escHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function getFullTemplateHtml(templateId: string, sections: Section[], basicInfoData: { name: string; contact: string }, avatarUrl: string | null): string {
  const accentColor = templateAccentColors[templateId] || '#374151';
  const name = escHtml(basicInfoData.name || '姓名');
  const contact = escHtml(basicInfoData.contact || '');
  
  // 获取基本信息模块
  const basicSection = sections.find(s => /^基本|^个人|^联系|^信息/i.test(s.name));
  
  // 过滤掉基本信息模块，其余模块按原始顺序显示
  const displaySections = sections.filter(s => !(/^基本|^个人|^联系|^信息/i.test(s.name)));
  
  const avatarHtml = avatarUrl 
    ? `<img src="${avatarUrl}" alt="证件照" style="width:100%;height:100%;object-fit:cover;border-radius:50%;" />`
    : `<svg viewBox="0 0 100 100" style="width:100%;height:100%;">
        <circle cx="50" cy="35" r="25" fill="#f5d0c5"/>
        <ellipse cx="50" cy="90" rx="35" ry="25" fill="#374151"/>
        <rect x="35" y="55" width="30" height="20" fill="#ffffff" rx="2"/>
        <path d="M 40 75 L 50 85 L 60 75" fill="#dc2626"/>
        <circle cx="42" cy="32" r="3" fill="#1f2937"/>
        <circle cx="58" cy="32" r="3" fill="#1f2937"/>
      </svg>`;
  
  const contactParts = contact.split('|').map(p => p.trim()).filter(p => p);
  
  if (templateId === 'creative-design') {
    return `
      <div class="resume-template creative">
        <div class="resume-banner" style="background: linear-gradient(135deg, ${accentColor}, #ec4899);">
          <div class="banner-content">
            <div class="banner-left">
              <h1 class="banner-title-cn">个人简历</h1>
              <p class="banner-title-en">Personal Resume</p>
              <p class="banner-slogan">${name}</p>
              <div class="banner-icons">
                <span class="icon-gold">🎨</span>
                <span class="icon-gold">✨</span>
              </div>
            </div>
            <div class="banner-right">
              <div class="avatar-circle">${avatarHtml}</div>
            </div>
          </div>
          <div class="banner-accent"></div>
        </div>
        <div class="resume-body-modern">
          <section class="resume-section-modern">
            <div class="section-block" style="background: linear-gradient(135deg, ${accentColor}, #ec4899);">
              <span class="block-pattern"></span>
              <h3>关于我</h3>
            </div>
            <div class="section-grid">
              ${contactParts.map(p => `<div class="grid-item"><span class="value">${p}</span></div>`).join('')}
            </div>
          </section>
          ${displaySections.map(section => `
          <section class="resume-section-modern">
            <div class="section-block" style="background: linear-gradient(135deg, ${accentColor}, #ec4899);">
              <span class="block-pattern"></span>
              <h3>${escHtml(section.name)}</h3>
            </div>
            <div class="work-item-modern">
              <p class="work-detail-text" style="white-space: pre-wrap;">${escHtml(section.content || '')}</p>
            </div>
          </section>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  if (templateId === 'elegant') {
    return `
      <div class="resume-template elegant">
        <div class="resume-banner" style="background: linear-gradient(135deg, ${accentColor}, #d97706);">
          <div class="banner-content">
            <div class="banner-left">
              <h1 class="banner-title-cn">个人简历</h1>
              <p class="banner-title-en">Personal Resume</p>
              <p class="banner-slogan">${name}</p>
              <div class="banner-icons">
                <span class="icon-gold">👔</span>
                <span class="icon-gold">📊</span>
              </div>
            </div>
            <div class="banner-right">
              <div class="avatar-circle">${avatarHtml}</div>
            </div>
          </div>
          <div class="banner-accent"></div>
        </div>
        <div class="resume-body-modern">
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>基本信息</h3>
            </div>
            <div class="section-grid">
              ${contactParts.map(p => `<div class="grid-item"><span class="value">${p}</span></div>`).join('')}
            </div>
          </section>
          ${displaySections.map(section => `
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>${escHtml(section.name)}</h3>
            </div>
            <div class="work-item-modern">
              <p class="work-detail-text" style="white-space: pre-wrap;">${escHtml(section.content || '')}</p>
            </div>
          </section>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  if (templateId === 'modern-minimal') {
    return `
      <div class="resume-template modern-minimal">
        <div class="resume-banner" style="background: linear-gradient(135deg, ${accentColor}, #a78bfa);">
          <div class="banner-content">
            <div class="banner-left">
              <h1 class="banner-title-cn">个人简历</h1>
              <p class="banner-title-en">Personal Resume</p>
              <p class="banner-slogan">${name}</p>
              <div class="banner-icons">
                <span class="icon-gold">🌿</span>
                <span class="icon-gold">✉️</span>
              </div>
            </div>
            <div class="banner-right">
              <div class="avatar-circle">${avatarHtml}</div>
            </div>
          </div>
          <div class="banner-accent"></div>
        </div>
        <div class="resume-body-modern">
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>基本信息</h3>
            </div>
            <div class="section-grid">
              ${contactParts.map(p => `<div class="grid-item"><span class="value">${p}</span></div>`).join('')}
            </div>
          </section>
          ${displaySections.map(section => `
          <section class="resume-section-modern">
            <div class="section-block" style="background: ${accentColor};">
              <span class="block-pattern"></span>
              <h3>${escHtml(section.name)}</h3>
            </div>
            <div class="work-item-modern">
              <p class="work-detail-text" style="white-space: pre-wrap;">${escHtml(section.content || '')}</p>
            </div>
          </section>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  if (templateId === 'startup') {
    return `
      <div class="resume-template startup-a4">
        <div class="startup-header">
          <div class="startup-header-content">
            <div class="startup-left">
              <h1 class="startup-name">${name}</h1>
              <p class="startup-intention">
                ${contactParts.map((p, i) => `<span>${p}</span>${i < contactParts.length - 1 ? '<span class="startup-pipe">|</span>' : ''}`).join('')}
              </p>
            </div>
            <div class="startup-right">
              <div class="startup-avatar">${avatarHtml}</div>
            </div>
          </div>
        </div>
        <div class="startup-body">
          ${displaySections.map(section => `
          <section class="startup-section">
            <h2 class="startup-section-title">${escHtml(section.name)}</h2>
            <div class="startup-divider"></div>
            <div class="startup-entry">
              <div class="startup-entry-detail">
                <p class="startup-detail-text" style="white-space: pre-wrap;">${escHtml(section.content || '')}</p>
              </div>
            </div>
          </section>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  if (templateId === 'executive') {
    return `
      <div class="resume-template executive-pro">
        <div class="resume-header-pro">
          <div class="header-left">
            <h1 class="name-title">${name}</h1>
            <div class="info-lines">
              ${contactParts.map(p => `<p class="info-line">${p}</p>`).join('')}
            </div>
          </div>
          <div class="header-right">
            <div class="avatar-pro">${avatarHtml}</div>
          </div>
        </div>
        <div class="resume-body-pro">
          ${displaySections.map(section => `
          <section class="section-pro">
            <div class="section-banner" style="background: ${accentColor};">
              <h3>${escHtml(section.name)}</h3>
            </div>
            <div class="section-content">
              <div class="entry-item">
                <div class="entry-details">
                  <p class="detail-line" style="white-space: pre-wrap;">${escHtml(section.content || '')}</p>
                </div>
              </div>
            </div>
          </section>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  if (templateId === 'modern-tech') {
    return `
      <div class="resume-template tech-a4">
        <div class="tech-header">
          <div class="tech-header-main">
            <h1 class="tech-name">${name}</h1>
            <div class="tech-info-block">
              ${contactParts.map(p => `<p class="tech-info-line">${p}</p>`).join('')}
            </div>
          </div>
          <div class="tech-avatar">${avatarHtml}</div>
        </div>
        <div class="tech-body">
          ${displaySections.map(section => `
          <section class="tech-section">
            <div class="tech-banner" style="background: ${accentColor};">
              <h3>${escHtml(section.name)}</h3>
            </div>
            <div class="tech-content">
              <div class="tech-entry">
                <div class="tech-entry-detail">
                  <p class="tech-detail-text" style="white-space: pre-wrap;">${escHtml(section.content || '')}</p>
                </div>
              </div>
            </div>
          </section>
          `).join('')}
        </div>
      </div>
    `;
  }
  
  return `
    <div class="resume-template minimal-a4">
      <div class="minimal-header">
        <div class="minimal-header-content">
          <h1 class="minimal-name">${name}</h1>
          <div class="minimal-info-lines">
            ${contactParts.map(p => `<p class="minimal-info-row">${p}</p>`).join('')}
          </div>
        </div>
        <div class="minimal-avatar">${avatarHtml}</div>
      </div>
      <div class="minimal-body">
        ${displaySections.map(section => `
        <section class="minimal-section">
          <h2 class="minimal-section-title">${escHtml(section.name)}</h2>
          <div class="minimal-divider"></div>
          <div class="minimal-entry">
            <div class="minimal-entry-detail">
              <p class="minimal-detail-text" style="white-space: pre-wrap;">${escHtml(section.content || '')}</p>
            </div>
          </div>
        </section>
        `).join('')}
      </div>
    </div>
  `;
}

const fullTemplateHtml = computed(() => {
  return getFullTemplateHtml(
    selectedTemplate.value,
    printSections.value,
    basicInfo.value || { name: '姓名', contact: '' },
    avatarImage.value
  );
});
</script>

<style scoped>
.diff-view {
  max-width: 1400px;
  margin: 0 auto;
  animation: fade-up 0.5s ease;
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.diff-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
}

.diff-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--white);
  margin-bottom: 6px;
}

.diff-subtitle {
  font-size: 15px;
  color: var(--slate-400);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  color: var(--slate-400);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-right: 16px;
}

.back-btn:hover {
  background: var(--white-alpha-10);
  color: var(--white);
}

.template-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 500;
  color: var(--slate-400);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.template-btn:hover {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: var(--emerald-400);
}

.style-switcher {
  display: flex;
  align-items: center;
  gap: 8px;
}

.style-switcher select {
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 500;
  color: var(--white);
  cursor: pointer;
  outline: none;
  transition: border-color var(--transition-fast);
}

.style-switcher select:focus {
  border-color: rgba(16, 185, 129, 0.3);
}

.style-switcher select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.style-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(250, 250, 250, 0.1);
  border-top-color: var(--emerald-400);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.template-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-lg);
  font-size: 13px;
}

.template-label {
  color: var(--slate-500);
}

.template-name {
  font-weight: 600;
  color: var(--emerald-400);
}

.export-buttons {
  display: flex;
  gap: 8px;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.export-btn svg {
  width: 16px;
  height: 16px;
}

.export-btn.original {
  background: var(--bg-tertiary);
  color: var(--slate-300);
  border: var(--border-subtle);
}

.export-btn.original:hover {
  background: var(--bg-elevated);
  color: var(--white);
}

.export-btn.optimized {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  color: var(--bg-primary);
  box-shadow: var(--glow-emerald);
}

.export-btn.optimized:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
}

.view-toggle {
  display: flex;
  gap: 4px;
  padding: 4px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-md);
}

.toggle-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  border-radius: var(--radius-sm);
  color: var(--slate-500);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.toggle-btn svg {
  width: 18px;
  height: 18px;
}

.toggle-btn:hover {
  color: var(--white);
}

.toggle-btn.active {
  background: rgba(16, 185, 129, 0.2);
  color: var(--emerald-400);
}

.summary-banner {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px 24px;
  background: rgba(16, 185, 129, 0.05);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-xl);
  margin-bottom: 24px;
}

.banner-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 185, 129, 0.1);
  border-radius: var(--radius-lg);
  color: var(--emerald-400);
  flex-shrink: 0;
}

.banner-icon svg {
  width: 22px;
  height: 22px;
}

.banner-content {
  flex: 1;
}

.banner-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--emerald-400);
  margin-bottom: 6px;
}

.banner-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--slate-300);
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 20px;
  text-align: center;
}

.stat-card.highlight {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border-color: transparent;
}

.stat-card.highlight .stat-value,
.stat-card.highlight .stat-label {
  color: var(--bg-primary);
}

.stat-value {
  font-family: 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 32px;
  font-weight: 700;
  color: var(--white);
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--emerald-400);
  margin-top: 8px;
}

.section-tabs {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 8px;
  margin-bottom: 24px;
  scrollbar-width: thin;
  scrollbar-color: var(--emerald-500) var(--bg-tertiary);
}

.section-tabs::-webkit-scrollbar {
  height: 6px;
}

.section-tabs::-webkit-scrollbar-track {
  background: var(--bg-tertiary);
  border-radius: var(--radius-full);
}

.section-tabs::-webkit-scrollbar-thumb {
  background: linear-gradient(90deg, var(--emerald-500), var(--teal-500));
  border-radius: var(--radius-full);
  border: 2px solid var(--bg-tertiary);
}

.section-tabs::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(90deg, var(--emerald-400), var(--teal-400));
}

.section-tab {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 18px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-lg);
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast);
  color: var(--slate-400);
}

.section-tab:hover {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.05);
  color: var(--white);
}

.section-tab.active {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border-color: transparent;
  color: var(--bg-primary);
}

.tab-index {
  font-size: 11px;
  font-weight: 600;
  opacity: 0.6;
  font-family: 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
}

.tab-name {
  font-size: 13px;
  font-weight: 600;
}

.tab-badge {
  padding: 3px 8px;
  background: rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-full);
  font-size: 10px;
  font-weight: 700;
  color: var(--emerald-400);
}

.section-tab.active .tab-badge {
  background: rgba(0, 0, 0, 0.2);
  color: var(--bg-primary);
}

.diff-container {
  margin-bottom: 24px;
}

.side-by-side {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.diff-panel {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.diff-panel.optimized {
  border-color: rgba(16, 185, 129, 0.3);
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.1);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--bg-tertiary);
  border-bottom: var(--border-subtle);
}

.diff-panel.optimized .panel-header {
  background: rgba(16, 185, 129, 0.1);
  border-bottom-color: rgba(16, 185, 129, 0.2);
}

.panel-label {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--slate-300);
}

.panel-label svg {
  width: 18px;
  height: 18px;
}

.optimized-label {
  color: var(--emerald-400);
}

.panel-action {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--bg-elevated);
  border: var(--border-subtle);
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 600;
  color: var(--slate-400);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.panel-action svg {
  width: 14px;
  height: 14px;
}

.panel-action:hover {
  background: var(--bg-tertiary);
  color: var(--white);
}

.panel-action.primary {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border-color: transparent;
  color: var(--bg-primary);
}

.panel-action.primary:hover {
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.panel-content {
  padding: 24px;
  min-height: 300px;
}

.edit-wrapper {
  position: relative;
}

.content-text {
  width: 100%;
  min-height: 300px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--slate-300);
  white-space: pre-wrap;
  word-break: break-word;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  font-family: inherit;
  padding: 0;
}

.content-text.editable {
  cursor: text;
  transition: all var(--transition-fast);
}

.content-text.editable:focus {
  color: var(--white);
}

.edit-overlay {
  position: absolute;
  top: 0;
  right: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.edit-wrapper:hover .edit-overlay,
.edit-wrapper:focus-within .edit-overlay {
  opacity: 1;
}

.edit-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--slate-400);
}

.edit-hint svg {
  width: 14px;
  height: 14px;
}

.save-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.save-status.idle {
  color: var(--slate-400);
}

.save-status.saving {
  color: var(--amber-400);
  background: rgba(251, 191, 36, 0.1);
}

.save-status.saved {
  color: var(--emerald-400);
  background: rgba(16, 185, 129, 0.1);
}

.save-status.error {
  color: var(--red-400);
  background: rgba(239, 68, 68, 0.1);
}

.save-status svg {
  width: 14px;
  height: 14px;
}

.save-status .spinner {
  animation: spin 1s linear infinite;
}

.optimized-text {
  color: var(--white);
  font-weight: 500;
}

.no-rewrite {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  height: 200px;
  color: var(--slate-500);
}

.no-rewrite svg {
  width: 40px;
  height: 40px;
}

.unified-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.unified-block {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.unified-block.optimized-block {
  border-color: rgba(16, 185, 129, 0.3);
}

.block-header {
  padding: 12px 20px;
  background: var(--bg-tertiary);
  border-bottom: var(--border-subtle);
}

.optimized-block .block-header {
  background: rgba(16, 185, 129, 0.1);
  border-bottom-color: rgba(16, 185, 129, 0.2);
}

.block-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--slate-400);
}

.optimized-block .block-label {
  color: var(--emerald-400);
}

.block-content {
  padding: 20px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--slate-300);
  white-space: pre-wrap;
}

.unified-arrow {
  display: flex;
  justify-content: center;
  color: var(--emerald-500);
}

.unified-arrow svg {
  width: 24px;
  height: 24px;
}

.analysis-panel {
  margin-top: 24px;
}

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.analysis-card {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 24px;
  background: var(--bg-tertiary);
  border-bottom: var(--border-subtle);
}

.card-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
}

.card-icon svg {
  width: 18px;
  height: 18px;
}

.issue-icon {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.suggestion-icon {
  background: rgba(16, 185, 129, 0.1);
  color: var(--emerald-400);
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--white);
}

.card-count {
  margin-left: auto;
  padding: 4px 10px;
  background: var(--bg-elevated);
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
  color: var(--slate-400);
}

.card-body {
  padding: 20px 24px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.issue-tag {
  padding: 8px 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  color: #f87171;
}

.suggestion-list {
  margin: 0;
  padding-left: 20px;
  color: var(--slate-300);
}

.suggestion-list li {
  margin-bottom: 10px;
  font-size: 13px;
  line-height: 1.6;
}

.suggestion-list li:last-child {
  margin-bottom: 0;
}

.empty-state {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--slate-500);
  font-size: 13px;
}

.empty-state svg {
  width: 20px;
  height: 20px;
}

.print-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
}

.print-modal {
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.print-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: var(--border-subtle);
}

.print-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--white);
}

.print-actions {
  display: flex;
  gap: 12px;
}

.print-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.print-btn svg {
  width: 16px;
  height: 16px;
}

.print-btn.print-action {
  background: var(--bg-tertiary);
  color: var(--slate-300);
}

.print-btn.print-action:hover {
  background: var(--bg-elevated);
  color: var(--white);
}

.print-btn.pdf-action {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  color: var(--bg-primary);
  box-shadow: var(--glow-emerald);
}

.print-btn.pdf-action:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
}

.close-btn {
  padding: 10px 18px;
  background: var(--bg-tertiary);
  border: var(--border-subtle);
  border-radius: var(--radius-lg);
  font-size: 13px;
  font-weight: 600;
  color: var(--slate-300);
  cursor: pointer;
}

.close-btn:hover {
  color: var(--white);
}

.print-body {
  flex: 1;
  overflow: auto;
  padding: 24px;
  background: var(--bg-primary);
}

.resume-paper {
  background: white;
  padding: 0;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  min-height: 800px;
  color: #1e293b;
}

.resume-paper :deep(.resume-template) {
  font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
  color: #1f2937;
  line-height: 1.6;
  background: white;
}

.resume-paper :deep(.resume-template *) {
  box-sizing: border-box;
}

/* Executive Pro Template */
.resume-paper :deep(.resume-template.executive-pro) {
  background: white;
  padding: 0;
}

.resume-paper :deep(.resume-header-pro) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32px 40px;
  border-bottom: 1px solid #e5e7eb;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.resume-paper :deep(.header-left) {
  flex: 1;
}

.resume-paper :deep(.name-title) {
  font-size: 36px;
  font-weight: 800;
  color: #1f2937;
  margin: 0 0 16px 0;
  letter-spacing: 1px;
}

.resume-paper :deep(.info-lines) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resume-paper :deep(.info-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.resume-paper :deep(.header-right) {
  margin-left: 32px;
}

.resume-paper :deep(.avatar-pro) {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  overflow: hidden;
  background: #f3f4f6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.resume-paper :deep(.resume-body-pro) {
  padding: 24px 40px;
}

.resume-paper :deep(.section-pro) {
  margin-bottom: 24px;
}

.resume-paper :deep(.section-banner) {
  padding: 10px 20px;
  color: white;
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 16px;
  border-radius: 4px;
  letter-spacing: 1px;
}

.resume-paper :deep(.section-banner h3) {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

.resume-paper :deep(.section-content) {
  padding: 0 4px;
}

.resume-paper :deep(.entry-item) {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.resume-paper :deep(.entry-item:last-child) {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.resume-paper :deep(.entry-details) {
  padding-left: 0;
}

.resume-paper :deep(.detail-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0 0 6px 0;
  line-height: 1.6;
}

.resume-paper :deep(.skills-list) {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.resume-paper :deep(.skill-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

/* Tech A4 Template */
.resume-paper :deep(.resume-template.tech-a4) {
  background: white;
  padding: 0;
}

.resume-paper :deep(.tech-header) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32px 40px;
  border-bottom: 1px solid #e5e7eb;
  position: relative;
}

.resume-paper :deep(.tech-header-main) {
  flex: 1;
  text-align: center;
}

.resume-paper :deep(.tech-name) {
  font-size: 32px;
  font-weight: 800;
  color: #1f2937;
  margin: 0 0 16px 0;
  letter-spacing: 2px;
}

.resume-paper :deep(.tech-info-block) {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.resume-paper :deep(.tech-info-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.resume-paper :deep(.tech-avatar) {
  position: absolute;
  right: 40px;
  top: 32px;
  width: 90px;
  height: 90px;
  border-radius: 50%;
  overflow: hidden;
  background: #f3f4f6;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.resume-paper :deep(.tech-body) {
  padding: 24px 40px;
}

.resume-paper :deep(.tech-section) {
  margin-bottom: 20px;
}

.resume-paper :deep(.tech-banner) {
  padding: 8px 16px;
  color: white;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 12px;
  border-radius: 2px;
  letter-spacing: 1px;
}

.resume-paper :deep(.tech-banner h3) {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
}

.resume-paper :deep(.tech-content) {
  padding: 0 4px;
}

.resume-paper :deep(.tech-entry) {
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.resume-paper :deep(.tech-entry:last-child) {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.resume-paper :deep(.tech-entry-detail) {
  padding-left: 0;
}

.resume-paper :deep(.tech-detail-text) {
  font-size: 12px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.resume-paper :deep(.tech-skill-item) {
  font-size: 13px;
  color: #374151;
  margin-bottom: 8px;
  line-height: 1.6;
}

/* Minimal A4 Template */
.resume-paper :deep(.resume-template.minimal-a4) {
  background: white;
  padding: 0;
}

.resume-paper :deep(.minimal-header) {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 40px 50px 24px 50px;
  position: relative;
}

.resume-paper :deep(.minimal-header-content) {
  flex: 1;
  text-align: center;
}

.resume-paper :deep(.minimal-name) {
  font-size: 36px;
  font-weight: 800;
  color: #000000;
  margin: 0 0 16px 0;
  letter-spacing: 4px;
}

.resume-paper :deep(.minimal-info-lines) {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.resume-paper :deep(.minimal-info-row) {
  font-size: 13px;
  color: #000000;
  margin: 0;
  line-height: 1.6;
}

.resume-paper :deep(.minimal-avatar) {
  position: absolute;
  right: 50px;
  top: 40px;
  width: 85px;
  height: 85px;
  border-radius: 50%;
  overflow: hidden;
  background: #f3f4f6;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.resume-paper :deep(.minimal-body) {
  padding: 0 50px 40px 50px;
}

.resume-paper :deep(.minimal-section) {
  margin-bottom: 20px;
}

.resume-paper :deep(.minimal-section-title) {
  font-size: 15px;
  font-weight: 700;
  color: #000000;
  margin: 0 0 6px 0;
  letter-spacing: 1px;
}

.resume-paper :deep(.minimal-divider) {
  height: 1px;
  background: #000000;
  margin-bottom: 12px;
  width: 100%;
}

.resume-paper :deep(.minimal-entry) {
  margin-bottom: 12px;
}

.resume-paper :deep(.minimal-entry-detail) {
  padding-left: 0;
}

.resume-paper :deep(.minimal-detail-text) {
  font-size: 13px;
  color: #000000;
  margin: 0;
  line-height: 1.8;
}

.resume-paper :deep(.minimal-skills) {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.resume-paper :deep(.minimal-skill-line) {
  font-size: 13px;
  color: #000000;
  margin: 0;
  line-height: 1.6;
}

.resume-paper :deep(.minimal-evaluation) {
  font-size: 13px;
  color: #000000;
  margin: 0;
  line-height: 1.8;
  text-align: justify;
}

/* Creative Design Template */
.resume-paper :deep(.resume-template.creative) {
  background: white;
  padding: 0;
}

.resume-paper :deep(.resume-template.creative .resume-banner) {
  padding: 40px;
  color: white;
  position: relative;
  overflow: hidden;
}

.resume-paper :deep(.resume-template.creative .banner-content) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resume-paper :deep(.resume-template.creative .banner-left) {
  flex: 1;
}

.resume-paper :deep(.resume-template.creative .banner-title-cn) {
  font-size: 48px;
  font-weight: 800;
  margin: 0 0 8px 0;
  letter-spacing: 4px;
}

.resume-paper :deep(.resume-template.creative .banner-title-en) {
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 12px 0;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.resume-paper :deep(.resume-template.creative .banner-slogan) {
  font-size: 14px;
  opacity: 0.8;
  margin: 0 0 16px 0;
}

.resume-paper :deep(.resume-template.creative .banner-icons) {
  display: flex;
  gap: 12px;
}

.resume-paper :deep(.resume-template.creative .icon-gold) {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
}

.resume-paper :deep(.resume-template.creative .banner-right) {
  margin-left: 40px;
}

.resume-paper :deep(.resume-template.creative .avatar-circle) {
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.resume-paper :deep(.resume-template.creative .banner-accent) {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #86198f, #fbbf24, #86198f);
}

.resume-paper :deep(.resume-template.creative .resume-body-modern) {
  padding: 32px 40px;
}

.resume-paper :deep(.resume-template.creative .resume-section-modern) {
  margin-bottom: 28px;
}

.resume-paper :deep(.resume-template.creative .section-block) {
  padding: 10px 20px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  letter-spacing: 2px;
}

.resume-paper :deep(.resume-template.creative .block-pattern) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 3px,
    rgba(255, 255, 255, 0.1) 3px,
    rgba(255, 255, 255, 0.1) 6px
  );
}

.resume-paper :deep(.resume-template.creative .section-block h3) {
  margin: 0;
  position: relative;
  z-index: 1;
}

.resume-paper :deep(.resume-template.creative .section-grid) {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px 24px;
}

.resume-paper :deep(.resume-template.creative .grid-item) {
  font-size: 14px;
  color: #374151;
}

.resume-paper :deep(.resume-template.creative .grid-item .value) {
  color: #1f2937;
  font-weight: 600;
}

.resume-paper :deep(.resume-template.creative .work-item-modern) {
  margin-bottom: 16px;
}

.resume-paper :deep(.resume-template.creative .work-detail-text) {
  font-size: 14px;
  color: #4b5563;
  margin: 0;
  line-height: 1.8;
}

.resume-paper :deep(.resume-template.creative .skill-tags-modern) {
  font-size: 14px;
  color: #4b5563;
  line-height: 1.8;
}

/* Elegant Template */
.resume-paper :deep(.resume-template.elegant) {
  background: white;
  padding: 0;
}

.resume-paper :deep(.resume-template.elegant .resume-banner) {
  padding: 40px;
  color: white;
  position: relative;
  overflow: hidden;
}

.resume-paper :deep(.resume-template.elegant .banner-content) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resume-paper :deep(.resume-template.elegant .banner-left) {
  flex: 1;
}

.resume-paper :deep(.resume-template.elegant .banner-title-cn) {
  font-size: 48px;
  font-weight: 800;
  margin: 0 0 8px 0;
  letter-spacing: 4px;
}

.resume-paper :deep(.resume-template.elegant .banner-title-en) {
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 12px 0;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.resume-paper :deep(.resume-template.elegant .banner-slogan) {
  font-size: 14px;
  opacity: 0.8;
  margin: 0 0 16px 0;
}

.resume-paper :deep(.resume-template.elegant .banner-icons) {
  display: flex;
  gap: 12px;
}

.resume-paper :deep(.resume-template.elegant .icon-gold) {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
}

.resume-paper :deep(.resume-template.elegant .banner-right) {
  margin-left: 40px;
}

.resume-paper :deep(.resume-template.elegant .avatar-circle) {
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.resume-paper :deep(.resume-template.elegant .banner-accent) {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #92400e, #fbbf24, #92400e);
}

.resume-paper :deep(.resume-template.elegant .resume-body-modern) {
  padding: 32px 40px;
}

.resume-paper :deep(.resume-template.elegant .resume-section-modern) {
  margin-bottom: 28px;
}

.resume-paper :deep(.resume-template.elegant .section-block) {
  padding: 10px 20px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  letter-spacing: 2px;
}

.resume-paper :deep(.resume-template.elegant .block-pattern) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 3px,
    rgba(255, 255, 255, 0.1) 3px,
    rgba(255, 255, 255, 0.1) 6px
  );
}

.resume-paper :deep(.resume-template.elegant .section-block h3) {
  margin: 0;
  position: relative;
  z-index: 1;
}

.resume-paper :deep(.resume-template.elegant .section-grid) {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px 24px;
}

.resume-paper :deep(.resume-template.elegant .grid-item) {
  font-size: 14px;
  color: #374151;
}

.resume-paper :deep(.resume-template.elegant .grid-item .value) {
  color: #1f2937;
  font-weight: 600;
}

.resume-paper :deep(.resume-template.elegant .edu-item-modern) {
  margin-bottom: 12px;
}

.resume-paper :deep(.resume-template.elegant .edu-detail-text) {
  font-size: 14px;
  color: #4b5563;
  margin: 0;
  line-height: 1.8;
}

.resume-paper :deep(.resume-template.elegant .work-item-modern) {
  margin-bottom: 16px;
}

.resume-paper :deep(.resume-template.elegant .work-detail-text) {
  font-size: 14px;
  color: #4b5563;
  margin: 0;
  line-height: 1.8;
}

.resume-paper :deep(.resume-template.elegant .skill-tags-modern) {
  font-size: 14px;
  color: #4b5563;
  line-height: 1.8;
}

/* Modern Minimal Template */
.resume-paper :deep(.resume-template.modern-minimal) {
  background: white;
  padding: 0;
}

.resume-paper :deep(.resume-template.modern-minimal .resume-banner) {
  padding: 40px;
  color: white;
  position: relative;
  overflow: hidden;
}

.resume-paper :deep(.resume-template.modern-minimal .banner-content) {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resume-paper :deep(.resume-template.modern-minimal .banner-left) {
  flex: 1;
}

.resume-paper :deep(.resume-template.modern-minimal .banner-title-cn) {
  font-size: 48px;
  font-weight: 800;
  margin: 0 0 8px 0;
  letter-spacing: 4px;
}

.resume-paper :deep(.resume-template.modern-minimal .banner-title-en) {
  font-size: 16px;
  opacity: 0.9;
  margin: 0 0 12px 0;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.resume-paper :deep(.resume-template.modern-minimal .banner-slogan) {
  font-size: 14px;
  opacity: 0.8;
  margin: 0 0 16px 0;
}

.resume-paper :deep(.resume-template.modern-minimal .banner-icons) {
  display: flex;
  gap: 12px;
}

.resume-paper :deep(.resume-template.modern-minimal .icon-gold) {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(251, 191, 36, 0.4);
}

.resume-paper :deep(.resume-template.modern-minimal .banner-right) {
  margin-left: 40px;
}

.resume-paper :deep(.resume-template.modern-minimal .avatar-circle) {
  width: 120px;
  height: 120px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 60px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.resume-paper :deep(.resume-template.modern-minimal .banner-accent) {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #7c3aed, #fbbf24, #7c3aed);
}

.resume-paper :deep(.resume-template.modern-minimal .resume-body-modern) {
  padding: 32px 40px;
}

.resume-paper :deep(.resume-template.modern-minimal .resume-section-modern) {
  margin-bottom: 28px;
}

.resume-paper :deep(.resume-template.modern-minimal .section-block) {
  padding: 10px 20px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
  position: relative;
  overflow: hidden;
  letter-spacing: 2px;
}

.resume-paper :deep(.resume-template.modern-minimal .block-pattern) {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: repeating-linear-gradient(
    45deg,
    transparent,
    transparent 3px,
    rgba(255, 255, 255, 0.1) 3px,
    rgba(255, 255, 255, 0.1) 6px
  );
}

.resume-paper :deep(.resume-template.modern-minimal .section-block h3) {
  margin: 0;
  position: relative;
  z-index: 1;
}

.resume-paper :deep(.resume-template.modern-minimal .section-grid) {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px 24px;
}

.resume-paper :deep(.resume-template.modern-minimal .grid-item) {
  font-size: 14px;
  color: #374151;
}

.resume-paper :deep(.resume-template.modern-minimal .grid-item .value) {
  color: #1f2937;
  font-weight: 600;
}

.resume-paper :deep(.resume-template.modern-minimal .edu-item-modern) {
  margin-bottom: 12px;
}

.resume-paper :deep(.resume-template.modern-minimal .edu-detail-text) {
  font-size: 14px;
  color: #4b5563;
  margin: 0;
  line-height: 1.8;
}

.resume-paper :deep(.resume-template.modern-minimal .work-item-modern) {
  margin-bottom: 16px;
}

.resume-paper :deep(.resume-template.modern-minimal .work-detail-text) {
  font-size: 14px;
  color: #4b5563;
  margin: 0;
  line-height: 1.8;
}

.resume-paper :deep(.resume-template.modern-minimal .skill-tags-modern) {
  font-size: 14px;
  color: #4b5563;
  line-height: 1.8;
}

/* Startup A4 Template */
.resume-paper :deep(.resume-template.startup-a4) {
  background: white;
  padding: 0;
  position: relative;
}

.resume-paper :deep(.startup-header) {
  position: relative;
  background: #0d9488;
}

.resume-paper :deep(.startup-header-content) {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 32px 50px;
  z-index: 1;
}

.resume-paper :deep(.startup-left) {
  flex: 1;
}

.resume-paper :deep(.startup-name) {
  font-size: 32px;
  font-weight: 800;
  color: #ffffff;
  margin: 0 0 12px 0;
  letter-spacing: 2px;
}

.resume-paper :deep(.startup-intention) {
  font-size: 13px;
  color: #ffffff;
  margin: 0 0 16px 0;
  opacity: 0.95;
}

.resume-paper :deep(.startup-pipe) {
  margin: 0 8px;
  opacity: 0.6;
}

.resume-paper :deep(.startup-right) {
  margin-left: 24px;
}

.resume-paper :deep(.startup-avatar) {
  width: 90px;
  height: 90px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.15);
  border: 3px solid #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.resume-paper :deep(.startup-body) {
  padding: 24px 50px 40px 50px;
}

.resume-paper :deep(.startup-section) {
  margin-bottom: 20px;
}

.resume-paper :deep(.startup-section-title) {
  font-size: 15px;
  font-weight: 700;
  color: #0d9488;
  margin: 0 0 6px 0;
  letter-spacing: 1px;
}

.resume-paper :deep(.startup-divider) {
  height: 1px;
  background: #0d9488;
  margin-bottom: 12px;
  width: 100%;
}

.resume-paper :deep(.startup-entry) {
  margin-bottom: 12px;
}

.resume-paper :deep(.startup-entry-detail) {
  padding-left: 0;
}

.resume-paper :deep(.startup-detail-text) {
  font-size: 13px;
  color: #4b5563;
  margin: 0 0 4px 0;
  line-height: 1.8;
}

.resume-paper :deep(.startup-skills) {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.resume-paper :deep(.startup-skill-line) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.resume-paper :deep(.startup-evaluation) {
  font-size: 13px;
  color: #4b5563;
  margin: 0;
  line-height: 1.8;
  text-align: justify;
}

@media print {
  body * {
    visibility: hidden;
  }
  
  .print-modal,
  .print-modal * {
    visibility: visible;
  }
  
  .print-modal {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    max-width: none;
    max-height: none;
    border-radius: 0;
  }
  
  .print-header {
    display: none;
  }
  
  .print-body {
    padding: 0;
    background: white;
  }
  
  .resume-paper {
    box-shadow: none;
    padding: 20mm;
  }
}

@media (max-width: 1024px) {
  .side-by-side {
    grid-template-columns: 1fr;
  }
  
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .diff-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-tabs {
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
  }
}
</style>
