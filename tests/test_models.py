from app.models import Base
from sqlalchemy import inspect
from app.db import get_engine

def test_schema_creation(temp_db):
    """
    Verify that tables are created by Base.metadata.create_all (called in fixture).
    """
    engine = get_engine()
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    assert "users" in tables
    assert "scores" in tables
    assert "responses" in tables
    assert "question_bank" in tables
    assert "journal_entries" in tables
