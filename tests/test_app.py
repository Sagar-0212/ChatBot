import os
import sys
import pytest

# Ensure project root is in sys.path (two directories up from tests/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.db import query_db
from app.nlp.nlp_engine import NLPEngine

def test_database_connection():
    """
    Verifies that the SQLite database is populated with realistic seeded data.
    """
    student_count = query_db("SELECT COUNT(*) FROM students", one=True)[0]
    faq_count = query_db("SELECT COUNT(*) FROM faq", one=True)[0]
    assert student_count >= 5
    assert faq_count >= 5

def test_nlp_engine_classification():
    """
    Verifies that the NLP engine successfully loads models and routes queries to correct intents.
    """
    engine = NLPEngine()
    
    # Check admissions intent classification and dynamic DB lookup
    admission_res = engine.process_message("What are the admission requirements for computer science?")
    assert admission_res['intent'] == 'admission'
    assert 'Eligibility' in admission_res['response']
    
    # Check that semantically similar admissions queries also route to admission intent and return dynamic admissions details
    queries = [
        "Tell me about admissions",
        "Admission information",
        "What courses are offered?",
        "What is the fee structure?"
    ]
    for q in queries:
        res = engine.process_message(q)
        assert res['intent'] == 'admission', f"Query '{q}' failed to route to admission intent"
        assert 'B.Tech' in res['response'] or 'MBA' in res['response'] or 'MCA' in res['response']
        
    # Check exams intent classification
    exams_res = engine.process_message("when is my exam?")
    assert exams_res['intent'] == 'exam'
    assert 'examination schedule' in exams_res['response']

def test_flask_endpoints():
    """
    Verifies that HTTP routes respond with appropriate status codes and payloads.
    """
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        # Test public homepage
        home_res = client.get('/')
        assert home_res.status_code == 200
        assert b"Rajarambapu Institute of Technology" in home_res.data
        
        # Test Chat API
        chat_res = client.post('/api/chat', json={
            "message": "tell me about library timings",
            "session_id": "test_session_id"
        })
        assert chat_res.status_code == 200
        chat_data = chat_res.get_json()
        assert "response" in chat_data
        assert "library" in chat_data["response"].lower()
        
        # Test Admin Login GET
        login_res = client.get('/admin/login')
        assert login_res.status_code == 200
        assert b"Staff Portal" in login_res.data
