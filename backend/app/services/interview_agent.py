import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable

from app.services.siliconflow_client import SiliconFlowClient, extract_json_object
from app.db.interview_repo import InterviewRepo


# ============================================================
# Resume Chunking
# ============================================================

def chunk_resume_text(text: str, chunk_size: int = 300, chunk_overlap: int = 50) -> List[str]:
    """RecursiveCharacterTextSplitter 等效分块，无外部依赖。"""
    if not text or not text.strip():
        return []

    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 1 <= chunk_size:
            current = (current + "\n\n" + para).strip() if current else para
        else:
            if current:
                chunks.append(current)
            if len(para) <= chunk_size:
                current = para
            else:
                sentences = re.split(r'(?<=[。！？.!?])\s*', para)
                for sent in sentences:
                    sent = sent.strip()
                    if not sent:
                        continue
                    if len(current) + len(sent) + 1 <= chunk_size:
                        current = (current + " " + sent).strip() if current else sent
                    else:
                        if current:
                            chunks.append(current)
                        if chunk_overlap > 0 and current:
                            overlap_text = current[-chunk_overlap:] if len(current) > chunk_overlap else current
                            current = overlap_text + " " + sent
                        else:
                            current = sent
                if current:
                    chunks.append(current)
                    current = ""

    if current:
        chunks.append(current)

    return [c for c in chunks if c.strip()]


def flatten_sections(sections: Any) -> str:
    """将简历 sections JSON 展平为可检索的文本。"""
    if isinstance(sections, str):
        try:
            sections = json.loads(sections)
        except (json.JSONDecodeError, TypeError):
            return sections

    if isinstance(sections, dict):
        lines = []
        for key, val in sections.items():
            if isinstance(val, str):
                lines.append(f"{key}: {val}")
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, dict):
                        lines.append(json.dumps(item, ensure_ascii=False))
                    elif isinstance(item, str):
                        lines.append(f"- {item}")
            elif isinstance(val, dict):
                lines.append(json.dumps(val, ensure_ascii=False))
        return "\n".join(lines)

    if isinstance(sections, list):
        return "\n".join(json.dumps(item, ensure_ascii=False) if isinstance(item, dict) else str(item) for item in sections)

    return str(sections)


# ============================================================
# System Prompts
# ============================================================

_SYSTEM_PROMPTS = {
    "diagnose": """# Role: 小优 - 资深大厂面试官与职业发展教练

你是"小优"，拥有10年以上头部互联网/科技公司校招与社招面试经验，精通结构化面试、STAR法则与胜任力模型。
语调：专业、犀利、一针见血。拒绝废话和套话。

## 当前模式：简历深度面诊

1. 岗位解构 → 2. 简历扫描（寻找逻辑漏洞、数据造假嫌疑点、高价值产出、技术栈匹配度）→ 3. GAP分析 → 4. 给出全局建议

## 搜索工具
你可以调用 search_resume 工具检索简历中的具体细节。

输出格式：
先用 2-3 句话总结候选人核心竞争力，然后逐项指出风险点和改进建议，最后给出 3-5 条全局面试建议。""",

    "technical": """# Role: 小优 - 资深大厂面试官与职业发展教练

你是"小优"，拥有10年以上头部互联网/科技公司校招与社招面试经验。
语调：专业、犀利。抛出有深度的场景题，绝不用搜索引擎能查到的八股文。

## 当前模式：岗位技术拷问

一次只问一个问题。根据候选人的回答，决定是追问还是进入下一题。计划 3-5 题。

## 搜索工具
每轮提问前，先调用 search_resume 检索与问题相关的简历片段，确保问题紧贴候选人的项目经历和技术栈。

## 行为规则
- 每次只输出一道题，等待用户回答
- 回答太敷衍时直接指出，要求重答
- 答得好的也简要肯定再进入下一题
- 3-5 题后自动结束并生成报告""",

    "behavioral": """# Role: 小优 - 资深大厂面试官与职业发展教练

你是"小优"，精通 HR 行为面试和胜任力模型。
语调：设定有压迫感的职场场景，考验候选人的软技能。

## 当前模式：行为面试（HR面）演练

一次只问一个问题。围绕 STAR 法则（Situation, Task, Action, Result）深挖。计划 3-5 题。

## 搜索工具
每轮提问前调用 search_resume 检索简历中的项目/团队经历，设计针对性场景题。

## 行为规则
- 每次只输出一道行为场景题
- 用户回答后用 STAR 框架点评
- 3-5 题后自动结束并生成报告""",

    "simulation": """# Role: 小优 - 资深大厂面试官与职业发展教练

你是"小优"，拥有10年以上校招与社招面试经验。
语调：真实面试官风格，由浅入深，逐步施压。

## 当前模式：全真沉浸式模拟面试

模拟真实面试全流程：开场寒暄 → 自我介绍点评 → 项目深挖 → 技术/行为交叉提问 → 候选人反问。计划 5-8 题。

## 搜索工具
每轮提问前调用 search_resume 检索相关简历片段，确保模拟逼真。

## 行为规则
- 按真实面试节奏推进
- 回答不够深入时追问
- 5-8 题后逐步收尾，最后生成报告""",
}


