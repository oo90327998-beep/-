import json
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from supabase import AsyncClient


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


class ResumeRepo:
    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    # ── resume_records ──────────────────────────────────────────────

    async def create_record(self, filename: str, user_id: Optional[int] = None) -> int:
        data = {"filename": filename}
        if user_id is not None:
            data["user_id"] = user_id
        r = await self.client.table("resume_records").insert(data).execute()
        return r.data[0]["id"]

    async def delete_record(self, resume_id: int, user_id: Optional[int] = None) -> bool:
        await self.client.table("resume_versions").delete().eq("resume_id", resume_id).execute()
        await self.client.table("ats_reports").delete().eq("resume_id", resume_id).execute()
        query = self.client.table("resume_records").delete().eq("id", resume_id)
        if user_id is not None:
            query = query.eq("user_id", user_id)
        r = await query.execute()
        return len(r.data) > 0 if r.data else False

    async def set_ocr_result(self, resume_id: int, extracted_text: str, sections: Any) -> None:
        data = {
            "extracted_text": extracted_text,
            "sections_json": json.dumps(sections, ensure_ascii=False),
        }
        await self.client.table("resume_records").update(data).eq("id", resume_id).execute()

    async def set_suggestions(self, resume_id: int, suggestions: Any) -> None:
        data = {"suggestions_json": json.dumps(suggestions, ensure_ascii=False)}
        await self.client.table("resume_records").update(data).eq("id", resume_id).execute()

    async def set_images(self, resume_id: int, images: List[str]) -> None:
        data = {"images_json": json.dumps(images, ensure_ascii=False)}
        await self.client.table("resume_records").update(data).eq("id", resume_id).execute()

    async def get_images(self, resume_id: int) -> List[str]:
        r = await self.client.table("resume_records").select("images_json").eq("id", resume_id).maybe_single().execute()
        if not r.data or not r.data.get("images_json"):
            return []
        return json.loads(r.data["images_json"])

    async def get_record(self, resume_id: int, user_id: Optional[int] = None) -> Optional[ResumeRecord]:
        query = self.client.table("resume_records").select("*").eq("id", resume_id)
        if user_id is not None:
            query = query.eq("user_id", user_id)
        r = await query.maybe_single().execute()
        return self._row_to_record(r.data) if r.data else None

    async def get_sections(self, resume_id: int) -> Optional[Any]:
        r = await self.client.table("resume_records").select("sections_json").eq("id", resume_id).maybe_single().execute()
        if not r.data or not r.data.get("sections_json"):
            return None
        return json.loads(r.data["sections_json"])

    async def get_extracted_text(self, resume_id: int) -> Optional[str]:
        r = await self.client.table("resume_records").select("extracted_text").eq("id", resume_id).maybe_single().execute()
        return None if not r.data else r.data.get("extracted_text")

    async def get_suggestions(self, resume_id: int) -> Optional[Any]:
        r = await self.client.table("resume_records").select("suggestions_json").eq("id", resume_id).maybe_single().execute()
        if not r.data or not r.data.get("suggestions_json"):
            return None
        return json.loads(r.data["suggestions_json"])

    async def list_all_records(
        self, limit: int = 20, offset: int = 0, user_id: Optional[int] = None
    ) -> List[ResumeRecord]:
        query = self.client.table("resume_records").select("*", count="exact") \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1)
        if user_id is not None:
            query = query.eq("user_id", user_id)
        r = await query.execute()
        return [self._row_to_record(row) for row in (r.data or [])]

    async def count_all_records(self, user_id: Optional[int] = None) -> int:
        query = self.client.table("resume_records").select("id", count="exact")
        if user_id is not None:
            query = query.eq("user_id", user_id)
        r = await query.execute()
        return r.count or 0

    # ── resume_versions ─────────────────────────────────────────────

    async def create_version(
        self, resume_id: int, version_name: str, style_type: str, sections: Any
    ) -> int:
        data = {
            "resume_id": resume_id,
            "version_name": version_name,
            "style_type": style_type,
            "sections_json": json.dumps(sections, ensure_ascii=False),
        }
        r = await self.client.table("resume_versions").insert(data).execute()
        return r.data[0]["id"]

    async def get_versions(self, resume_id: int) -> List[ResumeVersion]:
        r = await self.client.table("resume_versions").select("*") \
            .eq("resume_id", resume_id) \
            .order("created_at", desc=True) \
            .execute()
        return [self._row_to_version(row) for row in (r.data or [])]

    async def get_version(self, version_id: int) -> Optional[ResumeVersion]:
        r = await self.client.table("resume_versions").select("*").eq("id", version_id).maybe_single().execute()
        return self._row_to_version(r.data) if r.data else None

    async def delete_version(self, version_id: int) -> bool:
        r = await self.client.table("resume_versions").delete().eq("id", version_id).execute()
        return len(r.data) > 0 if r.data else False

    # ── experience_answers ──────────────────────────────────────────

    async def save_experience_answer(self, session_id: str, question_key: str, answer_text: str) -> None:
        data = {
            "session_id": session_id,
            "question_key": question_key,
            "answer_text": answer_text,
        }
        await self.client.table("experience_answers").upsert(data).execute()

    async def get_experience_answers(self, session_id: str) -> Dict[str, str]:
        r = await self.client.table("experience_answers").select("question_key,answer_text") \
            .eq("session_id", session_id).execute()
        return {row["question_key"]: row["answer_text"] or "" for row in (r.data or [])}

    async def create_session_id(self) -> str:
        return str(uuid.uuid4())

    # ── ats_reports ─────────────────────────────────────────────────

    async def save_ats_report(
        self, resume_id: int, score: int, issues: List[str], suggestions: List[str]
    ) -> int:
        data = {
            "resume_id": resume_id,
            "score": score,
            "issues_json": json.dumps(issues, ensure_ascii=False),
            "suggestions_json": json.dumps(suggestions, ensure_ascii=False),
        }
        r = await self.client.table("ats_reports").insert(data).execute()
        return r.data[0]["id"]

    async def get_ats_report(self, resume_id: int) -> Optional[ATSReport]:
        r = await self.client.table("ats_reports").select("*") \
            .eq("resume_id", resume_id) \
            .order("created_at", desc=True) \
            .limit(1) \
            .maybe_single() \
            .execute()
        return self._row_to_ats(r.data) if r.data else None

    # ── users ───────────────────────────────────────────────────────

    async def create_user(
        self, username: str, email: str, password_hash: str, nickname: Optional[str] = None
    ) -> int:
        data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "nickname": nickname or username,
        }
        r = await self.client.table("users").insert(data).execute()
        return r.data[0]["id"]

    _ALLOWED_USER_FIELDS = {"id", "username", "email"}

    async def _get_user_by_field(self, field: str, value) -> Optional[User]:
        if field not in self._ALLOWED_USER_FIELDS:
            raise ValueError(f"Invalid field: {field}")
        try:
            r = await self.client.table("users").select("*").eq(field, value).maybe_single().execute()
            if hasattr(r, 'data') and r.data:
                return self._row_to_user(r.data)
            return None
        except Exception as e:
            import logging
            logging.getLogger("resume-api").error(f"get_user_by_{field} failed: {e}")
            return None

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
        r = await self.client.table("users").update(values).eq("id", user_id).execute()
        return len(r.data) > 0 if r.data else False

    # ── helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _row_to_record(row: dict) -> ResumeRecord:
        return ResumeRecord(
            id=row["id"],
            filename=row["filename"],
            extracted_text=row.get("extracted_text"),
            sections_json=row.get("sections_json"),
            suggestions_json=row.get("suggestions_json"),
            images_json=row.get("images_json"),
            user_id=row.get("user_id"),
            created_at=str(row.get("created_at", "")),
            updated_at=str(row.get("updated_at", "")),
        )

    @staticmethod
    def _row_to_version(row: dict) -> ResumeVersion:
        return ResumeVersion(
            id=row["id"],
            resume_id=row["resume_id"],
            version_name=row["version_name"],
            style_type=row.get("style_type", "standard"),
            sections_json=row.get("sections_json"),
            created_at=str(row.get("created_at", "")),
        )

    @staticmethod
    def _row_to_ats(row: dict) -> ATSReport:
        return ATSReport(
            id=row["id"],
            resume_id=row["resume_id"],
            score=row["score"],
            issues_json=row.get("issues_json"),
            suggestions_json=row.get("suggestions_json"),
            created_at=str(row.get("created_at", "")),
        )

    @staticmethod
    def _row_to_user(row: dict) -> User:
        return User(
            id=row["id"],
            username=row["username"],
            email=row["email"],
            password_hash=row["password_hash"],
            nickname=row.get("nickname"),
            avatar=row.get("avatar"),
            created_at=str(row.get("created_at", "")),
            updated_at=str(row.get("updated_at", "")),
        )
