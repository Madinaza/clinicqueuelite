PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS doctors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER UNIQUE,
  name TEXT NOT NULL,
  branch TEXT NOT NULL,
  experience INTEGER NOT NULL,
  address TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'AVAILABLE',
  email TEXT UNIQUE,
  password TEXT
);

CREATE TABLE IF NOT EXISTS appointments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  doctor_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'WAITING',
  note TEXT,
  appt_date TEXT,
  appt_time TEXT,
  created_at INTEGER DEFAULT (strftime('%s','now')),
  responded_at INTEGER,
  completed_at INTEGER,
  FOREIGN KEY(patient_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);
