"""
Evaluate All ML Models Script
Comprehensive evaluation of all ML models in Soul Sense EQ Test
Generates detailed metrics, visualizations, and comparison reports
"""

import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add experiments directory to path for legacy emotion classification support
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "experiments"))

from scripts.model_evaluation import ModelEvaluator, compare_models
from app.ml.predictor import SoulSenseMLPredictor
from emotion_classification.predict import EmotionPredictor
from emotion_classification.train import train as train_emotion_model
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize


def evaluate_depression_risk_predictor():
    """Evaluate the Depression Risk Predictor (Random Forest)"""
    print("\n" + "="*70)
    print("EVALUATING DEPRESSION RISK PREDICTOR")
    print("="*70)
    
    # Initialize predictor
    predictor = SoulSenseMLPredictor(use_versioning=False)
    
    # Generate test data (same distribution as training)
    np.random.seed(123)  # Different seed for test data
    n_test = 200
    
    X_test = np.zeros((n_test, len(predictor.feature_names)))
    y_test = []
    
    for i in range(n_test):
        # Generate individual question scores (1-5)
        q_scores = np.random.randint(1, 6, 5)
        
        # Calculate derived features
        total_score = q_scores.sum()
        age = np.random.randint(12, 50)
        avg_score = total_score / 5
        
        # Create feature vector
        X_test[i] = [
            q_scores[0], q_scores[1], q_scores[2], q_scores[3], q_scores[4],
            total_score, age, avg_score
        ]
        
        # Generate labels (same rules as training)
        if total_score <= 10 or avg_score <= 2:
            y_test.append(2)  # High risk
        elif total_score <= 15 or avg_score <= 3:
            y_test.append(1)  # Moderate risk
        else:
            y_test.append(0)  # Low risk
    
    y_test = np.array(y_test)
    
    # Scale features
    X_test_scaled = predictor.scaler.transform(X_test)
    
    # Make predictions
    y_pred = predictor.model.predict(X_test_scaled)
    y_proba = predictor.model.predict_proba(X_test_scaled)
    
    # Evaluate
    evaluator = ModelEvaluator(
        model_name="Depression_Risk_Predictor",
        model_type="classification"
    )
    
    metrics = evaluator.generate_full_report(
        y_true=y_test,
        y_pred=y_pred,
        y_proba=y_proba,
        class_names=predictor.class_names,
        output_dir="evaluation_results/depression_predictor"
    )
    
    return evaluator, metrics


def evaluate_emotion_classifier():
    """Evaluate the Emotion Classifier (Logistic Regression)"""
    print("\n" + "="*70)
    print("EVALUATING EMOTION CLASSIFIER")
    print("="*70)
    
    model_path = "Emotion_Classification/model.pkl"
    
    # Check if model exists
    if not os.path.exists(model_path):
        print("⚠️  Emotion classifier model not found. Training new model...")
        train_emotion_model()
    
    # Load model
    try:
        model_data = joblib.load(model_path)
        model = model_data['model']
        vectorizer = model_data['vectorizer']
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("   Please ensure the emotion classifier is properly trained.")
        return None, None
    
    # Generate synthetic test data for demonstration
    # In production, use real journal entries from database
    test_texts = [
        "I feel so happy and excited today! Everything is going great.",
        "Life is wonderful and I'm grateful for everything.",
        "I'm feeling sad and down. Nothing seems to work out.",
        "I feel anxious and worried about the future.",
        "Today was okay, nothing special happened.",
        "Just another regular day at work.",
        "I'm thrilled about the new opportunities coming my way!",
        "Feeling depressed and hopeless about everything.",
        "Had a neutral day, neither good nor bad.",
        "So excited and happy about my achievements!",
        "I feel terrible and everything is going wrong.",
        "Things are fine, no complaints.",
        "I'm overjoyed and can't stop smiling!",
        "Feeling miserable and upset about recent events.",
        "Today was average, nothing noteworthy.",
        "I'm ecstatic about the wonderful news!",
        "Feeling stressed and overwhelmed by problems.",
        "Just a normal day with routine activities.",
        "I feel blessed and content with my life.",
        "Experiencing sadness and frustration today."
    ]
    
    # True labels (0=Negative, 1=Neutral, 2=Positive)
    y_test = np.array([2, 2, 0, 0, 1, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0])
    
    # Transform and predict
    X_test = vectorizer.transform(test_texts)
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    
    # Evaluate
    evaluator = ModelEvaluator(
        model_name="Emotion_Classifier",
        model_type="classification"
    )
    
    class_names = ['Negative', 'Neutral', 'Positive']
    
    metrics = evaluator.generate_full_report(
        y_true=y_test,
        y_pred=y_pred,
        y_proba=y_proba,
        class_names=class_names,
        output_dir="evaluation_results/emotion_classifier"
    )
    
    return evaluator, metrics


