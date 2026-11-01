/*
==============================================================================
  Career Orchestrator - SAP HANA Cloud SQL Database
  File: 08_stored_procedures.sql
  Purpose: Stored procedures for Career Orchestrator database operations.
  SAP HANA Cloud SQL - Compliant
==============================================================================
*/

-- STORED PROCEDURE 1: GET_EMPLOYEE_SKILL_SUMMARY
-- Purpose: Returns a summary of an employee's skills, proficiency levels,
--          and experience metrics.
CREATE PROCEDURE CAREER_ORCHESTRATOR.GET_EMPLOYEE_SKILL_SUMMARY
(
    IN p_employee_email NVARCHAR(255),
    OUT p_skill_count INT,
    OUT p_avg_proficiency DECIMAL(5,2),
    OUT p_experience_tier NVARCHAR(50)
)
LANGUAGE SQLSCRIPT
SQL SECURITY DEFINER
AS
BEGIN
    -- Get skill count and average proficiency
    SELECT
        COUNT(us.skill_id) INTO p_skill_count,
        ROUND(AVG(us.proficiency_level), 2) INTO p_avg_proficiency
    FROM CAREER_ORCHESTRATOR.USER_SKILLS us
    INNER JOIN CAREER_ORCHESTRATOR.USERS u
        ON us.user_id = u.user_id
    WHERE u.email = p_employee_email;

    -- Determine experience tier
    SELECT
        CASE
            WHEN u.years_of_experience < 5 THEN 'Junior'
            WHEN u.years_of_experience < 10 THEN 'Mid-Level'
            WHEN u.years_of_experience < 15 THEN 'Senior'
            ELSE 'Expert/Principal'
        END INTO p_experience_tier
    FROM CAREER_ORCHESTRATOR.USERS u
    WHERE u.email = p_employee_email;
END;

-- STORED PROCEDURE 2: GET_SKILL_PROFILE_FOR_EMPLOYEE
-- Purpose: Returns a comprehensive skill profile for an employee.
CREATE PROCEDURE CAREER_ORCHESTRATOR.GET_SKILL_PROFILE_FOR_EMPLOYEE
(
    IN p_employee_email NVARCHAR(255)
)
LANGUAGE SQLSCRIPT
SQL SECURITY DEFINER
AS
BEGIN
    SELECT
        u.user_id,
        u.first_name || ' ' || u.last_name AS employee_name,
        u.current_role,
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
        s.skill_category AS domain_category
    FROM CAREER_ORCHESTRATOR.USERS u
    INNER JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
        ON u.user_id = us.user_id
    INNER JOIN CAREER_ORCHESTRATOR.SKILLS s
        ON us.skill_id = s.skill_id
    WHERE u.email = p_employee_email
    ORDER BY s.skill_category, s.skill_name;
END;

-- STORED PROCEDURE 3: GET_CAREER_GAP_ANALYSIS
-- Purpose: Returns skill gaps for an employee against a target job role.
CREATE PROCEDURE CAREER_ORCHESTRATOR.GET_CAREER_GAP_ANALYSIS
(
    IN p_employee_email NVARCHAR(255),
    IN p_target_role NVARCHAR(100)
)
LANGUAGE SQLSCRIPT
SQL SECURITY DEFINER
AS
BEGIN
    SELECT
        u.first_name || ' ' || u.last_name AS employee_name,
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
            ELSE 'EXCEEDS'
        END AS gap_status
    FROM CAREER_ORCHESTRATOR.JOB_ROLES r
    CROSS JOIN CAREER_ORCHESTRATOR.USERS u
    INNER JOIN CAREER_ORCHESTRATOR.ROLE_SKILLS rs
        ON r.role_id = rs.role_id
    INNER JOIN CAREER_ORCHESTRATOR.SKILLS s
        ON rs.skill_id = s.skill_id
    LEFT JOIN CAREER_ORCHESTRATOR.USER_SKILLS us
        ON u.user_id = us.user_id AND us.skill_id = s.skill_id
    WHERE u.email = p_employee_email

-- STORED PROCEDURE 4: UPDATE_USER_PROFILE
-- Purpose: Updates user profile information and timestamp.
CREATE PROCEDURE CAREER_ORCHESTRATOR.UPDATE_USER_PROFILE
(
    IN p_user_id BIGINT,
    IN p_location NVARCHAR(100),
    IN p_current_role NVARCHAR(100),
    IN p_profile_summary CLOB
)
LANGUAGE SQLSCRIPT
SQL SECURITY DEFINER
AS
BEGIN
    UPDATE CAREER_ORCHESTRATOR.USERS
    SET
        location = p_location,
        current_role = p_current_role,
        profile_summary = p_profile_summary,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id;

    -- Return success message
    SELECT
        'Profile updated successfully for user_id = ' || p_user_id AS status_message
    FROM DUMMY;
END;

-- STORED PROCEDURE 5: GET_GLOBALLY_REQUIRED_SKILLS
-- Purpose: Returns skills that are commonly required across multiple roles.
CREATE PROCEDURE CAREER_ORCHESTRATOR.GET_GLOBALLY_REQUIRED_SKILLS
(
    IN p_min_roles INT DEFAULT 2
)
LANGUAGE SQLSCRIPT
SQL SECURITY DEFINER
AS
BEGIN
    SELECT
        s.skill_id,
        s.skill_name,
        s.skill_category,
        COUNT(rs.role_id) AS roles_requiring,
        ROUND(AVG(rs.required_level), 2) AS avg_required_level,
        LISTAGG(s.skill_name, ', ') WITHIN GROUP (ORDER BY s.skill_name)
            AS roles_list
    FROM CAREER_ORCHESTRATOR.SKILLS s
    INNER JOIN CAREER_ORCHESTRATOR.ROLE_SKILLS rs
        ON s.skill_id = rs.skill_id
    GROUP BY s.skill_id, s.skill_name, s.skill_category
    HAVING COUNT(rs.role_id) >= p_min_roles
    ORDER BY roles_requiring DESC;
END;

        AND r.role_name = p_target_role
    ORDER BY s.skill_name;
END;
