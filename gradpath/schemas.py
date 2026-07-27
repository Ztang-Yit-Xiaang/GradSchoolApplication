"""Canonical data models, schemas, and validation helpers for GradPath Planner."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

SCHEMA_VERSION = "2.0"

AdmissionMode = Literal[
    "committee_program",
    "hybrid_committee_faculty",
    "direct_pi_sponsor",
    "rotation_or_umbrella",
    "research_thesis_ms",
    "coursework_professional_ms",
    "unknown_needs_review",
]

ContactPolicy = Literal["required", "recommended", "optional", "discouraged", "unknown"]
AdvisorBinding = Literal[
    "before_application", "at_admission", "after_admission", "after_rotations", "unknown"
]
FundingOwner = Literal["program", "pi", "mixed", "self_funded", "unknown"]
PortfolioCategory = Literal[
    "Lottery",
    "Reach",
    "Core/Target",
    "Lower-variance high-fit",
    "Research MS backup",
    "Professional/coursework MS backup",
    "Needs more evidence",
    "Archive",
]
ConfidenceLevel = Literal["High", "Medium", "Low", "Unknown"]
ReviewStatus = Literal["verified", "needs_review", "unverified"]


@dataclass
class EvidenceItem:
    source_url: str = ""
    page_title: str = ""
    retrieval_date: str = ""
    evidence_excerpt: str = ""
    confidence: ConfidenceLevel = "Low"
    review_status: ReviewStatus = "unverified"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> EvidenceItem:
        if not data or not isinstance(data, dict):
            return cls()
        return cls(
            source_url=str(data.get("source_url", "")),
            page_title=str(data.get("page_title", "")),
            retrieval_date=str(data.get("retrieval_date", "")),
            evidence_excerpt=str(data.get("evidence_excerpt", "")),
            confidence=data.get("confidence", "Low"),
            review_status=data.get("review_status", "unverified"),
        )


@dataclass
class AdmissionModeModel:
    application_mode: AdmissionMode = "unknown_needs_review"
    mode_evidence: str = ""
    mode_source_url: str = ""
    mode_confidence: ConfidenceLevel = "Low"
    contact_policy: ContactPolicy = "unknown"
    advisor_binding: AdvisorBinding = "unknown"
    funding_owner: FundingOwner = "unknown"
    faculty_names_requested: bool = False
    number_of_verified_fit_pis: int = 0
    number_of_backup_pis: int = 0
    primary_advisor_eligibility_verified: bool = False
    recruiting_status: str = "unknown"
    recruiting_evidence: str = ""
    recruiting_last_checked: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> AdmissionModeModel:
        if not data or not isinstance(data, dict):
            return cls()
        return cls(
            application_mode=data.get("application_mode", "unknown_needs_review"),
            mode_evidence=str(data.get("mode_evidence", "")),
            mode_source_url=str(data.get("mode_source_url", "")),
            mode_confidence=data.get("mode_confidence", "Low"),
            contact_policy=data.get("contact_policy", "unknown"),
            advisor_binding=data.get("advisor_binding", "unknown"),
            funding_owner=data.get("funding_owner", "unknown"),
            faculty_names_requested=bool(data.get("faculty_names_requested", False)),
            number_of_verified_fit_pis=int(data.get("number_of_verified_fit_pis", 0)),
            number_of_backup_pis=int(data.get("number_of_backup_pis", 0)),
            primary_advisor_eligibility_verified=bool(
                data.get("primary_advisor_eligibility_verified", False)
            ),
            recruiting_status=str(data.get("recruiting_status", "unknown")),
            recruiting_evidence=str(data.get("recruiting_evidence", "")),
            recruiting_last_checked=str(data.get("recruiting_last_checked", "")),
        )


@dataclass
class PeerFeedbackRecord:
    score: float = 2.5
    confidence: ConfidenceLevel = "Low"
    status: str = "No public evidence found"
    evidence_log: list[str] = field(default_factory=list)
    verified_facts: list[str] = field(default_factory=list)
    student_reports: list[str] = field(default_factory=list)
    anonymous_claims: list[str] = field(default_factory=list)
    manual_review_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> PeerFeedbackRecord:
        if not data or not isinstance(data, dict):
            return cls()
        return cls(
            score=float(data.get("score", 2.5)),
            confidence=data.get("confidence", "Low"),
            status=str(data.get("status", "No public evidence found")),
            evidence_log=list(data.get("evidence_log", [])),
            verified_facts=list(data.get("verified_facts", [])),
            student_reports=list(data.get("student_reports", [])),
            anonymous_claims=list(data.get("anonymous_claims", [])),
            manual_review_notes=str(data.get("manual_review_notes", "")),
        )


@dataclass
class PIRecord:
    name: str
    university: str = ""
    department: str = ""
    research_areas: list[str] = field(default_factory=list)
    eligibility_verified: bool = False
    recruiting_status: str = "unknown"
    recent_grants: list[str] = field(default_factory=list)
    hiring_likelihood_signal: str = "Normal"
    research_fit_score: float = 0.0
    mentoring_score: float = 2.5
    overall_pi_score: float = 0.0
    feedback: PeerFeedbackRecord = field(default_factory=PeerFeedbackRecord)
    outreach_status: str = "Not Contacted"
    user_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["feedback"] = self.feedback.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PIRecord:
        return cls(
            name=str(data.get("name", "")),
            university=str(data.get("university", "")),
            department=str(data.get("department", "")),
            research_areas=list(data.get("research_areas", [])),
            eligibility_verified=bool(data.get("eligibility_verified", False)),
            recruiting_status=str(data.get("recruiting_status", "unknown")),
            recent_grants=list(data.get("recent_grants", [])),
            hiring_likelihood_signal=str(data.get("hiring_likelihood_signal", "Normal")),
            research_fit_score=float(data.get("research_fit_score", 0.0)),
            mentoring_score=float(data.get("mentoring_score", 2.5)),
            overall_pi_score=float(data.get("overall_pi_score", 0.0)),
            feedback=PeerFeedbackRecord.from_dict(data.get("feedback")),
            outreach_status=str(data.get("outreach_status", "Not Contacted")),
            user_notes=str(data.get("user_notes", "")),
        )


@dataclass
class ProgramRecord:
    id: str
    school: str
    program: str
    degree: str
    field: str
    portfolio_category: PortfolioCategory = "Needs more evidence"
    admission_mode: AdmissionModeModel = field(default_factory=AdmissionModeModel)
    program_score: float = 0.0
    pi_score: float = 0.0
    overall_fit_score: float = 0.0
    stipend_amount: float = 0.0
    real_stipend_amount: float = 0.0
    location: str = ""
    col_index: float = 1.0
    application_deadline: str = ""
    application_fee: float = 0.0
    submission_status: str = "Not Started"
    evidence_items: list[dict[str, Any]] = field(default_factory=list)
    pi_list: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["admission_mode"] = self.admission_mode.to_dict()
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProgramRecord:
        return cls(
            id=str(data.get("id", "")),
            school=str(data.get("school", "")),
            program=str(data.get("program", "")),
            degree=str(data.get("degree", "")),
            field=str(data.get("field", "")),
            portfolio_category=data.get("portfolio_category", "Needs more evidence"),
            admission_mode=AdmissionModeModel.from_dict(data.get("admission_mode")),
            program_score=float(data.get("program_score", 0.0)),
            pi_score=float(data.get("pi_score", 0.0)),
            overall_fit_score=float(data.get("overall_fit_score", 0.0)),
            stipend_amount=float(data.get("stipend_amount", 0.0)),
            real_stipend_amount=float(data.get("real_stipend_amount", 0.0)),
            location=str(data.get("location", "")),
            col_index=float(data.get("col_index", 1.0)),
            application_deadline=str(data.get("application_deadline", "")),
            application_fee=float(data.get("application_fee", 0.0)),
            submission_status=str(data.get("submission_status", "Not Started")),
            evidence_items=list(data.get("evidence_items", [])),
            pi_list=list(data.get("pi_list", [])),
        )


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
