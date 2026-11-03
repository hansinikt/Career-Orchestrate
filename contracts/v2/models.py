"""CANONICAL CONTRACT v2.0. Single source of truth for every request and response. Frontend types, backend routes, fixtures and tests must match this file.
Rules: extra="forbid" everywhere (unknown fields are rejected); there is NO field for age, date of birth, gender or years of experience, anywhere.
Changing this file needs agreement from all four developers, then `make contracts` regenerates contracts/v2/openapi.yaml."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

class S(BaseModel):
    model_config = ConfigDict(extra="forbid")

Interest = Literal["people", "data", "operations", "planning", "compliance"]
Style = Literal["progress", "goals", "encouragement", "accountability", "challenge"]
Band = Literal["strong_fit", "bridgeable", "stretch"]
Source = Literal["declared", "declared_alias", "extracted", "user_added"]
Signal = Literal["declared_only", "mentioned", "performed"]

# ---------- profile ----------
class DeclaredSkill(S):
    name: str = Field(min_length=1, max_length=80)
    level: int = Field(ge=1, le=3, description="1 Beginner, 2 Intermediate, 3 Advanced (the worker's own statement)")
class Preferences(S):
    interests: list[Interest] = Field(default_factory=list, max_length=5, description="Ordered, most wanted first")
    weekly_hours: Optional[int] = Field(default=None, ge=1, le=40)
class MotivationPrefs(S):
    styles: list[Style] = Field(min_length=1, max_length=5, description="One or more styles the worker chose; first is primary")
    check_in: Literal["daily", "weekly", "off"] = "weekly"
    paused: bool = False
class ProfileCreate(S):
    display_name: str = Field(min_length=1, max_length=60)
    current_role: Optional[str] = Field(default=None, max_length=80)
    work_examples: list[str] = Field(min_length=1, max_length=5, description="Each 10..1000 chars, in the worker's own words")
    declared_skills: list[DeclaredSkill] = Field(default_factory=list, max_length=30)
    stated_goal_role_id: Optional[str] = Field(default=None, description="Role the worker says they want, e.g. R001. Always shown back to them.")
    preferences: Optional[Preferences] = None
    motivation: Optional[MotivationPrefs] = None
    consent: bool = Field(description="Must be true. Worker agrees to processing of the text they entered.")
class Profile(S):
    profile_id: str
    display_name: str
    current_role: Optional[str]
    work_examples: list[str]
    declared_skills: list[DeclaredSkill]
    stated_goal_role_id: Optional[str]
    preferences: Optional[Preferences]
    motivation: Optional[MotivationPrefs]
    created_at: str

# ---------- skills discovery and confirmation ----------
class Evidence(S):
    quote: str = Field(description="Verbatim substring of one of the worker's work examples")
    work_example_index: int = Field(ge=0)
class SkillSuggestion(S):
    suggestion_id: str
    skill_id: str
    name: str
    suggested_level: int = Field(ge=1, le=3)
    source: Source
    signal: Signal
    evidence: list[Evidence]
    explanation: str
class ExtractResponse(S):
    profile_id: str
    suggestions: list[SkillSuggestion]
    unmatched_declared: list[str] = Field(description="Declared skills with no scored equivalent; shown to the worker, not scored")
    extraction_mode: Literal["rules", "llm+rules"]
    warnings: list[str] = Field(default_factory=list)
class Decision(S):
    suggestion_id: str
    action: Literal["accept", "edit", "reject"]
    level: Optional[int] = Field(default=None, ge=1, le=3, description="Required when action is edit")
class AddedSkill(S):
    skill_id: str
    level: int = Field(ge=1, le=3)
class ConfirmRequest(S):
    decisions: list[Decision] = Field(description="Exactly one decision per suggestion")
    added_skills: list[AddedSkill] = Field(default_factory=list)
class ConfirmedSkill(S):
    skill_id: str
    name: str
    level: int = Field(ge=1, le=3)
    source: Source
    evidence: list[Evidence]
class ConfirmResponse(S):
    profile_id: str
    confirmed_skills: list[ConfirmedSkill]
    rejected_skill_ids: list[str]

# ---------- roles ----------
class FeatureScores(S):
    skill_coverage: float
    preference_fit: Optional[float] = Field(description="null when the worker gave no interests (feature dropped, weights renormalised)")
    learnability: float
class MatchedSkill(S):
    skill_id: str
    name: str
    user_level: int
    required_level: int
    coverage: float
    evidence_quotes: list[str]
class SkillGap(S):
    skill_id: str
    name: str
    required_level: int
    user_level: int
    gap_levels: int
    mandatory: bool
    importance: int
    est_hours: float
    priority: float
class RoleRecommendation(S):
    rank: int
    role_id: str
    title: str
    score: float
    band: Band
    feature_scores: FeatureScores
    weights_used: dict[str, float]
    blocking_gaps: list[str]
    matched: list[MatchedSkill]
    gaps: list[SkillGap]
    est_gap_hours: float
    openness_flags: list[str]
    explanation: str
    provisional_weights: bool = True
    course_count: int = 0
    course_hours: float = 0
    build_skills: list[str] = Field(default_factory=list, description="Names of the role's researched requirements the worker does not have yet (empty when the role has no course data)")
class RecommendationsResponse(S):
    profile_id: str
    recommendations: list[RoleRecommendation]
    goal: Optional[RoleRecommendation] = Field(description="The worker's stated goal role with its own analysis, even if it is not in the top ranks")
    disclaimer: str

# ---------- learning plan ----------
class Resource(S):
    resource_id: str
    title: str
    provider: str
    url: Optional[str]
    skill_ids: list[str]
    level_from: int
    level_to: int
    est_hours: Optional[float]
    duration_text: str
    cost: str
    verification_status: Literal["verified", "seed_unverified", "sample_placeholder"]
    last_verified: Optional[str]
    note: str
# ---------- job options: courses for one role (additive in v3) ----------
class PathRequirement(S):
    id: str
    name: str
    evidence: str
    have: bool
    courses_covering: int
class PathCourse(S):
    resource_id: str
    title: str
    provider: str
    url: Optional[str]
    level: Optional[Literal["beginner", "intermediate", "advanced"]]
    level_basis: str
    est_hours: Optional[float]
    duration_text: str
    cost: Optional[str]
    rating: Optional[float]
    rating_count: Optional[int]
    certificate: Optional[bool]
    prerequisites: Optional[str]
    covers: list[str]
    why: str
    decided_by: Literal["agent", "rules"]
    verification_status: Literal["verified", "seed_unverified", "sample_placeholder"]
    units: list[str] = Field(default_factory=list, description="Modules or sections as listed on the course page")
    topics: list[str] = Field(default_factory=list, description="Topics as listed on the course page")
class RolePathResponse(S):
    profile_id: str
    role_id: str
    role_title: str
    requirements: list[PathRequirement]
    courses: list[PathCourse]
    mode: Literal["agent", "rules"]
    source_note: str
class PlanRequest(S):
    role_id: str
    weekly_hours: Optional[int] = Field(default=None, ge=1, le=40)
class PlanStep(S):
    order: int
    skill_id: str
    skill_name: str
    status: Literal["resource_found", "no_verified_resource"]
    resource: Optional[Resource]
    est_hours: float
    rationale: str
    builds_on: list[str]
class PlanResponse(S):
    plan_id: str
    profile_id: str
    role_id: str
    role_title: str
    total_est_hours: float
    weekly_hours: Optional[int]
    weeks_at_pace: Optional[int]
    steps: list[PlanStep]
    unresolved_skill_ids: list[str]
    includes_unverified_resources: bool
    disclaimer: str

# ---------- progress and motivation ----------
class ProgressUpdate(S):
    step_order: int = Field(ge=1)
    percent: int = Field(ge=0, le=100)
    hours_logged: Optional[float] = Field(default=None, ge=0, le=100)
class StepProgress(S):
    order: int
    skill_name: str
    est_hours: float
    percent: int
class NextMessage(S):
    message_id: str
    style: Style
    event: Literal["start", "step_done", "halfway", "behind", "welcome_back", "plan_done"]
    text: str
    suggested_action: Literal["none", "share_summary"]
class ProgressResponse(S):
    profile_id: str
    plan_id: str
    percent: int
    hours_done: float
    hours_total: float
    steps_done: int
    steps_total: int
    steps: list[StepProgress]
    last_activity_at: Optional[str]
    next_message: Optional[NextMessage]
class MessageFeedback(S):
    helpful: bool

# ---------- job-ad openness check ----------
class ReadinessRequest(S):
    text: str = Field(min_length=20, max_length=5000)
class ReadinessFlag(S):
    rule_id: str
    matched_text: str
    why: str
    suggestion: str
class ReadinessResult(S):
    status: Literal["flagged", "no_flags"]
    flags: list[ReadinessFlag]
    skills_first: bool
    limitations: list[str]

# ---------- bias audit ----------
class AuditRequest(S):
    canary: bool = Field(default=False, description="Demo only: add a deliberately biased variant to prove the audit can catch bias")
class AuditMetrics(S):
    skills_jaccard: float
    top3_overlap: int
    kendall_tau: float
    max_abs_score_delta: float
    plan_hours_delta: float
    lexicon_hits: int
class AuditFlag(S):
    variant_id: str
    metric: str
    observed: float
    threshold: float
    message: str
class AuditVariant(S):
    variant_id: str
    cue: str
    metrics: AuditMetrics
    flags: list[AuditFlag]
class ReviewRequest(S):
    reviewer: str = Field(min_length=1, max_length=60)
    decision: Literal["acknowledged", "override", "escalate"]
    note: Optional[str] = Field(default=None, max_length=500)
class AuditReview(S):
    reviewer: str
    decision: str
    note: Optional[str]
    reviewed_at: str
class AuditResult(S):
    audit_id: str
    profile_id: str
    status: Literal["pass", "flagged"]
    canary: bool
    variants: list[AuditVariant]
    thresholds: dict[str, float]
    limitations: list[str]
    review: Optional[AuditReview]
    created_at: str

# ---------- v3 additions (additive only): trace, market, course scout, missions ----------
AgentName = Literal["skills_discovery", "market_intelligence", "learning_pathway", "inclusive_matching", "bias_audit", "human_in_the_loop"]
class AgentStep(S):
    step: int = Field(ge=1)
    agent: AgentName
    mode: str
    input_summary: str
    output_summary: str
    stopped_at_gate: bool
    created_at: str
class TraceResponse(S):
    profile_id: str
    steps: list[AgentStep]
class MarketSkill(S):
    skill_id: str
    name: str
    roles_asking: int = Field(ge=0, description="How many roles in OUR catalogue list this skill")
    mandatory_in: int = Field(ge=0)
class MarketResponse(S):
    profile_id: str
    roles_in_catalogue: int
    top_role_ids: list[str]
    held: list[MarketSkill]
    next_skills: list[MarketSkill]
    source_note: str
class ScoutStep(S):
    order: int
    skill_id: str
    skill_name: str
    current_resource_id: Optional[str]
    pick_resource_id: Optional[str]
    reason: str
    decided_by: Literal["agent", "rules"]
    candidates: list[Resource]
class ScoutResponse(S):
    profile_id: str
    plan_id: str
    mode: Literal["agent", "rules"]
    steps: list[ScoutStep]
    note: str
class ScoutChoice(S):
    order: int
    resource_id: str
class ScoutApproveRequest(S):
    choices: list[ScoutChoice] = Field(min_length=1, max_length=20)
class Mission(S):
    mission_id: str
    order: int
    title: str
    brief: str
    source: str
    chapter_title: Optional[str]
    status: Literal["open", "locked", "done", "declined"]
    percent: int = Field(ge=0, le=100, description="0 not started, 50 started, 100 proof uploaded")
    proof_name: Optional[str]
class MissionsResponse(S):
    profile_id: str
    missions: list[Mission]
    today_mission_id: Optional[str]
class MissionDeclineResponse(S):
    missions: MissionsResponse
    message: Optional[NextMessage] = Field(description="Encouragement for the worker, or null when messages are paused")
class ProofRequest(S):
    file_name: str = Field(min_length=1, max_length=120)
    content_base64: str = Field(min_length=1, max_length=2_900_000, description="File content, at most about 2 MB")
    note: Optional[str] = Field(default=None, max_length=500)
class Chapter(S):
    chapter_id: str
    title: str
    est_hours: Optional[float]
    done: bool
class ChaptersResponse(S):
    profile_id: str
    step_order: int
    resource_id: Optional[str]
    chapters: list[Chapter]
    percent: int
    source: Literal["chapters", "manual"]
    next_message: Optional[NextMessage]
class ChapterTick(S):
    chapter_id: str
    done: bool
EduLevel = Literal["school", "grade10", "grade12", "diploma", "bachelor", "master", "other"]
class EducationItem(S):
    level: EduLevel
    field: Optional[str] = Field(default=None, max_length=80)
    institution: Optional[str] = Field(default=None, max_length=80)
class CertItem(S):
    name: str = Field(min_length=1, max_length=100)
    issuer: Optional[str] = Field(default=None, max_length=80)
class Background(S):
    education: list[EducationItem] = Field(default_factory=list, max_length=5)
    certifications: list[CertItem] = Field(default_factory=list, max_length=10)
    languages: list[str] = Field(default_factory=list, max_length=8)
    tools: list[str] = Field(default_factory=list, max_length=20)
    barriers: list[Literal["time", "money", "confidence", "device_internet", "language", "caring_duties", "unsure_start"]] = Field(default_factory=list, max_length=7)
    situation: Optional[Literal["promotion", "switch_field", "returning", "cv_not_showing_skills", "other"]] = None
    situations: list[Literal["promotion", "switch_field", "returning", "cv_not_showing_skills", "other"]] = Field(default_factory=list, max_length=5, description="All that apply; situation holds the first")
    learning_formats: list[Literal["video", "reading", "hands_on", "live"]] = Field(default_factory=list, max_length=4)
class CVParseRequest(S):
    text: str = Field(min_length=40, max_length=20000, description="Plain text of the CV")
class CVFileRequest(S):
    file_name: str = Field(min_length=1, max_length=200)
    content_base64: str = Field(min_length=8, max_length=2_800_000, description="PDF or Word (.docx) file, at most 2 MB before encoding")
class CVFileText(S):
    text: str
    truncated: bool
    pages: int
class ParsedCert(S):
    name: str
    issuer: Optional[str]
class ParsedEducation(S):
    line: str
    level: Optional[EduLevel]
    field: Optional[str]
    institution: Optional[str]
class CVParseResponse(S):
    current_role: Optional[str]
    work_examples: list[str]
    skills: list[str]
    tools: list[str]
    certifications: list[ParsedCert]
    education: list[ParsedEducation]
    languages: list[str]
    mode: Literal["rules", "llm+rules"]
    ignored_lines: int = Field(ge=0, description="Lines about age, gender, years worked and similar that were dropped and never used")
    warnings: list[str]
class CVDocument(S):
    profile_id: str
    file_name: str
    text: str
    sections: list[str]

# ---------- meta and errors ----------
class Meta(S):
    app_version: str
    contract_version: str
    mode: Literal["replay", "live"]
    extraction_mode: Literal["rules", "llm+rules"]
    weights: dict[str, float]
    weights_are_provisional: bool
    catalog: dict[str, int]
    resource_policy: dict[str, bool]
    disclaimers: list[str]
class ErrorBody(S):
    code: Literal["VALIDATION_ERROR", "FORBIDDEN_FIELD", "NOT_FOUND", "CONSENT_REQUIRED", "SKILLS_NOT_CONFIRMED", "NO_ACTIVE_PLAN", "INTERNAL"]
    message: str
    details: Optional[dict] = None
class ErrorResponse(S):
    error: ErrorBody
