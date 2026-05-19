import json
import time
import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repo import ResumeRepo, User
from app.api.auth_routes import get_current_user
from app.services.siliconflow_client import SiliconFlowClient
from app.services.resume_ocr import (
    extract_text_from_pdf_bytes, 
    extract_images_from_pdf_bytes, 
    extract_text_async,
    extract_images_async,
    llm_extract_sections
)
from app.services.suggestions import llm_generate_suggestions
from app.services.performance_cache import result_cache, performance_monitor
from app.services.pdf_generator import generate_resume_pdf
from app.api.rate_limit import rate_limit_llm, rate_limit_ocr, rate_limit_general
from app.services.advanced_features import (
    get_experience_questions,
    llm_refine_experience,
    get_style_types,
    llm_transform_style,
    llm_ats_check,
    llm_generate_cover_letter,
    llm_interview_coach,
    llm_career_recommend,
    llm_career_planning,
    get_job_positions,
    llm_resume_assistant,
    llm_resume_question_answer,
)


router = APIRouter()


def _safe_parse_sections(sections_json: Optional[str]) -> List[dict]:
    """Safely parse sections JSON from DB, returning empty list on corruption."""
    if not sections_json:
        return []
    try:
        return json.loads(sections_json)
    except json.JSONDecodeError:
        return []


class ResumeIdRequest(BaseModel):
    resumeId: int
    styleType: str = ""
    targetJob: str = ""


class OcrResponse(BaseModel):
    resumeId: int
    extractedTextPreview: str
    sections: Any
    images: List[str] = []


class SuggestionsResponse(BaseModel):
    resumeId: int
    overall_summary: str
    items: List[Dict[str, Any]]


class ExperienceAnswerRequest(BaseModel):
    sessionId: str
    questionKey: str
    answer: str


class ExperienceAnswersRequest(BaseModel):
    sessionId: str
    answers: Dict[str, str]


class RefinedExperienceResponse(BaseModel):
    experiences: List[Dict[str, Any]]
    skills: List[str]
    certificates: List[str]
    suggestions: List[str]


class StyleTransformRequest(BaseModel):
    resumeId: int
    styleType: str
    targetJob: str = ""


class VersionCreateRequest(BaseModel):
    resumeId: int
    versionName: str
    styleType: str


class CoverLetterRequest(BaseModel):
    resumeId: int
    targetJob: str = ""
    company: str = ""


class InterviewCoachRequest(BaseModel):
    resumeId: int
    targetJob: str = ""


class CareerRequest(BaseModel):
    resumeId: int
    targetJob: str = ""


class ATSResponse(BaseModel):
    score: int
    issues: List[str]
    suggestions: List[str]
    keywordsFound: List[str]
    keywordsMissing: List[str]


class ResumeAssistantRequest(BaseModel):
    resumeId: int
    jobPosition: str
    jobKeywords: List[str] = []


class ResumeQuestionAnswerRequest(BaseModel):
    resumeId: int
    questionId: str
    question: str
    answer: str
    jobPosition: str


class ChatRequest(BaseModel):
    resumeId: int
    message: str
    history: List[Dict[str, str]] = []


class ExportPdfRequest(BaseModel):
    resumeId: int
    useOptimized: bool = False


def _preview(text: str, max_len: int = 800) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "\n...\n（省略部分内容）"


