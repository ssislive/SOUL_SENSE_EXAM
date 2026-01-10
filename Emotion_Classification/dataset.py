import sqlite3
import pandas as pd
import logging


def label_from_score(score: float) -> int:
    if score < -0.2:
        return 0  # negative
    elif score > 0.2:
        return 2  # positive
    return 1      # neutral


def load_training_data(db_path: str):
    conn = sqlite3.connect(db_path)

    try:
        journal_query = """
        SELECT entry_text, sentiment_score
        FROM journal_entries
        WHERE entry_text IS NOT NULL
          AND sentiment_score IS NOT NULL
        """
        df = pd.read_sql_query(journal_query, conn)

        if not df.empty:
            df["label"] = df["sentiment_score"].apply(label_from_score)
            logging.info("Loaded training data from journal_entries")
            return df["entry_text"], df["label"]

    except Exception:
        pass  
    try:
        response_query = """
        SELECT response_value
        FROM responses
        WHERE response_value IS NOT NULL
        """
        df = pd.read_sql_query(response_query, conn)

        if not df.empty:
            # Convert numeric responses into pseudo-text
            df["entry_text"] = df["response_value"].apply(
                lambda x: f"I feel {'very good' if x >= 3 else 'neutral' if x == 2 else 'bad'}"
            )
            df["label"] = df["response_value"].apply(
                lambda x: 2 if x >= 3 else 1 if x == 2 else 0
            )
            logging.info("Loaded training data from EQ responses")
            return df["entry_text"], df["label"]

    except Exception:
        pass

    conn.close()

    texts = [
        "I feel happy and confident",
        "I am calm and relaxed",
        "I feel stressed and overwhelmed",
        "I feel sad and unmotivated",
        "I feel neutral today"
    ]
    labels = [2, 2, 0, 0, 1]

    logging.warning("Using synthetic data for ML training")
    return texts, labels
