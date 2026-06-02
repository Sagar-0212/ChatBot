from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash
from app.models.db import query_db, insert_db
from werkzeug.security import check_password_hash
from app.nlp.train_model import train_intent_classifier
from app.routes.chat import nlp

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def is_admin_logged_in():
    """Checks if the admin is logged in via session."""
    return session.get('admin_logged_in') is True

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Renders login screen and authenticates administrator.
    """
    if is_admin_logged_in():
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('admin/login.html')
            
        user = query_db("SELECT * FROM admin_users WHERE username = ?", (username,), one=True)
        if user and check_password_hash(user['password_hash'], password):
            session['admin_logged_in'] = True
            session['admin_username'] = user['username']
            session['admin_role'] = user['role']
            flash(f"Welcome back, {user['username']}!", 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """
    Logs out the admin and clears session data.
    """
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
def dashboard():
    """
    Renders the Administrator Command Center.
    Loads recent chat transcripts, FAQ management lists, student databases,
    admissions, exams schedules, and class timetables.
    """
    if not is_admin_logged_in():
        return redirect(url_for('admin.login'))
        
    # Fetch counts for key statistics cards
    stats = {
        'total_queries': query_db("SELECT COUNT(*) FROM student_queries", one=True)[0],
        'total_faqs': query_db("SELECT COUNT(*) FROM faq", one=True)[0],
        'total_students': query_db("SELECT COUNT(*) FROM students", one=True)[0],
        'total_admissions': query_db("SELECT COUNT(*) FROM admissions", one=True)[0]
    }
    
    # Fetch lists for data tables
    recent_queries = query_db("SELECT * FROM student_queries ORDER BY timestamp DESC LIMIT 20")
    faqs = query_db("SELECT * FROM faq ORDER BY created_at DESC")
    students = query_db("SELECT * FROM students LIMIT 100")
    admissions = query_db("SELECT * FROM admissions")
    timetable = [dict(slot) for slot in query_db("SELECT * FROM timetable ORDER BY day_of_week, start_time")]
    exams = [dict(ex) for ex in query_db("SELECT * FROM exams ORDER BY exam_date, exam_time")]
    
    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_queries=recent_queries,
        faqs=faqs,
        students=students,
        admissions=admissions,
        timetable=timetable,
        exams=exams
    )

# ==========================================
# FAQ CRUD OPERATIONS
# ==========================================

@admin_bp.route('/api/faq', methods=['POST'])
def add_faq():
    """Adds a new FAQ into the database."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    intent_category = request.form.get('intent_category', '').strip()
    keyword_tags = request.form.get('keyword_tags', '').strip()
    
    if not question or not answer or not intent_category:
        return jsonify({"error": "Question, Answer, and Intent Category are required fields."}), 400
        
    try:
        insert_db(
            "INSERT INTO faq (question, answer, intent_category, keyword_tags) VALUES (?, ?, ?, ?)",
            (question, answer, intent_category, keyword_tags)
        )
        return jsonify({"message": "FAQ added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add FAQ: {str(e)}"}), 500

@admin_bp.route('/api/faq/<int:faq_id>/update', methods=['POST'])
def update_faq(faq_id):
    """Updates an existing FAQ by ID."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    question = request.form.get('question', '').strip()
    answer = request.form.get('answer', '').strip()
    intent_category = request.form.get('intent_category', '').strip()
    keyword_tags = request.form.get('keyword_tags', '').strip()
    
    if not question or not answer or not intent_category:
        return jsonify({"error": "Question, Answer, and Intent Category are required fields."}), 400
        
    try:
        insert_db(
            "UPDATE faq SET question = ?, answer = ?, intent_category = ?, keyword_tags = ? WHERE id = ?",
            (question, answer, intent_category, keyword_tags, faq_id)
        )
        return jsonify({"message": "FAQ updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update FAQ: {str(e)}"}), 500

@admin_bp.route('/api/faq/<int:faq_id>/delete', methods=['POST'])
def delete_faq(faq_id):
    """Deletes an FAQ by ID."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        insert_db("DELETE FROM faq WHERE id = ?", (faq_id,))
        return jsonify({"message": "FAQ deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete FAQ: {str(e)}"}), 500

# ==========================================
# ADMISSIONS CRUD OPERATIONS
# ==========================================

