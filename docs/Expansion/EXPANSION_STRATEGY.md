# Soul Sense Exam - Multi-Platform Expansion Strategy

## 🚀 Overview & Vision

This document outlines the technical strategy to expand "Soul Sense Exam" from a local Windows application to a **cross-platform ecosystem** (Windows, Web, Mobile).

To achieve this, we must transition from a **Monolithic Desktop App** (Logic + UI mixed) to a **Client-Server Architecture**.

### 🏗️ The New Architecture

1.  **Backend (The Core)**: A central API (FastAPI) handling Database, AI Logic, and Auth.
2.  **Database**: Migrate from local `SQLite` to `PostgreSQL` (Cloud-ready).
3.  **Clients**:
    - **Windows**: The existing Tkinter app (Refactored to sync with API).
    - **Web**: A modern React/Next.js dashboard.
    - **Mobile**: A React Native or Flutter app for daily journaling on the go.

---

## 📦 Group 1: The Foundation - API & Decoupling

**Goal:** Extract business logic from the Tkinter UI into a standalone API service.
**Priority:** High (Prerequisite for Web/Mobile).

### 1.1: Initialize Backend Project

- [ ] **Create `backend/` Directory**: Setup a FastAPI project structure.
- [ ] **Docker Setup**: Create `Dockerfile` and `docker-compose.yml` for the API and Postgres.
- [ ] **Dependency Management**: Define `requirements-backend.txt` (FastAPI, Pydantic, SQLAlchemy).

### 1.2: Database Migration (SQLite → PostgreSQL)

- [ ] **Schema Porting**: Convert existing SQLAlchemy models (`User`, `Score`, `Journal`) to work with Postgres.
- [ ] **Migration Script**: Create a script to export data from local `soulsense.db` to the new Postgres instance.
- [ ] **Connection Manager**: Update `db.py` to read connection strings from `.env` (support both SQLite for local dev and Postgres for prod).

### 1.3: Authentication API

- [ ] **JWT Implementation**: Implement OAuth2 with Password Flow (Access + Refresh Tokens).
- [ ] **Endpoints**: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`.
- [ ] **Security**: Hash passwords using `bcrypt` (already used, just move logic to API).

### 1.4: Assessment & Journal API

- [ ] **Endpoints**:
  - `GET /questions`: Fetch active questions.
  - `POST /submit-test`: Submit exam answers and calculate score.
  - `POST /journal`: Create a daily log.
  - `GET /history`: Fetch past scores/journals.

---

## 🌐 Group 2: The Web Client (Browser Expansion)

**Goal:** Provide a zero-installation accessible version of Soul Sense.
**Stack:** React (Next.js) + TailwindCSS.

### 2.1: Web Project Setup

- [ ] **Initialize Frontend**: Create `frontend-web/` using Next.js.
- [ ] **UI Component Library**: Install Shadcn/UI or TailwindUI for rapid development.
- [ ] **API Client**: Setup `axios` or `fetch` wrapper with Auth header injection.

### 2.2: Core Pages

- [ ] **Landing & Auth**: Login / Register pages connected to API.
- [ ] **Dashboard**: Re-create the Tkinter "Dashboard" using `Recharts` (Web charts).
- [ ] **Journaling**: Web form for daily entry sliders.

### 2.3: The Web Exam

- [ ] **Exam Interface**: A step-by-step wizard for answering questions.
- [ ] **Results Page**: Beautiful CSS-based visualizations of the result.

---

## 📱 Group 3: The Mobile Client (On-The-Go)

**Goal:** Enable quick journaling and notifications.
**Stack:** React Native (sharing logic with Web) OR Flutter.

### 3.1: Mobile Project Setup

- [ ] **Initialize App**: Create `mobile-app/`.
- [ ] **Navigation**: Setup Stack/Tab navigation (Home, Journal, Profile).

### 3.2: Mobile Features

- [ ] **Daily Nudge**: Local Notifications to remind users to journal.
- [ ] **Quick Journal**: Optimized touch interface for sliders (Sleep, Energy).
- [ ] **Offline Mode**: Cache journal entries locally and sync when online.

---

## 🖥️ Group 4: Windows Client Refactoring

**Goal:** Keep the desktop app alive but integrated.

### 4.1: Cloud Sync

- [ ] **Sync Engine**: Add a "Sync" button to push local SQLite data to the Cloud API.
- [ ] **Hybrid Mode**: Allow the app to work offline (SQLite) and sync when connected.

---

## 🤖 Group 5: AI & Scalability (The Future)

**Goal:** Move AI processing to the cloud for heavy lifting.

### 5.1: AI Microservice

- [ ] **Agent API**: Expose specific endpoints for different agents (e.g., `POST /api/agent/assessment`).
- [ ] **Task Planner**: Move the "Smart Task Breakdown" logic to the server.
- [ ] **LLM Gateway**: Centralized API route to manage OpenAI/Gemini costs and keys secure on the server, not the client.

---

## ✅ Contributors Guide to Picking Issues

1.  **Pick a Group**: Decide if you are Backend (Group 1), Frontend (Group 2), or Mobile (Group 3).
2.  **Check Dependencies**: Group 1 must be stable before Groups 2 & 3 can fully function.
3.  **Modular PRs**: Submit small PRs (e.g., "Add Login Endpoint" instead of "Build entire API").
