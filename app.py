import sqlite3
import tkinter as tk
from tkinter import messagebox
import time

# ================= DATABASE SETUP =================
conn = sqlite3.connect("soulsense_db.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    age INTEGER,
    total_score INTEGER,
    avg_response REAL,
    max_response INTEGER,
    min_response INTEGER,
    score_variance REAL,
    normalized_score REAL,
    time_taken_seconds INTEGER
)
""")
conn.commit()

def migrate_scores_table():
    cursor.execute("PRAGMA table_info(scores)")
    existing_columns = [col[1] for col in cursor.fetchall()]

    required_columns = {
        "avg_response": "REAL",
        "max_response": "INTEGER",
        "min_response": "INTEGER",
        "score_variance": "REAL",
        "normalized_score": "REAL",
        "time_taken_seconds": "INTEGER"
    }

    for column, dtype in required_columns.items():
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE scores ADD COLUMN {column} {dtype}")

    conn.commit()

migrate_scores_table()

# ================= QUESTIONS =================
questions = [
    {"text": "You can recognize your emotions as they happen.", "age_min": 12, "age_max": 25},
    {"text": "You find it easy to understand why you feel a certain way.", "age_min": 14, "age_max": 30},
    {"text": "You can control your emotions even in stressful situations.", "age_min": 15, "age_max": 35},
    {"text": "You reflect on your emotional reactions to situations.", "age_min": 13, "age_max": 28},
    {"text": "You are aware of how your emotions affect others.", "age_min": 16, "age_max": 40}
]

# ================= FEATURE ENGINEERING =================
def extract_features(responses):
    n = len(responses)
    if n == 0:
        return {"avg": 0, "max": 0, "min": 0, "variance": 0, "normalized": 0}

    avg = sum(responses) / n
    variance = sum((x - avg) ** 2 for x in responses) / n

    return {
        "avg": round(avg, 2),
        "max": max(responses),
        "min": min(responses),
        "variance": round(variance, 2),
        "normalized": round(sum(responses) / (n * 5), 2)
    }

# ================= SPLASH SCREEN =================
def show_splash():
    splash = tk.Tk()
    splash.title("SoulSense")
    splash.geometry("500x300")
    splash.resizable(False, False)
    splash.configure(bg="#1E1E2F")

    tk.Label(splash, text="SoulSense", font=("Arial", 32, "bold"),
             fg="white", bg="#1E1E2F").pack(pady=40)

    tk.Label(splash, text="Emotional Awareness Assessment",
             font=("Arial", 14), fg="#CCCCCC", bg="#1E1E2F").pack()
    tk.Label(
        splash,
        text="Loading...",
        font=("Arial", 14),
        fg="white",
        bg="#1E1E2F"
    ).pack(pady=30)
    splash.after(2500, lambda: (splash.destroy(), show_user_details()))
    splash.mainloop()

# ================= USER DETAILS =================
def show_user_details():
    global root, username, age

    root = tk.Tk()
    root.title("SoulSense - User Details")
    root.geometry("450x350")
    root.resizable(False, False)

    username = tk.StringVar()
    age = tk.StringVar()

    tk.Label(root, text="SoulSense Assessment",
             font=("Arial", 20, "bold")).pack(pady=20)

    tk.Label(root, text="Enter your name:", font=("Arial", 15)).pack()
    tk.Entry(root, textvariable=username, font=("Arial", 15), width=25).pack(pady=8)

    tk.Label(root, text="Enter your age:", font=("Arial", 15)).pack()
    tk.Entry(root, textvariable=age, font=("Arial", 15), width=25).pack(pady=8)

    tk.Button(root, text="Start Assessment",
              command=lambda: submit_details(root),
              bg="#4CAF50", fg="white",
              font=("Arial", 14, "bold"),
              width=20).pack(pady=25)

    root.mainloop()

def submit_details(window):
    if not username.get() or not age.get().isdigit():
        messagebox.showerror("Error", "Please enter valid name and age")
        return

    window.destroy()
    start_quiz(username.get(), int(age.get()))

# ================= QUIZ WINDOW =================
def start_quiz(username, age):
    filtered_questions = [q for q in questions if q["age_min"] <= age <= q["age_max"]]

    if not filtered_questions:
        messagebox.showinfo("No Questions", "No questions available for your age group.")
        return

    quiz = tk.Tk()
    quiz.title("SoulSense Assessment")
    quiz.geometry("750x580")
    quiz.resizable(False, False)

    score = 0
    current_q = 0
    responses = []
    var = tk.IntVar()

    # ---------- TIMER ----------
    start_time = time.time()
    timer_running = True

    timer_label = tk.Label(quiz, font=("Arial", 14, "bold"), fg="#1E88E5")
    timer_label.pack(pady=5)

    def update_timer():
        if timer_running:
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            timer_label.config(text=f"Time: {mins:02d}:{secs:02d}")
            quiz.after(1000, update_timer)

    update_timer()

    # ---------- QUESTION ----------
    question_label = tk.Label(quiz, wraplength=700, font=("Arial", 16))
    question_label.pack(pady=20)

    options = [
        ("Strongly Disagree", 1),
        ("Disagree", 2),
        ("Neutral", 3),
        ("Agree", 4),
        ("Strongly Agree", 5)
    ]

    for text, val in options:
        tk.Radiobutton(quiz, text=text, variable=var,
                       value=val, font=("Arial", 14)).pack(anchor="w", padx=60)

    def load_question():
        question_label.config(text=filtered_questions[current_q]["text"])

    def save_and_exit(title):
        nonlocal timer_running
        timer_running = False

        elapsed_time = int(time.time() - start_time)
        features = extract_features(responses)

        cursor.execute("""
            INSERT INTO scores
            (username, age, total_score, avg_response, max_response, min_response,
             score_variance, normalized_score, time_taken_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username, age, score,
            features["avg"], features["max"], features["min"],
            features["variance"], features["normalized"],
            elapsed_time
        ))
        conn.commit()

        mins, secs = divmod(elapsed_time, 60)

        messagebox.showinfo(
            title,
            f"Questions Attempted: {len(responses)}\n"
            f"Score: {score}\n"
            f"Time Taken: {mins} min {secs} sec"
        )

        quiz.destroy()
        conn.close()

    def next_question():
        nonlocal current_q, score
        if var.get() == 0:
            messagebox.showwarning("Warning", "Please select an option")
            return

        responses.append(var.get())
        score += var.get()
        var.set(0)
        current_q += 1

        if current_q < len(filtered_questions):
            load_question()
        else:
            save_and_exit("Test Completed")

    def stop_test():
        if messagebox.askyesno("Stop Test", "Stop the test and save progress?"):
            save_and_exit("Test Stopped")

    tk.Button(quiz, text="Next", command=next_question,
              bg="#4CAF50", fg="white",
              font=("Arial", 14, "bold"), width=15).pack(pady=15)

    tk.Button(quiz, text="Stop Test", command=stop_test,
              bg="#E53935", fg="white",
              font=("Arial", 13, "bold"), width=15).pack()

    load_question()
    quiz.mainloop()

# ================= START APP =================
show_splash()
