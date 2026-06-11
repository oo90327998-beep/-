<template>
  <div class="coach-view">
    <!-- History Sidebar -->
    <aside v-if="showHistory" class="history-sidebar">
      <div class="history-header">
        <h4>历史面试</h4>
        <button class="close-btn" @click="showHistory = false">×</button>
      </div>
      <div class="history-list">
        <div v-if="sessions.length === 0" class="history-empty">暂无历史面试记录</div>
        <div
          v-for="s in sessions"
          :key="s.sessionId"
          class="history-item"
          :class="{ active: s.sessionId === currentSessionId }"
          @click="loadSession(s.sessionId)"
        >
          <div class="history-mode">{{ modeLabel(s.mode) }}</div>
          <div class="history-meta">
            <span :class="'status-' + s.status">{{ s.status === 'active' ? '进行中' : s.status === 'completed' ? '已完成' : '已取消' }}</span>
            <span>{{ formatDate(s.createdAt) }}</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Chat Area -->
    <div class="chat-container">
      <!-- Top Bar -->
      <div class="top-bar">
        <div class="top-bar-left">
          <span class="coach-avatar">⭐</span>
          <span class="coach-name">小优教练</span>
          <span v-if="currentMode" class="mode-badge">{{ modeLabel(currentMode) }}</span>
        </div>
        <div class="top-bar-right">
          <button v-if="currentSessionId" class="new-chat-btn" @click="resetSession">
            ＋ 新对话
          </button>
          <button class="history-btn" @click="showHistory = !showHistory">
            📋 历史记录
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- Welcome / Mode Selection -->
        <div v-if="chatMessages.length === 0 && !currentSessionId" class="welcome-message">
          <div class="welcome-icon">⭐</div>
          <h3>你好！我是<strong>小优</strong>，你的专属 AI 面试教练</h3>
          <p>拥有10年以上大厂面试经验，帮你扒开简历包装，直击薄弱点</p>
          <p class="welcome-subtitle">请选择训练模式（或直接输入你的问题）</p>
          <div class="mode-menu">
            <div
              v-for="(m, idx) in modes"
              :key="m.key"
              class="mode-item"
              @click="startSession(m.key)"
            >
              <span class="mode-number">{{ idx + 1 }}</span>
              <div>
                <div class="mode-title">{{ m.label }}</div>
                <div class="mode-desc">{{ m.desc }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Session progress -->
        <div v-if="currentSessionId && currentMode" class="progress-bar-wrap">
          <div class="progress-text">{{ modeLabel(currentMode) }} · 第 {{ questionCount + 1 }} 题</div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progressPct + '%' }"></div>
          </div>
        </div>

        <!-- Messages -->
        <div v-for="(msg, idx) in chatMessages" :key="idx" class="message" :class="msg.role">
          <div class="message-avatar">
            <span v-if="msg.role === 'user'">我</span>
            <span v-else>⭐</span>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessage(msg.content)"></div>
            <span class="message-time">{{ msg.time }}</span>
          </div>
        </div>

        <!-- Streaming indicator -->
        <div v-if="chatLoading" class="message assistant loading">
          <div class="message-avatar"><span>⭐</span></div>
          <div class="message-content">
            <div class="typing-indicator"><span></span><span></span><span></span></div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="chat-input-area">
        <div class="input-wrapper">
          <button
            class="voice-btn"
            :class="{ recording: isRecording }"
            @mousedown.prevent="startRecording"
            @mouseup.prevent="stopRecording"
            @mouseleave.prevent="stopRecording"
            @touchstart.prevent="startRecording"
            @touchend.prevent="stopRecording"
            title="按住说话"
          >
            🎤
          </button>
          <textarea
            ref="chatInputRef"
            v-model="chatInput"
            :placeholder="isRecording ? '正在聆听...' : '输入你的回答...'"
            @keydown.enter.exact.prevent="sendMessage"
            @input="autoResizeTextarea"
            :disabled="isRecording"
            rows="1"
          ></textarea>
          <button class="send-btn" :disabled="!chatInput.trim() || chatLoading" @click="sendMessage">
            <span>➤</span>
          </button>
        </div>
        <p class="input-hint">
          <template v-if="!resumeId">请先上传简历，让小优了解你的背景</template>
          <template v-else-if="currentSessionId">按 Enter 发送 · 已加载简历</template>
          <template v-else>选择上方模式开始面试</template>
        </p>
      </div>
    </div>

    <!-- Report Modal -->
    <div v-if="report" class="modal-overlay" @click.self="report = null">
      <div class="report-modal">
        <div class="report-header">
          <h3>面试报告</h3>
          <button class="close-btn" @click="report = null">×</button>
        </div>
        <div class="report-body">
          <div class="report-score">
            <div class="score-circle">
              <span class="score-number">{{ report.overallScore || '-' }}</span>
              <span class="score-label">综合评分</span>
            </div>
          </div>
          <div v-if="report.strengths?.length" class="report-section">
            <h4>✅ 优势</h4>
            <ul><li v-for="s in report.strengths" :key="s">{{ s }}</li></ul>
          </div>
          <div v-if="report.weaknesses?.length" class="report-section">
            <h4>⚠️ 薄弱项</h4>
            <ul><li v-for="w in report.weaknesses" :key="w">{{ w }}</li></ul>
          </div>
          <div v-if="report.suggestions?.length" class="report-section">
            <h4>💡 建议</h4>
            <ul><li v-for="sg in report.suggestions" :key="sg">{{ sg }}</li></ul>
          </div>
          <div v-if="report.fullReport" class="report-section full-report">
            <h4>📝 详细报告</h4>
            <div class="report-text" v-html="formatMessage(report.fullReport)"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onUnmounted } from 'vue';
