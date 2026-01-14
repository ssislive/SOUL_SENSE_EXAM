# Soul Sense Exam - File Architecture Guide

This document maps each **Wave/Phase/Step** from `CONTRIBUTOR_ROADMAP.md` to specific files and directories.
Use this as a reference to know **WHERE** to write your code.

---

## 📁 Current Project Structure (Desktop App)

```
SOUL_SENSE_EXAM/
├── app/                        # 🎯 CORE APPLICATION (Desktop)
│   ├── __init__.py
│   ├── main.py                 # Entry point (Tkinter app)
│   ├── models.py               # SQLAlchemy database models
│   ├── db.py                   # Database connection
│   ├── auth.py                 # Authentication logic
│   ├── config.py               # App configuration
│   ├── constants.py            # Global constants
│   ├── questions.py            # Question loading/management
│   ├── utils.py                # Utility functions
│   │
│   ├── ui/                     # 🎨 TKINTER UI VIEWS
│   │   ├── auth.py             # Login/Register screens
│   │   ├── dashboard.py        # Main dashboard
│   │   ├── exam.py             # Quiz/Exam interface
│   │   ├── journal.py          # Daily journaling
│   │   ├── profile.py          # User profile (Medical, Personal, Strengths)
│   │   ├── settings.py         # Settings screen
│   │   ├── results.py          # Exam results display
│   │   ├── daily_view.py       # Daily history view
│   │   ├── sidebar.py          # Sidebar navigation
│   │   ├── styles.py           # UI themes and colors
│   │   ├── feedback.py         # 🆕 WAVE 1: Feedback Board
│   │   ├── onboarding.py       # 🆕 WAVE 2: Progressive onboarding
│   │   ├── chat.py             # 🆕 WAVE 6: Virtual Friend UI
│   │   ├── analytics.py        # 🆕 WAVE 8: Trend visualizations
│   │   │
│   │   └── components/         # 🧩 REUSABLE UI COMPONENTS
│   │       ├── timeline.py     # Life events timeline
│   │       ├── tag_input.py    # Tag/chip input widget
│   │       ├── image_cropper.py# Avatar cropper
│   │       └── slider_group.py # 🆕 Grouped sliders component
│   │
│   ├── ml/                     # 🤖 MACHINE LEARNING
│   │   ├── models/             # Trained model files (.pkl)
│   │   ├── risk_predictor.py   # Risk prediction logic
│   │   └── clustering/         # Clustering models
│   │
│   ├── services/               # 🔧 BUSINESS LOGIC SERVICES
│   │   ├── sync.py             # 🆕 WAVE 4: Cloud sync engine
│   │   ├── notifications.py    # 🆕 WAVE 5: Reminder system
│   │   └── feedback_service.py # 🆕 WAVE 1: Feedback logic
│   │
│   └── locales/                # 🌐 INTERNATIONALIZATION
│       ├── en.json
│       └── ...
│
├── scripts/                    # 🛠️ UTILITY SCRIPTS
│   ├── seed_db.py              # Database seeding
│   ├── admin_cli.py            # Admin CLI
│   ├── ml_training_pipeline.py # ML training scripts
│   ├── anonymize_data.py       # 🆕 WAVE 8: Data anonymization
│   └── ...
│
├── migrations/                 # 📦 ALEMBIC MIGRATIONS
│   └── versions/               # Each model change needs a migration here
│
├── tests/                      # 🧪 TEST FILES
│   ├── unit/                   # Unit tests
│   │   ├── test_models.py
│   │   ├── test_agents.py      # 🆕
│   │   └── ...
│   ├── integration/            # Integration tests
│   │   ├── test_api.py         # 🆕
│   │   └── ...
│   └── ui/                     # UI tests
│       └── test_feedback.py    # 🆕
│
├── data/                       # 💾 LOCAL DATA
│   ├── soulsense.db            # SQLite database
│   └── cache/                  # Cached data
│
├── docs/                       # 📚 DOCUMENTATION
│   ├── api/                    # 🆕 API documentation
│   │   └── openapi.yaml        # 🆕 API schema
│   └── ml/                     # 🆕 ML methodology docs
│
├── .github/                    # 🔄 GITHUB CONFIGURATION
│   ├── workflows/              # GitHub Actions
│   │   ├── python-app.yml      # CI/CD
│   │   └── label-feedback.yml  # 🆕 WAVE 1
│   └── ISSUE_TEMPLATE/         # Issue templates
│       └── feedback.yml        # 🆕 WAVE 1
│
├── .env.example                # 🆕 Environment variables template
├── config.json                 # App configuration
└── requirements.txt            # Python dependencies
```

