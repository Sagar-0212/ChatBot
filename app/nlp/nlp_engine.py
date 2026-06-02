import os
import sys
import pickle
import re
from app.nlp.similarity_engine import SimilarityEngine
from app.models.db import query_db, insert_db

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

class NLPEngine:
    """
    Main NLP routing and processing system.
    Determines user intent via a trained classifier or falls back to FAQ similarity matches,
    then fetches dynamic content from the database.
    """
    def __init__(self):
        self.similarity_engine = SimilarityEngine(threshold=0.3)
        self.model = None
        self.vectorizer = None
        self.load_model()

    def load_model(self):
        """Loads the trained ML intent model if it exists."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        model_path = Config.MODEL_PATH
        vectorizer_path = Config.VECTORIZER_PATH
        
        if not os.path.isabs(model_path):
            model_path = os.path.join(project_root, model_path)
        if not os.path.isabs(vectorizer_path):
            vectorizer_path = os.path.join(project_root, vectorizer_path)

        if os.path.exists(model_path) and os.path.exists(vectorizer_path):
            try:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                print("NLP Engine: Model and Vectorizer loaded successfully.")
            except Exception as e:
                print(f"NLP Engine: Error loading model files: {e}")
        else:
            print("NLP Engine: Model files not found. Relying on similarity matching fallback.")

    def has_word_match(self, text: str, keywords: list) -> bool:
        """
        Checks if any of the keywords exists in the text as a full word using regex boundaries.
        This prevents false substring matches (e.g. 'timing' matching 'timings').
        """
        if not keywords:
            return False
        pattern = r'\b(' + '|'.join(re.escape(kw) for kw in keywords) + r')\b'
        return bool(re.search(pattern, text.lower()))

    def process_message(self, user_message: str, session_id: str = "default") -> dict:
        """
        Processes a student query, detects the intent, queries relevant tables,
        and logs the transaction in student_queries.
        
        :param user_message: String message sent by user.
        :param session_id: Unique session identifier for chat history tracking.
        :return: Dict containing bot response, intent, and confidence score.
        """
        user_message_clean = user_message.strip()
        user_message_lower = user_message_clean.lower()
        
        if not user_message_clean:
            return {
                "response": "Please type a valid question.",
                "intent": "empty",
                "confidence": 1.0
            }

        # 1. Default intent classifier prediction
        intent = "student_query"
        confidence = 0.5
        response = None

        # Predict intent using scikit-learn Naive Bayes model
        if self.model and self.vectorizer:
            try:
                vec = self.vectorizer.transform([user_message_lower])
                probs = self.model.predict_proba(vec)[0]
                best_class_idx = probs.argmax()
                intent = self.model.classes_[best_class_idx]
                confidence = float(probs[best_class_idx])
                print(f"[Intent Classification] Query: '{user_message_clean}' -> Predicted Intent: '{intent}' (Confidence: {confidence:.4f})")
            except Exception as e:
                print(f"NLP Engine: Prediction error: {e}")
                intent = "student_query"
                confidence = 0.5

        # 2. Check for Low Confidence Fallbacks
        CONFIDENCE_THRESHOLD = 0.65
        if confidence < CONFIDENCE_THRESHOLD:
            # Check for admission keyword indicators (word boundaries)
            admission_keywords = ['admission', 'admissions', 'fee', 'fees', 'eligibility', 'course', 'courses', 'program', 'programs', 'intake', 'documents', 'criteria']
            if self.has_word_match(user_message_lower, admission_keywords):
                intent = "admission"
                confidence = 0.85
                print(f"[Fallback Override] Query: '{user_message_clean}' -> Overridden to 'admission' due to keywords.")
            
            # Check for exam keyword indicators (word boundaries)
            elif self.has_word_match(user_message_lower, ['exam', 'exams', 'examination', 'examinations', 'venue', 'venues', 'test', 'tests']):
                intent = "exam"
                confidence = 0.85
                print(f"[Fallback Override] Query: '{user_message_clean}' -> Overridden to 'exam' due to keywords.")
            
            # Check for timetable keyword indicators (word boundaries; omitting 'timing' to avoid conflict with 'library timings')
            elif self.has_word_match(user_message_lower, ['timetable', 'timetables', 'schedule', 'schedules', 'class', 'classes', 'lecture', 'lectures']):
                intent = "timetable"
                confidence = 0.85
                print(f"[Fallback Override] Query: '{user_message_clean}' -> Overridden to 'timetable' due to keywords.")

        # Fetch FAQ similarity beforehand in case it is student_query
        faq_match, sim_score = self.similarity_engine.find_best_match(user_message_lower)

        # 3. Dynamic content routing based on predicted intent (No hardcoding)
        if intent == "admission":
            # Query admissions table dynamically on-demand
            programs = query_db("SELECT * FROM admissions")
            if programs:
                matched_prog = None
                for prog in programs:
                    prog_name_lower = prog['program'].lower()
                    # Fuzzy match program names or standard shorthand tags
                    if prog_name_lower in user_message_lower or (
                        ("cse" in user_message_lower or "computer science" in user_message_lower) and "computer science" in prog_name_lower
                    ) or (
                        ("mechanical" in user_message_lower or "mech" in user_message_lower) and "mechanical" in prog_name_lower
                    ) or (
                        ("civil" in user_message_lower) and "civil" in prog_name_lower
                    ) or (
                        ("mba" in user_message_lower) and "mba" in prog_name_lower
                    ) or (
                        ("mca" in user_message_lower) and "mca" in prog_name_lower
                    ):
                        matched_prog = prog
                        break
                
                if matched_prog:
                    response = (
                        f"Details for the {matched_prog['program']} program at RIT:\n"
                        f"• Eligibility Criteria: {matched_prog['eligibility']}\n"
                        f"• Annual Tuition Fee: INR {matched_prog['total_fees']:,.2f}\n"
                        f"• Intake Capacity: {matched_prog['intake_seats']} seats\n"
                        f"• Admission Deadline: {matched_prog['last_date']}\n"
                        f"• Documents Required: {matched_prog['documents_required']}"
                    )
                else:
                    # Output list of all programs dynamically
                    prog_list = "\n".join([f"• {p['program']} (Fee: INR {p['total_fees']:,.2f})" for p in programs])
                    response = (
                        f"At Rajarambapu Institute of Technology (RIT), we offer the following programs:\n{prog_list}\n\n"
                        f"Please ask about eligibility, fees, or deadlines for a specific program (e.g. B.Tech, MBA, MCA)."
                    )
            else:
                response = "Currently, no academic admission programs are listed in our database."

        elif intent == "exam":
            # Query exams table dynamically on-demand
            exams = query_db("SELECT * FROM exams ORDER BY exam_date ASC")
            if exams:
                # Filter by department if mentioned
                filtered_exams = []
                for ex in exams:
                    dept = ex['department'].lower()
                    if dept in user_message_lower or (
                        ("cs" in user_message_lower or "cse" in user_message_lower) and dept == "cse"
                    ):
                        filtered_exams.append(ex)
                
                # If no specific department matched, show all upcoming exams
                display_list = filtered_exams if filtered_exams else exams
                exam_details = [
                    f"• {ex['subject']} ({ex['exam_type']}) - Date: {ex['exam_date']} at {ex['exam_time']} | Venue: {ex['venue']} | Duration: {ex['duration_minutes']} mins"
                    for ex in display_list
                ]
                response = "Here is the upcoming examination schedule at RIT:\n" + "\n".join(exam_details)
            else:
                response = "No upcoming examinations are listed in our database."

        elif intent == "timetable":
            # Query timetable table dynamically on-demand
            timetable = query_db("SELECT * FROM timetable")
            if timetable:
                # Filter by department if mentioned
                filtered_slots = []
                for slot in timetable:
                    dept = slot['department'].lower()
                    if dept in user_message_lower or (
                        ("cs" in user_message_lower or "cse" in user_message_lower) and dept == "cse"
                    ):
                        filtered_slots.append(slot)
                
                # If no specific department matched, show all class slots
                display_slots = filtered_slots if filtered_slots else timetable
                slots_text = [
                    f"• {slot['subject']} ({slot['day_of_week']}): {slot['start_time']} - {slot['end_time']} | Room: {slot['room_no']} | Faculty: {slot['faculty_name']}"
                    for slot in display_slots
                ]
                response = "Here is the class timetable at RIT:\n" + "\n".join(slots_text)
            else:
                response = "No class timetable schedules are listed in our database."

        else: # student_query intent (FAQ similarity is STRICTLY isolated here)
            if faq_match:
                insert_db("UPDATE faq SET view_count = view_count + 1 WHERE id = ?", (faq_match['id'],))
                response = faq_match['answer']
                confidence = max(confidence, sim_score)
            else:
                response = (
                    "I apologize, but I couldn't find a direct answer to your question in our FAQs. "
                    "You can ask about RIT admissions, examinations, class timetables, or contact administrative services."
                )

        # Log query to student_queries table
        insert_db(
            "INSERT INTO student_queries (user_message, bot_response, intent_detected, confidence_score, session_id) VALUES (?, ?, ?, ?, ?)",
            (user_message_clean, response, intent, confidence, session_id)
        )

        return {
            "response": response,
            "intent": intent,
            "confidence": confidence
        }
