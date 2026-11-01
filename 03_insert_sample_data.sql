/*
==============================================================================
  Career Orchestrator - SAP HANA Cloud SQL Database
  File: 03_insert_sample_data.sql
  Purpose: Insert realistic sample records for the Career Orchestrator project.
  SAP HANA Cloud SQL - Compliant
==============================================================================
*/

-- RESET SEQUENCE FIRST (to avoid primary key conflicts on re-run)
-- Begin sequence resets for USERS and WORK_EXPERIENCE
DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'USERS_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'USERS_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'WORK_EXPERIENCE_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'WORK_EXPERIENCE_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;


DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'SKILLS_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'SKILLS_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'USER_SKILLS_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'USER_SKILLS_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'JOB_ROLES_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES

DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'ROLE_SKILLS_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'ROLE_SKILLS_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'LEARNING_RESOURCES_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'LEARNING_RESOURCES_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'LEARNING_PLANS_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'LEARNING_PLANS_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;

-- ============================================================================
-- INSERT DATA
-- ============================================================================

-- TABLE 1: USERS - Insert Anitha Raman
INSERT INTO CAREER_ORCHESTRATOR.USERS (user_id, email, first_name, last_name, date_of_birth, age, location, years_of_experience, current_role, profile_summary, created_at)
VALUES (CAREER_ORCHESTRATOR.USERS_seq.NEXTVAL,
        'anitha.raman@email.com',
        'Anitha',
        'Raman',
        TO_DATE('1983-04-15', 'YYYY-MM-DD'),
        42,
        'Coimbatore',
        15,
        'Administrative Coordinator',
        'Experienced administrative professional with 15 years of expertise in office management, team coordination, process optimization, and ERP systems. Seeking to leverage administrative expertise in operations and HR functions.',
        CURRENT_TIMESTAMP);

-- TABLE 2: WORK_EXPERIENCE - Insert samples
INSERT INTO CAREER_ORCHESTRATOR.WORK_EXPERIENCE (experience_id, user_id, company_name, position_title, start_date, end_date, location, is_current, created_at)
VALUES (CAREER_ORCHESTRATOR.WORK_EXPERIENCE_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'anitha.raman@email.com'),
        'Chennai Regional Office, ABC Ltd.',
        'Administrative Coordinator',
        TO_DATE('2011-03-14', 'YYYY-MM-DD'),
        TO_DATE('2023-08-31', 'YYYY-MM-DD'),
        'Chennai',
        FALSE,
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.WORK_EXPERIENCE (experience_id, user_id, company_name, position_title, start_date, end_date, location, is_current, created_at)
VALUES (CAREER_ORCHESTRATOR.WORK_EXPERIENCE_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'anitha.raman@email.com'),
        'Coimbatore Corporate Office, ABC Ltd.',
        'Administrative Coordinator',
        TO_DATE('2023-09-01', 'YYYY-MM-DD'),
        NULL,
        'Coimbatore',
        TRUE,
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.WORK_EXPERIENCE (experience_id, user_id, company_name, position_title, start_date, end_date, location, is_current, created_at)
VALUES (CAREER_ORCHESTRATOR.WORK_EXPERIENCE_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'anitha.raman@email.com'),
        'Regional Operations Pvt. Ltd.',
        'Operations Support Executive',
        TO_DATE('2008-06-01', 'YYYY-MM-DD'),
        TO_DATE('2011-03-13', 'YYYY-MM-DD'),
        'Coimbatore',
        FALSE,
        CURRENT_TIMESTAMP);

