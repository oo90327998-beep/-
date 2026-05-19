<template>
  <div class="toolbox-view">
    <div class="toolbox-header">
      <h2 class="toolbox-title">求职工具箱</h2>
      <p class="toolbox-subtitle">AI 驱动的全方位求职辅助，助你斩获心仪 Offer</p>
    </div>

    <div class="tool-cards">
      <div
        v-for="tool in tools"
        :key="tool.id"
        class="tool-card"
        :class="{ active: activeTool === tool.id }"
        @click="selectTool(tool.id)"
      >
        <span class="tool-icon">{{ tool.icon }}</span>
        <div class="tool-info">
          <span class="tool-name">{{ tool.name }}</span>
          <span class="tool-desc">{{ tool.desc }}</span>
        </div>
        <span class="tool-arrow">→</span>
      </div>
    </div>

    <div v-if="activeTool" class="tool-panel">
      <div class="panel-header">
        <h3>{{ activeToolMeta?.name }}</h3>
        <button class="panel-close" @click="activeTool = null">✕</button>
      </div>

      <!-- ATS 检测 -->
      <div v-if="activeTool === 'ats'" class="panel-body">
        <div class="tool-input-row">
          <div class="tool-input-group">
            <label>目标岗位（可选）</label>
            <input v-model="getToolState('ats').targetJob" type="text" placeholder="例如：前端开发工程师" />
          </div>
          <button
            class="generate-btn"
            :disabled="getToolState('ats').loading"
            @click="runATSCheck"
          >
            <span v-if="getToolState('ats').loading" class="btn-spinner"></span>
            <span>{{ getToolState('ats').loading ? '检测中...' : '开始检测' }}</span>
          </button>
        </div>

        <div v-if="atsReport" class="ats-result">
          <div class="ats-score" :class="scoreClass">
            <div class="score-circle">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(250,250,250,0.05)" stroke-width="8"/>
                <circle
                  cx="50" cy="50" r="45"
                  fill="none"
                  :stroke="scoreColor"
                  stroke-width="8"
                  stroke-linecap="round"
                  :stroke-dasharray="circumference"
                  :stroke-dashoffset="scoreOffset"
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div class="score-inner">
                <div class="score-value">{{ atsReport.score }}</div>
                <div class="score-max">/100</div>
              </div>
            </div>
            <div class="score-label">ATS 友好度</div>
            <div class="score-status">{{ scoreStatus }}</div>
          </div>

          <div class="ats-details">
            <div v-if="atsReport.issues?.length" class="detail-card">
              <h4>⚠️ 检测到的问题</h4>
              <ul>
                <li v-for="(issue, idx) in atsReport.issues" :key="idx">{{ issue }}</li>
              </ul>
            </div>
            <div v-if="atsReport.suggestions?.length" class="detail-card">
              <h4>💡 优化建议</h4>
              <ul>
                <li v-for="(s, idx) in atsReport.suggestions" :key="idx">{{ s }}</li>
              </ul>
            </div>
          </div>
        </div>

        <div v-else-if="!getToolState('ats').loading" class="panel-empty">
          <p>点击"开始检测"获取 ATS 友好度评分</p>
        </div>
      </div>

      <!-- 求职信 -->
      <div v-if="activeTool === 'cover-letter'" class="panel-body">
        <div class="tool-input-row">
          <div class="tool-input-group">
            <label>目标岗位</label>
            <input v-model="getToolState('cover-letter').targetJob" type="text" placeholder="例如：前端开发工程师" />
          </div>
          <div class="tool-input-group">
            <label>目标公司</label>
            <input v-model="getToolState('cover-letter').company" type="text" placeholder="例如：字节跳动" />
          </div>
          <button class="generate-btn" :disabled="getToolState('cover-letter').loading" @click="handleGenerateCoverLetter">
            <span v-if="getToolState('cover-letter').loading" class="btn-spinner"></span>
            <span>{{ getToolState('cover-letter').loading ? '生成中...' : '开始生成' }}</span>
          </button>
        </div>
        <div v-if="getToolState('cover-letter').result" class="result-cards">
          <div class="result-card">
            <div class="result-card-header">
              <h4>正式求职信</h4>
              <button class="copy-btn" @click="copyText(getToolState('cover-letter').result.cover_letter)">复制</button>
            </div>
            <div class="result-text">{{ getToolState('cover-letter').result.cover_letter }}</div>
          </div>
          <div class="result-card">
            <div class="result-card-header">
              <h4>HR 邮件正文</h4>
              <button class="copy-btn" @click="copyText(getToolState('cover-letter').result.email_body)">复制</button>
            </div>
            <div class="result-text">{{ getToolState('cover-letter').result.email_body }}</div>
          </div>
          <div class="result-card">
            <div class="result-card-header">
              <h4>简短自荐话术</h4>
              <button class="copy-btn" @click="copyText(getToolState('cover-letter').result.quick_pitch)">复制</button>
            </div>
            <div class="result-text">{{ getToolState('cover-letter').result.quick_pitch }}</div>
          </div>
        </div>
      </div>

      <!-- 职位推荐 -->
      <div v-if="activeTool === 'recommend'" class="panel-body">
        <div class="tool-input-row">
          <div class="tool-input-group">
            <label>目标岗位</label>
            <input v-model="getToolState('recommend').targetJob" type="text" placeholder="例如：前端开发工程师" />
          </div>
          <button class="generate-btn" :disabled="getToolState('recommend').loading" @click="handleGenerateRecommend">
            <span v-if="getToolState('recommend').loading" class="btn-spinner"></span>
            <span>{{ getToolState('recommend').loading ? '生成中...' : '开始生成' }}</span>
          </button>
        </div>
        <div v-if="getToolState('recommend').result" class="result-cards">
          <div v-if="getToolState('recommend').result.profile" class="result-card">
            <h4>能力画像</h4>
            <div class="tag-list">
              <span v-for="s in getToolState('recommend').result.profile.strengths" :key="s" class="tag strength">{{ s }}</span>
            </div>
          </div>
          <div v-if="getToolState('recommend').result.recommended_jobs?.length" class="result-card">
            <h4>推荐岗位</h4>
            <div v-for="(j, i) in getToolState('recommend').result.recommended_jobs" :key="i" class="job-item">
              <div class="job-header">
                <span class="job-title">{{ j.title }}</span>
                <span class="match-score">{{ j.match_score }}% 匹配</span>
              </div>
              <p class="job-reason">{{ j.reason }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 职涯规划 -->
      <div v-if="activeTool === 'planning'" class="panel-body">
        <div class="tool-input-row">
          <div class="tool-input-group">
            <label>目标岗位</label>
            <input v-model="getToolState('planning').targetJob" type="text" placeholder="例如：前端开发工程师" />
          </div>
          <button class="generate-btn" :disabled="getToolState('planning').loading" @click="handleGeneratePlanning">
            <span v-if="getToolState('planning').loading" class="btn-spinner"></span>
            <span>{{ getToolState('planning').loading ? '生成中...' : '开始生成' }}</span>
          </button>
        </div>
        <div v-if="getToolState('planning').result" class="result-cards">
          <div v-if="getToolState('planning').result.current_assessment" class="result-card">
            <h4>当前能力评估</h4>
            <p class="assessment-level">{{ getToolState('planning').result.current_assessment.overall_level }}</p>
            <div class="tag-list">
              <span v-for="c in getToolState('planning').result.current_assessment.core_competencies" :key="c" class="tag strength">{{ c }}</span>
            </div>
          </div>
          <div v-if="getToolState('planning').result.career_directions?.length" class="result-card">
            <h4>职业方向建议</h4>
            <div v-for="(d, i) in getToolState('planning').result.career_directions" :key="i" class="direction-item">
              <div class="direction-header">
                <span class="direction-name">{{ d.direction }}</span>
                <span class="fit-score">{{ d.fit_score }}% 适合</span>
              </div>
              <p class="transition-plan">{{ d.transition_plan }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 经历挖掘机 -->
      <div v-if="activeTool === 'excavator'" class="panel-body">
        <ExperienceExcavator />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  checkATS,
  getATSReport,
  generateCoverLetter,
  careerRecommend,
  careerPlanning,
} from '../api/client';
import { toast } from '../composables/useToast';
import type { ATSReport } from '../types';
import ExperienceExcavator from './ExperienceExcavator.vue';

const props = defineProps<{
  resumeId: number | null;
}>();

const tools = [
  { id: 'ats', icon: '📊', name: 'ATS 检测', desc: '检查简历能否通过机器初筛' },
  { id: 'cover-letter', icon: '✉️', name: '求职信', desc: 'AI 生成正式求职信与自荐话术' },
  { id: 'recommend', icon: '🎯', name: '职位推荐', desc: '根据能力画像推荐匹配岗位' },
  { id: 'planning', icon: '🧭', name: '职涯规划', desc: '评估当前能力，规划职业方向' },
  { id: 'excavator', icon: '⛏️', name: '经历挖掘', desc: '引导回忆经历，提炼专业简历' },
];

const activeTool = ref<string | null>(null);

// Per-tool isolated state
interface ToolState {
  targetJob: string;
  company: string;
  loading: boolean;
  result: any;
}
const toolStates = ref<Record<string, ToolState>>({});
function getToolState(toolId: string): ToolState {
  if (!toolStates.value[toolId]) {
    toolStates.value[toolId] = { targetJob: '', company: '', loading: false, result: null };
  }
  return toolStates.value[toolId];
}

const atsReport = ref<ATSReport | null>(null);

const circumference = 2 * Math.PI * 45;

const activeToolMeta = computed(() => tools.find(t => t.id === activeTool.value));

const scoreClass = computed(() => {
  if (!atsReport.value) return '';
  const s = atsReport.value.score;
  if (s >= 90) return 'excellent';
  if (s >= 70) return 'good';
  if (s >= 50) return 'fair';
  return 'poor';
});

const scoreColor = computed(() => {
  if (!atsReport.value) return '#94a3b8';
  const s = atsReport.value.score;
  if (s >= 90) return '#22c55e';
  if (s >= 70) return '#3b82f6';
  if (s >= 50) return '#f59e0b';
  return '#ef4444';
});

const scoreOffset = computed(() => {
  if (!atsReport.value) return circumference;
  return circumference - (atsReport.value.score / 100) * circumference;
});

const scoreStatus = computed(() => {
  if (!atsReport.value) return '';
  const s = atsReport.value.score;
  if (s >= 90) return '优秀';
  if (s >= 70) return '良好';
  if (s >= 50) return '一般';
  return '需改进';
});

function selectTool(toolId: string) {
  if (!props.resumeId && toolId !== 'excavator') {
    toast.info('请先上传简历');
    return;
  }
  activeTool.value = activeTool.value === toolId ? null : toolId;
}

onMounted(async () => {
  if (props.resumeId) {
    try {
      atsReport.value = await getATSReport(props.resumeId);
    } catch { /* no report yet */ }
  }
});

async function runATSCheck() {
  if (!props.resumeId) return;
  const state = getToolState('ats');
  state.loading = true;
  try {
    atsReport.value = await checkATS(props.resumeId);
  } catch {
    toast.error('ATS 检测失败，请重试');
  } finally {
    state.loading = false;
  }
}

async function handleGenerateCoverLetter() {
  if (!props.resumeId) return;
  const state = getToolState('cover-letter');
  state.loading = true;
  state.result = null;
  try {
    state.result = await generateCoverLetter(props.resumeId, state.targetJob, state.company);
  } catch (e: any) {
    toast.error(e?.message || '生成失败');
  } finally {
    state.loading = false;
  }
}

async function handleGenerateRecommend() {
  if (!props.resumeId) return;
  const state = getToolState('recommend');
  state.loading = true;
  state.result = null;
  try {
    state.result = await careerRecommend(props.resumeId, state.targetJob);
  } catch (e: any) {
    toast.error(e?.message || '生成失败');
  } finally {
    state.loading = false;
  }
}

async function handleGeneratePlanning() {
  if (!props.resumeId) return;
  const state = getToolState('planning');
  state.loading = true;
  state.result = null;
  try {
    state.result = await careerPlanning(props.resumeId, state.targetJob);
  } catch (e: any) {
    toast.error(e?.message || '生成失败');
  } finally {
    state.loading = false;
  }
}

function copyText(text: string) {
  navigator.clipboard.writeText(text).then(() => {
    toast.success('已复制到剪贴板');
  }).catch(() => {
    const ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    toast.success('已复制到剪贴板');
  });
}
</script>

<style scoped>
.toolbox-view {
  max-width: 900px;
  margin: 0 auto;
  animation: fade-up 0.4s ease;
}

@keyframes fade-up {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: translateY(0); }
}

