# Soul Sense Exam - Complete Modular Contributor Roadmap

This document contains **ALL planned issues** organized into safe, modular execution steps.
Every original issue # is preserved and mapped to a specific Step.

---

## 🌊 WAVE 1: Community Feedback System

**Goal:** Build the public feedback board.

### 🟢 Phase 1.1: Core UI & Submission

_Goal: Basic read/write functionality._

| Step      | Action                                               | Issues Solved                  |
| --------- | ---------------------------------------------------- | ------------------------------ |
| **1.1.1** | Create Feedback Board page layout (static mock)      | `Feedback #1`, `Feedback #13`  |
| **1.1.2** | Build Submission Form (Title, Category, Description) | `Feedback #2`, `Feedback #3`   |
| **1.1.3** | Connect form to database/storage                     | (Backend task)                 |
| **1.1.4** | Render feedback list from storage                    | `Feedback #14` (Filter/Search) |

### 🟡 Phase 1.2: Engagement Features

_Goal: Make it interactive._

| Step      | Action                                       | Issues Solved                 |
| --------- | -------------------------------------------- | ----------------------------- |
| **1.2.1** | Add Upvote button + sorting by votes         | `Feedback #4`, `Feedback #15` |
| **1.2.2** | Add Status badges (Open/In Progress/Shipped) | `Feedback #10`                |
| **1.2.3** | Create "Roadmap" view (filter by status)     | `Feedback #12`                |
| **1.2.4** | User notification system (when addressed)    | `Feedback #11`                |

### 🔴 Phase 1.3: GitHub & Moderation

_Goal: Admin tools and safety._

| Step      | Action                                           | Issues Solved  |
| --------- | ------------------------------------------------ | -------------- |
| **1.3.1** | Create GitHub Issue template for feedback        | `Feedback #16` |
| **1.3.2** | Script to auto-create GitHub Issue from feedback | `Feedback #5`  |
| **1.3.3** | GitHub Action to auto-label feedback issues      | `Feedback #17` |
| **1.3.4** | GitHub Action to close issues when PR merges     | `Feedback #18` |
| **1.3.5** | Write moderation guidelines document             | `Feedback #19` |
| **1.3.6** | Implement rate-limiting & abuse protection       | `Feedback #20` |

### 🟣 Phase 1.4: AI-Powered Feedback Analysis (Advanced)

_Goal: Smart feedback processing._

| Step      | Action                              | Issues Solved |
| --------- | ----------------------------------- | ------------- |
| **1.4.1** | Sentiment analysis on feedback text | `Feedback #6` |
| **1.4.2** | Duplicate detection using NLP       | `Feedback #7` |
| **1.4.3** | AI summarization of feedback themes | `Feedback #8` |
| **1.4.4** | Auto-suggest tags based on content  | `Feedback #9` |

---

## 🌊 WAVE 2: Profile Data Expansion

**Goal:** Collect comprehensive user context.

### 🟢 Phase 2.1: Lifestyle & Health Inputs

| Step      | Action                                      | Issues Solved |
| --------- | ------------------------------------------- | ------------- |
| **2.1.1** | Add "Support System" field (friends/family) | `Issue #26`   |
| **2.1.2** | Add "Relationship Stress" slider            | `Issue #27`   |
| **2.1.3** | Add "Social Interaction Frequency" dropdown | `Issue #28`   |
| **2.1.4** | Add "Exercise Frequency" input              | `Issue #29`   |
| **2.1.5** | Add "Dietary Patterns" dropdown             | `Issue #30`   |
| **2.1.6** | Add "Screen Time" work/entertainment split  | `Issue #31`   |

### 🟡 Phase 2.2: Goals & Vision

| Step      | Action                                      | Issues Solved |
| --------- | ------------------------------------------- | ------------- |
| **2.2.1** | Add "Short-Term Goals" text field           | `Issue #32`   |
| **2.2.2** | Add "Long-Term Vision" text field           | `Issue #33`   |
| **2.2.3** | Add "Biggest Current Challenge" open prompt | `Issue #34`   |
| **2.2.4** | Add "Primary Help Area" dropdown            | `Issue #35`   |

