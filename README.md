# 🧠 Soul Sense EQ Test

Soul Sense EQ Test is a desktop-based Emotional Intelligence (EQ) assessment application built using Python, Tkinter, and SQLite.
It provides a✅ Tip: If you see `ModuleNotFoundError`, it usually means your virtual environment is **not active** or the package isn't installed inside it.

---

## 🌍 Multi-language Support

SoulSense now supports multiple languages with easy switching!

### Supported Languages
- **English** (default)
- **हिंदी (Hindi)**
- **Español (Spanish)**

### Quick Start
1. Launch the application
2. Select your language from the dropdown at the top of the main screen
3. All UI elements update instantly
4. Your preference is saved automatically

### For Contributors
Want to add your language? See our [I18N Guide](I18N_GUIDE.md) for:
- Step-by-step instructions
- Translation template
- Testing guidelines

---

## 🔐 Admin Interface

SoulSense includes a powerful admin interface for managing questions and categories.

### Features
- **GUI Admin Panel** - User-friendly graphical interface
- **CLI Tool** - Command-line interface for automation
- **Secure Access** - Password-protected admin accounts
- **CRUD Operations** - Create, Read, Update, Delete questions
- **Category Management** - Organize questions by category
- **Metadata Support** - Age range, difficulty, weight customization

### Quick Start

**Create Admin Account:**
```bash
python admin_cli.py create-admin --no-auth
```

**Launch GUI:**
```bash
python admin_interface.py
```

**CLI Commands:**
```bash
python admin_cli.py list                    # List all questions
python admin_cli.py add                     # Add new question
python admin_cli.py view --id 1             # View question
python admin_cli.py update --id 1           # Update question
python admin_cli.py delete --id 1           # Delete question
python admin_cli.py categories              # View statistics
```

