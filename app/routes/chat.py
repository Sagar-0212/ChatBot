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
