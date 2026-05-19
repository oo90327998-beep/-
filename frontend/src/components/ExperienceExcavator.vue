<template>
  <div class="experience-excavator">
    <div class="excavator-header">
      <div class="header-content">
        <div class="header-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <span>专为无经验大学生设计</span>
        </div>
        <h2 class="header-title">经历挖掘机</h2>
        <p class="header-desc">
          通过交互式问卷引导你回忆经历，AI 自动将大白话提炼为专业的项目经历
        </p>
      </div>
    </div>

    <div class="excavator-body">
      <div v-if="!showResult" class="question-flow">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
          <div class="progress-label">{{ currentQuestionIndex + 1 }} / {{ questions.length }}</div>
        </div>

        <div v-if="currentQuestion" class="question-card">
          <div class="question-number">问题 {{ currentQuestionIndex + 1 }}</div>
          <h3 class="question-text">{{ currentQuestion.question }}</h3>
          <p class="question-hint">{{ currentQuestion.hint }}</p>

          <div class="answer-area">
            <textarea 
              v-model="answers[currentQuestion.key]"
              class="answer-input"
              placeholder="请输入你的回答..."
              rows="4"
            ></textarea>

            <div class="voice-section">
              <button 
                class="voice-btn"
                :class="{ recording: isRecording }"
                @click="toggleVoiceInput"
              >
                <svg v-if="!isRecording" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                  <line x1="8" y1="23" x2="16" y2="23"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <circle cx="12" cy="12" r="3" fill="currentColor"/>
                </svg>
                <span>{{ isRecording ? '正在录音...' : '语音输入' }}</span>
              </button>
              <p class="voice-hint">点击开始语音输入，再次点击停止</p>
            </div>
          </div>

          <div class="nav-buttons">
            <button 
              class="nav-btn secondary"
              :disabled="currentQuestionIndex === 0"
              @click="prevQuestion"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15,18 9,12 15,6"/>
              </svg>
              <span>上一题</span>
            </button>
            <button 
              v-if="currentQuestionIndex < questions.length - 1"
              class="nav-btn primary"
              @click="nextQuestion"
            >
              <span>下一题</span>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9,18 15,12 9,6"/>
              </svg>
            </button>
            <button 
              v-else
              class="nav-btn primary generate"
              :disabled="isGenerating"
              @click="generateResult"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              <span>{{ isGenerating ? 'AI 提炼中...' : '生成专业经历' }}</span>
            </button>
          </div>
        </div>
      </div>

      <div v-else class="result-section">
        <div class="result-header">
          <div class="result-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22,4 12,14.01 9,11.01"/>
            </svg>
          </div>
          <h3 class="result-title">AI 已提炼你的专业经历</h3>
          <p class="result-desc">以下是根据你的回答生成的专业简历内容</p>
        </div>

        <div class="result-cards">
          <div v-if="result?.experiences?.length" class="result-card experiences">
            <h4 class="card-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
              </svg>
              项目/实习经历
            </h4>
            <div class="experience-list">
              <div 
                v-for="(exp, idx) in result.experiences" 
                :key="idx"
                class="experience-item"
              >
                <div class="exp-header">
                  <span class="exp-title">{{ exp.title }}</span>
                  <span class="exp-type">{{ exp.type }}</span>
                </div>
                <div class="exp-time">{{ exp.time }}</div>
                <p class="exp-desc">{{ exp.description }}</p>
                <div v-if="exp.achievements?.length" class="exp-achievements">
                  <span class="achievements-label">成果：</span>
                  <span v-for="(a, i) in exp.achievements" :key="i" class="achievement-tag">{{ a }}</span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="result?.skills?.length" class="result-card skills">
            <h4 class="card-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              技能清单
            </h4>
            <div class="tag-list">
              <span v-for="(skill, idx) in result.skills" :key="idx" class="tag">{{ skill }}</span>
            </div>
          </div>

          <div v-if="result?.certificates?.length" class="result-card certificates">
            <h4 class="card-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="8" r="7"/>
                <polyline points="8.21,13.89 7,23 12,20 17,23 15.79,13.88"/>
              </svg>
              证书荣誉
            </h4>
            <div class="tag-list">
              <span v-for="(cert, idx) in result.certificates" :key="idx" class="tag">{{ cert }}</span>
            </div>
          </div>

          <div v-if="result?.suggestions?.length" class="result-card suggestions">
            <h4 class="card-title">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9"/>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
              简历建议
            </h4>
            <ul class="suggestion-list">
              <li v-for="(s, idx) in result.suggestions" :key="idx">{{ s }}</li>
            </ul>
          </div>
        </div>

        <div class="result-actions">
          <button class="action-btn secondary" @click="resetQuestionnaire">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="1 4 1 10 7 10"/>
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
            </svg>
            <span>重新填写</span>
          </button>
          <button class="action-btn primary" @click="copyResult">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            <span>{{ copied ? '已复制' : '复制全部内容' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import {
  getExperienceQuestions,
  createExperienceSession,
  refineExperience
} from '../api/client';
import { toast } from '../composables/useToast';
import type { ExperienceQuestion, RefinedExperienceResponse } from '../types';

const questions = ref<ExperienceQuestion[]>([]);
const sessionId = ref('');
const currentQuestionIndex = ref(0);
const answers = ref<Record<string, string>>({});
const isRecording = ref(false);
const isGenerating = ref(false);
const showResult = ref(false);
const result = ref<RefinedExperienceResponse | null>(null);
const copied = ref(false);

const currentQuestion = computed(() => questions.value[currentQuestionIndex.value]);

const progress = computed(() => {
  if (questions.value.length === 0) return 0;
  return ((currentQuestionIndex.value + 1) / questions.value.length) * 100;
});

onMounted(async () => {
  try {
    const [questionsData, sessionData] = await Promise.all([
      getExperienceQuestions(),
      createExperienceSession()
    ]);
    questions.value = questionsData;
    sessionId.value = sessionData.sessionId;
  } catch (e) {
    console.error('Failed to load questions:', e);
  }
});

function prevQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--;
  }
}