### 🔴 Phase 2.3: User Preferences & Calibration

| Step      | Action                                     | Issues Solved |
| --------- | ------------------------------------------ | ------------- |
| **2.3.1** | Add "Decision-Making Style" selector       | `Issue #36`   |
| **2.3.2** | Add "Risk Tolerance" slider                | `Issue #37`   |
| **2.3.3** | Add "Readiness for Change" scale           | `Issue #38`   |
| **2.3.4** | Add "Advice Frequency Preference" toggle   | `Issue #39`   |
| **2.3.5** | Add "Reminder Style" (Gentle/Motivational) | `Issue #40`   |
| **2.3.6** | Add "Advice Boundaries" multi-select       | `Issue #41`   |
| **2.3.7** | Add "AI Trust Level" slider                | `Issue #42`   |

### 🟣 Phase 2.4: Trust, Safety & UX

| Step      | Action                                  | Issues Solved |
| --------- | --------------------------------------- | ------------- |
| **2.4.1** | Implement Data Usage Consent modal      | `Issue #43`   |
| **2.4.2** | Add Emergency Disclaimer acceptance     | `Issue #44`   |
| **2.4.3** | Add Crisis Support preference toggle    | `Issue #45`   |
| **2.4.4** | Make all profile inputs editable        | `Issue #46`   |
| **2.4.5** | Implement progressive onboarding wizard | `Issue #47`   |

---

## 🌊 WAVE 3: Core AI Agent Architecture

**Goal:** Build the modular agent system.

### 🟢 Phase 3.1: Agent Framework Foundation

| Step      | Action                                        | Issues Solved |
| --------- | --------------------------------------------- | ------------- |
| **3.1.1** | Define base `Agent` class interface           | `Agent #1`    |
| **3.1.2** | Create Orchestration layer (agent sequencing) | `Agent #7`    |
| **3.1.3** | Implement structured logging for agents       | `Agent #10`   |
| **3.1.4** | Create REST API wrapper for agents            | `Agent #8`    |
| **3.1.5** | Implement Context Memory module               | `Agent #9`    |

### 🟡 Phase 3.2: Assessment & Insight Agents

| Step      | Action                                      | Issues Solved |
| --------- | ------------------------------------------- | ------------- |
| **3.2.1** | Build Assessment Agent (question selection) | `Agent #2`    |
| **3.2.2** | Build Insight Generator (scores to text)    | `Agent #3`    |
| **3.2.3** | Build Question Rephrasing Agent             | `Agent #6`    |
| **3.2.4** | Build Personalization Agent                 | `Agent #5`    |

### 🔴 Phase 3.3: Safety & Reliability

| Step      | Action                                      | Issues Solved |
| --------- | ------------------------------------------- | ------------- |
| **3.3.1** | Build Safety Guard Agent (crisis detection) | `Agent #4`    |
| **3.3.2** | Add Confidence Scoring to outputs           | `Agent #11`   |
| **3.3.3** | Build Human-in-the-Loop review queue        | `Agent #12`   |
| **3.3.4** | Add performance monitoring metrics          | `Agent #13`   |
| **3.3.5** | Build Fallback Agent (graceful degradation) | `Agent #14`   |
| **3.3.6** | Implement Privacy-Aware data filtering      | `Agent #15`   |

---

## 🌊 WAVE 4: Platform Expansion (Web/Mobile/API)

**Goal:** Launch cross-platform.

### 🟢 Phase 4.1: Backend API (FastAPI)

| Step      | Action                                   | Issues (NEW) |
| --------- | ---------------------------------------- | ------------ |
| **4.1.1** | Initialize FastAPI project structure     | `Tech #101`  |
| **4.1.2** | Setup PostgreSQL database connection     | `Tech #102`  |
| **4.1.3** | Implement JWT Authentication endpoints   | `Tech #103`  |
| **4.1.4** | Create Question/Assessment API endpoints | `Tech #104`  |
| **4.1.5** | Create Journaling API endpoints          | `Tech #105`  |
| **4.1.6** | Create User Profile API endpoints        | `Tech #106`  |

### 🟡 Phase 4.2: Web Client (Next.js)