.toolbox-header {
  text-align: center;
  margin-bottom: 32px;
}

.toolbox-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--white);
  margin-bottom: 8px;
}

.toolbox-subtitle {
  font-size: 15px;
  color: var(--slate-400);
}

.tool-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.tool-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px 20px;
  background: var(--bg-secondary);
  border: 1px solid rgba(250, 250, 250, 0.05);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tool-card:hover {
  border-color: rgba(16, 185, 129, 0.25);
  background: rgba(16, 185, 129, 0.05);
  transform: translateY(-1px);
}

.tool-card.active {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.08);
}

.tool-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.tool-info {
  flex: 1;
  min-width: 0;
}

.tool-name {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 2px;
}

.tool-desc {
  font-size: 12px;
  color: var(--slate-500);
}

.tool-arrow {
  color: var(--slate-600);
  transition: transform var(--transition-fast);
}

.tool-card:hover .tool-arrow {
  transform: translateX(3px);
  color: var(--emerald-400);
}

/* Panel */
.tool-panel {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
  animation: fade-in 0.25s ease;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  border-bottom: var(--border-subtle);
  background: var(--bg-tertiary);
}

.panel-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--white);
}

.panel-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-sm);
  color: var(--slate-400);
  cursor: pointer;
  font-size: 14px;
  transition: all var(--transition-fast);
}

