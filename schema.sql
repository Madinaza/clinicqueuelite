PRAGMA foreign_keys = ON;

-- =========================
-- USERS (patients + admin)
-- =========================
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('patient','ADMIN')),
  created_at INTEGER DEFAULT (strftime('%s','now'))
);

-- =========================
-- DOCTORS
-- =========================
CREATE TABLE IF NOT EXISTS doctors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  branch TEXT NOT NULL,
  experience INTEGER DEFAULT 0,
  address TEXT DEFAULT '',
  status TEXT NOT NULL DEFAULT 'AVAILABLE' CHECK(status IN ('AVAILABLE','BUSY','OFFLINE')),

  -- link to users table (optional)
  user_id INTEGER UNIQUE,

  -- temp doctor login (optional)
  email TEXT UNIQUE,
  password TEXT
);

-- =========================
-- APPOINTMENTS / QUEUE
-- =========================
CREATE TABLE IF NOT EXISTS appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  doctor_id INTEGER NOT NULL,

  status TEXT NOT NULL DEFAULT 'WAITING'
    CHECK(status IN ('WAITING','ACCEPTED','IN_PROGRESS','DONE','REJECTED','CANCELLED')),

  note TEXT,
  created_at INTEGER NOT NULL DEFAULT (strftime('%s','now')),
  responded_at INTEGER,
  completed_at INTEGER,

  FOREIGN KEY(patient_id) REFERENCES users(id),
  FOREIGN KEY(doctor_id) REFERENCES doctors(id)
);

CREATE INDEX IF NOT EXISTS idx_appt_patient ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appt_doctor ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appt_status ON appointments(status);