import { toast } from '../composables/useToast';

const API_BASE = '/api';

const props = defineProps<{ resumeId: number | null }>();

// ── State ────────────────────────────────────────────────

interface ChatMessage { role: 'user' | 'assistant'; content: string; time: string; }
interface SessionItem { sessionId: string; mode: string; status: string; createdAt: string; }

const modes = [
  { key: 'diagnose', label: '简历深度面诊', desc: '提交简历与目标岗位，全方位挑刺并预测核心考题' },
  { key: 'technical', label: '岗位技术拷问', desc: '针对目标岗位，进行专业场景题连环追问' },
  { key: 'behavioral', label: '行为面试 (HR面)', desc: '实战演练抗压能力、团队协作等高频软技能陷阱题' },
  { key: 'simulation', label: '全真沉浸式模拟', desc: '直接开启一轮"你问我答"的实战模拟面试' },
];

const chatMessages = ref<ChatMessage[]>([]);
const chatInput = ref('');
const chatLoading = ref(false);
const currentSessionId = ref<string | null>(null);
const currentMode = ref<string | null>(null);
const questionCount = ref(0);
const sessions = ref<SessionItem[]>([]);
const showHistory = ref(false);
const report = ref<any>(null);
const isRecording = ref(false);

const messagesContainer = ref<HTMLElement | null>(null);
const chatInputRef = ref<HTMLTextAreaElement | null>(null);

let recognition: any = null;

// ── Computed ─────────────────────────────────────────────

const progressPct = computed(() => {
  const maxQ: Record<string, number> = { diagnose: 1, technical: 5, behavioral: 5, simulation: 8 };
  const max = maxQ[currentMode.value || ''] || 5;
  return Math.min((questionCount.value / max) * 100, 95);
});

// ── Helpers ──────────────────────────────────────────────

function modeLabel(mode: string): string {
  const map: Record<string, string> = { diagnose: '简历面诊', technical: '技术拷问', behavioral: '行为面试', simulation: '全真模拟' };
  return map[mode] || mode;
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function getCurrentTime(): string {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text: string): string {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function formatMessage(content: string): string {
  return escapeHtml(content)
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
}

function autoResizeTextarea() {
  if (chatInputRef.value) {
    chatInputRef.value.style.height = 'auto';
    chatInputRef.value.style.height = Math.min(chatInputRef.value.scrollHeight, 100) + 'px';
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(new Error('请求超时')), 600000);
  try {
    const resp = await fetch(url, { ...options, credentials: 'include', signal: controller.signal });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`${resp.status} ${text || resp.statusText}`);
    }
    return resp.json();
  } finally {
    clearTimeout(timeout);
  }
}

// ── API Calls ────────────────────────────────────────────