@admin_bp.route('/api/admission', methods=['POST'])
def add_admission():
    """Adds a new admission program to the database."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    program = request.form.get('program', '').strip()
    eligibility = request.form.get('eligibility', '').strip()
    total_fees = request.form.get('total_fees', '0')
    intake_seats = request.form.get('intake_seats', '0')
    last_date = request.form.get('last_date', '').strip()
    documents_required = request.form.get('documents_required', '').strip()
    
    if not program or not eligibility or not total_fees or not last_date:
        return jsonify({"error": "Program, Eligibility, Fees, and Deadline are required fields."}), 400
        
    try:
        insert_db(
            "INSERT INTO admissions (program, eligibility, total_fees, intake_seats, last_date, documents_required) VALUES (?, ?, ?, ?, ?, ?)",
            (program, eligibility, float(total_fees), int(intake_seats), last_date, documents_required)
        )
        return jsonify({"message": "Program added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add program: {str(e)}"}), 500

@admin_bp.route('/api/admission/<int:prog_id>/update', methods=['POST'])
def update_admission(prog_id):
    """Updates an existing admission program by ID."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    program = request.form.get('program', '').strip()
    eligibility = request.form.get('eligibility', '').strip()
    total_fees = request.form.get('total_fees', '0')
    intake_seats = request.form.get('intake_seats', '0')
    last_date = request.form.get('last_date', '').strip()
    documents_required = request.form.get('documents_required', '').strip()
    
    if not program or not eligibility or not total_fees or not last_date:
        return jsonify({"error": "Program, Eligibility, Fees, and Deadline are required fields."}), 400
        
    try:
        insert_db(
            "UPDATE admissions SET program = ?, eligibility = ?, total_fees = ?, intake_seats = ?, last_date = ?, documents_required = ? WHERE id = ?",
            (program, eligibility, float(total_fees), int(intake_seats), last_date, documents_required, prog_id)
        )
        return jsonify({"message": "Program updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update program: {str(e)}"}), 500