---

## 🆕 Proposed Expansion Structure

```
SOUL_SENSE_EXAM/
├── app/                        # Windows Desktop (existing)
│
├── core/                       # 🆕 SHARED LOGIC (Desktop + Backend)
│   ├── __init__.py
│   ├── models.py               # Shared data models
│   ├── validators.py           # Input validation
│   └── constants.py            # Shared constants
│
├── backend/                    # 🆕 WAVE 4: FastAPI Backend
│   ├── main.py                 # FastAPI entry point
│   ├── requirements.txt        # Backend dependencies
│   ├── Dockerfile              # Container setup
│   ├── .env.example            # Backend env template
│   │
│   ├── auth/                   # Authentication
│   │   ├── __init__.py
│   │   ├── jwt.py              # JWT token logic
│   │   └── dependencies.py     # Auth dependencies
│   │
│   ├── api/                    # API Routes (FastAPI routers)
│   │   ├── __init__.py
│   │   ├── auth.py             # /auth endpoints
│   │   ├── questions.py        # /questions endpoints
│   │   ├── journal.py          # /journal endpoints
│   │   ├── profile.py          # /profile endpoints
│   │   ├── feedback.py         # 🆕 WAVE 1: /feedback endpoints
│   │   └── agents.py           # 🆕 WAVE 3: /agents endpoints
│   │
│   ├── core/                   # Backend core
│   │   ├── database.py         # PostgreSQL connection
│   │   ├── config.py           # Backend config
│   │   └── schemas.py          # Pydantic schemas
│   │
│   ├── agents/                 # 🆕 WAVE 3: AI Agents
│   │   ├── __init__.py
│   │   ├── base.py             # Base Agent class
│   │   ├── orchestrator.py     # Multi-agent coordinator
│   │   ├── assessment.py       # Assessment Agent
│   │   ├── insight.py          # Insight Generator
│   │   ├── safety.py           # Safety Guard
│   │   ├── planner.py          # 🆕 WAVE 5: Task Planner
│   │   ├── virtual_friend.py   # 🆕 WAVE 6: Virtual Friend
│   │   └── memory.py           # 🆕 WAVE 6: Conversation memory
│   │
│   └── llm/                    # 🆕 WAVE 7: LLM Integration
│       ├── __init__.py
│       ├── gateway.py          # LLM API gateway
│       ├── prompts.py          # Prompt management
│       ├── safety_filter.py    # Output safety filter
│       └── rate_limiter.py     # API rate limiting
│
├── frontend-web/               # 🆕 WAVE 4: Next.js Web Client
│   ├── package.json
│   ├── next.config.js
│   ├── .env.example
│   │
│   ├── src/
│   │   ├── pages/              # Page routes
│   │   │   ├── index.tsx       # Landing page
│   │   │   ├── login.tsx       # Login
│   │   │   ├── register.tsx    # Register
│   │   │   ├── dashboard.tsx   # Dashboard
│   │   │   ├── exam.tsx        # Exam wizard
│   │   │   ├── journal.tsx     # Journal entry
│   │   │   ├── profile.tsx     # Profile settings
│   │   │   ├── feedback.tsx    # 🆕 WAVE 1: Feedback board
│   │   │   └── chat.tsx        # 🆕 WAVE 6: Virtual Friend
│   │   │
│   │   ├── components/         # Reusable components
│   │   │   ├── FeedbackBoard/  # WAVE 1
│   │   │   │   ├── FeedbackList.tsx
│   │   │   │   ├── FeedbackForm.tsx
│   │   │   │   └── VoteButton.tsx
│   │   │   ├── ProfileForm/    # WAVE 2
│   │   │   ├── ChatWindow/     # WAVE 6
│   │   │   └── ...
│   │   │
│   │   └── services/
│   │       ├── api.ts          # API client
│   │       └── auth.ts         # Auth utilities
│   │
│   └── styles/
│       └── globals.css
│
├── mobile-app/                 # 🆕 WAVE 4: Flutter App
│   ├── pubspec.yaml
│   ├── lib/
│   │   ├── main.dart           # Entry point
│   │   ├── screens/
│   │   │   ├── login_screen.dart
│   │   │   ├── journal_screen.dart
│   │   │   └── chat_screen.dart
│   │   ├── widgets/
│   │   ├── services/
│   │   │   ├── api_service.dart
│   │   │   ├── auth_service.dart
│   │   │   └── notification_service.dart  # WAVE 5
│   │   └── models/
│   └── android/ & ios/
│
└── shared/                     # 🆕 SHARED RESOURCES
    ├── prompts/                # LLM prompts (WAVE 7)
    │   ├── mental_health.txt
    │   ├── task_planner.txt
    │   └── virtual_friend.txt
    ├── schemas/                # Shared JSON schemas
    │   └── api_contract.json
    └── locales/                # Shared translations
```

