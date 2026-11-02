/*
==============================================================================
  Career Orchestrator - SAP HANA Cloud SQL Database
  File: 06_advanced_queries.sql
  Purpose: Advanced SQL queries including subqueries, CASE statements,
           window functions, and complex analytical queries.
  SAP HANA Cloud SQL - Compliant
==============================================================================
*/

-- 6.1: SUBQUERY - RECOMMENDATION RANKING
-- Purpose: Rank users by their average skill proficiency level.
-- Demonstrates: Subquery with AVG and ranking logic
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    u.current_role,
    COUNT(us.skill_id) AS skill_count,
    ROUND(AVG(us.proficiency_level), 2) AS avg_proficiency,
    CASE
        WHEN ROUND(AVG(us.proficiency_level), 2) >= 4.5 THEN 'Top Performer'
        WHEN ROUND(AVG(us.proficiency_level), 2) >= 3.5 THEN 'Skilled'
        WHEN ROUND(AVG(us.proficiency_level), 2) >= 2.5 THEN 'Developing'
        ELSE 'Beginner'
    END AS performance_tier
FROM CAREER_ORCHESTRATOR.USERS u
INNER JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id
GROUP BY
    u.user_id,
    u.first_name,
    u.last_name,
    u.current_role
HAVING COUNT(us.skill_id) >= 3
ORDER BY avg_proficiency DESC;

-- 6.2: SUBQUERY - SKILL GAP ANALYSIS
-- Purpose: For a specific job role, identify which required skills are
--          missing or at a low proficiency level for a user.
-- Demonstrates: Subquery with NOT EXISTS/EXISTS pattern
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    u.current_role,
    r.role_name AS target_role,
    s.skill_name,
    s.skill_category,
    rs.required_level,
    us.proficiency_level,
    CASE
        WHEN us.proficiency_level IS NULL THEN 'MISSING'
        WHEN us.proficiency_level < rs.required_level THEN 'GAP'
        ELSE 'MECHANALLY PASS'
    END AS skill_gap_status
FROM CAREER_ORCHESTRATOR.JOB_ROLES r
CROSS JOIN CAREER_ORCHESTRATOR.USERS u
INNER JOIN CAREER_ORCHESTRATOR.ROLE_SKILLS rs
    ON r.role_id = rs.role_id
INNER JOIN CAREER_ORCHESTRATOR.SKILLS s
    ON rs.skill_id = s.skill_id
LEFT JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id AND us.skill_id = s.skill_id
WHERE r.role_name = 'Operations Analyst'
    AND u.email = 'anitha.raman@email.com'
ORDER BY s.skill_name;

-- 6.3: MULTI-LEVEL SUBQUERY - CAREER ADVANCEMENT TRACK
-- Purpose: Identify career roles that an employee could advance to based on
--          their skills exceeding minimum requirements.
-- Demonstrates: Nested subqueries
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    u.current_role,
    next_role.role_name AS potential_next_role,
    next_role.min_experience,
    next_role.required_skill_level,
    CASE
        WHEN u.years_of_experience >= next_role.min_experience THEN 'Experience Ready'
        ELSE 'Experience Shortfall'
    END AS readiness,
    CASE
        WHEN u.years_of_experience >= next_role.min_experience
            AND cnt.avg_skill_level >= next_role.required_skill_level
        THEN 'QUALIFIED'
        WHEN u.years_of_experience >= next_role.min_experience
            AND cnt.avg_skill_level < next_role.required_skill_level
        THEN 'SKILL GAP'
        ELSE 'NOT READY'
    END AS advancement_status
