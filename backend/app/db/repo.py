import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy import select, insert, update, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ResumeRecord as ResumeRecordModel
from app.db.models import ResumeVersion as ResumeVersionModel
from app.db.models import ExperienceAnswer as ExperienceAnswerModel
from app.db.models import ATSReport as ATSReportModel
from app.db.models import User as UserModel


@dataclass
class ResumeRecord:
    id: int
    filename: str
    extracted_text: Optional[str]
    sections_json: Optional[str]
    suggestions_json: Optional[str]
    images_json: Optional[str]
    user_id: Optional[int]
    created_at: str
    updated_at: str


@dataclass
class ResumeVersion:
    id: int
    resume_id: int
    version_name: str
    style_type: str
    sections_json: Optional[str]
    created_at: str


@dataclass
class ATSReport:
    id: int
    resume_id: int
    score: int
    issues_json: Optional[str]
    suggestions_json: Optional[str]
    created_at: str


@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    nickname: Optional[str]
    avatar: Optional[str]
    created_at: str
    updated_at: str


def _model_to_record(m: ResumeRecordModel) -> ResumeRecord:
    return ResumeRecord(
        id=m.id,
        filename=m.filename,
        extracted_text=m.extracted_text,
        sections_json=m.sections_json,
        suggestions_json=m.suggestions_json,
        images_json=m.images_json,
        user_id=m.user_id,
        created_at=str(m.created_at),
        updated_at=str(m.updated_at),
    )


def _model_to_version(m: ResumeVersionModel) -> ResumeVersion:
    return ResumeVersion(
        id=m.id,
        resume_id=m.resume_id,
        version_name=m.version_name,
        style_type=m.style_type,
        sections_json=m.sections_json,
        created_at=str(m.created_at),
    )


def _model_to_ats(m: ATSReportModel) -> ATSReport:
    return ATSReport(
        id=m.id,
        resume_id=m.resume_id,
        score=m.score,
        issues_json=m.issues_json,
        suggestions_json=m.suggestions_json,
        created_at=str(m.created_at),
    )


def _model_to_user(m: UserModel) -> User:
    return User(
        id=m.id,
        username=m.username,
        email=m.email,
        password_hash=m.password_hash,
        nickname=m.nickname,
        avatar=m.avatar,
        created_at=str(m.created_at),
        updated_at=str(m.updated_at),
    )


