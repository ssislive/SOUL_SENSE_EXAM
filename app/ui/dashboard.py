# analytics_dashboard.py - COMPLETE FIXED VERSION (Merged)
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from collections import Counter
import matplotlib
matplotlib.use("Agg") # Prevent GUI mainloop conflicts
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import json
import os
import sqlite3

from app.i18n_manager import get_i18n

# REMOVE THIS LINE - it's causing the error
# from app.models import get_session, Score, JournalEntry
from app.models import Score, JournalEntry
from app.db import get_session, get_connection
from app.analysis.time_based_analysis import time_analyzer

# Import emotional profile clustering
try:
    from app.ml.clustering import (
        EmotionalProfileClusterer,
        ClusteringVisualizer,
        EMOTIONAL_PROFILES,
        create_profile_clusterer,
        get_user_emotional_profile
    )
    CLUSTERING_AVAILABLE = True
except ImportError:
    CLUSTERING_AVAILABLE = False


class AnalyticsDashboard:
    def __init__(self, parent_root, username, colors=None, theme="light"):
        self.parent_root = parent_root
        self.username = username
        self.benchmarks = self.load_benchmarks()
        self.i18n = get_i18n()
        self.theme = theme
        # Default colors for dark/light theme
        if colors:
            self.colors = colors
        else:
            self.colors = {
                "bg": "#0F172A" if theme == "dark" else "#F8FAFC",
                "surface": "#1E293B" if theme == "dark" else "#FFFFFF",
                "text_primary": "#F8FAFC" if theme == "dark" else "#0F172A",
                "text_secondary": "#94A3B8" if theme == "dark" else "#64748B",
                "primary": "#3B82F6",
                "border": "#334155" if theme == "dark" else "#E2E8F0"
            }

    def load_benchmarks(self):
        """Load population benchmarks from JSON"""
        try:
            with open("app/benchmarks.json", "r") as f:
                return json.load(f)
        except Exception:
            return None
        
    def open_dashboard(self):
        """Open analytics dashboard with theme support"""
        colors = self.colors
        
        dashboard = tk.Toplevel(self.parent_root)
        dashboard.title(self.i18n.get("dashboard.title"))
        dashboard.geometry("950x750")
        dashboard.configure(bg=colors.get("bg", "#0F172A"))
        
        # Header
        header = tk.Frame(dashboard, bg=colors.get("primary", "#3B82F6"))
        header.pack(fill="x")
        
        tk.Label(
            header,
            text=f"📊 {self.i18n.get('dashboard.analytics')}", 
            font=("Segoe UI", 18, "bold"),
            bg=colors.get("primary", "#3B82F6"),
            fg="white"
        ).pack(pady=15)
        
        # Configure ttk style for dark/light theme
        style = ttk.Style()
        if self.theme == "dark":
            style.configure("TNotebook", background=colors.get("bg", "#0F172A"))
            style.configure("TFrame", background=colors.get("bg", "#0F172A"))
        
        notebook = ttk.Notebook(dashboard)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Correlation Analysis Tab
        correlation_frame = ttk.Frame(notebook)
        notebook.add(correlation_frame, text="🔗 Correlation")
        self.show_correlation_analysis(correlation_frame)
            
        # EQ Trends
        eq_frame = ttk.Frame(notebook)
        notebook.add(eq_frame, text=self.i18n.get("dashboard.eq_trends_tab"))
        self.show_eq_trends(eq_frame)
        
        # Time-Based Analysis
        time_frame = ttk.Frame(notebook)
        notebook.add(time_frame, text=self.i18n.get("dashboard.time_based_tab"))
        self.show_time_based_analysis(time_frame)
        
        # Journal Analytics
        journal_frame = ttk.Frame(notebook)
        notebook.add(journal_frame, text=self.i18n.get("dashboard.journal_tab"))
        self.show_journal_analytics(journal_frame)
        
        # Insights
        insights_frame = ttk.Frame(notebook)
        notebook.add(insights_frame, text=self.i18n.get("dashboard.insights_tab"))
        self.show_insights(insights_frame)
        
        # Emotional Profile Clustering Tab
        if CLUSTERING_AVAILABLE:
            clustering_frame = ttk.Frame(notebook)
            notebook.add(clustering_frame, text="🧬 Emotional Profile")
            self.show_emotional_profile(clustering_frame)
        
    # ========== NEW CORRELATION ANALYSIS METHOD ==========
    def show_correlation_analysis(self, parent):
        """Show correlation analysis between EQ scores"""
        # Title
        tk.Label(parent, text=self.i18n.get("dashboard.correlation_title"), 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Description
        tk.Label(parent, 
                text=self.i18n.get("dashboard.correlation_desc"),
                font=("Arial", 11), wraplength=550).pack(pady=5)
        
        # Button to run analysis
        button_frame = tk.Frame(parent)
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text=self.i18n.get("dashboard.run_analysis"), 
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
            conn = get_connection()
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
            ax1.set_title(self.i18n.get("dashboard.trend_title"), fontweight='bold')
            ax1.set_xlabel(self.i18n.get("dashboard.trend_xlabel"))
            ax1.set_ylabel(self.i18n.get("dashboard.trend_ylabel"))
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
            ax2.set_title(self.i18n.get("dashboard.distribution_title"), fontweight='bold')
            ax2.set_xlabel(self.i18n.get("dashboard.distribution_xlabel"))
            ax2.set_ylabel(self.i18n.get("dashboard.distribution_ylabel"))
            ax2.grid(True, alpha=0.3)
            
            # Plot 3: Moving average
            ax3 = fig.add_subplot(223)
            if len(scores) >= 3:
                window = min(3, len(scores))
                moving_avg = [np.mean(scores[max(0, i-window+1):i+1]) 
                             for i in range(len(scores))]
                ax3.plot(x_values, moving_avg, 's-', color='#9C27B0', linewidth=2)
                ax3.set_title(self.i18n.get("dashboard.moving_avg_title", window=window), fontweight='bold')
                ax3.set_xlabel(self.i18n.get("dashboard.trend_xlabel"))
                ax3.set_ylabel(self.i18n.get("dashboard.moving_avg_ylabel"))
                ax3.grid(True, alpha=0.3)
            
            # Plot 4: Performance comparison
            ax4 = fig.add_subplot(224)
            if len(scores) >= 4:
                half = len(scores) // 2
                positions = [self.i18n.get("dashboard.first_half"), self.i18n.get("dashboard.second_half")]
                averages = [np.mean(scores[:half]), np.mean(scores[half:])]
                colors = ['#FF9800', '#4CAF50']
                bars = ax4.bar(positions, averages, color=colors)
                ax4.set_title(self.i18n.get("dashboard.performance_title"), fontweight='bold')
                ax4.set_ylabel(self.i18n.get("dashboard.performance_ylabel"))
                
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
        # Set colors
        colors = self.colors
        bg_color = colors.get("bg", "#F8FAFC")
        surface_color = colors.get("surface", "#FFFFFF")
        text_primary = colors.get("text_primary", "#0F172A")
        text_secondary = colors.get("text_secondary", "#64748B")
        
        # Configure parent
        parent.configure(style="TFrame")
        
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT total_score, timestamp, id, sentiment_score 
            FROM scores 
            WHERE username = ? 
            ORDER BY id
            """, (self.username,))
            data = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching EQ trends: {e}")
            data = []
        finally:
            conn.close()
        
        if not data:
            tk.Label(parent, text="No EQ data available", font=("Arial", 14), bg=bg_color, fg=text_primary).pack(pady=50)
            return
        
        scores = [row[0] for row in data]
        sentiment_scores = [row[3] if len(row) > 3 else None for row in data]
        
        tk.Label(parent, text="📈 EQ Score Progress Over Time", 
                font=("Segoe UI", 16, "bold"), bg=bg_color, fg=text_primary).pack(pady=(15, 10))
        
        # Stats frame
        stats_frame = tk.Frame(parent, bg=surface_color, relief=tk.RIDGE, bd=1,
                              highlightbackground=colors.get("border", "#E2E8F0"), highlightthickness=1)
        stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create two columns for stats
        left_col = tk.Frame(stats_frame, bg=surface_color)
        left_col.pack(side=tk.LEFT, padx=30, pady=15, expand=True)
        
        right_col = tk.Frame(stats_frame, bg=surface_color)
        right_col.pack(side=tk.LEFT, padx=30, pady=15, expand=True)
        
        tk.Label(left_col, text=f"Total Attempts: {len(scores)}", 
                font=("Segoe UI", 11, "bold"), bg=surface_color, fg=text_primary).pack(anchor="w", pady=2)
        tk.Label(left_col, text=f"Latest Score: {scores[-1]}", 
                font=("Segoe UI", 11), bg=surface_color, fg=text_primary).pack(anchor="w", pady=2)
        tk.Label(left_col, text=f"Best Score: {max(scores)}", 
                font=("Segoe UI", 11), bg=surface_color, fg="#22C55E").pack(anchor="w", pady=2)
        
        tk.Label(right_col, text=f"First Score: {scores[0]}", 
                font=("Segoe UI", 11), bg=surface_color, fg=text_primary).pack(anchor="w", pady=2)
        tk.Label(right_col, text=f"Average Score: {sum(scores)/len(scores):.1f}", 
                font=("Segoe UI", 11), bg=surface_color, fg=text_primary).pack(anchor="w", pady=2)
        
        if len(scores) > 1:
            improvement = scores[-1] - scores[0]
            improvement_pct = (improvement / scores[0]) * 100 if scores[0] != 0 else 0
            color = "#22C55E" if improvement > 0 else "#EF4444" if improvement < 0 else "#3B82F6"
            symbol = "↑" if improvement > 0 else "↓" if improvement < 0 else "→"
            tk.Label(right_col, text=f"Progress: {symbol} {improvement:+d} ({improvement_pct:+.1f}%)", 
                    font=("Segoe UI", 11, "bold"), bg=surface_color, fg=color).pack(anchor="w", pady=2)
        
        # Create matplotlib figure
        plt.style.use('dark_background' if self.theme == 'dark' else 'default')
        if self.theme == 'dark':
            fig_bg = '#1E293B' # Surface color for dark mode chart
            plot_bg = '#1E293B'
            text_color = '#F8FAFC'
            grid_color = '#334155'
        else:
            fig_bg = '#F8FAFC'
            plot_bg = '#F8FAFC'
            text_color = '#0F172A'
            grid_color = '#E2E8F0'

        fig = Figure(figsize=(6, 4), dpi=80, facecolor=fig_bg)
        ax1 = fig.add_subplot(111)
        ax1.set_facecolor(plot_bg)
        
        # Plot EQ Score
        l1, = ax1.plot(range(1, len(scores) + 1), scores, 
               marker='o', linestyle='-', linewidth=2, markersize=8,
               color='#22C55E', markerfacecolor='#22C55E', 
               markeredgewidth=2, markeredgecolor='white', label="EQ Score")
        
        ax1.set_xlabel('Attempt Number', fontsize=11, fontweight='bold', color=text_color)
        ax1.set_ylabel('EQ Score', fontsize=11, fontweight='bold', color='#22C55E')
        ax1.tick_params(axis='y', labelcolor='#22C55E', colors=text_color)
        ax1.tick_params(axis='x', colors=text_color)
        ax1.set_title('EQ Score & Emotional Sentiment Trends', fontsize=12, fontweight='bold', pad=15, color=text_color)
        ax1.grid(True, alpha=0.3, linestyle='--', color=grid_color)
        ax1.set_xticks(range(1, len(scores) + 1))
        
        for spine in ax1.spines.values():
            spine.set_color(grid_color)
        
        # Plot Sentiment Score (Secondary Axis)
        if sentiment_scores and any(s is not None and s != 0 for s in sentiment_scores):
            ax2 = ax1.twinx()
            # Filter out Nones for plotting
            valid_indices = [i for i, s in enumerate(sentiment_scores) if s is not None]
            valid_x = [i + 1 for i in valid_indices]
            valid_y = [sentiment_scores[i] for i in valid_indices]
            
            l2, = ax2.plot(valid_x, valid_y, 
                     marker='s', linestyle='--', linewidth=2, markersize=6,
                     color='#F59E0B', markerfacecolor='#F59E0B',
                     markeredgewidth=2, markeredgecolor='white', label="Sentiment")
                     
            ax2.set_ylabel('Sentiment Score (-100 to +100)', fontsize=11, fontweight='bold', color='#F59E0B')
            ax2.tick_params(axis='y', labelcolor='#F59E0B', colors=text_color)
            ax2.set_ylim(-110, 110)
            
            for spine in ax2.spines.values():
                spine.set_color(grid_color)
            
            # Combined Legend
            lines = [l1, l2]
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, loc='upper left')
        else:
            ax1.legend(loc='upper left')
        
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
        
        # Helper to create styled section
        def create_styled_text(parent_frame, bg_color):
            t = tk.Text(parent_frame, height=7, width=50, font=("Arial", 10), 
                       bg=bg_color, fg="black", relief=tk.FLAT)
            t.tag_config("label", foreground="#555555", font=("Arial", 10, "bold"))
            t.tag_config("value", foreground="#000000", font=("Arial", 10))
            t.tag_config("highlight", foreground="#2E7D32", font=("Arial", 10, "bold")) # Green
            t.tag_config("alert", foreground="#C62828", font=("Arial", 10, "bold")) # Red
            t.tag_config("info", foreground="#1565C0", font=("Arial", 10, "bold")) # Blue
            return t

        def insert_pair(text_widget, label, value, value_tag="value"):
            text_widget.insert(tk.END, f"{label}: ", "label")
            text_widget.insert(tk.END, f"{value}\n", value_tag)
        
        # Stats Frame 1 - Basic Statistics
        stats1_frame = tk.Frame(scrollable_frame, bg="#f0f0f0", relief=tk.RIDGE, bd=2)
        stats1_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(stats1_frame, text="📊 Score Statistics", 
                font=("Arial", 11, "bold"), bg="#f0f0f0", fg="black").pack(anchor="w", padx=10, pady=5)
        
        stats_text1 = create_styled_text(stats1_frame, "#f0f0f0")
        stats_text1.pack(padx=10, pady=5)
        
        insert_pair(stats_text1, "Total Attempts", trend_data.get('total_attempts', 0))
        insert_pair(stats_text1, "First Score", trend_data.get('first_score', 'N/A'))
        insert_pair(stats_text1, "Latest Score", trend_data.get('last_score', 'N/A'), "highlight")
        insert_pair(stats_text1, "Average Score", f"{trend_data.get('average_score', 0):.1f}")
        insert_pair(stats_text1, "Highest Score", trend_data.get('max_score', 'N/A'))
        insert_pair(stats_text1, "Lowest Score", trend_data.get('min_score', 'N/A'))
        insert_pair(stats_text1, "Score Std Dev", f"{trend_data.get('score_std_dev', 0):.2f}")
        stats_text1.config(state=tk.DISABLED)
        
        # Stats Frame 2 - Trend Information
        stats2_frame = tk.Frame(scrollable_frame, bg="#e3f2fd", relief=tk.RIDGE, bd=2)
        stats2_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(stats2_frame, text="📈 Trend Analysis", 
                font=("Arial", 11, "bold"), bg="#e3f2fd", fg="black").pack(anchor="w", padx=10, pady=5)
        
        stats_text2 = create_styled_text(stats2_frame, "#e3f2fd")
        stats_text2.config(height=5)
        stats_text2.pack(padx=10, pady=5)
        
        imp = trend_data.get('total_improvement', 0)
        imp_tag = "highlight" if imp > 0 else "alert" if imp < 0 else "value"
        
        insert_pair(stats_text2, "Total Improvement", f"{imp:+d} points", imp_tag)
        insert_pair(stats_text2, "Improvement %", f"{trend_data.get('improvement_percentage', 0):+.1f}%", imp_tag)
        insert_pair(stats_text2, "Trend Direction", trend_data.get('trend_direction', 'Unknown'), "info")
        insert_pair(stats_text2, "First Attempt", trend_data.get('first_attempt_date', 'N/A'))
        insert_pair(stats_text2, "Latest Attempt", trend_data.get('last_attempt_date', 'N/A'))
        stats_text2.config(state=tk.DISABLED)
        
        # Response Pattern Analysis
        response_patterns = time_analyzer.analyze_response_patterns_over_time(self.username)
        
        if "error" not in response_patterns:
            stats3_frame = tk.Frame(scrollable_frame, bg="#f5f5f5", relief=tk.RIDGE, bd=2)
            stats3_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(stats3_frame, text="🔄 Response Pattern Changes", 
                    font=("Arial", 11, "bold"), bg="#f5f5f5", fg="black").pack(anchor="w", padx=10, pady=5)
            
            stats_text3 = create_styled_text(stats3_frame, "#f5f5f5")
            stats_text3.config(height=4)
            stats_text3.pack(padx=10, pady=5)
            
            insert_pair(stats_text3, "Total Responses", response_patterns.get('total_responses', 0))
            insert_pair(stats_text3, "Unique Questions", response_patterns.get('unique_questions_answered', 0))
            insert_pair(stats_text3, "Overall Avg Response", f"{response_patterns.get('overall_average_response', 0):.2f}")
            insert_pair(stats_text3, "Consistency (Std Dev)", f"{response_patterns.get('overall_response_std_dev', 0):.2f}")
            stats_text3.config(state=tk.DISABLED)
        
        # Comparative Analysis (Last 30 days vs historical)
        comparative = time_analyzer.get_comparative_analysis(self.username, lookback_days=30)
        
        if "error" not in comparative:
            stats4_frame = tk.Frame(scrollable_frame, bg="#fff3e0", relief=tk.RIDGE, bd=2)
            stats4_frame.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(stats4_frame, text="📅 Recent vs Historical (Last 30 Days)", 
                    font=("Arial", 11, "bold"), bg="#fff3e0", fg="black").pack(anchor="w", padx=10, pady=5)
            
            comp_text = create_styled_text(stats4_frame, "#fff3e0")
            comp_text.config(height=6)
            comp_text.pack(padx=10, pady=5)
            
            if "historical" in comparative:
                hist = comparative["historical"]
                insert_pair(comp_text, "Historical Avg", f"{hist.get('average_score', 0):.1f}")
                insert_pair(comp_text, "Historical Attempts", hist.get('attempts', 0))
                comp_text.insert(tk.END, "\n")
            
            if "recent" in comparative:
                recent = comparative["recent"]
                insert_pair(comp_text, "Recent Avg (30d)", f"{recent.get('average_score', 0):.1f}")
                insert_pair(comp_text, "Recent Attempts", recent.get('attempts', 0))
            
            if "performance_change" in comparative:
                change = comparative["performance_change"]
                change_pct = comparative.get("performance_change_percentage", 0)
                change_tag = "highlight" if change > 0 else "alert" if change < 0 else "value"
                symbol = "📈" if change > 0 else "📉" if change < 0 else "⚖️"
                
                comp_text.insert(tk.END, f"\n{symbol} Change: ", "label")
                comp_text.insert(tk.END, f"{change:+.1f} ({change_pct:+.1f}%)", change_tag)
            
            comp_text.config(state=tk.DISABLED)

    def show_journal_analytics(self, parent):
        """Show journal analytics"""
        conn = get_connection() # Use centralized connection logic
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
    
    # ========== EMOTIONAL PROFILE CLUSTERING TAB ==========
    def show_emotional_profile(self, parent):
        """Show emotional profile clustering analysis."""
        if not CLUSTERING_AVAILABLE:
            tk.Label(parent, text="❌ Clustering module not available", 
                    font=("Arial", 14)).pack(pady=50)
            return
        
        # Title
        tk.Label(parent, text="🧬 Your Emotional Profile", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Description
        tk.Label(parent, 
                text="Discover your emotional profile based on unsupervised learning analysis of your assessment patterns.",
                font=("Arial", 11), wraplength=600).pack(pady=5)
        
        # Results frame
        results_frame = tk.Frame(parent, bg="#f8f9fa", relief=tk.RIDGE, bd=2)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Load or compute profile
        try:
            profile = get_user_emotional_profile(self.username)
            
            if profile is None:
                tk.Label(results_frame, 
                        text="⚠️ Not enough data to determine your emotional profile yet.\n\n"
                             "Complete more assessments to unlock this feature!",
                        font=("Arial", 12), bg="#f8f9fa", fg="#666").pack(pady=50)
                return
            
            profile_info = profile.get('profile', {})
            
            # --- Sentiment-style summary card (compact) ---
            # Use avg_sentiment from features if available (scale -1..1 -> -100..100)
            avg_sent = 0
            try:
                avg_sent = float(profile.get('features', {}).get('avg_sentiment', 0))
            except Exception:
                avg_sent = 0

            sentiment_score = avg_sent * 100.0
            if sentiment_score > 20:
                sentiment_label = "Positive"
                sentiment_color = "#4CAF50"
            elif sentiment_score < -20:
                sentiment_label = "Negative"
                sentiment_color = "#E53935"
            else:
                sentiment_label = "Neutral/Balanced"
                sentiment_color = "#FFC107"

            card_bg = "#111111"
            card_fg = sentiment_color

            card_frame = tk.Frame(results_frame, bg=card_bg, relief=tk.RIDGE, bd=0)
            card_frame.pack(fill=tk.X, padx=20, pady=(10, 8))

            tk.Label(card_frame, text="Emotional Sentiment:",
                    font=("Arial", 12, "bold"), bg=card_bg, fg="#FFFFFF").pack(anchor="w", padx=12, pady=(10, 0))

            # Large score line
            score_text = f"{sentiment_score:+.1f} ({sentiment_label})"
            tk.Label(card_frame, text=score_text,
                    font=("Arial", 20, "bold"), bg=card_bg, fg=card_fg).pack(anchor="w", padx=12, pady=(4, 2))

            # Subtext
            subtext = "Your reflection shows balanced emotions."
            if sentiment_label == "Positive":
                subtext = "Your reflection shows positive emotional tone."
            elif sentiment_label == "Negative":
                subtext = "Your reflection indicates negative emotional tone; consider support."

            tk.Label(card_frame, text=subtext,
                    font=("Arial", 10, "italic"), bg=card_bg, fg="#DDDDDD").pack(anchor="w", padx=12, pady=(0, 10))

            # Quick actions
            action_frame = tk.Frame(card_frame, bg=card_bg)
            action_frame.pack(anchor="e", padx=12, pady=(0, 10))

            def _open_full_report():
                try:
                    clusterer = create_profile_clusterer()
                    visualizer = ClusteringVisualizer(clusterer)
                    report_text = visualizer.generate_profile_report(self.username)

                    rpt = tk.Toplevel(self.parent_root)
                    rpt.title("Emotional Profile Report")
                    txt = tk.Text(rpt, wrap=tk.WORD, font=("Courier", 10))
                    txt.insert(tk.END, report_text)
                    txt.config(state=tk.DISABLED)
                    txt.pack(fill=tk.BOTH, expand=True)
                except Exception as e:
                    tk.messagebox.showerror("Error", f"Could not open report: {e}")

            tk.Button(action_frame, text="See full profile report",
                      command=_open_full_report, bg="#333333", fg="#FFFFFF", padx=8, pady=4).pack()

            # Profile Header
            header_frame = tk.Frame(results_frame, bg="#f8f9fa")
            header_frame.pack(fill=tk.X, padx=20, pady=15)
            
            profile_emoji = profile_info.get('emoji', '🔍')
            profile_name = profile_info.get('name', 'Unknown')
            profile_color = profile_info.get('color', '#333333')
            
            tk.Label(header_frame, 
                    text=f"{profile_emoji} {profile_name}",
                    font=("Arial", 20, "bold"), bg="#f8f9fa", fg=profile_color).pack()
            
            # Confidence
            confidence = profile.get('confidence', 0) * 100
            tk.Label(header_frame, 
                    text=f"Confidence: {confidence:.1f}%",
                    font=("Arial", 11), bg="#f8f9fa", fg="#666").pack(pady=5)
            
            # Description
            desc_frame = tk.Frame(results_frame, bg="#ffffff", relief=tk.GROOVE, bd=1)
            desc_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(desc_frame, 
                    text=profile_info.get('description', ''),
                    font=("Arial", 11), bg="#ffffff", wraplength=550).pack(pady=15, padx=15)
            
            # Two-column layout for characteristics and recommendations
            content_frame = tk.Frame(results_frame, bg="#f8f9fa")
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Characteristics column
            char_frame = tk.Frame(content_frame, bg="#e3f2fd", relief=tk.GROOVE, bd=1)
            char_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
            
            tk.Label(char_frame, text="✨ Key Characteristics",
                    font=("Arial", 12, "bold"), bg="#e3f2fd").pack(pady=10)
            
            for char in profile_info.get('characteristics', []):
                tk.Label(char_frame, text=f"• {char}",
                        font=("Arial", 10), bg="#e3f2fd", 
                        wraplength=250, justify=tk.LEFT).pack(anchor="w", padx=15, pady=3)
            
            # Recommendations column
            rec_frame = tk.Frame(content_frame, bg="#e8f5e9", relief=tk.GROOVE, bd=1)
            rec_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
            
            tk.Label(rec_frame, text="💡 Recommendations",
                    font=("Arial", 12, "bold"), bg="#e8f5e9").pack(pady=10)
            
            for rec in profile_info.get('recommendations', []):
                tk.Label(rec_frame, text=f"→ {rec}",
                        font=("Arial", 10), bg="#e8f5e9",
                        wraplength=250, justify=tk.LEFT).pack(anchor="w", padx=15, pady=3)
            
            # Profile Distribution (All Profiles Overview)
            dist_frame = tk.Frame(results_frame, bg="#f8f9fa")
            dist_frame.pack(fill=tk.X, padx=20, pady=15)
            
            tk.Label(dist_frame, text="📊 All Emotional Profiles",
                    font=("Arial", 12, "bold"), bg="#f8f9fa").pack(pady=5)
            
            # Show all profiles as a legend
            profiles_row = tk.Frame(dist_frame, bg="#f8f9fa")
            profiles_row.pack()
            
            for pid, pinfo in EMOTIONAL_PROFILES.items():
                is_current = pid == profile.get('cluster_id')
                badge_bg = pinfo['color'] if is_current else "#cccccc"
                badge_fg = "white" if is_current else "#666666"
                
                badge = tk.Label(profiles_row, 
                               text=f"{pinfo['emoji']} {pinfo['name'][:15]}",
                               font=("Arial", 9, "bold" if is_current else "normal"),
                               bg=badge_bg, fg=badge_fg,
                               padx=8, pady=4, relief=tk.RAISED if is_current else tk.FLAT)
                badge.pack(side=tk.LEFT, padx=3)
            
        except Exception as e:
            tk.Label(results_frame, 
                    text=f"⚠️ Error loading profile: {str(e)}",
                    font=("Arial", 11), bg="#f8f9fa", fg="red").pack(pady=50)
        
    def generate_insights(self):
        """Generate insights"""
        insights = []
        
        session = get_session()
        try:
            # EQ and Sentiment insights from SCORES table
            eq_rows = session.query(Score.total_score, Score.sentiment_score)\
                .filter_by(username=self.username)\
                .order_by(Score.id)\
                .all()
            scores = [r[0] for r in eq_rows]
            test_sentiments = [r[1] for r in eq_rows if r[1] is not None]
            
            # Journal insights purely from Journal entries
            j_rows = session.query(JournalEntry.sentiment_score)\
                .filter_by(username=self.username)\
                .all()
            journal_sentiments = [r[0] for r in j_rows]
        finally:
            session.close()
        
        if len(scores) > 1:
            improvement = ((scores[-1] - scores[0]) / scores[0]) * 100 if scores[0] != 0 else 0
            if improvement > 10:
                insights.append(f"📈 Great progress! Your EQ improved by {improvement:.1f}%")
            elif improvement > 0:
                insights.append(f"📊 Steady progress with {improvement:.1f}% EQ improvement")
            else:
                insights.append("💪 Focus on emotional awareness to boost EQ scores")
        
        if journal_sentiments:
            avg_sentiment = sum(journal_sentiments) / len(journal_sentiments)
            if avg_sentiment > 20:
                insights.append("😊 Your journal shows positive emotional tone - keep it up!")
            elif avg_sentiment < -20:
                insights.append("🤗 Consider stress management techniques for better emotional balance")
            else:
                insights.append("⚖️ You maintain balanced emotional tone in your reflections")
                
        # Correlation Insight
        if scores and test_sentiments:
            latest_score = scores[-1]
            latest_sentiment = test_sentiments[-1]
            
            if latest_score > 35 and latest_sentiment < -20:
                insights.append("🎭 You have high EQ skills but are feeling down. Use your skills to navigate this emotions.")
            elif latest_score < 25 and latest_sentiment > 20:
                insights.append("🌱 Your spirit is high despite lower EQ scores! Use this optimism to learn emotional skills.")
        
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