"""CANONICAL DATA CONTRACTS (v1.0). Single source of truth: OpenAPI + JSON Schema are generated from this file.
Changing anything here requires a Contract Change Proposal (see AGENTS.md)."""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")

# ---------- enums (string literals; identical in API, DB and UI) ----------
Origin = Literal["explicit", "inferred", "user_added"]
SkillStatus = Literal["pending", "confirmed", "rejected"]
LevelSignal = Literal["mentioned", "performed", "owned_outcome"]
Band = Literal["strong_fit", "bridgeable", "stretch"]
StageName = Literal["extract_skills", "confirm_skills", "match_roles", "select_role",
                    "learning_plan", "employer_readiness", "bias_audit", "compose_result"]
StageStatus = Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED", "SKIPPED", "AWAITING_USER"]
WorkflowStatus = Literal["QUEUED", "RUNNING", "AWAITING_USER", "COMPLETED", "COMPLETED_WITH_WARNINGS", "FAILED", "CANCELLED"]
StageKind = Literal["llm", "deterministic", "human"]

# ---------- APIError ----------
class APIError(Strict):
    code: Literal["VALIDATION_ERROR", "CONSENT_REQUIRED", "NOT_FOUND", "CONFLICT_STATE", "STAGE_FAILED",
                  "LLM_UNAVAILABLE", "LLM_SCHEMA_VIOLATION", "TIMEOUT", "RATE_LIMITED", "INTERNAL_ERROR"]
    message: str
    retryable: bool
    details: Optional[dict] = None
    request_id: str
class APIErrorResponse(Strict):
    error: APIError

# ---------- CareerProfile ----------
class Consent(Strict):
    given: bool
    version: str = "2026-10-v1"
    at: Optional[str] = None
class WorkEntry(Strict):
    title: str = Field(max_length=120)
    organisation: Optional[str] = Field(default=None, max_length=120)
    description: str = Field(max_length=2500, description="Free text: what the person actually did")
class Preferences(Strict):
    interest_tags: list[str] = Field(default_factory=list, max_length=3, description="Ordered, most preferred first (max 3)")
    work_mode: Optional[Literal["onsite", "hybrid", "remote"]] = None
    weekly_learning_hours: Optional[int] = Field(default=None, ge=1, le=40)
class CareerProfileInput(Strict):
    consent: Consent
    language: Literal["en"] = "en"
    display_name: Optional[str] = Field(default=None, max_length=80)
    summary_text: Optional[str] = Field(default=None, max_length=1500)
    work_entries: list[WorkEntry] = Field(min_length=1, max_length=10)
    preferences: Preferences = Preferences()
class CareerProfile(CareerProfileInput):
    profile_id: str
    created_at: str
    updated_at: str
    is_synthetic: bool = False
# NOTE: there is deliberately NO age / date-of-birth / gender / photo field (data minimisation).

# ---------- Skills ----------
class SkillEvidence(Strict):
    evidence_id: str
    quote: str = Field(description="Verbatim substring of the user's input (whitespace-normalised)")
    source: Literal["summary_text", "work_entry"]
    entry_index: Optional[int] = None
    level_signal: LevelSignal
class NormalizedSkill(Strict):
    skill_id: str
    name: str
    origin: Origin
    status: SkillStatus
    level: int = Field(ge=0, le=3, description="0 none,1 foundational,2 working,3 advanced/owned")
    evidence_ids: list[str]
    confidence: Literal["low", "medium", "high"]
    rationale: str = Field(max_length=240)
class ClarifyingQuestion(Strict):
    question_id: str
    text: str
    skill_ids: list[str]
class SkillExtractionResult(Strict):
    evidence: list[SkillEvidence]
    skills: list[NormalizedSkill]
    clarifying_questions: list[ClarifyingQuestion] = Field(max_length=3)
    dropped_ungrounded: int = 0
    taxonomy_version: str

# ---------- Roles ----------
class Requirement(Strict):
    skill_id: str
    importance: int = Field(ge=1, le=5)
    required_level: int = Field(ge=1, le=3)
    mandatory: bool
class MarketSignal(Strict):
    kind: Literal["demand_note", "salary_range", "vacancy_count"]
    text: str
    source_url: str
    as_of: str
class RoleProfile(Strict):
    role_id: str
    title: str
    summary: str
    tags: list[str]
    requirements: list[Requirement]
    requires_degree: Optional[bool] = None
    max_experience_years: Optional[int] = None
    onet_soc: Optional[str] = None
    provenance: Literal["team_curated_unverified", "team_curated_onet_checked"]
    market_signals: list[MarketSignal] = []
    proof_templates: list[str] = []

class SkillGap(Strict):
    skill_id: str
    name: str
    required_level: int
    user_level: int
    gap_levels: int
    mandatory: bool
    importance: int
    est_hours: float
    priority: float
class MatchedSkill(Strict):
    skill_id: str
    name: str
    user_level: int
    required_level: int
    coverage: float
    evidence_ids: list[str]
class FeatureScores(Strict):
    skill_coverage: float
    preference_fit: Optional[float]
    learnability: float
class RoleRecommendation(Strict):
    role_id: str
    title: str
    rank: int
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

