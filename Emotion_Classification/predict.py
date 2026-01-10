import joblib
from Emotion_Classification.labels import EMOTION_LABELS

MODEL_PATH = "Emotion_Classification/model.pkl"

_bundle = joblib.load(MODEL_PATH)
_model = _bundle["model"]
_vectorizer = _bundle["vectorizer"]


def predict_emotion(text: str) -> str:
    X = _vectorizer.transform([text])
    label = _model.predict(X)[0]
    return EMOTION_LABELS[label]
