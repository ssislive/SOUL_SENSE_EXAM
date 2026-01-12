"""
Soul Sense Exam Module
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import time

# ---------------- SAFE FALLBACK SESSION ----------------
class FallbackExamSession:
    def __init__(self, username, age, age_group, questions):
        self.username = username
        self.age = age
        self.age_group = age_group
        self.questions = questions
        self.index = 0
        self.responses = []
        self.response_times = []
        self.score = 0
        self.sentiment_score = 0
        self.reflection_text = ""

    def is_finished(self):
        return self.index >= len(self.questions)

    def get_current_question(self):
        q = self.questions[self.index]
        return q[0], q[1] if len(q) > 1 else ""

    def get_progress(self):
        total = len(self.questions)
        current = self.index + 1
        pct = (current / total) * 100
        return current, total, pct

    def submit_answer(self, value):
        self.responses.append(value)
        self.response_times.append(time.time())
        self.score += value
        self.index += 1

    def go_back(self):
        if self.index > 0:
            self.index -= 1
            self.score -= self.responses.pop()
            self.response_times.pop()
            return True
        return False

    def submit_reflection(self, text, analyzer=None):
        self.reflection_text = text

    def finish_exam(self):
        return True


# ---------------- EXAM MANAGER ----------------
class ExamManager:
    def __init__(self, app):
        self.app = app
        self.root = app.root
        self.answer_var = tk.IntVar()
        self.session = None

    # 🔑 Compatibility with main app
    def start(self):
        self.start_test()

    def start_test(self):
        try:
            from app.services.exam_service import ExamSession
        except Exception:
            logging.warning("ExamSession not found, using fallback")
            ExamSession = FallbackExamSession

        self.session = ExamSession(
            username=self.app.username,
            age=self.app.age,
            age_group=self.app.age_group,
            questions=self.app.questions
        )

        self.show_question()

    def show_question(self):
        self.app.clear_screen()
        colors = self.app.colors

        if self.session.is_finished():
            self.show_reflection_screen()
            return

        q_text, q_tooltip = self.session.get_current_question()
        current, total, pct = self.session.get_progress()

        container = tk.Frame(self.root, bg=colors["bg"])
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text=f"Question {current} of {total}",
            font=("Segoe UI", 14, "bold"),
            bg=colors["bg"]
        ).pack(pady=10)

        ttk.Progressbar(
            container,
            value=pct,
            maximum=100
        ).pack(fill="x", padx=40, pady=5)

        card = tk.Frame(container, bg=colors["surface"])
        card.pack(padx=40, pady=30, fill="x")

        tk.Label(
            card,
            text=q_text,
            wraplength=500,
            font=("Segoe UI", 14),
            bg=colors["surface"]
        ).pack(pady=15)

        self.answer_var.set(0)
        for label, val in [("Never",1),("Sometimes",2),("Often",3),("Always",4)]:
            tk.Radiobutton(
                card,
                text=label,
                variable=self.answer_var,
                value=val,
                bg=colors["surface"],
                font=("Segoe UI", 12)
            ).pack(anchor="w", padx=20)

        btns = tk.Frame(container, bg=colors["bg"])
        btns.pack(pady=20)

        if current > 1:
            tk.Button(
                btns, text="Previous",
                command=self.previous_question
            ).pack(side="left", padx=10)

        tk.Button(
            btns, text="Next",
            command=self.save_answer
        ).pack(side="left", padx=10)

    def previous_question(self):
        if self.session.go_back():
            self.show_question()

    def save_answer(self):
        val = self.answer_var.get()
        if val == 0:
            messagebox.showwarning("Required", "Select an option")
            return
        self.session.submit_answer(val)
        self.show_question()

    def show_reflection_screen(self):
        self.app.clear_screen()

        frame = tk.Frame(self.root)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Final Reflection",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=20)

        self.reflection = tk.Text(frame, height=6)
        self.reflection.pack(padx=40, pady=10, fill="x")

        tk.Button(
            frame,
            text="Finish Test",
            command=self.submit_reflection
        ).pack(pady=20)

    def submit_reflection(self):
        text = self.reflection.get("1.0", "end").strip()
        self.session.submit_reflection(text)
        self.finish_test()

    def finish_test(self):
        self.session.finish_exam()

        self.app.current_score = self.session.score
        self.app.responses = self.session.responses
        self.app.current_max_score = len(self.session.responses) * 4
        self.app.current_percentage = (
            self.app.current_score / self.app.current_max_score * 100
            if self.app.current_max_score else 0
        )

        if hasattr(self.app, "results"):
            self.app.results.show_visual_results()
        else:
            messagebox.showinfo(
                "Completed",
                f"Score: {self.app.current_percentage:.1f}%"
            )
