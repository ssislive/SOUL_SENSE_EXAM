import pytest
from unittest.mock import MagicMock
import sys
import os

# Update import to point to the actual class
from app.ml.risk_predictor import RiskPredictor

def test_ml_predictor_import():
    """Verify the class is importable"""
    assert RiskPredictor is not None

def test_ml_predictor_initialization_mocked(mocker):
    """
    Verify initialization doesn't crash if dependencies are mocked.
    """
    # Mock glob to return empty list or specific files
    mocker.patch("glob.glob", return_value=[])
    
    try:
        predictor = RiskPredictor(models_dir="mock_models")
        assert predictor is not None
        # Model should be None if no files found
        assert predictor.model is None
    except Exception as e:
        pytest.fail(f"ML Predictor initialization failed: {e}")

def test_predict_smoke(mocker):
    """Verify predict method returns expected structure (mocked model)"""
    # Mock glob to find a file
    mocker.patch("glob.glob", return_value=["models/risk_model_v1.pkl"])
    mocker.patch("os.path.getctime", return_value=1234567890)
    
    # Mock joblib load
    mock_model = MagicMock()
    mock_model.predict.return_value = ["Low Risk"]
    mock_model.predict_proba.return_value = [[0.9, 0.1, 0.0]]
    
    mocker.patch("joblib.load", return_value=mock_model)
    
    predictor = RiskPredictor(models_dir="models")
    
    # Test predict
    label = predictor.predict(total_score=10, sentiment_score=0.5, age=25)
    assert label == "Low Risk"
    
    # Test predict_with_explanation
    result = predictor.predict_with_explanation(
        responses=[], 
        age=25, 
        total_score=10, 
        sentiment_score=0.5
    )
    
    assert result["prediction_label"] == "Low Risk"
    assert result["confidence"] == 0.9
