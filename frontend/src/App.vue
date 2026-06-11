<template>
  <!-- Auth loading -->
  <div v-if="authChecking" class="auth-screen">
    <div class="auth-screen-content">
      <div class="auth-spinner"></div>
      <p>正在验证身份...</p>
    </div>
  </div>

  <!-- Require login -->
  <div v-else-if="!isLoggedIn" class="auth-screen">
    <div class="auth-screen-card">
      <div class="auth-screen-brand">
        <span class="brand-emoji">🪐</span>
        <h1>简历星球</h1>
        <p>AI 智能简历优化助手</p>
      </div>
      <LoginView :required="true" @login-success="handleLoginSuccess" />
    </div>
  </div>

  <!-- Full app (authenticated) -->
  <div v-else class="app-shell">
    <div class="bg-grid"></div>
    <div class="bg-glow"></div>
    <div class="bg-noise"></div>
    <canvas ref="particleCanvas" class="particle-canvas"></canvas>

    <nav class="navbar">
      <div class="nav-brand">
        <div class="brand-logo">
          <div class="logo-ring"></div>
          <span class="logo-text">🪐</span>
        </div>
        <div class="brand-info">
          <span class="brand-name">简历星球</span>
          <span class="brand-tag">AI 驱动</span>
        </div>
      </div>

      <div class="nav-links">
        <button
          v-for="tab in navTabs"
          :key="tab.id"
          class="nav-link"
          :class="{ active: currentView === tab.id }"
          @click="currentView = tab.id"
        >
          <span class="link-icon">{{ tab.icon }}</span>
          <span class="link-text">{{ tab.label }}</span>
        </button>
      </div>

      <div class="nav-user">
        <div v-if="isLoggedIn && currentUser" class="user-info">
          <div class="user-avatar">
            {{ currentUser.nickname?.charAt(0) || currentUser.username.charAt(0) }}
          </div>
          <span class="user-name">{{ currentUser.nickname || currentUser.username }}</span>
          <button class="logout-btn" @click="handleLogout" title="退出登录">
            <span>🚪</span>
          </button>
        </div>
        <button v-else class="login-btn" @click="showLoginModal = true">
          <span class="btn-icon">🔐</span>
          <span class="btn-text">登录</span>
        </button>
      </div>
    </nav>

    <main class="main-content">
      <!-- 我的简历 tab -->
      <template v-if="currentView === 'resumes'">
        <div v-if="!showDiffView" class="resumes-layout">
          <UploadView
            @result="handleResult"
            :key="uploadKey"
          />
          <ResumeList
            :active-id="resumeId"
            @select="handleLoadResume"
            @refresh="handleRefreshList"
          />
        </div>
        <DiffView
          v-else
          :sections="sections"
          :suggestions="suggestions"
          :resume-id="resumeId"
          :selected-template="selectedTemplate"
          :images="resumeImages"
          @style-changed="handleStyleChange"
          @sections-updated="handleSectionsUpdate"
          @back="handleBackToUpload"
          @open-templates="showTemplateModal = true"
        />
      </template>

      <!-- 小优教练 tab -->
      <CoachView
        v-else-if="currentView === 'coach'"
        :resume-id="resumeId"
      />

      <!-- 工具箱 tab -->
      <ToolboxView
        v-else-if="currentView === 'toolbox'"
        :resume-id="resumeId"
      />

      <!-- Fallback empty state -->
      <div v-else class="empty-state">
        <div class="empty-grid">
          <div class="empty-card main">
            <div class="empty-icon">
              <div class="icon-ring"></div>
              <span>📄</span>
            </div>
            <h3>上传您的简历</h3>
            <p>上传 PDF 解锁 AI 驱动的优化</p>
            <button class="btn-glow" @click="currentView = 'resumes'">
              <span>开始使用</span>
              <span class="btn-arrow">→</span>
            </button>
          </div>
          <div class="empty-card stat">
            <span class="stat-value">6</span>
            <span class="stat-label">优化模式</span>
          </div>
          <div class="empty-card stat">
            <span class="stat-value">5</span>
            <span class="stat-label">职业工具</span>
          </div>
          <div class="empty-card feature">
            <span class="feature-icon">✨</span>
            <span>AI 驱动分析</span>
          </div>
        </div>
      </div>
    </main>

    <footer class="app-footer">
      <span class="footer-brand">简历星球</span>
      <span class="footer-divider">·</span>
      <span>AI 精心打造</span>
    </footer>

    <div v-if="showLoginModal" class="modal-overlay" @click.self="showLoginModal = false">
      <LoginView @login-success="handleLoginSuccess" />
    </div>

    <ToastContainer />

    <div v-if="appError" class="app-error-overlay">
      <div class="app-error-card">
        <h3>应用出现错误</h3>
        <p>{{ appError }}</p>
        <button @click="appError = null">关闭</button>
        <button class="reload-btn" @click="window.location.reload()">刷新页面</button>
      </div>
    </div>

    <div v-if="showTemplateModal" class="modal-overlay template-modal-overlay" @click.self="showTemplateModal = false">
      <div class="template-modal-wrapper">
        <TemplateLibrary @select-template="handleSelectTemplate" />
        <button class="template-modal-close" @click="showTemplateModal = false" title="关闭">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, onErrorCaptured } from 'vue';
