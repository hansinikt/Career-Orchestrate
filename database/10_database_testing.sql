/*
==============================================================================
  Career Orchestrator - SAP HANA Cloud SQL Database
  File: 10_database_testing.sql
  Purpose: Database testing documentation and verification queries.
  SAP HANA Cloud SQL - Compliant
==============================================================================
*/

-- SECTION 1: SCHEMA VERIFICATION
-- Verify the CAREER_ORCHESTRATOR schema exists.
SELECT
    SCHEMA_NAME,
    SCHEMA_OWNER,
    DEFAULT_SCHEMA,
    SCHEMA_STATUS
FROM SYS.M_SCHEMAS
WHERE SCHEMA_NAME = 'CAREER_ORCHESTRATOR';

-- SECTION 2: TABLE COUNT VERIFICATION
-- Verify all 12 required tables exist and count rows.
SELECT 'USERS' AS table_name, COUNT(*) AS row_count FROM CAREER_ORCHESTRATOR.USERS
UNION ALL SELECT 'WORK_EXPERIENCE', COUNT(*) FROM CAREER_ORCHESTRATOR.WORK_EXPERIENCE
UNION ALL SELECT 'SKILLS', COUNT(*) FROM CAREER_ORCHESTRATOR.SKILLS
UNION ALL SELECT 'USER_SKILLS', COUNT(*) FROM CAREER_ORCHESTRATOR.USER_SKILLS
UNION ALL SELECT 'JOB_ROLES', COUNT(*) FROM CAREER_ORCHESTRATOR.JOB_ROLES
UNION ALL SELECT 'ROLE_SKILLS', COUNT(*) FROM CAREER_ORCHESTRATOR.ROLE_SKILLS
UNION ALL SELECT 'LEARNING_RESOURCES', COUNT(*) FROM CAREER_ORCHESTRATOR.LEARNING_RESOURCES
UNION ALL SELECT 'LEARNING_PLANS', COUNT(*) FROM CAREER_ORCHESTRATOR.LEARNING_PLANS
UNION ALL SELECT 'RECOMMENDATIONS', COUNT(*) FROM CAREER_ORCHESTRATOR.RECOMMENDATIONS
UNION ALL SELECT 'WORK_SAMPLES', COUNT(*) FROM CAREER_ORCHESTRATOR.WORK_SAMPLES
UNION ALL SELECT 'BIAS_AUDITS', COUNT(*) FROM CAREER_ORCHESTRATOR.BIAS_AUDITS
UNION ALL SELECT 'HUMAN_REVIEWS', COUNT(*) FROM CAREER_ORCHESTRATOR.HUMAN_REVIEWS
ORDER BY table_name;

-- SECTION 3: PRIMARY KEY VERIFICATION
-- Verify primary keys exist on all tables.
SELECT t.TABLE_NAME, k.CONSTRAINT_NAME, k.CONSTRAINT_TYPE
FROM SYS.M_TABLES t
INNER JOIN SYS.M_CONSTRAINTS k ON t.TABLE_NAME = k.TABLE_NAME
WHERE t.SCHEMA_NAME = 'CAREER_ORCHESTRATOR'
    AND k.CONSTRAINT_TYPE = 'PRIMARY KEY'
ORDER BY t.TABLE_NAME;

-- SECTION 4: FOREIGN KEY VERIFICATION
-- Verify all foreign key constraints exist.
SELECT t.TABLE_NAME, k.CONSTRAINT_NAME, k.CONSTRAINT_TYPE, k.REFERENCED_TABLE_NAME, k.POSITION
FROM SYS.M_TABLES t
INNER JOIN SYS.M_CONSTRAINTS k ON t.TABLE_NAME = k.TABLE_NAME
WHERE t.SCHEMA_NAME = 'CAREER_ORCHESTRATOR'
    AND k.CONSTRAINT_TYPE = 'REFERENTIAL'
ORDER BY t.TABLE_NAME, k.POSITION;

