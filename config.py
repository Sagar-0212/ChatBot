import os
from decouple import config

class Config:
    """
    Configuration class for RIT College AI Chatbot.
    Loads values from environment variables via python-decouple, providing sensible defaults.
    """
    # Flask configuration
    SECRET_KEY = config('SECRET_KEY', default='rit-college-chatbot-super-secret-key-12345')
    DEBUG = config('DEBUG', default=False, cast=bool)
    
    # Database configuration (Defaults to local SQLite db inside project structure)
    DATABASE_URL = config('DATABASE_URL', default='sqlite:///database/college_chatbot.db')
    
    # JWT security settings
    JWT_SECRET_KEY = config('JWT_SECRET_KEY', default='rit-college-jwt-token-signing-secret-67890')
    JWT_EXPIRY_HOURS = config('JWT_EXPIRY_HOURS', default=24, cast=int)
    
    # NLP and Machine Learning model paths
    MODEL_PATH = config('MODEL_PATH', default=os.path.join('trained_models', 'chatbot_model.pkl'))
    VECTORIZER_PATH = config('VECTORIZER_PATH', default=os.path.join('trained_models', 'vectorizer.pkl'))
    
    # CORS policy configuration
    CORS_ORIGINS = config('CORS_ORIGINS', default='*')

    @classmethod
    def get_sqlite_db_path(cls) -> str:
        """
        Parses the DATABASE_URL and returns a clean, absolute or relative local file path for sqlite3 library.
        e.g. 'sqlite:///database/college_chatbot.db' -> 'database/college_chatbot.db'
        """
        url = cls.DATABASE_URL
        if url.startswith("sqlite:///"):
            # Strip the prefix to get the file path
            path = url[10:]
            # Ensure it resolves correctly
            return path
        return url
