import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import logging
import threading
import time
from datetime import datetime
import json
import webbrowser
import os
import sys
import random # For random tips

# NLTK (optional) - import defensively so app can run without it
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    SENTIMENT_AVAILABLE = True
except Exception:
    SENTIMENT_AVAILABLE = False
    SentimentIntensityAnalyzer = None
import traceback # Keep this, it was in the original and not explicitly removed

from app.db import get_session, get_connection
from app.config import APP_CONFIG
from app.models import User, Score, Response, Question
from app.exceptions import DatabaseError, ValidationError, AuthenticationError, APIConnectionError, SoulSenseError
from app.logger import setup_logging
from app.data_cleaning import DataCleaner
from app.utils import load_settings, save_settings, compute_age_group
from app.questions import load_questions

# Try importing optional features
try:
    from journal_feature import JournalFeature
except ImportError:
    logging.warning("Could not import JournalFeature")
    JournalFeature = None

try:
    from ml_predictor import SoulSenseMLPredictor
except ImportError:
    logging.warning("Could not import SoulSenseMLPredictor")
    SoulSenseMLPredictor = None

try:
    from analytics_dashboard import AnalyticsDashboard
except ImportError:
    logging.warning("Could not import AnalyticsDashboard")
    AnalyticsDashboard = None

# Ensure VADER lexicon is downloaded when NLTK is available
if SENTIMENT_AVAILABLE:
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        try:
            nltk.download('vader_lexicon', quiet=True)
        except Exception:
            # If download fails, continue without sentiment functionality
            SENTIMENT_AVAILABLE = False

# ---------------- LOGGING SETUP ----------------
setup_logging()

def show_error(title, message, error_obj=None):
    """
    Display a friendly error message to the user and ensure it's logged.
    """
    if error_obj:
        logging.error(f"{title}: {message} | Error: {error_obj}", exc_info=(type(error_obj), error_obj, error_obj.__traceback__) if hasattr(error_obj, '__traceback__') else True)
    else:
        logging.error(f"{title}: {message}")
    
    # Show UI dialog
    try:
        messagebox.showerror(title, f"{message}\n\nDetails have been logged." if error_obj else message)
    except Exception:
        # Fallback if UI fails
        print(f"CRITICAL UI ERROR: {title} - {message}", file=sys.stderr)

def global_exception_handler(self, exc, val, tb):
    """
    Global exception handler for Tkinter callbacks.
    Catches unhandled errors, logs them, and shows a friendly dialog.
    """
    logging.critical("Unhandled exception in GUI", exc_info=(exc, val, tb))
    
    title = "Unexpected Error"
    message = "An unexpected error occurred."
    
    # Handle custom exceptions nicely
    if isinstance(val, SoulSenseError):
        title = "Application Error"
        message = str(val)
    elif isinstance(val, tk.TclError):
        title = "Interface Error"
        message = "A graphical interface error occurred."
    
    show_error(title, message)

# Hook into Tkinter's exception reporting
tk.Tk.report_callback_exception = global_exception_handler

# ---------------- SETTINGS ----------------
# Imported from app.utils

# ---------------- BENCHMARK DATA ----------------
# Based on EQ test norms (simulated data for demonstration)
BENCHMARK_DATA = {
    "age_groups": {
        "Under 18": {"avg_score": 28, "std_dev": 6, "sample_size": 1200},
        "18-25": {"avg_score": 32, "std_dev": 7, "sample_size": 2500},
        "26-35": {"avg_score": 34, "std_dev": 6, "sample_size": 3200},
        "36-50": {"avg_score": 36, "std_dev": 5, "sample_size": 2800},
        "51-65": {"avg_score": 38, "std_dev": 4, "sample_size": 1800},
        "65+": {"avg_score": 35, "std_dev": 6, "sample_size": 900}
    },
    "global": {
        "avg_score": 34,
        "std_dev": 6,
        "sample_size": 12500,
        "percentiles": {
            10: 24,
            25: 29,
            50: 34,
            75: 39,
            90: 42
        }
    },
    "professions": {
        "Student": {"avg_score": 31, "std_dev": 7},
        "Professional": {"avg_score": 36, "std_dev": 5},
        "Manager": {"avg_score": 38, "std_dev": 4},
        "Healthcare": {"avg_score": 39, "std_dev": 3},
        "Education": {"avg_score": 37, "std_dev": 4},
        "Technology": {"avg_score": 33, "std_dev": 6},
        "Creative": {"avg_score": 35, "std_dev": 5}
    }
}