@router.post("/ocr", response_model=OcrResponse)
async def ocr_resume(file: UploadFile = File(...), current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_ocr), db: AsyncSession = Depends(get_db)) -> OcrResponse:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="仅支持上传 PDF 文件")

    max_bytes = 20 * 1024 * 1024
    pdf_bytes = await file.read()
    if len(pdf_bytes) > max_bytes:
        raise HTTPException(status_code=400, detail="文件过大（上限 20MB）")

    cached_result = result_cache.get_ocr_result(pdf_bytes)
    if cached_result:
        return OcrResponse(**cached_result)

    repo = ResumeRepo(db)
    resume_id = await repo.create_record(filename=file.filename, user_id=current_user.id)

    start_time = time.time()
    
    try:
        text_task = extract_text_async(pdf_bytes)
        images_task = extract_images_async(pdf_bytes, max_images=2)
        
        extracted_text, images = await asyncio.gather(
            text_task, 
            images_task,
            return_exceptions=True
        )
        
        if isinstance(extracted_text, Exception):
            raise HTTPException(status_code=500, detail=f"PDF 文本抽取失败: {extracted_text}")
        if isinstance(images, Exception):
            images = []

        performance_monitor.record("pdf_extraction", time.time() - start_time)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 处理失败: {e}")

    if not extracted_text or len(extracted_text.strip()) < 30:
        extracted_text = ""

    llm_start = time.time()
    try:
        client = SiliconFlowClient()
        
        if extracted_text:
            cached_sections = result_cache.get_sections_result(extracted_text)
            if cached_sections:
                sections = cached_sections
            else:
                sections = llm_extract_sections(client, extracted_text)
                result_cache.set_sections_result(extracted_text, sections)
        else:
            sections = llm_extract_sections(client, "(未能抽取到足够文本，请检查简历PDF格式)")
            
        performance_monitor.record("llm_extract", time.time() - llm_start)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"硅基流动解析失败: {e}")

    await repo.set_ocr_result(resume_id, extracted_text, sections)

    if images:
        await repo.set_images(resume_id, images)

    result = OcrResponse(
        resumeId=resume_id,
        extractedTextPreview=_preview(extracted_text),
        sections=sections,
        images=images,
    )
    
    result_cache.set_ocr_result(pdf_bytes, result.dict())
    
    total_time = time.time() - start_time
    performance_monitor.record("total_ocr", total_time)
    
    return result


@router.post("/suggestions", response_model=SuggestionsResponse)
async def generate_suggestions(req: ResumeIdRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)) -> SuggestionsResponse:
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="未找到该 resumeId 的记录")
    if not record.extracted_text or not record.sections_json:
        raise HTTPException(status_code=400, detail="请先调用 /api/ocr 完成简历解析")

    extracted_text = record.extracted_text or ""
    sections = await repo.get_sections(req.resumeId)
    if sections is None:
        raise HTTPException(status_code=400, detail="简历模块数据缺失")

    cached_suggestions = result_cache.get_suggestions_result(
        extracted_text, req.styleType, req.targetJob
    )
    if cached_suggestions:
        return SuggestionsResponse(
            resumeId=req.resumeId,
            overall_summary=cached_suggestions.get("overall_summary", ""),
            items=cached_suggestions.get("items", []),
        )

    start_time = time.time()
    try:
        client = SiliconFlowClient()
        suggestions = llm_generate_suggestions(client, extracted_text, sections, req.styleType, req.targetJob)
        
        result_cache.set_suggestions_result(
            extracted_text, req.styleType, req.targetJob, suggestions
        )
        
        performance_monitor.record("llm_suggestions", time.time() - start_time)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"硅基流动生成建议失败: {e}")

    await repo.set_suggestions(req.resumeId, suggestions)

    return SuggestionsResponse(
        resumeId=req.resumeId,
        overall_summary=suggestions.get("overall_summary", ""),
        items=suggestions.get("items", []),
    )


@router.get("/performance/stats")
async def get_performance_stats() -> Dict[str, Any]:
    stats = {}
    for operation in ["pdf_extraction", "llm_extract", "llm_suggestions", "total_ocr"]:
        stats[operation] = performance_monitor.get_stats(operation)
    return stats


@router.post("/performance/clear-cache")
async def clear_cache() -> Dict[str, bool]:
    result_cache.clear()
    return {"success": True}