| Step      | Action                          | Issues (NEW) |
| --------- | ------------------------------- | ------------ |
| **4.2.1** | Setup Next.js project with auth | `Tech #201`  |
| **4.2.2** | Build Login/Register pages      | `Tech #202`  |
| **4.2.3** | Build Dashboard component       | `Tech #203`  |
| **4.2.4** | Build Exam/Quiz wizard          | `Tech #204`  |
| **4.2.5** | Build Journaling page           | `Tech #205`  |
| **4.2.6** | Build Profile settings page     | `Tech #206`  |

### 🔴 Phase 4.3: Mobile Client (Flutter/React Native)

| Step      | Action                               | Issues (NEW) |
| --------- | ------------------------------------ | ------------ |
| **4.3.1** | Initialize mobile app structure      | `Tech #301`  |
| **4.3.2** | Implement auth flow (login/register) | `Tech #302`  |
| **4.3.3** | Build Quick Journal screen           | `Tech #303`  |
| **4.3.4** | Implement push notifications         | `Tech #304`  |
| **4.3.5** | Add offline caching                  | `Tech #305`  |

### 🟣 Phase 4.4: Windows Desktop Integration

| Step      | Action                               | Issues (NEW) |
| --------- | ------------------------------------ | ------------ |
| **4.4.1** | Create Sync Engine (local → cloud)   | `Tech #401`  |
| **4.4.2** | Implement hybrid offline/online mode | `Tech #402`  |

---

## 🌊 WAVE 5: AI Task Planner

**Goal:** Smart productivity assistant.

### 🟢 Phase 5.1: Core Planning Logic

| Step      | Action                                      | Issues Solved |
| --------- | ------------------------------------------- | ------------- |
| **5.1.1** | Build Task Planning Agent (goal → subtasks) | `Planner #1`  |
| **5.1.2** | Implement daily task suggestions            | `Planner #2`  |
| **5.1.3** | Add mood-aware task adjustment              | `Planner #3`  |
| **5.1.4** | Implement task priority classification      | `Planner #4`  |

### 🟡 Phase 5.2: User Interaction

| Step      | Action                                 | Issues Solved |
| --------- | -------------------------------------- | ------------- |
| **5.2.1** | Build gentle reminder/nudge system     | `Planner #5`  |
| **5.2.2** | Add task completion reflection prompts | `Planner #6`  |
| **5.2.3** | Implement burnout prevention detection | `Planner #7`  |

---

## 🌊 WAVE 6: Virtual Friend Chat

**Goal:** Empathetic conversation companion.

### 🟢 Phase 6.1: Conversation Core

| Step      | Action                                  | Issues Solved |
| --------- | --------------------------------------- | ------------- |
| **6.1.1** | Build Virtual Friend Conversation Agent | `VFriend #8`  |
| **6.1.2** | Implement Empathetic Response Engine    | `VFriend #9`  |
| **6.1.3** | Add Context-Aware Conversation Memory   | `VFriend #10` |
| **6.1.4** | Build Emotional Check-in Agent          | `VFriend #11` |

### 🟡 Phase 6.2: Safety & Customization

| Step      | Action                                   | Issues Solved |
| --------- | ---------------------------------------- | ------------- |
| **6.2.1** | Implement Boundary & Dependency Control  | `VFriend #12` |
| **6.2.2** | Add Crisis Detection & Safety Escalation | `VFriend #13` |
| **6.2.3** | Add Tone Customization options           | `VFriend #14` |
| **6.2.4** | Build Conversation-to-Insight Mapping    | `VFriend #15` |

---

## 🌊 WAVE 7: LLM Integration

**Goal:** Connect to Large Language Models.

### 🟢 Phase 7.1: LLM Gateway

| Step      | Action                                      | Issues Solved |
| --------- | ------------------------------------------- | ------------- |
| **7.1.1** | Build centralized LLM Integration Layer     | `LLM #1`      |
| **7.1.2** | Create Mental Health prompt templates       | `LLM #2`      |
| **7.1.3** | Define System Prompt for ethical boundaries | `LLM #3`      |
| **7.1.4** | Implement Context Window Management         | `LLM #4`      |
| **7.1.5** | Build User Intent Classification            | `LLM #5`      |

