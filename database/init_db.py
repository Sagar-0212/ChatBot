import os
import sys
import sqlite3
from werkzeug.security import generate_password_hash

# Add parent directory to sys.path to load Config correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def init_database():
    """
    Initializes the SQLite database tables and seeds them with RIT (Rajarambapu Institute of Technology) realistic data.
    Ensures tables are created safely and no duplicate rows are inserted on consecutive runs.
    """
    # Get database path from configuration
    db_path = Config.get_sqlite_db_path()
    
    # Resolve relative path if it's running from different directories
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)
        
    print(f"Connecting to database at: {db_path}")
    
    # Ensure database parent directory exists
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        print(f"Created database directory: {db_dir}")

    # Establish connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ==========================================
    # 1. CREATE TABLES
    # ==========================================
    
    # admin_users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'superadmin')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("[Success] Table 'admin_users' created or verified.")

    # students
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL CHECK(year BETWEEN 1 AND 4),
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL
    );
    """)
    print("[Success] Table 'students' created or verified.")

    # admissions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        program TEXT UNIQUE NOT NULL,
        eligibility TEXT NOT NULL,
        total_fees REAL NOT NULL,
        intake_seats INTEGER NOT NULL,
        last_date TEXT NOT NULL,
        documents_required TEXT NOT NULL
    );
    """)
    print("[Success] Table 'admissions' created or verified.")

    # exams
    # Drops table if schema is old to ensure clean rebuild during bootstrapping/development
    cursor.execute("DROP TABLE IF EXISTS exams;")
    cursor.execute("""
    CREATE TABLE exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        subject TEXT NOT NULL,
        department TEXT NOT NULL,
        year_of_study INTEGER NOT NULL CHECK(year_of_study BETWEEN 1 AND 4),
        semester INTEGER NOT NULL CHECK(semester BETWEEN 1 AND 8),
        exam_date TEXT NOT NULL,
        exam_time TEXT NOT NULL,
        venue TEXT NOT NULL,
        duration_minutes INTEGER NOT NULL,
        exam_type TEXT NOT NULL
    );
    """)
    print("[Success] Table 'exams' created and verified.")

    # timetable
    # Drops table if schema is old to ensure clean rebuild during bootstrapping/development
    cursor.execute("DROP TABLE IF EXISTS timetable;")
    cursor.execute("""
    CREATE TABLE timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT NOT NULL,
        year_of_study INTEGER NOT NULL CHECK(year_of_study BETWEEN 1 AND 4),
        semester INTEGER NOT NULL CHECK(semester BETWEEN 1 AND 8),
        day_of_week TEXT NOT NULL,
        subject TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        room_no TEXT NOT NULL,
        faculty_name TEXT NOT NULL
    );
    """)
    print("[Success] Table 'timetable' created and verified.")

    # faq
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faq (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL UNIQUE,
        answer TEXT NOT NULL,
        intent_category TEXT NOT NULL,
        keyword_tags TEXT NOT NULL,
        view_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    print("[Success] Table 'faq' created or verified.")

    # student_queries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student_queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_message TEXT NOT NULL,
        bot_response TEXT NOT NULL,
        intent_detected TEXT,
        confidence_score REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        session_id TEXT NOT NULL
    );
    """)
    print("[Success] Table 'student_queries' created or verified.")

    # ==========================================
    # 2. SEED REALISTIC DATA FOR RIT
    # ==========================================
    
    def is_empty(table_name):
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0] == 0

    # Seeding admin_users
    if is_empty("admin_users"):
        admins = [
            ("admin", generate_password_hash("admin123"), "superadmin"),
            ("registrar", generate_password_hash("reg456"), "admin"),
            ("academic_dean", generate_password_hash("dean789"), "admin"),
            ("admissions_officer", generate_password_hash("adm101"), "admin"),
            ("exam_coordinator", generate_password_hash("exam202"), "admin")
        ]
        cursor.executemany(
            "INSERT INTO admin_users (username, password_hash, role) VALUES (?, ?, ?)",
            admins
        )
        print("[Seeded] Seeded 5 administrative users into 'admin_users'.")

    # Seeding students
    if is_empty("students"):
        students = [
            ("Rajesh Kumar", "RIT-2023-CSE-045", "CSE", 3, "rajesh.kumar@ritindia.edu", "9876543210"),
            ("Priya Sharma", "RIT-2024-EL-012", "Electronics", 2, "priya.sharma@ritindia.edu", "8765432109"),
            ("Amit Patel", "RIT-2022-ME-102", "Mechanical", 4, "amit.patel@ritindia.edu", "7654321098"),
            ("Sneha Reddy", "RIT-2025-IT-088", "IT", 1, "sneha.reddy@ritindia.edu", "6543210987"),
            ("Vikram Singh", "RIT-2023-EE-031", "Electrical", 3, "vikram.singh@ritindia.edu", "9988776655")
        ]
        cursor.executemany(
            "INSERT INTO students (name, roll_no, department, year, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
            students
        )
        print("[Seeded] Seeded 5 students into 'students'.")

    # Seeding admissions
    if is_empty("admissions"):
        admissions = [
            ("B.Tech Computer Science and Engineering", "10+2 with Physics, Chemistry, Mathematics (min 60%), JEE Main / MHT-CET / RIT Entrance score", 185000.0, 120, "2026-07-31", "10th & 12th Marksheet, Entrance Score Card, Transfer Certificate, Passport Photos"),
            ("B.Tech Mechanical Engineering", "10+2 with Physics, Chemistry, Mathematics (min 55%), RIT Entrance score", 155000.0, 90, "2026-07-31", "10th & 12th Marksheet, Transfer Certificate, Migration Certificate, Aadhar Card"),
            ("MCA (Master of Computer Applications)", "Graduation in BCA/B.Sc/B.Com with Mathematics at 10+2 level or Graduation level (min 50%), MAH-MCA-CET score", 110000.0, 60, "2026-08-15", "Graduation Degree, Class 10/12 Marksheets, MAH-MCA-CET Score Card, Identity Proof"),
            ("MBA (Master of Business Administration)", "Any Graduate Degree from a recognized University (min 50%), MAH-MBA-CET / CAT / CMAT score", 125000.0, 60, "2026-08-15", "Graduation Degree, Entrance Admit Card/Score Card, Character Certificate, Passport Photos"),
            ("B.Tech Civil Engineering", "10+2 with Physics, Chemistry, Mathematics (min 50%)", 135000.0, 60, "2026-07-31", "10th & 12th Marksheet, Transfer Certificate, Passport Photos")
        ]
        cursor.executemany(
            "INSERT INTO admissions (program, eligibility, total_fees, intake_seats, last_date, documents_required) VALUES (?, ?, ?, ?, ?, ?)",
            admissions
        )
        print("[Seeded] Seeded 5 academic programs into 'admissions'.")

    # Seeding exams (including subject_code and semester)
    # Target dataset for CSE, Year 2, Semester 4
    exams = [
        ("CS-204", "Computer Networks", "CSE", 2, 4, "2026-06-15", "10:00", "Block A - Hall 202", 180, "End-Semester"),
        ("CS-205", "Operating Systems", "CSE", 2, 4, "2026-06-16", "14:00", "Block A - Hall 101", 180, "End-Semester"),
        ("CS-206", "Database Management Systems", "CSE", 2, 4, "2026-06-17", "10:00", "Block A - Hall 202", 180, "End-Semester"),
        ("CS-207", "Software Engineering", "CSE", 2, 4, "2026-06-18", "14:00", "Block A - Hall 102", 180, "End-Semester"),
        ("EC-301", "Microprocessors & Microcontrollers", "Electronics", 3, 6, "2026-06-19", "10:00", "Block B - Lab 3", 120, "Mid-Term"),
        ("ME-203", "Fluid Mechanics", "Mechanical", 2, 4, "2026-06-20", "10:00", "Block C - Room 301", 180, "End-Semester"),
        ("EE-305", "Electrical Machines", "Electrical", 3, 6, "2026-06-19", "14:00", "Block B - Hall 104", 180, "End-Semester")
    ]
    cursor.executemany(
        "INSERT INTO exams (subject_code, subject, department, year_of_study, semester, exam_date, exam_time, venue, duration_minutes, exam_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        exams
    )
    print("[Seeded] Seeded examination schedules into 'exams'.")

    # Seeding timetable (including semester)
    # Target dataset for CSE, Year 2, Semester 4
    timetable = [
        ("CSE", 2, 4, "Monday", "Computer Networks", "09:00", "10:30", "Block A - 301", "Dr. S. R. Patil"),
        ("CSE", 2, 4, "Monday", "Operating Systems", "10:45", "12:15", "Block A - 301", "Prof. M. A. Deshmukh"),
        ("CSE", 2, 4, "Tuesday", "Database Management Systems", "09:00", "10:30", "Block A - 301", "Dr. Anand Rao"),
        ("CSE", 2, 4, "Tuesday", "Software Engineering", "10:45", "12:15", "Block A - 301", "Prof. Shalini Sen"),
        ("CSE", 2, 4, "Wednesday", "Computer Networks Lab", "14:00", "17:00", "CSE Lab 2", "Dr. S. R. Patil"),
        ("CSE", 2, 4, "Thursday", "Operating Systems Lab", "09:00", "12:00", "CSE Lab 3", "Prof. M. A. Deshmukh"),
        ("CSE", 2, 4, "Friday", "Database Management Systems Lab", "10:45", "13:45", "CSE Lab 1", "Dr. Anand Rao"),
        # Other semesters / departments
        ("Electronics", 2, 4, "Tuesday", "Analog Circuits", "11:00", "12:30", "Block B - 102", "Dr. S. K. Verma"),
        ("Mechanical", 4, 8, "Wednesday", "CAD/CAM Lab", "14:00", "17:00", "Mechanical Lab Floor 1", "Prof. Rajesh Nair"),
        ("CSE", 1, 2, "Thursday", "Mathematics-II", "09:00", "10:30", "Block A - Auditorium 1", "Dr. H. S. Murthy")
    ]
    cursor.executemany(
        "INSERT INTO timetable (department, year_of_study, semester, day_of_week, subject, start_time, end_time, room_no, faculty_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        timetable
    )
    print("[Seeded] Seeded class schedules into 'timetable'.")

    # Seeding faq
    if is_empty("faq"):
        faqs = [
            ("What are the college library timings?", "The Central Library of Rajarambapu Institute of Technology (RIT) is open from 8:00 AM to 8:00 PM on weekdays, and 9:00 AM to 4:00 PM on Saturdays. It remains closed on Sundays and official holidays.", "student_query", "library, timings, hours, books", 15),
            ("How can I apply for an hostel room?", "Hostel allotment is done online through the RIT student portal after paying the registration fee. Alternatively, you can contact the Warden's Office in Block E.", "student_query", "hostel, room, accommodation, Warden, registration", 32),
            ("What is the attendance requirement to write examinations?", "Students at Rajarambapu Institute of Technology (RIT) must maintain a minimum of 75% attendance in each registered subject to be eligible to appear for the semester end examinations. Shortfall may result in debarment.", "student_query", "attendance, exam eligibility, debarment, rule", 48),
            ("How do I contact the placement cell?", "The RIT Training & Placement Cell is located on the Ground Floor of the Administrative Block. You can reach them at placement@ritindia.edu or contact Prof. Amit Dwivedi (Placement Officer).", "student_query", "placement, placement cell, jobs, internship, placement officer", 55),
            ("Where can I get my transcript or marksheet verified?", "Official transcripts and marksheet verifications are handled by the Controller of Examinations (CoE) office on the second floor of the RIT Administrative Block. Apply via the online portal and submit copy of certificates.", "student_query", "transcript, marksheet, verification, CoE, registrar", 22)
        ]
        cursor.executemany(
            "INSERT INTO faq (question, answer, intent_category, keyword_tags, view_count) VALUES (?, ?, ?, ?, ?)",
            faqs
        )
        print("[Seeded] Seeded 5 FAQs into 'faq'.")

    # Seeding student_queries
    if is_empty("student_queries"):
        student_queries = [
            ("What are the eligibility criteria for CSE?", "For B.Tech Computer Science and Engineering, the eligibility is 10+2 with Physics, Chemistry, Mathematics (min 60%) and a valid JEE Main or RIT Entrance score.", "admission", 0.95, "sess_abc123"),
            ("When is the DSA exam scheduled?", "The Data Structures & Algorithms exam is scheduled for 2026-06-15 at 10:00 AM at Block A - Hall 202.", "exam", 0.89, "sess_abc123"),
            ("Who teaches Artificial Intelligence?", "The Artificial Intelligence class is taught by Dr. Anand Rao.", "timetable", 0.92, "sess_xyz789"),
            ("How to apply for hostel rooms?", "Hostel allotment is done online through the RIT student portal after paying the registration fee. Alternatively, you can contact the Warden's Office in Block E.", "student_query", 0.97, "sess_uvw456"),
            ("Tell me about library hours", "The Central Library of Rajarambapu Institute of Technology (RIT) is open from 8:00 AM to 8:00 PM on weekdays, and 9:00 AM to 4:00 PM on Saturdays.", "student_query", 0.94, "sess_uvw456")
        ]
        cursor.executemany(
            "INSERT INTO student_queries (user_message, bot_response, intent_detected, confidence_score, session_id) VALUES (?, ?, ?, ?, ?)",
            student_queries
        )
        print("[Seeded] Seeded 5 student query records into 'student_queries'.")

    # Commit changes and close
    conn.commit()
    conn.close()
    print("Database initialization successfully completed.")

if __name__ == "__main__":
    init_database()