import UploadView from './components/UploadView.vue';
import DiffView from './components/DiffView.vue';
import TemplateLibrary from './components/TemplateLibrary.vue';
import CoachView from './components/CoachView.vue';
import ToolboxView from './components/ToolboxView.vue';
import ResumeList from './components/ResumeList.vue';
import LoginView from './components/LoginView.vue';
import ToastContainer from './components/ToastContainer.vue';
import { getResume } from './api/client';
import { toast } from './composables/useToast';
import type { Section, SuggestionsResponse } from './types';

interface User {
  id: number;
  username: string;
  email: string;
  nickname?: string;
  avatar?: string;
}

const currentView = ref<'resumes' | 'coach' | 'toolbox'>('resumes');
const showDiffView = ref(false);
const showTemplateModal = ref(false);
const resumeId = ref<number | null>(null);
const sections = ref<Section[]>([]);
const suggestions = ref<SuggestionsResponse | null>(null);
const uploadKey = ref(0);
const selectedTemplate = ref<string>('minimal-clean');
const resumeImages = ref<string[]>([]);
const particleCanvas = ref<HTMLCanvasElement | null>(null);
let animationId: number | null = null;

const authChecking = ref(true);
const showLoginModal = ref(false);
const isLoggedIn = ref(false);
const currentUser = ref<User | null>(null);

const navTabs = [
  { id: 'resumes', icon: '📄', label: '我的简历' },
  { id: 'coach', icon: '⭐', label: '小优教练' },
  { id: 'toolbox', icon: '🧰', label: '工具箱' },
];

function handleResult(data: { resumeId: number; sections: Section[]; suggestions: SuggestionsResponse | null; styleType: string; targetJob: string; images?: string[] }) {
  resumeId.value = data.resumeId;
  sections.value = data.sections;
  suggestions.value = data.suggestions;
  resumeImages.value = data.images || [];
  currentView.value = 'resumes';
  showDiffView.value = true;
}

function safeParse<T>(val: any, fallback: T): T {
  if (val == null) return fallback;
  if (typeof val === 'string') {
    try { return JSON.parse(val); } catch { return fallback; }
  }
  return val;
}

async function handleLoadResume(resumeId: number) {
  try {
    const data = await getResume(resumeId);
    resumeId.value = resumeId;
    sections.value = safeParse(data.sections, []);
    suggestions.value = safeParse(data.suggestions, null);
    resumeImages.value = safeParse(data.images, []);
    currentView.value = 'resumes';
    showDiffView.value = true;
  } catch {
    toast.error('加载简历失败');
  }
}

function handleBackToUpload() {
  showDiffView.value = false;
}

function handleRefreshList() {
  uploadKey.value++;
}

function handleStyleChange(newSections: Section[]) {
  sections.value = newSections;
}

function handleSectionsUpdate(updatedSections: Section[]) {
  sections.value = updatedSections;
}

function handleSelectTemplate(templateId: string) {
  selectedTemplate.value = templateId;
  showTemplateModal.value = false;
  if (sections.value.length === 0) {
    toast.info('请先上传简历后再使用模板');
  }
}