@admin_bp.route('/api/admission/<int:prog_id>/delete', methods=['POST'])
def delete_admission(prog_id):
    """Deletes an admission program by ID."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        insert_db("DELETE FROM admissions WHERE id = ?", (prog_id,))
        return jsonify({"message": "Program deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete program: {str(e)}"}), 500

# ==========================================
# EXAMS CRUD OPERATIONS
# ==========================================

@admin_bp.route('/api/exam', methods=['POST'])
def add_exam():
    """Adds a new exam schedule to the database."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    subject_code = request.form.get('subject_code', '').strip()
    subject = request.form.get('subject', '').strip()
    department = request.form.get('department', '').strip()
    year_of_study = request.form.get('year_of_study', '1')
    semester = request.form.get('semester', '1')
    exam_date = request.form.get('exam_date', '').strip()
    exam_time = request.form.get('exam_time', '').strip()
    venue = request.form.get('venue', '').strip()
    duration_minutes = request.form.get('duration_minutes', '180')
    exam_type = request.form.get('exam_type', '').strip()
    
    if not subject_code or not subject or not department or not exam_date or not exam_time or not venue:
        return jsonify({"error": "Subject Code, Subject Name, Department, Date, Time, and Venue are required."}), 400
        
    try:
        insert_db(
            "INSERT INTO exams (subject_code, subject, department, year_of_study, semester, exam_date, exam_time, venue, duration_minutes, exam_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (subject_code, subject, department, int(year_of_study), int(semester), exam_date, exam_time, venue, int(duration_minutes), exam_type)
        )
        return jsonify({"message": "Exam scheduled successfully!"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to schedule exam: {str(e)}"}), 500

@admin_bp.route('/api/exam/<int:exam_id>/update', methods=['POST'])
def update_exam(exam_id):
    """Updates an existing exam schedule by ID."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    subject_code = request.form.get('subject_code', '').strip()
    subject = request.form.get('subject', '').strip()
    department = request.form.get('department', '').strip()
    year_of_study = request.form.get('year_of_study', '1')
    semester = request.form.get('semester', '1')
    exam_date = request.form.get('exam_date', '').strip()
    exam_time = request.form.get('exam_time', '').strip()
    venue = request.form.get('venue', '').strip()
    duration_minutes = request.form.get('duration_minutes', '180')
    exam_type = request.form.get('exam_type', '').strip()
    
    if not subject_code or not subject or not department or not exam_date or not exam_time or not venue:
        return jsonify({"error": "Subject Code, Subject Name, Department, Date, Time, and Venue are required."}), 400
        
    try:
        insert_db(
            "UPDATE exams SET subject_code = ?, subject = ?, department = ?, year_of_study = ?, semester = ?, exam_date = ?, exam_time = ?, venue = ?, duration_minutes = ?, exam_type = ? WHERE id = ?",
            (subject_code, subject, department, int(year_of_study), int(semester), exam_date, exam_time, venue, int(duration_minutes), exam_type, exam_id)
        )
        return jsonify({"message": "Exam schedule updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update exam: {str(e)}"}), 500

@admin_bp.route('/api/exam/<int:exam_id>/delete', methods=['POST'])
def delete_exam(exam_id):
    """Deletes an exam schedule by ID."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        insert_db("DELETE FROM exams WHERE id = ?", (exam_id,))
        return jsonify({"message": "Exam schedule deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete exam schedule: {str(e)}"}), 500

# ==========================================
# TIMETABLE CRUD OPERATIONS
# ==========================================

@admin_bp.route('/api/timetable', methods=['POST'])
def add_timetable():
    """Adds a new class timetable entry to the database."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    department = request.form.get('department', '').strip()
    year_of_study = request.form.get('year_of_study', '1')
    semester = request.form.get('semester', '1')
    day_of_week = request.form.get('day_of_week', '').strip()
    subject = request.form.get('subject', '').strip()
    start_time = request.form.get('start_time', '').strip()
    end_time = request.form.get('end_time', '').strip()
    room_no = request.form.get('room_no', '').strip()
    faculty_name = request.form.get('faculty_name', '').strip()
    
    if not department or not day_of_week or not subject or not start_time or not end_time or not room_no or not faculty_name:
        return jsonify({"error": "All timetable entry fields are required."}), 400
        
    try:
        insert_db(
            "INSERT INTO timetable (department, year_of_study, semester, day_of_week, subject, start_time, end_time, room_no, faculty_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (department, int(year_of_study), int(semester), day_of_week, subject, start_time, end_time, room_no, faculty_name)
        )
        return jsonify({"message": "Timetable slot added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to add class schedule: {str(e)}"}), 500

@admin_bp.route('/api/timetable/<int:slot_id>/update', methods=['POST'])
def update_timetable(slot_id):
    """Updates an existing class timetable entry by ID."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    department = request.form.get('department', '').strip()
    year_of_study = request.form.get('year_of_study', '1')
    semester = request.form.get('semester', '1')
    day_of_week = request.form.get('day_of_week', '').strip()
    subject = request.form.get('subject', '').strip()
    start_time = request.form.get('start_time', '').strip()
    end_time = request.form.get('end_time', '').strip()
    room_no = request.form.get('room_no', '').strip()
    faculty_name = request.form.get('faculty_name', '').strip()
    
    if not department or not day_of_week or not subject or not start_time or not end_time or not room_no or not faculty_name:
        return jsonify({"error": "All timetable entry fields are required."}), 400
        
    try:
        insert_db(
            "UPDATE timetable SET department = ?, year_of_study = ?, semester = ?, day_of_week = ?, subject = ?, start_time = ?, end_time = ?, room_no = ?, faculty_name = ? WHERE id = ?",
            (department, int(year_of_study), int(semester), day_of_week, subject, start_time, end_time, room_no, faculty_name, slot_id)
        )
        return jsonify({"message": "Timetable slot updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update class schedule: {str(e)}"}), 500

@admin_bp.route('/api/timetable/<int:slot_id>/delete', methods=['POST'])
def delete_timetable(slot_id):
    """Deletes a class timetable entry by ID."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        insert_db("DELETE FROM timetable WHERE id = ?", (slot_id,))
        return jsonify({"message": "Timetable slot deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete class schedule: {str(e)}"}), 500

# ==========================================
# NLP RETRAINING HANDLER
# ==========================================

@admin_bp.route('/api/train', methods=['POST'])
def retrain_model():
    """Triggers retraining and hot-reloads the scikit-learn model."""
    if not is_admin_logged_in():
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        # Re-run training scripts
        train_intent_classifier()
        # Force re-load on the active NLP model
        nlp.load_model()
        return jsonify({"message": "NLP Engine retrained and hot-reloaded successfully!"}), 200
    except Exception as e:
        return jsonify({"error": f"Retraining failed: {str(e)}"}), 500
