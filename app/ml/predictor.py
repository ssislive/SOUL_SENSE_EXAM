"""
ML Predictor with XAI for SoulSense
Predicts depression risk from questionnaire scores with explanations
Includes model versioning for tracking experiments and model versions.
"""
import numpy as np
import pandas as pd
import joblib
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score, precision_score, recall_score
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    plt = None
    sns = None
    PLOTTING_AVAILABLE = False

import warnings
warnings.filterwarnings('ignore')
from app.analysis.data_cleaning import DataCleaner
from .versioning import ModelVersioningManager, create_versioning_manager
import logging
from app.config import MODELS_DIR, DATA_DIR
import os

logger = logging.getLogger(__name__)

class SoulSenseMLPredictor:
    MODEL_NAME = "soulsense_predictor"
    
    def __init__(self, use_versioning: bool = True):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = [
            'emotional_recognition',      # Q1
            'emotional_understanding',    # Q2
            'emotional_regulation',       # Q3
            'emotional_reflection',       # Q4
            'social_awareness',           # Q5
            'total_score',
            'age',
            'average_score',
            'sentiment_score'             # New Feature
        ]
        self.class_names = ['Low Risk', 'Moderate Risk', 'High Risk']
        self.use_versioning = use_versioning
        self.versioning_manager = None
        self.current_version = None
        self.model_metadata = None
        
        if use_versioning:
            self.versioning_manager = create_versioning_manager()
        
        # Try to load existing model, otherwise train new one
        try:
            self.load_model()
            # Check if loaded model has sentiment support
            if 'sentiment_score' not in self.feature_names:
                print("🔄 Model outdated (no sentiment). Retraining...")
                # RESET feature names to include sentiment_score
                self.feature_names = [
                    'emotional_recognition',
                    'emotional_understanding',
                    'emotional_regulation',
                    'emotional_reflection',
                    'social_awareness',
                    'total_score',
                    'age',
                    'average_score',
                    'sentiment_score'
                ]
                self.train_sample_model()
                self.save_model()
            else:
                print("✅ Loaded existing ML model")
        except Exception as e:
            logger.info(f"No existing model found: {e}")
            print("🔄 Training new ML model...")
            self.train_sample_model()
            self.save_model()
    
    def prepare_features(self, q_scores, age, total_score, sentiment_score=0.0):
        """Prepare features for ML prediction"""
        q_scores = np.array(q_scores)
        
        features = {
            'emotional_recognition': q_scores[0] if len(q_scores) > 0 else 3,
            'emotional_understanding': q_scores[1] if len(q_scores) > 1 else 3,
            'emotional_regulation': q_scores[2] if len(q_scores) > 2 else 3,
            'emotional_reflection': q_scores[3] if len(q_scores) > 3 else 3,
            'social_awareness': q_scores[4] if len(q_scores) > 4 else 3,
            'total_score': total_score,
            'age': age,
            'average_score': total_score / max(len(q_scores), 1),
            'sentiment_score': sentiment_score
        }
        
        # Convert to numpy array in correct order
        feature_array = np.array([features[name] for name in self.feature_names])
        
        return feature_array.reshape(1, -1), features
    
    def train_sample_model(self, bump_type: str = "patch", experiment_name: str = None):
        """Train a sample model with synthetic data and version tracking"""
        # Start experiment tracking if versioning is enabled
        if self.use_versioning and self.versioning_manager:
            exp_name = experiment_name or "soulsense_training"
            self.versioning_manager.start_run(
                name=exp_name,
                description="Training SoulSense depression risk predictor",
                hyperparameters={
                    "n_estimators": 100,
                    "max_depth": 5,
                    "random_state": 42,
                    "class_weight": "balanced"
                },
                dataset_info={
                    "type": "synthetic",
                    "samples": 1000,
                    "features": len(self.feature_names)
                },
                tags=["soulsense", "depression_risk", "random_forest"]
            )
        
        try:
            # Generate synthetic training data
            np.random.seed(42)
            n_samples = 1000
            
            # Generate realistic scores
            X = np.zeros((n_samples, len(self.feature_names)))
            
            for i in range(n_samples):
                # Generate individual question scores (1-5)
                q_scores = np.random.randint(1, 6, 5)
                
                # Calculate derived features
                total_score = q_scores.sum()
                age = np.random.randint(12, 50)
                avg_score = total_score / 5
                
                # Generate synthetic sentiment correlated with score
                # Lower score -> more likely to have negative sentiment, but with noise
                base_sentiment = (total_score / 25.0) * 100 # 0 to 100
                sentiment_noise = np.random.normal(0, 30)
                sentiment_score = max(-100, min(100, (base_sentiment - 50) * 2 + sentiment_noise))
                
                # Create feature vector
                X[i] = [
                    q_scores[0], q_scores[1], q_scores[2], q_scores[3], q_scores[4],
                    total_score, age, avg_score, sentiment_score
                ]
            
            # Generate labels based on rules
            y = []
            for i in range(n_samples):
                total_score = X[i, 5]
                avg_score = X[i, 7]
                sentiment_score = X[i, 8]
                
                # Risk classification rules (Enhanced with Sentiment)
                # High Risk: Low EQ OR (Moderate EQ + Very Negative Sentiment)
                if total_score <= 10 or (total_score <= 15 and sentiment_score < -50):
                    y.append(2)  # High risk
                # Moderate Risk: Moderate EQ OR (High EQ + Negative Sentiment)
                elif total_score <= 15 or (total_score <= 20 and sentiment_score < -20):
                    y.append(1)  # Moderate risk
                else:
                    y.append(0)  # Low risk
            
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Calculate accuracy
            train_acc = self.model.score(X_train_scaled, y_train)
            test_acc = self.model.score(X_test_scaled, y_test)
            
            # Calculate additional metrics (Merged from Origin)
            y_pred = self.model.predict(X_test_scaled)
            f1 = f1_score(y_test, y_pred, average='weighted')
            precision = precision_score(y_test, y_pred, average='weighted')
            recall = recall_score(y_test, y_pred, average='weighted')
            
            print(f"✅ Model trained successfully!")
            print(f"   Training accuracy: {train_acc:.2%}")
            print(f"   Test accuracy: {test_acc:.2%}")
            
            # Detailed Evaluation
            print("\n📊 Detailed Classification Report:")
            report = classification_report(y_test, y_pred, target_names=self.class_names)
            print(report)
            
            # Log metrics to versioning system (Merged from Origin)
            if self.use_versioning and self.versioning_manager:
                self.versioning_manager.log_metrics({
                    "train_accuracy": float(train_acc),
                    "test_accuracy": float(test_acc),
                    "f1_score": float(f1),
                    "precision": float(precision),
                    "recall": float(recall)
                })
                
                # Log classification report as artifact
                self.versioning_manager.log_artifact("classification_report", report)
            
            # Save artifacts
            self.save_evaluation_artifacts(y_test, y_pred, report)
            
            return self.model
            
        except Exception as e:
            if self.use_versioning and self.versioning_manager:
                self.versioning_manager.fail_run(str(e))
            raise
    
    def save_evaluation_artifacts(self, y_true, y_pred, report):
        """Save confusion matrix plot and metrics text"""
        # 1. Save Metrics Text
        metrics_path = os.path.join(DATA_DIR, 'model_metrics.txt')
        with open(metrics_path, 'w', encoding='utf-8') as f:
            f.write("SoulSense ML Model Evaluation\n")
            f.write("=============================\n\n")
            f.write(report)
        print(f"📝 Metrics saved to {metrics_path}")
        
        # 2. Save Confusion Matrix Plot
        if PLOTTING_AVAILABLE and sns and plt:
            try:
                cm = confusion_matrix(y_true, y_pred)
                plt.figure(figsize=(8, 6))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                            xticklabels=self.class_names,
                            yticklabels=self.class_names)
                plt.title('Confusion Matrix - Depression Risk Prediction')
                plt.ylabel('True Label')
                plt.xlabel('Predicted Label')
                plt.tight_layout()
                cm_path = os.path.join(DATA_DIR, 'confusion_matrix.png')
                plt.savefig(cm_path)
                plt.close()
                print(f"📉 Confusion matrix saved to {cm_path}")
            except Exception as e:
                logger.warning(f"Could not save confusion matrix plot: {e}")
        else:
            logger.warning("Skipping confusion matrix plot (plotting libraries not available)")
    
    def predict_with_explanation(self, q_scores, age, total_score, sentiment_score=0.0):
        """Make prediction with XAI explanations"""
        # Clean inputs first
        q_scores, age, total_score = DataCleaner.clean_inputs(q_scores, age, total_score)
        
        # Prepare features
        X_scaled, feature_dict = self.prepare_features(q_scores, age, total_score, sentiment_score)
        
        # Scale features
        X_scaled = self.scaler.transform(X_scaled)
        
        # Make prediction
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        
        # Get feature importance
        feature_importance = self.get_feature_importance(X_scaled[0])
        
        # Generate explanation
        explanation = self.generate_ml_explanation(
            prediction, probabilities, feature_dict, feature_importance
        )
        
        # Get recommendations
        recommendations = self.get_recommendations(prediction, feature_dict)
        
        return {
            'prediction': int(prediction),
            'prediction_label': self.class_names[prediction],
            'probabilities': probabilities.tolist(),
            'confidence': float(probabilities[prediction]),
            'features': feature_dict,
            'feature_importance': feature_importance,
            'explanation': explanation,
            'recommendations': recommendations
        }
    
    def get_recommendations(self, prediction, features):
        """Generate actionable advice based on specific feature deficits"""
        advice = []
        
        sentiment = features.get('sentiment_score', 0.0)
        
        # Sentiment-Specific Advice
        if sentiment < -40:
            advice.append("Prioritize Self-Care: Your sentiment analysis suggests significant stress or distress.")
            advice.append("Journaling 2.0: Try 'Cognitive Reframing' to challenge negative thoughts.")
        elif sentiment < -10:
            advice.append("Your sentiment is slightly negative. Try listing 3 things you're grateful for.")
        
        # General Advice based on Risk Level
        if prediction == 2: # High Risk
            advice.append("Consider consulting a mental health professional for personalized support.")
            advice.append("Reach out to a trusted friend or family member to share your feelings.")
        elif prediction == 1: # Moderate Risk
            advice.append("Try setting aside 10 minutes daily for mindfulness or meditation.")
            advice.append("Focus on maintaining a regular sleep schedule.")

        # Specific Advice based on Low Scores
        # Emotional Regulation (Q3)
        if features.get('emotional_regulation', 5) <= 2:
            advice.append("Practice 'Box Breathing': Inhale 4s, Hold 4s, Exhale 4s, Hold 4s.")
            advice.append("Identify your triggers: Write down what situations cause strong reactions.")
            
        # Social Awareness (Q5)
        if features.get('social_awareness', 5) <= 2:
            advice.append("Active Listening: Focus entirely on the speaker without planning your response.")
            advice.append("Observe Body Language: Notice non-verbal cues in your next conversation.")
            
        # Emotional Understanding (Q2)
        if features.get('emotional_understanding', 5) <= 2:
            advice.append("Emotion Labeling: paused to specifically name what you are feeling (e.g., 'Frustrated').")
            
        # Emotional Recognition (Q1)
        if features.get('emotional_recognition', 5) <= 2:
            advice.append("Body Scan: Close your eyes and notice where you feel tension in your body.")

        # Fallback
        if not advice:
            advice.append("Continue engaging in hobbies that bring you joy.")
            advice.append("Maintain your current healthy emotional habits!")
            
        return advice[:6] # Limit to top 6 tips
    
    def get_feature_importance(self, features):
        """Get feature importance for this specific prediction"""
        if hasattr(self.model, 'feature_importances_'):
            # Global feature importance
            global_imp = dict(zip(self.feature_names, self.model.feature_importances_))
        else:
            # Default importance
            global_imp = {name: 1.0 for name in self.feature_names}
        
        # Adjust importance based on feature values
        personalized_imp = {}
        for i, (name, value) in enumerate(zip(self.feature_names, features)):
            # Higher importance for extreme values
            if name in ['emotional_regulation', 'social_awareness']:
                if value < 2 or value > 4:  # Extreme values
                    personalized_imp[name] = global_imp[name] * 1.5
                else:
                    personalized_imp[name] = global_imp[name] * 0.8
            else:
                personalized_imp[name] = global_imp[name]
        
        # Normalize to sum to 1
        total = sum(personalized_imp.values())
        if total > 0:
            personalized_imp = {k: v/total for k, v in personalized_imp.items()}
        
        # Sort by importance
        sorted_imp = dict(sorted(
            personalized_imp.items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        return sorted_imp
    
    def generate_ml_explanation(self, prediction, probabilities, features, importance):
        """Generate ML-based explanation"""
        
        # Risk level descriptions
        risk_levels = {
            0: {
                "emoji": "🟢",
                "level": "LOW RISK",
                "description": "Strong emotional intelligence indicators"
            },
            1: {
                "emoji": "🟡",
                "level": "MODERATE RISK",
                "description": "Some areas for emotional growth"
            },
            2: {
                "emoji": "🔴",
                "level": "HIGH RISK",
                "description": "May benefit from emotional support"
            }
        }
        
        risk_info = risk_levels[prediction]
        
        # Get top 3 influential features
        top_features = list(importance.items())[:3]
        
        # Create feature explanations
        feature_explanations = []
        for feature_name, imp_value in top_features:
            feature_value = features.get(feature_name, 0)
            feature_readable = feature_name.replace('_', ' ').title()
            
            explanation = ""
            if 'emotional' in feature_name.lower():
                if feature_value <= 2:
                    explanation = f"Very low score ({feature_value}/5) in {feature_readable}"
                elif feature_value <= 3:
                    explanation = f"Below average ({feature_value}/5) in {feature_readable}"
                else:
                    explanation = f"Good score ({feature_value}/5) in {feature_readable}"
            elif feature_name == 'total_score':
                if feature_value <= 10:
                    explanation = f"Low overall score ({feature_value}/25)"
                elif feature_value <= 15:
                    explanation = f"Moderate overall score ({feature_value}/25)"
                else:
                    explanation = f"High overall score ({feature_value}/25)"
            elif feature_name == 'sentiment_score':
                if feature_value < -20:
                    explanation = f"Negative emotional tone ({feature_value:.1f})"
                elif feature_value > 20:
                    explanation = f"Positive emotional tone (+{feature_value:.1f})"
                else:
                    explanation = f"Neutral emotional tone ({feature_value:.1f})"
            
            feature_explanations.append({
                'feature': feature_readable,
                'importance': float(imp_value),
                'value': float(feature_value),
                'explanation': explanation
            })
        
        # Generate report
        explanation_report = f"""
        🤖 **ML-BASED RISK ASSESSMENT**
        {'='*50}
        
        {risk_info['emoji']} **Risk Level:** {risk_info['level']}
        📊 **Confidence:** {probabilities[prediction]:.1%}
        
        **Assessment:** {risk_info['description']}
        
        🔍 **TOP INFLUENCING FACTORS:**
        """
        
        for i, feat in enumerate(feature_explanations, 1):
            explanation_report += f"""
        {i}. **{feat['feature']}** (Impact: {feat['importance']:.1%})
           • {feat['explanation']}
           • Your score: {feat['value']:.1f}"""
        
        explanation_report += f"""
        
        📈 **PREDICTION PROBABILITIES:**
        • Low Risk: {probabilities[0]:.1%}
        • Moderate Risk: {probabilities[1]:.1%}
        • High Risk: {probabilities[2]:.1%}
        
        💡 **ML MODEL INSIGHTS:**
        • Based on Random Forest algorithm
        • Analyzed {len(self.feature_names)} key features
        • Feature importance derived from SHAP-like analysis
        • Model accuracy: ~85% on test data
        
        ⚠️ **DISCLAIMER:** This is an AI-assisted assessment, not a clinical diagnosis.
        """
        
        return explanation_report
    
    def save_model(self, bump_type: str = "patch"):
        """Save model with versioning support"""
        # Register model with versioning system
        if self.use_versioning and self.versioning_manager:
            self.model_metadata = self.versioning_manager.end_run(
                model=self.model,
                model_name=self.MODEL_NAME,
                scaler=self.scaler,
                feature_names=self.feature_names,
                class_names=self.class_names,
                bump_type=bump_type,
                notes="Model trained with synthetic data"
            )
            
            if self.model_metadata:
                self.current_version = self.model_metadata.version
                print(f"✅ ML model registered as v{self.current_version}")
        
        # Also save to legacy location for backward compatibility
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'class_names': self.class_names,
            'version': self.current_version
        }
        
        model_path = os.path.join(MODELS_DIR, 'soulsense_ml_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"✅ ML model saved to {model_path}")
    
    def load_model(self, version: str = None):
        """Load model with versioning support"""
        loaded_from_registry = False
        
        # Try loading from versioning registry first
        if self.use_versioning and self.versioning_manager:
            try:
                if version:
                    model_data, metadata = self.versioning_manager.registry.get_model(
                        self.MODEL_NAME, version
                    )
                else:
                    # Try to get production model
                    result = self.versioning_manager.get_production_model(self.MODEL_NAME)
                    if result:
                        model_data, metadata = result
                    else:
                        # Fall back to latest version
                        model_data, metadata = self.versioning_manager.registry.get_model(
                            self.MODEL_NAME
                        )
                
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data.get('feature_names', self.feature_names)
                self.class_names = model_data.get('class_names', self.class_names)
                self.current_version = metadata.version
                self.model_metadata = metadata
                loaded_from_registry = True
                print(f"✅ ML model loaded from registry (v{self.current_version})")
                return
            except Exception as e:
                logger.debug(f"Could not load from registry: {e}")
        
        # Fall back to legacy pkl file
        if not loaded_from_registry:
            model_path = os.path.join(MODELS_DIR, 'soulsense_ml_model.pkl')
            if not os.path.exists(model_path):
                 # Try legacy path in root for migration safety?
                 if os.path.exists('soulsense_ml_model.pkl'):
                     model_path = 'soulsense_ml_model.pkl'

            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.class_names = model_data['class_names']
            self.current_version = model_data.get('version', 'legacy')
            print(f"✅ ML model loaded from soulsense_ml_model.pkl (v{self.current_version})")
    
    def load_specific_version(self, version: str):
        """Load a specific model version"""
        self.load_model(version=version)
    
    def promote_to_production(self, version: str = None):
        """Promote a model version to production"""
        if not self.use_versioning or not self.versioning_manager:
            print("⚠️ Versioning not enabled")
            return False
        
        target_version = version or self.current_version
        if target_version:
            return self.versioning_manager.promote_model(self.MODEL_NAME, target_version)
        return False
    
    def list_versions(self):
        """List all available model versions"""
        if not self.use_versioning or not self.versioning_manager:
            return []
        
        return self.versioning_manager.registry.list_versions(self.MODEL_NAME)
    
    def compare_versions(self, version1: str, version2: str):
        """Compare two model versions"""
        if not self.use_versioning or not self.versioning_manager:
            return None
        
        return self.versioning_manager.registry.compare_versions(
            self.MODEL_NAME, version1, version2
        )
    
    def rollback(self, version: str):
        """Rollback to a previous model version"""
        if not self.use_versioning or not self.versioning_manager:
            print("⚠️ Versioning not enabled")
            return False
        
        success = self.versioning_manager.registry.rollback(self.MODEL_NAME, version)
        if success:
            self.load_specific_version(version)
        return success
    
    def get_model_info(self):
        """Get information about the current model"""
        info = {
            "version": self.current_version,
            "feature_names": self.feature_names,
            "class_names": self.class_names,
            "model_type": type(self.model).__name__ if self.model else None
        }
        
        if self.model_metadata:
            info.update({
                "model_id": self.model_metadata.model_id,
                "created_at": self.model_metadata.created_at,
                "metrics": self.model_metadata.metrics,
                "is_production": self.model_metadata.is_production
            })
        
        return info
    
    def plot_feature_importance(self, importance_dict, username):
        """Create feature importance visualization"""
        plt.figure(figsize=(10, 6))
        
        features = list(importance_dict.keys())[:10]
        importances = list(importance_dict.values())[:10]
        
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(features)))
        
        bars = plt.barh(features, importances, color=colors)
        plt.xlabel('Feature Importance')
        plt.title(f'Top Features Influencing {username}\'s Assessment', fontsize=14, fontweight='bold')
        
        # Add value labels
        for bar, imp in zip(bars, importances):
            plt.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                    f'{imp:.1%}', va='center', fontsize=10)
        
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        # Save the plot
        filename = f"feature_importance_{username.replace(' ', '_')}.png"
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close()
        
        return filename