.panel-close:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #f87171;
}

.panel-body {
  padding: 24px;
}

.panel-empty {
  text-align: center;
  padding: 40px;
  color: var(--slate-500);
  font-size: 14px;
}

/* Input row */
.tool-input-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.tool-input-group {
  flex: 1;
  min-width: 160px;
}

.tool-input-group label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--slate-400);
  margin-bottom: 6px;
}

.tool-input-group input {
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

.tool-input-group input::placeholder {
  color: var(--slate-500);
}

.tool-input-group input:focus {
  border-color: rgba(16, 185, 129, 0.3);
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 11px 22px;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border: none;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
  color: var(--bg-primary);
  cursor: pointer;
  white-space: nowrap;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(9, 9, 11, 0.3);
  border-top-color: var(--bg-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ATS Result */
.ats-result {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 32px;
}

.ats-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-lg);
}

.score-circle {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 12px;
}

.score-circle svg {
  width: 100%;
  height: 100%;
}

.score-inner {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-value {
  font-size: 36px;
  font-weight: 800;
  color: var(--white);
  line-height: 1;
}

.score-max {
  font-size: 12px;
  color: var(--slate-500);
}

.score-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--slate-400);
  margin-bottom: 4px;
}

.score-status {
  font-size: 14px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 12px;
}

