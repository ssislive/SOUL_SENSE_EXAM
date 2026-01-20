# Test Fixtures Documentation

This document describes the reusable test fixtures available for SOUL_SENSE_EXAM testing.

## Overview

The test fixtures are organized into two main files:
- `tests/conftest.py` - Core pytest fixtures (database isolation, UI mocks)
- `tests/fixtures.py` - Factory classes and specialized fixtures for database entities and ML components

## Quick Start

### Using Fixtures in Tests

Fixtures are automatically available to all test functions:

```python
def test_user_creation(temp_db, sample_user):
    """temp_db provides isolated database, sample_user creates a test user."""
    assert sample_user.username.startswith("test_user")
    assert temp_db.query(User).count() == 1
```

### Using Factories Directly

For more control, import factory classes:

```python
from tests.fixtures import UserFactory, ScoreFactory

def test_custom_user(temp_db):
    user = UserFactory.create(temp_db, username="custom_name")
    scores = ScoreFactory.create_batch(temp_db, user, count=5)
    assert len(scores) == 5
```

---

## Database Fixtures

### Core Fixtures (conftest.py)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `temp_db` | function | In-memory SQLite database, patched into app.db module |
| `mock_tk_root` | session | Mocks Tkinter root for CI environments |
| `mock_tk_variables` | function | Mocks StringVar/IntVar/BooleanVar |
| `mock_app` | function | Mock SoulSenseApp controller |

### Entity Fixtures (fixtures.py)

| Fixture | Dependencies | Description |
|---------|--------------|-------------|
| `sample_user` | temp_db | Creates a basic User record |
| `sample_user_with_profiles` | temp_db | User with all profile types attached |
| `sample_score` | temp_db, sample_user | Single Score record |
| `sample_scores_batch` | temp_db, sample_user | 10 Score records |
| `sample_responses` | temp_db, sample_user | 10 Response records |
| `sample_journal_entry` | temp_db, sample_user | JournalEntry record |
| `sample_question_bank` | temp_db | 20 Question records |

### Utility Fixtures

| Fixture | Description |
|---------|-------------|
| `isolated_db` | Standalone in-memory DB without patching |
| `populated_db` | Pre-populated DB with 3 users, scores, responses |

---

## Factory Classes

### UserFactory

Creates test User instances with optional associated profiles.

```python
from tests.fixtures import UserFactory

# Basic user
user = UserFactory.create(session)

# User with all profiles
user = UserFactory.create_with_profiles(
    session,
    username="test_user",
    include_medical=True,
    include_personal=True,
    include_strengths=True,
    include_emotional=True
)
```

### ScoreFactory

Creates Score records with realistic data.

```python
from tests.fixtures import ScoreFactory

# Single score
score = ScoreFactory.create(session, user=user, total_score=85)

# Batch of scores over 30 days
scores = ScoreFactory.create_batch(
    session, 
    user, 
    count=10, 
    score_range=(50, 100),
    days_span=30
)
```

### ResponseFactory

Creates Response records simulating assessment answers.

```python
from tests.fixtures import ResponseFactory

# Single response
response = ResponseFactory.create(session, user=user, question_id=1, response_value=4)

# Complete assessment simulation
responses = ResponseFactory.create_batch(
    session,
    user,
    question_count=20,
    response_pattern="varied"  # or "consistent_high", "consistent_low", "random"
)
```

### JournalEntryFactory

Creates JournalEntry records with realistic content.

```python
from tests.fixtures import JournalEntryFactory

entry = JournalEntryFactory.create(
    session,
    username="test_user",
    content="Today was productive...",
    sentiment_score=0.7,
    sleep_hours=7.5,
    stress_level=3
)
```

### QuestionFactory

Creates Question records for the question bank.

```python
from tests.fixtures import QuestionFactory

# Single question
question = QuestionFactory.create(session, question_text="How do you feel?")

# Full question bank
questions = QuestionFactory.create_question_bank(session, count=20)
```

---

## ML Fixtures

### Feature Data Fixtures

| Fixture | Description |
|---------|-------------|
| `sample_user_features` | DataFrame with 50 users of random features |
| `sample_clustered_features` | DataFrame with clear cluster separation |

### FeatureDataFactory

Creates feature datasets for ML testing.

```python
from tests.fixtures import FeatureDataFactory

# Random features
df = FeatureDataFactory.create_user_features(n_users=100)

# Features with clear clusters
df = FeatureDataFactory.create_clustered_features(
    n_users_per_cluster=20,
    n_clusters=4
)
```

### Mock ML Component Fixtures

| Fixture | Description |
|---------|-------------|
| `mock_score` | Mock Score object for ML functions |
| `mock_response` | Mock Response object for ML functions |
| `mock_clusterer` | Pre-configured mock EmotionalProfileClusterer |
| `mock_feature_extractor` | Pre-configured mock EmotionalFeatureExtractor |
| `mock_risk_predictor` | Pre-configured mock RiskPredictor |

### MockMLComponents

Creates mock ML components with predictable behavior.

```python
from tests.fixtures import MockMLComponents

# Mock clusterer that returns predictable results
clusterer = MockMLComponents.create_mock_clusterer(n_clusters=4)
result = clusterer.predict("user")
assert result['cluster_id'] == 0

# Mock risk predictor
predictor = MockMLComponents.create_mock_risk_predictor()
result = predictor.predict_with_explanation(...)
assert result['prediction_label'] == 'Low Risk'
```

---

## Sample Data Constants

The fixtures module provides sample data constants for consistent test data:

```python
from tests.fixtures import (
    SAMPLE_EMOTIONS,      # ["Anxiety", "Stress", "Calmness", ...]
    SAMPLE_TRIGGERS,      # ["Work deadlines", "Social situations", ...]
    SAMPLE_COPING,        # ["Deep breathing", "Exercise", ...]
    SAMPLE_SUPPORT_STYLES,# ["Encouraging & Motivating", ...]
    SAMPLE_STRENGTHS,     # ["Empathy", "Creativity", ...]
    SAMPLE_BLOOD_TYPES,   # ["A+", "A-", "B+", ...]
    SAMPLE_OCCUPATIONS,   # ["Student", "Engineer", ...]
)
```

---

## Best Practices

### 1. Use `temp_db` for Database Isolation

Always use the `temp_db` fixture for tests that interact with the database:

```python
def test_database_operation(temp_db):
    # temp_db is already an open session
    # All changes are isolated and cleaned up after the test
    pass
```

### 2. Prefer Factories for Custom Data

When you need specific configurations, use factories:

```python
def test_high_scorer(temp_db):
    user = UserFactory.create(temp_db)
    ScoreFactory.create(temp_db, user=user, total_score=95)
```

### 3. Use Mock Components for Unit Tests

For unit tests of ML components, use mocks to avoid database dependencies:

```python
def test_clustering_logic(mock_clusterer, sample_user_features):
    result = mock_clusterer.fit(data=sample_user_features)
    assert 'error' not in result
```

### 4. Reset Factory Counters Between Test Modules

If username uniqueness matters across modules:

```python
@pytest.fixture(autouse=True)
def reset_factories():
    UserFactory.reset_counter()
    yield
```

---

## Migration from Local Fixtures

If your tests define local fixtures that duplicate functionality from this module,
consider migrating to use the shared fixtures:

### Before (local fixture)
```python
@pytest.fixture
def temp_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

### After (using shared fixtures)
```python
# Just use the fixture - it's automatically available!
def test_something(temp_db):
    # temp_db is provided by conftest.py
    pass
```

For tests that need complete isolation from the patching behavior of `temp_db`,
use `isolated_db` instead.
