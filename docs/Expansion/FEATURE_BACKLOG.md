# Soul Sense Exam - Feature Backlog & Contributor Guide

This document organizes the planned **Functionality & AI Features** into logical groups. Contributors can pick an issue from a group to work on.

> **Note:** These features should be implemented following the client-server architecture outlined in `EXPANSION_STRATEGY.md`.

---

## 📢 Group A: Community & User Feedback

**Focus:** Transparency, user engagement, and listening to our community.
**Skill Level:** Beginner/Intermediate (Web/UI focus).

### A1: The Feedback Board

- [ ] **Issue #1**: **Create Public Feedback Board** - A dedicated page for users to see and vote on improvements.
- [ ] **Issue #2**: **Feedback Submission Form** - User-facing form with categories (Bug, Feature, UX).
- [ ] **Issue #4**: **Upvote System** - Allow community voting to prioritize development.

### A2: Feedback Loop & Management

- [ ] **Issue #6**: **Sentiment Analysis** (AI) - Auto-detect if feedback is positive/negative.
- [ ] **Issue #7**: **Duplicate Detection** (AI/NLP) - Auto-merge similar requests.
- [ ] **Issue #10**: **Status Tracking** - Publicly show "In Progress", "Shipped", etc.
- [ ] **Issue #11**: **Notify Users** - Auto-email/notify when their requested feature is live.
- [ ] **Issue #13**: **Feedback Wall UI** - A visual "Community Board" styling.

---

## 🧠 Group B: Core AI Agent Architecture

**Focus:** Backend logic, Multi-Agent Systems (MAS), and Python/FastAPI.
**Skill Level:** Advanced (Backend/AI).

### B1: The "Brain" Infrastructure

- [ ] **Agent #1**: **Architecture Design** - Define the `Agent` class interface (Inputs, Outputs, Memory).
- [ ] **Agent #7**: **Orchestration Layer** - The "Manager" that calls specific agents (Assessment, Insight) in order.
- [ ] **Agent #8**: **API Interface** - Expose agents via REST (e.g., `POST /api/agents/assess`).

### B2: Specialized Agents

- [ ] **Agent #2**: **Assessment Agent** - Selects the next question based on user profile & previous answers.
- [ ] **Agent #3**: **Insight Generator** - Converts raw scores to human-readable text (Rule-based first, then LLM).
- [ ] **Agent #4**: **Safety Guard** - Scans inputs for crisis keywords _before_ processing.

---

## 💬 Group C: Deep Personalization (The Virtual Friend)

**Focus:** NLP, Conversation logic, and User Psychology.
**Skill Level:** Intermediate/Advanced.

### C1: Virtual Friend

- [ ] **Friend #8**: **Conversation Agent** - A chat bot focused on listening and validating (not fixing).
- [ ] **Friend #9**: **Empathetic Engine** - logic to ensure responses validate emotions ("I hear you", "That sounds hard").
- [ ] **Friend #10**: **Context Memory** - Remember "Session 1: Work Stress" to mention it in "Session 2".
- [ ] **Friend #14**: **Tone Customization** - User setting for "Calm", "Cheerleader", or "Rational" persona.

### C2: AI Task Planner

- [ ] **Planner #1**: **Smart Task Breakdown** - Take "Clean House" and break it into "1. Dishes (10m)", "2. Laundry".
- [ ] **Planner #3**: **Mood-Aware Scheduling** - If `Energy < 30%`, suggest "Rest" or "Low Effort" tasks only.
- [ ] **Planner #5**: **Gentle Nudges** - Notifications that encourage ("You got this") rather than demand.

---

## 🛡️ Group D: Advanced ML & LLM Integration

**Focus:** Large Language Models, Safety Filters, Data Pipelines.
**Skill Level:** Expert (Data Science/MLOps).

### D1: LLM Gateway (The Integration Layer)

- [ ] **LLM #1**: **Centralized Gateway** - A single Python service handling all calls to OpenAI/Gemini.
- [ ] **LLM #2**: **Prompt Engineering** - Library of system prompts for "Therapy Friend", "Coach", "Planner".
- [ ] **LLM #6**: **Safety Filter** - Regex & Model-based check to block harmful outputs _after_ generation.

### D2: Data & Analytics

- [ ] **ML #85**: **Data Anonymization** - Pipeline to scrub Names/Emails from datasets.
- [ ] **ML #86**: **Consent Flow** - UI/Backend logic to lock ML features until explicit user consent.
- [ ] **ML #90**: **Trend Visualization** - Generate graphs for "Anxiety over Time" or "Happiness vs Sleep".
- [ ] **ML #92**: **Pipeline Automation** - Scripts to retrain the "Risk Predictor" model monthly.

---

## 🛠️ Group E: Profile Context (Data Collection)

**Focus:** Expanding the data model to support the AI.
**Skill Level:** Beginner/Intermediate (Full Stack).

### E1: Expanded Metrics

- [ ] **Issue #26**: **Support System** - DB field for "Who do you rely on?".
- [ ] **Issue #31**: **Screen Time** - Track work/play balance.
- [ ] **Issue #32**: **Goal Tracking** - Structured input for Short/Long term goals.
- [ ] **Issue #46**: **Editable Profile** - Allow users to update these answers anytime.

---

## ✅ How to Contribute

1.  **Select a Group**: Choose based on your interest (UI -> Group A, Agents -> Group B).
2.  **Pick an Issue**: Comment on the GitHub issue to claim it.
3.  **Follow Architecture**: Remember to build these as API endpoints (Backend) or UI Components (Frontend) as defined in `EXPANSION_STRATEGY.md`.