-- TABLE 3: SKILLS - Insert skills
INSERT INTO CAREER_ORCHESTRATOR.SKILLS (skill_id, skill_name, skill_category, proficiency_level, description, created_at)
VALUES (CAREER_ORCHESTRATOR.SKILLS_seq.NEXTVAL,
        'Communication',
        'Interpersonal',
        5,
        'Advanced written and verbal communication skills; excels in stakeholder communication and presentations.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.SKILLS (skill_id, skill_name, skill_category, proficiency_level, description, created_at)
VALUES (CAREER_ORCHESTRATOR.SKILLS_seq.NEXTVAL,
        'Microsoft Excel',
        'Technical',
        5,
        'Advanced Excel skills including complex formulas, pivot tables, data validation, and VBA macros.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.SKILLS (skill_id, skill_name, skill_category, proficiency_level, description, created_at)
VALUES (CAREER_ORCHESTRATOR.SKILLS_seq.NEXTVAL,
        'Data Management',
        'Technical',
        4,
        'Proficient in data entry, data validation, database management, and report generation.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.SKILLS (skill_id, skill_name, skill_category, proficiency_level, description, created_at)
VALUES (CAREER_ORCHESTRATOR.SKILLS_seq.NEXTVAL,
        'Scheduling',
        'Interpersonal',
        4,
        'Expert in scheduling appointments, managing calendars, and coordinating multi-party meetings.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.SKILLS (skill_id, skill_name, skill_category, proficiency_level, description, created_at)
VALUES (CAREER_ORCHESTRATOR.SKILLS_seq.NEXTVAL,
        'Team Coordination',
        'Leadership',
        4,
        'Strong ability to coordinate team activities, delegate tasks, and ensure timely completion of project milestones.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.SKILLS (skill_id, skill_name, skill_category, proficiency_level, description, created_at)
VALUES (CAREER_ORCHESTRATOR.SKILLS_seq.NEXTVAL,
        'Process Management',
        'Technical',
        5,
        'Extensive experience in end-to-end process mapping, documentation, and optimization of business processes.',
        CURRENT_TIMESTAMP);

  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'RECOMMENDATIONS_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'RECOMMENDATIONS_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;

INSERT INTO CAREER_ORCHESTRATOR.ROLE_SKILLS (role_skill_id, role_id, skill_id, required_level, notes, created_at)
VALUES (CAREER_ORCHESTRATOR.ROLE_SKILLS_seq.NEXTVAL,
        (SELECT role_id FROM CAREER_ORCHESTRATOR.JOB_ROLES WHERE role_name = 'Operations Analyst'),
        (SELECT skill_id FROM CAREER_ORCHESTRATOR.SKILLS WHERE skill_name = 'Data Management'),
        4,
        'Core skill for analyzing operational data to optimize processes.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.ROLE_SKILLS (role_skill_id, role_id, skill_id, required_level, notes, created_at)
VALUES (CAREER_ORCHESTRATOR.ROLE_SKILLS_seq.NEXTVAL,
        (SELECT role_id FROM CAREER_ORCHESTRATOR.JOB_ROLES WHERE role_name = 'Operations Analyst'),
        (SELECT skill_id FROM CAREER_ORCHESTRATOR.SKILLS WHERE skill_name = 'Communication'),
        4,
        'Required for presenting findings to stakeholders and cross-functional teams.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.ROLE_SKILLS (role_skill_id, role_id, skill_id, required_level, notes, created_at)
VALUES (CAREER_ORCHESTRATOR.ROLE_SKILLS_seq.NEXTVAL,
        (SELECT role_id FROM CAREER_ORCHESTRATOR.JOB_ROLES WHERE role_name = 'HR Operations Specialist'),
        (SELECT skill_id FROM CAREER_ORCHESTRATOR.SKILLS WHERE skill_name = 'Communication'),
        4,
        'Essential for employee interactions and policy communication.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.ROLE_SKILLS (role_skill_id, role_id, skill_id, required_level, notes, created_at)
VALUES (CAREER_ORCHESTRATOR.ROLE_SKILLS_seq.NEXTVAL,
        (SELECT role_id FROM CAREER_ORCHESTRATOR.JOB_ROLES WHERE role_name = 'HR Operations Specialist'),
        (SELECT skill_id FROM CAREER_ORCHESTRATOR.SKILLS WHERE skill_name = 'Scheduling'),
        3,
        'Required for coordinating interviews and managing employee schedules.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.ROLE_SKILLS (role_skill_id, role_id, skill_id, required_level, notes, created_at)
VALUES (CAREER_ORCHESTRATOR.ROLE_SKILLS_seq.NEXTVAL,
        (SELECT role_id FROM CAREER_ORCHESTRATOR.JOB_ROLES WHERE role_name = 'Project Coordinator'),
        (SELECT skill_id FROM CAREER_ORCHESTRATOR.SKILLS WHERE skill_name = 'Team Coordination'),
        4,
        'Core skill for managing team activities and ensuring project milestones.',
        CURRENT_TIMESTAMP);

END;

DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'WORK_SAMPLES_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'WORK_SAMPLES_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

DO BEGIN
  DECLARE seq_name NVARCHAR(255);

INSERT INTO CAREER_ORCHESTRATOR.ROLE_SKILLS (role_skill_id, role_id, skill_id, required_level, notes, created_at)
VALUES (CAREER_ORCHESTRATOR.ROLE_SKILLS_seq.NEXTVAL,
        (SELECT role_id FROM CAREER_ORCHESTRATOR.JOB_ROLES WHERE role_name = 'Business Operations Associate'),
        (SELECT skill_id FROM CAREER_ORCHESTRATOR.SKILLS WHERE skill_name = 'Microsoft Excel'),
        4,
        'Required for data analysis, reporting, and process documentation.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.ROLE_SKILLS (role_skill_id, role_id, skill_id, required_level, notes, created_at)
VALUES (CAREER_ORCHESTRATOR.ROLE_SKILLS_seq.NEXTVAL,
        (SELECT role_id FROM CAREER_ORCHESTRATOR.JOB_ROLES WHERE role_name = 'Business Operations Associate'),
        (SELECT skill_id FROM CAREER_ORCHESTRATOR.SKILLS WHERE skill_name = 'Data Management'),
        3,
        'Needed for maintaining operational data and generating reports.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.ROLE_SKILLS (role_skill_id, role_id, skill_id, required_level, notes, created_at)
VALUES (CAREER_ORCHESTRATOR.ROLE_SKILLS_seq.NEXTVAL,
        (SELECT role_id FROM CAREER_ORCHESTRATOR.JOB_ROLES WHERE role_name = 'Administrative Process Analyst'),
        (SELECT skill_id FROM CAREER_ORCHESTRATOR.SKILLS WHERE skill_name = 'Process Management'),
        5,
        'Critical skill for designing and optimizing administrative workflows.',
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.ROLE_SKILLS (role_skill_id, role_id, skill_id, required_level, notes, created_at)
VALUES (CAREER_ORCHESTRATOR.ROLE_SKILLS_seq.NEXTVAL,
        (SELECT role_id FROM CAREER_ORCHESTRATOR.JOB_ROLES WHERE role_name = 'Administrative Process Analyst'),
        (SELECT skill_id FROM CAREER_ORCHESTRATOR.SKILLS WHERE skill_name = 'Communication'),
        4,
        'Required for documenting processes and liaising with stakeholders.',
        CURRENT_TIMESTAMP);

-- TABLE 7: LEARNING_RESOURCES - Insert sample resources
INSERT INTO CAREER_ORCHESTRATOR.LEARNING_RESOURCES (resource_id, title, description, resource_type, url, estimated_hours, created_at)
VALUES (CAREER_ORCHESTRATOR.LEARNING_RESOURCES_seq.NEXTVAL,
        'Advanced Microsoft Excel for Business Analysts',
        'Comprehensive course covering complex formulas, pivot tables, and data visualization for business analysis.',
        'Course',
        'https://learning.link/excel-advanced',
        12.50,
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.LEARNING_RESOURCES (resource_id, title, description, resource_type, url, estimated_hours, created_at)
VALUES (CAREER_ORCHESTRATOR.LEARNING_RESOURCES_seq.NEXTVAL,
        'Leading High-Performing Teams',
        'Expert guide on team leadership, delegation, and performance management.',
        'Book',
        'https://learning.link/team-leadership',
        8.00,
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.LEARNING_RESOURCES (resource_id, title, description, resource_type, url, estimated_hours, created_at)
VALUES (CAREER_ORCHESTRATOR.LEARNING_RESOURCES_seq.NEXTVAL,
        'Business Process Reengineering Best Practices',
        'Article series on modern approaches to business process optimization.',
        'Article',
        'https://learning.link/bpr-best-practices',
        2.00,
        CURRENT_TIMESTAMP);

-- TABLE 8: LEARNING_PLANS - Insert learning goals
INSERT INTO CAREER_ORCHESTRATOR.LEARNING_PLANS (plan_id, user_id, resource_id, goal_description, target_completion_date, status, progress_percentage, created_at)
VALUES (CAREER_ORCHESTRATOR.LEARNING_PLANS_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'anitha.raman@email.com'),
        (SELECT resource_id FROM CAREER_ORCHESTRATOR.LEARNING_RESOURCES WHERE title = 'Advanced Microsoft Excel for Business Analysts'),
        'Complete advanced Excel course to qualify for Operations Analyst role.',
        TO_DATE('2026-12-31', 'YYYY-MM-DD'),
        'In Progress',
        40,
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.LEARNING_PLANS (plan_id, user_id, resource_id, goal_description, target_completion_date, status, progress_percentage, created_at)
VALUES (CAREER_ORCHESTRATOR.LEARNING_PLANS_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'anitha.raman@email.com'),

-- TABLE 9: RECOMMENDATIONS - Insert sample AI recommendations
INSERT INTO CAREER_ORCHESTRATOR.RECOMMENDATIONS (recommendation_id, user_id, recommended_role, rationale, confidence_score, is_approved, created_at)
VALUES (CAREER_ORCHESTRATOR.RECOMMENDATIONS_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'anitha.raman@email.com'),
        'HR Operations Specialist',
        'Strong communication and scheduling skills combined with 15 years of administrative experience make Anitha well-suited for HR operations.',
        85.50,
        FALSE,
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.RECOMMENDATIONS (recommendation_id, user_id, recommended_role, rationale, confidence_score, is_approved, created_at)
VALUES (CAREER_ORCHESTRATOR.RECOMMENDATIONS_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'anitha.raman@email.com'),
        'Project Coordinator',
        'Extensive team coordination experience and data management skills position Anitha well for project coordination.',
        78.25,
        FALSE,
        CURRENT_TIMESTAMP);

-- TABLE 10: WORK_SAMPLES - Insert sample work samples
INSERT INTO CAREER_ORCHESTRATOR.WORK_SAMPLES (work_sample_id, user_id, title, description, file_url, upload_date, created_at)
VALUES (CAREER_ORCHESTRATOR.WORK_SAMPLES_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'anitha.raman@email.com'),
        'Process Optimization Report - ABC Ltd.',
        'Comprehensive process optimization report for administrative workflows showing 20% efficiency improvement.',
        'https://files.samples.com/abc-process-optimization.pdf',
        TO_DATE('2023-09-15', 'YYYY-MM-DD'),
        CURRENT_TIMESTAMP);

INSERT INTO CAREER_ORCHESTRATOR.WORK_SAMPLES (work_sample_id, user_id, title, description, file_url, upload_date, created_at)
VALUES (CAREER_ORCHESTRATOR.WORK_SAMPLES_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'anitha.raman@email.com'),
        'Resource Schedule - Q3 2023',
        'Monthly resource schedule showing coordination of 15+ team members and third-party vendors across 3 sites.',
        'https://files.samples.com/q3-2023-resource-schedule.xlsx',
        TO_DATE('2023-10-01', 'YYYY-MM-DD'),
        CURRENT_TIMESTAMP);

-- TABLE 11: BIAS_AUDITS - Insert sample audit results
INSERT INTO CAREER_ORCHESTRATOR.BIAS_AUDITS (audit_id, audit_date, recommendation_id, reviewer_user_id, bias_findings, audit_result, created_at)
VALUES (CAREER_ORCHESTRATOR.BIAS_AUDITS_seq.NEXTVAL,
        CURRENT_TIMESTAMP,
        (SELECT recommendation_id FROM CAREER_ORCHESTRATOR.RECOMMENDATIONS WHERE recommended_role = 'HR Operations Specialist' ORDER BY created_at DESC LIMIT 1),
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'hr.reviewer@email.com'),
        'No significant bias detected. Recommendation considers age, location, and experience factors fairly.',
        'Pass',
        CURRENT_TIMESTAMP);

-- TABLE 12: HUMAN_REVIEWS - Insert human expert reviews
INSERT INTO CAREER_ORCHESTRATOR.HUMAN_REVIEWS (review_id, user_id, recommendation_id, reviewer_name, feedback, rating, created_at)
VALUES (CAREER_ORCHESTRATOR.HUMAN_REVIEWS_seq.NEXTVAL,
        (SELECT user_id FROM CAREER_ORCHESTRATOR.USERS WHERE email = 'hr.reviewer@email.com'),
        (SELECT recommendation_id FROM CAREER_ORCHESTRATOR.RECOMMENDATIONS WHERE recommended_role = 'HR Operations Specialist' ORDER BY created_at DESC LIMIT 1),
        'Dr. Priya Nair',
        'Anitha has excellent organizational skills and communication abilities. Her 15 years of hands-on experience with administrative processes will translate well to HR operations.',
        5,
        CURRENT_TIMESTAMP);

        (SELECT resource_id FROM CAREER_ORCHESTRATOR.LEARNING_RESOURCES WHERE title = 'Leading High-Performing Teams'),
        'Read book to develop leadership skills for Project Coordinator role.',
        TO_DATE('2026-10-30', 'YYYY-MM-DD'),
        'Not Started',
        0,
        CURRENT_TIMESTAMP);

  seq_name := 'BIAS_AUDITS_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'BIAS_AUDITS_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

DO BEGIN
  DECLARE seq_name NVARCHAR(255);
  seq_name := 'HUMAN_REVIEWS_seq';
  DECLARE continuation INTEGER;
  DECLARE sql_text NVARCHAR(500);
  SELECT COUNT(*) INTO continuation FROM SYS.M_SEQUENCES
   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'HUMAN_REVIEWS_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

   WHERE SEQUENCE_SCHEMA = 'CAREER_ORCHESTRATOR' AND SEQUENCE_NAME = 'JOB_ROLES_seq';
  IF continuation > 0 THEN
    sql_text := 'DROP SEQUENCE CAREER_ORCHESTRATOR.' || seq_name;
    EXECUTE IMMEDIATE :sql_text;
  END IF;
  sql_text := 'CREATE SEQUENCE CAREER_ORCHESTRATOR.' || seq_name || ' START WITH 1 INCREMENT BY 1';
  EXECUTE IMMEDIATE :sql_text;
END;

