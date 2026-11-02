/*
==============================================================================
  Career Orchestrator - SAP HANA Cloud SQL Database
  File: 05_join_queries.sql
  Purpose: Queries demonstrating INNER JOIN, LEFT JOIN, and other join types
           with SAP HANA SQL syntax.
  SAP HANA Cloud SQL - Compliant
==============================================================================
*/

-- 5.1: INNER JOIN - User with their Skills
-- Purpose: List all users and their associated skills with proficiency.
-- Demonstrates: INNER JOIN across USERS, USER_SKILLS, SKILLS
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    u.current_role,
    s.skill_name,
    us.proficiency_level
FROM CAREER_ORCHESTRATOR.USERS u
INNER JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id
INNER JOIN CAREER_ORCHESTRATOR.SKILLS s
    ON us.skill_id = s.skill_id
WHERE u.email = 'anitha.raman@email.com'
ORDER BY s.skill_name;

-- 5.2: LEFT JOIN - Users with Work Experience
-- Purpose: List all users with their work experience (if any).
-- Demonstrates: LEFT JOIN to include users without work experience
SELECT
    u.user_id,

-- 5.3: LEFT JOIN - Employees with Optional Work Samples
-- Purpose: List users with their work samples, including users without samples.
-- Demonstrates: LEFT JOIN with optional related records
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    ws.title AS work_sample_title,
    ws.description,
    ws.file_url,
    ws.upload_date
FROM CAREER_ORCHESTRATOR.USERS u
LEFT JOIN CAREER_ORCHESTRATOR.WORK_SAMPLES ws
    ON u.user_id = ws.user_id
ORDER BY u.last_name, u.first_name;

-- 5.4: FULL OUTER JOIN - (Where Supported in SAP HANA)
-- Purpose: List all skills and all users who possess them, including
--          skills without users and users without skills.
-- Note: SAP HANA supports FULL OUTER JOIN.
-- Demonstrates: FULL OUTER JOIN for complete data coverage
SELECT
    s.skill_name,
    u.first_name || ' ' || u.last_name AS employee_name,
    us.proficiency_level
FROM CAREER_ORCHESTRATOR.SKILLS s
FULL OUTER JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON s.skill_id = us.skill_id
FULL OUTER JOIN CAREER_ORCHESTRATOR.USERS u
    ON us.user_id = u.user_id
ORDER BY s.skill_name;

-- 5.5: MULTI-TABLE JOIN - Career Profile Report
-- Purpose: Comprehensive career profile combining user, experience, skills,
--          and job roles information.
-- Demonstrates: Multi-table join across 5 tables
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    u.location,
    u.years_of_experience,
    u.current_role,
    w.position_title,
    w.company_name,
    s.skill_name,
    us.proficiency_level AS skill_level,
    jr.role_name AS matching_role
FROM CAREER_ORCHESTRATOR.USERS u
LEFT JOIN CAREER_ORCHESTRATOR.WORK_EXPERIENCE w
    ON u.user_id = w.user_id
LEFT JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id
LEFT JOIN CAREER_ORCHESTRATOR.SKILLS s
    ON us.skill_id = s.skill_id
LEFT JOIN CAREER_ORCHESTRATOR.JOB_ROLES jr
    ON jr.role_name ILIKE '%' || REPLACE(UPPER(u.current_role), ' ', '') || '%'
WHERE u.email = 'anitha.raman@email.com'
ORDER BY s.skill_name;

-- 5.6: JOIN - Work Experience with Corresponding Skills
-- Purpose: For each work experience entry, show the skills relevant to that
--          period of the employee's career.
-- Demonstrates: Nested JOINs
SELECT
    w.experience_id,
    w.company_name,
    w.position_title,

-- 5.7: JOIN - Recommendations with Reviewer Information
-- Purpose: List all AI recommendations with their reviewer details.
-- Demonstrates: JOIN across RECOMMENDATIONS, USERS, BIAS_AUDITS
SELECT
    r.recommendation_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    r.recommended_role,
    r.confidence_score,
    r.is_approved,
    b.review_result,
    br.first_name || ' ' || br.last_name AS reviewer_name
FROM CAREER_ORCHESTRATOR.RECOMMENDATIONS r
INNER JOIN CAREER_ORCHESTRATOR.USERS u
    ON r.user_id = u.user_id
LEFT JOIN CAREER_ORCHESTRATOR.BIAS_AUDITS b
    ON r.recommendation_id = b.recommendation_id
LEFT JOIN CAREER_ORCHESTRATOR.USERS br
    ON b.reviewer_user_id = br.user_id
ORDER BY r.created_at DESC;

    w.start_date,
    w.end_date,
    s.skill_name,
    us.proficiency_level
FROM CAREER_ORCHESTRATOR.WORK_EXPERIENCE w
INNER JOIN CAREER_ORCHESTRATOR.USERS u
    ON w.user_id = u.user_id
LEFT JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id
LEFT JOIN CAREER_ORCHESTRATOR.SKILLS s
    ON us.skill_id = s.skill_id
WHERE u.email = 'anitha.raman@email.com'
    AND w.is_current = TRUE
ORDER BY w.start_date DESC, s.skill_name;

    u.first_name || ' ' || u.last_name AS employee_name,
    u.current_role,
    w.company_name,
    w.position_title,
    w.start_date,
    w.end_date,
    w.is_current
FROM CAREER_ORCHESTRATOR.USERS u
LEFT JOIN CAREER_ORCHESTRATOR.WORK_EXPERIENCE w
    ON u.user_id = w.user_id
ORDER BY u.last_name, u.first_name, w.start_date;
