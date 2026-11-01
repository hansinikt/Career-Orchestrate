/*
==============================================================================
  Career Orchestrator - SAP HANA Cloud SQL Database
  ================================================
  File: 01_create_schema.sql
  Purpose: Create the CAREER_ORCHESTRATOR schema (if not already exists)
  SAP HANA Cloud SQL - Compliant
==============================================================================
*/

-- ============================================================================
-- STEP 1: CREATE SCHEMA
-- ============================================================================
-- Note: The following statement will fail if the user does not have the
-- required privileges. In SAP HANA Database Explorer, run this as a user
-- with ALTER ANY SCHEMA privilege (e.g., SYSTEM).
--
-- If the schema already exists, this statement will throw an error.
-- To avoid failures when re-running, we use a control query to check first.
-- ============================================================================

DO BEGIN
  DECLARE schema_exists NVARCHAR(100);

  -- Check if the schema already exists in the catalog
  SELECT SCHEMA_NAME
    INTO schema_exists
    FROM SYS.M_SCHEMAS
   WHERE SCHEMA_NAME = 'CAREER_ORCHESTRATOR';

  -- If the schema does not exist, create it
  IF schema_exists IS NULL THEN
    EXECUTE IMMEDIATE 'CREATE SCHEMA CAREER_ORCHESTRATOR';
    SELECT 'Schema CAREER_ORCHESTRATOR created successfully.' AS MESSAGE FROM DUMMY;
  ELSE
    SELECT 'Schema CAREER_ORCHESTRATOR already exists. No action needed.' AS MESSAGE FROM DUMMY;
  END IF;
END;

-- ============================================================================
-- STEP 2: SET SCHEMA AS CURRENT (for subsequent statements)
-- ============================================================================
-- Note: This statement requires ownership or ALTER privilege on the schema.
-- In SAP HANA Database Explorer, you can run this after creating the schema.
-- ============================================================================

SET SCHEMA CAREER_ORCHESTRATOR;
