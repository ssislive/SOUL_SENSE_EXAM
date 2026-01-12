from app.db import get_session
from sqlalchemy import text

def test_db_session(temp_db):
    session = get_session()
    result = session.execute(text("SELECT 1"))
    assert result.scalar() == 1
    session.close()