# ---------------- LOGGING ----------------
logging.basicConfig(
    filename="logs/soulsense.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

# ---------------- DB INIT ----------------
conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    total_score INTEGER,
    age INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# ---------------- LOAD QUESTIONS FROM DB ----------------
try:
    rows = load_questions()  # [(id, text, tooltip, min_age, max_age)]
    # Store (text, tooltip) tuple
    all_questions = [(q[1], q[2]) for q in rows]
    
    if not all_questions:
        raise ResourceError("Question bank empty: No questions found in database.")

    logging.info("Loaded %s total questions from DB", len(all_questions))

except Exception as e:
    show_error("Fatal Error", "Question bank could not be loaded.\nThe application cannot start.", e)
    sys.exit(1)

# ---------------- GUI ----------------
class SoulSenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Soul Sense EQ Test")
        self.root.geometry("650x550")  # Increased size for benchmarking
        
        # Initialize ML Predictor

        try:
            self.ml_predictor = SoulSenseMLPredictor()
            logging.info("ML Predictor initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize ML Predictor: {e}")
            self.ml_predictor = None

        # Initialize Journal Feature
        self.journal_feature = JournalFeature(self.root)



        # Load settings
        self.settings = load_settings()
        
        # Define color schemes
        self.color_schemes = {
            "light": {
                "bg": "#FFFFFF", # Pure white for max contrast
                "fg": "#000000",
                "button_bg": "#E0E0E0",
                "button_fg": "#000000",
                "entry_bg": "#FFFFFF",
                "entry_fg": "#000000",
                "radiobutton_bg": "#FFFFFF",
                "radiobutton_fg": "#000000",
                "label_bg": "#FFFFFF",
                "label_fg": "#000000",
                "frame_bg": "#FFFFFF",
                "chart_bg": "#FFFFFF",
                "chart_fg": "#000000",
                "improvement_good": "#2E7D32", # Darker green
                "improvement_bad": "#C62828", # Darker red
                "improvement_neutral": "#F9A825", # Darker yellow
                "excellent": "#1565C0", # Darker blue
                "good": "#2E7D32",
                "average": "#EF6C00", # Darker orange
                "needs_work": "#C62828",
                "benchmark_better": "#2E7D32",
                "benchmark_worse": "#C62828",
                "benchmark_same": "#F9A825"
            },
            "dark": {
                "bg": "#121212", # Hard dark
                "fg": "#FFFFFF",
                "button_bg": "#333333",
                "button_fg": "#FFFFFF",
                "entry_bg": "#000000",
                "entry_fg": "#FFFFFF",
                "radiobutton_bg": "#121212",
                "radiobutton_fg": "#FFFFFF",
                "label_bg": "#121212",
                "label_fg": "#FFFFFF",
                "frame_bg": "#121212",
                "chart_bg": "#1E1E1E",
                "chart_fg": "#FFFFFF",
                "improvement_good": "#66BB6A", # Lighter green
                "improvement_bad": "#EF5350", # Lighter red
                "improvement_neutral": "#FFEE58", # Lighter yellow
                "excellent": "#42A5F5", # Lighter blue
                "good": "#66BB6A",
                "average": "#FFA726", # Lighter orange
                "needs_work": "#EF5350",
                "benchmark_better": "#66BB6A",
                "benchmark_worse": "#EF5350",
                "benchmark_same": "#FFEE58"
            }
        }
        
        # Apply theme
        self.apply_theme(self.settings.get("theme", "light"))
        
        # Test variables
        self.username = ""
        self.age = None
        self.age_group = None
        self.profession = None
        
        # Initialize Sentiment Variables
        self.sentiment_score = 0.0 
        self.reflection_text = ""
        
        # Initialize Sentiment Analyzer
        try:
            self.sia = SentimentIntensityAnalyzer()
            logging.info("SentimentIntensityAnalyzer initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize SentimentIntensityAnalyzer: {e}")
            self.sia = None

        self.current_question = 0
        self.responses = []
        self.current_score = 0
        self.current_max_score = 0
        self.current_percentage = 0
        
        # Load questions based on settings
        question_count = self.settings.get("question_count", 10)
        self.questions = all_questions[:min(question_count, len(all_questions))]
        logging.info("Using %s questions based on settings", len(self.questions))
        
        self.create_welcome_screen()

    def apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        self.current_theme = theme_name
        self.colors = self.color_schemes.get(theme_name, self.color_schemes["light"])
        
        # Configure root window
        self.root.configure(bg=self.colors["bg"])
        
        # Configure default widget styles
        self.root.option_add("*Background", self.colors["bg"])
        self.root.option_add("*Foreground", self.colors["fg"])
        self.root.option_add("*Button.Background", self.colors["button_bg"])
        self.root.option_add("*Button.Foreground", self.colors["button_fg"])
        self.root.option_add("*Entry.Background", self.colors["entry_bg"])
        self.root.option_add("*Entry.Foreground", self.colors["entry_fg"])
        self.root.option_add("*Label.Background", self.colors["label_bg"])
        self.root.option_add("*Label.Foreground", self.colors["label_fg"])
        self.root.option_add("*Radiobutton.Background", self.colors["radiobutton_bg"])
        self.root.option_add("*Radiobutton.Foreground", self.colors["radiobutton_fg"])
        self.root.option_add("*Radiobutton.selectColor", self.colors["bg"])
        self.root.option_add("*Frame.Background", self.colors["frame_bg"])

    def toggle_tooltip(self, event, text):
        """Toggle tooltip visibility on click/enter"""
        if hasattr(self, 'tooltip_win') and self.tooltip_win:
            self.tooltip_win.destroy()
            self.tooltip_win = None
            return

        x, y, _, _ = event.widget.bbox("insert")
        x += event.widget.winfo_rootx() + 25
        y += event.widget.winfo_rooty() + 25

        self.tooltip_win = tk.Toplevel(self.root)
        self.tooltip_win.wm_overrideredirect(True)
        self.tooltip_win.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip_win,
            text=text,
            justify='left',
            background="#ffffe0", # Light yellow for tooltip
            foreground="#000000",
            relief='solid',
            borderwidth=1,
            font=("Arial", 10)
        )
        label.pack(ipadx=1)
        
        # Auto-hide after 3 seconds
        self.root.after(3000, lambda: self.tooltip_win.destroy() if hasattr(self, 'tooltip_win') and self.tooltip_win else None)


    def create_widget(self, widget_type, *args, **kwargs):
        """Create a widget with current theme colors"""
        # Override colors if not specified
        if widget_type == tk.Label:
            kwargs.setdefault("bg", self.colors["label_bg"])
            kwargs.setdefault("fg", self.colors["label_fg"])
        elif widget_type == tk.Button:
            kwargs.setdefault("bg", self.colors["button_bg"])
            kwargs.setdefault("fg", self.colors["button_fg"])
            kwargs.setdefault("activebackground", self.darken_color(self.colors["button_bg"]))
            kwargs.setdefault("activeforeground", self.colors["button_fg"])
        elif widget_type == tk.Entry:
            kwargs.setdefault("bg", self.colors["entry_bg"])
            kwargs.setdefault("fg", self.colors["entry_fg"])
            kwargs.setdefault("insertbackground", self.colors["fg"])
        elif widget_type == tk.Radiobutton:
            kwargs.setdefault("bg", self.colors["radiobutton_bg"])
            kwargs.setdefault("fg", self.colors["radiobutton_fg"])
            kwargs.setdefault("selectcolor", self.colors["bg"])
        elif widget_type == tk.Frame:
            kwargs.setdefault("bg", self.colors["frame_bg"])
        
        return widget_type(*args, **kwargs)

    def darken_color(self, color):
        """Darken a color for active button state"""
        if color.startswith("#"):
            # Convert hex to rgb, darken, then back to hex
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            r = max(0, r - 30)
            g = max(0, g - 30)
            b = max(0, b - 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        return color



    def create_welcome_screen(self):
        """Create initial welcome screen with settings option"""
        self.clear_screen()
        
        # Title
        title = self.create_widget(
            tk.Label,
            self.root,
            text="Welcome to Soul Sense EQ Test",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=20)
        
        # Description
        desc = self.create_widget(
            tk.Label,
            self.root,
            text="Assess your Emotional Intelligence\nwith our comprehensive questionnaire",
            font=("Arial", 12)
        )
        desc.pack(pady=10)
        
        # Current settings display
        settings_frame = self.create_widget(tk.Frame, self.root)
        settings_frame.pack(pady=20)
        
        settings_label = self.create_widget(
            tk.Label,
            settings_frame,
            text="Current Settings:",
            font=("Arial", 11, "bold")
        )
        settings_label.pack()
        
        settings_text = self.create_widget(
            tk.Label,
            settings_frame,
            text=f"• Questions: {len(self.questions)}\n" +
                 f"• Theme: {self.settings.get('theme', 'light').title()}\n" +
                 f"• Sound: {'On' if self.settings.get('sound_effects', True) else 'Off'}",
            font=("Arial", 10),
            justify="left"
        )
        settings_text.pack(pady=5)
        
        # Buttons
        button_frame = self.create_widget(tk.Frame, self.root)
        button_frame.pack(pady=20)
        
        start_btn = self.create_widget(
            tk.Button,
            button_frame,
            text="Start Test",
            command=self.create_username_screen,
            font=("Arial", 12),
            width=15
        )
        start_btn.pack(pady=5)
        
        # Journal Button
        journal_btn = self.create_widget(
            tk.Button,
            button_frame,
            text="📖 Daily Journal",
            command=self.open_journal_flow,
            font=("Arial", 12),
            width=15,
            bg="#FFB74D", # Orange accent
            fg="black"
        )
        journal_btn.pack(pady=5)

        # Dashboard Button (NEW)
        dashboard_btn = self.create_widget(
            tk.Button,
            button_frame,
            text="📊 Dashboard",
            command=self.open_dashboard_flow,
            font=("Arial", 12),
            width=15,
            bg="#29B6F6", # Light Blue accent
            fg="black"
        )
        dashboard_btn.pack(pady=5)
        
        # View History button
        history_btn = self.create_widget(
            tk.Button,
            button_frame,
            text="View History",
            command=self.show_history_screen,
            font=("Arial", 12),
            width=15
        )
        history_btn.pack(pady=5)
        
        settings_btn = self.create_widget(
            tk.Button,
            button_frame,
            text="Settings",
            command=self.show_settings,
            font=("Arial", 12),
            width=15
        )
        settings_btn.pack(pady=5)
        
        exit_btn = self.create_widget(
            tk.Button,
            button_frame,
            text="Exit",
            command=self.force_exit,
            font=("Arial", 12),
            width=15
        )
        exit_btn.pack(pady=5)

    def open_journal_flow(self):
        """Handle journal access, prompting for name if needed"""
        if not self.username:
            name = simpledialog.askstring("Journal Access", "Please enter your name to access your journal:", parent=self.root)
            if name and name.strip():
                self.username = name.strip()
            else:
                return
        
        self.journal_feature.open_journal_window(self.username)

    def open_dashboard_flow(self):
        """Handle dashboard access, prompting for name if needed"""
        if not self.username:
            name = simpledialog.askstring("Dashboard Access", "Please enter your name to view your dashboard:", parent=self.root)
            if name and name.strip():
                self.username = name.strip()
            else:
                return
        
        if AnalyticsDashboard:
            dashboard = AnalyticsDashboard(self.root, self.username)
            dashboard.open_dashboard()
        else:
            messagebox.showerror("Error", "Dashboard component could not be loaded")

    def run_bias_check(self):
        """Quick bias check after test completion"""
        try:
            checker = SimpleBiasChecker()
            bias_result = checker.check_age_bias()
            
            if bias_result.get('status') == 'potential_bias':
                # Log bias warning
                logging.warning(f"Potential age bias detected: {bias_result}")
                
                # Optional: Show warning to user
                # messagebox.showwarning("Bias Alert", 
                #     f"Note: Test scores show differences across age groups.\n"
                #     f"Issues: {', '.join(bias_result.get('issues', []))}")
        
        except Exception as e:
            logging.error(f"Bias check failed: {e}")
            
    def show_settings(self):
        """Show settings configuration window"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("400x400")
        
        # Apply theme to settings window
        settings_win.configure(bg=self.colors["bg"])
        
        # Center window
        settings_win.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - settings_win.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - settings_win.winfo_height()) // 2
        settings_win.geometry(f"+{x}+{y}")
        
        # Title
        title = tk.Label(
            settings_win,
            text="Configure Test Settings",
            font=("Arial", 16, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        title.pack(pady=15)
        
        # Question Count
        qcount_frame = tk.Frame(settings_win, bg=self.colors["bg"])
        qcount_frame.pack(pady=10, fill="x", padx=20)
        
        qcount_label = tk.Label(
            qcount_frame,
            text="Number of Questions:",
            font=("Arial", 12),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        qcount_label.pack(anchor="w")
        
        self.qcount_var = tk.IntVar(value=self.settings.get("question_count", 10))
        qcount_spin = tk.Spinbox(
            qcount_frame,
            from_=5,
            to=min(50, len(all_questions)),
            textvariable=self.qcount_var,
            font=("Arial", 12),
            width=10,
            bg=self.colors["entry_bg"],
            fg=self.colors["entry_fg"],
            buttonbackground=self.colors["button_bg"]
        )
        qcount_spin.pack(anchor="w", pady=5)
        
        # Theme Selection
        theme_frame = tk.Frame(settings_win, bg=self.colors["bg"])
        theme_frame.pack(pady=10, fill="x", padx=20)
        
        theme_label = tk.Label(
            theme_frame,
            text="Theme:",
            font=("Arial", 12),
            bg=self.colors["bg"],
            fg=self.colors["fg"]
        )
        theme_label.pack(anchor="w")
        
        self.theme_var = tk.StringVar(value=self.settings.get("theme", "light"))
        
        theme_light = tk.Radiobutton(
            theme_frame,
            text="Light Theme",
            variable=self.theme_var,
            value="light",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            activeforeground=self.colors["fg"]
        )
        theme_light.pack(anchor="w", pady=2)
        
        theme_dark = tk.Radiobutton(
            theme_frame,
            text="Dark Theme",
            variable=self.theme_var,
            value="dark",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            activeforeground=self.colors["fg"]
        )
        theme_dark.pack(anchor="w", pady=2)
        
        # Sound Effects
        sound_frame = tk.Frame(settings_win, bg=self.colors["bg"])
        sound_frame.pack(pady=10, fill="x", padx=20)
        
        self.sound_var = tk.BooleanVar(value=self.settings.get("sound_effects", True))
        sound_cb = tk.Checkbutton(
            sound_frame,
            text="Enable Sound Effects",
            variable=self.sound_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            activebackground=self.colors["bg"],
            activeforeground=self.colors["fg"]
        )
        sound_cb.pack(anchor="w")
        
        # Buttons
        btn_frame = tk.Frame(settings_win, bg=self.colors["bg"])
        btn_frame.pack(pady=20)
        
        def apply_settings():
            """Apply and save settings"""
            new_settings = {
                "question_count": self.qcount_var.get(),
                "theme": self.theme_var.get(),
                "sound_effects": self.sound_var.get()
            }
            
            # Update questions based on new count
            question_count = new_settings["question_count"]
            self.questions = all_questions[:min(question_count, len(all_questions))]
            
            # Save settings
            self.settings.update(new_settings)
            if save_settings(self.settings):
                # Apply theme immediately
                self.apply_theme(new_settings["theme"])
                messagebox.showinfo("Success", "Settings saved successfully!")
                settings_win.destroy()
                # Recreate welcome screen with updated settings
                self.create_welcome_screen()
        
        apply_btn = tk.Button(
            btn_frame,
            text="Apply",
            command=apply_settings,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            width=10,
            activebackground=self.darken_color(self.colors["button_bg"])
        )
        apply_btn.pack(side="left", padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=settings_win.destroy,
            font=("Arial", 12),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            width=10,
            activebackground=self.darken_color(self.colors["button_bg"])
        )
        cancel_btn.pack(side="left", padx=5)
        
        def reset_defaults():
            """Reset to default settings"""
            self.qcount_var.set(DEFAULT_SETTINGS["question_count"])
            self.theme_var.set(DEFAULT_SETTINGS["theme"])
            self.sound_var.set(DEFAULT_SETTINGS["sound_effects"])
        
        reset_btn = tk.Button(
            settings_win,
            text="Reset to Defaults",
            command=reset_defaults,
            font=("Arial", 10),
            bg=self.colors["button_bg"],
            fg=self.colors["button_fg"],
            activebackground=self.darken_color(self.colors["button_bg"])
        )
        reset_btn.pack(pady=10)

    # ---------- ORIGINAL SCREENS (Modified) ----------
    def create_username_screen(self):
        self.clear_screen()
        
        # Username
        self.create_widget(
            tk.Label,
            self.root,
            text="Enter Your Name:",
            font=("Arial", 14)
        ).pack(pady=10)
        
        self.name_entry = self.create_widget(
            tk.Entry,
            self.root,
            font=("Arial", 14)
        )
        self.name_entry.pack(pady=5)

        # Age
        self.create_widget(
            tk.Label,
            self.root,
            text="Enter Your Age (optional):",
            font=("Arial", 14)
        ).pack(pady=5)
        
        self.age_entry = self.create_widget(
            tk.Entry,
            self.root,
            font=("Arial", 14)
        )
        self.age_entry.pack(pady=5)
        self.root.bind("<Return>", self._enter_start)
        
        # Profession (optional, for benchmarking)
        self.create_widget(
            tk.Label,
            self.root,
            text="Your Profession (optional, for benchmarking):",
            font=("Arial", 14)
        ).pack(pady=5)
        
        self.profession_var = tk.StringVar()
        profession_frame = self.create_widget(tk.Frame, self.root)
        profession_frame.pack(pady=5)
        
        professions = ["Student", "Professional", "Manager", "Healthcare", "Education", "Technology", "Creative", "Other"]
        profession_menu = tk.OptionMenu(profession_frame, self.profession_var, *professions)
        profession_menu.config(font=("Arial", 12), bg=self.colors["button_bg"], fg=self.colors["button_fg"])
        profession_menu.pack()

        # Start button
        self.create_widget(
            tk.Button,
            self.root,
            text="Start Test",
            command=self.start_test
        ).pack(pady=15)
        
        # Back button
        self.create_widget(
            tk.Button,
            self.root,
            text="Back to Main",
            command=self.create_welcome_screen
        ).pack(pady=5)

    def validate_name_input(self, name):
        if not name:
            return False, "Please enter your name."
        if not all(c.isalpha() or c.isspace() for c in name):
            return False, "Name must contain only letters and spaces."
        return True, None

    def validate_age_input(self, age_str):
        if age_str == "":
            return True, None, None
        try:
            age = int(age_str)
            if not (1 <= age <= 120):
                return False, None, "Age must be between 1 and 120."
            return True, age, None
        except ValueError:
            return False, None, "Age must be numeric."
    
    def _enter_start(self, event):
        self.start_test()

    def start_test(self):
        # Reset test state completely
        self.current_question = 0
        self.responses = []
        self.current_score = 0
        self.sentiment_score = 0.0
        self.reflection_text = ""
        
        self.username = self.name_entry.get().strip()
        age_str = self.age_entry.get().strip()
        self.profession = self.profession_var.get() if self.profession_var.get() else None

        ok, err = self.validate_name_input(self.username)
        if not ok:
            messagebox.showwarning("Input Error", err)
            return

        ok, age, err = self.validate_age_input(age_str)
        if not ok:
            messagebox.showwarning("Input Error", err)
            return

        self.age = age
        self.age_group = compute_age_group(age)

        logging.info(
            "Session started | user=%s | age=%s | age_group=%s | profession=%s | questions=%s",
            self.username, self.age, self.age_group, self.profession, len(self.questions)
        )

        self.show_question()

    def show_question(self):
        self.clear_screen()

        if self.current_question >= len(self.questions):
            self.finish_test()
            return

        q_data = self.questions[self.current_question]
        # Handle both tuple (new format) and string (legacy safety)
        if isinstance(q_data, tuple):
            q_text = q_data[0]
            q_tooltip = q_data[1]
        else:
            q_text = q_data
            q_tooltip = None

        # Question counter
        self.create_widget(
            tk.Label,
            self.root,
            text=f"Question {self.current_question + 1} of {len(self.questions)}",
            font=("Arial", 12)
        ).pack(pady=5)
        
        q_frame = self.create_widget(tk.Frame, self.root)
        q_frame.pack(pady=20)
        
        self.create_widget(
            tk.Label,
            q_frame,
            text=f"Q{self.current_question + 1}: {q_text}",
            wraplength=400,
            font=("Arial", 12)
        ).pack(side="left")
        
        # Tooltip content
        tooltip_text = q_tooltip if q_tooltip else "Select the option that best describes you.\nThere are no right or wrong answers."

        # Tooltip Icon
        info_btn = tk.Button(
            q_frame,
            text="ℹ️",
            font=("Arial", 12),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            relief="flat",
            command=lambda: None # Placeholder, real action via bind
        )
        info_btn.pack(side="left", padx=5)
        info_btn.bind("<Button-1>", lambda e: self.toggle_tooltip(e, tooltip_text))
        info_btn.bind("<Return>", lambda e: self.toggle_tooltip(e, tooltip_text))

        # Bind Enter to Next
        self.root.bind("<Return>", lambda e: self.save_answer())

        self.answer_var = tk.IntVar()
        
        # Set the default value if we have a previous response for this question
        if self.current_question < len(self.responses):
            self.answer_var.set(self.responses[self.current_question])

        for val, txt in enumerate(["Never", "Sometimes", "Often", "Always"], 1):
            self.create_widget(
                tk.Radiobutton,
                self.root,
                text=f"{txt} ({val})",
                variable=self.answer_var,
                value=val
            ).pack(anchor="w", padx=50)

        # Navigation buttons
        button_frame = self.create_widget(tk.Frame, self.root)
        button_frame.pack(pady=15)
        
        # Always show Previous button except on first question
        if self.current_question > 0:
            self.create_widget(
                tk.Button,
                button_frame,
                text="← Previous",
                command=self.previous_question,
                font=("Arial", 11)
            ).pack(side="left", padx=5)
        
        # Show different text for last question
        if self.current_question == len(self.questions) - 1:
            next_text = "Finish Test"
        else:
            next_text = "Next →"
        
        self.create_widget(
            tk.Button,
            button_frame,
            text=next_text,
            command=self.save_answer,
            font=("Arial", 11)
        ).pack(side="left", padx=5)

    def previous_question(self):
        # Save current answer before moving back
        current_answer = self.answer_var.get()
        if current_answer > 0:  # Only save if an answer was selected
            if self.current_question < len(self.responses):
                # Update existing response
                self.responses[self.current_question] = current_answer
            else:
                # Add new response if it doesn't exist
                self.responses.append(current_answer)
        
        # Move to previous question
        if self.current_question > 0:
            self.current_question -= 1
            self.show_question()

    def save_answer(self):
        ans = self.answer_var.get()
        if ans == 0:
            messagebox.showwarning("Input Error", "Please select an answer.")
            return

        # Save or update the response
        if self.current_question < len(self.responses):
            self.responses[self.current_question] = ans
        else:
            self.responses.append(ans)
        
        # Save individual response
        conn = get_connection()
        cursor = conn.cursor()

        qid = self.current_question + 1
        ts = datetime.utcnow().isoformat()

        try:
            cursor.execute(
                """
                INSERT INTO responses
                (username, question_id, response_value, age_group, timestamp)
                VALUES (?, ?, ?, ?, ?)
                """,
                (self.username, qid, ans, self.age_group, ts)
            )
            conn.commit()
        except Exception:
            logging.error("Failed to store response", exc_info=True)

        self.current_question += 1
        
        if self.current_question >= len(self.questions):
            self.show_reflection_screen()
        else:
            self.show_question()

    def finish_test(self):
        self.current_score = sum(self.responses)
        self.current_max_score = len(self.responses) * 4
        self.current_percentage = (self.current_score / self.current_max_score) * 100 if self.current_max_score > 0 else 0
        
        conn = get_connection() # Get clean session
        cursor = conn.cursor() # Get cursor explicitly
        
        try:
            # Save to Database with new columns
            cursor.execute(
                "INSERT INTO scores (username, age, total_score, sentiment_score, reflection_text, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
                (self.username, self.age, self.current_score, self.sentiment_score, self.reflection_text, datetime.utcnow().isoformat())
            )
            conn.commit()
        except Exception:
            logging.error("Failed to store final score", exc_info=True)


        # Run bias check
        # self.run_bias_check()  # TODO: Implement bias check
        
        self.show_visual_results()

    def show_reflection_screen(self):
        """Show the open-ended reflection question"""
        self.clear_screen()
        
        # Header
        self.create_widget(
            tk.Label, 
            self.root, 
            text="Final Reflection", 
            font=("Arial", 24, "bold")
        ).pack(pady=20)
        
        self.create_widget(
            tk.Label, 
            self.root, 
            text="Describe a recent situation where you felt challenged emotionally.\nHow did you handle it?", 
            font=("Arial", 14),
            wraplength=600
        ).pack(pady=10)
        
        # Text Area
        self.reflection_entry = tk.Text(self.root, height=10, width=60, font=("Arial", 12))
        self.reflection_entry.pack(pady=20, padx=20)
        
        # Submit Button
        self.create_widget(
            tk.Button,
            self.root,
            text="Submit & See Results",
            command=self.submit_reflection,
            font=("Arial", 14, "bold")
        ).pack(pady=20)
        
    def submit_reflection(self):
        """Analyze reflection and finish test"""
        text = self.reflection_entry.get("1.0", tk.END).strip()
        
        if not text:
            if not messagebox.askyesno("Skip?", "You haven't written anything. Do you want to skip?"):
                return
            self.sentiment_score = 0.0
            self.reflection_text = ""
        else:
            self.reflection_text = text
            # Analyze sentiment
            try:
                scores = self.sia.polarity_scores(text)
                # Convert compound (-1 to 1) to -100 to 100
                self.sentiment_score = scores['compound'] * 100
            except Exception as e:
                logging.error(f"Error analyzing sentiment: {e}")
                self.sentiment_score = 0.0
        
        self.finish_test()



    # ---------- BENCHMARKING FUNCTIONS ----------
    def calculate_percentile(self, score, avg_score, std_dev):
        """Calculate percentile based on normal distribution"""
        if std_dev == 0:
            return 50 if score == avg_score else (100 if score > avg_score else 0)
        
        # Z-score calculation
        z_score = (score - avg_score) / std_dev
        
        # Convert Z-score to percentile (simplified approximation)
        # This is a simplified version - in production you'd use proper statistical functions
        if z_score <= -2.5:
            percentile = 1
        elif z_score <= -2.0:
            percentile = 2
        elif z_score <= -1.5:
            percentile = 7
        elif z_score <= -1.0:
            percentile = 16
        elif z_score <= -0.5:
            percentile = 31
        elif z_score <= 0:
            percentile = 50
        elif z_score <= 0.5:
            percentile = 69
        elif z_score <= 1.0:
            percentile = 84
        elif z_score <= 1.5:
            percentile = 93
        elif z_score <= 2.0:
            percentile = 98
        elif z_score <= 2.5:
            percentile = 99
        else:
            percentile = 99.5
            
        return percentile

    def get_benchmark_comparison(self):
        """Get benchmark comparisons for the current score"""
        comparisons = {}
        
        # Global comparison
        global_bench = BENCHMARK_DATA["global"]
        comparisons["global"] = {
            "your_score": self.current_score,
            "avg_score": global_bench["avg_score"],
            "difference": self.current_score - global_bench["avg_score"],
            "percentile": self.calculate_percentile(self.current_score, global_bench["avg_score"], global_bench["std_dev"]),
            "sample_size": global_bench["sample_size"]
        }
        
        # Age group comparison
        if self.age_group and self.age_group in BENCHMARK_DATA["age_groups"]:
            age_bench = BENCHMARK_DATA["age_groups"][self.age_group]
            comparisons["age_group"] = {
                "group": self.age_group,
                "your_score": self.current_score,
                "avg_score": age_bench["avg_score"],
                "difference": self.current_score - age_bench["avg_score"],
                "percentile": self.calculate_percentile(self.current_score, age_bench["avg_score"], age_bench["std_dev"]),
                "sample_size": age_bench["sample_size"]
            }
        
        # Profession comparison
        if self.profession and self.profession in BENCHMARK_DATA["professions"]:
            prof_bench = BENCHMARK_DATA["professions"][self.profession]
            comparisons["profession"] = {
                "profession": self.profession,
                "your_score": self.current_score,
                "avg_score": prof_bench["avg_score"],
                "difference": self.current_score - prof_bench["avg_score"],
                "percentile": self.calculate_percentile(self.current_score, prof_bench["avg_score"], prof_bench["std_dev"])
            }
        
        return comparisons

    def get_benchmark_interpretation(self, comparisons):
        """Get interpretation text based on benchmark comparisons"""
        interpretations = []
        
        if "global" in comparisons:
            comp = comparisons["global"]
            if comp["difference"] > 5:
                interpretations.append(f"Your score is significantly higher than the global average ({comp['avg_score']}).")
            elif comp["difference"] > 2:
                interpretations.append(f"Your score is above the global average ({comp['avg_score']}).")
            elif comp["difference"] < -5:
                interpretations.append(f"Your score is significantly lower than the global average ({comp['avg_score']}).")
            elif comp["difference"] < -2:
                interpretations.append(f"Your score is below the global average ({comp['avg_score']}).")
            else:
                interpretations.append(f"Your score is close to the global average ({comp['avg_score']}).")
            
            interpretations.append(f"You scored higher than {comp['percentile']:.1f}% of test-takers globally.")
        
        if "age_group" in comparisons:
            comp = comparisons["age_group"]
            if comp["difference"] > 0:
                interpretations.append(f"You scored above average for your age group ({comp['group']}).")
            elif comp["difference"] < 0:
                interpretations.append(f"You scored below average for your age group ({comp['group']}).")
            else:
                interpretations.append(f"You scored average for your age group ({comp['group']}).")
            
            interpretations.append(f"You're in the {comp['percentile']:.0f}th percentile for your age group.")
        
        if "profession" in comparisons:
            comp = comparisons["profession"]
            if comp["difference"] > 0:
                interpretations.append(f"You scored above average for {comp['profession']} professionals.")
            elif comp["difference"] < 0:
                interpretations.append(f"You scored below average for {comp['profession']} professionals.")
            else:
                interpretations.append(f"You scored average for {comp['profession']} professionals.")
        
        return interpretations

    def create_benchmark_chart(self, parent, comparisons):
        """Create a visual benchmark comparison chart"""
        chart_frame = self.create_widget(tk.Frame, parent)
        chart_frame.pack(fill="x", pady=10)
        
        self.create_widget(
            tk.Label,
            chart_frame,
            text="Benchmark Comparison",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", pady=5)
        
        # Create canvas for benchmark bars
        chart_canvas = tk.Canvas(chart_frame, height=150, bg=self.colors["chart_bg"], highlightthickness=0)
        chart_canvas.pack(fill="x", pady=10)
        
        # Prepare data for chart
        chart_data = []
        if "global" in comparisons:
            chart_data.append(("Global", comparisons["global"]))
        if "age_group" in comparisons:
            chart_data.append((comparisons["age_group"]["group"], comparisons["age_group"]))
        if "profession" in comparisons:
            chart_data.append((comparisons["profession"]["profession"], comparisons["profession"]))
        
        if not chart_data:
            return chart_frame
        
        # Calculate chart dimensions
        num_bars = len(chart_data)
        chart_width = 500
        bar_width = 80
        spacing = 30
        start_x = 100
        max_score = max([max(d["your_score"], d["avg_score"]) for _, d in chart_data])
        scale_factor = 100 / max(1, max_score)
        
        # Draw bars for each comparison
        for i, (label, data) in enumerate(chart_data):
            x = start_x + i * (bar_width + spacing)
            
            # Your score bar
            your_height = data["your_score"] * scale_factor
            y_your = 130 - your_height
            your_color = self.colors["benchmark_better"] if data["difference"] > 0 else self.colors["benchmark_worse"] if data["difference"] < 0 else self.colors["benchmark_same"]
            
            chart_canvas.create_rectangle(x, y_your, x + bar_width/2, 130, 
                                         fill=your_color, outline="black")
            chart_canvas.create_text(x + bar_width/4, y_your - 10, 
                                    text=f"You: {data['your_score']}", 
                                    fill=self.colors["chart_fg"], font=("Arial", 8, "bold"))
            
            # Average score bar
            avg_height = data["avg_score"] * scale_factor
            y_avg = 130 - avg_height
            
            chart_canvas.create_rectangle(x + bar_width/2, y_avg, x + bar_width, 130, 
                                         fill="#888888", outline="black")
            chart_canvas.create_text(x + bar_width * 0.75, y_avg - 10, 
                                    text=f"Avg: {data['avg_score']}", 
                                    fill=self.colors["chart_fg"], font=("Arial", 8, "bold"))
            
            # Label
            chart_canvas.create_text(x + bar_width/2, 145, text=label, 
                                    fill=self.colors["chart_fg"], font=("Arial", 9))
            
            # Difference indicator
            diff = data["difference"]
            if diff != 0:
                diff_text = f"{'+' if diff > 0 else ''}{diff:.1f}"
                diff_color = self.colors["benchmark_better"] if diff > 0 else self.colors["benchmark_worse"]
                chart_canvas.create_text(x + bar_width/2, y_your - 25, text=diff_text, 
                                        fill=diff_color, font=("Arial", 9, "bold"))
        
        # Y-axis labels
        for score in [0, max_score//2, max_score]:
            y = 130 - (score * scale_factor)
            chart_canvas.create_text(80, y, text=str(score), fill=self.colors["chart_fg"], font=("Arial", 8))
        
        chart_canvas.create_text(50, 65, text="Score", fill=self.colors["chart_fg"], angle=90)
        
        # Legend
        legend_frame = self.create_widget(tk.Frame, chart_frame)
        legend_frame.pack(pady=5)
        
        # Your score legend
        your_legend = tk.Canvas(legend_frame, width=20, height=20, bg=self.colors["chart_bg"], highlightthickness=0)
        your_legend.create_rectangle(0, 0, 20, 20, fill=self.colors["benchmark_better"], outline="black")
        your_legend.pack(side="left", padx=5)
        tk.Label(legend_frame, text="Your Score", bg=self.colors["chart_bg"], fg=self.colors["chart_fg"]).pack(side="left", padx=5)
        
        # Average score legend
        avg_legend = tk.Canvas(legend_frame, width=20, height=20, bg=self.colors["chart_bg"], highlightthickness=0)
        avg_legend.create_rectangle(0, 0, 20, 20, fill="#888888", outline="black")
        avg_legend.pack(side="left", padx=20)
        tk.Label(legend_frame, text="Average Score", bg=self.colors["chart_bg"], fg=self.colors["chart_fg"]).pack(side="left", padx=5)
        
        return chart_frame

    def show_visual_results(self):
        """Show visual results with charts and graphs"""
        self.clear_screen()
        
        # Get benchmark comparisons
        comparisons = self.get_benchmark_comparison()
        benchmark_interpretations = self.get_benchmark_interpretation(comparisons)
        
        # Create scrollable frame for results
        canvas = tk.Canvas(self.root, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = self.create_widget(tk.Frame, canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Header
        header_frame = self.create_widget(tk.Frame, scrollable_frame)
        header_frame.pack(fill="x", pady=10, padx=20)
        
        self.create_widget(
            tk.Label,
            header_frame,
            text=f"Test Results for {self.username}",
            font=("Arial", 22, "bold")
        ).pack()
        
        # Score Summary
        summary_frame = self.create_widget(tk.Frame, scrollable_frame)
        summary_frame.pack(fill="x", pady=20, padx=20)
        
        # Create visual score display
        score_display_frame = self.create_widget(tk.Frame, summary_frame)
        score_display_frame.pack(pady=10)
        
        # Large score display
        score_text = f"{self.current_score}/{self.current_max_score}"
        score_label = self.create_widget(
            tk.Label,
            score_display_frame,
            text=score_text,
            font=("Arial", 36, "bold")
        )
        score_label.pack()
        
        # Percentage display
        percentage_text = f"{self.current_percentage:.1f}%"
        percentage_label = self.create_widget(
            tk.Label,
            score_display_frame,
            text=percentage_text,
            font=("Arial", 24)
        )
        percentage_label.pack()
        
        # Sentiment Score display (if available)
        if hasattr(self, 'sentiment_score') and self.sentiment_score is not None:
            sentiment_frame = self.create_widget(tk.Frame, score_display_frame)
            sentiment_frame.pack(pady=10)
            
            # Sentiment label
            self.create_widget(
                tk.Label,
                sentiment_frame,
                text="Emotional Sentiment:",
                font=("Arial", 12, "bold")
            ).pack()
            
            # Sentiment score with color coding
            if self.sentiment_score < -20:
                sentiment_color = "#D32F2F"  # Red for negative
                sentiment_label_text = "Negative"
            elif self.sentiment_score > 20:
                sentiment_color = "#388E3C"  # Green for positive
                sentiment_label_text = "Positive"
            else:
                sentiment_color = "#FBC02D"  # Yellow for neutral
                sentiment_label_text = "Neutral"
            
            sentiment_score_label = self.create_widget(
                tk.Label,
                sentiment_frame,
                text=f"{self.sentiment_score:+.1f} ({sentiment_label_text})",
                font=("Arial", 18, "bold"),
                fg=sentiment_color
            )
            sentiment_score_label.pack()
            
            # Sentiment explanation
            sentiment_desc = ""
            if self.sentiment_score < -60:
                sentiment_desc = "Your reflection shows significant distress"
            elif self.sentiment_score < -20:
                sentiment_desc = "Your reflection indicates some negative emotion"
            elif self.sentiment_score > 60:
                sentiment_desc = "Your reflection shows strong positive emotion"
            elif self.sentiment_score > 20:
                sentiment_desc = "Your reflection indicates positive feelings"
            else:
                sentiment_desc = "Your reflection shows balanced emotions"
            
            self.create_widget(
                tk.Label,
                sentiment_frame,
                text=sentiment_desc,
                font=("Arial", 10),
                fg=self.colors["fg"]
            ).pack()
        
        
        # Progress bar visualization
        progress_frame = self.create_widget(tk.Frame, summary_frame)
        progress_frame.pack(pady=20)
        
        self.create_widget(
            tk.Label,
            progress_frame,
            text="Your EQ Score Progress:",
            font=("Arial", 12, "bold")
        ).pack(pady=5)
        
        # Create progress bar canvas
        progress_canvas = tk.Canvas(progress_frame, width=400, height=30, bg=self.colors["bg"], highlightthickness=0)
        progress_canvas.pack()
        
        # Draw progress bar
        progress_width = 400
        fill_width = (self.current_percentage / 100) * progress_width
        
        # Determine color based on score
        if self.current_percentage >= 80:
            bar_color = self.colors["excellent"]
            level = "Excellent"
        elif self.current_percentage >= 65:
            bar_color = self.colors["good"]
            level = "Good"
        elif self.current_percentage >= 50:
            bar_color = self.colors["average"]
            level = "Average"
        else:
            bar_color = self.colors["needs_work"]
            level = "Needs Work"
        
        # Draw background
        progress_canvas.create_rectangle(0, 0, progress_width, 30, fill="#e0e0e0", outline="")
        # Draw fill
        progress_canvas.create_rectangle(0, 0, fill_width, 30, fill=bar_color, outline="")
        # Draw text
        progress_canvas.create_text(progress_width/2, 15, text=f"{level} - {self.current_percentage:.1f}%", 
                                  fill="white" if self.current_percentage > 50 else "black",
                                  font=("Arial", 10, "bold"))
        
        # Score markers
        markers_frame = self.create_widget(tk.Frame, progress_frame)
        markers_frame.pack(fill="x", pady=5)
        
        for i in range(0, 101, 25):
            marker_label = self.create_widget(
                tk.Label,
                markers_frame,
                text=f"{i}%",
                font=("Arial", 8)
            )
            marker_label.pack(side="left", expand=True)
        
        # --- SENTIMENT ANALYSIS DISPLAY ---
        sentiment_frame = self.create_widget(tk.Frame, summary_frame)
        sentiment_frame.pack(fill="x", pady=20, padx=20)
        
        self.create_widget(
            tk.Label,
            sentiment_frame,
            text="Emotional Sentiment:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w")
        
        # Color coding
        if self.sentiment_score > 20:
            s_color = "green"
            s_text = "Positive Outlook"
        elif self.sentiment_score < -20:
            s_color = "red"
            s_text = "Negative Emotion"
        else:
            s_color = "#FFC107" # Amber
            s_text = "Neutral/Balanced"
            
        self.create_widget(
            tk.Label,
            sentiment_frame,
            text=f"{self.sentiment_score:+.1f} ({s_text})",
            font=("Arial", 18, "bold"),
            fg=s_color
        ).pack(anchor="w", pady=5)
        
        # Description
        if self.sentiment_score < -60:
            desc = "Your reflection shows significant distress."
        elif self.sentiment_score < -20:
            desc = "Your reflection indicates some negative emotion."
        elif self.sentiment_score > 60:
            desc = "Your reflection shows strong positive emotion!"
        elif self.sentiment_score > 20:
            desc = "Your reflection indicates positive feelings."
        else:
            desc = "Your reflection shows balanced emotions."
            
        self.create_widget(
            tk.Label,
            sentiment_frame,
            text=desc,
            font=("Arial", 11, "italic"),
            wraplength=400
        ).pack(anchor="w")
        # ----------------------------------
        
        # BENCHMARK SECTION
        benchmark_frame = self.create_widget(tk.Frame, scrollable_frame)
        benchmark_frame.pack(fill="x", pady=20, padx=20)
        
        self.create_widget(
            tk.Label,
            benchmark_frame,
            text="Benchmark Analysis",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=10)
        
        # Benchmark interpretations
        if benchmark_interpretations:
            interpretation_frame = self.create_widget(tk.Frame, benchmark_frame)
            interpretation_frame.pack(fill="x", pady=10)
            
            for interpretation in benchmark_interpretations:
                self.create_widget(
                    tk.Label,
                    interpretation_frame,
                    text=f"• {interpretation}",
                    font=("Arial", 10),
                    anchor="w"
                ).pack(anchor="w", pady=2)
        
        # Benchmark chart
        if comparisons:
            self.create_benchmark_chart(benchmark_frame, comparisons)
        
        # Detailed benchmark stats
        if "global" in comparisons:
            stats_frame = self.create_widget(tk.Frame, benchmark_frame)
            stats_frame.pack(fill="x", pady=10)
            
            comp = comparisons["global"]
            stats_text = f"""
            Global Comparison:
            • Your Score: {comp['your_score']}
            • Global Average: {comp['avg_score']} (based on {comp['sample_size']:,} people)
            • Difference: {comp['difference']:+.1f}
            • Percentile Rank: {comp['percentile']:.1f}th percentile
            """
            
            self.create_widget(
                tk.Label,
                stats_frame,
                text=stats_text.strip(),
                font=("Arial", 10),
                justify="left",
                anchor="w"
            ).pack(anchor="w")
        
        # EQ Category Analysis (simulated)
        categories_frame = self.create_widget(tk.Frame, scrollable_frame)
        categories_frame.pack(fill="x", pady=20, padx=20)
        
        self.create_widget(
            tk.Label,
            categories_frame,
            text="EQ Category Analysis",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=10)
        
        categories = ["Self-Awareness", "Self-Regulation", "Motivation", "Empathy", "Social Skills"]
        for category in categories:
            cat_frame = self.create_widget(tk.Frame, categories_frame)
            cat_frame.pack(fill="x", pady=2)
            
            self.create_widget(
                tk.Label,
                cat_frame,
                text=category,
                font=("Arial", 10),
                width=15,
                anchor="w"
            ).pack(side="left")
            
            # Simulated category score
            cat_score = min(100, self.current_percentage + random.uniform(-10, 10))
            cat_canvas = tk.Canvas(cat_frame, width=200, height=15, bg=self.colors["bg"], highlightthickness=0)
            cat_canvas.pack(side="left", padx=10)
            
            cat_fill_width = (cat_score / 100) * 200
            cat_color = self.colors["good"] if cat_score >= 70 else self.colors["average"] if cat_score >= 50 else self.colors["needs_work"]
            
            cat_canvas.create_rectangle(0, 0, 200, 15, fill="#e0e0e0", outline="")
            cat_canvas.create_rectangle(0, 0, cat_fill_width, 15, fill=cat_color, outline="")
            cat_canvas.create_text(100, 7, text=f"{cat_score:.0f}%", fill="white" if cat_score > 50 else "black", font=("Arial", 8))
        
        # Test summary
        summary_text_frame = self.create_widget(tk.Frame, scrollable_frame)
        summary_text_frame.pack(fill="x", pady=20, padx=20)
        
        summary_text = f"""
        Test Summary:
        • Questions Answered: {len(self.responses)}/{len(self.questions)}
        • Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        • Age Group: {self.age_group if self.age_group else 'Not specified'}
        • Profession: {self.profession if self.profession else 'Not specified'}
        • Average Response: {self.current_score/len(self.responses):.1f} out of 4
        """
        
        self.create_widget(
            tk.Label,
            summary_text_frame,
            text=summary_text.strip(),
            font=("Arial", 10),
            justify="left",
            anchor="w"
        ).pack(anchor="w")
        
        # Buttons frame
        button_frame = self.create_widget(tk.Frame, scrollable_frame)
        button_frame.pack(pady=20, padx=20)
        
        button_frame.pack(pady=20, padx=20)
        
        # Grid Layout for Buttons
        # Row 0: AI Analysis (Center, Prominent)
        if self.ml_predictor:
            btn_ai = tk.Button(
                button_frame,
                text="🤖 AI Analysis",
                command=self.show_ml_analysis,
                font=("Segoe UI", 12, "bold"),
                bg="#1976D2",
                fg="white",
                activebackground="#1565C0",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=20,
                pady=8
            )
            btn_ai.grid(row=0, column=0, columnspan=2, pady=(0, 15))
            
            def on_enter(e): btn_ai['bg'] = "#2196F3"
            def on_leave(e): btn_ai['bg'] = "#1976D2"
            btn_ai.bind("<Enter>", on_enter)
            btn_ai.bind("<Leave>", on_leave)

        # Row 1: Comparison & History
        row1_frame = tk.Frame(button_frame)
        row1_frame.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Check if user has previous attempts
        cursor.execute(
            "SELECT COUNT(*) FROM scores WHERE username = ?",
            (self.username,)
        )
        previous_count = cursor.fetchone()[0]
        
        if previous_count > 1:
            self.create_widget(
                tk.Button,
                row1_frame,
                text="Compare Previous",
                command=self.show_comparison_screen,
                font=("Arial", 11),
                width=16
            ).pack(side="left", padx=5)
        
        self.create_widget(
            tk.Button,
            row1_frame,
            text="View History",
            command=self.show_history_screen,
            font=("Arial", 11),
            width=16
        ).pack(side="left", padx=5)
        
        # Row 2: Standard Actions
        row2_frame = tk.Frame(button_frame)
        row2_frame.grid(row=2, column=0, columnspan=2, pady=5)

        self.create_widget(
            tk.Button,
            row2_frame,
            text="Take Another",
            command=self.reset_test,
            font=("Arial", 11),
            width=16
        ).pack(side="left", padx=5)
        
        self.create_widget(
            tk.Button,
            row2_frame,
            text="Main Menu",
            command=self.create_welcome_screen,
            font=("Arial", 11),
            width=16
        ).pack(side="left", padx=5)
        
        # Pack canvas and scrollbar (unchanged)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_ml_analysis(self):
        """Show AI-powered analysis in a popup window"""
        if not self.ml_predictor:
            messagebox.showerror("Error", "AI Model not loaded.")
            return
            
        try:
            # 1. Get Prediction
            result = self.ml_predictor.predict_with_explanation(
                self.responses,
                self.age,
                self.current_score,
                sentiment_score=self.sentiment_score
            )
            
            # 2. Create Layout
            popup = tk.Toplevel(self.root)
            popup.title("🤖 SoulSense AI Analysis")
            popup.geometry("650x750")
            popup.configure(bg="#F5F5F5")

            # Main Scrollable Frame
            canvas = tk.Canvas(popup, bg="#F5F5F5")
            scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg="#F5F5F5")

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            # --- CARD 1: OVERVIEW ---
            risk_color = "#D32F2F" if result['prediction'] == 2 else "#FBC02D" if result['prediction'] == 1 else "#388E3C"
            bg_color = "#FFEBEE" if result['prediction'] == 2 else "#FFFDE7" if result['prediction'] == 1 else "#E8F5E9"
            
            card1 = tk.Frame(scrollable_frame, bg="white", bd=1, relief="solid")
            card1.pack(fill="x", padx=20, pady=10)
            
            # Header
            header_frame = tk.Frame(card1, bg=risk_color, height=80)
            header_frame.pack(fill="x")
            
            tk.Label(
                header_frame, 
                text=result['prediction_label'].upper(), 
                font=("Arial", 18, "bold"),
                bg=risk_color,
                fg="white"
            ).pack(pady=10)
            
            tk.Label(
                header_frame,
                text=f"Confidence: {result['confidence']:.1%}",
                font=("Arial", 12),
                bg=risk_color,
                fg="white"
            ).pack(pady=(0, 10))

            tk.Label(
                card1, 
                text="Based on your inputs, the AI model suggests:", 
                font=("Arial", 11, "italic"),
                bg="white",
                fg="#555"
            ).pack(pady=15)

            # --- CARD 2: ACTION PLAN ---
            tk.Label(scrollable_frame, text="✅ RECOMMENDED ACTIONS", font=("Arial", 14, "bold"), bg="#F5F5F5", fg="#333").pack(anchor="w", padx=25, pady=(15,5))
            
            card2 = tk.Frame(scrollable_frame, bg="white", bd=0, highlightbackground="#ddd", highlightthickness=1)
            card2.pack(fill="x", padx=20)

            if 'recommendations' in result and result['recommendations']:
                for tip in result['recommendations']:
                    row = tk.Frame(card2, bg="white")
                    row.pack(fill="x", pady=10, padx=15)
                    
                    tk.Label(row, text="🔹", font=("Arial", 12), bg="white", fg=risk_color).pack(side="left", anchor="n")
                    tk.Label(
                        row, 
                        text=tip, 
                        font=("Arial", 11), 
                        bg="white", 
                        fg="#333", 
                        wraplength=500, 
                        justify="left"
                    ).pack(side="left", padx=10)
            else:
                tk.Label(card2, text="No specific recommendations available.", bg="white").pack(pady=20)

            # --- CARD 3: TOP FACTORS ---
            tk.Label(scrollable_frame, text="🔍 INFLUENCING FACTORS", font=("Arial", 14, "bold"), bg="#F5F5F5", fg="#333").pack(anchor="w", padx=25, pady=(20,5))
            
            card3 = tk.Frame(scrollable_frame, bg="white", bd=0, highlightbackground="#ddd", highlightthickness=1)
            card3.pack(fill="x", padx=20, pady=10)

            card3.pack(fill="x", padx=20, pady=10)

            # Filter out non-5-point scale features for clean visualization
            visual_features = {k: v for k, v in result['features'].items() 
                             if k not in ['total_score', 'age', 'average_score']}
            
            sorted_features = sorted(visual_features.items(), key=lambda x: result['feature_importance'].get(x[0], 0), reverse=True)[:3]
            
            for feature, value in sorted_features:
                imp = result['feature_importance'].get(feature, 0)
                f_name = feature.replace('_', ' ').title()
                
                f_row = tk.Frame(card3, bg="white")
                f_row.pack(fill="x", pady=8, padx=15)
                
                # Label Row (Name + Value)
                label_row = tk.Frame(f_row, bg="white")
                label_row.pack(fill="x", pady=(0, 2))
                
                tk.Label(
                    label_row, 
                    text=f_name, 
                    font=("Segoe UI", 11, "bold"), 
                    bg="white", 
                    fg="#444"
                ).pack(side="left")
                
                # Format Score
                if feature == 'sentiment_score':
                    score_text = f"{value:+.1f}"
                elif feature == 'total_score':
                    score_text = f"{value/25*100:.0f}/100"
                else:
                    # Assume 5-point scale
                    score_text = f"{value*20:.0f}/100"
                
                tk.Label(
                    label_row, 
                    text=score_text, 
                    font=("Segoe UI", 11, "bold"), 
                    bg="white", 
                    fg="#666"
                ).pack(side="right")
                
                # Progress Bar
                bar_bg = tk.Frame(f_row, bg="#F0F2F5", height=12, width=400)
                bar_bg.pack(fill="x", pady=2)
                bar_bg.pack_propagate(False)
                
                fill_width = int(520 * imp * 3.5) # Scale to available width
                # Note: fill_width is relative to parent, simplified here as frame width isn't fixed yet
                # We use a fractional width approach or fixed max
                
                tk.Frame(
                    bar_bg, 
                    bg="#4CAF50" if imp < 0.1 else "#2196F3" if imp < 0.3 else "#FF9800", # Color by impact
                    height=12, 
                    width=fill_width
                ).pack(side="left")

            # Close Button
            btn_close = tk.Button(
                scrollable_frame,
                text="Close Analysis",
                command=popup.destroy,
                font=("Segoe UI", 12, "bold"),
                bg="#546E7A", # Blue Grey
                fg="white", 
                activebackground="#455A64",
                activeforeground="white",
                relief="flat",
                cursor="hand2",
                width=20,
                pady=10
            )
            btn_close.pack(pady=30)
            
            # Hover for close
            btn_close.bind("<Enter>", lambda e: btn_close.configure(bg="#455A64"))
            btn_close.bind("<Leave>", lambda e: btn_close.configure(bg="#546E7A"))
            
        except Exception as e:
            logging.error("AI Analysis failed", exc_info=True)
            messagebox.showerror("Analysis Error", f"Could not generate AI report.\n{e}")

    def show_history_screen(self):
        """Show history of all tests for the current user"""
        self.clear_screen()
        
        # Header with back button
        header_frame = self.create_widget(tk.Frame, self.root)
        header_frame.pack(pady=10, fill="x")
        
        self.create_widget(
            tk.Button,
            header_frame,
            text="← Back",
            command=self.create_welcome_screen,
            font=("Arial", 10)
        ).pack(side="left", padx=10)
        
        self.create_widget(
            tk.Label,
            header_frame,
            text="Test History" + (f" for {self.username}" if self.username else ""),
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=50)
        
        # Get history data
        if not self.username:
            cursor.execute(
                """
                SELECT DISTINCT username FROM scores 
                ORDER BY timestamp DESC 
                LIMIT 5
                """
            )
            users = cursor.fetchall()
            
            if not users:
                self.create_widget(
                    tk.Label,
                    self.root,
                    text="No test history found. Please take a test first.",
                    font=("Arial", 12)
                ).pack(pady=50)
                
                self.create_widget(
                    tk.Button,
                    self.root,
                    text="Back to Main",
                    command=self.create_welcome_screen,
                    font=("Arial", 12)
                ).pack(pady=20)
                return
            
            # Show user selection
            user_frame = self.create_widget(tk.Frame, self.root)
            user_frame.pack(pady=20)
            
            self.create_widget(
                tk.Label,
                user_frame,
                text="Select a user to view their history:",
                font=("Arial", 12)
            ).pack(pady=10)
            
            for user in users:
                username = user[0]
                user_btn = self.create_widget(
                    tk.Button,
                    user_frame,
                    text=username,
                    command=lambda u=username: self.view_user_history(u),
                    font=("Arial", 12),
                    width=20
                )
                user_btn.pack(pady=5)
            
            return
        
        # If username is set, show that user's history
        self.display_user_history(self.username)

    def view_user_history(self, username):
        """View history for a specific user"""
        self.username = username
        self.display_user_history(username)

    def display_user_history(self, username):
        """Display history for a specific user"""
        self.clear_screen()
        
        # Get history data
        cursor.execute(
            """
            SELECT id, total_score, age, timestamp 
            FROM scores 
            WHERE username = ? 
            ORDER BY timestamp DESC
            """,
            (username,)
        )
        history = cursor.fetchall()
        
        # Header with back button
        header_frame = self.create_widget(tk.Frame, self.root)
        header_frame.pack(pady=10, fill="x")
        
        self.create_widget(
            tk.Button,
            header_frame,
            text="← Back",
            command=self.show_history_screen,
            font=("Arial", 10)
        ).pack(side="left", padx=10)
        
        self.create_widget(
            tk.Label,
            header_frame,
            text=f"Test History for {username}",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=50)
        
        if not history:
            self.create_widget(
                tk.Label,
                self.root,
                text="No test history found.",
                font=("Arial", 12)
            ).pack(pady=50)
            
            self.create_widget(
                tk.Button,
                self.root,
                text="Back to History",
                command=self.show_history_screen,
                font=("Arial", 12)
            ).pack(pady=20)
            return
        
        # Create scrollable frame for history
        canvas = tk.Canvas(self.root, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = self.create_widget(tk.Frame, canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Display each test result
        for idx, (test_id, score, age, timestamp) in enumerate(history):
            # Calculate percentage (assuming 4 points per question)
            max_score = len(self.questions) * 4
            percentage = (score / max_score) * 100 if max_score > 0 else 0
            
            test_frame = self.create_widget(tk.Frame, scrollable_frame, relief="groove", borderwidth=2)
            test_frame.pack(fill="x", padx=20, pady=5)
            
            # Format date
            try:
                date_str = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
            except:
                date_str = str(timestamp)
            
            # Test info
            info_frame = self.create_widget(tk.Frame, test_frame)
            info_frame.pack(fill="x", padx=10, pady=5)
            
            self.create_widget(
                tk.Label,
                info_frame,
                text=f"Test #{test_id}",
                font=("Arial", 11, "bold"),
                anchor="w"
            ).pack(side="left", padx=5)
            
            self.create_widget(
                tk.Label,
                info_frame,
                text=f"Score: {score}/{max_score} ({percentage:.1f}%)",
                font=("Arial", 10),
                anchor="w"
            ).pack(side="left", padx=20)
            
            if age:
                self.create_widget(
                    tk.Label,
                    info_frame,
                    text=f"Age: {age}",
                    font=("Arial", 10),
                    anchor="w"
                ).pack(side="left", padx=20)
            
            self.create_widget(
                tk.Label,
                info_frame,
                text=date_str,
                font=("Arial", 9),
                anchor="w"
            ).pack(side="right", padx=5)
            
            # Progress bar visualization
            progress_frame = self.create_widget(tk.Frame, test_frame)
            progress_frame.pack(fill="x", padx=10, pady=2)
            
            # Progress bar using tkinter canvas
            bar_canvas = tk.Canvas(progress_frame, height=20, bg=self.colors["bg"], highlightthickness=0)
            bar_canvas.pack(fill="x")
            
            # Draw progress bar
            bar_width = 300
            fill_width = (percentage / 100) * bar_width
            
            # Background
            bar_canvas.create_rectangle(0, 0, bar_width, 20, fill="#cccccc", outline="")
            # Fill (green for current/latest test, blue for others)
            fill_color = "#4CAF50" if idx == 0 else "#2196F3"
            bar_canvas.create_rectangle(0, 0, fill_width, 20, fill=fill_color, outline="")
            # Percentage text
            text_color = "black" if self.current_theme == "light" else "white"
            bar_canvas.create_text(bar_width/2, 10, text=f"{percentage:.1f}%", fill=text_color)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = self.create_widget(tk.Frame, self.root)
        button_frame.pack(pady=20)
        
        if len(history) >= 2:
            self.create_widget(
                tk.Button,
                button_frame,
                text="Compare All Tests",
                command=self.show_comparison_screen,
                font=("Arial", 12)
            ).pack(side="left", padx=10)
        
        self.create_widget(
            tk.Button,
            button_frame,
            text="Back to Main",
            command=self.create_welcome_screen,
            font=("Arial", 12)
        ).pack(side="left", padx=10)

    def show_comparison_screen(self):
        """Show visual comparison of current test with previous attempts"""
        self.clear_screen()
        
        # Get all test data for the current user
        cursor.execute(
            """
            SELECT id, total_score, timestamp 
            FROM scores 
            WHERE username = ? 
            ORDER BY timestamp ASC
            """,
            (self.username,)
        )
        all_tests = cursor.fetchall()
        
        if len(all_tests) < 2:
            messagebox.showinfo("No Comparison", "You need at least 2 tests to compare.")
            self.create_welcome_screen()
            return
        
        # Header with back button
        header_frame = self.create_widget(tk.Frame, self.root)
        header_frame.pack(pady=10, fill="x")
        
        self.create_widget(
            tk.Button,
            header_frame,
            text="← Back",
            command=self.show_history_screen,
            font=("Arial", 10)
        ).pack(side="left", padx=10)
        
        self.create_widget(
            tk.Label,
            header_frame,
            text=f"Test Comparison for {self.username}",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=50)
        
        self.create_widget(
            tk.Label,
            self.root,
            text=f"Showing {len(all_tests)} tests over time",
            font=("Arial", 12)
        ).pack(pady=5)
        
        # Prepare data for visualization
        test_numbers = list(range(1, len(all_tests) + 1))
        scores = [test[1] for test in all_tests]
        max_score = len(self.questions) * 4
        percentages = [(score / max_score) * 100 for score in scores]
        
        # Create main comparison frame
        comparison_frame = self.create_widget(tk.Frame, self.root)
        comparison_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Left side: Bar chart visualization
        left_frame = self.create_widget(tk.Frame, comparison_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        self.create_widget(
            tk.Label,
            left_frame,
            text="Score Comparison",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Create bar chart using tkinter canvas
        chart_canvas = tk.Canvas(left_frame, bg=self.colors["chart_bg"], height=300)
        chart_canvas.pack(fill="both", expand=True, pady=10)
        
        # Draw bar chart
        chart_width = 400
        chart_height = 250
        bar_width = 30
        spacing = 20
        
        # Find max value for scaling
        max_value = max(scores)
        scale_factor = chart_height * 0.8 / max_value if max_value > 0 else 1
        
        # Draw bars
        for i, (test_num, score, percentage) in enumerate(zip(test_numbers, scores, percentages)):
            x = i * (bar_width + spacing) + 50
            bar_height = score * scale_factor
            y = chart_height - bar_height
            
            # Color: green for current/latest test, blue for others
            color = self.colors["improvement_good"] if i == len(test_numbers) - 1 else "#2196F3"
            
            # Draw bar
            chart_canvas.create_rectangle(x, y, x + bar_width, chart_height, fill=color, outline="black")
            
            # Draw test number below bar
            chart_canvas.create_text(x + bar_width/2, chart_height + 15, 
                                   text=f"Test {test_num}", 
                                   fill=self.colors["chart_fg"])
            
            # Draw score above bar
            chart_canvas.create_text(x + bar_width/2, y - 15, 
                                   text=f"{score}", 
                                   fill=self.colors["chart_fg"], 
                                   font=("Arial", 10, "bold"))
            
            # Draw percentage inside bar
            chart_canvas.create_text(x + bar_width/2, y + bar_height/2, 
                                   text=f"{percentage:.0f}%", 
                                   fill="white", 
                                   font=("Arial", 9, "bold"))
        
        # Draw Y-axis labels
        for i in range(0, max_score + 1, 10):
            y = chart_height - (i * scale_factor)
            chart_canvas.create_text(30, y, text=str(i), fill=self.colors["chart_fg"])
            chart_canvas.create_line(40, y, 45, y, fill=self.colors["chart_fg"])
        
        chart_canvas.create_text(20, 15, text="Score", fill=self.colors["chart_fg"], angle=90)
        
        # Right side: Statistics and improvement
        right_frame = self.create_widget(tk.Frame, comparison_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        self.create_widget(
            tk.Label,
            right_frame,
            text="Statistics & Improvement",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Calculate statistics
        first_score = scores[0]
        last_score = scores[-1]
        best_score = max(scores)
        worst_score = min(scores)
        avg_score = sum(scores) / len(scores)
        improvement = last_score - first_score
        improvement_percent = ((last_score - first_score) / first_score * 100) if first_score > 0 else 0
        
        # Display statistics
        stats_text = f"""
        First Test: {first_score} ({percentages[0]:.1f}%)
        Latest Test: {last_score} ({percentages[-1]:.1f}%)
        Best Score: {best_score} ({max(percentages):.1f}%)
        Worst Score: {worst_score} ({min(percentages):.1f}%)
        Average: {avg_score:.1f} ({(sum(percentages)/len(percentages)):.1f}%)
        """
        
        stats_label = self.create_widget(
            tk.Label,
            right_frame,
            text=stats_text.strip(),
            font=("Arial", 12),
            justify="left"
        )
        stats_label.pack(pady=10, padx=20, anchor="w")
        
        # Improvement indicator
        improvement_frame = self.create_widget(tk.Frame, right_frame)
        improvement_frame.pack(pady=20, padx=20, fill="x")
        
        improvement_color = self.colors["improvement_good"] if improvement > 0 else self.colors["improvement_bad"] if improvement < 0 else self.colors["improvement_neutral"]
        improvement_symbol = "↑" if improvement > 0 else "↓" if improvement < 0 else "→"
        
        self.create_widget(
            tk.Label,
            improvement_frame,
            text="Overall Improvement:",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")
        
        improvement_text = f"{improvement_symbol} {improvement:+.1f} points ({improvement_percent:+.1f}%)"
        improvement_label = self.create_widget(
            tk.Label,
            improvement_frame,
            text=improvement_text,
            font=("Arial", 12, "bold"),
            fg=improvement_color
        )
        improvement_label.pack(pady=5)
        
        # Interpretation of improvement
        if improvement > 10:
            interpretation = "Excellent progress! Keep up the good work."
        elif improvement > 5:
            interpretation = "Good improvement. You're getting better!"
        elif improvement > 0:
            interpretation = "Slight improvement. Every bit counts!"
        elif improvement == 0:
            interpretation = "Consistent performance. Try to push further next time."
        else:
            interpretation = "Need to focus on improvement. Review your responses."
        
        self.create_widget(
            tk.Label,
            improvement_frame,
            text=interpretation,
            font=("Arial", 10),
            wraplength=200
        ).pack(pady=10)
        
        # Trend visualization (simple arrow indicators)
        trend_frame = self.create_widget(tk.Frame, right_frame)
        trend_frame.pack(pady=10)
        
        self.create_widget(
            tk.Label,
            trend_frame,
            text="Score Trend:",
            font=("Arial", 11, "bold")
        ).pack(anchor="w")
        
        # Create simple trend line
        trend_canvas = tk.Canvas(trend_frame, width=200, height=80, bg=self.colors["chart_bg"])
        trend_canvas.pack(pady=10)
        
        # Draw trend line
        points = []
        for i, percentage in enumerate(percentages):
            x = i * (180 / (len(percentages) - 1)) + 10 if len(percentages) > 1 else 100
            y = 70 - (percentage * 60 / 100)
            points.append((x, y))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                x1, y1 = points[i]
                x2, y2 = points[i + 1]
                color = self.colors["improvement_good"] if y2 < y1 else self.colors["improvement_bad"] if y2 > y1 else self.colors["improvement_neutral"]
                trend_canvas.create_line(x1, y1, x2, y2, fill=color, width=2)
        
        for i, (x, y) in enumerate(points):
            color = self.colors["improvement_good"] if i == len(points) - 1 else "#2196F3"
            trend_canvas.create_oval(x-3, y-3, x+3, y+3, fill=color, outline="black")
        
        # Buttons at bottom
        button_frame = self.create_widget(tk.Frame, self.root)
        button_frame.pack(pady=20)
        
        self.create_widget(
            tk.Button,
            button_frame,
            text="View Detailed History",
            command=self.show_history_screen,
            font=("Arial", 12)
        ).pack(side="left", padx=10)
        
        self.create_widget(
            tk.Button,
            button_frame,
            text="Take Another Test",
            command=self.reset_test,
            font=("Arial", 12)
        ).pack(side="left", padx=10)
        
        self.create_widget(
            tk.Button,
            button_frame,
            text="Back to Main",
            command=self.create_welcome_screen,
            font=("Arial", 12)
        ).pack(side="left", padx=10)

    def reset_test(self):
        """Reset test variables and start over"""
        self.username = ""
        self.age = None
        self.age_group = None
        self.profession = None
        self.current_question = 0
        self.responses = []
        self.current_score = 0
        self.current_max_score = 0
        self.current_percentage = 0
        self.create_username_screen()

    def force_exit(self):
        try:
            conn.close()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

# ---------------- MAIN ----------------
class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.geometry("400x300")
        
        # Center Window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 300) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self.root.configure(bg="#2C3E50")
        
        tk.Label(self.root, text="Soul Sense", font=("Arial", 30, "bold"), bg="#2C3E50", fg="white").pack(expand=True, pady=(50, 10))
        tk.Label(self.root, text="Emotional Intelligence Exam", font=("Arial", 14), bg="#2C3E50", fg="#BDC3C7").pack(expand=True, pady=(0, 50))
        
        self.loading_label = tk.Label(self.root, text="Initializing...", font=("Arial", 10), bg="#2C3E50", fg="#BDC3C7")
        self.loading_label.pack(side="bottom", pady=20)

    def close_after_delay(self, delay, callback):
        self.root.after(delay, callback)

if __name__ == "__main__":
    splash_root = tk.Tk()
    splash = SplashScreen(splash_root)

    def launch_main_app():
        splash_root.destroy()
        root = tk.Tk()
        app = SoulSenseApp(root)
        root.protocol("WM_DELETE_WINDOW", app.force_exit)
        root.mainloop()

    splash.close_after_delay(2000, launch_main_app)
    splash_root.mainloop()