class ResumeRepo:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── resume_records ──────────────────────────────────────────────

    async def create_record(self, filename: str, user_id: Optional[int] = None) -> int:
        stmt = (
            insert(ResumeRecordModel)
            .values(filename=filename, user_id=user_id)
            .returning(ResumeRecordModel.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def delete_record(self, resume_id: int, user_id: Optional[int] = None) -> bool:
        await self.db.execute(
            delete(ResumeVersionModel).where(ResumeVersionModel.resume_id == resume_id)
        )
        await self.db.execute(
            delete(ATSReportModel).where(ATSReportModel.resume_id == resume_id)
        )
        stmt = delete(ResumeRecordModel).where(ResumeRecordModel.id == resume_id)
        if user_id is not None:
            stmt = stmt.where(ResumeRecordModel.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    async def set_ocr_result(self, resume_id: int, extracted_text: str, sections: Any) -> None:
        sections_json = json.dumps(sections, ensure_ascii=False)
        stmt = (
            update(ResumeRecordModel)
            .where(ResumeRecordModel.id == resume_id)
            .values(extracted_text=extracted_text, sections_json=sections_json)
        )
        await self.db.execute(stmt)

    async def set_suggestions(self, resume_id: int, suggestions: Any) -> None:
        suggestions_json = json.dumps(suggestions, ensure_ascii=False)
        stmt = (
            update(ResumeRecordModel)
            .where(ResumeRecordModel.id == resume_id)
            .values(suggestions_json=suggestions_json)
        )
        await self.db.execute(stmt)

    async def set_images(self, resume_id: int, images: List[str]) -> None:
        images_json = json.dumps(images, ensure_ascii=False)
        stmt = (
            update(ResumeRecordModel)
            .where(ResumeRecordModel.id == resume_id)
            .values(images_json=images_json)
        )
        await self.db.execute(stmt)

    async def get_images(self, resume_id: int) -> List[str]:
        record = await self.get_record(resume_id)
        if record is None or not record.images_json:
            return []
        return json.loads(record.images_json)

    async def get_record(self, resume_id: int, user_id: Optional[int] = None) -> Optional[ResumeRecord]:
        stmt = select(ResumeRecordModel).where(ResumeRecordModel.id == resume_id)
        if user_id is not None:
            stmt = stmt.where(ResumeRecordModel.user_id == user_id)
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        return _model_to_record(row) if row else None

    async def get_sections(self, resume_id: int) -> Optional[Any]:
        record = await self.get_record(resume_id)
        if record is None or not record.sections_json:
            return None
        return json.loads(record.sections_json)

    async def get_extracted_text(self, resume_id: int) -> Optional[str]:
        record = await self.get_record(resume_id)
        return None if record is None else record.extracted_text

    async def get_suggestions(self, resume_id: int) -> Optional[Any]:
        record = await self.get_record(resume_id)
        if record is None or not record.suggestions_json:
            return None
        return json.loads(record.suggestions_json)

    async def list_all_records(
        self, limit: int = 20, offset: int = 0, user_id: Optional[int] = None
    ) -> List[ResumeRecord]:
        stmt = select(ResumeRecordModel).order_by(desc(ResumeRecordModel.created_at))
        if user_id is not None:
            stmt = stmt.where(ResumeRecordModel.user_id == user_id)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.db.execute(stmt)
        return [_model_to_record(m) for m in result.scalars().all()]

    async def count_all_records(self, user_id: Optional[int] = None) -> int:
        stmt = select(func.count()).select_from(ResumeRecordModel)
        if user_id is not None:
            stmt = stmt.where(ResumeRecordModel.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    # ── resume_versions ─────────────────────────────────────────────

    async def create_version(
        self, resume_id: int, version_name: str, style_type: str, sections: Any
    ) -> int:
        sections_json = json.dumps(sections, ensure_ascii=False)
        stmt = (
            insert(ResumeVersionModel)
            .values(
                resume_id=resume_id,
                version_name=version_name,
                style_type=style_type,
                sections_json=sections_json,
            )
            .returning(ResumeVersionModel.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_versions(self, resume_id: int) -> List[ResumeVersion]:
        stmt = (
            select(ResumeVersionModel)
            .where(ResumeVersionModel.resume_id == resume_id)
            .order_by(desc(ResumeVersionModel.created_at))
        )
        result = await self.db.execute(stmt)
        return [_model_to_version(m) for m in result.scalars().all()]

    async def get_version(self, version_id: int) -> Optional[ResumeVersion]:
        stmt = select(ResumeVersionModel).where(ResumeVersionModel.id == version_id)
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        return _model_to_version(row) if row else None

    async def delete_version(self, version_id: int) -> bool:
        stmt = delete(ResumeVersionModel).where(ResumeVersionModel.id == version_id)
        result = await self.db.execute(stmt)
        return result.rowcount > 0

    # ── experience_answers ──────────────────────────────────────────

    async def save_experience_answer(self, session_id: str, question_key: str, answer_text: str) -> None:
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        stmt = pg_insert(ExperienceAnswerModel).values(
            session_id=session_id,
            question_key=question_key,
            answer_text=answer_text,
        ).on_conflict_do_update(
            index_elements=["session_id", "question_key"],
            set_=dict(answer_text=answer_text),
        )
        await self.db.execute(stmt)

    async def get_experience_answers(self, session_id: str) -> Dict[str, str]:
        stmt = select(ExperienceAnswerModel).where(
            ExperienceAnswerModel.session_id == session_id
        )
        result = await self.db.execute(stmt)
        rows = result.scalars().all()
        return {row.question_key: row.answer_text or "" for row in rows}

    async def create_session_id(self) -> str:
        return str(uuid.uuid4())

    # ── ats_reports ─────────────────────────────────────────────────

    async def save_ats_report(
        self, resume_id: int, score: int, issues: List[str], suggestions: List[str]
    ) -> int:
        issues_json = json.dumps(issues, ensure_ascii=False)
        suggestions_json = json.dumps(suggestions, ensure_ascii=False)
        stmt = (
            insert(ATSReportModel)
            .values(
                resume_id=resume_id,
                score=score,
                issues_json=issues_json,
                suggestions_json=suggestions_json,
            )
            .returning(ATSReportModel.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def get_ats_report(self, resume_id: int) -> Optional[ATSReport]:
        stmt = (
            select(ATSReportModel)
            .where(ATSReportModel.resume_id == resume_id)
            .order_by(desc(ATSReportModel.created_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        return _model_to_ats(row) if row else None

    # ── users ───────────────────────────────────────────────────────

    async def create_user(
        self, username: str, email: str, password_hash: str, nickname: Optional[str] = None
    ) -> int:
        stmt = (
            insert(UserModel)
            .values(
                username=username,
                email=email,
                password_hash=password_hash,
                nickname=nickname or username,
            )
            .returning(UserModel.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    _ALLOWED_USER_FIELDS = {"id", "username", "email"}

    async def _get_user_by_field(self, field: str, value) -> Optional[User]:
        if field not in self._ALLOWED_USER_FIELDS:
            raise ValueError(f"Invalid field: {field}")
        col = getattr(UserModel, field)
        stmt = select(UserModel).where(col == value)
        result = await self.db.execute(stmt)
        row = result.scalar_one_or_none()
        return _model_to_user(row) if row else None

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self._get_user_by_field("id", user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        return await self._get_user_by_field("username", username)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self._get_user_by_field("email", email)

    _ALLOWED_UPDATE_COLUMNS = {"nickname", "avatar"}

    async def update_user(
        self, user_id: int, nickname: Optional[str] = None, avatar: Optional[str] = None
    ) -> bool:
        values = {}
        if nickname is not None:
            values["nickname"] = nickname
        if avatar is not None:
            values["avatar"] = avatar
        if not values:
            return False

        for col_name in values:
            if col_name not in self._ALLOWED_UPDATE_COLUMNS:
                raise ValueError(f"Invalid column: {col_name}")

        stmt = (
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(**values)
        )
        result = await self.db.execute(stmt)
        return result.rowcount > 0