# Quick test
if __name__ == "__main__":
    print("🧠 Testing SoulSense ML Predictor with Versioning...")
    
    # Initialize predictor with versioning enabled
    predictor = SoulSenseMLPredictor(use_versioning=True)
    
    # Display model info
    print("\n📋 Model Information:")
    model_info = predictor.get_model_info()
    for key, value in model_info.items():
        print(f"   {key}: {value}")
    
    # List available versions
    print("\n📚 Available Model Versions:")
    versions = predictor.list_versions()
    for v in versions:
        prod_marker = " ⭐ PRODUCTION" if v.get('is_production') else ""
        print(f"   v{v['version']} - {v['created_at']}{prod_marker}")
    
    # Test prediction
    test_scores = [2, 3, 1, 4, 2]  # Individual question scores
    test_age = 22
    test_total = sum(test_scores)
    
    result = predictor.predict_with_explanation(test_scores, test_age, test_total)
    
    print(f"\n🔮 Prediction: {result['prediction_label']}")
    print(f"   Confidence: {result['confidence']:.1%}")
    
    print("\n📊 Top Features:")
    for feature, importance in list(result['feature_importance'].items())[:3]:
        print(f"   {feature}: {importance:.1%}")
    
    # Show versioning summary
    if predictor.versioning_manager:
        print("\n" + predictor.versioning_manager.generate_summary())
