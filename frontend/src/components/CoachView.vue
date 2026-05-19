<template>
  <div class="coach-view">
    <div class="chat-container">
      <div class="chat-messages" ref="messagesContainer">
        <div v-if="chatMessages.length === 0" class="welcome-message">
          <div class="welcome-icon">⭐</div>
          <h3>你好！我是<strong>小优</strong>，你的专属 AI 面试教练</h3>
          <p>拥有10年以上大厂面试经验，帮你扒开简历包装，直击薄弱点</p>
          <p class="welcome-subtitle">请选择训练模式（或直接输入你的问题）</p>
          <div class="mode-menu">
            <div class="mode-item" @click="sendQuickQuestion('帮我做简历深度面诊')">
              <span class="mode-number">1</span>
              <div>
                <div class="mode-title">简历深度面诊</div>
                <div class="mode-desc">提交简历与目标岗位，全方位挑刺并预测核心考题</div>
              </div>
            </div>
            <div class="mode-item" @click="sendQuickQuestion('请对我进行岗位技术拷问')">
              <span class="mode-number">2</span>
              <div>
                <div class="mode-title">岗位技术拷问</div>
                <div class="mode-desc">针对目标岗位，进行专业场景题连环追问</div>
              </div>
            </div>
            <div class="mode-item" @click="sendQuickQuestion('请对我进行行为面试演练')">
              <span class="mode-number">3</span>
              <div>
                <div class="mode-title">行为面试 (HR面) 演练</div>
                <div class="mode-desc">实战演练抗压能力、团队协作等高频软技能陷阱题</div>
              </div>
            </div>
            <div class="mode-item" @click="sendQuickQuestion('开始全真沉浸式模拟面试')">
              <span class="mode-number">4</span>
              <div>
                <div class="mode-title">全真沉浸式模拟</div>
                <div class="mode-desc">直接开启一轮"你问我答"的实战模拟面试</div>
              </div>
            </div>
          </div>
        </div>

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

        <div v-if="chatLoading" class="message assistant loading">
          <div class="message-avatar"><span>⭐</span></div>
          <div class="message-content">
            <div class="typing-indicator"><span></span><span></span><span></span></div>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <div class="input-wrapper">
          <textarea
            ref="chatInputRef"
            v-model="chatInput"
            placeholder="输入你的面试问题..."
            @keydown.enter.exact.prevent="sendChatMessage"
            @input="autoResizeTextarea"
            rows="1"
          ></textarea>
          <button class="send-btn" :disabled="!chatInput.trim() || chatLoading" @click="sendChatMessage">
            <span>➤</span>
          </button>
        </div>
        <p class="input-hint">按 Enter 发送 · {{ resumeId ? '已加载简历，小优已了解你的背景' : '请先上传简历，让小优了解你的背景' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onUnmounted } from 'vue';
import { chatWithAssistant } from '../api/client';
import { toast } from '../composables/useToast';

const props = defineProps<{ resumeId: number | null }>();

interface ChatMessage { role: 'user' | 'assistant'; content: string; time: string; }
const chatMessages = ref<ChatMessage[]>([]);
const chatInput = ref('');
const chatLoading = ref(false);
const messagesContainer = ref<HTMLElement | null>(null);
const chatInputRef = ref<HTMLTextAreaElement | null>(null);

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatMessage(content: string): string {
  return escapeHtml(content)
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

function getCurrentTime(): string {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
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

function sendQuickQuestion(question: string) {
  chatInput.value = question;
  sendChatMessage();
}

async function sendChatMessage() {
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

  chatMessages.value.push({ role: 'user', content: message, time: getCurrentTime() });
  chatInput.value = '';
  chatLoading.value = true;
  scrollToBottom();

  try {
    const history = chatMessages.value.slice(0, -1).map(m => ({ role: m.role, content: m.content }));
    const result = await chatWithAssistant(props.resumeId!, message, history);
    chatMessages.value.push({ role: 'assistant', content: result.response, time: getCurrentTime() });
  } catch {
    toast.error('小优暂时无法回复，请稍后重试');
  } finally {
    chatLoading.value = false;
    scrollToBottom();
  }
}

onUnmounted(() => {});
</script>

<style scoped>
.coach-view {
  max-width: 800px;
  margin: 0 auto;
  height: calc(100vh - 160px);
  display: flex;
  flex-direction: column;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
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

.chat-input-area {
  padding: 16px 24px;
  border-top: var(--border-subtle);
  background: var(--bg-tertiary);
}

.input-wrapper {
  display: flex;
  gap: 8px;
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
</style>