# ---------- Learning ----------
class LearningResource(Strict):
    resource_id: str
    title: str
    provider: str
    url: Optional[str]
    skill_ids: list[str]
    level_from: int
    level_to: int
    est_hours: Optional[float]
    cost: Literal["free", "paid", "unknown"]
    verification_status: Literal["verified", "seed_unverified", "broken"]
    last_verified: Optional[str] = None
class PlanStep(Strict):
    order: int
    skill_id: str
    skill_name: str
    status: Literal["resource_found", "no_verified_resource", "already_met"]
    resource: Optional[LearningResource]
    est_hours: float
    builds_on: list[str]
    rationale: str
class LearningPlan(Strict):
    plan_id: str
    role_id: str
    total_est_hours: float
    weeks_at_pace: Optional[int]
    steps: list[PlanStep]
    unresolved_skill_ids: list[str]
    proof_tasks: list[str]

# ---------- Employer readiness ----------
class Achievement(Strict):
    text: str
    evidence_ids: list[str] = Field(min_length=1)
    needs_user_input: list[str] = []
class TransferItem(Strict):
    skill_id: str
    role_requirement: str
    evidence_ids: list[str]
class ResumeTip(Strict):
    type: Literal["reword", "quantify_prompt", "add_section"]
    suggestion: str
    evidence_ids: list[str]
class PortfolioIdea(Strict):
    title: str
    description: str
    skill_ids: list[str]
class InterviewItem(Strict):
    question: str
    star_hint: str
    evidence_ids: list[str]
class GroundingReport(Strict):
    dropped_claims: int
    flagged_numbers: list[str]
class EmployerReadinessResult(Strict):
    role_id: str
    relevant_achievements: list[Achievement]
    transferable_experience: list[TransferItem]
    resume_improvements: list[ResumeTip]
    portfolio_suggestions: list[PortfolioIdea]
    interview_prep: list[InterviewItem]
    remaining_prep: list[str]
    openness_flags: list[str]
    grounding_report: GroundingReport

# ---------- Bias audit ----------
class AuditVariantResult(Strict):
    variant_id: str
    cue_set: Literal["baseline", "direct_age_cue", "proxy_experience_years"]
    label: str
    skills_jaccard: float
    top3_overlap: int
    kendall_tau: float
    max_abs_score_delta: float
    plan_hours_delta: float
    lexicon_hits: int
class AuditFlag(Strict):
    variant_id: str
    metric: str
    observed: float
    threshold: float
    message: str
class Reviewer(Strict):
    status: Literal["pending", "reviewed"]
    decision: Optional[Literal["accept_no_action", "investigate", "block_release"]] = None
    note: Optional[str] = None
    reviewed_at: Optional[str] = None
class BiasAuditResult(Strict):
    audit_id: str
    profile_id: str
    status: Literal["RUNNING", "SUCCEEDED", "FAILED"]
    created_at: str
    mode: Literal["deterministic_only", "llm_extraction", "replay"]
    repeats: int
    variants: list[AuditVariantResult]
    thresholds: dict[str, float]
    flags: list[AuditFlag]
    verdict: Literal["pass", "flag", "inconclusive"]
    reviewer: Reviewer
    limitations: list[str]

# ---------- Workflow ----------
class StageState(Strict):
    name: StageName
    kind: StageKind
    status: StageStatus
    attempts: int = 0
    cache_hit: bool = False
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    error: Optional[APIError] = None
class WorkflowState(Strict):
    workflow_id: str
    profile_id: str
    status: WorkflowStatus
    current_stage: Optional[StageName]
    stages: list[StageState]
    selected_role_ids: list[str] = []
    warnings: list[str] = []
    mode: Literal["live", "replay", "mock"]
    created_at: str
    updated_at: str
class WorkflowResults(Strict):
    workflow_id: str
    skills: Optional[SkillExtractionResult] = None
    recommendations: Optional[list[RoleRecommendation]] = None
    learning_plans: Optional[list[LearningPlan]] = None
    employer_readiness: Optional[list[EmployerReadinessResult]] = None
    bias_audit: Optional[BiasAuditResult] = None
    disclaimers: list[str]

# ---------- request bodies ----------
class SkillDecision(Strict):
    skill_id: str
    action: Literal["confirm", "reject", "set_level"]
    level: Optional[int] = Field(default=None, ge=1, le=3)
class AddedSkill(Strict):
    skill_id: str
    level: int = Field(ge=1, le=3)
    note: Optional[str] = Field(default=None, max_length=240)
class SkillConfirmationRequest(Strict):
    decisions: list[SkillDecision]
    added_skills: list[AddedSkill] = []
class RoleSelectionRequest(Strict):
    role_ids: list[str] = Field(min_length=1, max_length=2)
class StartWorkflowRequest(Strict):
    profile_id: str
class AuditRequest(Strict):
    profile_id: str
    repeats: int = Field(default=1, ge=1, le=5)
    include_proxy_cues: bool = True
class ReviewRequest(Strict):
    decision: Literal["accept_no_action", "investigate", "block_release"]
    note: Optional[str] = Field(default=None, max_length=500)
