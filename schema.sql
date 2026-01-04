PRAGMA foreign_keys = ON;

-- =========================
-- USERS
-- =========================
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL
);

-- =========================
-- DOCTORS
-- =========================
CREATE TABLE IF NOT EXISTS doctors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  branch TEXT NOT NULL,
  experience INTEGER NOT NULL,
  address TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'AVAILABLE',

  -- optional link to users doctor account (can be NULL)
  user_id INTEGER UNIQUE,

  -- temp login for doctor panel
  email TEXT UNIQUE,
  password TEXT
);

-- =========================
-- APPOINTMENTS (SCHEDULED)
-- =========================
CREATE TABLE IF NOT EXISTS appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  doctor_id INTEGER NOT NULL,

  status TEXT NOT NULL DEFAULT 'WAITING',

  created_at INTEGER DEFAULT (strftime('%s','now')),
  responded_at INTEGER,
  completed_at INTEGER,

  -- scheduling
  appt_date TEXT,  -- YYYY-MM-DD
  appt_time TEXT,  -- HH:MM

  -- doctor notes
  note TEXT,

  FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);
