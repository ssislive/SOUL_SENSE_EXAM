"""
Enhanced SoulSense App with XAI - Use this file instead of app.py
All original functionality + XAI explanations
"""
import sqlite3
import tkinter as tk
from tkinter import messagebox, Toplevel, scrolledtext
from xai_explainer import SoulSenseXAI
from ml_predictor import SoulSenseMLPredictor

# DATABASE SETUP
conn = sqlite3.connect("soulsense_db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    age INTEGER,
    total_score INTEGER
)
""")
conn.commit()

# Initialize XAI
xai = SoulSenseXAI()

# QUESTIONS
questions = [
    {"text": "You can recognize your emotions as they happen.", "age_min": 12, "age_max": 25},
    {"text": "You find it easy to understand why you feel a certain way.", "age_min": 14, "age_max": 30},
    {"text": "You can control your emotions even in stressful situations.", "age_min": 15, "age_max": 35},
    {"text": "You reflect on your emotional reactions to situations.", "age_min": 13, "age_max": 28},
    {"text": "You are aware of how your emotions affect others.", "age_min": 16, "age_max": 40}
]

# USER DETAILS WINDOW
root = tk.Tk()
root.title("SoulSense - Emotional Intelligence Assessment")
root.geometry("450x350")
root.resizable(False, False)

# Set window icon (optional)
try:
    root.iconbitmap('icon.ico')
except:
    pass

# Configure colors
bg_color = "#f0f8ff"
button_color = "#4CAF50"
text_color = "#333333"

root.configure(bg=bg_color)

username = tk.StringVar()
age = tk.StringVar()

# Header
header = tk.Label(
    root,
    text="🧠 SoulSense Assessment",
    font=("Arial", 22, "bold"),
    bg=bg_color,
    fg="#2c3e50"
)
header.pack(pady=20)

# Subtitle
tk.Label(
    root,
    text="Emotional Intelligence Evaluation",
    font=("Arial", 12),
    bg=bg_color,
    fg="#7f8c8d"
).pack()

# Username field
tk.Label(
    root, 
    text="Enter your name:", 
    font=("Arial", 14, "bold"),
    bg=bg_color,
    fg=text_color
).pack(pady=(20, 5))

tk.Entry(
    root, 
    textvariable=username, 
    font=("Arial", 13), 
    width=25,
    relief=tk.GROOVE,
    bd=2
).pack(pady=5)

# Age field
tk.Label(
    root, 
    text="Enter your age:", 
    font=("Arial", 14, "bold"),
    bg=bg_color,
    fg=text_color
).pack(pady=(15, 5))

tk.Entry(
    root, 
    textvariable=age, 
    font=("Arial", 13), 
    width=25,
    relief=tk.GROOVE,
    bd=2
).pack(pady=5)

def submit_details():
    """Validate and start assessment"""
    if not username.get().strip():
        messagebox.showerror("Error", "Please enter your name")
        return
    
    if not age.get().isdigit():
        messagebox.showerror("Error", "Please enter a valid age (numbers only)")
        return
    
    age_int = int(age.get())
    if age_int < 12 or age_int > 100:
        messagebox.showerror("Error", "Age must be between 12 and 100")
        return
    
    root.destroy()
    start_quiz(username.get().strip(), age_int)

# Start button
tk.Button(
    root,
    text="🚀 Start Assessment",
    command=submit_details,
    bg=button_color,
    fg="white",
    font=("Arial", 14, "bold"),
    width=20,
    height=2,
    relief=tk.RAISED,
    bd=3,
    cursor="hand2"
).pack(pady=25)

# Footer
tk.Label(
    root,
    text="Your emotional intelligence journey starts here",
    font=("Arial", 10),
    bg=bg_color,
    fg="#7f8c8d"
).pack(side=tk.BOTTOM, pady=10)

# QUIZ WINDOW
def start_quiz(username, age):
    q_scores = []  # Track individual question scores
    """Main assessment window"""
    filtered_questions = [
        q for q in questions if q["age_min"] <= age <= q["age_max"]
    ]
    
    if not filtered_questions:
        messagebox.showinfo("No Questions", "No questions available for your age group.")
        return
    
    quiz = tk.Tk()
    quiz.title(f"SoulSense Assessment - {username}")
    quiz.geometry("800x600")
    quiz.configure(bg=bg_color)
    
    # Progress tracking
    score = 0
    current_q = 0
    var = tk.IntVar()
    
    # Question counter
    counter_label = tk.Label(
        quiz,
        text=f"Question 1 of {len(filtered_questions)}",
        font=("Arial", 12, "bold"),
        bg=bg_color,
        fg="#3498db"
    )
    counter_label.pack(pady=10)
    
    # Question display
    question_frame = tk.Frame(quiz, bg=bg_color)
    question_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
    
    question_label = tk.Label(
        question_frame,
        text="",
        wraplength=700,
        font=("Arial", 16, "bold"),
        bg=bg_color,
        fg="#2c3e50",
        justify="center"
    )
    question_label.pack(pady=20)
    
    # Response options
    options_frame = tk.Frame(quiz, bg=bg_color)
    options_frame.pack(pady=10)
    
    options = [
        ("😔 Strongly Disagree", 1),
        ("🙁 Disagree", 2),
        ("😐 Neutral", 3),
        ("🙂 Agree", 4),
        ("😊 Strongly Agree", 5)
    ]
    
    for text, val in options:
        rb = tk.Radiobutton(
            options_frame,
            text=text,
            variable=var,
            value=val,
            font=("Arial", 13),
            bg=bg_color,
            fg=text_color,
            selectcolor="#e3f2fd",
            activebackground=bg_color,
            indicatoron=True,
            width=25,
            anchor="w"
        )
        rb.pack(pady=3, padx=50, anchor="w")
    
    def load_question():
        """Load current question"""
        question_label.config(text=filtered_questions[current_q]["text"])
        counter_label.config(text=f"Question {current_q + 1} of {len(filtered_questions)}")
    
    def next_question():
        q_scores.append(var.get()) 
        """Handle next question or completion"""
        nonlocal current_q, score
        
        if var.get() == 0:
            messagebox.showwarning("Warning", "Please select an option before continuing")
            return
        
        score += var.get()
        var.set(0)
        current_q += 1
        
        if current_q < len(filtered_questions):
            load_question()
        else:
            # Save score to database
            cursor.execute(
                "INSERT INTO scores (username, age, total_score) VALUES (?, ?, ?)",
                (username, age, score)
            )
            conn.commit()
            
            # Get user ID
            user_id = cursor.lastrowid
            
            # Generate XAI explanation
            explanation = xai.analyze_score(score, username, age)
            
            # Save explanation
            xai.save_explanation(user_id, score, explanation)
            
            # Show results with XAI
           show_results(username, score, explanation, q_scores, age)
            quiz.destroy()
    
def show_results(username, score, explanation, q_scores, age):
    """Display results with ML XAI explanation"""
    results_window = Toplevel()
    results_window.title("Assessment Results with AI Insights")
    results_window.geometry("1000x800")
    results_window.configure(bg=bg_color)
    
    # Initialize ML predictor
    ml_predictor = SoulSenseMLPredictor()
    
    # Get ML prediction with XAI
    ml_result = ml_predictor.predict_with_explanation(q_scores, age, score)
    
    # Create notebook/tabs for different views
    notebook = ttk.Notebook(results_window)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)
    
    # Tab 1: Summary
    summary_frame = tk.Frame(notebook, bg=bg_color)
    notebook.add(summary_frame, text='📊 Summary')
    
    # Header
    tk.Label(
        summary_frame,
        text="🎯 Assessment Complete!",
        font=("Arial", 24, "bold"),
        bg=bg_color,
        fg="#2c3e50"
    ).pack(pady=20)
    
    # Score display with ML prediction
    score_frame = tk.Frame(summary_frame, bg="#e8f5e9", relief=tk.RAISED, bd=2)
    score_frame.pack(pady=10, padx=50, fill=tk.X)
    
    tk.Label(
        score_frame,
        text=f"👤 User: {username} | 🎂 Age: {age}",
        font=("Arial", 14),
        bg="#e8f5e9"
    ).pack(pady=5)
    
    tk.Label(
        score_frame,
        text=f"📊 Total Score: {score}/25",
        font=("Arial", 18, "bold"),
        bg="#e8f5e9",
        fg="#27ae60"
    ).pack(pady=5)
    
    # ML Prediction
    risk_colors = {
        'Low Risk': "#27ae60",
        'Moderate Risk': "#f39c12", 
        'High Risk': "#e74c3c"
    }
    
    risk_color = risk_colors.get(ml_result['prediction_label'], "#2c3e50")
    
    tk.Label(
        score_frame,
        text=f"🤖 AI Risk Assessment: {ml_result['prediction_label']}",
        font=("Arial", 16, "bold"),
        bg="#e8f5e9",
        fg=risk_color
    ).pack(pady=10)
    
    tk.Label(
        score_frame,
        text=f"🔍 Confidence: {ml_result['confidence']:.1%}",
        font=("Arial", 14),
        bg="#e8f5e9"
    ).pack(pady=5)
    
    # Tab 2: ML Explanation
    ml_frame = tk.Frame(notebook, bg=bg_color)
    notebook.add(ml_frame, text='🤖 AI Insights')
    
    tk.Label(
        ml_frame,
        text="Machine Learning Analysis",
        font=("Arial", 20, "bold"),
        bg=bg_color,
        fg="#2c3e50"
    ).pack(pady=20)
    
    # ML Explanation
    ml_text = scrolledtext.ScrolledText(
        ml_frame,
        wrap=tk.WORD,
        width=90,
        height=25,
        font=("Arial", 11),
        bg="#f8f9fa",
        relief=tk.GROOVE,
        bd=2
    )
    ml_text.pack(pady=10, padx=20)
    ml_text.insert(tk.END, ml_result['explanation'])
    ml_text.config(state=tk.DISABLED)
    
    # Tab 3: Feature Importance
    feature_frame = tk.Frame(notebook, bg=bg_color)
    notebook.add(feature_frame, text='📈 Feature Impact')
    
    tk.Label(
        feature_frame,
        text="How Each Factor Influenced Your Assessment",
        font=("Arial", 18, "bold"),
        bg=bg_color,
        fg="#2c3e50"
    ).pack(pady=20)
    
    # Create feature importance display
    canvas = tk.Canvas(feature_frame, bg=bg_color, height=500)
    scrollbar = tk.Scrollbar(feature_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=bg_color)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Display top features
    row = 0
    for feature, importance in list(ml_result['feature_importance'].items())[:10]:
        feature_readable = feature.replace('_', ' ').title()
        feature_value = ml_result['features'].get(feature, 0)
        
        # Create feature card
        card = tk.Frame(
            scrollable_frame,
            bg="#ffffff",
            relief=tk.RAISED,
            bd=1
        )
        card.grid(row=row, column=0, pady=5, padx=20, sticky="ew")
        
        # Importance bar
        bar_width = int(importance * 300)
        tk.Label(
            card,
            text="",
            bg="#3498db",
            width=bar_width,
            anchor="w"
        ).grid(row=0, column=0, sticky="w", ipady=5)
        
        # Feature info
        tk.Label(
            card,
            text=f"{feature_readable}",
            font=("Arial", 12, "bold"),
            bg="#ffffff",
            fg="#2c3e50"
        ).grid(row=0, column=1, padx=10, sticky="w")
        
        tk.Label(
            card,
            text=f"Impact: {importance:.1%} | Value: {feature_value:.1f}",
            font=("Arial", 10),
            bg="#ffffff",
            fg="#7f8c8d"
        ).grid(row=1, column=1, padx=10, sticky="w", pady=(0, 5))
        
        row += 1
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Buttons
    button_frame = tk.Frame(results_window, bg=bg_color)
    button_frame.pack(pady=10)
    
    # Generate feature importance plot
    def generate_plot():
        filename = ml_predictor.plot_feature_importance(
            ml_result['feature_importance'],
            username
        )
        messagebox.showinfo("Plot Saved", f"Feature importance plot saved as:\n{filename}")
    
    tk.Button(
        button_frame,
        text="📈 Save Feature Plot",
        command=generate_plot,
        bg="#3498db",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15,
        relief=tk.RAISED
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        button_frame,
        text="💾 Save Full Report",
        command=lambda: save_full_report(username, score, explanation, ml_result),
        bg="#9b59b6",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15,
        relief=tk.RAISED
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        button_frame,
        text="🔄 Take Again",
        command=lambda: [results_window.destroy(), start_quiz(username, age)],
        bg="#f39c12",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15,
        relief=tk.RAISED
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        button_frame,
        text="❌ Close",
        command=lambda: [results_window.destroy(), close_app()],
        bg="#e74c3c",
        fg="white",
        font=("Arial", 11, "bold"),
        width=15,
        relief=tk.RAISED
    ).pack(side=tk.LEFT, padx=5)

def save_full_report(username, score, explanation, ml_result):
    """Save comprehensive report with ML insights"""
    filename = f"soulsense_ml_report_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    report = f"""
    SOUL SENSE - COMPREHENSIVE ASSESSMENT REPORT
    {'='*60}
    
    BASIC INFORMATION:
    • Username: {username}
    • Total Score: {score}/25
    • Assessment Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    {'='*60}
    AI MACHINE LEARNING ASSESSMENT:
    • Risk Level: {ml_result['prediction_label']}
    • Confidence: {ml_result['confidence']:.1%}
    
    PREDICTION PROBABILITIES:
    • Low Risk: {ml_result['probabilities'][0]:.1%}
    • Moderate Risk: {ml_result['probabilities'][1]:.1%}
    • High Risk: {ml_result['probabilities'][2]:.1%}
    
    {'='*60}
    FEATURE IMPORTANCE ANALYSIS:
    """
    
    for feature, importance in ml_result['feature_importance'].items():
        readable_name = feature.replace('_', ' ').title()
        value = ml_result['features'].get(feature, 0)
        report += f"\n• {readable_name}: {importance:.1%} (Value: {value:.1f})"
    
    report += f"\n\n{'='*60}"
    report += "\nDETAILED EXPLANATION:\n"
    report += ml_result['explanation']
    
    report += f"\n\n{'='*60}"
    report += "\nTRADITIONAL ANALYSIS:\n"
    report += explanation
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    messagebox.showinfo("Report Saved", f"Comprehensive report saved as:\n{filename}")
    
    def save_report(username, score, explanation):
        """Save report to text file"""
        filename = f"soulsense_report_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(explanation)
        messagebox.showinfo("Saved", f"Report saved as {filename}")
    
    def close_app():
        """Close application"""
        conn.close()
        xai.close()
        root.quit()
    
    # Next button
    button_frame = tk.Frame(quiz, bg=bg_color)
    button_frame.pack(pady=20)
    
    tk.Button(
        button_frame,
        text="➡️ Next Question" if current_q < len(filtered_questions) - 1 else "🏁 Finish",
        command=next_question,
        bg=button_color,
        fg="white",
        font=("Arial", 14, "bold"),
        width=20,
        height=2,
        relief=tk.RAISED,
        bd=3,
        cursor="hand2"
    ).pack()
    
    # Load first question
    load_question()
    quiz.mainloop()


# Import datetime at the top (add this line)
from datetime import datetime

# Start the app
if __name__ == "__main__":
    root.mainloop()
