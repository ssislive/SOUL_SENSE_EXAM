import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from journal_feature import JournalFeature
from analytics_dashboard import AnalyticsDashboard
from i18n_manager import get_i18n, I18nManager
from tkinter import messagebox, font
from journal_feature import JournalFeature
from analytics_dashboard import AnalyticsDashboard
from datetime import datetime

# DATABASE SETUP
conn = sqlite3.connect("soulsense_db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    age INTEGER,
    total_score INTEGER,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

try:
    cursor.execute("ALTER TABLE scores ADD COLUMN age INTEGER")
except sqlite3.OperationalError:
    pass

conn.commit()


# Initialize i18n
i18n = get_i18n()

#QUESTIONS
#QUESTIONS - Now loaded from translation files
def get_questions():
    """Get questions in current language"""
    question_texts = i18n.get_all_questions()
    return [
        {"text": question_texts[0] if len(question_texts) > 0 else "Question 1", "age_min": 12, "age_max": 25},
        {"text": question_texts[1] if len(question_texts) > 1 else "Question 2", "age_min": 14, "age_max": 30},
        {"text": question_texts[2] if len(question_texts) > 2 else "Question 3", "age_min": 15, "age_max": 35},
        {"text": question_texts[3] if len(question_texts) > 3 else "Question 4", "age_min": 13, "age_max": 28},
        {"text": question_texts[4] if len(question_texts) > 4 else "Question 5", "age_min": 16, "age_max": 40}
    ]

questions = get_questions()
# QUESTIONS
questions = [
    {"text": "You can recognize your emotions as they happen.", "age_min": 12, "age_max": 25},
    {"text": "You find it easy to understand why you feel a certain way.", "age_min": 14, "age_max": 30},
    {"text": "You can control your emotions even in stressful situations.", "age_min": 15, "age_max": 35},
    {"text": "You reflect on your emotional reactions to situations.", "age_min": 13, "age_max": 28},
    {"text": "You are aware of how your emotions affect others.", "age_min": 16, "age_max": 40}
]

# Custom colors
COLORS = {
    "primary": "#4CAF50",
    "secondary": "#2196F3",
    "accent": "#FF9800",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "light_bg": "#f0f4f8",
    "card_bg": "#ffffff",
    "text": "#333333",
    "subtext": "#666666",
    "border": "#e0e0e0",
    "analytics": "#9C27B0",
    "correlation": "#E91E63",
    "insights": "#009688",
    "white": "#FFFFFF",
    "light_white": "#F8F9FA"
}

def show_analysis_complete(username, score, age, total_questions):
    """Show the completion screen as a main window"""
    analysis_window = tk.Tk()
    analysis_window.title("Analysis & Insights - SoulSense")
    
    # Get screen dimensions
    screen_width = analysis_window.winfo_screenwidth()
    screen_height = analysis_window.winfo_screenheight()
    
    # Set to nearly full screen (95% of screen)
    window_width = int(screen_width * 0.95)
    window_height = int(screen_height * 0.95)
    
    analysis_window.geometry(f"{window_width}x{window_height}")
    analysis_window.configure(bg=COLORS["light_bg"])
    
    # Make window resizable
    analysis_window.resizable(True, True)
    
    # Center the window
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    analysis_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Create main container with Canvas and Scrollbar
    main_container = tk.Frame(analysis_window, bg=COLORS["light_bg"])
    main_container.pack(fill="both", expand=True)
    
    # Create a canvas for scrolling
    canvas = tk.Canvas(main_container, bg=COLORS["light_bg"], highlightthickness=0)
    scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    
    # Create a frame inside the canvas for content
    content_frame = tk.Frame(canvas, bg=COLORS["light_bg"])
    
    # Configure canvas scrolling
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Put the content frame in the canvas
    canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
    # Update scrollregion when content frame size changes
    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    content_frame.bind("<Configure>", configure_scroll_region)
    
    # Also update canvas window width
    def configure_canvas_window(event):
        canvas.itemconfig(canvas_window, width=event.width)
    
    canvas.bind("<Configure>", configure_canvas_window)
    
    # Header
    header_frame = tk.Frame(content_frame, bg=COLORS["primary"])
    header_frame.pack(fill="x", pady=(0, 30))
    
    header_content = tk.Frame(header_frame, bg=COLORS["primary"], padx=min(100, window_width//10), pady=30)
    header_content.pack(fill="x")
    
    tk.Label(
        header_content,
        text="🎉 Assessment Complete!",
        font=("Arial", 28, "bold"),
        bg=COLORS["primary"],
        fg="white"
    ).pack(pady=(0, 10))
    
    tk.Label(
        header_content,
        text=f"Congratulations {username}! Your emotional intelligence journey begins.",
        font=("Arial", 14),
        bg=COLORS["primary"],
        fg=COLORS["light_white"]  # Changed from rgba to light white
    ).pack()
    
    # Main content area
    main_content = tk.Frame(content_frame, bg=COLORS["light_bg"], padx=min(80, window_width//12), pady=20)
    main_content.pack(fill="both", expand=True)
    
    # Congratulations message
    tk.Label(
        main_content,
        text="Your Results Are Ready",
        font=("Arial", 22, "bold"),
        bg=COLORS["light_bg"],
        fg=COLORS["text"]
    ).pack(anchor="w", pady=(0, 10))
    
    tk.Label(
        main_content,
        text="Explore detailed insights and analysis options below:",
        font=("Arial", 14),
        bg=COLORS["light_bg"],
        fg=COLORS["subtext"]
    ).pack(anchor="w", pady=(0, 30))
    
    # Score Summary Card
    score_card = tk.Frame(main_content, bg=COLORS["card_bg"], relief="solid", borderwidth=1)
    score_card.pack(fill="x", pady=(0, 40))
    
    score_inner = tk.Frame(score_card, bg=COLORS["card_bg"], padx=40, pady=40)
    score_inner.pack(fill="both", expand=True)
    
    tk.Label(
        score_inner,
        text="Your EQ Score Summary",
        font=("Arial", 24, "bold"),
        bg=COLORS["card_bg"],
        fg=COLORS["text"]
    ).pack(pady=(0, 20))
    
    # Score display in center
    score_display_frame = tk.Frame(score_inner, bg=COLORS["card_bg"])
    score_display_frame.pack(pady=20)
    
    tk.Label(
        score_display_frame,
        text=f"{score}",
        font=("Arial", 48, "bold"),
        bg=COLORS["card_bg"],
        fg=COLORS["primary"]
    ).pack(side="left")
    
    tk.Label(
        score_display_frame,
        text=f" / {total_questions * 5}",
        font=("Arial", 32),
        bg=COLORS["card_bg"],
        fg=COLORS["subtext"]
    ).pack(side="left", padx=(10, 0), pady=(15, 0))
    
    # Average score
    avg_score = score / total_questions
    avg_frame = tk.Frame(score_inner, bg=COLORS["card_bg"])
    avg_frame.pack(pady=10)
    
    tk.Label(
        avg_frame,
        text="Average Score: ",
        font=("Arial", 16),
        bg=COLORS["card_bg"],
        fg=COLORS["subtext"]
    ).pack(side="left")
    
    tk.Label(
        avg_frame,
        text=f"{avg_score:.1f}",
        font=("Arial", 18, "bold"),
        bg=COLORS["card_bg"],
        fg=COLORS["primary"]
    ).pack(side="left", padx=(5, 0))
    
    tk.Label(
        avg_frame,
        text=" per question",
        font=("Arial", 16),
        bg=COLORS["card_bg"],
        fg=COLORS["subtext"]
    ).pack(side="left", padx=(5, 0))
    
    # Score interpretation
    if avg_score >= 4.0:
        interpretation = "🌟 Excellent emotional awareness and regulation skills!"
        interpretation_color = COLORS["success"]
    elif avg_score >= 3.0:
        interpretation = "👍 Good emotional intelligence with solid foundation!"
        interpretation_color = "#FFA000"
    else:
        interpretation = "📈 Great opportunity for emotional intelligence growth!"
        interpretation_color = COLORS["warning"]
    
    tk.Label(
        score_inner,
        text=interpretation,
        font=("Arial", 14, "italic"),
        bg=COLORS["card_bg"],
        fg=interpretation_color
    ).pack(pady=(20, 0))
    
    # Analysis Options Section
    analysis_header_frame = tk.Frame(main_content, bg=COLORS["light_bg"])
    analysis_header_frame.pack(fill="x", pady=(0, 20))
    
    tk.Label(
        analysis_header_frame,
        text="📊 Explore Your Results",
        font=("Arial", 26, "bold"),
        bg=COLORS["light_bg"],
        fg=COLORS["text"]
    ).pack(anchor="w")
    
    tk.Label(
        analysis_header_frame,
        text="Choose from our comprehensive analysis tools to gain deeper insights:",
        font=("Arial", 14),
        bg=COLORS["light_bg"],
        fg=COLORS["subtext"]
    ).pack(anchor="w", pady=(10, 0))
    
    # Analysis buttons grid - 2 columns
    buttons_container = tk.Frame(main_content, bg=COLORS["light_bg"])
    buttons_container.pack(fill="both", expand=True, pady=(0, 30))
    
    # Function definitions for buttons
    def open_dashboard():
        analysis_window.destroy()
        dashboard = AnalyticsDashboard(None, username)
        dashboard.open_dashboard()
        conn.close()
    
    def check_correlation():
        messagebox.showinfo("Correlation Analysis", 
            "This feature analyzes correlations between:\n\n"
            "• Your responses across different emotional domains\n"
            "• Age vs EQ score patterns and trends\n"
            "• Response patterns and emotional regulation\n"
            "• Question clusters and their relationships\n\n"
            "Feature coming in the next update!")
    
    def advanced_analysis():
        messagebox.showinfo("Advanced Analysis",
            "Advanced analysis includes:\n\n"
            "• Pattern recognition in emotional responses\n"
            "• Emotional intelligence sub-domains breakdown\n"
            "• Personalized growth recommendations\n"
            "• Comparative analysis with peer groups\n"
            "• Trend analysis across multiple assessments\n\n"
            "Feature coming soon!")
    
    def generate_report():
        messagebox.showinfo("Insights Report",
            "Your personalized insights report includes:\n\n"
            "• Strengths and areas for improvement\n"
            "• Actionable development recommendations\n"
            "• Progress tracking and milestone planning\n"
            "• Emotional intelligence development roadmap\n"
            "• Resource recommendations for growth\n\n"
            "Feature in development!")
    
    def take_another_test():
        analysis_window.destroy()
        conn.close()
        # Restart application
        main()
    
    def view_history():
        cursor.execute(
            "SELECT id, total_score, timestamp FROM scores WHERE username = ? ORDER BY timestamp DESC LIMIT 10",
            (username,)
        )
        history = cursor.fetchall()
        
        if history:
            history_text = f"Recent Tests for {username}:\n\n"
            for test_id, total_score, timestamp in history:
                try:
                    date_obj = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    date_str = date_obj.strftime("%b %d, %Y")
                except:
                    date_str = timestamp
                history_text += f"• Test #{test_id}: {total_score}/{total_questions*5} points ({date_str})\n"
            
            history_text += f"\nTotal tests completed: {len(history)}"
            messagebox.showinfo("Test History", history_text)
        else:
            messagebox.showinfo("Test History", "No test history found.")
    
    # Define button configurations
    button_configs = [
        {
            "text": "📈 Detailed Dashboard",
            "command": open_dashboard,
            "bg": COLORS["primary"],
            "description": "Interactive dashboard with charts, trends, and visual analytics"
        },
        {
            "text": "🔗 Check Correlation",
            "command": check_correlation,
            "bg": COLORS["correlation"],
            "description": "Analyze relationships between different emotional factors"
        },
        {
            "text": "📊 Advanced Analysis",
            "command": advanced_analysis,
            "bg": COLORS["analytics"],
            "description": "Deep dive into patterns, clusters, and predictive insights"
        },
        {
            "text": "📋 Generate Insights Report",
            "command": generate_report,
            "bg": COLORS["insights"],
            "description": "Personalized PDF report with actionable recommendations"
        },
        {
            "text": "🔄 Take Another Test",
            "command": take_another_test,
            "bg": COLORS["secondary"],
            "description": "Retake assessment to track progress and improvement"
        },
        {
            "text": "📜 View History",
            "command": view_history,
            "bg": COLORS["accent"],
            "description": "View past assessments and track your emotional growth"
        }
    ]
    
    # Create buttons in 2x3 grid
    for i, config in enumerate(button_configs):
        row = i // 2
        col = i % 2
        
        button_frame = tk.Frame(buttons_container, bg=COLORS["light_bg"], padx=15, pady=15)
        button_frame.grid(row=row, column=col, sticky="nsew", padx=15, pady=15)
        
        # Configure grid weights
        buttons_container.grid_rowconfigure(row, weight=1)
        buttons_container.grid_columnconfigure(col, weight=1)
        
        # Button
        btn = tk.Button(
            button_frame,
            text=config["text"],
            command=config["command"],
            bg=config["bg"],
            fg="white",
            font=("Arial", 14, "bold"),
            relief="flat",
            padx=30,
            pady=20,
            cursor="hand2",
            wraplength=250
        )
        btn.pack(fill="both", expand=True)
        
        # Description
        tk.Label(
            button_frame,
            text=config["description"],
            font=("Arial", 11),
            bg=COLORS["light_bg"],
            fg=COLORS["subtext"],
            wraplength=280,
            justify="center"
        ).pack(pady=(10, 0))
    
    # Bottom navigation frame
    bottom_frame = tk.Frame(content_frame, bg=COLORS["light_bg"], pady=30)
    bottom_frame.pack(fill="x", pady=(20, 0))
    
    bottom_inner = tk.Frame(bottom_frame, bg=COLORS["light_bg"])
    bottom_inner.pack(fill="x", padx=min(80, window_width//12))
    
    def return_to_main():
        analysis_window.destroy()
        conn.close()
        # Restart the main application
        main()
    
    tk.Button(
        bottom_inner,
        text="🏠 Return to Main Menu",
        command=return_to_main,
        bg="#607D8B",
        fg="white",
        font=("Arial", 12),
        relief="flat",
        padx=25,
        pady=12,
        cursor="hand2"
    ).pack(side="left", padx=10)
    
    def close_all():
        analysis_window.destroy()
        conn.close()
        exit()
    
    tk.Button(
        bottom_inner,
        text="Exit Application",
        command=close_all,
        bg="#757575",
        fg="white",
        font=("Arial", 12),
        relief="flat",
        padx=25,
        pady=12,
        cursor="hand2"
    ).pack(side="right", padx=10)
    
    # Add mousewheel scrolling
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    # Bind mousewheel for scrolling
    analysis_window.bind_all("<MouseWheel>", on_mousewheel)
    
    # Also bind for Linux
    analysis_window.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    analysis_window.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
    
    # Clean up bindings when window closes
    def on_close():
        analysis_window.unbind_all("<MouseWheel>")
        analysis_window.unbind_all("<Button-4>")
        analysis_window.unbind_all("<Button-5>")
        analysis_window.destroy()
        conn.close()
    
    analysis_window.protocol("WM_DELETE_WINDOW", on_close)
    
    analysis_window.mainloop()

# USER DETAILS WINDOW
root = tk.Tk()
root.title(i18n.get("user_details_title"))
root.geometry("450x450")
root.resizable(False, False)
root.configure(bg=COLORS["light_bg"])

# Language selector frame
lang_frame = tk.Frame(root)
lang_frame.pack(pady=10)

tk.Label(lang_frame, text=i18n.get("settings.language") + ":", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

current_lang = tk.StringVar(value=i18n.current_language)
lang_selector = ttk.Combobox(
    lang_frame, 
    textvariable=current_lang,
    values=list(I18nManager.SUPPORTED_LANGUAGES.keys()),
    state="readonly",
    width=10
)
lang_selector.pack(side=tk.LEFT, padx=5)

# Title label (will be updated on language change)
title_label = tk.Label(
    root,
    text=i18n.get("app_title"),
    font=("Arial", 20, "bold")
)
title_label.pack(pady=20)

# Name label and entry
name_label = tk.Label(root, text=i18n.get("enter_name"), font=("Arial", 15))
name_label.pack()
tk.Entry(root, textvariable=username, font=("Arial", 15), width=25).pack(pady=8)

# Age label and entry
age_label = tk.Label(root, text=i18n.get("enter_age"), font=("Arial", 15))
age_label.pack()
tk.Entry(root, textvariable=age, font=("Arial", 15), width=25).pack(pady=8)
    text="SoulSense Assessment",
    font=("Arial", 22, "bold"),
    bg=COLORS["light_bg"],
    fg=COLORS["text"]
).pack(pady=20)

tk.Label(root, text="Enter your name:", font=("Arial", 13), bg=COLORS["light_bg"], fg=COLORS["text"]).pack()
name_entry = tk.Entry(root, textvariable=tk.StringVar(), font=("Arial", 13), width=25, bg="white", relief="solid", borderwidth=1)
name_entry.pack(pady=5)

tk.Label(root, text="Enter your age:", font=("Arial", 13), bg=COLORS["light_bg"], fg=COLORS["text"]).pack()
age_entry = tk.Entry(root, textvariable=tk.StringVar(), font=("Arial", 13), width=25, bg="white", relief="solid", borderwidth=1)
age_entry.pack(pady=5)

def update_ui_language():
    """Update all UI elements when language changes"""
    global questions
    root.title(i18n.get("user_details_title"))
    title_label.config(text=i18n.get("app_title"))
    name_label.config(text=i18n.get("enter_name"))
    age_label.config(text=i18n.get("enter_age"))
    start_btn.config(text=i18n.get("start_assessment"))
    journal_btn.config(text=i18n.get("open_journal"))
    dashboard_btn.config(text=i18n.get("view_dashboard"))
    # Reload questions in new language
    questions = get_questions()

def on_language_change(event):
    """Handle language selection change"""
    new_lang = current_lang.get()
    if i18n.switch_language(new_lang):
        update_ui_language()

lang_selector.bind('<<ComboboxSelected>>', on_language_change)

def submit_details():
    if not username.get():
        messagebox.showerror(i18n.get("errors.empty_name"), i18n.get("errors.empty_name"))
        return
    
    if not age.get().isdigit():
        messagebox.showerror(i18n.get("errors.invalid_age"), i18n.get("errors.invalid_age"))
    username = name_entry.get().strip()
    age_str = age_entry.get().strip()
    
    if not username:
        messagebox.showerror("Error", "Please enter your name")
        return
    
    if not age_str.isdigit():
        messagebox.showerror("Error", "Please enter a valid age (numbers only)")

        return
    
    user_age = int(age_str)
    if user_age < 12:
        messagebox.showerror(i18n.get("errors.minimum_age"), i18n.get("errors.minimum_age"))
        return

    root.destroy()
    start_quiz(username, user_age)

start_btn = tk.Button(
    root,
    text=i18n.get("start_assessment"),
    command=submit_details,
    bg=COLORS["primary"],
    fg="white",

    font=("Arial", 14, "bold"),
    width=20
)
start_btn.pack(pady=15)
    font=("Arial", 13, "bold"),
    width=20,
    relief="flat",
    padx=20,
    pady=8,
    cursor="hand2"
).pack(pady=20)

# Initialize features
journal_feature = JournalFeature(root)

journal_btn = tk.Button(
    root,

    text=i18n.get("open_journal"),
    command=lambda: journal_feature.open_journal_window(username.get() or "Guest"),
    bg="#2196F3",
    fg="white",
    font=("Arial", 12),
    width=20
)
journal_btn.pack(pady=5)
    text="📝 Open Journal",
    command=lambda: journal_feature.open_journal_window(name_entry.get() or "Guest"),
    bg=COLORS["secondary"],
    fg="white",
    font=("Arial", 11),
    width=20,
    relief="flat",
    padx=15,
    pady=6,
    cursor="hand2"
).pack(pady=5)

dashboard_btn = tk.Button(
    root,
    text=i18n.get("view_dashboard"),
    command=lambda: AnalyticsDashboard(root, username.get() or "Guest").open_dashboard(),
    bg="#FF9800",
    fg="white",
    font=("Arial", 12),
    width=20
)
dashboard_btn.pack(pady=5)
    text="📊 View Dashboard",
    command=lambda: AnalyticsDashboard(root, name_entry.get() or "Guest").open_dashboard(),
    bg=COLORS["accent"],
    fg="white",
    font=("Arial", 11),
    width=20,
    relief="flat",
    padx=15,
    pady=6,
    cursor="hand2"
).pack(pady=5)

# QUIZ WINDOW
def start_quiz(username, age):

    # Get fresh i18n instance
    quiz_i18n = get_i18n()
    
    # Show ALL questions to EVERYONE, regardless of age
    # We ignore the age_min and age_max filters
    filtered_questions = questions  # All 5 questions for everyone
    
    # If you want MORE questions, add them to the questions list above
    # For example, add these additional questions:
    # questions.append({"text": "You can easily put yourself in someone else's shoes.", "age_min": 12, "age_max": 100})
    # questions.append({"text": "You stay calm under pressure.", "age_min": 12, "age_max": 100})
    # etc.

    quiz = tk.Tk()
    quiz.title(quiz_i18n.get("app_title"))
    quiz.geometry("750x550")

    # Store quiz state in a dictionary to avoid nonlocal issues
    filtered_questions = questions
    
    quiz = tk.Tk()
    quiz.title(f"SoulSense Assessment - {username}")
    quiz.geometry("850x650")
    quiz.configure(bg=COLORS["light_bg"])
    
    # Header frame
    header_frame = tk.Frame(quiz, bg=COLORS["primary"], height=80)
    header_frame.pack(fill="x", pady=(0, 20))
    header_frame.pack_propagate(False)
    
    tk.Label(
        header_frame,
        text="SoulSense EQ Assessment",
        font=("Arial", 20, "bold"),
        bg=COLORS["primary"],
        fg="white"
    ).pack(pady=20)
    
    # Main content frame with card-like appearance
    content_frame = tk.Frame(quiz, bg=COLORS["card_bg"], relief="solid", borderwidth=1)
    content_frame.pack(fill="both", expand=True, padx=40, pady=10)
    
    # Progress section
    progress_frame = tk.Frame(content_frame, bg=COLORS["card_bg"])
    progress_frame.pack(fill="x", pady=(20, 10), padx=30)
    
    quiz_state = {
        "current_q": 0,
        "score": 0,
        "responses": [],
        "username": username,
        "age": age
    }

    var = tk.IntVar()
    
    # Question counter with better styling
    counter_label = tk.Label(
        progress_frame,
        text="",
        font=("Arial", 12, "bold"),
        bg=COLORS["card_bg"],
        fg=COLORS["primary"]
    )
    counter_label.pack(side="left")
    
    # Progress bar
    progress_canvas = tk.Canvas(progress_frame, height=8, width=300, bg=COLORS["border"], highlightthickness=0)
    progress_canvas.pack(side="right")
    progress_bar = progress_canvas.create_rectangle(0, 0, 0, 8, fill=COLORS["primary"], outline="")
    
    # Question area
    question_area = tk.Frame(content_frame, bg=COLORS["card_bg"])
    question_area.pack(fill="both", expand=True, padx=30, pady=10)
    
    # Question label with better styling
    question_label = tk.Label(
        question_area,
        text="",
        wraplength=700,
        font=("Arial", 16),
        bg=COLORS["card_bg"],
        fg=COLORS["text"],
        justify="left"
    )
    question_label.pack(anchor="w", pady=(20, 30))
    
    # Options frame
    options_frame = tk.Frame(question_area, bg=COLORS["card_bg"])
    options_frame.pack(fill="both", expand=True, padx=10)
    
    options = [
        (quiz_i18n.get("quiz.strongly_disagree"), 1),
        (quiz_i18n.get("quiz.disagree"), 2),
        (quiz_i18n.get("quiz.neutral"), 3),
        (quiz_i18n.get("quiz.agree"), 4),
        (quiz_i18n.get("quiz.strongly_agree"), 5)
    ]
    
    # Create radio buttons with better styling
    radio_buttons = []
    for i, (text, val) in enumerate(options):
        rb_frame = tk.Frame(options_frame, bg=COLORS["card_bg"])
        rb_frame.pack(fill="x", pady=8)
        
        rb = tk.Radiobutton(
            rb_frame,
            text=text,
            variable=var,
            value=val,

            font=("Arial", 14)
        ).pack(anchor="w", padx=60, pady=2)

    # Question counter
    counter_label = tk.Label(
        quiz,
        text=quiz_i18n.get("quiz.question_counter", current=1, total=len(filtered_questions)),
        font=("Arial", 12, "bold"),
        fg="gray"
    )
    counter_label.pack(pady=5)


            font=("Arial", 13),
            bg=COLORS["card_bg"],
            fg=COLORS["text"],
            selectcolor=COLORS["primary"],
            activebackground=COLORS["card_bg"],
            activeforeground=COLORS["text"],
            cursor="hand2"
        )
        rb.pack(side="left")
        radio_buttons.append(rb)
        
        # Add hover effect
        def on_enter(e, rb=rb):
            rb.config(bg="#f5f5f5")
        def on_leave(e, rb=rb):
            rb.config(bg=COLORS["card_bg"])
        
        rb.bind("<Enter>", on_enter)
        rb.bind("<Leave>", on_leave)
    
    # Navigation buttons frame
    nav_frame = tk.Frame(content_frame, bg=COLORS["card_bg"])
    nav_frame.pack(fill="x", pady=30, padx=30)
    
    def update_progress():
        """Update progress bar and counter"""
        current_q = quiz_state["current_q"]
        total_q = len(filtered_questions)
        
        # Update counter
        counter_label.config(text=f"Question {current_q + 1} of {total_q}")
        
        # Update progress bar
        progress_width = (current_q / total_q) * 300 if total_q > 0 else 0
        progress_canvas.coords(progress_bar, 0, 0, progress_width, 8)
    
    def load_question():
        current_q = quiz_state["current_q"]
        question_label.config(text=filtered_questions[current_q]["text"])

        counter_label.config(text=quiz_i18n.get("quiz.question_counter", 
                                                 current=current_q + 1, 
                                                 total=len(filtered_questions)))

        if current_q < len(quiz_state["responses"]):
            var.set(quiz_state["responses"][current_q])
        else:
            var.set(0)
        
        update_progress()
    
    def update_navigation_buttons():
        current_q = quiz_state["current_q"]
        if current_q == 0:
            prev_btn.config(state="disabled", bg="#B0BEC5")
        else:
            prev_btn.config(state="normal", bg=COLORS["secondary"])
        
        if current_q == len(filtered_questions) - 1:

            next_btn.config(text=quiz_i18n.get("quiz.finish"))
        else:
            next_btn.config(text=quiz_i18n.get("quiz.next"))


            next_btn.config(text="Finish Assessment ✓")
        else:
            next_btn.config(text="Next Question →")

    def save_current_answer():
        current_answer = var.get()
        if current_answer > 0:
            current_q = quiz_state["current_q"]
            if current_q < len(quiz_state["responses"]):
                quiz_state["responses"][current_q] = current_answer
            else:
                quiz_state["responses"].append(current_answer)
    
    def previous_question():
        save_current_answer()
        if quiz_state["current_q"] > 0:
            quiz_state["current_q"] -= 1
            load_question()
            update_navigation_buttons()
    
    def next_question():
        current_q = quiz_state["current_q"]

        if var.get() == 0:

            messagebox.showwarning(quiz_i18n.get("quiz.warning"), 
                                  quiz_i18n.get("errors.select_option"))

            messagebox.showwarning("Selection Required", "Please select an option to continue.")

            return

        save_current_answer()
        var.set(0)
        
        if current_q < len(filtered_questions) - 1:
            quiz_state["current_q"] += 1
            load_question()
            update_navigation_buttons()
        else:
            quiz_state["score"] = sum(quiz_state["responses"])
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO scores (username, age, total_score, timestamp) VALUES (?, ?, ?, ?)",
                (quiz_state["username"], quiz_state["age"], quiz_state["score"], timestamp)
            )
            conn.commit()


            # Show completion message with options
            max_score = len(filtered_questions) * 5
            avg_score = quiz_state['score']/len(filtered_questions)
            
            result = messagebox.askyesno(
                quiz_i18n.get("results.completed"),
                f"{quiz_i18n.get('results.thank_you', username=quiz_state['username'])}\n"
                f"{quiz_i18n.get('results.your_score', score=quiz_state['score'], max_score=max_score)}\n"
                f"{quiz_i18n.get('results.average', average=f'{avg_score:.1f}')}\n\n"
                f"{quiz_i18n.get('results.view_dashboard_prompt')}"
            )

            # Store references before destroying quiz window
            username = quiz_state["username"]
            score = quiz_state["score"]
            age = quiz_state["age"]
            total_questions = len(filtered_questions)

            
            # Destroy the quiz window first
            quiz.destroy()
            
            # Now show analysis in a new main window
            show_analysis_complete(username, score, age, total_questions)
    
    # Previous button
    prev_btn = tk.Button(
        nav_frame,

        text=quiz_i18n.get("quiz.previous"),

        text="← Previous Question",

        command=previous_question,
        bg="#B0BEC5",
        fg="white",
        font=("Arial", 12, "bold"),
        width=18,
        relief="flat",
        padx=15,
        pady=10,
        cursor="hand2",
        state="disabled"
    )
    prev_btn.pack(side="left", padx=10)
    
    # Next button
    next_btn = tk.Button(
        nav_frame,

        text=quiz_i18n.get("quiz.next"),

        text="Next Question →",

        command=next_question,
        bg=COLORS["primary"],
        fg="white",
        font=("Arial", 12, "bold"),
        width=18,
        relief="flat",
        padx=15,
        pady=10,
        cursor="hand2"
    )
    next_btn.pack(side="right", padx=10)
    
    # Add keyboard shortcuts
    def on_key_press(event):
        if event.keysym == 'Left' and quiz_state["current_q"] > 0:
            previous_question()
        elif event.keysym == 'Right' or event.keysym == 'Return':
            next_question()
    
    quiz.bind('<Left>', on_key_press)
    quiz.bind('<Right>', on_key_press)
    quiz.bind('<Return>', on_key_press)
    
    # Initialize
    load_question()
    update_navigation_buttons()
    
    quiz.mainloop()

def main():
    """Main function to start the application"""
    root.mainloop()

if __name__ == "__main__":
    main()
