<template>
  <div class="upload-view">
    <div class="bento-grid">
      <div class="bento-hero">
        <div class="hero-content">
          <div class="hero-badge">
            <span class="badge-dot"></span>
            <span>简历星球 · AI 驱动</span>
          </div>
          <h1 class="hero-title">
            智能优化您的简历<br/>
            <span class="gradient-text">智领未来</span>
          </h1>
          <p class="hero-desc">
            上传您的 PDF 简历，让 AI 分析、优化并增强每个部分，实现最大影响力。
          </p>
        </div>
      </div>

      <div class="bento-upload">
        <div class="upload-header">
          <h3>上传简历</h3>
          <span class="upload-format">仅支持 PDF · 最大 20MB</span>
        </div>
        
        <div 
          class="drop-zone"
          :class="{ 'drag-over': isDragOver, 'has-file': file }"
          @dragover.prevent="isDragOver = true"
          @dragleave.prevent="isDragOver = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input 
            ref="fileInput"
            type="file" 
            accept="application/pdf"
            class="hidden-input"
            @change="handleFileChange"
          />
          
          <div class="drop-content">
            <div class="drop-icon">
              <div class="icon-glow"></div>
              <span>{{ file ? '✓' : '⬆' }}</span>
            </div>
            <div class="drop-text">
              <span class="drop-main">{{ file ? file.name : '将 PDF 拖放到此处' }}</span>
              <span class="drop-sub">{{ file ? `${(file.size / 1024).toFixed(1)} KB` : '或点击浏览' }}</span>
            </div>
          </div>
          
          <div class="drop-glow"></div>
        </div>

        <div class="target-job-input">
          <label>目标岗位 <span class="optional-label">(可选)</span></label>
          <input
            v-model="targetJob"
            type="text"
            placeholder="例如：前端开发工程师"
            :disabled="isLoading"
          />
        </div>

        <div class="submit-row">
          <button
            class="submit-btn"
            :class="{ ready: file && !isLoading }"
            :disabled="!file || isLoading"
            @click="handleSubmit"
          >
            <span v-if="isLoading" class="btn-loader"></span>
            <span v-else class="btn-content">
              <span>开始 AI 分析</span>
              <span class="btn-arrow">→</span>
            </span>
          </button>
          <button
            v-if="isLoading"
            class="cancel-btn"
            @click="handleCancel"
          >
            取消分析
          </button>
        </div>

        <div v-if="error" class="error-msg">
          <span>⚠</span>
          <span>{{ error }}</span>
        </div>

        <div v-if="isLoading" class="progress-section">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
            <div class="progress-glow" :style="{ left: `${progress}%` }"></div>
          </div>
          <div class="progress-steps">
            <div 
              v-for="(step, idx) in progressSteps" 
              :key="idx"
              class="step"
              :class="{ active: idx <= currentStep, done: idx < currentStep }"
            >
              <span class="step-num">{{ idx < currentStep ? '✓' : idx + 1 }}</span>
              <span class="step-text">{{ step }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="bento-scene">
        <div class="scene-header">
          <h3>优化模式</h3>
        </div>
        <div class="scene-grid">
          <button
            v-for="(info, key) in styles"
            :key="key"
            class="scene-btn"
            :class="{ active: selectedStyle === key }"
            @click="selectedStyle = key"
          >
            <span class="scene-icon">{{ getSceneIcon(key) }}</span>
            <span class="scene-name">{{ info.name }}</span>
          </button>
        </div>
        <p class="scene-desc">{{ styles[selectedStyle]?.description }}</p>
      </div>

      <div class="bento-features">
        <div class="feature-item">
          <span class="feature-icon">✦</span>
          <div class="feature-text">
            <span class="feature-title">智能分析</span>
            <span class="feature-desc">AI 驱动的结构识别</span>
          </div>
        </div>
        <div class="feature-item">
          <span class="feature-icon">◎</span>
          <div class="feature-text">
            <span class="feature-title">ATS 优化</span>
            <span class="feature-desc">通过 HR 系统筛选</span>
          </div>
        </div>
        <div class="feature-item">
          <span class="feature-icon">◈</span>
          <div class="feature-text">
            <span class="feature-title">6 种场景模式</span>
            <span class="feature-desc">为您的目标量身定制</span>
          </div>
        </div>
      </div>

      <div class="bento-stats">
        <div class="stat">
          <span class="stat-value">6</span>
          <span class="stat-label">模式</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-value">4</span>
          <span class="stat-label">工具</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat">
          <span class="stat-value">∞</span>
          <span class="stat-label">免费</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ocrResume, generateSuggestions, transformStyle, getStyles } from '../api/client';
import type { Section, SuggestionsResponse, StyleInfo } from '../types';