def generate_summary_report(depression_metrics, emotion_metrics):
    """Generate a summary report comparing both models"""
    print("\n" + "="*70)
    print("GENERATING SUMMARY REPORT")
    print("="*70)
    
    os.makedirs("evaluation_results", exist_ok=True)
    
    with open("evaluation_results/EVALUATION_SUMMARY.md", 'w', encoding='utf-8') as f:
        f.write("# Model Evaluation Summary Report\n\n")
        f.write("## Soul Sense EQ Test - ML Models Performance\n\n")
        
        f.write("This report summarizes the evaluation metrics for all machine learning models in the Soul Sense EQ Test system.\n\n")
        
        f.write("---\n\n")
        
        # Depression Risk Predictor
        f.write("## 1. Depression Risk Predictor\n\n")
        f.write("**Model Type:** Random Forest Classifier  \n")
        f.write("**Purpose:** Predict depression risk levels from EQ questionnaire responses  \n")
        f.write("**Classes:** Low Risk, Moderate Risk, High Risk  \n\n")
        
        if depression_metrics:
            f.write("### Performance Metrics\n\n")
            f.write(f"- **Accuracy:** {depression_metrics['accuracy']:.4f} ({depression_metrics['accuracy']*100:.2f}%)  \n")
            f.write(f"- **Precision:** {depression_metrics['precision']:.4f}  \n")
            f.write(f"- **Recall:** {depression_metrics['recall']:.4f}  \n")
            f.write(f"- **F1-Score:** {depression_metrics['f1_score']:.4f}  \n")
            
            if 'auc_roc' in depression_metrics:
                f.write(f"- **AUC-ROC:** {depression_metrics['auc_roc']:.4f}  \n")
            
            f.write("\n### Per-Class Performance\n\n")
            if 'per_class' in depression_metrics:
                f.write("| Class | Precision | Recall | F1-Score |\n")
                f.write("|-------|-----------|--------|----------|\n")
                for class_name, metrics in depression_metrics['per_class'].items():
                    f.write(f"| {class_name} | {metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['f1_score']:.4f} |\n")
            
            f.write("\n### Interpretation\n\n")
            acc = depression_metrics['accuracy']
            if acc >= 0.9:
                f.write("✅ **Excellent** - Model shows outstanding performance.\n\n")
            elif acc >= 0.8:
                f.write("✅ **Good** - Model performs well for the task.\n\n")
            elif acc >= 0.7:
                f.write("⚠️ **Fair** - Model is acceptable but could be improved.\n\n")
            else:
                f.write("❌ **Poor** - Model needs significant improvement.\n\n")
        
        f.write("---\n\n")
        
        # Emotion Classifier
        f.write("## 2. Emotion Classifier\n\n")
        f.write("**Model Type:** Logistic Regression with TF-IDF  \n")
        f.write("**Purpose:** Classify emotional tone of journal entries  \n")
        f.write("**Classes:** Negative, Neutral, Positive  \n\n")
        
        if emotion_metrics:
            f.write("### Performance Metrics\n\n")
            f.write(f"- **Accuracy:** {emotion_metrics['accuracy']:.4f} ({emotion_metrics['accuracy']*100:.2f}%)  \n")
            f.write(f"- **Precision:** {emotion_metrics['precision']:.4f}  \n")
            f.write(f"- **Recall:** {emotion_metrics['recall']:.4f}  \n")
            f.write(f"- **F1-Score:** {emotion_metrics['f1_score']:.4f}  \n")
            
            if 'auc_roc' in emotion_metrics:
                f.write(f"- **AUC-ROC:** {emotion_metrics['auc_roc']:.4f}  \n")
            
            f.write("\n### Per-Class Performance\n\n")
            if 'per_class' in emotion_metrics:
                f.write("| Class | Precision | Recall | F1-Score |\n")
                f.write("|-------|-----------|--------|----------|\n")
                for class_name, metrics in emotion_metrics['per_class'].items():
                    f.write(f"| {class_name} | {metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['f1_score']:.4f} |\n")
            
            f.write("\n### Interpretation\n\n")
            acc = emotion_metrics['accuracy']
            if acc >= 0.9:
                f.write("✅ **Excellent** - Model shows outstanding performance.\n\n")
            elif acc >= 0.8:
                f.write("✅ **Good** - Model performs well for the task.\n\n")
            elif acc >= 0.7:
                f.write("⚠️ **Fair** - Model is acceptable but could be improved.\n\n")
            else:
                f.write("❌ **Poor** - Model needs significant improvement.\n\n")
        
        f.write("---\n\n")
        
        # Overall Summary
        f.write("## Overall Assessment\n\n")
        
        if depression_metrics and emotion_metrics:
            avg_acc = (depression_metrics['accuracy'] + emotion_metrics['accuracy']) / 2
            avg_f1 = (depression_metrics['f1_score'] + emotion_metrics['f1_score']) / 2
            
            f.write(f"### Aggregate Statistics\n\n")
            f.write(f"- **Average Accuracy:** {avg_acc:.4f} ({avg_acc*100:.2f}%)  \n")
            f.write(f"- **Average F1-Score:** {avg_f1:.4f}  \n\n")
            
            f.write("### Model Comparison\n\n")
            f.write("| Model | Accuracy | F1-Score | Best For |\n")
            f.write("|-------|----------|----------|----------|\n")
            f.write(f"| Depression Risk Predictor | {depression_metrics['accuracy']:.4f} | {depression_metrics['f1_score']:.4f} | Structured questionnaire data |\n")
            f.write(f"| Emotion Classifier | {emotion_metrics['accuracy']:.4f} | {emotion_metrics['f1_score']:.4f} | Unstructured text analysis |\n\n")
        
        f.write("---\n\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        f.write("### For Developers\n\n")
        f.write("- Monitor model performance on real-world data regularly  \n")
        f.write("- Collect user feedback to identify areas for improvement  \n")
        f.write("- Consider retraining models when performance degrades  \n")
        f.write("- Implement A/B testing for model updates  \n\n")
        
        f.write("### For Researchers\n\n")
        f.write("- Validate models on larger, diverse datasets  \n")
        f.write("- Test for bias across demographic groups  \n")
        f.write("- Explore ensemble methods for improved performance  \n")
        f.write("- Document limitations and ethical considerations  \n\n")
        
        f.write("### For Users\n\n")
        f.write("- Understand that predictions are probabilistic, not deterministic  \n")
        f.write("- Use insights as guidance, not clinical diagnosis  \n")
        f.write("- Consult mental health professionals for serious concerns  \n")
        f.write("- Provide feedback to help improve the system  \n\n")
        
        f.write("---\n\n")
        
        # Technical Details
        f.write("## Technical Details\n\n")
        f.write("### Evaluation Methodology\n\n")
        f.write("**Metrics Used:**\n\n")
        f.write("- **Accuracy:** Proportion of correct predictions  \n")
        f.write("- **Precision:** Proportion of positive predictions that are correct  \n")
        f.write("- **Recall:** Proportion of actual positives correctly identified  \n")
        f.write("- **F1-Score:** Harmonic mean of precision and recall  \n")
        f.write("- **AUC-ROC:** Area under the receiver operating characteristic curve  \n\n")
        
        f.write("**Why These Metrics Matter:**\n\n")
        f.write("- **Accuracy** provides overall performance assessment  \n")
        f.write("- **Precision** indicates reliability of positive predictions  \n")
        f.write("- **Recall** measures ability to find all positive cases  \n")
        f.write("- **F1-Score** balances precision and recall  \n")
        f.write("- **AUC-ROC** evaluates model's discrimination ability  \n\n")
        
        f.write("### RMSE Note\n\n")
        f.write("**RMSE (Root Mean Squared Error)** is primarily used for regression tasks where the model predicts continuous values. ")
        f.write("Both models in Soul Sense are **classification models** (predicting categories, not continuous values), so RMSE is not applicable. ")
        f.write("For classification tasks, **accuracy**, **precision**, **recall**, and **F1-score** are the appropriate metrics.\n\n")
        
        f.write("---\n\n")
        
        f.write(f"**Report Generated:** {depression_metrics.get('timestamp', 'N/A') if depression_metrics else 'N/A'}  \n")
        f.write(f"**Evaluation Framework:** Soul Sense Model Evaluation Module  \n")
        f.write(f"**Reference:** See [RESEARCH_REFERENCES.md](../RESEARCH_REFERENCES.md) for academic citations  \n")
    
    print("✅ Summary report saved to: evaluation_results/EVALUATION_SUMMARY.md")


def main():
    """Main evaluation pipeline"""
    print("\n" + "="*70)
    print("SOUL SENSE EQ TEST - COMPREHENSIVE MODEL EVALUATION")
    print("="*70)
    print("\nThis script evaluates all ML models with comprehensive metrics:")
    print("  • Accuracy, Precision, Recall, F1-Score")
    print("  • Per-class performance metrics")
    print("  • Confusion matrices and ROC curves")
    print("  • Detailed evaluation reports")
    print("\nNote: RMSE is not applicable for classification models.")
    print("="*70)
    
    try:
        # Evaluate Depression Risk Predictor
        depression_evaluator, depression_metrics = evaluate_depression_risk_predictor()
        
        # Evaluate Emotion Classifier
        emotion_evaluator, emotion_metrics = evaluate_emotion_classifier()
        
        # Generate comparison
        if depression_evaluator and emotion_evaluator:
            print("\n" + "="*70)
            print("GENERATING MODEL COMPARISON")
            print("="*70)
            compare_models(
                [depression_evaluator, emotion_evaluator],
                output_path="evaluation_results/model_comparison.png"
            )
        
        # Generate summary report
        generate_summary_report(depression_metrics, emotion_metrics)
        
        print("\n" + "="*70)
        print("EVALUATION COMPLETE!")
        print("="*70)
        print("\n📁 All results saved to: evaluation_results/")
        print("\n📊 Generated Files:")
        print("   • Depression Predictor metrics and visualizations")
        print("   • Emotion Classifier metrics and visualizations")
        print("   • Model comparison chart")
        print("   • Comprehensive summary report (EVALUATION_SUMMARY.md)")
        print("\n✅ Evaluation completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
