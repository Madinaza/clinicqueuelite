import sqlite3

DB_PATH = "clinicflow.db"

def seed_temp_accounts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ----- ADMIN TEMP ACCOUNT -----
    cur.execute("SELECT 1 FROM users WHERE email=?", ("admin@clinicflow.com",))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO users (email,password,role) VALUES (?,?,?)",
            ("admin@clinicflow.com", "admin123", "ADMIN")
        )

    # ----- DOCTOR TEMP ACCOUNTS -----
    # Ensure doctors exist + give them temp email/password
    doctors = [
        ("Dr. Ahmed Hassan", "Cardiology", 12, "Main Clinic – Floor 2", "AVAILABLE", "ahmed@clinicflow.com", "doc123"),
        ("Dr. Sarah Ali", "Dermatology", 8, "West Wing – Room 14", "AVAILABLE", "sarah@clinicflow.com", "doc123"),
        ("Dr. John Smith", "Neurology", 15, "East Wing – Room 9", "BUSY", "john@clinicflow.com", "doc123"),
    ]

    for d in doctors:
        name, branch, exp, addr, status, email, pwd = d
        cur.execute("SELECT id FROM doctors WHERE email=?", (email,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO doctors (name,branch,experience,address,status,email,password)
                VALUES (?,?,?,?,?,?,?)
            """, (name, branch, exp, addr, status, email, pwd))

    conn.commit()
    conn.close()

seed_temp_accounts()
print("✅ Seeded temporary admin + doctor accounts")
