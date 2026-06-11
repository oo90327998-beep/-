import json
import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from supabase import AsyncClient

from app.db.database import get_supabase
from app.db.repo import ResumeRepo, User
from app.db.interview_repo import InterviewRepo
from app.api.auth_routes import get_current_user
from app.api.rate_limit import rate_limit_llm
from app.services.interview_agent import (
    InterviewAgent,
    build_interview_agent,
    embed_and_store_chunks,
)

router = APIRouter(prefix="/api/interview", tags=["interview"])


# ── Pydantic Models ────────────────────────────────────────────

class CreateSessionRequest(BaseModel):
    resumeId: int
    mode: str  # diagnose | technical | behavioral | simulation


class SendMessageRequest(BaseModel):
    sessionId: str
    message: str
    history: List[Dict[str, str]] = []


class SessionSummary(BaseModel):
    sessionId: str
    mode: str
    status: str
    createdAt: str


# ── Helpers ────────────────────────────────────────────────────

def _safe_parse_sections(sections_json: Optional[str]) -> Any:
    if not sections_json:
        return []
    try:
        return json.loads(sections_json)
    except json.JSONDecodeError:
        return []


# ── Routes ─────────────────────────────────────────────────────

@router.post("/session")
async def create_session(
    req: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncClient = Depends(get_supabase),
):
    resume_repo = ResumeRepo(db)
    record = await resume_repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    if req.mode not in ("diagnose", "technical", "behavioral", "simulation"):
        raise HTTPException(status_code=400, detail=f"无效的面试模式: {req.mode}")

    interview_repo = InterviewRepo(db)
    session_id = await interview_repo.create_session(
        user_id=current_user.id,
        resume_id=req.resumeId,
        mode=req.mode,
    )

    sections = _safe_parse_sections(record.sections_json)

    try:
        chunk_count = await embed_and_store_chunks(session_id, sections, interview_repo)
    except Exception as e:
        await interview_repo.update_session_status(session_id, "cancelled")
        raise HTTPException(status_code=502, detail=f"简历向量化失败: {e}")

    return {
        "sessionId": session_id,
        "mode": req.mode,
        "chunksEmbedded": chunk_count,
    }


@router.post("/message")
async def send_message(
    req: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    _rate=Depends(rate_limit_llm),
    db: AsyncClient = Depends(get_supabase),
):
    interview_repo = InterviewRepo(db)
    session = await interview_repo.get_session(req.sessionId)
    if session is None:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此会话")
    if session.status != "active":
        raise HTTPException(status_code=400, detail="面试已结束")

    resume_repo = ResumeRepo(db)
    sections = await resume_repo.get_sections(session.resume_id)
    if sections is None:
        raise HTTPException(status_code=404, detail="简历数据不存在")

    agent = await build_interview_agent(
        session_id=req.sessionId,
        mode=session.mode,
        user_id=current_user.id,
        sections=sections,
        repo=interview_repo,
    )

    async def sse_generator():
        try:
            response = await agent.process_message(req.message, req.history)
            yield f"data: {json.dumps({'content': response}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncClient = Depends(get_supabase),
):
    interview_repo = InterviewRepo(db)
    sessions = await interview_repo.list_sessions(current_user.id, limit=20)
    return [
        {
            "sessionId": s.session_id,
            "mode": s.mode,
            "status": s.status,
            "createdAt": s.created_at,
        }
        for s in sessions
    ]


@router.get("/report/{session_id}")
async def get_report(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncClient = Depends(get_supabase),
):
    interview_repo = InterviewRepo(db)
    session = await interview_repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此会话")

    report = await interview_repo.get_report(session_id)
    if report is None:
        raise HTTPException(status_code=404, detail="面试报告尚未生成")

    return {
        "sessionId": session_id,
        "overallScore": report.overall_score,
        "strengths": report.strengths,
        "weaknesses": report.weaknesses,
        "suggestions": report.suggestions,
        "fullReport": report.full_report,
        "createdAt": report.created_at,
    }


@router.get("/messages/{session_id}")
async def get_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncClient = Depends(get_supabase),
):
    interview_repo = InterviewRepo(db)
    session = await interview_repo.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="面试会话不存在")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此会话")

    messages = await interview_repo.get_messages(session_id)
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "createdAt": m.created_at,
        }
        for m in messages
    ]