def build_system_prompt(mode: str, resume_context: str) -> str:
    base = _SYSTEM_PROMPTS.get(mode, _SYSTEM_PROMPTS["diagnose"])
    return base + f"\n\n## 候选人简历\n{resume_context}\n\n记住：你始终是“小优”，不是通用 AI 助手。拒绝回答与面试无关的问题。"


# ============================================================
# Interview Agent State
# ============================================================

@dataclass
class AgentContext:
    session_id: str
    mode: str
    user_id: int
    resume_text: str
    sections: Any
    client: SiliconFlowClient
    repo: InterviewRepo
    embedding_client: SiliconFlowClient


class InterviewAgent:
    """面试助手 Agent —— 管理面试会话、执行 RAG 检索、生成响应。"""

    def __init__(self, ctx: AgentContext):
        self.ctx = ctx
        self._system_prompt = build_system_prompt(ctx.mode, flatten_sections(ctx.sections))

    # ── Tool: search_resume ────────────────────────────────────────

    async def search_resume(self, query: str) -> str:
        """RAG 检索简历中与 query 最相关的片段。"""
        try:
            embedding = self.ctx.embedding_client.embed([query])[0]
        except Exception:
            return "[检索失败：embedding API 不可用]"

        try:
            chunks = await self.ctx.repo.search_resume_chunks(
                self.ctx.session_id, embedding, top_k=3
            )
        except Exception:
            return "[检索失败：数据库查询异常]"

        if not chunks:
            return "[未找到相关简历内容]"

        results = []
        for c in chunks:
            sim = c.get("similarity", 0)
            content = c.get("content", "")
            results.append(f"[相似度: {sim:.2f}] {content}")

        return "\n\n".join(results)

    # ── Tool: generate_report ──────────────────────────────────────

    async def generate_report(self) -> Dict[str, Any]:
        """生成面试结束报告。"""
        messages = await self.ctx.repo.get_messages(self.ctx.session_id)
        transcript = "\n".join(
            f"{'👤 候选人' if m.role == 'user' else '🤖 小优'}: {m.content or ''}"
            for m in messages
        )

        prompt = f"""基于以下面试对话记录，生成面试评估报告：

{transcript}

输出 JSON：
{{
  "overall_score": 8.5,
  "strengths": ["优势1", "优势2"],
  "weaknesses": ["薄弱项1", "薄弱项2"],
  "suggestions": ["建议1", "建议2", "建议3"],
  "full_report": "完整的面试报告文本（小优的口吻，包含总体评价、各维度分析、改进建议）"
}}"""

        response = self.ctx.client.chat(
            messages=[
                {"role": "system", "content": "你是小优，资深面试官。基于面试对话记录生成专业的面试评估报告。只输出 JSON，不要 markdown 代码块。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        try:
            report = extract_json_object(response)
        except Exception:
            report = {
                "overall_score": 0,
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "full_report": response,
            }

        await self.ctx.repo.save_report(
            session_id=self.ctx.session_id,
            overall_score=float(report.get("overall_score", 0)),
            strengths=report.get("strengths", []),
            weaknesses=report.get("weaknesses", []),
            suggestions=report.get("suggestions", []),
            full_report=report.get("full_report", ""),
        )

        await self.ctx.repo.complete_session(self.ctx.session_id)
        return report

    # ── Main Agent Loop ────────────────────────────────────────────

    async def process_message(
        self,
        user_message: str,
        history: List[Dict[str, str]],
    ) -> str:
        """处理用户消息，返回 Agent 响应。"""

        messages = await self.ctx.repo.get_messages(self.ctx.session_id)

        # 判断是否需要结束面试
        question_count = sum(1 for m in messages if m.role == "assistant")

        # 模式相关的题目数上限
        max_questions = {
            "diagnose": 1,
            "technical": 5,
            "behavioral": 5,
            "simulation": 8,
        }.get(self.ctx.mode, 5)

        should_end = question_count >= max_questions

        # 构建 LLM 消息
        llm_messages: List[Dict[str, str]] = [
            {"role": "system", "content": self._system_prompt},
        ]

        # 注入历史消息（最近 20 条）
        recent_history = history[-20:] if len(history) > 20 else history
        for msg in recent_history:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

        # 如果应该结束，追加结束指令
        if should_end:
            llm_messages.append({
                "role": "user",
                "content": "[系统指令] 面试已到结束节点。请生成完整的面试评估报告，以 JSON 格式输出报告（包含 overall_score, strengths, weaknesses, suggestions, full_report），不要继续提问。",
            })
        else:
            llm_messages.append({"role": "user", "content": user_message})

        # 保存用户消息
        await self.ctx.repo.save_message(self.ctx.session_id, "user", user_message)

        # 调用 LLM
        temperature = {
            "diagnose": 0.4,
            "technical": 0.6,
            "behavioral": 0.6,
            "simulation": 0.7,
        }.get(self.ctx.mode, 0.6)

        response = self.ctx.client.chat(
            messages=llm_messages,
            temperature=temperature,
            max_tokens=2000,
        )

        # 保存 assistant 消息
        await self.ctx.repo.save_message(self.ctx.session_id, "assistant", response)

        # 如果是面诊模式或已到达结尾，尝试生成报告
        if self.ctx.mode == "diagnose" or should_end:
            try:
                report: Dict[str, Any] = await self._parse_or_generate_report(response)
                await self.ctx.repo.save_report(
                    session_id=self.ctx.session_id,
                    overall_score=float(report.get("overall_score", 0)),
                    strengths=report.get("strengths", []),
                    weaknesses=report.get("weaknesses", []),
                    suggestions=report.get("suggestions", []),
                    full_report=report.get("full_report", ""),
                )
                await self.ctx.repo.complete_session(self.ctx.session_id)
            except Exception:
                pass

        return response

    async def _parse_or_generate_report(self, response: str) -> Dict[str, Any]:
        try:
            return extract_json_object(response)
        except Exception:
            return await self.generate_report()

# ============================================================
# Factory
# ============================================================

async def build_interview_agent(
    session_id: str,
    mode: str,
    user_id: int,
    sections: Any,
    repo: InterviewRepo,
) -> InterviewAgent:
    client = SiliconFlowClient()
    emb_client = SiliconFlowClient(model="BAAI/bge-large-zh-v1.5")

    resume_text = flatten_sections(sections)

    ctx = AgentContext(
        session_id=session_id,
        mode=mode,
        user_id=user_id,
        resume_text=resume_text,
        sections=sections,
        client=client,
        repo=repo,
        embedding_client=emb_client,
    )

    return InterviewAgent(ctx)


async def embed_and_store_chunks(
    session_id: str,
    sections: Any,
    repo: InterviewRepo,
) -> int:
    """将简历分块并 embedding 存入 Supabase。返回 chunk 数量。"""
    text = flatten_sections(sections)
    chunks = chunk_resume_text(text, chunk_size=300, chunk_overlap=50)

    if not chunks:
        return 0

    client = SiliconFlowClient(model="BAAI/bge-large-zh-v1.5")

    batch_size = 8
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        all_embeddings.extend(client.embed(batch))

    chunk_data = [
        {
            "chunk_index": idx,
            "content": chunk,
            "embedding": emb,
        }
        for idx, (chunk, emb) in enumerate(zip(chunks, all_embeddings))
    ]

    await repo.save_resume_chunks(session_id, chunk_data)
    return len(chunk_data)
