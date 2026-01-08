import tkinter as tk
from tkinter import ttk
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates

class AnalyticsDashboard:
    def __init__(self, parent_root, username):
        self.parent_root = parent_root
        self.username = username
        
    def open_dashboard(self):
        """Open analytics dashboard"""
        dashboard = tk.Toplevel(self.parent_root)
        dashboard.title("📊 Emotional Health Dashboard")
        dashboard.geometry("600x500")
        
        tk.Label(dashboard, text="📊 Emotional Health Analytics", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        notebook = ttk.Notebook(dashboard)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # EQ Trends
        eq_frame = ttk.Frame(notebook)
        notebook.add(eq_frame, text="EQ Trends")
        self.show_eq_trends(eq_frame)
        
        # Journal Analytics
        journal_frame = ttk.Frame(notebook)
        notebook.add(journal_frame, text="Journal Analytics")
        self.show_journal_analytics(journal_frame)
        
        # Insights
        insights_frame = ttk.Frame(notebook)
        notebook.add(insights_frame, text="Insights")
        self.show_insights(insights_frame)
        
    def show_eq_trends(self, parent):
        """Show EQ score trends with matplotlib graph"""
        conn = sqlite3.connect("soulsense_db")
        cursor = conn.cursor()
        cursor.execute("""
        SELECT total_score, timestamp, id 
        FROM scores 
        WHERE username = ? 
        ORDER BY id
        """, (self.username,))
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            tk.Label(parent, text="No EQ data available", font=("Arial", 14)).pack(pady=50)
            return
        
        scores = [row[0] for row in data]
        timestamps = []
        
        # Parse timestamps, handle missing ones
        for i, row in enumerate(data):
            if row[1]:
                try:
                    timestamps.append(datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"))
                except:
                    timestamps.append(datetime.now())
            else:
                timestamps.append(datetime.now())
        
        tk.Label(parent, text="📈 EQ Score Progress Over Time", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(parent, bg="#f0f0f0", relief=tk.RIDGE, bd=2)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create two columns for stats
        left_col = tk.Frame(stats_frame, bg="#f0f0f0")
        left_col.pack(side=tk.LEFT, padx=20, pady=10)
        
        right_col = tk.Frame(stats_frame, bg="#f0f0f0")
        right_col.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(left_col, text=f"Total Attempts: {len(scores)}", 
                font=("Arial", 11, "bold"), bg="#f0f0f0").pack(anchor="w", pady=2)
        tk.Label(left_col, text=f"Latest Score: {scores[-1]}", 
                font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=2)
        tk.Label(left_col, text=f"Best Score: {max(scores)}", 
                font=("Arial", 11), bg="#f0f0f0", fg="green").pack(anchor="w", pady=2)
        
        tk.Label(right_col, text=f"First Score: {scores[0]}", 
                font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=2)
        tk.Label(right_col, text=f"Average Score: {sum(scores)/len(scores):.1f}", 
                font=("Arial", 11), bg="#f0f0f0").pack(anchor="w", pady=2)
        
        if len(scores) > 1:
            improvement = scores[-1] - scores[0]
            improvement_pct = (improvement / scores[0]) * 100
            color = "green" if improvement > 0 else "red" if improvement < 0 else "blue"
            symbol = "↑" if improvement > 0 else "↓" if improvement < 0 else "→"
            tk.Label(right_col, text=f"Progress: {symbol} {improvement:+d} ({improvement_pct:+.1f}%)", 
                    font=("Arial", 11, "bold"), bg="#f0f0f0", fg=color).pack(anchor="w", pady=2)
        
        # Create matplotlib figure
        fig = Figure(figsize=(6, 4), dpi=80)
        ax = fig.add_subplot(111)
        
        # Plot line graph
        ax.plot(range(1, len(scores) + 1), scores, 
               marker='o', linestyle='-', linewidth=2, markersize=8,
               color='#4CAF50', markerfacecolor='#2196F3', 
               markeredgewidth=2, markeredgecolor='#1976D2')
        
        # Fill area under line
        ax.fill_between(range(1, len(scores) + 1), scores, alpha=0.3, color='#4CAF50')
        
        # Formatting
        ax.set_xlabel('Attempt Number', fontsize=11, fontweight='bold')
        ax.set_ylabel('EQ Score', fontsize=11, fontweight='bold')
        ax.set_title('Your EQ Progress Journey', fontsize=12, fontweight='bold', pad=15)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xticks(range(1, len(scores) + 1))
        
        # Add value labels on points
        for i, score in enumerate(scores):
            ax.annotate(str(score), 
                       xy=(i + 1, score), 
                       xytext=(0, 10),
                       textcoords='offset points',
                       ha='center',
                       fontsize=9,
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Add trend analysis
        if len(scores) >= 3:
            trend_frame = tk.Frame(parent, bg="#e3f2fd", relief=tk.RIDGE, bd=2)
            trend_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(trend_frame, text="📊 Trend Analysis", 
                    font=("Arial", 11, "bold"), bg="#e3f2fd").pack(pady=5)
            
            recent_trend = sum(scores[-3:]) / 3 - sum(scores[:3]) / 3
            if recent_trend > 5:
                trend_msg = "🎉 Strong upward trend! You're making excellent progress!"
            elif recent_trend > 0:
                trend_msg = "📈 Positive trend! Keep up the good work!"
            elif recent_trend < -5:
                trend_msg = "💪 Scores declining. Focus on emotional awareness practices."
            elif recent_trend < 0:
                trend_msg = "📉 Slight decline. Consider reviewing past strategies."
            else:
                trend_msg = "⚖️ Stable scores. Ready for the next breakthrough!"
            
            tk.Label(trend_frame, text=trend_msg, 
                    font=("Arial", 10), bg="#e3f2fd", wraplength=500).pack(pady=5)
        
    def show_journal_analytics(self, parent):
        """Show journal analytics"""
        session = get_session()
        try:
            rows = session.query(JournalEntry.sentiment_score, JournalEntry.emotional_patterns)\
                .filter_by(username=self.username)\
                .all()
        finally:
            session.close()
        
        if not rows:
            tk.Label(parent, text="No journal data available", font=("Arial", 14)).pack(pady=50)
            return
            
        tk.Label(parent, text="📝 Journal Analytics", font=("Arial", 14, "bold")).pack(pady=10)
        
        sentiments = [r[0] for r in rows]
        
        # Stats
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(stats_frame, text=f"Total Entries: {len(rows)}", font=("Arial", 12)).pack(anchor="w")
        tk.Label(stats_frame, text=f"Avg Sentiment: {sum(sentiments)/len(sentiments):.1f}", 
                font=("Arial", 12)).pack(anchor="w")
        tk.Label(stats_frame, text=f"Most Positive: {max(sentiments):.1f}", 
                font=("Arial", 12)).pack(anchor="w")
        
        # Patterns
        patterns_frame = tk.Frame(parent)
        patterns_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(patterns_frame, text="Top Emotional Patterns:", 
                font=("Arial", 12, "bold")).pack(anchor="w")
        
        all_patterns = []
        for r in rows:
            if r[1]: # emotional_patterns
                all_patterns.extend(r[1].split('; '))
        
        pattern_counts = Counter(all_patterns)
        
        patterns_text = tk.Text(patterns_frame, height=6, font=("Arial", 11))
        patterns_text.pack(fill=tk.BOTH, expand=True)
        
        for pattern, count in pattern_counts.most_common(3):
            percentage = (count / len(rows)) * 100
            patterns_text.insert(tk.END, f"{pattern}: {count} times ({percentage:.1f}%)\n")
        
        patterns_text.config(state=tk.DISABLED)
        
    def show_insights(self, parent):
        """Show personalized insights"""
        tk.Label(parent, text="🔍 Your Insights", font=("Arial", 14, "bold")).pack(pady=10)
        
        insights_text = tk.Text(parent, wrap=tk.WORD, font=("Arial", 11), bg="#f8f9fa")
        insights_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        insights = self.generate_insights()
        
        for insight in insights:
            insights_text.insert(tk.END, f"• {insight}\n\n")
            
        insights_text.config(state=tk.DISABLED)
        
    def generate_insights(self):
        """Generate insights"""
        insights = []
        
        session = get_session()
        try:
            # EQ insights
            eq_rows = session.query(Score.total_score)\
                .filter_by(username=self.username)\
                .order_by(Score.id)\
                .all()
            scores = [r[0] for r in eq_rows]
            
            # Journal insights
            j_rows = session.query(JournalEntry.sentiment_score)\
                .filter_by(username=self.username)\
                .all()
            sentiments = [r[0] for r in j_rows]
        finally:
            session.close()
        
        if len(scores) > 1:
            improvement = ((scores[-1] - scores[0]) / scores[0]) * 100
            if improvement > 10:
                insights.append(f"📈 Great progress! Your EQ improved by {improvement:.1f}%")
            elif improvement > 0:
                insights.append(f"📊 Steady progress with {improvement:.1f}% EQ improvement")
            else:
                insights.append("💪 Focus on emotional awareness to boost EQ scores")
        
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            if avg_sentiment > 20:
                insights.append("😊 Your journal shows positive emotional tone - keep it up!")
            elif avg_sentiment < -20:
                insights.append("🤗 Consider stress management techniques for better emotional balance")
            else:
                insights.append("⚖️ You maintain balanced emotional tone in your reflections")
        
        if not insights:
            insights.append("📝 Complete more assessments and journal entries for insights!")
            
        return insights