### 🟡 Phase 7.2: LLM Safety

| Step      | Action                                  | Issues Solved |
| --------- | --------------------------------------- | ------------- |
| **7.2.1** | Build LLM Output Safety Filter          | `LLM #6`      |
| **7.2.2** | Add Crisis Language Detection (pre-LLM) | `LLM #7`      |
| **7.2.3** | Add Confidence/Uncertainty annotation   | `LLM #8`      |

### 🔴 Phase 7.3: LLM Memory & Personalization

| Step      | Action                                     | Issues Solved |
| --------- | ------------------------------------------ | ------------- |
| **7.3.1** | Implement Short-Term Conversational Memory | `LLM #9`      |
| **7.3.2** | Build Long-Term Insight Summarization      | `LLM #10`     |
| **7.3.3** | Add LLM-Assisted Task Breakdown            | `LLM #11`     |
| **7.3.4** | Implement Mood-Aware Prompt Variants       | `LLM #12`     |

### 🟣 Phase 7.4: LLM Operations

| Step      | Action                                     | Issues Solved |
| --------- | ------------------------------------------ | ------------- |
| **7.4.1** | Define LLM Response Quality Metrics        | `LLM #13`     |
| **7.4.2** | Implement LLM Cost & Rate-Limit Management | `LLM #14`     |
| **7.4.3** | Build Model Switching & Fallback Strategy  | `LLM #15`     |

---

## 🌊 WAVE 8: MLOps & Scale

**Goal:** Professionalize the ML pipeline.

### 🟢 Phase 8.1: ML Pipeline Infrastructure

| Step      | Action                               | Issues Solved |
| --------- | ------------------------------------ | ------------- |
| **8.1.1** | Build Model Comparison Framework     | `ML #83`      |
| **8.1.2** | Implement Dataset Versioning         | `ML #91`      |
| **8.1.3** | Automate ML Pipeline (train/eval)    | `ML #92`      |
| **8.1.4** | Add Error Handling in data pipelines | `ML #95`      |
| **8.1.5** | Implement Experiment Logging         | `ML #96`      |

### 🟡 Phase 8.2: Data Privacy & Consent

| Step      | Action                                | Issues Solved |
| --------- | ------------------------------------- | ------------- |
| **8.2.1** | Implement Data Anonymization pipeline | `ML #85`      |
| **8.2.2** | Add Consent-based Data Usage flow     | `ML #86`      |

### 🔴 Phase 8.3: Analytics & Visualization

| Step      | Action                                      | Issues Solved |
| --------- | ------------------------------------------- | ------------- |
| **8.3.1** | Implement Risk Level Classification         | `ML #87`      |
| **8.3.2** | Build Recommendation Personalization Engine | `ML #88`      |
| **8.3.3** | Create Emotional Trends Visualization       | `ML #90`      |

### 🟣 Phase 8.4: Deployment & Documentation

| Step      | Action                                | Issues Solved |
| --------- | ------------------------------------- | ------------- |
| **8.4.1** | Optimize ML Model Performance         | `ML #94`      |
| **8.4.2** | Define Model Deployment Strategy      | `ML #97`      |
| **8.4.3** | Write Research-oriented Documentation | `ML #98`      |
| **8.4.4** | Complete Scalability Planning         | `ML #99`      |
| **8.4.5** | Finalize AI-driven Roadmap document   | `ML #100`     |

---

## ✅ Issue Checklist Summary

| Category   | Issue Range | Total   |
| ---------- | ----------- | ------- |
| Feedback   | #1-20       | 20      |
| Profile    | #26-47      | 22      |
| Agent      | #1-15       | 15      |
| Planner    | #1-7        | 7       |
| VFriend    | #8-15       | 8       |
| LLM        | #1-15       | 15      |
| ML         | #83-100     | 18      |
| Tech (NEW) | #101-402    | 18      |
| **TOTAL**  |             | **123** |

---

## 📋 How to Contribute

1.  **Find an Open Wave** on GitHub (start with Wave 1).
2.  **Pick a Step** from that Wave's Phase.
3.  **Comment** on the corresponding Issue to claim it.
4.  **Submit a PR** for that specific Step only.