async function startSession(mode: string) {
  if (!props.resumeId) {
    toast.error('请先上传简历');
    return;
  }
  chatLoading.value = true;
  try {
    const data = await fetchJson<{ sessionId: string; chunksEmbedded: number }>(
      `${API_BASE}/interview/session`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ resumeId: props.resumeId, mode }) }
    );
    currentSessionId.value = data.sessionId;
    currentMode.value = mode;
    chatMessages.value = [];
    questionCount.value = 0;

    // Send initial message based on mode
    const initMessages: Record<string, string> = {
      diagnose: '帮我做简历深度面诊',
      technical: '请对我进行岗位技术拷问',
      behavioral: '请对我进行行为面试演练',
      simulation: '开始全真沉浸式模拟面试',
    };

    await sendSSEMessage(initMessages[mode] || '开始面试');
  } catch {
    toast.error('创建面试会话失败');
  } finally {
    chatLoading.value = false;
  }
}

async function sendSSEMessage(message: string) {
  if (!currentSessionId.value) return;

  const history = chatMessages.value.map(m => ({ role: m.role, content: m.content }));

  chatLoading.value = true;
  scrollToBottom();

  try {
    const resp = await fetch(`${API_BASE}/interview/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ sessionId: currentSessionId.value, message, history }),
    });

    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`${resp.status} ${text}`);
    }

    const reader = resp.body?.getReader();
    if (!reader) throw new Error('No response stream');

    const decoder = new TextDecoder();
    let buffer = '';
    let fullContent = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') break;

          try {
            const parsed = JSON.parse(data);
            if (parsed.error) {
              throw new Error(parsed.error);
            }
            if (parsed.content) {
              fullContent += parsed.content;
              // Update last assistant message or append new one
              const last = chatMessages.value[chatMessages.value.length - 1];
              if (last && last.role === 'assistant') {
                last.content = fullContent;
              } else {
                chatMessages.value.push({ role: 'assistant', content: fullContent, time: getCurrentTime() });
              }
              scrollToBottom();
            }
          } catch {
            // Skip parse errors for partial chunks
          }
        }
      }
    }

    questionCount.value++;
    chatMessages.value[chatMessages.value.length - 1].content = fullContent;

    // After diagnosis mode or if we see report data, fetch it
    if (currentMode.value === 'diagnose') {
      await loadReport(currentSessionId.value);
    }
  } catch (err: any) {
    toast.error(err.message || '小优暂时无法回复');
  } finally {
    chatLoading.value = false;
  }
}

// ── Fast local responses for greetings ────────────────────

const FAST_RESPONSES: Record<string, string> = {
  '你好': '你好！我是小优，你的 AI 面试教练。请选择或直接告诉我你想练习的模式（面诊/技术拷问/行为面试/模拟面试）。',
  '你是谁': '我是小优，拥有10年以上大厂面试经验的 AI 面试教练。我可以帮你进行简历面诊、技术拷问、行为面试和全真模拟面试。',
  '谢谢': '不客气！有任何面试相关的问题随时问我。',
  '感谢': '不用谢，能帮到你就好。继续加油！💪',
  'hello': 'Hi！我是小优，很高兴见到你。请选择面试模式开始训练吧。',
  'hi': 'Hi！我是小优，你的 AI 面试教练。有什么我可以帮你的？',
};

function matchFastResponse(input: string): string | null {
  const trimmed = input.trim().replace(/[，。！？,!?\s]/g, '');
  // exact match
  for (const [key, resp] of Object.entries(FAST_RESPONSES)) {
    if (trimmed === key) return resp;
  }
  // short input (<5 chars) that looks like greeting → fast response
  if (trimmed.length <= 4 && /^(你好|你是谁|谢谢|感谢|hello|hi|嗨|嘿)/i.test(trimmed)) {
    return '你好！我是小优，你的 AI 面试教练。请选择训练模式，或告诉我你想练习的方向。';
  }
  return null;
}

async function sendMessage() {
  const message = chatInput.value.trim();
  if (!message || chatLoading.value) return;

  if (!props.resumeId) {
    chatMessages.value.push({
      role: 'assistant',
      content: '请先在【我的简历】页面上传简历，我才能为你提供个性化的面试辅导哦。',
      time: getCurrentTime(),
    });
    chatInput.value = '';
    scrollToBottom();
    return;
  }

  if (!currentSessionId.value) {
    toast.error('请先选择上方训练模式');
    return;
  }

  chatMessages.value.push({ role: 'user', content: message, time: getCurrentTime() });
  chatInput.value = '';
  scrollToBottom();

  // Check for fast local response
  const fastReply = matchFastResponse(message);
  if (fastReply) {
    chatMessages.value.push({ role: 'assistant', content: fastReply, time: getCurrentTime() });
    scrollToBottom();
    return;
  }

  await sendSSEMessage(message);
}

async function loadReport(sessionId: string) {
  try {
    const data = await fetchJson<any>(`${API_BASE}/interview/report/${sessionId}`);
    report.value = data;
  } catch {
    // Report not ready yet
  }
}

function resetSession() {
  currentSessionId.value = null;
  currentMode.value = null;
  chatMessages.value = [];
  questionCount.value = 0;
  report.value = null;
  chatInput.value = '';
}

async function loadSessions() {
  try {
    sessions.value = await fetchJson<SessionItem[]>(`${API_BASE}/interview/sessions`);
  } catch {
    // Silently fail
  }
}

async function loadSession(sessionId: string) {
  currentSessionId.value = sessionId;
  try {
    const msgs = await fetchJson<any[]>(`${API_BASE}/interview/messages/${sessionId}`);
    chatMessages.value = msgs.map((m: any) => ({
      role: m.role,
      content: m.content,
      time: formatDate(m.createdAt),
    }));
    questionCount.value = msgs.filter((m: any) => m.role === 'assistant').length;
    await loadReport(sessionId);
  } catch {
    toast.error('加载会话失败');
  }
  showHistory.value = false;
}

// ── Voice Input ──────────────────────────────────────────

function initSpeechRecognition() {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  recognition = new SpeechRecognition();
  recognition.lang = 'zh-CN';
  recognition.interimResults = true;
  recognition.continuous = true;

  recognition.onresult = (event: any) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      transcript += event.results[i][0].transcript;
    }
    chatInput.value = transcript;
  };

  recognition.onerror = () => {
    isRecording.value = false;
    toast.error('语音识别失败，请手动输入');
  };

  recognition.onend = () => {
    isRecording.value = false;
  };
}

function startRecording() {
  if (!recognition) initSpeechRecognition();
  if (!recognition || isRecording.value) return;
  try {
    recognition.start();
    isRecording.value = true;
  } catch {
    // Already started
  }
}

function stopRecording() {
  if (!recognition || !isRecording.value) return;
  try {
    recognition.stop();
  } catch {
    // Already stopped
  }
  isRecording.value = false;
}

// ── Lifecycle ────────────────────────────────────────────

watch(() => props.resumeId, () => {
  if (props.resumeId) loadSessions();
}, { immediate: true });

onUnmounted(() => {
  if (recognition) {
    try { recognition.stop(); } catch { /* ignore */ }
  }
});
</script>

<style scoped>
.coach-view {
  display: flex;
  height: calc(100vh - 160px);
  max-width: 960px;
  margin: 0 auto;
  gap: 0;
}

/* ── History Sidebar ─────────────────────────────────── */

.history-sidebar {
  width: 260px;
  flex-shrink: 0;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-right: none;
  border-radius: var(--radius-xl) 0 0 var(--radius-xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: var(--border-subtle);
}

.history-header h4 {
  font-size: 14px;
  color: var(--white);
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: var(--slate-400);
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover { color: var(--white); }

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.history-empty {
  text-align: center;
  color: var(--slate-500);
  font-size: 13px;
  padding: 24px 0;
}

.history-item {
  padding: 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 4px;
}

.history-item:hover {
  background: var(--bg-tertiary);
}

.history-item.active {
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.history-mode {
  font-size: 13px;
  color: var(--white);
  font-weight: 500;
  margin-bottom: 4px;
}

.history-meta {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: var(--slate-500);
}

.status-active { color: var(--amber-400); }
.status-completed { color: var(--emerald-400); }
.status-cancelled { color: var(--slate-500); }

/* ── Chat Container ──────────────────────────────────── */

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 20px;
  border-bottom: var(--border-subtle);
  background: var(--bg-tertiary);
}

.top-bar-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.coach-avatar {
  font-size: 20px;
}

.coach-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--white);
}

.mode-badge {
  font-size: 11px;
  padding: 2px 10px;
  background: rgba(16, 185, 129, 0.1);
  color: var(--emerald-400);
  border-radius: 999px;
}

.history-btn {
  font-size: 12px;
  padding: 6px 14px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--slate-300);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.history-btn:hover {
  border-color: rgba(16, 185, 129, 0.3);
}

.top-bar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.new-chat-btn {
  font-size: 12px;
  padding: 6px 14px;
  background: var(--emerald-500);
  border: none;
  border-radius: var(--radius-md);
  color: white;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.new-chat-btn:hover {
  background: var(--emerald-400);
}

/* ── Progress Bar ────────────────────────────────────── */

.progress-bar-wrap {
  padding: 12px 24px 0;
}

.progress-text {
  font-size: 11px;
  color: var(--slate-400);
  margin-bottom: 6px;
}

.progress-track {
  height: 4px;
  background: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--emerald-500), var(--teal-400));
  border-radius: 2px;
  transition: width 0.5s ease;
}

/* ── Messages ─────────────────────────────────────────── */

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.welcome-message {
  text-align: center;
  padding: 30px 20px;
}

.welcome-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.welcome-message h3 {
  font-size: 18px;
  color: var(--white);
  margin-bottom: 8px;
}

.welcome-message p {
  font-size: 14px;
  color: var(--slate-400);
  margin-bottom: 4px;
}

.welcome-subtitle {
  color: var(--slate-500) !important;
  margin-bottom: 24px !important;
}

.mode-menu {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  max-width: 560px;
  margin: 0 auto;
  text-align: left;
}

.mode-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.05);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.mode-item:hover {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.05);
}

.mode-number {
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 50%;
  font-size: 13px;
  font-weight: 600;
  color: var(--emerald-400);
  flex-shrink: 0;
}

.mode-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 2px;
}

.mode-desc {
  font-size: 11px;
  color: var(--slate-500);
  line-height: 1.4;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  color: var(--slate-400);
  flex-shrink: 0;
}

.message.assistant .message-avatar {
  background: rgba(16, 185, 129, 0.1);
  color: var(--emerald-400);
}

.message-content {
  flex: 1;
  min-width: 0;
}

.message-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--slate-300);
}

.message-time {
  font-size: 10px;
  color: var(--slate-600);
  margin-top: 4px;
  display: block;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: var(--slate-500);
  border-radius: 50%;
  animation: bounce 1.2s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-6px); }
}

/* ── Input Area ────────────────────────────────────────── */

.chat-input-area {
  padding: 16px 24px;
  border-top: var(--border-subtle);
  background: var(--bg-tertiary);
}

.input-wrapper {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.voice-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-md);
  font-size: 18px;
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.voice-btn:hover {
  border-color: rgba(16, 185, 129, 0.3);
}

.voice-btn.recording {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.4);
  animation: pulse-rec 1.5s infinite;
}

@keyframes pulse-rec {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.3); }
  50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
}

.input-wrapper textarea {
  flex: 1;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border: 1px solid rgba(250, 250, 250, 0.08);
  border-radius: var(--radius-md);
  color: var(--white);
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: border-color var(--transition-fast);
}

.input-wrapper textarea:focus {
  border-color: rgba(16, 185, 129, 0.3);
}

.input-wrapper textarea:disabled {
  opacity: 0.6;
}

.send-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border: none;
  border-radius: var(--radius-md);
  color: var(--bg-primary);
  font-size: 16px;
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.input-hint {
  font-size: 11px;
  color: var(--slate-500);
  margin-top: 8px;
  text-align: center;
}

/* ── Report Modal ──────────────────────────────────────── */

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.report-modal {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  max-width: 560px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.report-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px 0;
}

.report-header h3 {
  font-size: 18px;
  color: var(--white);
  margin: 0;
}

.report-body {
  padding: 24px;
}

.report-score {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.1);
  border: 3px solid var(--emerald-500);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.score-number {
  font-size: 28px;
  font-weight: 700;
  color: var(--emerald-400);
}

.score-label {
  font-size: 10px;
  color: var(--slate-400);
}

.report-section {
  margin-bottom: 20px;
}

.report-section h4 {
  font-size: 14px;
  color: var(--white);
  margin-bottom: 8px;
}

.report-section ul {
  margin: 0;
  padding-left: 18px;
}

.report-section li {
  font-size: 13px;
  color: var(--slate-300);
  line-height: 1.7;
}

.full-report .report-text {
  font-size: 13px;
  color: var(--slate-300);
  line-height: 1.7;
}
</style>