.ats-score.excellent .score-status {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.ats-score.good .score-status {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.ats-score.fair .score-status {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.ats-score.poor .score-status {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.ats-details {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-card {
  padding: 18px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.detail-card h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 10px;
}

.detail-card ul {
  margin: 0;
  padding-left: 18px;
}

.detail-card li {
  margin-bottom: 6px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--slate-300);
}

/* Result cards */
.result-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-card {
  padding: 20px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
}

.result-card h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(250, 250, 250, 0.06);
}

.result-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(250, 250, 250, 0.06);
}

.result-card-header h4 {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.result-text {
  font-size: 13px;
  line-height: 1.8;
  color: var(--slate-300);
  white-space: pre-wrap;
}

.copy-btn {
  padding: 6px 14px;
  background: var(--bg-secondary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  color: var(--slate-400);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.copy-btn:hover {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: var(--emerald-400);
}

/* Tags */
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag.strength {
  padding: 6px 14px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 20px;
  font-size: 13px;
  color: var(--emerald-400);
}

/* Job items */
.job-item {
  padding: 14px;
  background: var(--bg-secondary);
  border: 1px solid rgba(250, 250, 250, 0.05);
  border-radius: var(--radius-md);
  margin-bottom: 10px;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.job-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--white);
}

.match-score {
  padding: 3px 10px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  color: var(--emerald-400);
}

.job-reason {
  font-size: 13px;
  color: var(--slate-400);
  line-height: 1.5;
}

/* Assessment */
.assessment-level {
  font-size: 15px;
  font-weight: 600;
  color: var(--emerald-400);
  margin-bottom: 12px;
}

/* Direction items */
.direction-item {
  padding: 14px;
  background: var(--bg-secondary);
  border: 1px solid rgba(250, 250, 250, 0.05);
  border-radius: var(--radius-md);
  margin-bottom: 10px;
}

.direction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.direction-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--white);
}

.fit-score {
  padding: 3px 10px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--emerald-400);
}

.transition-plan {
  font-size: 13px;
  color: var(--slate-400);
  line-height: 1.5;
}

@media (max-width: 768px) {
  .tool-cards {
    grid-template-columns: 1fr;
  }

  .ats-result {
    grid-template-columns: 1fr;
  }

  .tool-input-row {
    flex-direction: column;
  }

  .tool-input-group {
    min-width: 100%;
  }
}
</style>