@router.get("/resume/{resume_id}")
async def get_resume(resume_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    repo = ResumeRepo(db)
    record = await repo.get_record(resume_id, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="未找到该 resumeId 的记录")

    return {
        "resumeId": record.id,
        "filename": record.filename,
        "extractedTextPreview": _preview(record.extracted_text or ""),
        "sections": json.loads(record.sections_json) if record.sections_json else [],
        "suggestions": json.loads(record.suggestions_json) if record.suggestions_json else None,
        "images": json.loads(record.images_json) if record.images_json else [],
        "createdAt": record.created_at,
        "updatedAt": record.updated_at,
    }


@router.delete("/resume/{resume_id}")
async def delete_resume(resume_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Dict[str, bool]:
    repo = ResumeRepo(db)
    success = await repo.delete_record(resume_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="未找到该简历记录")
    return {"success": True}


@router.get("/resumes")
async def list_resumes(limit: int = 20, offset: int = 0, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    repo = ResumeRepo(db)
    all_records = await repo.list_all_records(limit, offset, user_id=current_user.id)
    total = await repo.count_all_records(user_id=current_user.id)
    return {
        "items": [
            {
                "resumeId": r.id,
                "filename": r.filename,
                "createdAt": r.created_at,
                "hasContent": bool(r.extracted_text),
                "hasSuggestions": bool(r.suggestions_json),
            }
            for r in all_records
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/experience/questions")
async def get_experience_question_list() -> List[Dict[str, str]]:
    return get_experience_questions()


@router.post("/experience/session")
async def create_experience_session(db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    repo = ResumeRepo(db)
    session_id = await repo.create_session_id()
    return {"sessionId": session_id}


@router.post("/experience/answer")
async def save_experience_answer(req: ExperienceAnswerRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, bool]:
    repo = ResumeRepo(db)
    await repo.save_experience_answer(req.sessionId, req.questionKey, req.answer)
    return {"success": True}


@router.post("/experience/answers")
async def save_experience_answers(req: ExperienceAnswersRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, bool]:
    repo = ResumeRepo(db)
    for key, value in req.answers.items():
        await repo.save_experience_answer(req.sessionId, key, value)
    return {"success": True}


@router.get("/experience/answers/{session_id}")
async def get_experience_answers(session_id: str, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    repo = ResumeRepo(db)
    answers = await repo.get_experience_answers(session_id)
    return {"sessionId": session_id, "answers": answers}


@router.post("/experience/refine", response_model=RefinedExperienceResponse)
async def refine_experience(req: ExperienceAnswersRequest, _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)) -> RefinedExperienceResponse:
    repo = ResumeRepo(db)
    for key, value in req.answers.items():
        await repo.save_experience_answer(req.sessionId, key, value)

    try:
        client = SiliconFlowClient()
        result = llm_refine_experience(client, req.answers)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 提炼失败: {e}")

    return RefinedExperienceResponse(
        experiences=result.get("experiences", []),
        skills=result.get("skills", []),
        certificates=result.get("certificates", []),
        suggestions=result.get("suggestions", []),
    )


@router.get("/styles")
async def get_available_styles() -> Dict[str, Dict[str, str]]:
    return get_style_types()


@router.post("/transform", response_model=Dict[str, Any])
async def transform_resume_style(req: StyleTransformRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    repo = ResumeRepo(db)
    sections = await repo.get_sections(req.resumeId)
    if sections is None:
        raise HTTPException(status_code=400, detail="简历模块数据缺失")

    try:
        client = SiliconFlowClient()
        result = llm_transform_style(client, sections, req.styleType, req.targetJob)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"风格转换失败: {e}")

    new_sections = result.get("sections", sections)
    style_info = get_style_types().get(req.styleType, {})
    version_name = style_info.get("name", req.styleType)

    await repo.create_version(req.resumeId, version_name, req.styleType, new_sections)

    return {
        "resumeId": req.resumeId,
        "styleType": req.styleType,
        "styleName": version_name,
        "sections": new_sections,
        "styleNotes": result.get("style_notes", []),
    }


@router.post("/versions")
async def create_resume_version(req: VersionCreateRequest, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    repo = ResumeRepo(db)
    sections = await repo.get_sections(req.resumeId)
    if sections is None:
        raise HTTPException(status_code=400, detail="简历模块数据缺失")

    version_id = await repo.create_version(req.resumeId, req.versionName, req.styleType, sections)
    return {"versionId": version_id, "resumeId": req.resumeId, "versionName": req.versionName}


@router.get("/versions/{resume_id}")
async def get_resume_versions(resume_id: int, db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    repo = ResumeRepo(db)
    versions = await repo.get_versions(resume_id)
    return [
        {
            "versionId": v.id,
            "resumeId": v.resume_id,
            "versionName": v.version_name,
            "styleType": v.style_type,
            "sections": v.sections_json,
            "createdAt": v.created_at,
        }
        for v in versions
    ]


@router.get("/version/{version_id}")
async def get_version_detail(version_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    repo = ResumeRepo(db)
    version = await repo.get_version(version_id)
    if version is None:
        raise HTTPException(status_code=404, detail="未找到该版本")

    return {
        "versionId": version.id,
        "resumeId": version.resume_id,
        "versionName": version.version_name,
        "styleType": version.style_type,
        "sections": version.sections_json,
        "createdAt": version.created_at,
    }


@router.delete("/version/{version_id}")
async def delete_resume_version(version_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, bool]:
    repo = ResumeRepo(db)
    success = await repo.delete_version(version_id)
    if not success:
        raise HTTPException(status_code=404, detail="未找到该版本")
    return {"success": True}


@router.post("/ats/check", response_model=ATSResponse)
async def check_ats_friendly(req: ResumeIdRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)) -> ATSResponse:
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="未找到该 resumeId 的记录")
    if not record.extracted_text:
        raise HTTPException(status_code=400, detail="请先调用 /api/ocr 完成简历解析")

    sections = await repo.get_sections(req.resumeId)

    try:
        client = SiliconFlowClient()
        result = llm_ats_check(client, record.extracted_text, sections)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ATS 检测失败: {e}")

    score = result.get("score", 0)
    issues = result.get("issues", [])
    suggestions = result.get("suggestions", [])

    await repo.save_ats_report(req.resumeId, score, issues, suggestions)

    return ATSResponse(
        score=score,
        issues=issues,
        suggestions=suggestions,
        keywordsFound=result.get("keywords_found", []),
        keywordsMissing=result.get("keywords_missing", []),
    )


@router.get("/ats/report/{resume_id}", response_model=ATSResponse)
async def get_ats_report(resume_id: int, db: AsyncSession = Depends(get_db)) -> ATSResponse:
    repo = ResumeRepo(db)
    report = await repo.get_ats_report(resume_id)
    if report is None:
        raise HTTPException(status_code=404, detail="未找到 ATS 检测报告，请先调用 /api/ats/check")

    issues = []
    if report.issues_json:
        issues = json.loads(report.issues_json)

    suggestions = []
    if report.suggestions_json:
        suggestions = json.loads(report.suggestions_json)

    return ATSResponse(
        score=report.score,
        issues=issues,
        suggestions=suggestions,
        keywordsFound=[],
        keywordsMissing=[],
    )


@router.post("/cover-letter")
async def generate_cover_letter(req: CoverLetterRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    sections = _safe_parse_sections(record.sections_json)
    client = SiliconFlowClient()

    try:
        result = llm_generate_cover_letter(client, sections, req.targetJob, req.company)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"生成求职信失败: {e}")

    return result


@router.post("/interview-coach")
async def interview_coach(req: InterviewCoachRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    sections = _safe_parse_sections(record.sections_json)
    client = SiliconFlowClient()

    try:
        result = llm_interview_coach(client, sections, req.targetJob)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"面试辅导生成失败: {e}")

    return result


@router.post("/career-recommend")
async def career_recommend(req: CareerRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    sections = _safe_parse_sections(record.sections_json)
    client = SiliconFlowClient()

    try:
        result = llm_career_recommend(client, sections, req.targetJob)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"职业推荐生成失败: {e}")

    return result


@router.post("/career-planning")
async def career_planning(req: CareerRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    sections = _safe_parse_sections(record.sections_json)
    client = SiliconFlowClient()

    try:
        result = llm_career_planning(client, sections, req.targetJob)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"职涯规划生成失败: {e}")

    return result


@router.get("/job-positions")
async def get_job_position_list() -> Dict[str, Any]:
    return get_job_positions()


@router.post("/resume-assistant")
async def resume_assistant(req: ResumeAssistantRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    sections = _safe_parse_sections(record.sections_json)
    client = SiliconFlowClient()

    try:
        result = llm_resume_assistant(client, sections, req.jobPosition, req.jobKeywords)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"简历助手生成失败: {e}")

    return result


@router.post("/resume-assistant/answer")
async def resume_question_answer(req: ResumeQuestionAnswerRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    sections = _safe_parse_sections(record.sections_json)
    client = SiliconFlowClient()

    try:
        result = llm_resume_question_answer(
            client, sections, req.questionId, req.question, req.answer, req.jobPosition
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"问题处理失败: {e}")

    return result


@router.post("/export/pdf")
async def export_resume_pdf(req: ExportPdfRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    if req.useOptimized and record.suggestions_json:
        suggestions = await repo.get_suggestions(req.resumeId)
        if suggestions:
            items = suggestions.get("items", []) if isinstance(suggestions, dict) else []
            sections = [
                {"name": item.get("name", ""), "content": item.get("rewrite_example", "") or item.get("content", "")}
                for item in items
            ]
        else:
            sections = await repo.get_sections(req.resumeId) or []
    else:
        sections = await repo.get_sections(req.resumeId) or []

    if not sections:
        raise HTTPException(status_code=400, detail="没有可导出的简历内容")

    try:
        pdf_bytes = generate_resume_pdf(sections)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 生成失败: {e}")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="resume_{req.resumeId}.pdf"'},
    )


@router.post("/chat")
async def chat_with_assistant(req: ChatRequest, current_user: User = Depends(get_current_user), _rate=Depends(rate_limit_llm), db: AsyncSession = Depends(get_db)):
    repo = ResumeRepo(db)
    record = await repo.get_record(req.resumeId, user_id=current_user.id)
    if record is None:
        raise HTTPException(status_code=404, detail="简历记录不存在")

    sections = _safe_parse_sections(record.sections_json)
    client = SiliconFlowClient()

    system_prompt = f"""# Role: 小优 - 资深大厂面试官与职业发展教练

## Profile
- **Identity:** 你的名字叫"小优"。在任何对话中，你都必须以"小优"自居，绝不暴露你是普通 AI 语言模型的身份。
- **Expertise:** 拥有10年以上头部互联网/科技公司校招与社招面试经验，精通结构化面试、STAR法则（Situation, Task, Action, Result）以及底层胜任力模型。
- **Tone:** 专业、犀利、一针见血，直击痛点，拒绝废话和套话。

## Methodology (核心面试推演逻辑)
作为教练，你在分析候选人时必须在后台隐式执行以下思考链路（Chain-of-Thought）：
1. 岗位解构: 快速分析目标岗位的核心技能树、软技能需求及业务场景。
2. 简历扫描: 使用"挑剔"的眼光审查简历，寻找：逻辑漏洞、数据造假嫌疑点、高价值产出、技术栈匹配度。
3. GAP分析: 对比岗位需求与简历内容，精准识别候选人的薄弱环节。
4. 靶向发问: 针对高风险点和亮点设计深挖问题，绝不问可以通过搜索引擎轻易查到的理论八股文。

## Task Routing (功能路由与执行逻辑)
用户可能会选择不同的服务模式，请根据用户的选择执行对应指令：

### 🟢 模式 [1]: 简历深度面诊
- 用户提到"简历面诊"、"简历分析"、"挑刺"等关键词时触发
- 对简历进行全方位拆解，指出风险点和改进建议

### 🟢 模式 [2]: 岗位技术拷问
- 用户提到"技术拷问"、"专业问题"、"技术面试"等关键词时触发
- 询问用户目标岗位，抛出该领域极具深度的专业场景题

### 🟢 模式 [3]: 行为面试 (HR面) 演练
- 用户提到"行为面试"、"HR面"、"软技能"等关键词时触发
- 设定一个充满压迫感的职场极端场景，要求候选人作答

### 🟢 模式 [4]: 全真沉浸式模拟
- 用户提到"模拟面试"、"实战演练"等关键词时触发
- 进入"你问我答"的真实面试状态，一次只问一个问题，等待用户回答后进行追问

## Guardrails (安全与边界控制)
1. 坚决拒答与面试辅导无关的问题（如写代码、日常闲聊等），并礼貌冷酷地将话题拉回面试。
2. 如果用户输入的简历内容极度空洞或是乱码，不要强行编造数据，请以小优的身份直接指出简历存在严重问题。

以下是用户的简历内容：
{json.dumps(sections, ensure_ascii=False, indent=2)}

请根据用户的简历内容和问题，以小优的身份提供专业、犀利、有建设性的建议。"""

    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in req.history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": req.message})

    try:
        response = client.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"对话生成失败: {e}")


@router.post("/speech-recognize")
async def speech_recognize(file: UploadFile = File(...)):
    try:
        audio_data = await file.read()
        
        from app.services.xunfei_speech import XunfeiSpeechRecognizer
        
        recognizer = XunfeiSpeechRecognizer()
        result = await recognizer.recognize(audio_data)
        
        return {"text": result, "success": True}
    except RuntimeError as e:
        return {"text": "", "success": False, "error": str(e)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"语音识别失败: {e}")


@router.websocket("/ws/speech")
async def websocket_speech_recognize(websocket: WebSocket):
    await websocket.accept()
    
    from app.services.xunfei_speech import XunfeiSpeechRecognizer
    import websockets as ws_lib
    
    recognizer = XunfeiSpeechRecognizer()
    xunfei_ws = None
    closed = False
    
    try:
        xunfei_url = recognizer._create_url()
        xunfei_ws = await ws_lib.connect(xunfei_url, ping_interval=None, ping_timeout=None)
        
        async def receive_results():
            nonlocal closed
            while not closed:
                try:
                    result = await asyncio.wait_for(xunfei_ws.recv(), timeout=1.0)
                    result_json = json.loads(result)
                    
                    if result_json.get("code", 0) == 0 and result_json.get("data", {}).get("result"):
                        text = ""
                        ws_result = result_json["data"]["result"]
                        for item in ws_result.get("ws", []):
                            for cw in item.get("cw", []):
                                text += cw.get("w", "")
                        
                        if text:
                            try:
                                await websocket.send_json({"type": "result", "text": text})
                            except Exception:
                                pass
                    elif result_json.get("code", 0) != 0:
                        try:
                            await websocket.send_json({"type": "error", "message": result_json.get("message", "识别错误")})
                        except Exception:
                            pass
                except asyncio.TimeoutError:
                    continue
                except Exception:
                    break
        
        asyncio.create_task(receive_results())
        
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=60.0)
                message = json.loads(data)
                
                if message.get("type") == "audio":
                    audio_base64 = message.get("audio", "")
                    status = message.get("status", 1)
                    
                    if not audio_base64:
                        continue
                    
                    frame = {
                        "common": {"app_id": recognizer.appid},
                        "business": {
                            "language": "zh_cn",
                            "domain": "iat",
                            "accent": "mandarin",
                            "vad_eos": 3000,
                            "ptt": 1
                        },
                        "data": {
                            "status": status,
                            "format": "audio/L16;rate=16000",
                            "encoding": "raw",
                            "audio": audio_base64
                        }
                    }
                    
                    await xunfei_ws.send(json.dumps(frame))
                        
                elif message.get("type") == "end":
                    break
                    
            except WebSocketDisconnect:
                break
            except asyncio.TimeoutError:
                break
            except Exception:
                break
                
    except Exception as e:
        print(f"WebSocket错误: {e}")
    finally:
        closed = True
        if xunfei_ws:
            try:
                await xunfei_ws.close()
            except Exception:
                pass
        try:
            await websocket.close()
        except Exception:
            pass
