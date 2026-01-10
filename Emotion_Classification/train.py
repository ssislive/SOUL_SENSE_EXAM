import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from .dataset import load_training_data
from .features import build_vectorizer


DB_PATH = "db/soulsense.db"
MODEL_PATH = "Emotion_Classification/model.pkl"


def train():
    texts, labels = load_training_data(DB_PATH)

    vectorizer = build_vectorizer()
    X = vectorizer.fit_transform(texts)

    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    print(classification_report(y_test, preds))

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    joblib.dump(
        {"model": model, "vectorizer": vectorizer},
        MODEL_PATH
    )

    print("✅ Emotion classification model saved:", MODEL_PATH)


if __name__ == "__main__":
    train()
