from datetime import datetime

from sqlalchemy import BigInteger, Identity, String, Text, Integer, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import DateTime


class Base(DeclarativeBase):
    pass


class ResumeRecord(Base):
    __tablename__ = "resume_records"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    sections_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    images_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    versions: Mapped[list["ResumeVersion"]] = relationship(back_populates="resume", cascade="all, delete-orphan")
    ats_reports: Mapped[list["ATSReport"]] = relationship(back_populates="resume", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_resume_records_created_at", "created_at"),
    )


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    resume_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("resume_records.id"), nullable=False)
    version_name: Mapped[str] = mapped_column(Text, nullable=False)
    style_type: Mapped[str] = mapped_column(String(50), default="standard", server_default="standard")
    sections_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    resume: Mapped["ResumeRecord"] = relationship(back_populates="versions")

    __table_args__ = (
        Index("idx_resume_versions_resume_id", "resume_id"),
    )


class ExperienceAnswer(Base):
    __tablename__ = "experience_answers"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    session_id: Mapped[str] = mapped_column(Text, nullable=False)
    question_key: Mapped[str] = mapped_column(Text, nullable=False)
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("session_id", "question_key", name="uq_experience_session_question"),
    )


class ATSReport(Base):
    __tablename__ = "ats_reports"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    resume_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("resume_records.id"), nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    issues_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestions_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    resume: Mapped["ResumeRecord"] = relationship(back_populates="ats_reports")

    __table_args__ = (
        Index("idx_ats_reports_resume_id", "resume_id"),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True)
    avatar: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("idx_users_username", "username"),
        Index("idx_users_email", "email"),
    )
