import json
import os
import re
import time
from typing import Any, Dict, List, Optional

import requests


def _config_path_default() -> str:
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "siliconflow.json"
    )


def _load_siliconflow_config() -> Dict[str, Any]:
    cfg_path = os.getenv("SILICONFLOW_CONFIG_PATH", "").strip() or _config_path_default()
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except FileNotFoundError:
        return {}
    except Exception:
        return {}
    return {}


class SiliconFlowClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        cfg = _load_siliconflow_config()

        env_api_key = os.getenv("SILICONFLOW_API_KEY", "").strip()
        env_base_url = os.getenv("SILICONFLOW_BASE_URL", "").strip()
        env_model = os.getenv("SILICONFLOW_MODEL", "").strip()

        self.api_key = (api_key or env_api_key or cfg.get("apiKey") or cfg.get("api_key") or "").strip()
        self.base_url = (
            base_url
            or env_base_url
            or cfg.get("baseUrl")
            or cfg.get("base_url")
            or "https://api.siliconflow.cn/v1"
        ).strip()
        self.model = (model or env_model or cfg.get("model") or cfg.get("modelName") or "").strip() or "deepseek-ai/DeepSeek-V4-Flash"

        if not self.api_key:
            raise RuntimeError(
                "SILICONFLOW API Key 未设置：请配置环境变量或填写 backend/config/siliconflow.json"
            )

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 2048,
        extra: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        timeout: int = 180,
    ) -> str:
        url = self.base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if extra:
            payload.update(extra)

        if max_retries < 1:
            max_retries = 1

        proxies = {
            "http": None,
            "https": None,
        }

        last_error = None
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=timeout, proxies=proxies)
                break
            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    print(f"[SiliconFlow] 请求超时，{wait_time}秒后重试 (尝试 {attempt + 2}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(
                        f"硅基流动请求超时: 已重试{max_retries}次，每次超时{timeout}秒。"
                        f"建议：1) 检查网络连接 2) 稍后重试 3) 减少简历内容长度"
                    ) from e
            except requests.RequestException as e:
                raise RuntimeError(f"硅基流动请求异常: {e}") from e

        if not resp.ok:
            resp_text = ""
            try:
                resp_text = (resp.text or "").strip()
            except Exception:
                resp_text = ""
            resp_text = resp_text[:5000]
            raise RuntimeError(
                f"硅基流动返回错误: HTTP {resp.status_code} {resp.reason}; "
                f"body={resp_text or '(空响应)'}; model={self.model}"
            )

        data = resp.json()

        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            for k in ["output_text", "text", "result"]:
                if k in data and isinstance(data[k], str):
                    return data[k]
            raise RuntimeError(f"无法解析硅基流动响应: {data}")


    def embed(self, texts: List[str], max_retries: int = 3, timeout: int = 60) -> List[List[float]]:
        url = self.base_url.rstrip("/") + "/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": texts,
        }

        proxies = {"http": None, "https": None}

        last_error = None
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=timeout, proxies=proxies)
                break
            except requests.exceptions.Timeout as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"[SiliconFlow] embedding 超时，{wait_time}秒后重试 (尝试 {attempt + 2}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    raise RuntimeError(f"硅基流动 embedding 请求超时") from e
            except requests.RequestException as e:
                raise RuntimeError(f"硅基流动 embedding 请求异常: {e}") from e

        if not resp.ok:
            raise RuntimeError(f"硅基流动 embedding 返回错误: HTTP {resp.status_code}")

        data = resp.json()
        try:
            items = sorted(data["data"], key=lambda x: x.get("index", 0))
            return [item["embedding"] for item in items]
        except Exception:
            raise RuntimeError(f"无法解析硅基流动 embedding 响应: {data}")


def extract_json_object(text: str) -> Any:
    text = text.strip()
    if not text:
        raise ValueError("输入文本为空")

    # 方法1：尝试直接解析整个文本
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 方法2：移除可能的markdown代码块标记
    cleaned = re.sub(r'^```(?:json)?\s*', '', text)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 方法3：找到第一个完整的JSON对象（处理嵌套）
    start = cleaned.find('{')
    if start == -1:
        raise ValueError("未找到JSON对象起始标记 '{'")

    # 统一栈：存 '(' → push '{'; 存 '[' → push '['; 遇 '}' 期望栈顶是 '{'; 遇 ']' 期望栈顶是 '['
    stack: list[str] = []
    in_string = False
    escape_next = False
    end = -1

    for i, char in enumerate(cleaned[start:], start):
        if escape_next:
            escape_next = False
            continue

        if char == '\\' and in_string:
            escape_next = True
            continue

        if char == '"' and not escape_next:
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == '{':
            stack.append('{')
        elif char == '[':
            stack.append('[')
        elif char == '}':
            if stack and stack[-1] == '{':
                stack.pop()
                if not stack:
                    end = i
                    break
        elif char == ']':
            if stack and stack[-1] == '[':
                stack.pop()

    if end >= 0 and not stack:
        return json.loads(cleaned[start:end + 1])

    # 自动修复：补全缺失的括号和字符串
    json_str = cleaned[start:]
    json_str = json_str.rstrip()

    if in_string:
        json_str = json_str + '"'

    # 移除末尾的逗号和不完整的键值对
    json_str = re.sub(r',\s*$', '', json_str)
    json_str = re.sub(r',\s*"[^"]*"\s*:\s*$', '', json_str)
    json_str = re.sub(r',\s*$', '', json_str)

    # 重新扫描，找出需要补的闭合括号
    repair_stack: list[str] = []
    r_in_string = False
    r_escape = False

    for char in json_str:
        if r_escape:
            r_escape = False
            continue
        if char == '\\' and r_in_string:
            r_escape = True
            continue
        if char == '"' and not r_escape:
            r_in_string = not r_in_string
            continue
        if r_in_string:
            continue
        if char == '{':
            repair_stack.append('}')
        elif char == '[':
            repair_stack.append(']')
        elif char == '}':
            if repair_stack and repair_stack[-1] == '}':
                repair_stack.pop()
        elif char == ']':
            if repair_stack and repair_stack[-1] == ']':
                repair_stack.pop()

    if repair_stack:
        json_str = json_str + ''.join(reversed(repair_stack))

    # 尝试解析
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        raise ValueError(f"JSON解析失败，提取的内容片段: {json_str[:500]}...")
