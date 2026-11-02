/*
==============================================================================
  Career Orchestrator - SAP HANA Cloud SQL Database
  File: 07_create_views.sql
  Purpose: Database views for employee skill profiles, career
           recommendations, and skill gap analysis.
  SAP HANA Cloud SQL - Compliant
==============================================================================
*/

-- ============================================================================
-- VIEW 1: EMP_SKILL_PROFILE
-- ============================================================================
-- Purpose: Employee skill profile view for HR dashboards and reporting.
-- Shows each employee's skills with proficiency levels.
-- Requires: USERS, USER_SKILLS, SKILLS
-- ============================================================================
CREATE VIEW CAREER_ORCHESTRATOR.EMP_SKILL_PROFILE AS
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    u.current_role,
    u.location,
    u.years_of_experience,
    s.skill_id,
    s.skill_name,
    s.skill_category,
    us.proficiency_level,
    CASE
        WHEN us.proficiency_level >= 4 THEN 'Advanced'
        WHEN us.proficiency_level >= 3 THEN 'Intermediate'
        WHEN us.proficiency_level >= 2 THEN 'Beginner'
        ELSE 'Novice'
    END AS proficiency_tier,
    us.created_at AS skill_acquired_date
FROM CAREER_ORCHESTRATOR.USERS u
INNER JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id
INNER JOIN CAREER_ORCHESTRATOR.SKILLS s
    ON us.skill_id = s.skill_id
ORDER BY
    u.user_id,
    s.skill_name;

COMMENT ON VIEW CAREER_ORCHESTRATOR.EMP_SKILL_PROFILE
    IS 'Employee skill profile view combining user and skill information with proficiency tiers.';

-- ============================================================================
-- VIEW 2: CAREER_RECOMMENDATION_DETAIL
-- ============================================================================
-- Purpose: Detailed view for career recommendations including
--          user profile, recommended role, and confidence metrics.
-- Requires: USERS, RECOMMENDATIONS, JOB_ROLES
-- ============================================================================
CREATE VIEW CAREER_ORCHESTRATOR.CAREER_RECOMMENDATION_DETAIL AS
SELECT
    r.recommendation_id,
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    u.current_role,
    r.recommended_role,
    r.rationale,
    r.confidence_score,
    r.is_approved,
    r.created_at AS recommendation_date,
    jr.role_description
FROM CAREER_ORCHESTRATOR.RECOMMENDATIONS r
INNER JOIN CAREER_ORCHESTRATOR.USERS u
    ON r.user_id = u.user_id
INNER JOIN CAREER_ORCHESTRATOR.JOB_ROLES jr
    ON r.recommended_role = jr.role_name
ORDER BY r.created_at DESC;

COMMENT ON VIEW CAREER_ORCHESTRATOR.CAREER_RECOMMENDATION_DETAIL
    IS 'Detailed view of AI-generated career recommendations with user and role context.';

-- ============================================================================
-- VIEW 3: SKILL_GAP_ANALYSIS
-- ============================================================================
-- Purpose: View for analyzing skill gaps between required job role skills
--          and an employee's actual skill proficiency.
-- Requires: USERS, JOB_ROLES, ROLE_SKILLS, SKILLS, USER_SKILLS
-- ============================================================================
CREATE VIEW CAREER_ORCHESTRATOR.SKILL_GAP_ANALYSIS AS
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    u.current_role,
    r.role_name AS target_role,
    s.skill_name,
    s.skill_category,
    rs.required_level,
    CASE
        WHEN us.proficiency_level IS NULL THEN 0
        ELSE us.proficiency_level
    END AS current_proficiency,
    CASE
        WHEN us.proficiency_level IS NULL THEN rs.required_level
        ELSE us.proficiency_level - rs.required_level
    END AS proficiency_delta,
    CASE
        WHEN us.proficiency_level IS NULL THEN 'MISSING'
        WHEN us.proficiency_level < rs.required_level THEN 'GAP'
        WHEN us.proficiency_level = rs.required_level THEN 'ON TRACK'
        ELSE 'EXCEEDS REQUIREMENTS'
    END AS gap_status
FROM CAREER_ORCHESTRATOR.JOB_ROLES r
CROSS JOIN CAREER_ORCHESTRATOR.USERS u
INNER JOIN CAREER_ORCHESTRATOR.ROLE_SKILLS rs
    ON r.role_id = rs.role_id
INNER JOIN CAREER_ORCHESTRATOR.SKILLS s
    ON rs.skill_id = s.skill_id
LEFT JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id AND us.skill_id = s.skill_id
WHERE u.email = 'anitha.raman@email.com'
ORDER BY
    r.role_name,
    s.skill_name;