---

## 📍 Complete Step-to-File Mapping

### 🌊 WAVE 1: Community Feedback (All Steps)

| Step      | Description                | File(s)                                                      | Platform |
| --------- | -------------------------- | ------------------------------------------------------------ | -------- |
| **1.1.1** | Feedback Board UI skeleton | `app/ui/feedback.py`                                         | Desktop  |
|           |                            | `frontend-web/src/pages/feedback.tsx`                        | Web      |
| **1.1.2** | Submission Form            | `app/ui/feedback.py` (add form)                              | Desktop  |
|           |                            | `frontend-web/src/components/FeedbackBoard/FeedbackForm.tsx` | Web      |
| **1.1.3** | Connect to DB              | `app/models.py` (add `Feedback` model)                       | All      |
|           |                            | `migrations/versions/xxx_add_feedback.py`                    | All      |
| **1.1.4** | Display List               | `app/ui/feedback.py` (render list)                           | Desktop  |
| **1.2.1** | Upvote Button              | `app/ui/feedback.py` (add vote logic)                        | Desktop  |
|           |                            | `frontend-web/src/components/FeedbackBoard/VoteButton.tsx`   | Web      |
| **1.2.2** | Status Badges              | `app/ui/feedback.py` (add status display)                    | Desktop  |
| **1.2.3** | Roadmap View               | `app/ui/feedback.py` (add filter)                            | Desktop  |
| **1.2.4** | User Notifications         | `app/services/notification_service.py` (NEW)                 | All      |
| **1.3.1** | GitHub Template            | `.github/ISSUE_TEMPLATE/feedback.yml`                        | GitHub   |
| **1.3.2** | Feedback-to-Issue Script   | `scripts/feedback_to_github.py` (NEW)                        | Scripts  |
| **1.3.3** | Auto-Label Action          | `.github/workflows/label-feedback.yml`                       | GitHub   |
| **1.3.4** | Auto-Close Action          | `.github/workflows/close-on-merge.yml`                       | GitHub   |
| **1.3.5** | Moderation Guidelines      | `docs/MODERATION.md` (NEW)                                   | Docs     |
| **1.3.6** | Rate Limiting              | `app/services/feedback_service.py`                           | All      |
| **1.4.1** | Sentiment Analysis         | `backend/agents/feedback_analyzer.py` (NEW)                  | Backend  |
| **1.4.2** | Duplicate Detection        | Same as above                                                | Backend  |
| **1.4.3** | AI Summarization           | Same as above                                                | Backend  |
| **1.4.4** | Auto-Tag Suggestion        | Same as above                                                | Backend  |

---

### 🌊 WAVE 2: Profile Expansion (All Steps)

