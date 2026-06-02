import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.db import query_db

class SimilarityEngine:
    """
    Computes semantic similarity between user input and FAQ questions.
    Uses TF-IDF Vectorization and Cosine Similarity.
    Isolated exclusively for student_query intent handling.
    """
    def __init__(self, threshold=0.3):
        self.threshold = threshold

    def find_best_match(self, user_message: str):
        """
        Compares the user query against all stored FAQs using TF-IDF.
        
        :param user_message: The text submitted by the student.
        :return: A tuple of (faq_dict, similarity_score) or (None, score)
        """
        # Fetch FAQs from database
        faqs = query_db("SELECT id, question, answer, intent_category FROM faq")
        if not faqs or len(faqs) == 0:
            return None, 0.0

        # Prepare corpus
        faq_list = [dict(row) for row in faqs]
        questions = [faq['question'] for faq in faq_list]
        
        # Fit vectorizer on current FAQ questions
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform(questions)
            query_vector = vectorizer.transform([user_message])
            
            # Compute cosine similarity between the query and all FAQs
            similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()
            best_idx = int(np.argmax(similarities))
            best_score = float(similarities[best_idx])
            
            if best_score >= self.threshold:
                match = faq_list[best_idx]
                # Normalize categories to conform to the 4-class system
                if match['intent_category'] not in ['admission', 'exam', 'timetable', 'student_query']:
                    match['intent_category'] = 'student_query'
                return match, best_score
            return None, best_score
        except Exception as e:
            # Handle potential vectorizer errors (e.g. empty vocab if questions are too short/stop words)
            print(f"Error during TF-IDF similarity calculation: {e}")
            return None, 0.0