### Documentation
See [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for comprehensive documentation.

---

## ▶️ How to Runeractive self-reflection test, persists results locally, and is designed with maintainability, testability, and extensibility in mind.

**🌍 Now available in multiple languages: English, Hindi (हिंदी), and Spanish (Español)!**

---

## ✨ Features

- **🌐 Multi-language Support (NEW!)**
  - English, Hindi, and Spanish translations
  - Easy language switching from the UI
  - Persistent language preferences
  - Simple framework for adding more languages
- **User Authentication System**
  - Secure user registration and login
  - Password hashing with SHA-256
  - Session management with logout functionality
  - User-specific data tracking
- **Outlier Detection & Data Quality**
  - Statistical outlier detection using multiple methods (Z-score, IQR, MAD, Modified Z-score)
  - Ensemble outlier detection with consensus voting
  - Inconsistency pattern detection for users
  - Age-group and global analysis capabilities
  - Comprehensive data quality reporting
- Interactive Tkinter-based GUI
- SQLite-backed persistence for questions, responses, and scores
- Questions loaded once into the database, then read-only at runtime
- Automatic EQ score calculation with interpretation
- Stores:
  - Per-question responses
  - Final EQ score
  - Optional age and age group
  - User authentication data
- Backward-compatible database schema migrations
- Pytest-based test suite with isolated temporary databases
- Daily emotional journal with AI sentiment analysis
- Emotional pattern tracking and insights
- View past journal entries and emotional journey

---

## 📝 Journal Feature

The journal feature allows users to:

- Write daily emotional reflections
- Get AI-powered sentiment analysis of entries
- Track emotional patterns over time
- View past entries and emotional journey
- Receive insights on stress indicators, growth mindset, and self-reflection

**AI Analysis Capabilities:**

- **Sentiment Scoring:** Analyzes positive/negative emotional tone using NLTK's VADER
- **Pattern Detection:** Identifies stress indicators, relationship focus, growth mindset, and self-reflection
- **Emotional Tracking:** Monitors emotional trends over time

---

## 🧠 Sentiment Analysis Integration

### Overview

Soul Sense integrates **NLTK's VADER (Valence Aware Dictionary and sEntiment Reasoner)** sentiment analysis into both the EQ test and journal features, providing a more comprehensive understanding of users' emotional states.

### How It Helps Users

#### 1. **Captures Emotional Context Beyond Multiple Choice**

- MCQ questions only capture structured responses (Never/Sometimes/Often/Always)
- Open-ended reflection reveals **actual emotional state** in the user's own words
- Detects disconnect between quantitative scores and qualitative feelings

#### 2. **More Nuanced Risk Assessment**

The AI Analysis considers:

- **Quantitative data**: EQ scores (structured responses)
- **Qualitative data**: Sentiment score from written reflection (-100 to +100)

This dual analysis provides insights like:

- `High EQ + Negative Sentiment` = Good skills but currently struggling
- `Low EQ + Positive Sentiment` = Room for growth but good emotional resilience

#### 3. **Personalized Recommendations**

Based on sentiment ranges:

- **Negative (-20 to -100)**: Suggests journaling, professional support, stress management
- **Neutral (-20 to +20)**: Encourages continued practice
- **Positive (+20 to +100)**: Reinforces strengths, suggests mentorship

#### 4. **Validation & Empathy**

- Users feel heard when their written reflection is analyzed
- System acknowledges current emotional state
- Creates more human interaction vs. just numbers

### Technical Implementation

**VADER Features:**

- ✅ Understands negation: "I am NOT happy" → negative
- ✅ Detects intensity: "devastatingly sad" vs. "a bit sad"
- ✅ Works on casual, everyday language
- ✅ Real-time analysis with no external API calls

### Where Results Are Shown

1. **Results Dashboard**: Displays sentiment score alongside EQ score
2. **AI Analysis Popup**: Comprehensive analysis with:
   - Risk level and confidence
   - Sentiment score interpretation
   - Top influencing factors
   - Personalized recommendations based on both EQ and sentiment
3. **Journal Analytics**: Tracks sentiment trends over time (when using Daily Journal)

---

## 🛠 Technologies Used

- Python 3.11+
- Tkinter (GUI)
- SQLite3 (Database)
- Pytest (Testing)

---

## 📂 Project Structure (Refactored)

```bash
SOUL_SENSE_EXAM/
│
├── app/                     # Core application package
│   ├── __init__.py
│   ├── main.py              # Tkinter application entry point
│   ├── config.py            # Centralized configuration
│   ├── db.py                # Database connection & migrations
│   ├── models.py            # SQLAlchemy models
│   ├── auth.py              # Authentication logic
│   ├── questions.py         # Question loading logic
│   └── utils.py             # Shared helpers
│
├── migrations/              # Alembic migrations
│   ├── versions/            # Migration scripts
│   └── env.py               # Alembic config
│
├── scripts/                 # Maintenance scripts
│   ├── __init__.py
│   └── load_questions.py    # Seed data loader
│
├── data/
│   └── questions.txt        # Source question bank
│
├── db/
│   └── soulsense.db         # SQLite database
│
├── tests/                   # Pytest test suite
│
├── logs/
│   └── soulsense.log        # Application logs
│
├── alembic.ini              # Alembic config
├── pytest.ini               # Pytest config
├── requirements.txt         # Dependencies
└── README.md
```

---

## 🧩 Question Format

Each question is rated on a 4-point Likert scale:

- Never (1)
- Sometimes (2)
- Often (3)
- Always (4)

### Sample Questions

- You can recognize your emotions as they happen.
- You adapt well to changing situations.
- You actively listen to others when they speak.

---

## 🐍 Setting Up a Virtual Environment & Installing Packages

It’s recommended to use a **virtual environment** to keep your project dependencies isolated from your system Python.

1️⃣ Create a Virtual Environment  
From your project root directory:

```bash
python -m venv venv
```

This will create a `venv/` folder inside your project.

2️⃣ Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

When active, your terminal prompt will show `(venv)`.

3️⃣ Install Required Packages

Once activated, install your project dependencies:

```bash
pip install -r requirements.txt
```

<!--4️⃣ Save Dependencies (Optional but Recommended)

Freeze installed packages to a `requirements.txt` file:
pip freeze > requirements.txt

Later, to replicate the environment on another machine:
pip install -r requirements.txt -->

> Always **activate the virtual environment** before running scripts or installing new packages.

✅ Tip: If you see `ModuleNotFoundError`, it usually means your virtual environment is **not active** or the package isn’t installed inside it.

---

## ▶️ How to Run

### 1. Database Setup

Ensure your database schema is up to date:

```bash
python -m alembic upgrade head
```

### 2. Start the Application

Launch the SoulSense interface:

```bash
python -m app.main
```

## 🛠️ Troubleshooting & Developer Notes

### Common Issues & Fixes

1.  **"Failed to fetch questions from DB" / `KeyError: min_age`**

    - **Cause**: Database schema is outdated (missing columns in `QuestionCache`).
    - **Fix**: Run migration or reset database:
      ```bash
      python -m scripts.fix_db
      python -m scripts.load_questions
      ```

2.  **`ImportError: cannot import name 'get_session' from 'app.models'`**

    - **Fix**: This project strictly separates DB connection logic (`app.db`) from models (`app.models`). Ensure you import `get_session` from `app.db`.

3.  **Application Freeze on Startup**

    - **Cause**: Matplotlib trying to use an interactive backend (TkAgg) conflicting with Tkinter main loop.
    - **Fix**: Ensure `matplotlib.use('Agg')` is called _before_ importing `pyplot`.

4.  **`ObjectNotExecutableError`**
    - **Cause**: SQLAlchemy 2.0+ requires raw SQL to be wrapped in `text()`.
    - **Fix**: Use `from sqlalchemy import text` and wrap strings: `connection.execute(text("SELECT ..."))`.

### For Contributors

- Always install new dependencies via `pip install -r requirements.txt`.
- If you change the database models, generate a migration: `python -m alembic revision --autogenerate -m "message"`.
- This project uses **SQLAlchemy 2.0** syntax. Avoid legacy query patterns.

> **Note:** Do not use `npm run dev`. This is a pure Python application.

**Authentication Flow:**

1. **First-time users:** Click "Sign Up" to create an account

   - Choose a username (minimum 3 characters)
   - Set a password (minimum 4 characters)
   - Confirm your password

2. **Returning users:** Enter your username and password to login

3. **During the test:** Use the logout button to switch users or exit securely

**Security Features:**

- Passwords are hashed using SHA-256 encryption
- User sessions are managed securely
- Each user's data is isolated and protected

---

## 🧪 Running Tests

From the project root:

```bash
    python -m pytest -v
```

Tests use temporary SQLite databases and do not affect production data.

### Running Outlier Detection Tests

```bash
    python -m pytest tests/test_outlier_detection.py -v
```

---

## 📊 Outlier Detection Feature

### Overview

The outlier detection module identifies extreme or inconsistent emotional intelligence scores using advanced statistical methods.

**Supported Methods:**
- **Z-Score**: Identifies scores deviating significantly from mean
- **IQR (Interquartile Range)**: Robust method for skewed distributions
- **Modified Z-Score**: Uses median/MAD for robustness
- **MAD (Median Absolute Deviation)**: Resistant to extreme values
- **Ensemble**: Consensus-based approach combining multiple methods

### Command Line Usage

```bash
# Analyze user scores
python scripts/outlier_analysis.py --user john_doe --method ensemble

# Analyze age group
python scripts/outlier_analysis.py --age-group "18-25" --method iqr

# Global analysis
python scripts/outlier_analysis.py --global --method zscore

# Check inconsistency patterns
python scripts/outlier_analysis.py --inconsistency john_doe --days 30

# Get statistics
python scripts/outlier_analysis.py --stats --age-group "26-35"

# Output as JSON
python scripts/outlier_analysis.py --user john_doe --format json
```

### Python API

```python
from app.db import get_session
from app.outlier_detection import OutlierDetector

detector = OutlierDetector()
session = get_session()

# Detect outliers for user
result = detector.detect_outliers_for_user(session, "john_doe", method="ensemble")

# Detect by age group
result = detector.detect_outliers_by_age_group(session, "18-25", method="iqr")

# Global analysis
result = detector.detect_outliers_global(session, method="zscore")

# Inconsistency analysis
result = detector.detect_inconsistency_patterns(session, "john_doe", time_window_days=30)
```

---

## 🧱 Design Notes

- Database schemas are created and migrated safely at runtime
- Question loading is idempotent and separated from application logic
- Core logic is decoupled from the GUI to enable testing
- Outlier detection uses NumPy for efficient statistical computations
- All methods are fully tested with comprehensive edge case coverage

---

## 📌 Status

- Refactor complete
- Tests added
- Stable baseline for further enhancements (e.g., decorators, generators)

## 🤝 Contributing

We welcome contributions from the community.  
Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing to help maintain a respectful and inclusive environment.