| Step      | Description            | File(s)                                                  |
| --------- | ---------------------- | -------------------------------------------------------- |
| **2.1.1** | Support System Input   | `app/ui/profile.py` → `_render_lifestyle_view()`         |
| **2.1.2** | Relationship Stress    | Same as above                                            |
| **2.1.3** | Social Interaction     | Same as above                                            |
| **2.1.4** | Exercise Frequency     | Same as above                                            |
| **2.1.5** | Dietary Patterns       | Same as above                                            |
| **2.1.6** | Screen Time            | Same as above                                            |
| **2.2.1** | Short-Term Goals       | `app/ui/profile.py` → `_render_goals_view()` (NEW)       |
| **2.2.2** | Long-Term Vision       | Same as above                                            |
| **2.2.3** | Current Challenge      | Same as above                                            |
| **2.2.4** | Primary Help Area      | Same as above                                            |
| **2.3.1** | Decision Style         | `app/ui/profile.py` → `_render_preferences_view()` (NEW) |
| **2.3.2** | Risk Tolerance         | Same as above                                            |
| **2.3.3** | Change Readiness       | Same as above                                            |
| **2.3.4** | Advice Frequency       | Same as above                                            |
| **2.3.5** | Reminder Style         | Same as above                                            |
| **2.3.6** | Advice Boundaries      | Same as above                                            |
| **2.3.7** | AI Trust Level         | Same as above                                            |
| **2.4.1** | Consent Modal          | `app/ui/onboarding.py` (NEW)                             |
| **2.4.2** | Emergency Disclaimer   | Same as above                                            |
| **2.4.3** | Crisis Support Toggle  | Same as above                                            |
| **2.4.4** | Editable Profile       | `app/ui/profile.py` (ensure edit mode)                   |
| **2.4.5** | Progressive Onboarding | `app/ui/onboarding.py` (wizard flow)                     |
| **DB**    | New Profile Fields     | `app/models.py` → Extend `PersonalProfile`               |
|           |                        | `migrations/versions/xxx_expand_profile.py`              |

---

### 🌊 WAVE 3: AI Agent Architecture (All Steps)

| Step      | Description            | File(s)                                   |
| --------- | ---------------------- | ----------------------------------------- |
| **3.1.1** | Base Agent Class       | `backend/agents/base.py`                  |
| **3.1.2** | Orchestration Layer    | `backend/agents/orchestrator.py`          |
| **3.1.3** | Agent Logging          | `backend/agents/base.py` (add logging)    |
| **3.1.4** | Agent API Wrapper      | `backend/api/agents.py`                   |
| **3.1.5** | Context Memory Module  | `backend/agents/memory.py`                |
| **3.2.1** | Assessment Agent       | `backend/agents/assessment.py`            |
| **3.2.2** | Insight Generator      | `backend/agents/insight.py`               |
| **3.2.3** | Question Rephraser     | `backend/agents/rephraser.py` (NEW)       |
| **3.2.4** | Personalization Agent  | `backend/agents/personalization.py` (NEW) |
| **3.3.1** | Safety Guard Agent     | `backend/agents/safety.py`                |
| **3.3.2** | Confidence Scoring     | `backend/agents/base.py` (add method)     |
| **3.3.3** | Human-in-Loop Queue    | `backend/agents/review_queue.py` (NEW)    |
| **3.3.4** | Performance Monitoring | `backend/agents/metrics.py` (NEW)         |
| **3.3.5** | Fallback Agent         | `backend/agents/fallback.py` (NEW)        |
| **3.3.6** | Privacy Filter         | `backend/agents/privacy.py` (NEW)         |
| **Tests** | Agent Tests            | `tests/unit/test_agents.py`               |

---

### 🌊 WAVE 4: Platform Expansion (All Steps)

| Step      | Description           | File(s)                                                    |
| --------- | --------------------- | ---------------------------------------------------------- |
| **4.1.1** | FastAPI Setup         | `backend/main.py`, `backend/requirements.txt`              |
| **4.1.2** | PostgreSQL Connection | `backend/core/database.py`                                 |
| **4.1.3** | JWT Auth              | `backend/auth/jwt.py`, `backend/api/auth.py`               |
| **4.1.4** | Questions API         | `backend/api/questions.py`                                 |
| **4.1.5** | Journal API           | `backend/api/journal.py`                                   |
| **4.1.6** | Profile API           | `backend/api/profile.py`                                   |
| **4.2.1** | Web Project Setup     | `frontend-web/package.json`, `frontend-web/next.config.js` |
| **4.2.2** | Web Login/Register    | `frontend-web/src/pages/login.tsx`, `register.tsx`         |
| **4.2.3** | Web Dashboard         | `frontend-web/src/pages/dashboard.tsx`                     |
| **4.2.4** | Web Exam              | `frontend-web/src/pages/exam.tsx`                          |
| **4.2.5** | Web Journal           | `frontend-web/src/pages/journal.tsx`                       |
| **4.2.6** | Web Profile           | `frontend-web/src/pages/profile.tsx`                       |
| **4.3.1** | Mobile Setup          | `mobile-app/pubspec.yaml`, `mobile-app/lib/main.dart`      |
| **4.3.2** | Mobile Auth           | `mobile-app/lib/screens/login_screen.dart`                 |
| **4.3.3** | Mobile Journal        | `mobile-app/lib/screens/journal_screen.dart`               |
| **4.3.4** | Push Notifications    | `mobile-app/lib/services/notification_service.dart`        |
| **4.3.5** | Offline Caching       | `mobile-app/lib/services/cache_service.dart` (NEW)         |
| **4.4.1** | Desktop Sync Engine   | `app/services/sync.py`                                     |
| **4.4.2** | Hybrid Mode           | `app/services/sync.py` (add offline logic)                 |

