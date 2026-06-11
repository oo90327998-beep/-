import type { 
  OcrResponse, 
  SuggestionsResponse, 
  ExperienceQuestion,
  RefinedExperienceResponse,
  StyleInfo,
  StyleTransformResponse,
  ResumeListItem,
  ATSReport
} from "../types";

const API_BASE = '/api';
const DEFAULT_TIMEOUT = 360000;  // backend LLM can take 3 retries × 180s each

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(new Error('请求超时，请稍后重试')), DEFAULT_TIMEOUT);

  try {
    const resp = await fetch(url, {
      ...options,
      credentials: 'include',
      signal: controller.signal,
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => "");
      throw new Error(`请求失败：${resp.status} ${text || resp.statusText}`);
    }
    const contentType = resp.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      throw new Error(`服务器返回了非 JSON 响应`);
    }
    return resp.json();
  } catch (err: unknown) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new Error('请求超时或已取消，请稍后重试');
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}

export async function ocrResume(file: File): Promise<OcrResponse> {
  const form = new FormData();
  form.append("file", file);

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(new Error('OCR 处理超时，请稍后重试')), 480000);
  try {
    const resp = await fetch(`${API_BASE}/ocr`, {
      method: "POST",
      body: form,
      credentials: 'include',
      signal: controller.signal,
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => "");
      throw new Error(`OCR 请求失败：${resp.status} ${text || resp.statusText}`);
    }
    return (await resp.json()) as OcrResponse;
  } catch (err: unknown) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new Error('OCR 请求超时或已取消，请稍后重试');
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}

export async function generateSuggestions(resumeId: number, styleType: string = '', targetJob: string = ''): Promise<SuggestionsResponse> {
  return fetchJson<SuggestionsResponse>(`${API_BASE}/suggestions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resumeId, styleType, targetJob }),
  });
}

export async function getResumes(limit: number = 20, offset: number = 0): Promise<{ items: ResumeListItem[]; total: number }> {
  return fetchJson<{ items: ResumeListItem[]; total: number }>(`${API_BASE}/resumes?limit=${limit}&offset=${offset}`);
}

export async function getResume(resumeId: number): Promise<any> {
  return fetchJson<any>(`${API_BASE}/resume/${resumeId}`);
}

export async function deleteResume(resumeId: number): Promise<{ success: boolean }> {
  return fetchJson<{ success: boolean }>(`${API_BASE}/resume/${resumeId}`, {
    method: 'DELETE',
  });
}

export async function getExperienceQuestions(): Promise<ExperienceQuestion[]> {
  return fetchJson<ExperienceQuestion[]>(`${API_BASE}/experience/questions`);
}

export async function createExperienceSession(): Promise<{ sessionId: string }> {
  return fetchJson<{ sessionId: string }>(`${API_BASE}/experience/session`, {
    method: 'POST',
  });
}

export async function saveExperienceAnswer(sessionId: string, questionKey: string, answer: string): Promise<{ success: boolean }> {
  return fetchJson<{ success: boolean }>(`${API_BASE}/experience/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sessionId, questionKey, answer }),
  });
}

export async function saveExperienceAnswers(sessionId: string, answers: Record<string, string>): Promise<{ success: boolean }> {
  return fetchJson<{ success: boolean }>(`${API_BASE}/experience/answers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sessionId, answers }),
  });
}

export async function refineExperience(sessionId: string, answers: Record<string, string>): Promise<RefinedExperienceResponse> {
  return fetchJson<RefinedExperienceResponse>(`${API_BASE}/experience/refine`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sessionId, answers }),
  });
}

export async function getStyles(): Promise<Record<string, StyleInfo>> {
  return fetchJson<Record<string, StyleInfo>>(`${API_BASE}/styles`);
}

export async function transformStyle(resumeId: number, styleType: string, targetJob: string = ''): Promise<StyleTransformResponse> {
  return fetchJson<StyleTransformResponse>(`${API_BASE}/transform`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resumeId, styleType, targetJob }),
  });
}

export async function checkATS(resumeId: number): Promise<ATSReport> {
  return fetchJson<ATSReport>(`${API_BASE}/ats/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resumeId }),
  });
}

export async function getATSReport(resumeId: number): Promise<ATSReport> {
  return fetchJson<ATSReport>(`${API_BASE}/ats/report/${resumeId}`);
}

export async function exportPdf(resumeId: number, useOptimized: boolean = false): Promise<void> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(new Error('导出超时，请稍后重试')), 30000);
  try {
    const resp = await fetch(`${API_BASE}/export/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ resumeId, useOptimized }),
      credentials: 'include',
      signal: controller.signal,
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => "");
      throw new Error(`导出失败：${resp.status} ${text || resp.statusText}`);
    }
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = useOptimized ? 'resume_optimized.pdf' : 'resume.pdf';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  } catch (err: unknown) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new Error('导出请求超时或已取消，请稍后重试');
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}

export async function generateCoverLetter(resumeId: number, targetJob: string = '', company: string = ''): Promise<any> {
  return fetchJson<any>(`${API_BASE}/cover-letter`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resumeId, targetJob, company }),
  });
}

export async function interviewCoach(resumeId: number, targetJob: string = ''): Promise<any> {
  return fetchJson<any>(`${API_BASE}/interview-coach`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resumeId, targetJob }),
  });
}

export async function careerRecommend(resumeId: number, targetJob: string = ''): Promise<any> {
  return fetchJson<any>(`${API_BASE}/career-recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resumeId, targetJob }),
  });
}

export async function careerPlanning(resumeId: number, targetJob: string = ''): Promise<any> {
  return fetchJson<any>(`${API_BASE}/career-planning`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resumeId, targetJob }),
  });
}

export async function chatWithAssistant(resumeId: number, message: string, history: Array<{role: string, content: string}> = []): Promise<{response: string}> {
  return fetchJson<{response: string}>(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resumeId, message, history }),
  });
}

export async function recognizeSpeech(audioBlob: Blob): Promise<{text: string, success: boolean, error?: string}> {
  const formData = new FormData();
  formData.append('file', audioBlob, 'audio.wav');
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(new Error('语音识别超时，请稍后重试')), 30000);
  try {
    const resp = await fetch(`${API_BASE}/speech-recognize`, {
      method: 'POST',
      body: formData,
      credentials: 'include',
      signal: controller.signal,
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => "");
      throw new Error(`语音识别失败：${resp.status} ${text || resp.statusText}`);
    }
    return resp.json();
  } catch (err: unknown) {
    if (err instanceof DOMException && err.name === 'AbortError') {
      return { text: '', success: false, error: '语音识别请求超时或已取消' };
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}