const emit = defineEmits<{
  result: [data: { resumeId: number; sections: Section[]; suggestions: SuggestionsResponse; styleType: string; targetJob: string; images?: string[] }];
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const file = ref<File | null>(null);
const isDragOver = ref(false);
const isLoading = ref(false);
const error = ref('');
const progress = ref(0);
const currentStep = ref(0);
let abortController: AbortController | null = null;

const styles = ref<Record<string, StyleInfo>>({});
const selectedStyle = ref('campus');
const targetJob = ref('');

const progressSteps = ['解析', '分析', '建议', '转换', '完成'];

const sceneIcons: Record<string, string> = {
  campus: '🎓',
  intern: '💼',
  tech: '💻',
  product: '📊',
  operation: '📈',
  english: '🌍',
};

function getSceneIcon(key: string): string {
  return sceneIcons[key] || '📝';
}

onMounted(async () => {
  try {
    styles.value = await getStyles();
  } catch (e) {
    console.error('Failed to load styles:', e);
  }
});

function triggerFileInput() {
  fileInput.value?.click();
}

function handleFileChange(e: Event) {
  const input = e.target as HTMLInputElement;
  const selectedFile = input.files?.[0];
  if (selectedFile) {
    file.value = selectedFile;
    error.value = '';
  }
}

function handleDrop(e: DragEvent) {
  isDragOver.value = false;
  const droppedFile = e.dataTransfer?.files[0];
  if (droppedFile && droppedFile.type === 'application/pdf') {
    file.value = droppedFile;
    error.value = '';
  } else {
    error.value = '请上传 PDF 文件';
  }
}

async function handleSubmit() {
  if (!file.value || isLoading.value) return;

  isLoading.value = true;
  error.value = '';
  progress.value = 0;
  currentStep.value = 0;
  abortController = new AbortController();

  let ocrResult: any = null;

  try {
    progress.value = 5;
    currentStep.value = 0;

    ocrResult = await ocrResume(file.value);
    progress.value = 100;
    currentStep.value = 4;

    const sections = Array.isArray(ocrResult.sections) ? ocrResult.sections as Section[] : [];

    // OCR 完成就立即展示结果，suggestions 和 transform 由 DiffView 后台加载
    emit('result', {
      resumeId: ocrResult.resumeId,
      sections,
      suggestions: null,
      styleType: selectedStyle.value,
      targetJob: targetJob.value,
      images: ocrResult.images || []
    });
  } catch (e: any) {
    if (e instanceof DOMException && e.name === 'AbortError') {
      error.value = '分析已取消';
    } else {
      error.value = e?.message || '分析失败，请重试';
    }
    if (ocrResult) {
      const sections = Array.isArray(ocrResult.sections) ? ocrResult.sections as Section[] : [];
      emit('result', {
        resumeId: ocrResult.resumeId,
        sections,
        suggestions: null,
        styleType: selectedStyle.value,
        targetJob: targetJob.value,
        images: ocrResult.images || []
      });
    }
    progress.value = 0;
    currentStep.value = 0;
  } finally {
    isLoading.value = false;
    abortController = null;
  }
}

function handleCancel() {
  if (abortController) {
    abortController.abort();
  }
}
</script>

<style scoped>
.upload-view {
  max-width: 1100px;
  margin: 0 auto;
  animation: fade-up 0.6s ease;
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto auto auto;
  gap: 16px;
}

.bento-hero {
  grid-column: span 2;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.bento-hero::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(ellipse at center, rgba(16, 185, 129, 0.05) 0%, transparent 50%);
  animation: rotate-glow 20s linear infinite;
}

@keyframes rotate-glow {
  to { transform: rotate(360deg); }
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: var(--emerald-400);
  margin-bottom: 20px;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: var(--emerald-500);
  border-radius: 50%;
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.hero-title {
  font-size: 36px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: var(--white);
  margin-bottom: 16px;
}

.gradient-text {
  background: linear-gradient(135deg, var(--emerald-400), var(--teal-400), var(--cyan-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 15px;
  line-height: 1.7;
  color: var(--slate-400);
  max-width: 400px;
}

.bento-upload {
  grid-column: span 2;
  grid-row: span 2;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 28px;
  display: flex;
  flex-direction: column;
}

.upload-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.upload-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--white);
}

.upload-format {
  font-size: 11px;
  color: var(--slate-500);
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border-radius: 4px;
}

.drop-zone {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  border: 1px dashed rgba(250, 250, 250, 0.1);
  border-radius: var(--radius-lg);
  background: var(--bg-tertiary);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.drop-zone:hover,
.drop-zone.drag-over {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.05);
}

.drop-zone.has-file {
  border-style: solid;
  border-color: rgba(16, 185, 129, 0.4);
}

.drop-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.drop-zone:hover .drop-glow,
.drop-zone.drag-over .drop-glow {
  opacity: 1;
}

.hidden-input {
  display: none;
}

.drop-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  position: relative;
  z-index: 1;
}

.drop-icon {
  position: relative;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--slate-400);
}