---

### 🌊 WAVE 5: AI Task Planner (All Steps)

| Step      | Description             | File(s)                                                      |
| --------- | ----------------------- | ------------------------------------------------------------ |
| **5.1.1** | Task Planning Agent     | `backend/agents/planner.py`                                  |
| **5.1.2** | Daily Suggestions       | `backend/agents/planner.py` (add method)                     |
| **5.1.3** | Mood-Aware Adjustment   | `backend/agents/planner.py` (add method)                     |
| **5.1.4** | Priority Classification | `backend/agents/planner.py` (add method)                     |
| **5.2.1** | Reminder System         | `app/services/notifications.py` (Desktop)                    |
|           |                         | `mobile-app/lib/services/notification_service.dart` (Mobile) |
| **5.2.2** | Reflection Prompts      | `backend/agents/planner.py` (add method)                     |
| **5.2.3** | Burnout Detection       | `backend/agents/planner.py` (add method)                     |

---

### 🌊 WAVE 6: Virtual Friend (All Steps)

| Step      | Description         | File(s)                                            |
| --------- | ------------------- | -------------------------------------------------- |
| **6.1.1** | Conversation Agent  | `backend/agents/virtual_friend.py`                 |
| **6.1.2** | Empathetic Engine   | `backend/agents/virtual_friend.py` (add method)    |
| **6.1.3** | Conversation Memory | `backend/agents/memory.py`                         |
| **6.1.4** | Emotional Check-in  | `backend/agents/virtual_friend.py` (add method)    |
| **6.2.1** | Boundary Control    | `backend/agents/virtual_friend.py` (add limits)    |
| **6.2.2** | Crisis Detection    | `backend/agents/safety.py` (extend)                |
| **6.2.3** | Tone Customization  | `backend/agents/virtual_friend.py` (add setting)   |
| **6.2.4** | Insight Mapping     | `backend/agents/virtual_friend.py` (add method)    |
| **UI**    | Chat Interface      | `app/ui/chat.py` (Desktop)                         |
|           |                     | `frontend-web/src/pages/chat.tsx` (Web)            |
|           |                     | `mobile-app/lib/screens/chat_screen.dart` (Mobile) |

---

### 🌊 WAVE 7: LLM Integration (All Steps)

| Step      | Description           | File(s)                                     |
| --------- | --------------------- | ------------------------------------------- |
| **7.1.1** | LLM Gateway           | `backend/llm/gateway.py`                    |
| **7.1.2** | Mental Health Prompts | `shared/prompts/mental_health.txt`          |
| **7.1.3** | System Prompt         | `shared/prompts/system.txt`                 |
| **7.1.4** | Context Window Logic  | `backend/llm/gateway.py` (add method)       |
| **7.1.5** | Intent Classification | `backend/llm/intent.py` (NEW)               |
| **7.2.1** | Output Safety Filter  | `backend/llm/safety_filter.py`              |
| **7.2.2** | Pre-LLM Crisis Check  | `backend/llm/safety_filter.py` (add method) |
| **7.2.3** | Confidence Annotation | `backend/llm/gateway.py` (add to response)  |
| **7.3.1** | Short-Term Memory     | `backend/llm/memory.py` (NEW)               |
| **7.3.2** | Insight Summarization | `backend/llm/summarizer.py` (NEW)           |
| **7.3.3** | LLM Task Breakdown    | `backend/llm/task_helper.py` (NEW)          |
| **7.3.4** | Mood-Aware Prompts    | `backend/llm/prompts.py` (NEW)              |
| **7.4.1** | Quality Metrics       | `backend/llm/metrics.py` (NEW)              |
| **7.4.2** | Rate Limiting         | `backend/llm/rate_limiter.py`               |
| **7.4.3** | Model Switching       | `backend/llm/gateway.py` (add fallback)     |

