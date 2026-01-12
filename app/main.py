# ==============================
# SoulSense Main Application
# FINAL VERSION WITH STRESS FLOW
# ==============================

import tkinter as tk
from tkinter import messagebox, simpledialog
import logging
import sys
from datetime import datetime

from app.ui.styles import UIStyles, ColorSchemes
from app.ui.auth import AuthManager
from app.ui.exam import ExamManager
from app.ui.results import ResultsManager
from app.ui.settings import SettingsManager
from app.db import get_connection
from app.utils import load_settings
from app.logger import setup_logging

from app.questions import load_questions
from app.exceptions import ResourceError


# ---------------- LOGGING ----------------
setup_logging()

# ---------------- STRESS OPTIONS ----------------
STRESS_OPTIONS = [
    "Work",
    "Relationships",
    "Family",
    "Finance",
    "Health",
    "Personal Growth"
]

conn = get_connection()
cursor = conn.cursor()

# ---------------- STRESS CONTEXT TABLE ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS stress_context (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    stress_triggers TEXT,
    stress_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# ---------------- MAIN APP ----------------
class SoulSenseApp:

    # ---------------- LOAD QUESTIONS ----------------
    try:
        rows = load_questions()  # [(id, text, tooltip, min_age, max_age)]

        all_questions = [
            (f"Q{idx + 1}. {q[1]}", q[2])
            for idx, q in enumerate(rows)
        ]

        if not all_questions:
            raise ResourceError("Question bank empty.")

    except Exception as e:
        import sys, logging
        logging.critical("Failed to load questions", exc_info=True)
        print("Fatal Error: Could not load questions.", file=sys.stderr)
        sys.exit(1)


    def on_start_test_click(self):
        """
        Called by AuthManager when Start Assessment is clicked.
        Ensures login first, then stress popup.
        """
        if not self.current_user_id and not self.username:
            # 🔧 FIX: call AuthManager, not missing method
            self.auth.create_username_screen(callback=self.after_login_start)
        else:
            self.after_login_start()

    def after_login_start(self):
        """
        Called ONLY after name/age/profession is collected.
        Now show stress popup.
        """
        self.show_stress_popup()

    def open_journal_flow(self):
        """
        Called by AuthManager.
        Opens Journal feature if available.
        """
        try:
            if hasattr(self, "journal_feature") and self.journal_feature:
                if not self.username:
                    name = simpledialog.askstring(
                        "Journal Access",
                        "Please enter your name to access your journal:",
                        parent=self.root
                    )
                    if not name:
                        return
                    self.username = name.strip()

            self.journal_feature.open_journal_window(self.username)
        except Exception as e:
            logging.exception("Failed to open journal")
            messagebox.showerror("Error", str(e))

    def open_dashboard_flow(self):
        """
        Called by AuthManager.
        Opens Analytics Dashboard if available.
        """
        try:
            from app.ui.dashboard import AnalyticsDashboard

            if not self.username:
                name = simpledialog.askstring(
                    "Dashboard Access",
                    "Please enter your name to view your dashboard:",
                    parent=self.root
                )
            if not name:
                return
            self.username = name.strip()

            dashboard = AnalyticsDashboard(
                self.root,
                self.username,
                self.colors,
                self.current_theme
            )
            dashboard.open_dashboard()
        except ImportError:
            messagebox.showinfo(
                "Dashboard",
                "Analytics Dashboard feature is not available."
            )
        except Exception as e:
            logging.exception("Failed to open dashboard")
            messagebox.showerror("Error", str(e))

    def show_history_screen(self):
        """
        Called by AuthManager.
        Shows the user's test history via ResultsManager.
        """
        try:
            self.results.show_history_screen()
        except Exception as e:
            logging.exception("Failed to show history screen")
            messagebox.showerror("Error", str(e))

    def show_settings(self):
        """
        Called by AuthManager.
        Opens the Settings window.
        """
        try:
            self.settings_manager.show_settings()
        except Exception as e:
            logging.exception("Failed to open settings")
            messagebox.showerror("Error", str(e))

    def __init__(self, root):
        self.root = root
        self.root.title("Soul Sense EQ Test")
        self.root.geometry("800x700")

        # Core Managers
        self.styles = UIStyles(self)
        self.auth = AuthManager(self)
        self.exam = ExamManager(self)
        self.results = ResultsManager(self)
        self.settings_manager = SettingsManager(self)

        # Settings
        self.settings = load_settings()
        self.apply_theme(self.settings.get("theme", "light"))

        # User State
        self.current_user_id = None
        self.username = ""
        self.age = None
        self.age_group = None
        self.profession = None

        # Exam State
        self.responses = []
        self.current_score = 0
        self.current_max_score = 0
        self.current_percentage = 0

        # Stress Context
        self.stress_triggers = "Not specified"
        self.stress_reason = "Not specified"

        self.create_welcome_screen()

        # ---------------- ML PREDICTOR (OPTIONAL) ----------------
        try:
            from app.ml.predictor import SoulSenseMLPredictor
            self.ml_predictor = SoulSenseMLPredictor()
        except Exception:
            self.ml_predictor = None


        # ---------------- QUESTIONS ----------------
        question_count = self.settings.get("question_count", 10)
        self.questions = self.all_questions[:min(question_count, len(self.all_questions))]
        self.total_questions_count = len(self.all_questions)

    # ---------------- THEME ----------------
    def apply_theme(self, theme):
        self.styles.apply_theme(theme)
        self.current_theme = theme
        self.colors = ColorSchemes.LIGHT if theme == "light" else ColorSchemes.DARK

    # ---------------- NAV ----------------
    def clear_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ---------------- START FLOW ----------------
    def start_test(self):
        """Intercept start → show stress popup"""
        self.exam.start()

    

    # ---------------- STRESS POPUP (STEP 1) ----------------
    def show_stress_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Stress Trigger (Optional)")
        popup.geometry("420x420")
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(
            popup,
            text="What is your main source of stress?",
            font=("Arial", 14, "bold")
        ).pack(pady=15)

        vars_map = {}
        for opt in STRESS_OPTIONS:
            v = tk.BooleanVar()
            vars_map[opt] = v
            tk.Checkbutton(
                popup,
                text=opt,
                variable=v,
                font=("Arial", 12)
            ).pack(anchor="w", padx=40)

        def next_step():
            selected = [k for k, v in vars_map.items() if v.get()]
            self.stress_triggers = ", ".join(selected) if selected else "Not specified"
            popup.destroy()
            self.show_stress_reason_popup()

        tk.Button(
            popup,
            text="Next",
            command=next_step,
            bg="#3B82F6",
            fg="white",
            font=("Arial", 12, "bold"),
            width=18
        ).pack(pady=25)

    # ---------------- STRESS POPUP (STEP 2) ----------------
    def show_stress_reason_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Describe Your Stress")
        popup.geometry("500x400")
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(
            popup,
            text="Describe your stress (max 200 words)",
            font=("Arial", 14, "bold")
        ).pack(pady=15)

        text_box = tk.Text(popup, height=8, width=55)
        text_box.pack(pady=10)

        counter = tk.Label(popup, text="0 / 200 words")
        counter.pack()

        def update_count(event=None):
            words = len(text_box.get("1.0", "end").strip().split())
            counter.config(text=f"{words} / 200 words", fg="red" if words > 200 else "black")

        text_box.bind("<KeyRelease>", update_count)

        def submit():
            text = text_box.get("1.0", "end").strip()
            if len(text.split()) > 200:
                messagebox.showerror("Limit Exceeded", "Maximum 200 words allowed.")
                return

            self.stress_reason = text if text else "Not specified"
            popup.destroy()
            self.save_stress_to_db()
            self.exam.start()  # 🔥 START EXAM

        tk.Button(
            popup,
            text="Submit",
            command=submit,
            bg="#10B981",
            fg="white",
            font=("Arial", 12, "bold"),
            width=20
        ).pack(pady=20)

    # ---------------- DB SAVE ----------------
    def save_stress_to_db(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO stress_context (username, stress_triggers, stress_reason)
                VALUES (?, ?, ?)
                """,
                (self.username, self.stress_triggers, self.stress_reason)
            )
            conn.commit()
            conn.close()
        except Exception:
            logging.exception("Failed to save stress context")

    # ---------------- UI ENTRY ----------------
    def create_welcome_screen(self):
        self.clear_screen()
        self.auth.create_welcome_screen()

    # ---------------- EXIT ----------------
    def force_exit(self):
        self.root.destroy()
        sys.exit(0)


# ---------------- RUN ----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SoulSenseApp(root)
    root.protocol("WM_DELETE_WINDOW", app.force_exit)
    root.mainloop()