FROM CAREER_ORCHESTRATOR.USERS u
INNER JOIN (

-- 6.5: AGGREGATE WITH RETURNING - EMPLOYEE READINESS SCORE
-- Purpose: Generate an overall readiness score for career recommendation.
-- Demonstrates: Multiple aggregate queries with CASE logic
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    u.current_role,
    COUNT(DISTINCT s.skill_id) AS skill_count,
    ROUND(AVG(us.proficiency_level), 2) AS avg_skill_level,
    ROUND(AVG(us.proficiency_level) / 5.0 * 100, 2) AS skill_competence_pct,
    CASE
        WHEN COUNT(DISTINCT s.skill_id) >= 5 THEN 'SKILLED'
        WHEN COUNT(DISTINCT s.skill_id) >= 3 THEN 'ADEQUATE'
        ELSE 'DEVELOPING'
    END AS skill_MATURITY,
    CASE
        WHEN u.years_of_experience >= 10 THEN 'EXPERIENCED'
        WHEN u.years_of_experience >= 5 THEN 'PROFESSIONAL'
        ELSE 'ENTRY-LEVEL'
    END AS experience_tier,
    CASE
        WHEN COUNT(DISTINCT s.skill_id) >= 5
            AND u.years_of_experience >= 10
            AND ROUND(AVG(us.proficiency_level) / 5.0 * 100, 2) >= 80
        THEN 'HIGH READINESS'
        WHEN COUNT(DISTINCT s.skill_id) >= 3
            AND u.years_of_experience >= 5
            AND ROUND(AVG(us.proficiency_level) / 5.0 * 100, 2) >= 60
        THEN 'MODERATE READINESS'
        ELSE 'LOW READINESS'
    END AS career_readiness_score
FROM CAREER_ORCHESTRATOR.USERS u
LEFT JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id
LEFT JOIN CAREER_ORCHESTRATOR.SKILLS s
    ON us.skill_id = s.skill_id
WHERE u.email = 'anitha.raman@email.com'
GROUP BY
    u.user_id,
    u.first_name,
    u.last_name,
    u.current_role,
    u.years_of_experience;

-- 6.6: COMPLEX AGGREGATION - SKILL DOMAIN SCORES
-- Purpose: Calculate average proficiency by skill category for a user.
-- Demonstrates: GROUP BY with CASE for domain classification
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    CASE
        WHEN s.skill_category IN ('Technical', 'Data Management') THEN 'Technical Skills'
        WHEN s.skill_category IN ('Interpersonal', 'Leadership') THEN 'Soft Skills'
        ELSE 'Other Skills'
    END AS skill_domain,
    COUNT(us.skill_id) AS skills_in_domain,
    ROUND(AVG(us.proficiency_level), 2) AS avg_proficiency_in_domain
FROM CAREER_ORCHESTRATOR.USERS u
INNER JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id
INNER JOIN CAREER_ORCHESTRATOR.SKILLS s
    ON us.skill_id = s.skill_id
WHERE u.email = 'anitha.raman@email.com'
GROUP BY
    u.user_id,
    s.skill_category
ORDER BY skill_domain, avg_proficiency_in_domain DESC;

-- 6.7: STRING OPERATIONS - EMPLOYEE NAME CONCATENATION
-- Purpose: Demonstrate various string operations for employee reports.
-- Demonstrates: Concatenation, SUBSTRING, TRIM, LENGTH, UPPER/LOWER
SELECT
    user_id,
    first_name,
    last_name,
    -- Full name variants
    first_name || ' ' || last_name AS full_name,
    UPPER(first_name) AS upper_first_name,
    LOWER(last_name) AS lower_last_name,
    -- Initial
    SUBSTRING(first_name, 1, 1) || '.' AS first_name_initial,
    -- Location variations
    LENGTH(TRIM(location)) AS location_length,
    UPPER(TRIM(location)) AS location_upper,
    -- Email variations
    LOWER(email) AS lowercase_email,
    REPLACE(email, '@', ' at ') AS masked_email
FROM CAREER_ORCHESTRATOR.USERS
WHERE email = 'anitha.raman@email.com';

-- 6.8: DATE OPERATIONS - EXPERIENCE TENURE CALCULATIONS
-- Purpose: Calculate tenure based on work experience dates.
-- Demonstrates: Date arithmetic in SAP HANA
SELECT
    w.experience_id,
    w.position_title,
    w.start_date,
    w.end_date,
    CASE
        WHEN w.end_date IS NULL THEN
            TRUNC(DATEDIFF('DAY', w.start_date, CURRENT_DATE)) / 365.25
        ELSE
            TRUNC(DATEDIFF('DAY', w.start_date, w.end_date)) / 365.25
    END AS tenure_years,
    CASE
        WHEN w.end_date IS NULL THEN
            TRUNC(DATEDIFF('DAY', w.start_date, CURRENT_DATE)) % 365
        ELSE
            TRUNC(DATEDIFF('DAY', w.start_date, w.end_date)) % 365
    END AS tenure_days
FROM CAREER_ORCHESTRATOR.WORK_EXPERIENCE w
INNER JOIN CAREER_ORCHESTRATOR.USERS u
    ON w.user_id = u.user_id
WHERE u.email = 'anitha.raman@email.com'
    AND w.is_current = TRUE
ORDER BY w.start_date DESC;

-- 6.9: CORRELATED SUBQUERY - TOP SKILLS PER EMPLOYEE
-- Purpose: For each user, find their highest proficiency skill.
-- Demonstrates: Correlated subquery
SELECT
    u.user_id,
    u.first_name || ' ' || u.last_name AS employee_name,
    s.skill_name,
    us.proficiency_level,
    (
        SELECT MAX(us2.proficiency_level)
        FROM CAREER_ORCHESTRATOR.USER_SKILLS us2
        WHERE us2.user_id = u.user_id
    ) AS max_proficiency
FROM CAREER_ORCHESTRATOR.USERS u
INNER JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON u.user_id = us.user_id
INNER JOIN CAREER_ORCHESTRATOR.SKILLS s
    ON us.skill_id = s.skill_id
WHERE us.proficiency_level = (
    SELECT MAX(us3.proficiency_level)
    FROM CAREER_ORCHESTRATOR.USER_SKILLS us3
    WHERE us3.user_id = u.user_id
)
ORDER BY u.user_id;

-- 6.10: GROUPING SETS - COMPREHENSIVE EXPERIENCE ANALYSIS
-- Purpose: Analyze experience distribution across different dimensions.
-- Demonstrates: GROUPING SETS for multi-dimensional aggregation
SELECT
    COALESCE(location, 'Unknown') AS location,
    COALESCE(current_role, 'Unknown') AS current_role,
    COUNT(*) AS employee_count,
    ROUND(AVG(years_of_experience), 2) AS avg_experience
FROM CAREER_ORCHESTRATOR.USERS
GROUP BY GROUPING SETS (
    (location),
    (current_role),
    (location, current_role),
    ()
)
ORDER BY location, current_role;

    SELECT DISTINCT
        r.role_id,
        r.role_name,
        r.min_experience,
        r.required_skill_level
    FROM CAREER_ORCHESTRATOR.JOB_ROLES r
    WHERE r.min_experience > 0
) next_role
    ON next_role.min_experience <= u.years_of_experience + 2