-- SECTION 5: SAMPLE DATA VERIFICATION
-- 5.1: Verify Anitha Raman record
SELECT user_id, email, first_name, last_name, age, location, years_of_experience, current_role, created_at
FROM CAREER_ORCHESTRATOR.USERS
WHERE email = 'anitha.raman@email.com';

-- 5.2: Verify sample skills exist
SELECT skill_id, skill_name, skill_category, proficiency_level
FROM CAREER_ORCHESTRATOR.SKILLS
WHERE skill_name IN ('Communication', 'Microsoft Excel', 'Data Management', 'Scheduling', 'Team Coordination', 'Process Management')
ORDER BY skill_name;

-- 5.3: Verify career roles exist
SELECT role_id, role_name, min_experience, required_skill_level
FROM CAREER_ORCHESTRATOR.JOB_ROLES

-- 6.1 Check for duplicate user IDs
SELECT COUNT(*) AS duplicate_count FROM (
    SELECT user_id FROM CAREER_ORCHESTRATOR.USERS GROUP BY user_id HAVING COUNT(*) > 1
) dup;

-- 6.2: Check for orphaned user_skill records
SELECT COUNT(*) AS orphan_count FROM CAREER_ORCHESTRATOR.USER_SKILLS us
LEFT JOIN CAREER_ORCHESTRATOR.USERS u ON us.user_id = u.user_id
WHERE u.user_id IS NULL;

-- 6.3: Check for orphaned skill records
SELECT COUNT(*) AS orphan_count FROM CAREER_ORCHESTRATOR.USER_SKILLS us
LEFT JOIN CAREER_ORCHESTRATOR.SKILLS s ON us.skill_id = s.skill_id
WHERE s.skill_id IS NULL;

-- 6.4: Check for orphaned work_experience records
SELECT COUNT(*) AS orphan_count FROM CAREER_ORCHESTRATOR.WORK_EXPERIENCE w
LEFT JOIN CAREER_ORCHESTRATOR.USERS u ON w.user_id = u.user_id
WHERE u.user_id IS NULL;

-- 6.5: Check for inconsistent proficiency levels
SELECT COUNT(*) AS invalid_proficiency FROM CAREER_ORCHESTRATOR.USER_SKILLS
WHERE proficiency_level < 1 OR proficiency_level > 5;

-- SECTION 7: INDEX VERIFICATION
-- Verify all indexes exist.
SELECT t.TABLE_NAME, i.INDEX_NAME, i.INDEX_TYPE, i.UNIQUENESS
FROM SYS.M_TABLES t
INNER JOIN SYS.M_INDEXES i ON t.TABLE_NAME = i.TABLE_NAME
WHERE t.SCHEMA_NAME = 'CAREER_ORCHESTRATOR'
    AND i.INDEX_TYPE IS NOT NULL
    AND i.INDEX_NAME NOT LIKE '%_PK%'
ORDER BY t.TABLE_NAME, i.INDEX_NAME;

-- SECTION 8: FOREIGN KEY REFERENTIAL INTEGRITY
-- Verify all foreign key references are satisfied.
SELECT 'WORK_EXPERIENCE' AS table_name, COUNT(*) AS orphan_count
FROM CAREER_ORCHESTRATOR.WORK_EXPERIENCE w
LEFT JOIN CAREER_ORCHESTRATOR.USERS u ON w.user_id = u.user_id
WHERE u.user_id IS NULL

UNION ALL SELECT 'USER_SKILLS', COUNT(*)
FROM CAREER_ORCHESTRATOR.USER_SKILLS us
LEFT JOIN CAREER_ORCHESTRATOR.USERS u ON us.user_id = u.user_id
WHERE u.user_id IS NULL

UNION ALL SELECT 'USER_SKILLS', COUNT(*)
FROM CAREER_ORCHESTRATOR.USER_SKILLS us
LEFT JOIN CAREER_ORCHESTRATOR.SKILLS s ON us.skill_id = s.skill_id
WHERE s.skill_id IS NULL

