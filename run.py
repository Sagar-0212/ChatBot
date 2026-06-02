import os
import sys

# Add current folder to sys.path to resolve imports correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def perform_first_run_checks():
    """
    Checks for the existence of database and model files on startup.
    Automatically initializes the database and trains the model if missing.
    """
    print("=" * 60)
    print("                BOOTSTRAPPING RIT CAMPUS CHATBOT")
    print("=" * 60)

    # 1. Check database existence
    db_path = Config.get_sqlite_db_path()
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)
        
    if not os.path.exists(db_path):
        print(">>> [First Run Indicator] SQLite database file not found.")
        print(f"    Expected path: {db_path}")
        print(">>> Running database/init_db.py to create schemas and seed initial data...")
        try:
            from database.init_db import init_database
            init_database()
            print(">>> [Success] Database successfully created and seeded.")
        except Exception as e:
            print(f">>> [Critical Error] Failed to initialize database: {e}")
            sys.exit(1)
    else:
        print(">>> [Status] SQLite database verified.")

    # 2. Check NLP model files existence
    model_path = Config.MODEL_PATH
    vectorizer_path = Config.VECTORIZER_PATH
    if not os.path.isabs(model_path):
        model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), model_path)
    if not os.path.isabs(vectorizer_path):
        vectorizer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), vectorizer_path)

    if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
        print(">>> [First Run Indicator] NLP model/vectorizer pickle files missing.")
        print(f"    Expected model path: {model_path}")
        print(f"    Expected vectorizer path: {vectorizer_path}")
        print(">>> Running app/nlp/train_model.py to train the intent classifier...")
        try:
            from app.nlp.train_model import train_intent_classifier
            train_intent_classifier()
            print(">>> [Success] NLP model successfully trained and pickled.")
        except Exception as e:
            print(f">>> [Critical Error] Failed to train NLP model: {e}")
            sys.exit(1)
    else:
        print(">>> [Status] NLP model files verified.")
    print("=" * 60)

# Run the bootstrapping checks before the Flask app factory creates the app instance
# This ensures that the NLPEngine does not load empty models or fail to connect to tables
perform_first_run_checks()

# Import create_app and instantiate Flask application
from app import create_app
app = create_app()

if __name__ == '__main__':
    debug_mode = Config.DEBUG
    db_path = Config.get_sqlite_db_path()
    if not os.path.isabs(db_path):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), db_path)

    print(" * Mode:        {'Development (Debug)' if debug_mode else 'Production'}")
    print(f" * Database:    {db_path}")
    print(f" * Models Dir:  {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained_models')}")
    print(" * Actions:     Visit http://127.0.0.1:5000/ to chat")
    print("                Visit http://127.0.0.1:5000/admin/login for admin controls")
    print("=" * 60)

    # Run the web server
    app.run(host='127.0.0.1', port=5000, debug=debug_mode)