function nextQuestion() {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++;
  }
}

function toggleVoiceInput() {
  if (!isRecording.value) {
    startVoiceInput();
  } else {
    stopVoiceInput();
  }
}

function startVoiceInput() {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (!SpeechRecognition) {
    toast.error('您的浏览器不支持语音识别功能，请使用 Chrome 浏览器');
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = 'zh-CN';
  recognition.continuous = true;
  recognition.interimResults = true;

  recognition.onresult = (event: any) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    const key = currentQuestion.value?.key;
    if (key) {
      answers.value[key] = (answers.value[key] || '') + transcript;
    }
  };

  recognition.onerror = (event: any) => {
    console.error('Speech recognition error:', event.error);
    isRecording.value = false;
  };

  recognition.onend = () => {
    isRecording.value = false;
  };

  (window as any).currentRecognition = recognition;
  recognition.start();
  isRecording.value = true;
}

function stopVoiceInput() {
  const recognition = (window as any).currentRecognition;
  if (recognition) {
    recognition.stop();
  }
  isRecording.value = false;
}

async function generateResult() {
  isGenerating.value = true;
  try {
    result.value = await refineExperience(sessionId.value, answers.value);
    showResult.value = true;
  } catch (e) {
    console.error('Failed to generate result:', e);
    toast.error('生成失败，请重试');
  } finally {
    isGenerating.value = false;
  }
}

function resetQuestionnaire() {
  currentQuestionIndex.value = 0;
  answers.value = {};
  showResult.value = false;
  result.value = null;
}

function copyResult() {
  if (!result.value) return;
  
  let text = '';
  
  if (result.value.experiences?.length) {
    text += '【项目/实习经历】\n';
    result.value.experiences.forEach(exp => {
      text += `${exp.title} (${exp.type})\n`;
      text += `时间：${exp.time}\n`;
      text += `${exp.description}\n`;
      if (exp.achievements?.length) {
        text += `成果：${exp.achievements.join('、')}\n`;
      }
      text += '\n';
    });
  }
  
  if (result.value.skills?.length) {
    text += `【技能】\n${result.value.skills.join('、')}\n\n`;
  }
  
  if (result.value.certificates?.length) {
    text += `【证书荣誉】\n${result.value.certificates.join('、')}\n\n`;
  }
  
  navigator.clipboard.writeText(text);
  copied.value = true;
  setTimeout(() => { copied.value = false; }, 2000);
}
</script>

