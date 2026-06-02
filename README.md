# RIT College AI Chatbot

A fully working, database-driven web application featuring an AI Chatbot and administrative management panel designed for Rajarambapu Institute of Technology (RIT). The application automatically bootstraps itself on the first run, creating the database, seeding sample RIT-specific datasets, training the NLP classifier, and launching the server.

---

## Project Overview
The RIT College AI Chatbot allows students to ask questions about admissions, exams, timetables, and campus facilities. Instead of hardcoded responses, the chatbot uses a scikit-learn Naive Bayes NLP intent classifier to predict student intents, combined with a precise word-boundary fallback override, and dynamically queries the SQLite3 database to construct real-time responses.

Administrators can log in to a secure dashboard to manage all informational records (Admissions, Exams, Timetables, and FAQs) using modern CRUD interfaces. Any updates made in the dashboard immediately affect chatbot responses without requiring model retraining.

---

## Features
- **Dynamic Database-Driven Responses**: All chatbot responses for admissions, exams, timetables, and FAQs are generated on-the-fly from live SQLite database tables.
- **NLP Intent Classification & Routing**: Powered by a scikit-learn Naive Bayes classifier trained on an expanded RIT-specific corpus.
- **Word-Boundary Fallback Scanner**: Intercepts low-confidence inputs using robust word boundaries (regex `\b`) to route queries (e.g. queries containing "fee" or "intake") before falling back to FAQ similarity search.
- **Secure Admin Panel**: Modern CRUD dashboard supporting Add, Edit, and Delete actions for all tables, built with styled modals and dynamic AJAX updates.
- **Auto-Bootstrapping**: First-run friendly startup script that detects missing databases or model pickle files, initializes schemas, seeds realistic RIT data, trains the NLP model, and launches the server.

---

## Technologies Used
- **Core backend**: Python 3.11+, Flask 3.x
- **Database**: SQLite3
- **Machine Learning**: scikit-learn (TF-IDF Vectorizer + Multinomial Naive Bayes)
- **Frontend / Styling**: Jinja2 Templates, Vanilla CSS (harmonious slate/blue palette, responsive layouts, micro-animations)
- **Testing**: pytest

---

## Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Sagar-0212/ChatBot.git
   cd ChatBot
   ```

2. **Install Dependencies**:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

---

## Run Commands

Launch the application with a single command:
```bash
python run.py
```

### What happens on the first run:
1. **Database Check**: Verifies if `database/college_chatbot.db` exists. If not, runs `database/init_db.py` to create tables and insert RIT-specific seed data.
2. **Model Check**: Checks if the model (`trained_models/chatbot_model.pkl`) exists. If missing, runs `app/nlp/train_model.py` to train and pickle the classifier.
3. **Server Launch**: Automatically boots the Flask web server at `http://127.0.0.1:5000/`.

---

## Verification & Testing
To run the automated integration tests:
```bash
pytest
```

---

## Screenshots Section

### Chatbot UI Interface
*(Placeholder for chatbot interface screenshot)*

### Admin CRUD Dashboard
*(Placeholder for admin panel and CRUD modals screenshot)*
