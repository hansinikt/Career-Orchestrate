-- User data only. The catalogue (skills, roles, courses) lives in data/v2/*.json under Git.
CREATE TABLE IF NOT EXISTS profiles (
  profile_id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  current_role TEXT,
  work_examples TEXT NOT NULL,
  declared_skills TEXT NOT NULL,
  stated_goal_role_id TEXT,
  preferences TEXT,
  motivation TEXT,
  consent_at TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS extractions (
  profile_id TEXT PRIMARY KEY REFERENCES profiles(profile_id) ON DELETE CASCADE,
  payload TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS confirmations (
  profile_id TEXT PRIMARY KEY REFERENCES profiles(profile_id) ON DELETE CASCADE,
  payload TEXT NOT NULL,
  confirmed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans (
  plan_id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
  role_id TEXT NOT NULL,
  payload TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS progress (
  plan_id TEXT NOT NULL REFERENCES plans(plan_id) ON DELETE CASCADE,
  step_order INTEGER NOT NULL,
  percent INTEGER NOT NULL,
  hours_logged REAL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (plan_id, step_order)
);

CREATE TABLE IF NOT EXISTS messages (
  message_id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
  plan_id TEXT,
  style TEXT NOT NULL,
  event TEXT NOT NULL,
  text TEXT NOT NULL,
  suggested_action TEXT NOT NULL,
  helpful INTEGER,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audits (
  audit_id TEXT PRIMARY KEY,
  profile_id TEXT NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
  payload TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  at TEXT NOT NULL,
  actor TEXT NOT NULL,
  action TEXT NOT NULL,
  profile_id TEXT,
  detail TEXT
);