---

### 🌊 WAVE 8: MLOps (All Steps)

| Step      | Description              | File(s)                                            |
| --------- | ------------------------ | -------------------------------------------------- |
| **8.1.1** | Model Comparison         | `scripts/model_comparison.py` (NEW)                |
| **8.1.2** | Dataset Versioning       | `scripts/version_dataset.py` (NEW)                 |
| **8.1.3** | Pipeline Automation      | `scripts/ml_training_pipeline.py` (extend)         |
| **8.1.4** | Error Handling           | `scripts/ml_training_pipeline.py` (add try/except) |
| **8.1.5** | Experiment Logging       | `scripts/ml_training_pipeline.py` (add MLflow/W&B) |
| **8.2.1** | Data Anonymization       | `scripts/anonymize_data.py`                        |
| **8.2.2** | Consent Enforcement      | `backend/api/profile.py` (check consent flag)      |
| **8.3.1** | Risk Classification      | `app/ml/risk_predictor.py` (add tiers)             |
| **8.3.2** | Recommendation Engine    | `backend/agents/recommendation.py` (NEW)           |
| **8.3.3** | Trend Visualization      | `app/ui/analytics.py` (NEW)                        |
| **8.4.1** | Performance Optimization | `app/ml/risk_predictor.py` (optimize)              |
| **8.4.2** | Deployment Strategy      | `docs/DEPLOYMENT.md` (NEW)                         |
| **8.4.3** | ML Documentation         | `docs/ml/methodology.md` (NEW)                     |
| **8.4.4** | Scalability Planning     | `docs/SCALABILITY.md` (NEW)                        |
| **8.4.5** | Finalize Roadmap         | `ROADMAP.md` (update)                              |

---

## 🎯 Quick Reference: Where Do I Code?

| I want to...               | Go to...                                 |
| -------------------------- | ---------------------------------------- |
| Add a Desktop UI screen    | `app/ui/`                                |
| Add a Desktop UI component | `app/ui/components/`                     |
| Add a database table       | `app/models.py` + `migrations/versions/` |
| Add shared logic           | `core/`                                  |
| Create an AI Agent         | `backend/agents/`                        |
| Build an API endpoint      | `backend/api/`                           |
| Add LLM logic              | `backend/llm/`                           |
| Add a Web page             | `frontend-web/src/pages/`                |
| Add a Web component        | `frontend-web/src/components/`           |
| Add a Mobile screen        | `mobile-app/lib/screens/`                |
| Add ML logic               | `app/ml/` or `scripts/`                  |
| Write tests                | `tests/unit/`, `tests/integration/`      |
| Add GitHub automation      | `.github/workflows/`                     |
| Write documentation        | `docs/`                                  |

---

## ⚙️ Configuration Files

| Purpose              | File                        | Notes                    |
| -------------------- | --------------------------- | ------------------------ |
| Desktop environment  | `.env` (root)               | Copy from `.env.example` |
| Backend environment  | `backend/.env`              | API keys, DB connection  |
| Web environment      | `frontend-web/.env.local`   | API URL                  |
| Desktop dependencies | `requirements.txt`          | Python packages          |
| Backend dependencies | `backend/requirements.txt`  | FastAPI, etc.            |
| Web dependencies     | `frontend-web/package.json` | Node packages            |
| Mobile dependencies  | `mobile-app/pubspec.yaml`   | Flutter packages         |
| Database migrations  | `alembic.ini`               | Alembic config           |

---

## 📝 Contributor Checklist

Before submitting a PR:

- [ ] Did I create files in the correct directory per this guide?
- [ ] Did I reference the correct Step # from `CONTRIBUTOR_ROADMAP.md`?
- [ ] Did I create a migration if I changed `models.py`?
- [ ] Did I add tests in `tests/`?
- [ ] Did I update the relevant `requirements.txt` or `package.json`?
- [ ] Did I run `pytest` (Desktop/Backend) or `npm test` (Web)?
- [ ] Did I update `.env.example` if I added new config?
