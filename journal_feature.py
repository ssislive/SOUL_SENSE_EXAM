# journal_feature.py - Fix the imports at the top
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import sqlite3
from sqlalchemy import desc

# Change this import line:
# from app.models import JournalEntry
# to:
try:
    from app.models import JournalEntry
except ImportError:
    # Fallback to direct SQLite
    JournalEntry = None

class JournalFeature:
    def __init__(self, parent_root):
        self.parent_root = parent_root
        # Database setup is handled efficiently by app.db.check_db_state or migration
        
    def open_journal_window(self, username):
        """Open the journal window"""
        self.username = username
        self.journal_window = tk.Toplevel(self.parent_root)
        self.journal_window.title("Emotional Journal")
        self.journal_window.geometry("600x500")
        
        # Title
        tk.Label(self.journal_window, text="Daily Emotional Reflection", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Date display
        today = datetime.now().strftime("%Y-%m-%d")
        tk.Label(self.journal_window, text=f"Date: {today}", 
                font=("Arial", 12)).pack(pady=5)
        
        # Text area for journal entry
        tk.Label(self.journal_window, text="Write your emotional reflection:", 
                font=("Arial", 12)).pack(pady=(10,5))
        
        self.text_area = scrolledtext.ScrolledText(self.journal_window, 
                                                  width=70, height=15, 
                                                  font=("Arial", 11))
        self.text_area.pack(pady=10, padx=20)
        
        # Buttons
        button_frame = tk.Frame(self.journal_window)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Save & Analyze", 
                 command=self.save_and_analyze, 
                 font=("Arial", 12), bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="View Past Entries", 
                 command=self.view_past_entries, 
                 font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="📊 Dashboard", 
                 command=self.open_dashboard, 
                 font=("Arial", 12), bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Close", 
                 command=self.journal_window.destroy, 
                 font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
    
    def analyze_sentiment(self, text):
        """Simple sentiment analysis based on emotional keywords"""
        positive_words = ['happy', 'joy', 'excited', 'grateful', 'peaceful', 'confident', 
                         'proud', 'hopeful', 'content', 'satisfied', 'calm', 'relaxed']
        negative_words = ['sad', 'angry', 'frustrated', 'anxious', 'worried', 'stressed', 
                         'disappointed', 'upset', 'overwhelmed', 'depressed', 'fear', 'lonely']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
            
        sentiment_score = (positive_count - negative_count) / max(total_words, 1) * 100
        return max(-100, min(100, sentiment_score))
    
    def extract_emotional_patterns(self, text):
        """Extract emotional patterns from text"""
        patterns = []
        text_lower = text.lower()
        
        # Stress indicators
        stress_words = ['stress', 'pressure', 'overwhelm', 'burden', 'exhausted']
        if any(word in text_lower for word in stress_words):
            patterns.append("Stress indicators detected")
        
        # Relationship mentions
        relationship_words = ['friend', 'family', 'colleague', 'partner', 'relationship']
        if any(word in text_lower for word in relationship_words):
            patterns.append("Social/relationship focus")
        
        # Growth mindset
        growth_words = ['learn', 'grow', 'improve', 'better', 'progress', 'develop']
        if any(word in text_lower for word in growth_words):
            patterns.append("Growth-oriented thinking")
        
        # Self-reflection
        reflection_words = ['realize', 'understand', 'reflect', 'think', 'feel', 'notice']
        if any(word in text_lower for word in reflection_words):
            patterns.append("Self-reflective content")
        
        return "; ".join(patterns) if patterns else "General emotional expression"
    
    def save_and_analyze(self):
        """Save journal entry and perform AI analysis"""
        content = self.text_area.get("1.0", tk.END).strip()
        
        if not content:
            messagebox.showwarning("Empty Entry", "Please write something before saving.")
            return
        
        if len(content) < 10:
            messagebox.showwarning("Too Short", "Please write at least 10 characters for meaningful analysis.")
            return
        
        # Perform analysis
        sentiment_score = self.analyze_sentiment(content)
        emotional_patterns = self.extract_emotional_patterns(content)
        
        # Save to database
        session = get_session()
        try:
            entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = JournalEntry(
                username=self.username,
                entry_date=entry_date,
                content=content,
                sentiment_score=sentiment_score,
                emotional_patterns=emotional_patterns
            )
            session.add(entry)
            session.commit()
            
            # Show analysis results
            self.show_analysis_results(sentiment_score, emotional_patterns)
            
            # Clear text area
            self.text_area.delete("1.0", tk.END)
            
        except Exception as e:
            logging.error("Failed to save journal entry", exc_info=True)
            messagebox.showerror("Error", f"Failed to save entry: {e}")
            session.rollback()
        finally:
            session.close()
    
    def show_analysis_results(self, sentiment_score, patterns):
        """Display AI analysis results"""
        result_window = tk.Toplevel(self.journal_window)
        result_window.title("AI Analysis Results")
        result_window.geometry("400x300")
        
        tk.Label(result_window, text="Emotional Analysis", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Sentiment interpretation
        if sentiment_score > 20:
            sentiment_text = "Positive emotional tone detected"
            color = "green"
        elif sentiment_score < -20:
            sentiment_text = "Negative emotional tone detected"
            color = "red"
        else:
            sentiment_text = "Neutral emotional tone"
            color = "blue"
        
        tk.Label(result_window, text=f"Sentiment Score: {sentiment_score:.1f}", 
                font=("Arial", 12)).pack(pady=5)
        tk.Label(result_window, text=sentiment_text, 
                font=("Arial", 12), fg=color).pack(pady=5)
        
        tk.Label(result_window, text="Emotional Patterns:", 
                font=("Arial", 12, "bold")).pack(pady=(15,5))
        tk.Label(result_window, text=patterns, 
                font=("Arial", 11), wraplength=350).pack(pady=5)
        
        tk.Button(result_window, text="Close", 
                 command=result_window.destroy, 
                 font=("Arial", 12)).pack(pady=20)
    
    def view_past_entries(self):
        """View past journal entries"""
        entries_window = tk.Toplevel(self.journal_window)
        entries_window.title("Past Journal Entries")
        entries_window.geometry("700x500")
        
        tk.Label(entries_window, text="Your Emotional Journey", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Create scrollable text area
        text_area = scrolledtext.ScrolledText(entries_window, width=80, height=25, 
                                            font=("Arial", 10))
        text_area.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Fetch entries from database with ORM
        session = get_session()
        try:
            entries = session.query(JournalEntry)\
                .filter_by(username=self.username)\
                .order_by(desc(JournalEntry.entry_date))\
                .all()
            
            if not entries:
                text_area.insert(tk.END, "No journal entries found. Start writing to track your emotional journey!")
            else:
                for entry in entries:
                    text_area.insert(tk.END, f"Date: {entry.entry_date}\n")
                    text_area.insert(tk.END, f"Sentiment: {entry.sentiment_score:.1f} | Patterns: {entry.emotional_patterns}\n")
                    text_area.insert(tk.END, f"Entry: {entry.content}\n")
                    text_area.insert(tk.END, "-" * 70 + "\n\n")
        finally:
            session.close()
        
        text_area.config(state=tk.DISABLED)
        
        tk.Button(entries_window, text="Close", 
                 command=entries_window.destroy, 
                 font=("Arial", 12)).pack(pady=10)
    
    def open_dashboard(self):
        """Open analytics dashboard"""
        dashboard = AnalyticsDashboard(self.journal_window, self.username)
        dashboard.open_dashboard()