CROSS JOIN (
    SELECT
        ss.role_id,
        AVG(ss.required_level) AS avg_skill_level
    FROM CAREER_ORCHESTRATOR.ROLE_SKILLS ss
    WHERE ss.role_id IN (
        SELECT DISTINCT r.role_id
        FROM CAREER_ORCHESTRATOR.JOB_ROLES r
        WHERE r.min_experience <= u.years_of_experience + 2
    )
    GROUP BY ss.role_id
) cnt
    ON cnt.role_id = next_role.role_id
WHERE u.email = 'anitha.raman@email.com'
ORDER BY next_role.min_experience;

-- 6.4: WINDOW FUNCTIONS - EMPIRICAL SKILL DISTRIBUTION
-- Purpose: Rank skills by proficiency level across all employees.
-- Demonstrates: RANK, DENSE_RANK window functions
SELECT
    s.skill_name,
    s.skill_category,
    COUNT(us.user_id) AS user_count_with_skill,
    ROUND(AVG(us.proficiency_level), 2) AS avg_proficiency,
    RANK() OVER (ORDER BY AVG(us.proficiency_level) DESC) AS proficiency_rank,
    DENSE_RANK() OVER (ORDER BY AVG(us.proficiency_level) DESC) AS dense_proficiency_rank,
    NTILE(5) OVER (ORDER BY AVG(us.proficiency_level) DESC) AS skill_quartile
FROM CAREER_ORCHESTRATOR.SKILLS s
INNER JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
    ON s.skill_id = us.skill_id
GROUP BY
    s.skill_id,
    s.skill_name,
    s.skill_category
ORDER BY proficiency_rank;