<style scoped>
.experience-excavator {
  max-width: 900px;
  margin: 0 auto;
}

.excavator-header {
  margin-bottom: 32px;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  color: var(--emerald-400);
  margin-bottom: 16px;
}

.header-badge svg {
  width: 16px;
  height: 16px;
}

.header-title {
  font-size: 32px;
  font-weight: 800;
  color: var(--white);
  margin-bottom: 8px;
}

.header-desc {
  font-size: 16px;
  color: var(--slate-400);
}

.question-flow {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 32px;
}

.progress-bar {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: 20px;
  margin-bottom: 24px;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--emerald-500), var(--teal-500));
  border-radius: 20px;
  transition: width 0.3s ease;
}

.progress-label {
  position: absolute;
  right: 0;
  top: 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--slate-400);
}

.question-card {
  margin-top: 24px;
}

.question-number {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--emerald-400);
  margin-bottom: 8px;
}

.question-text {
  font-size: 22px;
  font-weight: 700;
  color: var(--white);
  margin-bottom: 8px;
}

.question-hint {
  font-size: 14px;
  color: var(--slate-400);
  margin-bottom: 24px;
}

.answer-area {
  margin-bottom: 24px;
}

.answer-input {
  width: 100%;
  padding: 16px;
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-lg);
  font-size: 15px;
  line-height: 1.6;
  color: var(--white);
  background: var(--bg-tertiary);
  resize: vertical;
  transition: all var(--transition-fast);
}

.answer-input:focus {
  outline: none;
  border-color: rgba(16, 185, 129, 0.3);
}

.voice-section {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.voice-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-lg);
  font-size: 14px;
  font-weight: 600;
  color: var(--slate-300);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.voice-btn svg {
  width: 18px;
  height: 18px;
}

.voice-btn:hover {
  background: var(--bg-elevated);
  border-color: rgba(250, 250, 250, 0.15);
}

.voice-btn.recording {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.4);
  color: #ef4444;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.voice-hint {
  font-size: 13px;
  color: var(--slate-500);
}

.nav-buttons {
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.nav-btn svg {
  width: 18px;
  height: 18px;
}

.nav-btn.secondary {
  background: var(--bg-tertiary);
  color: var(--slate-300);
  border: 1px solid rgba(250, 250, 250, 0.08);
}

.nav-btn.secondary:hover:not(:disabled) {
  background: var(--bg-elevated);
}

.nav-btn.secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-btn.primary {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  color: var(--bg-primary);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.nav-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}

.nav-btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.result-section {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 32px;
}

.result-header {
  text-align: center;
  margin-bottom: 32px;
}

.result-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 50%;
  color: var(--emerald-400);
}

.result-icon svg {
  width: 32px;
  height: 32px;
}

.result-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--white);
  margin-bottom: 8px;
}

.result-desc {
  font-size: 15px;
  color: var(--slate-400);
}

.result-cards {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 32px;
}

.result-card {
  padding: 24px;
  background: var(--bg-tertiary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  color: var(--white);
  margin-bottom: 16px;
}

.card-title svg {
  width: 20px;
  height: 20px;
  color: var(--emerald-400);
}

.experience-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.experience-item {
  padding: 16px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-lg);
}

.exp-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.exp-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--white);
}

.exp-type {
  padding: 4px 10px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--emerald-400);
}

.exp-time {
  font-size: 13px;
  color: var(--slate-500);
  margin-bottom: 8px;
}

.exp-desc {
  font-size: 14px;
  line-height: 1.7;
  color: var(--slate-300);
  margin-bottom: 12px;
}

.exp-achievements {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.achievements-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--slate-400);
}

.achievement-tag {
  padding: 4px 10px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: var(--emerald-400);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 8px 14px;
  background: var(--bg-secondary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--slate-300);
}

.suggestion-list {
  margin: 0;
  padding-left: 20px;
}

.suggestion-list li {
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--slate-300);
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.action-btn svg {
  width: 18px;
  height: 18px;
}

.action-btn.secondary {
  background: var(--bg-tertiary);
  color: var(--slate-300);
  border: 1px solid rgba(250, 250, 250, 0.08);
}

.action-btn.secondary:hover {
  background: var(--bg-elevated);
}

.action-btn.primary {
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  color: var(--bg-primary);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
}
</style>
