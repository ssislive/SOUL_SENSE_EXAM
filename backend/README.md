# Backend API (Wave 4)

This directory will contain the FastAPI backend.

## Getting Started (Future)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Structure

```
backend/
├── main.py          # FastAPI entry point
├── auth/            # JWT authentication
├── api/             # API routes
├── core/            # Database, config, schemas
├── agents/          # AI Agents (Wave 3)
└── llm/             # LLM Integration (Wave 7)
```

See `FILE_ARCHITECTURE.md` for detailed file mappings.