.icon-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.drop-zone:hover .icon-glow {
  opacity: 1;
}

.drop-zone.has-file .drop-icon {
  color: var(--emerald-400);
}

.drop-text {
  text-align: center;
}

.drop-main {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--white);
  margin-bottom: 4px;
}

.drop-sub {
  font-size: 12px;
  color: var(--slate-500);
}

.target-job-input {
  margin-top: 16px;
}

.target-job-input label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--slate-400);
  margin-bottom: 6px;
}

.optional-label {
  color: var(--slate-500);
  font-weight: 400;
}

.target-job-input input {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--white);
  outline: none;
  transition: border-color var(--transition-fast);
}

.target-job-input input::placeholder {
  color: var(--slate-500);
}

.target-job-input input:focus {
  border-color: rgba(16, 185, 129, 0.3);
}

.target-job-input input:disabled {
  opacity: 0.5;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  margin-top: 20px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.1);
  border-radius: var(--radius-lg);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: var(--slate-400);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.submit-row {
  margin-top: 20px;
}

.submit-row .submit-btn {
  margin-top: 0;
}

.cancel-btn {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  background: transparent;
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: #f87171;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.cancel-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.4);
}

.submit-btn.ready {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border-color: transparent;
  color: var(--bg-primary);
  box-shadow: var(--glow-emerald);
}

.submit-btn.ready:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 50px rgba(16, 185, 129, 0.4);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-arrow {
  transition: transform var(--transition-fast);
}

.submit-btn.ready:hover .btn-arrow {
  transform: translateX(4px);
}

.btn-loader {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(250, 250, 250, 0.2);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: #f87171;
}

.progress-section {
  margin-top: 20px;
}

.progress-bar {
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--emerald-500), var(--teal-500));
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-glow {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  background: var(--emerald-500);
  border-radius: 50%;
  filter: blur(10px);
  opacity: 0.5;
  transition: left 0.3s ease;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.step-num {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.1);
  border-radius: 50%;
  font-size: 11px;
  font-weight: 600;
  color: var(--slate-500);
  transition: all var(--transition-normal);
}

.step.active .step-num {
  background: var(--emerald-500);
  border-color: var(--emerald-500);
  color: var(--bg-primary);
  box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
}

.step.done .step-num {
  background: var(--teal-500);
  border-color: var(--teal-500);
  color: var(--bg-primary);
}

.step-text {
  font-size: 11px;
  color: var(--slate-500);
}

.step.active .step-text {
  color: var(--emerald-400);
}

.step.done .step-text {
  color: var(--teal-400);
}

.bento-scene {
  grid-column: span 2;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 24px;
}

.scene-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 16px;
}

.scene-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.scene-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 14px 10px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.05);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.scene-btn:hover {
  border-color: rgba(16, 185, 129, 0.2);
  background: rgba(16, 185, 129, 0.05);
}

.scene-btn.active {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.1);
}

.scene-icon {
  font-size: 18px;
}

.scene-name {
  font-size: 11px;
  font-weight: 500;
  color: var(--slate-400);
}

.scene-btn.active .scene-name {
  color: var(--emerald-400);
}

.scene-desc {
  font-size: 12px;
  color: var(--slate-500);
  margin-top: 12px;
  text-align: center;
}

.bento-features {
  grid-column: span 2;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 14px;
}

.feature-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 185, 129, 0.1);
  border-radius: var(--radius-md);
  font-size: 16px;
  color: var(--emerald-400);
}

.feature-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.feature-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--white);
}

.feature-desc {
  font-size: 12px;
  color: var(--slate-500);
}

.bento-stats {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-family: 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 24px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--emerald-400), var(--teal-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 11px;
  color: var(--slate-500);
}

.stat-divider {
  width: 1px;
  height: 30px;
  background: rgba(250, 250, 250, 0.1);
}

@media (max-width: 900px) {
  .bento-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .bento-hero {
    grid-column: span 2;
  }
  
  .bento-upload {
    grid-column: span 2;
    grid-row: auto;
  }
  
  .bento-features {
    grid-column: span 2;
  }
}

@media (max-width: 640px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }
  
  .bento-hero,
  .bento-upload,
  .bento-scene,
  .bento-features,
  .bento-stats {
    grid-column: span 1;
  }
  
  .hero-title {
    font-size: 28px;
  }
  
  .scene-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
