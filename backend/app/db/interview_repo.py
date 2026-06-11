import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from supabase import AsyncClient


@dataclass
class InterviewSession:
    session_id: str
    user_id: int
    resume_id: int
    mode: str
    status: str
    current_question_index: int
    total_questions: int
    created_at: str
    updated_at: str


@dataclass
class InterviewMessage:
    id: int
    session_id: str
    role: str
    content: Optional[str]
    tool_calls: Optional[Any]
    created_at: str


@dataclass
class InterviewReport:
    id: int
    session_id: str
    overall_score: Optional[float]
    strengths: list
    weaknesses: list
    suggestions: list
    full_report: Optional[str]
    created_at: str


class InterviewRepo:
    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    # ── interview_sessions ─────────────────────────────────────────

    async def create_session(
        self, user_id: int, resume_id: int, mode: str
    ) -> str:
        session_id = str(uuid.uuid4())
        data = {
            "session_id": session_id,
            "user_id": user_id,
            "resume_id": resume_id,
            "mode": mode,
            "status": "active",
        }
        await self.client.table("interview_sessions").insert(data).execute()
        return session_id

    async def get_session(self, session_id: str) -> Optional[InterviewSession]:
        r = await self.client.table("interview_sessions").select("*") \
            .eq("session_id", session_id).maybe_single().execute()
        return self._row_to_session(r.data) if r.data else None

    async def list_sessions(self, user_id: int, limit: int = 20) -> List[InterviewSession]:
        r = await self.client.table("interview_sessions").select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .limit(limit).execute()
        return [self._row_to_session(row) for row in (r.data or [])]

    async def update_session_status(self, session_id: str, status: str) -> None:
        await self.client.table("interview_sessions").update({"status": status}) \
            .eq("session_id", session_id).execute()

    async def update_session_progress(
        self, session_id: str, question_index: int, total_questions: int
    ) -> None:
        await self.client.table("interview_sessions").update({
            "current_question_index": question_index,
            "total_questions": total_questions,
        }).eq("session_id", session_id).execute()

    async def complete_session(self, session_id: str) -> None:
        await self.client.table("interview_sessions").update({
            "status": "completed",
        }).eq("session_id", session_id).execute()

    # ── interview_messages ──────────────────────────────────────────

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[Any] = None,
    ) -> int:
        data: Dict[str, Any] = {"session_id": session_id, "role": role}
        if content is not None:
            data["content"] = content
        if tool_calls is not None:
            data["tool_calls"] = json.dumps(tool_calls, ensure_ascii=False)
        r = await self.client.table("interview_messages").insert(data).execute()
        return r.data[0]["id"]

    async def get_messages(self, session_id: str) -> List[InterviewMessage]:
        r = await self.client.table("interview_messages").select("*") \
            .eq("session_id", session_id) \
            .order("created_at").execute()
        return [self._row_to_message(row) for row in (r.data or [])]

    # ── interview_reports ───────────────────────────────────────────

    async def save_report(
        self,
        session_id: str,
        overall_score: float,
        strengths: list,
        weaknesses: list,
        suggestions: list,
        full_report: str,
    ) -> int:
        data = {
            "session_id": session_id,
            "overall_score": overall_score,
            "strengths": json.dumps(strengths, ensure_ascii=False),
            "weaknesses": json.dumps(weaknesses, ensure_ascii=False),
            "suggestions": json.dumps(suggestions, ensure_ascii=False),
            "full_report": full_report,
        }
        r = await self.client.table("interview_reports").insert(data).execute()
        return r.data[0]["id"]

    async def get_report(self, session_id: str) -> Optional[InterviewReport]:
        r = await self.client.table("interview_reports").select("*") \
            .eq("session_id", session_id).maybe_single().execute()
        return self._row_to_report(r.data) if r.data else None

    # ── resume_chunks ───────────────────────────────────────────────

    async def save_resume_chunks(
        self, session_id: str, chunks: List[Dict[str, Any]]
    ) -> None:
        if not chunks:
            return
        rows = [
            {
                "session_id": session_id,
                "chunk_index": c["chunk_index"],
                "content": c["content"],
                "embedding": json.dumps(c["embedding"]),
            }
            for c in chunks
        ]
        await self.client.table("resume_chunks").insert(rows).execute()

    async def search_resume_chunks(
        self, session_id: str, query_embedding: List[float], top_k: int = 3
    ) -> List[Dict[str, Any]]:
        embedding_str = json.dumps(query_embedding)
        r = await self.client.rpc("search_resume_chunks", {
            "query_session_id": session_id,
            "query_embedding": embedding_str,
            "top_k": top_k,
        }).execute()
        return r.data or []

    async def delete_resume_chunks(self, session_id: str) -> None:
        await self.client.table("resume_chunks").delete() \
            .eq("session_id", session_id).execute()

    # ── question_bank ───────────────────────────────────────────────

    async def search_question_bank(
        self, query_embedding: List[float], category: Optional[str] = None, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        embedding_str = json.dumps(query_embedding)
        params = {"query_embedding": embedding_str, "top_k": top_k}
        r = await self.client.rpc("search_question_bank", params).execute()
        results = r.data or []
        if category:
            results = [row for row in results if row.get("category") == category]
            results = results[:top_k]
        return results

    async def insert_question(
        self,
        question: str,
        category: str,
        embedding: List[float],
        role: Optional[str] = None,
        difficulty: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        data: Dict[str, Any] = {
            "question": question,
            "category": category,
            "embedding": json.dumps(embedding),
        }
        if role:
            data["role"] = role
        if difficulty:
            data["difficulty"] = difficulty
        if tags:
            data["tags"] = tags
        r = await self.client.table("question_bank").insert(data).execute()
        return r.data[0]["id"]

    # ── helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _row_to_session(row: dict) -> InterviewSession:
        return InterviewSession(
            session_id=row["session_id"],
            user_id=row["user_id"],
            resume_id=row["resume_id"],
            mode=row["mode"],
            status=row["status"],
            current_question_index=row.get("current_question_index", 0),
            total_questions=row.get("total_questions", 0),
            created_at=str(row.get("created_at", "")),
            updated_at=str(row.get("updated_at", "")),
        )

    @staticmethod
    def _row_to_message(row: dict) -> InterviewMessage:
        return InterviewMessage(
            id=row["id"],
            session_id=row["session_id"],
            role=row["role"],
            content=row.get("content"),
            tool_calls=row.get("tool_calls"),
            created_at=str(row.get("created_at", "")),
        )

    @staticmethod
    def _row_to_report(row: dict) -> InterviewReport:
        def _parse_json(raw) -> list:
            if raw is None:
                return []
            if isinstance(raw, list):
                return raw
            if isinstance(raw, str):
                try:
                    return json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    return []
            return []

        return InterviewReport(
            id=row["id"],
            session_id=row["session_id"],
            overall_score=row.get("overall_score"),
            strengths=_parse_json(row.get("strengths")),
            weaknesses=_parse_json(row.get("weaknesses")),
            suggestions=_parse_json(row.get("suggestions")),
            full_report=row.get("full_report"),
            created_at=str(row.get("created_at", "")),
        )