async function checkAuthStatus() {
  try {
    const response = await fetch('/api/auth/check', {
      credentials: 'include'
    });
    const data = await response.json();

    if (data.authenticated && data.user) {
      isLoggedIn.value = true;
      currentUser.value = data.user;
    } else {
      isLoggedIn.value = false;
      currentUser.value = null;
    }
  } catch (error) {
    console.error('Check auth error:', error);
    isLoggedIn.value = false;
    currentUser.value = null;
  } finally {
    authChecking.value = false;
  }
}

function handleLoginSuccess(user: User) {
  isLoggedIn.value = true;
  currentUser.value = user;
  showLoginModal.value = false;
}

async function handleLogout() {
  try {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    });
  } catch (error) {
    console.error('Logout error:', error);
  }
  
  isLoggedIn.value = false;
  currentUser.value = null;
}

const appError = ref<string | null>(null);

onErrorCaptured((err) => {
  console.error('Global error captured:', err);
  appError.value = err instanceof Error ? err.message : String(err);
  return false;
});

onMounted(() => {
  initParticles();
  checkAuthStatus();
});

onUnmounted(() => {
  if (animationId) {
    cancelAnimationFrame(animationId);
  }
  window.removeEventListener('resize', handleResize);
});

let handleResize: (() => void) | null = null;

function initParticles() {
  const canvas = particleCanvas.value;
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  handleResize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  };
  handleResize();
  window.addEventListener('resize', handleResize);
  
  const particles: { x: number; y: number; vx: number; vy: number; size: number; alpha: number }[] = [];
  const particleCount = 50;
  
  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      size: Math.random() * 2 + 1,
      alpha: Math.random() * 0.5 + 0.1,
    });
  }
  
  function animate() {
    if (!ctx || !canvas) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    particles.forEach((p, i) => {
      p.x += p.vx;
      p.y += p.vy;
      
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(16, 185, 129, ${p.alpha})`;
      ctx.fill();
      
      particles.slice(i + 1).forEach((p2) => {
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < 150) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(16, 185, 129, ${0.1 * (1 - dist / 150)})`;
          ctx.stroke();
        }
      });
    });
    
    animationId = requestAnimationFrame(animate);
  }
  
  animate();
}
</script>

<style>
/* 使用系统字体，避免依赖外部网络 */
/* @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap'); */

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(16, 185, 129, 0.3);
  border-radius: 4px;
  transition: background 0.2s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(16, 185, 129, 0.5);
}

::-webkit-scrollbar-corner {
  background: transparent;
}

/* Firefox 滚动条样式 */
* {
  scrollbar-width: thin;
  scrollbar-color: rgba(16, 185, 129, 0.3) rgba(255, 255, 255, 0.05);
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --bg-primary: #09090B;
  --bg-secondary: #0F0F12;
  --bg-tertiary: #18181B;
  --bg-elevated: #1F1F23;
  
  --emerald-400: #34D399;
  --emerald-500: #10B981;
  --emerald-600: #059669;
  --teal-400: #2DD4BF;
  --teal-500: #14B8A6;
  --teal-600: #0D9488;
  --cyan-400: #22D3EE;
  --cyan-500: #06B6D4;
  
  --slate-300: #CBD5E1;
  --slate-400: #94A3B8;
  --slate-500: #64748B;
  --slate-600: #475569;
  --slate-700: #334155;
  --slate-800: #1E293B;
  
  --white: #FAFAFA;
  --white-alpha-5: rgba(250, 250, 250, 0.05);
  --white-alpha-10: rgba(250, 250, 250, 0.1);
  --white-alpha-20: rgba(250, 250, 250, 0.2);
  
  --glow-emerald: 0 0 40px rgba(16, 185, 129, 0.3);
  --glow-teal: 0 0 40px rgba(20, 184, 166, 0.3);
  
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  
  --border-subtle: 1px solid rgba(250, 250, 250, 0.06);
  --border-glow: 1px solid rgba(16, 185, 129, 0.2);
  
  --transition-fast: 150ms ease;
  --transition-normal: 250ms ease;
  --transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1);
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: var(--bg-primary);
  color: var(--white);
  line-height: 1.6;
  overflow-x: hidden;
}

