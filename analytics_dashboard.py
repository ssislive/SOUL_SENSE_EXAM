# analytics_dashboard.py - COMPLETE FIXED VERSION
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import json
import os
import sqlite3

# REMOVE THIS LINE - it's causing the error
# from app.models import get_session, Score, JournalEntry

class AnalyticsDashboard:
    def __init__(self, parent_root, username):
        self.parent_root = parent_root
        self.username = username
        self.benchmarks = self.load_benchmarks()

    def load_benchmarks(self):
        """Load population benchmarks from JSON"""
        try:
            with open("app/benchmarks.json", "r") as f:
                return json.load(f)
        except Exception:
            return None
        
    def open_dashboard(self):
        """Open analytics dashboard"""
        dashboard = tk.Toplevel(self.parent_root)
        dashboard.title("📊 Emotional Health Dashboard")
        dashboard.geometry("900x700")  # Increased size for new tab
        
        tk.Label(dashboard, text="📊 Emotional Health Analytics", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        notebook = ttk.Notebook(dashboard)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Correlation Analysis Tab (NEW)
        correlation_frame = ttk.Frame(notebook)
        notebook.add(correlation_frame, text="🔗 Correlation")
        self.show_correlation_analysis(correlation_frame)  # NEW METHOD
            
        # EQ Trends
        eq_frame = ttk.Frame(notebook)
        notebook.add(eq_frame, text="📈 EQ Trends")
        self.show_eq_trends(eq_frame)
        
        # Time-Based Analysis
        time_frame = ttk.Frame(notebook)
        notebook.add(time_frame, text="Time-Based Analysis")
        self.show_time_based_analysis(time_frame)
        
        # Journal Analytics
        journal_frame = ttk.Frame(notebook)
        notebook.add(journal_frame, text="📝 Journal Analytics")
        self.show_journal_analytics(journal_frame)
        
        # Insights
        insights_frame = ttk.Frame(notebook)
        notebook.add(insights_frame, text="🔍 Insights")
        self.show_insights(insights_frame)
        
    # ========== NEW CORRELATION ANALYSIS METHOD ==========
    def show_correlation_analysis(self, parent):
        """Show correlation analysis between EQ scores"""
        # Title
        tk.Label(parent, text="🔗 Correlation Analysis", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Description
        tk.Label(parent, 
                text="Analyze patterns and relationships in your EQ scores",
                font=("Arial", 11), wraplength=550).pack(pady=5)
        
        # Button to run analysis
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="Run Correlation Analysis", 
                 command=lambda: self.run_correlation(parent),
                 bg="#4CAF50", fg="white",
                 font=("Arial", 11, "bold")).pack()
        
        # Text area for results
        self.correlation_text = tk.Text(parent, wrap=tk.WORD, height=15, 
                                       font=("Arial", 11))
        self.correlation_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Visualization frame
        self.correlation_viz_frame = tk.Frame(parent)
        self.correlation_viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def run_correlation(self, parent):
        """Run correlation analysis"""
        try:
            # Clear previous content
            self.correlation_text.delete(1.0, tk.END)
            
            # Clear previous visualization
            for widget in self.correlation_viz_frame.winfo_children():
                widget.destroy()
            
            # Get EQ scores
            conn = sqlite3.connect("soulsense_db")
            cursor = conn.cursor()
            
            # First, check what columns exist in the scores table
            cursor.execute("PRAGMA table_info(scores)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Build query based on available columns
            if 'timestamp' in columns:
                cursor.execute("""
                    SELECT total_score, timestamp 
                    FROM scores 
                    WHERE username = ? 
                    ORDER BY timestamp
                """, (self.username,))
            else:
                cursor.execute("""
                    SELECT total_score, id 
                    FROM scores 
                    WHERE username = ? 
                    ORDER BY id
                """, (self.username,))
            
            data = cursor.fetchall()
            conn.close()
            
            if len(data) < 2:
                self.correlation_text.insert(tk.END, 
                    "⚠️ Need at least 2 EQ tests for correlation analysis.\n\n"
                    "Complete more tests and try again!")
                return
            
            scores = [row[0] for row in data]
            
            # Start analysis
            self.correlation_text.insert(tk.END, "📊 **CORRELATION ANALYSIS RESULTS**\n")
            self.correlation_text.insert(tk.END, "="*60 + "\n\n")
            
            # Import numpy for calculations
            try:
                import numpy as np
                
                # Basic statistics
                self.correlation_text.insert(tk.END, "📈 **Basic Statistics:**\n")
                self.correlation_text.insert(tk.END, f"• Number of tests: {len(scores)}\n")
                self.correlation_text.insert(tk.END, f"• Average score: {np.mean(scores):.2f}/25\n")
                self.correlation_text.insert(tk.END, f"• Best score: {max(scores)}\n")
                self.correlation_text.insert(tk.END, f"• Worst score: {min(scores)}\n")
                self.correlation_text.insert(tk.END, f"• Score range: {max(scores) - min(scores)} points\n\n")
                
                # Trend analysis
                if len(scores) >= 3:
                    x = np.arange(len(scores))
                    z = np.polyfit(x, scores, 1)
                    trend = z[0]
                    
                    self.correlation_text.insert(tk.END, "📈 **Trend Analysis:**\n")
                    self.correlation_text.insert(tk.END, f"• Trend slope: {trend:.3f} points per test\n")
                    
                    if trend > 0.5:
                        self.correlation_text.insert(tk.END, "✅ **Strong positive trend!** Consistent improvement!\n")
                    elif trend > 0.1:
                        self.correlation_text.insert(tk.END, "↗️ **Positive trend** - Gradual improvement\n")
                    elif trend < -0.5:
                        self.correlation_text.insert(tk.END, "📉 **Strong negative trend** - Review strategies\n")
                    elif trend < -0.1:
                        self.correlation_text.insert(tk.END, "↘️ **Negative trend** - Needs attention\n")
                    else:
                        self.correlation_text.insert(tk.END, "⚖️ **Stable performance**\n")
                    self.correlation_text.insert(tk.END, "\n")
                
                # Consistency analysis
                std_dev = np.std(scores)
                cv = (std_dev / np.mean(scores) * 100) if np.mean(scores) > 0 else 0
                
                self.correlation_text.insert(tk.END, "🎯 **Consistency Analysis:**\n")
                self.correlation_text.insert(tk.END, f"• Standard deviation: {std_dev:.2f}\n")
                self.correlation_text.insert(tk.END, f"• Coefficient of variation: {cv:.1f}%\n")
                
                if cv < 15:
                    self.correlation_text.insert(tk.END, "✅ **Excellent consistency** - Very stable scores\n")
                elif cv < 25:
                    self.correlation_text.insert(tk.END, "👍 **Good consistency** - Reliable performance\n")
                elif cv < 35:
                    self.correlation_text.insert(tk.END, "⚠️ **Moderate variation** - Some fluctuations\n")
                else:
                    self.correlation_text.insert(tk.END, "🔀 **High variation** - Inconsistent performance\n")
                self.correlation_text.insert(tk.END, "\n")
                
                # Create visualizations
                self.create_correlation_visualizations(scores)
                
            except ImportError:
                self.correlation_text.insert(tk.END, 
                    "⚠️ NumPy not installed. Install with: pip install numpy\n")
            
            self.correlation_text.insert(tk.END, "\n" + "="*60 + "\n")
            self.correlation_text.insert(tk.END, "✅ **Analysis complete!**\n")
            
        except Exception as e:
            self.correlation_text.insert(tk.END, f"❌ **Error:** {str(e)}\n")
    
    def create_correlation_visualizations(self, scores):
        """Create visualizations for correlation analysis"""
        try:
            import numpy as np
            
            # Create figure
            fig = Figure(figsize=(10, 8))
            
            # Plot 1: Score trend
            ax1 = fig.add_subplot(221)
            x_values = range(1, len(scores) + 1)
            ax1.plot(x_values, scores, 'o-', color='#4CAF50', linewidth=2)
            ax1.set_title('EQ Score Trend', fontweight='bold')
            ax1.set_xlabel('Test Number')
            ax1.set_ylabel('Score')
            ax1.grid(True, alpha=0.3)
            
            # Add trend line if enough points
            if len(scores) >= 3:
                z = np.polyfit(x_values, scores, 1)
                p = np.poly1d(z)
                ax1.plot(x_values, p(x_values), "r--", alpha=0.5)
                ax1.text(0.05, 0.95, f'Trend: {z[0]:.2f}/test', 
                        transform=ax1.transAxes, fontsize=10,
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
            
            # Plot 2: Score distribution
            ax2 = fig.add_subplot(222)
            ax2.hist(scores, bins=5, color='#2196F3', edgecolor='black', alpha=0.7)
            ax2.set_title('Score Distribution', fontweight='bold')
            ax2.set_xlabel('Score')
            ax2.set_ylabel('Frequency')
            ax2.grid(True, alpha=0.3)
            
            # Plot 3: Moving average
            ax3 = fig.add_subplot(223)
            if len(scores) >= 3:
                window = min(3, len(scores))
                moving_avg = [np.mean(scores[max(0, i-window+1):i+1]) 
                             for i in range(len(scores))]
                ax3.plot(x_values, moving_avg, 's-', color='#9C27B0', linewidth=2)
                ax3.set_title(f'{window}-Test Moving Average', fontweight='bold')
                ax3.set_xlabel('Test Number')
                ax3.set_ylabel('Average Score')
                ax3.grid(True, alpha=0.3)
            
            # Plot 4: Performance comparison
            ax4 = fig.add_subplot(224)
            if len(scores) >= 4:
                half = len(scores) // 2
                positions = ['First Half', 'Second Half']
                averages = [np.mean(scores[:half]), np.mean(scores[half:])]
                colors = ['#FF9800', '#4CAF50']
                bars = ax4.bar(positions, averages, color=colors)
                ax4.set_title('Performance Comparison', fontweight='bold')
                ax4.set_ylabel('Average Score')
                
                # Add value labels
                for bar, avg in zip(bars, averages):
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2., height,
                            f'{avg:.1f}', ha='center', va='bottom')
            
            fig.tight_layout()
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.correlation_viz_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            self.correlation_text.insert(tk.END, f"⚠️ Could not create visualizations: {str(e)}\n")
    
    # ========== EXISTING METHODS (UPDATED) ==========
    def show_eq_trends(self, parent):
        """Show EQ score trends with matplotlib graph"""
        conn = sqlite3.connect("soulsense_db")
        cursor = conn.cursor()
        
        # Check what columns exist
        cursor.execute("PRAGMA table_info(scores)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build query based on available columns
        if 'timestamp' in columns:
            cursor.execute("""
                SELECT total_score, timestamp, id 
                FROM scores 
                WHERE username = ? 
                ORDER BY id
            """, (self.username,))
        else:
            cursor.execute("""
                SELECT total_score, id 
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
        
        # Parse timestamps if available
        for i, row in enumerate(data):
            if len(row) > 1 and row[1]:
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
            improvement_pct = (improvement / scores[0]) * 100 if scores[0] != 0 else 0
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

    def show_time_based_analysis(self, parent):
        """Show time-based analysis of responses for returning users"""
        tk.Label(parent, text="⏰ Time-Based Response Analysis", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Get score trends
        trend_data = time_analyzer.analyze_score_trends(self.username)
        
        if "error" in trend_data:
            tk.Label(parent, text="No data available for time-based analysis", 
                    font=("Arial", 12)).pack(pady=50)
            return
        
        # Create scrollable frame for stats
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Stats Frame 1 - Basic Statistics
        stats1_frame = tk.Frame(scrollable_frame, bg="#f0f0f0", relief=tk.RIDGE, bd=2)
        stats1_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(stats1_frame, text="📊 Score Statistics", 
                font=("Arial", 11, "bold"), bg="#f0f0f0").pack(anchor="w", padx=10, pady=5)
        
        stats_text1 = tk.Text(stats1_frame, height=7, width=50, font=("Arial", 10), bg="#f0f0f0")
        stats_text1.pack(padx=10, pady=5)
        
        stats_text1.insert(tk.END, f"Total Attempts: {trend_data.get('total_attempts', 0)}\n")
        stats_text1.insert(tk.END, f"First Score: {trend_data.get('first_score', 'N/A')}\n")
        stats_text1.insert(tk.END, f"Latest Score: {trend_data.get('last_score', 'N/A')}\n")
        stats_text1.insert(tk.END, f"Average Score: {trend_data.get('average_score', 0):.1f}\n")
        stats_text1.insert(tk.END, f"Highest Score: {trend_data.get('max_score', 'N/A')}\n")
        stats_text1.insert(tk.END, f"Lowest Score: {trend_data.get('min_score', 'N/A')}\n")
        stats_text1.insert(tk.END, f"Score Standard Deviation: {trend_data.get('score_std_dev', 0):.2f}\n")
        stats_text1.config(state=tk.DISABLED)
        
        # Stats Frame 2 - Trend Information
        stats2_frame = tk.Frame(scrollable_frame, bg="#e3f2fd", relief=tk.RIDGE, bd=2)
        stats2_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(stats2_frame, text="📈 Trend Analysis", 
                font=("Arial", 11, "bold"), bg="#e3f2fd").pack(anchor="w", padx=10, pady=5)
        
        stats_text2 = tk.Text(stats2_frame, height=5, width=50, font=("Arial", 10), bg="#e3f2fd")
        stats_text2.pack(padx=10, pady=5)
        
        stats_text2.insert(tk.END, f"Total Improvement: {trend_data.get('total_improvement', 0):+d} points\n")
        stats_text2.insert(tk.END, f"Improvement %: {trend_data.get('improvement_percentage', 0):+.1f}%\n")
        stats_text2.insert(tk.END, f"Trend Direction: {trend_data.get('trend_direction', 'Unknown')}\n")
        stats_text2.insert(tk.END, f"First Attempt: {trend_data.get('first_attempt_date', 'N/A')}\n")
        stats_text2.insert(tk.END, f"Latest Attempt: {trend_data.get('last_attempt_date', 'N/A')}\n")
        stats_text2.config(state=tk.DISABLED)
        
        # Response Pattern Analysis
        response_patterns = time_analyzer.analyze_response_patterns_over_time(self.username)
        
        if "error" not in response_patterns:
            stats3_frame = tk.Frame(scrollable_frame, bg="#f5f5f5", relief=tk.RIDGE, bd=2)
            stats3_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(stats3_frame, text="🔄 Response Pattern Changes", 
                    font=("Arial", 11, "bold"), bg="#f5f5f5").pack(anchor="w", padx=10, pady=5)
            
            pattern_summary = f"Total Responses: {response_patterns.get('total_responses', 0)}\n"
            pattern_summary += f"Unique Questions Answered: {response_patterns.get('unique_questions_answered', 0)}\n"
            pattern_summary += f"Overall Response Average: {response_patterns.get('overall_average_response', 0):.2f}\n"
            pattern_summary += f"Response Consistency (Std Dev): {response_patterns.get('overall_response_std_dev', 0):.2f}\n"
            
            stats_text3 = tk.Text(stats3_frame, height=4, width=50, font=("Arial", 10), bg="#f5f5f5")
            stats_text3.pack(padx=10, pady=5)
            stats_text3.insert(tk.END, pattern_summary)
            stats_text3.config(state=tk.DISABLED)
        
        # Comparative Analysis (Last 30 days vs historical)
        comparative = time_analyzer.get_comparative_analysis(self.username, lookback_days=30)
        
        if "error" not in comparative:
            stats4_frame = tk.Frame(scrollable_frame, bg="#fff3e0", relief=tk.RIDGE, bd=2)
            stats4_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(stats4_frame, text="📅 Recent vs Historical (Last 30 Days)", 
                    font=("Arial", 11, "bold"), bg="#fff3e0").pack(anchor="w", padx=10, pady=5)
            
            comp_text = tk.Text(stats4_frame, height=6, width=50, font=("Arial", 10), bg="#fff3e0")
            comp_text.pack(padx=10, pady=5)
            
            if "historical" in comparative:
                hist = comparative["historical"]
                comp_text.insert(tk.END, f"Historical Avg Score: {hist.get('average_score', 0):.1f}\n")
                comp_text.insert(tk.END, f"Historical Attempts: {hist.get('attempts', 0)}\n\n")
            
            if "recent" in comparative:
                recent = comparative["recent"]
                comp_text.insert(tk.END, f"Recent Avg Score (30d): {recent.get('average_score', 0):.1f}\n")
                comp_text.insert(tk.END, f"Recent Attempts: {recent.get('attempts', 0)}\n")
            
            if "performance_change" in comparative:
                change = comparative["performance_change"]
                change_pct = comparative.get("performance_change_percentage", 0)
                color_indicator = "📈" if change > 0 else "📉" if change < 0 else "⚖️"
                comp_text.insert(tk.END, f"\n{color_indicator} Performance Change: {change:+.1f} ({change_pct:+.1f}%)")
            
            comp_text.config(state=tk.DISABLED)

    def show_journal_analytics(self, parent):
        """Show journal analytics"""
        conn = sqlite3.connect("soulsense_db")
        cursor = conn.cursor()
        
        # Check if journal_entries table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='journal_entries'")
        if not cursor.fetchone():
            conn.close()
            tk.Label(parent, text="Journal feature not yet used", font=("Arial", 14)).pack(pady=50)
            return
        
        # Get journal data
        cursor.execute("""
            SELECT sentiment_score, emotional_patterns 
            FROM journal_entries 
            WHERE username = ? 
            ORDER BY id
        """, (self.username,))
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            tk.Label(parent, text="No journal entries found", font=("Arial", 14)).pack(pady=50)
            return
            
        tk.Label(parent, text="📝 Journal Analytics", font=("Arial", 14, "bold")).pack(pady=10)
        
        sentiments = [r[0] for r in rows if r[0] is not None]
        
        # Stats
        stats_frame = tk.Frame(parent)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(stats_frame, text=f"Total Entries: {len(rows)}", font=("Arial", 12)).pack(anchor="w")
        
        if sentiments:
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
            percentage = (count / len(rows)) * 100 if len(rows) > 0 else 0
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
        
        # Get EQ scores
        conn = sqlite3.connect("soulsense_db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT total_score 
            FROM scores 
            WHERE username = ? 
            ORDER BY id
        """, (self.username,))
        eq_rows = cursor.fetchall()
        
        # Get journal data if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='journal_entries'")
        journal_exists = cursor.fetchone()
        
        if journal_exists:
            cursor.execute("""
                SELECT sentiment_score 
                FROM journal_entries 
                WHERE username = ?
            """, (self.username,))
            j_rows = cursor.fetchall()
        else:
            j_rows = []
        
        conn.close()
        
        scores = [r[0] for r in eq_rows]
        
        if len(scores) > 1:
            improvement = ((scores[-1] - scores[0]) / scores[0]) * 100 if scores[0] != 0 else 0
            if improvement > 10:
                insights.append(f"📈 Great progress! Your EQ improved by {improvement:.1f}%")
            elif improvement > 0:
                insights.append(f"📊 Steady progress with {improvement:.1f}% EQ improvement")
            else:
                insights.append("💪 Focus on emotional awareness to boost EQ scores")
        
        if j_rows:
            sentiments = [r[0] for r in j_rows if r[0] is not None]
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
        
        # Add Benchmark Insights
        if self.benchmarks and self.benchmarks.get("global_avg"):
            avg = self.benchmarks["global_avg"]
            if scores and scores[-1] > avg:
                insights.append(f"🌟 You are above the Global Average ({avg:.1f})!")
            elif scores:
                insights.append(f"📊 Global Average is {avg:.1f}. Keep practicing!")

        return insights