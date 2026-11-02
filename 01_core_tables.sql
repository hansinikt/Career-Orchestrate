/* =============================================================================
   Career Orchestrator - SAP HANA Cloud SQL Database
   =============================================================================
     File: 01_core_tables.sql
     Purpose: Create core tables (Tables 1-6).

     Order matters for FK references:
       1. USERS (no FK dependencies)
       2. JOB_ROLES (no FK dependencies)
       3. SKILLS (no FK dependencies)
       4. WORK_EXPERIENCE (FK -> USERS)
       5. USER_SKILLS (FK -> USERS, SKILLS)
       6. ROLE_SKILLS (FK -> JOB_ROLES, SKILLS)

     Run AFTER 01_create_schema.sql and BEFORE 02_create_tables.sql.
   ============================================================================= */

-- TABLE 1: USERS
CREATE TABLE USERS (
    user_id              BIGINT PRIMARY KEY,
    email                NVARCHAR(255) NOT NULL UNIQUE,
    first_name           NVARCHAR(100) NOT NULL,
    last_name            NVARCHAR(100) NOT NULL,
    location             NVARCHAR(100),
    years_of_experience  INT CHECK (years_of_experience >= 0),
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE USERS IS 'User profiles for job seekers and employees.';
COMMENT ON COLUMN USERS.user_id              IS 'Primary key - unique user identifier.';
COMMENT ON COLUMN USERS.email                IS 'User email address (unique).';
COMMENT ON COLUMN USERS.first_name           IS 'User first name.';
COMMENT ON COLUMN USERS.last_name            IS 'User last name.';
COMMENT ON COLUMN USERS.location             IS 'User location/region.';
COMMENT ON COLUMN USERS.years_of_experience  IS 'Years of professional experience.';
COMMENT ON COLUMN USERS.created_at           IS 'Timestamp of record creation.';

-- TABLE 2: JOB_ROLES
CREATE TABLE JOB_ROLES (
    role_id            BIGINT PRIMARY KEY,
    role_name          NVARCHAR(100) NOT NULL UNIQUE,
    role_description   NVARCHAR(500)
);

COMMENT ON TABLE JOB_ROLES IS 'Reference table for job roles.';
COMMENT ON COLUMN JOB_ROLES.role_id        IS 'Primary key - unique role identifier.';
COMMENT ON COLUMN JOB_ROLES.role_name      IS 'Name of the job role (unique).';
COMMENT ON COLUMN JOB_ROLES.role_description IS 'Description of the job role.';

-- TABLE 3: SKILLS
CREATE TABLE SKILLS (
    skill_id       BIGINT PRIMARY KEY,
    skill_name     NVARCHAR(100) NOT NULL UNIQUE,
    skill_category NVARCHAR(100) NOT NULL
);

COMMENT ON TABLE SKILLS IS 'Reference table for skill catalog.';
COMMENT ON COLUMN SKILLS.skill_id       IS 'Primary key - unique skill identifier.';
COMMENT ON COLUMN SKILLS.skill_name     IS 'Name of the skill (unique).';
COMMENT ON COLUMN SKILLS.skill_category IS 'Category of the skill.';

-- TABLE 4: WORK_EXPERIENCE
CREATE TABLE WORK_EXPERIENCE (
    experience_id BIGINT PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    company_name  NVARCHAR(200) NOT NULL,
    position      NVARCHAR(100) NOT NULL,
    start_date    DATE NOT NULL,
    end_date      DATE,
    is_current    BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT FK_WORK_EXPERIENCE_USER
        FOREIGN KEY (user_id) REFERENCES USERS(user_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

COMMENT ON TABLE WORK_EXPERIENCE IS 'User work experience history.';
COMMENT ON COLUMN WORK_EXPERIENCE.experience_id IS 'Primary key - unique experience identifier.';
COMMENT ON COLUMN WORK_EXPERIENCE.user_id       IS 'Foreign key referencing USERS.user_id.';
COMMENT ON COLUMN WORK_EXPERIENCE.company_name  IS 'Company name for the work experience.';
COMMENT ON COLUMN WORK_EXPERIENCE.position      IS 'Job position held.';
COMMENT ON COLUMN WORK_EXPERIENCE.start_date    IS 'Start date of the work experience.';
COMMENT ON COLUMN WORK_EXPERIENCE.end_date      IS 'End date of the work experience (nullable if current).';
COMMENT ON COLUMN WORK_EXPERIENCE.is_current    IS 'Flag indicating if this experience is current.';
COMMENT ON COLUMN WORK_EXPERIENCE.created_at    IS 'Timestamp of record creation.';

-- TABLE 5: USER_SKILLS
CREATE TABLE USER_SKILLS (
    user_skill_id     BIGINT PRIMARY KEY,
    user_id           BIGINT NOT NULL,
    skill_id          BIGINT NOT NULL,
    proficiency_level INT CHECK (proficiency_level >= 0 AND proficiency_level <= 5),
    acquired_date     DATE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT FK_USER_SKILLS_USER
        FOREIGN KEY (user_id) REFERENCES USERS(user_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION,

    CONSTRAINT FK_USER_SKILLS_SKILL
        FOREIGN KEY (skill_id) REFERENCES SKILLS(skill_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

COMMENT ON TABLE USER_SKILLS IS 'Junction table linking users to their skills with proficiency levels.';
COMMENT ON COLUMN USER_SKILLS.user_skill_id   IS 'Primary key - unique user-skill record identifier.';
COMMENT ON COLUMN USER_SKILLS.user_id         IS 'Foreign key referencing USERS.user_id.';
COMMENT ON COLUMN USER_SKILLS.skill_id        IS 'Foreign key referencing SKILLS.skill_id.';
COMMENT ON COLUMN USER_SKILLS.proficiency_level IS 'Proficiency level 1-5 for the skill.';
COMMENT ON COLUMN USER_SKILLS.acquired_date   IS 'Date the skill was acquired.';
COMMENT ON COLUMN USER_SKILLS.created_at      IS 'Timestamp of record creation.';

-- TABLE 6: ROLE_SKILLS
CREATE TABLE ROLE_SKILLS (
    role_skill_id     BIGINT PRIMARY KEY,
    role_id           BIGINT NOT NULL,
    skill_id          BIGINT NOT NULL,
    proficiency_level INT CHECK (proficiency_level >= 0 AND proficiency_level <= 5),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT FK_ROLE_SKILLS_ROLE
        FOREIGN KEY (role_id) REFERENCES JOB_ROLES(role_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION,

    CONSTRAINT FK_ROLE_SKILLS_SKILL
        FOREIGN KEY (skill_id) REFERENCES SKILLS(skill_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

COMMENT ON TABLE ROLE_SKILLS IS 'Junction table linking job roles to required skills.';
COMMENT ON COLUMN ROLE_SKILLS.role_skill_id   IS 'Primary key - unique role-skill record identifier.';
COMMENT ON COLUMN ROLE_SKILLS.role_id         IS 'Foreign key referencing JOB_ROLES.role_id.';
COMMENT ON COLUMN ROLE_SKILLS.skill_id        IS 'Foreign key referencing SKILLS.skill_id.';
COMMENT ON COLUMN ROLE_SKILLS.proficiency_level IS 'Required proficiency level 1-5 for the skill in the role.';
COMMENT ON COLUMN ROLE_SKILLS.created_at      IS 'Timestamp of record creation.';
