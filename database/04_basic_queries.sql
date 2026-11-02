/*
==============================================================================
  Career Orchestrator - SAP HANA Cloud SQL Database
  File: 04_basic_queries.sql
  Purpose: Basic SELECT, UPDATE, DELETE queries demonstrating fundamental
           SAP HANA SQL operations.
  SAP HANA Cloud SQL - Compliant
==============================================================================
*/

-- 4.1: SELECT ALL EMPLOYEES
-- Purpose: Retrieve all user records with basic information.
-- Demonstrates: SELECT, basic column selection, ORDER BY
SELECT
    user_id,
    email,
    first_name,
    last_name,
    age,
    location,
    years_of_experience,
    current_role,
    created_at
FROM CAREER_ORCHESTRATOR.USERS
ORDER BY last_name, first_name;

-- 4.2: SELECT SPECIFIC EMPLOYEE DETAIL
-- Purpose: Retrieve detailed information for Anitha Raman.
-- Demonstrates: WHERE clause, column aliasing
SELECT
    user_id AS employee_id,
    email,
    first_name || ' ' || last_name AS full_name,
    age,
    location,
    years_of_experience,
    current_role,
    profile_summary
FROM CAREER_ORCHESTRATOR.USERS
WHERE email = 'anitha.raman@email.com';

-- 4.3: UPDATE RECORD - Update Last Modified Timestamp
-- Purpose: Simulate updating the last modified timestamp for a record.
-- Demonstrates: UPDATE, SET, WHERE clause
-- Note: In a production system, this would typically be handled by a trigger
--       or application code. SAP HANA does not support DEFAULT ON UPDATE.
UPDATE CAREER_ORCHESTRATOR.USERS
SET updated_at = CURRENT_TIMESTAMP

-- 4.6: AGGREGATE - COUNT USERS
-- Purpose: Count total number of users in the system.
-- Demonstrates: COUNT aggregate function
SELECT
    COUNT(*) AS total_users,
    COUNT(DISTINCT location) AS unique_locations
FROM CAREER_ORCHESTRATOR.USERS;

-- 4.7: AGGREGATE - AVERAGE EXPERIENCE
-- Purpose: Calculate average years of experience across all users.
-- Demonstrates: AVG aggregate function
SELECT
    ROUND(AVG(years_of_experience), 2) AS avg_years_experience,
    MIN(years_of_experience) AS min_years_experience,
    MAX(years_of_experience) AS max_years_experience
FROM CAREER_ORCHESTRATOR.USERS;

-- 4.8: AGGREGATE - GROUP BY LOCATION
-- Purpose: Count users and average experience per location.
-- Demonstrates: GROUP BY, aggregate functions with GROUP BY
SELECT
    location,
    COUNT(*) AS user_count,
    ROUND(AVG(years_of_experience), 2) AS avg_experience
FROM CAREER_ORCHESTRATOR.USERS
WHERE location IS NOT NULL
GROUP BY location
ORDER BY user_count DESC;

-- 4.9: AGGREGATE - HAVING CLAUSE
-- Purpose: Find locations with more than 1 user.
-- Demonstrates: GROUP BY with HAVING clause
SELECT
    location,
    COUNT(*) AS user_count
FROM CAREER_ORCHESTRATOR.USERS
WHERE location IS NOT NULL
GROUP BY location
HAVING COUNT(*) > 1
ORDER BY user_count DESC;

-- 4.10: SUBQUERY - FIND USERS WITH 10+ YEARS EXPERIENCE
-- Purpose: Find users with significant experience for mentoring programs.
-- Demonstrates: Subquery in WHERE clause
SELECT
    user_id,
    first_name,
    last_name,
    years_of_experience,
    current_role
FROM CAREER_ORCHESTRATOR.USERS
WHERE years_of_experience > (
    SELECT AVG(years_of_experience)
    FROM CAREER_ORCHESTRATOR.USERS
)
ORDER BY years_of_experience DESC;

-- 4.11: CASE STATEMENT - DISPATCH LEVEL
-- Purpose: Categorize users based on years of experience.
-- Demonstrates: CASE statement
SELECT
    user_id,
    first_name,
    last_name,
    years_of_experience,
    CASE
        WHEN years_of_experience < 5 THEN 'Junior'
        WHEN years_of_experience < 10 THEN 'Mid-Level'
        WHEN years_of_experience < 15 THEN 'Senior'
        ELSE 'Expert/Principal'
    END AS experience_level,
    CASE
        WHEN location IS NULL THEN 'Not Specified'
        WHEN LENGTH(TRIM(location)) = 0 THEN 'Not Specified'
        ELSE UPPER(SUBSTRING(location, 1, 1)) || SUBSTRING(location, 2)
    END AS formatted_location
FROM CAREER_ORCHESTRATOR.USERS
ORDER BY experience_level, years_of_experience DESC;

WHERE email = 'anitha.raman@email.com';

-- 4.4: VIEW UPDATE EFFECT (SELECT after UPDATE)
-- Purpose: Verify the update was applied.
-- Demonstrates: SELECT after UPDATE
SELECT
    user_id,
    email,
    updated_at
FROM CAREER_ORCHESTRATOR.USERS
WHERE email = 'anitha.raman@email.com';

-- 4.5: DELETE WITH CHECK - Demonstrate safe deletion pattern
-- Purpose: Show how to delete a record with proper table locking consideration.
--          This query is for demonstration only and is NOT executed.
-- Demonstrates: DELETE, WHERE clause
-- Example (commented out - NOT EXECUTED):
-- DELETE FROM CAREER_ORCHESTRATOR.USERS
-- WHERE email = 'test.user@email.com';