/* Auth screen (mandatory login gate) */
.auth-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  position: relative;
}

.auth-screen::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(250, 250, 250, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(250, 250, 250, 0.02) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
  z-index: 0;
}

.auth-screen-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 1;
}

.auth-spinner {
  width: 40px;
  height: 40px;
  border: 2px solid rgba(16, 185, 129, 0.2);
  border-top-color: var(--emerald-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.auth-screen-content p {
  font-size: 14px;
  color: var(--slate-400);
}

.auth-screen-card {
  width: 100%;
  max-width: 480px;
  padding: 40px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  position: relative;
  z-index: 1;
  animation: fade-in 0.5s ease;
}

.auth-screen-brand {
  text-align: center;
  margin-bottom: 32px;
}

.auth-screen-brand .brand-emoji {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.auth-screen-brand h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--white);
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.auth-screen-brand p {
  font-size: 14px;
  color: var(--slate-400);
}

.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

.bg-grid {
  position: fixed;
  inset: 0;
  background-image: 
    linear-gradient(rgba(250, 250, 250, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(250, 250, 250, 0.02) 1px, transparent 1px);
  background-size: 60px 60px;
  pointer-events: none;
  z-index: 0;
}

.bg-glow {
  position: fixed;
  inset: 0;
  background: 
    radial-gradient(ellipse 60% 40% at 50% 0%, rgba(16, 185, 129, 0.08) 0%, transparent 50%),
    radial-gradient(ellipse 40% 30% at 80% 50%, rgba(20, 184, 166, 0.05) 0%, transparent 50%),
    radial-gradient(ellipse 50% 40% at 20% 80%, rgba(6, 182, 212, 0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.bg-noise {
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  opacity: 0.03;
  pointer-events: none;
  z-index: 0;
}

.particle-canvas {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
}

.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 16px 32px;
  background: rgba(9, 9, 11, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: var(--border-subtle);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-ring {
  position: absolute;
  inset: 0;
  border: 1px solid transparent;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500)) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  animation: rotate-ring 8s linear infinite;
}

@keyframes rotate-ring {
  to { transform: rotate(360deg); }
}

.logo-text {
  font-family: 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--emerald-400), var(--teal-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.brand-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.brand-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--white);
  letter-spacing: -0.02em;
}

.brand-tag {
  font-size: 10px;
  font-weight: 500;
  color: var(--emerald-400);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: var(--border-subtle);
}

.nav-link {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  background: transparent;
  border-radius: var(--radius-md);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: var(--slate-400);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.link-icon {
  font-size: 14px;
}

.nav-link:hover:not(.disabled) {
  color: var(--white);
  background: var(--white-alpha-5);
}

.nav-link.active {
  color: var(--emerald-400);
  background: var(--white-alpha-10);
}

.nav-link.active::before {
  content: '';
  position: absolute;
  bottom: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background: linear-gradient(90deg, var(--emerald-500), var(--teal-500));
  border-radius: 1px;
}

.nav-link.disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.link-pulse {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 6px;
  height: 6px;
  background: var(--emerald-500);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-lg);
  font-size: 12px;
  font-weight: 500;
  color: var(--slate-400);
  transition: all var(--transition-normal);
}

.status-indicator.active {
  color: var(--emerald-400);
  border-color: rgba(16, 185, 129, 0.2);
}

.status-dot {
  width: 6px;
  height: 6px;
  background: var(--slate-500);
  border-radius: 50%;
  transition: all var(--transition-normal);
}

.status-indicator.active .status-dot {
  background: var(--emerald-500);
  box-shadow: 0 0 8px var(--emerald-500);
}

.main-content {
  flex: 1;
  padding: 32px;
  position: relative;
  z-index: 1;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
  animation: fade-in 0.6s ease;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.empty-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: auto auto;
  gap: 16px;
  max-width: 800px;
}

.empty-card {
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 24px;
  transition: all var(--transition-normal);
}

.empty-card:hover {
  border-color: rgba(16, 185, 129, 0.2);
  background: var(--bg-tertiary);
}

.empty-card.main {
  grid-column: span 2;
  grid-row: span 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 48px;
}

.empty-icon {
  position: relative;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
  font-size: 32px;
}

.icon-ring {
  position: absolute;
  inset: 0;
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 50%;
  animation: breathe 3s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.5; }
}

.empty-card h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 8px;
}

.empty-card p {
  font-size: 14px;
  color: var(--slate-400);
  margin-bottom: 24px;
}

.btn-glow {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border: none;
  border-radius: var(--radius-lg);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  font-weight: 600;
  color: var(--bg-primary);
  cursor: pointer;
  box-shadow: var(--glow-emerald);
  transition: all var(--transition-normal);
}

.btn-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 60px rgba(16, 185, 129, 0.4);
}

.btn-arrow {
  transition: transform var(--transition-fast);
}

.btn-glow:hover .btn-arrow {
  transform: translateX(4px);
}

.empty-card.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.stat-value {
  font-family: 'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 32px;
  font-weight: 600;
  background: linear-gradient(135deg, var(--emerald-400), var(--teal-400));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat-label {
  font-size: 12px;
  color: var(--slate-400);
}

.empty-card.feature {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--slate-300);
}

.feature-icon {
  font-size: 16px;
}

.app-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px 32px;
  font-size: 12px;
  color: var(--slate-500);
  border-top: var(--border-subtle);
  position: relative;
  z-index: 1;
}