UNION ALL SELECT 'WORK_EXPERIENCE', COUNT(*)
FROM CAREER_ORCHESTRATOR.WORK_EXPERIENCE
WHERE user_id IS NULL;

-- SECTION 9: SAMPLE COUNT SUMMARY
-- Summarize total sample records inserted.
SELECT 'USERS' AS table_name, COUNT(*) AS record_count FROM CAREER_ORCHESTRATOR.USERS
UNION ALL SELECT 'WORK_EXPERIENCE', COUNT(*) FROM CAREER_ORCHESTRATOR.WORK_EXPERIENCE
UNION ALL SELECT 'SKILLS', COUNT(*) FROM CAREER_ORCHESTRATOR.SKILLS
UNION ALL SELECT 'USER_SKILLS', COUNT(*) FROM CAREER_ORCHESTRATOR.USER_SKILLS
UNION ALL SELECT 'JOB_ROLES', COUNT(*) FROM CAREER_ORCHESTRATOR.JOB_ROLES
UNION ALL SELECT 'ROLE_SKILLS', COUNT(*) FROM CAREER_ORCHESTRATOR.ROLE_SKILLS
UNION ALL SELECT 'LEARNING_RESOURCES', COUNT(*) FROM CAREER_ORCHESTRATOR.LEARNING_RESOURCES
UNION ALL SELECT 'LEARNING_PLANS', COUNT(*) FROM CAREER_ORCHESTRATOR.LEARNING_PLANS
UNION ALL SELECT 'RECOMMENDATIONS', COUNT(*) FROM CAREER_ORCHESTRATOR.RECOMMENDATIONS
UNION ALL SELECT 'WORK_SAMPLES', COUNT(*) FROM CAREER_ORCHESTRATOR.WORK_SAMPLES
UNION ALL SELECT 'BIAS_AUDITS', COUNT(*) FROM CAREER_ORCHESTRATOR.BIAS_AUDITS
UNION ALL SELECT 'HUMAN_REVIEWS', COUNT(*) FROM CAREER_ORCHESTRATOR.HUMAN_REVIEWS;

-- SECTION 10: RECOMMENDATION VERIFICATION
SELECT r.recommendation_id, u.first_name || ' ' || u.last_name AS employee_name,
       r.recommended_role, r.confidence_score, r.is_approved,
       b.audit_result, br.first_name || ' ' || br.last_name AS reviewer_name,
       r.created_at
FROM CAREER_ORCHESTRATOR.RECOMMENDATIONS r
INNER JOIN CAREER_ORCHESTRATOR.USERS u ON r.user_id = u.user_id
LEFT JOIN CAREER_ORCHESTRATOR.BIAS_AUDITS b ON r.recommendation_id = b.recommendation_id
LEFT JOIN CAREER_ORCHESTRATOR.USERS br ON b.reviewer_user_id = br.user_id
ORDER BY r.created_at DESC;

-- SECTION 11: SKILL COVERAGE REPORT
SELECT u.user_id, u.first_name || ' ' || u.last_name AS employee_name,
       COUNT(us.skill_id) AS skill_count,
       ROUND(AVG(us.proficiency_level), 2) AS avg_proficiency,
       SUM(CASE WHEN us.proficiency_level >= 4 THEN 1 ELSE 0 END) AS advanced_skills,
       SUM(CASE WHEN us.proficiency_level >= 3 THEN 1 ELSE 0 END) AS intermediate_skills,
       SUM(CASE WHEN us.proficiency_level < 3 THEN 1 ELSE 0 END) AS beginner_skills
FROM CAREER_ORCHESTRATOR.USERS u
LEFT JOIN CAREER_ORCHESTRATOR.USER_SKILLS us ON u.user_id = us.user_id
WHERE u.email = 'anitha.raman@email.com'
GROUP BY u.user_id, u.first_name, u.last_name;

WHERE role_name IN ('Operations Analyst', 'HR Operations Specialist', 'Project Coordinator', 'Business Operations Associate', 'Administrative Process Analyst')
ORDER BY role_name;
