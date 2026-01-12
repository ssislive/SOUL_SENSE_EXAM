import time
import statistics
import logging
from datetime import datetime
from typing import List, Tuple, Optional, Any
from app.db import get_connection
from app.models import Score
from app.exceptions import DatabaseError

# Try importing NLTK sentiment analyzer
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
except ImportError:
    SentimentIntensityAnalyzer = None

logger = logging.getLogger(__name__)

class ExamSession:
    """
    Core engine for the Exam functionality.
    Manages state, timing, scoring, and persistence.
    Decoupled from any specific UI (Tkinter/CLI).
    """

    def __init__(self, username: str, age: int, age_group: str, questions: List[Tuple]):
        self.username = username
        self.age = age
        self.age_group = age_group
        self.questions = questions  # List of (id, text, tooltip, min_age, max_age) or (text, tooltip)
        
        # State
        self.current_question_index = 0
        self.responses: List[int] = []
        self.response_times: List[float] = []
        
        # Timing
        self.question_start_time: Optional[float] = None
        
        # Results
        self.score = 0
        self.sentiment_score = 0.0
        self.reflection_text = ""
        self.is_rushed = False
        self.is_inconsistent = False

    def start_exam(self):
        """Initialize or reset exam state"""
        self.current_question_index = 0
        self.responses = []
        self.response_times = []
        self.score = 0
        self.sentiment_score = 0.0
        self.reflection_text = ""
        self.start_question_timer()
        logger.info(f"Exam session started for user: {self.username}")

    def start_question_timer(self):
        """Mark the start time for the current question"""
        self.question_start_time = time.time()

    def get_current_question(self) -> Optional[Tuple[str, Optional[str]]]:
        """
        Return (text, tooltip) for the current question 
        or None if exam is finished.
        """
        if self.current_question_index >= len(self.questions):
            return None
            
        q_data = self.questions[self.current_question_index]
        
        # Handle different question tuple formats (id from DB vs raw text)
        # Format 1: (id, text, tooltip, min, max) -> DB
        # Format 2: (text, tooltip) -> Legacy/Simple
        
        if len(q_data) >= 3 and isinstance(q_data[0], int):
             # DB Format: id is 0, text is 1, tooltip is 2
             return (q_data[1], q_data[2])
        elif isinstance(q_data, tuple):
            return (q_data[0], q_data[1] if len(q_data) > 1 else None)
        else:
            return (str(q_data), None)

    def submit_answer(self, value: int):
        """
        Submit answer for current question and advance.
        Value should be 1-4.
        """
        if not (1 <= value <= 4):
            raise ValueError("Answer must be between 1 and 4")

        # Record metrics
        duration = 0.0
        if self.question_start_time:
            duration = time.time() - self.question_start_time
        
        # Store data
        # Handle overwriting if user went back
        if self.current_question_index < len(self.responses):
            self.responses[self.current_question_index] = value
            self.response_times[self.current_question_index] = duration
        else:
            self.responses.append(value)
            self.response_times.append(duration)
            
        # Optional: Save individual response to DB here if real-time persistence is needed
        # For simplicity, we save strict data at the end, but could add it here.
        self._save_response_to_db(value)

        # Advance
        self.current_question_index += 1
        self.start_question_timer()

    def go_back(self):
        """Return to previous question"""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.start_question_timer() # Reset timer for the re-visited question
            return True
        return False

    def get_progress(self) -> Tuple[int, int, float]:
        """Return (current, total, percentage)"""
        total = len(self.questions)
        pct = (self.current_question_index / total * 100) if total > 0 else 0
        return (self.current_question_index + 1, total, pct)

    def is_finished(self) -> bool:
        """Check if all questions are answered"""
        return self.current_question_index >= len(self.questions)

    def submit_reflection(self, text: str, analyzer: Any = None):
        """
        Analyze reflection text sentiment.
        Accepts an external analyzer instance (dependency injection) or tries to load default.
        """
        self.reflection_text = text.strip()
        
        if not self.reflection_text:
            self.sentiment_score = 0.0
            return

        try:
            # Use provided analyzer or default
            sia = analyzer
            if not sia and SentimentIntensityAnalyzer:
                sia = SentimentIntensityAnalyzer()
            
            if sia:
                scores = sia.polarity_scores(self.reflection_text)
                self.sentiment_score = scores['compound'] * 100
            else:
                self.sentiment_score = 0.0
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            self.sentiment_score = 0.0

    def calculate_metrics(self):
        """Calculate score and quality metrics (rushed, inconsistent)"""
        self.score = sum(self.responses)
        self.is_rushed = False
        self.is_inconsistent = False

        # 1. Rushed Detection
        if self.response_times:
            avg_time = statistics.mean(self.response_times)
            if avg_time < 2.0:
                self.is_rushed = True

        # 2. Inconsistent Detection (Internal Variance)
        if len(self.responses) > 1:
            variance = statistics.variance(self.responses)
            if variance > 2.0:
                self.is_inconsistent = True

        # 3. Inconsistent (Historical) - Requires DB access
        # For pure service, we might skip this or inject DB dependency.
        # We'll implement a simple DB check here using our existing db module.
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT total_score FROM scores WHERE username = ? ORDER BY timestamp DESC LIMIT 10", 
                (self.username,)
            )
            past_scores = [row[0] for row in cursor.fetchall()]
            if past_scores:
                avg_past = statistics.mean(past_scores)
                if avg_past > 0 and abs(self.score - avg_past) / avg_past > 0.2:
                    self.is_inconsistent = True
        except Exception as e:
            logger.warning(f"Could not check historical consistency: {e}")

    def finish_exam(self) -> bool:
        """Finalize exam, calculate scores, and save to DB."""
        self.calculate_metrics()
        
        timestamp = datetime.utcnow().isoformat()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO scores 
                (username, age, total_score, sentiment_score, reflection_text, 
                 is_rushed, is_inconsistent, timestamp, detailed_age_group) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (self.username, self.age, self.score, self.sentiment_score, 
                 self.reflection_text, self.is_rushed, self.is_inconsistent, 
                 timestamp, self.age_group)
            )
            conn.commit()
            logger.info(f"Exam saved. Score: {self.score}, Sentiment: {self.sentiment_score}")
            return True
        except Exception as e:
            logger.error(f"Failed to save exam results: {e}", exc_info=True)
            return False

    def _save_response_to_db(self, answer_value: int):
        """Helper to save single response"""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Map index to correct ID if possible
            q_data = self.questions[self.current_question_index]
            q_id = q_data[0] if (isinstance(q_data, tuple) and isinstance(q_data[0], int)) else (self.current_question_index + 1)
            
            cursor.execute(
                """
                INSERT INTO responses
                (username, question_id, response_value, age_group, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.username, q_id, answer_value, self.age_group, datetime.utcnow().isoformat())
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save response: {e}")