.footer-brand {
  font-weight: 600;
  color: var(--slate-400);
}

.footer-divider {
  color: var(--slate-600);
}

.nav-user {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-lg);
}

.user-avatar {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  color: var(--bg-primary);
}

.user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--white);
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  opacity: 0.6;
  transition: all var(--transition-fast);
}

.logout-btn:hover {
  opacity: 1;
  background: var(--white-alpha-10);
}

.login-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border: none;
  border-radius: var(--radius-lg);
  font-size: 13px;
  font-weight: 600;
  color: var(--bg-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: var(--glow-emerald);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fade-in 0.2s ease;
}

.modal-content {
  max-height: 80vh;
  overflow-y: auto;
  border-radius: var(--radius-xl);
}

.template-modal-overlay {
  z-index: 1001;
}

.template-modal-wrapper {
  position: relative;
  width: 96vw;
  height: 92vh;
  max-width: 1400px;
  animation: fade-in 0.3s ease;
}

.template-modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  color: var(--white);
  cursor: pointer;
  transition: all 0.2s ease;
}

.template-modal-close:hover {
  background: rgba(239, 68, 68, 0.6);
  border-color: rgba(239, 68, 68, 0.4);
  transform: scale(1.1);
}

.app-error-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.app-error-card {
  background: var(--bg-elevated);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-xl);
  padding: 32px;
  max-width: 440px;
  text-align: center;
}

.app-error-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #f87171;
  margin-bottom: 12px;
}

.app-error-card p {
  font-size: 13px;
  color: var(--slate-400);
  margin-bottom: 20px;
  line-height: 1.6;
}

.app-error-card button {
  padding: 10px 20px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.1);
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  color: var(--slate-300);
  cursor: pointer;
  margin: 0 6px;
  transition: all var(--transition-fast);
}

.app-error-card button:hover {
  background: var(--bg-secondary);
}

.app-error-card .reload-btn {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
  color: var(--emerald-400);
}

.app-error-card .reload-btn:hover {
  background: rgba(16, 185, 129, 0.2);
}

.resumes-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 900px;
  margin: 0 auto;
}

@media (max-width: 1024px) {
  .nav-link .link-text {
    display: none;
  }
  
  .nav-link {
    padding: 10px 12px;
  }
}

@media (max-width: 768px) {
  .navbar {
    flex-wrap: wrap;
    padding: 12px 16px;
    gap: 12px;
  }
  
  .nav-links {
    order: 3;
    width: 100%;
    justify-content: center;
  }
  
  .nav-user {
    order: 2;
  }
  
  .user-name {
    display: none;
  }
  
  .login-btn .btn-text {
    display: none;
  }
  
  .main-content {
    padding: 16px;
  }
  
  .empty-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .empty-card.main {
    grid-column: span 2;
  }
}
</style>
