<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <div class="header-icon">
          <div class="icon-ring"></div>
          <span>🔐</span>
        </div>
        <h2>{{ isLogin ? '欢迎回来' : '创建账户' }}</h2>
        <p>{{ isLogin ? '登录您的账户继续使用' : '注册新账户开始使用' }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="login-form">
        <div v-if="!isLogin" class="form-group">
          <label for="username">用户名</label>
          <div class="input-wrapper">
            <span class="input-icon">👤</span>
            <input
              id="username"
              v-model="form.username"
              type="text"
              placeholder="请输入用户名"
              :class="{ error: errors.username }"
              @blur="validateField('username')"
              @input="clearError('username')"
            />
          </div>
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>

        <div v-if="isLogin" class="form-group">
          <label for="loginUsername">用户名 / 邮箱</label>
          <div class="input-wrapper">
            <span class="input-icon">👤</span>
            <input
              id="loginUsername"
              v-model="form.loginUsername"
              type="text"
              placeholder="请输入用户名或邮箱"
              :class="{ error: errors.loginUsername }"
              @blur="validateField('loginUsername')"
              @input="clearError('loginUsername')"
            />
          </div>
          <span v-if="errors.loginUsername" class="error-message">{{ errors.loginUsername }}</span>
        </div>

        <div v-if="!isLogin" class="form-group">
          <label for="email">邮箱</label>
          <div class="input-wrapper">
            <span class="input-icon">📧</span>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="请输入邮箱地址"
              :class="{ error: errors.email }"
              @blur="validateField('email')"
              @input="clearError('email')"
            />
          </div>
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <div class="input-wrapper">
            <span class="input-icon">🔒</span>
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              :class="{ error: errors.password }"
              @blur="validateField('password')"
              @input="clearError('password')"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '🙈' : '👁️' }}
            </button>
          </div>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <div v-if="!isLogin" class="form-group">
          <label for="confirmPassword">确认密码</label>
          <div class="input-wrapper">
            <span class="input-icon">🔒</span>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              placeholder="请再次输入密码"
              :class="{ error: errors.confirmPassword }"
              @blur="validateField('confirmPassword')"
              @input="clearError('confirmPassword')"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showConfirmPassword = !showConfirmPassword"
            >
              {{ showConfirmPassword ? '🙈' : '👁️' }}
            </button>
          </div>
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
        </div>

        <div v-if="generalError" class="general-error">
          <span class="error-icon">⚠️</span>
          {{ generalError }}
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          <span v-else>{{ isLogin ? '登 录' : '注 册' }}</span>
        </button>
      </form>

      <div class="login-footer">
        <p>
          {{ isLogin ? '还没有账户？' : '已有账户？' }}
          <button type="button" class="switch-btn" @click="switchMode">
            {{ isLogin ? '立即注册' : '立即登录' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';

const props = withDefaults(defineProps<{
  required?: boolean;
}>(), {
  required: false,
});

const emit = defineEmits<{
  (e: 'login-success', user: any): void;
}>();

const isLogin = ref(true);
const isLoading = ref(false);
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const generalError = ref('');

const form = reactive({
  username: '',
  loginUsername: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const errors = reactive({
  username: '',
  loginUsername: '',
  email: '',
  password: '',
  confirmPassword: ''
});

function validateField(field: string): boolean {
  switch (field) {
    case 'username':
      if (!form.username.trim()) {
        errors.username = '请输入用户名';
        return false;
      }
      if (form.username.length < 3) {
        errors.username = '用户名至少需要3个字符';
        return false;
      }
      if (form.username.length > 20) {
        errors.username = '用户名不能超过20个字符';
        return false;
      }
      if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(form.username)) {
        errors.username = '用户名只能包含字母、数字、下划线和中文';
        return false;
      }
      errors.username = '';
      return true;

    case 'loginUsername':
      if (!form.loginUsername.trim()) {
        errors.loginUsername = '请输入用户名或邮箱';
        return false;
      }
      errors.loginUsername = '';
      return true;

    case 'email':
      if (!form.email.trim()) {
        errors.email = '请输入邮箱';
        return false;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        errors.email = '请输入有效的邮箱地址';
        return false;
      }
      errors.email = '';
      return true;

    case 'password':
      if (!form.password) {
        errors.password = '请输入密码';
        return false;
      }
      if (form.password.length < 6) {
        errors.password = '密码至少需要6个字符';
        return false;
      }
      if (form.password.length > 50) {
        errors.password = '密码不能超过50个字符';
        return false;
      }
      errors.password = '';
      return true;

    case 'confirmPassword':
      if (!form.confirmPassword) {
        errors.confirmPassword = '请确认密码';
        return false;
      }
      if (form.password !== form.confirmPassword) {
        errors.confirmPassword = '两次输入的密码不一致';
        return false;
      }
      errors.confirmPassword = '';
      return true;

    default:
      return true;
  }
}

function clearError(field: string) {
  errors[field as keyof typeof errors] = '';
  generalError.value = '';
}

function validateAll(): boolean {
  let isValid = true;
  
  if (isLogin.value) {
    if (!validateField('loginUsername')) isValid = false;
    if (!validateField('password')) isValid = false;
  } else {
    if (!validateField('username')) isValid = false;
    if (!validateField('email')) isValid = false;
    if (!validateField('password')) isValid = false;
    if (!validateField('confirmPassword')) isValid = false;
  }
  
  return isValid;
}

async function handleSubmit() {
  if (!validateAll()) return;
  
  isLoading.value = true;
  generalError.value = '';
  
  try {
    const endpoint = isLogin.value ? '/api/auth/login' : '/api/auth/register';
    const body = isLogin.value
      ? {
          username: form.loginUsername,
          password: form.password
        }
      : {
          username: form.username,
          email: form.email,
          password: form.password
        };
    
    const response = await fetch(`${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify(body)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      if (data.detail) {
        generalError.value = data.detail;
      } else {
        generalError.value = isLogin.value ? '登录失败，请重试' : '注册失败，请重试';
      }
      return;
    }
    
    emit('login-success', data.user);
    
  } catch (error: any) {
    console.error('Auth error:', error);
    generalError.value = '网络错误，请检查网络连接';
  } finally {
    isLoading.value = false;
  }
}

function switchMode() {
  isLogin.value = !isLogin.value;
  generalError.value = '';
  Object.keys(errors).forEach(key => {
    errors[key as keyof typeof errors] = '';
  });
  Object.keys(form).forEach(key => {
    form[key as keyof typeof form] = '';
  });
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
  padding: 32px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: var(--bg-secondary);
  border: var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 40px;
  animation: fade-in 0.4s ease;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.header-icon {
  position: relative;
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.header-icon .icon-ring {
  position: absolute;
  inset: 0;
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 50%;
  animation: breathe 3s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.5;
  }
}

.login-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: var(--white);
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: var(--slate-400);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--slate-300);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 14px;
  font-size: 16px;
  pointer-events: none;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 44px;
  background: var(--bg-tertiary);
  border: 1px solid rgba(250, 250, 250, 0.06);
  border-radius: var(--radius-md);
  font-size: 14px;
  color: var(--white);
  transition: all var(--transition-fast);
}

.input-wrapper input::placeholder {
  color: var(--slate-500);
}

.input-wrapper input:focus {
  outline: none;
  border-color: var(--emerald-500);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.input-wrapper input.error {
  border-color: #ef4444;
}

.toggle-password {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.toggle-password:hover {
  opacity: 1;
}

.error-message {
  font-size: 12px;
  color: #ef4444;
  margin-top: 4px;
}

.general-error {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: #fca5a5;
}

.error-icon {
  font-size: 14px;
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, var(--emerald-500), var(--teal-500));
  border: none;
  border-radius: var(--radius-lg);
  font-size: 15px;
  font-weight: 600;
  color: var(--bg-primary);
  cursor: pointer;
  box-shadow: var(--glow-emerald);
  transition: all var(--transition-normal);
  margin-top: 8px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 0 60px rgba(16, 185, 129, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(0, 0, 0, 0.2);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: var(--border-subtle);
}

.login-footer p {
  font-size: 13px;
  color: var(--slate-400);
}

.switch-btn {
  background: none;
  border: none;
  color: var(--emerald-400);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: color var(--transition-fast);
}

.switch-btn:hover {
  color: var(--emerald-300);
}
</style>
