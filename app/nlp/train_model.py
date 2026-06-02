import os
import sys
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score, confusion_matrix

# Ensure project root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

# Pinned NLP intent classes: student_query, admission, exam, timetable
TRAINING_DATA = [
    # 1. admission (admissions, eligibility, course/program names, fees, deadlines, documents)
    ("how do i get admission?", "admission"),
    ("what is the eligibility for computer science?", "admission"),
    ("what are the admission requirements?", "admission"),
    ("admission procedure and fees structure", "admission"),
    ("documents needed for admission", "admission"),
    ("last date for admission registration", "admission"),
    ("what is the fee for M.Tech Data Science?", "admission"),
    ("tell me about the intake seats for PhD AI", "admission"),
    ("admissions", "admission"),
    ("tell me about admissions", "admission"),
    ("admission details", "admission"),
    ("admission information", "admission"),
    ("course details", "admission"),
    ("course information", "admission"),
    ("available programs", "admission"),
    ("available courses", "admission"),
    ("what courses are offered?", "admission"),
    ("what is the fee structure?", "admission"),
    ("fee structure", "admission"),
    ("fees structure at RIT", "admission"),
    ("eligibility criteria", "admission"),
    ("requirements for admission", "admission"),
    ("what are the courses in RIT?", "admission"),
    ("list of programs offered", "admission"),
    ("how much is the MBA fee?", "admission"),
    ("what are the B.Tech criteria?", "admission"),
    ("eligibility guidelines for admissions", "admission"),
    ("how to apply for B.Tech?", "admission"),
    ("documents required for B.Tech admission", "admission"),
    
    # User-specified admission training examples
    ("What is the B.Tech fee?", "admission"),
    ("B.Tech fees", "admission"),
    ("MBA fees", "admission"),
    ("MCA fees", "admission"),
    ("Fee details", "admission"),
    ("Admission process", "admission"),
    ("How can I take admission?", "admission"),
    ("Eligibility for B.Tech", "admission"),
    ("Eligibility for MBA", "admission"),
    ("Courses available", "admission"),
    ("Programs offered", "admission"),
    ("Admission deadline", "admission"),
    ("Last date for admission", "admission"),
    ("Admission requirements", "admission"),

    # Additional semantic variations for admissions
    ("can you tell me the fee structure?", "admission"),
    ("admission criteria and intake", "admission"),
    ("course eligibility information", "admission"),
    ("what is the intake for B.Tech?", "admission"),
    ("how to get course information", "admission"),
    ("admissions and eligibility guidelines", "admission"),
    ("eligibility requirements for B.Tech", "admission"),
    ("fees structure for MBA", "admission"),
    ("fees structure for MCA", "admission"),
    
    # 2. exam (dates, schedules, venue, duration, types)
    ("when is the exams starting?", "exam"),
    ("what is the exam schedule?", "exam"),
    ("where is the exam hall?", "exam"),
    ("when is data structures exam?", "exam"),
    ("timetable for final exams", "exam"),
    ("duration of exam and rules", "exam"),
    ("is there any exam scheduled tomorrow?", "exam"),
    ("where is hall 202 for examinations?", "exam"),
    ("examination date sheet", "exam"),
    ("mid term exam schedule", "exam"),
    ("when are the practical exams?", "exam"),
    ("where is my end semester exam?", "exam"),
    ("final exam date", "exam"),
    ("when is the final exam?", "exam"),
    ("exam dates", "exam"),
    ("practical exam schedule at RIT", "exam"),
    ("exam halls and dates", "exam"),
    ("what is the date of exam?", "exam"),
    ("when does the end semester exam start?", "exam"),
    ("where is the exam hall for MCA?", "exam"),
    
    # 3. timetable (schedules, lectures, timings, rooms, faculty)
    ("class timetable for this week", "timetable"),
    ("show me the class schedule", "timetable"),
    ("what time is artificial intelligence class?", "timetable"),
    ("who teaches software engineering?", "timetable"),
    ("which room is the math lecture in?", "timetable"),
    ("what class do I have on Tuesday?", "timetable"),
    ("when does Analog Circuits start?", "timetable"),
    ("class timing", "timetable"),
    ("timetable details", "timetable"),
    ("daily lectures schedule", "timetable"),
    ("who is teaching CAD/CAM lab?", "timetable"),
    ("what room is class in today?", "timetable"),
    ("what is the class timetable?", "timetable"),
    ("class timings for computer science", "timetable"),
    ("lecture schedule for B.Tech", "timetable"),
    ("who is the teacher for maths?", "timetable"),
    ("which classroom is B.Tech lecture in?", "timetable"),
    ("when is the next class?", "timetable"),
    ("show class timetable", "timetable"),
    
    # 4. student_query (Generic campus queries: library, hostel, placements, etc. that route to FAQ)
    ("is library open on saturdays?", "student_query"),
    ("what are library timings?", "student_query"),
    ("how to borrow library books?", "student_query"),
    ("where is the central library?", "student_query"),
    ("how to apply for hostel?", "student_query"),
    ("hostel room allocation and fee", "student_query"),
    ("where is the hostel wardens office?", "student_query"),
    ("is hostel room available?", "student_query"),
    ("what is the placement record?", "student_query"),
    ("how to contact placement cell?", "student_query"),
    ("who is the placement officer?", "student_query"),
    ("companies visiting for placement", "student_query"),
    ("official marksheet verification procedure", "student_query"),
    ("where to get official transcripts?", "student_query"),
    ("what is the attendance rule for exams?", "student_query"),
    ("debarment rule for attendance shortfall", "student_query"),
    ("where is the library located?", "student_query"),
    ("library opening hours", "student_query"),
    ("hostel admission eligibility details", "student_query"),
    ("hostel rules and regulations", "student_query"),
    ("placement statistics at RIT", "student_query")
]

