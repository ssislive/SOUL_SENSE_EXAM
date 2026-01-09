# app/models.py - SIMPLE WORKING VERSION
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Create Base
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    last_login = Column(String, nullable=True)

class Score(Base):
    __tablename__ = 'scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    total_score = Column(Integer)
    age = Column(Integer)
    timestamp = Column(String, default=lambda: datetime.utcnow().isoformat())

class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    entry_date = Column(String, default=lambda: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
    content = Column(Text)
    sentiment_score = Column(Float)
    emotional_patterns = Column(Text)

# Simple function to get session
def get_session():
    from app.db import get_session as get_db_session
    return get_db_session()

# Export everything
__all__ = ['Base', 'User', 'Score', 'JournalEntry', 'get_session']