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
    interests: list[Interest] = Field(default_factory=list, max_length=3, description="Ordered, most wanted first")
    weekly_hours: Optional[int] = Field(default=None, ge=1, le=40)
class MotivationPrefs(S):
    styles: list[Style] = Field(min_length=1, max_length=2, description="1 or 2 styles the worker chose; first is primary")
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