def evaluate_model(X, y):
    """
    Evaluates the classifier using 5-Fold Stratified Cross-Validation
    and prints accuracy and confusion matrix.
    """
    # Create Pipeline elements
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    model = MultinomialNB()
    
    # Stratified K-Fold
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    acc_scores = []
    classes = sorted(list(set(y)))
    n_classes = len(classes)
    cv_conf_matrix = np.zeros((n_classes, n_classes), dtype=int)
    
    X_arr = np.array(X)
    y_arr = np.array(y)
    
    for train_idx, test_idx in skf.split(X_arr, y_arr):
        X_train, X_test = X_arr[train_idx], X_arr[test_idx]
        y_train, y_test = y_arr[train_idx], y_arr[test_idx]
        
        # Fit vectorizer on training fold
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        # Train classifier
        fold_model = MultinomialNB()
        fold_model.fit(X_train_vec, y_train)
        
        # Predict
        preds = fold_model.predict(X_test_vec)
        acc_scores.append(accuracy_score(y_test, preds))
        
        # Accumulate confusion matrix
        cm = confusion_matrix(y_test, preds, labels=classes)
        cv_conf_matrix += cm
        
    print("\n" + "="*50)
    print("      MODEL CROSS-VALIDATION PERFORMANCE REPORT")
    print("="*50)
    print(f"Stratified 5-Fold CV Accuracy: {np.mean(acc_scores)*100:.2f}% (Std: {np.std(acc_scores)*100:.2f}%)")
    
    print("\nConfusion Matrix (Rows = Actual, Columns = Predicted):")
    # Print header
    header = f"{'Actual \\ Pred':<20}" + "".join([f"{cls:<15}" for cls in classes])
    print(header)
    print("-" * len(header))
    for i, actual_cls in enumerate(classes):
        row_str = f"{actual_cls:<20}"
        for j in range(n_classes):
            row_str += f"{cv_conf_matrix[i, j]:<15}"
        print(row_str)
    print("="*50 + "\n")

def train_intent_classifier():
    """
    Trains a Multinomial Naive Bayes classifier on the expanded intent classes
    and saves the vectorizer and model as pickle files.
    """
    print(f"Training NLP Intent Classifier on {len(TRAINING_DATA)} samples...")
    
    X = [text for text, intent in TRAINING_DATA]
    y = [intent for text, intent in TRAINING_DATA]
    
    # First, run the cross-validation evaluation
    evaluate_model(X, y)
    
    # Create and fit the vectorizer and classifier on the full dataset
    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    model = MultinomialNB()
    
    X_vectorized = vectorizer.fit_transform(X)
    model.fit(X_vectorized, y)
    
    # Ensure trained models directory exists
    model_path = Config.MODEL_PATH
    vectorizer_path = Config.VECTORIZER_PATH
    
    # Resolve absolute paths if necessary
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isabs(model_path):
        model_path = os.path.join(project_root, model_path)
    if not os.path.isabs(vectorizer_path):
        vectorizer_path = os.path.join(project_root, vectorizer_path)
        
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    os.makedirs(os.path.dirname(vectorizer_path), exist_ok=True)
    
    # Save the vectorizer and model
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
        
    print(f"[Success] Model saved to {model_path}")
    print(f"[Success] Vectorizer saved to {vectorizer_path}")
    print("Training complete.")

if __name__ == "__main__":
    train_intent_classifier()
