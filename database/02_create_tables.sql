
-- TABLE 7: LEARNING_RESOURCES
-- Purpose: Reference table for learning content (articles, videos, courses, etc.)
CREATE TABLE LEARNING_RESOURCES (
    resource_id      BIGINT PRIMARY KEY,
    title            NVARCHAR(200) NOT NULL,
    description      CLOB,
    resource_type    NVARCHAR(50) NOT NULL CHECK (resource_type IN ('Article', 'Video', 'Course', 'Book', 'Document')),
    url              NVARCHAR(500),
    estimated_hours  DECIMAL(5, 2) CHECK (estimated_hours >= 0),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE LEARNING_RESOURCES IS 'Reference table for learning resources available to users.';
COMMENT ON COLUMN LEARNING_RESOURCES.resource_id   IS 'Primary key - unique resource identifier.';
COMMENT ON COLUMN LEARNING_RESOURCES.resource_type IS 'Type of resource; validated against allowed list.';

-- TABLE 8: LEARNING_PLANS
-- Purpose: Tracks user learning goals and progress
CREATE TABLE LEARNING_PLANS (
    plan_id                  BIGINT PRIMARY KEY,
    user_id                  BIGINT NOT NULL,
    resource_id              BIGINT,
    goal_description         NVARCHAR(300) NOT NULL,
    target_completion_date   DATE NOT NULL CHECK (target_completion_date >= CURRENT_DATE),
    status                   NVARCHAR(50) NOT NULL CHECK (status IN ('Not Started', 'In Progress', 'Completed', 'On Hold')),
    progress_percentage      INT CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    created_at               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT FK_LEARNING_PLANS_USER
        FOREIGN KEY (user_id) REFERENCES USERS(user_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION,

    CONSTRAINT FK_LEARNING_PLANS_RESOURCE
        FOREIGN KEY (resource_id) REFERENCES LEARNING_RESOURCES(resource_id)
        ON DELETE SET NULL
        ON UPDATE NO ACTION
);

COMMENT ON TABLE LEARNING_PLANS IS 'Tracks individual learning goals and progress for users.';
COMMENT ON COLUMN LEARNING_PLANS.plan_id             IS 'Primary key - unique plan identifier.';
COMMENT ON COLUMN LEARNING_PLANS.user_id             IS 'Foreign key referencing USERS.user_id.';
COMMENT ON COLUMN LEARNING_PLANS.status              IS 'Current status of the plan; validated against allowed values.';
COMMENT ON COLUMN LEARNING_PLANS.progress_percentage IS 'Completion progress from 0 to 100 percent.';

-- TABLE 9: RECOMMENDATIONS
-- Purpose: Stores AI-generated career recommendations
CREATE TABLE RECOMMENDATIONS (
    recommendation_id BIGINT PRIMARY KEY,
    user_id           BIGINT NOT NULL,
    recommended_role  NVARCHAR(100) NOT NULL,
    rationale         CLOB,
    confidence_score  DECIMAL(5, 2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 100),
    is_approved       BOOLEAN DEFAULT FALSE,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT FK_RECOMMENDATIONS_USER
        FOREIGN KEY (user_id) REFERENCES USERS(user_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

COMMENT ON TABLE RECOMMENDATIONS IS 'Stores AI-generated career path recommendations.';
COMMENT ON COLUMN RECOMMENDATIONS.recommendation_id IS 'Primary key - unique recommendation identifier.';
COMMENT ON COLUMN RECOMMENDATIONS.user_id           IS 'Foreign key referencing USERS.user_id.';
COMMENT ON COLUMN RECOMMENDATIONS.confidence_score  IS 'AI confidence score 0-100 for the recommendation.';

-- TABLE 10: WORK_SAMPLES
-- Purpose: Repository for user work samples / portfolio items
CREATE TABLE WORK_SAMPLES (
    work_sample_id BIGINT PRIMARY KEY,
    user_id        BIGINT NOT NULL,
    title          NVARCHAR(200) NOT NULL,
    description    CLOB,
    file_url       NVARCHAR(500),
    upload_date    DATE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT FK_WORK_SAMPLES_USER
        FOREIGN KEY (user_id) REFERENCES USERS(user_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION
);

COMMENT ON TABLE WORK_SAMPLES IS 'Repository for user work samples / portfolio items.';
COMMENT ON COLUMN WORK_SAMPLES.work_sample_id IS 'Primary key - unique work sample identifier.';
COMMENT ON COLUMN WORK_SAMPLES.user_id        IS 'Foreign key referencing USERS.user_id.';



-- TABLE 11: BIAS_AUDITS
-- Purpose: Records fairness audit results for AI recommendations
CREATE TABLE BIAS_AUDITS (
    audit_id         BIGINT PRIMARY KEY,
    audit_date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommendation_id BIGINT,
    reviewer_user_id BIGINT,
    bias_findings    CLOB,
    audit_result     NVARCHAR(50) NOT NULL CHECK (audit_result IN ('Pass', 'Fail', 'Needs Review')),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT FK_BIAS_AUDITS_RECOMMENDATION
        FOREIGN KEY (recommendation_id) REFERENCES RECOMMENDATIONS(recommendation_id)
        ON DELETE SET NULL
        ON UPDATE NO ACTION,

    CONSTRAINT FK_BIAS_AUDITS_REVIEWER
        FOREIGN KEY (reviewer_user_id) REFERENCES USERS(user_id)
        ON DELETE SET NULL
        ON UPDATE NO ACTION
);

COMMENT ON TABLE BIAS_AUDITS IS 'Records fairness audit results for AI recommendations.';
COMMENT ON COLUMN BIAS_AUDITS.audit_id         IS 'Primary key - unique audit identifier.';
COMMENT ON COLUMN BIAS_AUDITS.recommendation_id IS 'Foreign key referencing RECOMMENDATIONS.recommendation_id.';
COMMENT ON COLUMN BIAS_AUDITS.audit_result     IS 'Audit outcome; validated against allowed values.';

-- TABLE 12: HUMAN_REVIEWS
-- Purpose: Stores human expert feedback and ratings on AI recommendations
CREATE TABLE HUMAN_REVIEWS (
    review_id         BIGINT PRIMARY KEY,
    user_id           BIGINT NOT NULL,
    recommendation_id BIGINT,
    reviewer_name     NVARCHAR(150) NOT NULL,
    feedback          CLOB,
    rating            INT CHECK (rating BETWEEN 1 AND 5),
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT FK_HUMAN_REVIEWS_USER
        FOREIGN KEY (user_id) REFERENCES USERS(user_id)
        ON DELETE CASCADE
        ON UPDATE NO ACTION,

    CONSTRAINT FK_HUMAN_REVIEWS_RECOMMENDATION
        FOREIGN KEY (recommendation_id) REFERENCES RECOMMENDATIONS(recommendation_id)
        ON DELETE SET NULL
        ON UPDATE NO ACTION
);

COMMENT ON TABLE HUMAN_REVIEWS IS 'Stores human expert feedback and ratings on AI recommendations.';
COMMENT ON COLUMN HUMAN_REVIEWS.review_id       IS 'Primary key - unique review identifier.';
COMMENT ON COLUMN HUMAN_REVIEWS.user_id         IS 'Foreign key referencing USERS.user_id.';
COMMENT ON COLUMN HUMAN_REVIEWS.rating          IS 'Expert rating from 1 to 5 stars.';

