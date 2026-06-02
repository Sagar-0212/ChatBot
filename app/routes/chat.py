from flask import Blueprint, request, jsonify, render_template
from app.nlp.nlp_engine import NLPEngine
from app.models.db import query_db

chat_bp = Blueprint('chat', __name__)

# Initialize the NLP Processing Engine
nlp = NLPEngine()

@chat_bp.route('/')
def home():
    """
    Renders the public student facing Chatbot Interface.
    """
    # Fetch most viewed FAQs to display as quick links
    popular_faqs = query_db(
        "SELECT id, question, answer, intent_category FROM faq ORDER BY view_count DESC LIMIT 4"
    )
    return render_template('index.html', popular_faqs=popular_faqs)

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles user chat messages.
    Receives JSON body: { "message": "...", "session_id": "..." }
    Queries Admissions, Exams, and Timetable tables dynamically on demand.
    """
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    session_id = data.get('session_id', 'anonymous_session')

    if not message:
        return jsonify({
            "error": "Message is required"
        }), 400

    try:
        # Process message using NLP Router
        result = nlp.process_message(message, session_id=session_id)
        return jsonify(result), 200
    except Exception as e:
        print(f"Chat route error: {e}")
        return jsonify({
            "response": "I encountered an internal error. Please try again shortly.",
            "intent": "error",
            "confidence": 0.0
        }), 500

@chat_bp.route('/api/faqs', methods=['GET'])
def get_faqs():
    """
    Returns list of all FAQs for search or listing in JSON format.
    """
    try:
        faqs = query_db("SELECT id, question, answer, intent_category, view_count FROM faq ORDER BY question ASC")
        return jsonify([dict(faq) for faq in faqs]), 200
    except Exception as e:
        print(f"Failed to fetch FAQs: {e}")
        return jsonify({"error": "Unable to retrieve FAQs"}), 500

@chat_bp.route('/schedules')
def schedules():
    """
    Renders the public Schedules page containing the Timetable grid and Exam schedule.
    """
    return render_template('schedules.html')

@chat_bp.route('/api/schedules/exams', methods=['GET'])
def get_exams_api():
    """Returns all exams for JSON/AJAX scheduling and filtering."""
    try:
        exams = query_db("SELECT * FROM exams ORDER BY exam_date ASC, exam_time ASC")
        return jsonify([dict(ex) for ex in exams]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@chat_bp.route('/api/schedules/timetable', methods=['GET'])
def get_timetable_api():
    """Returns all timetable slots for JSON/AJAX scheduling and filtering."""
    try:
        timetable = query_db("SELECT * FROM timetable ORDER BY day_of_week, start_time ASC")
        return jsonify([dict(slot) for slot in timetable]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
