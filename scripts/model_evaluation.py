"""
Model Evaluation Metrics Module
Comprehensive evaluation for ML models in Soul Sense EQ Test
Includes accuracy, precision, recall, F1-score, and RMSE where applicable
"""

import numpy as np
import pandas as pd
import joblib
import os
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score,
    classification_report,
    confusion_matrix,
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    roc_auc_score,
    roc_curve
)
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json


class ModelEvaluator:
    """Comprehensive model evaluation and metrics reporting"""
    
    def __init__(self, model_name, model_type="classification"):
        """
        Initialize evaluator
        
        Args:
            model_name: Name of the model being evaluated
            model_type: "classification" or "regression"
        """
        self.model_name = model_name
        self.model_type = model_type
        self.metrics = {}
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def evaluate_classification(self, y_true, y_pred, y_proba=None, 
                               class_names=None, average='weighted'):
        """
        Evaluate classification model with comprehensive metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_proba: Predicted probabilities (optional, for AUC)
            class_names: Names of classes
            average: Averaging method for multi-class metrics
            
        Returns:
            Dictionary of evaluation metrics
        """
        print(f"\n{'='*60}")
        print(f"Evaluating {self.model_name} (Classification)")
        print(f"{'='*60}\n")
        
        # Core metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average=average, zero_division=0)
        recall = recall_score(y_true, y_pred, average=average, zero_division=0)
        f1 = f1_score(y_true, y_pred, average=average, zero_division=0)
        
        self.metrics = {
            'model_name': self.model_name,
            'model_type': 'classification',
            'timestamp': self.timestamp,
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1)
        }
        
        # Per-class metrics
        if class_names:
            precision_per_class = precision_score(y_true, y_pred, average=None, zero_division=0)
            recall_per_class = recall_score(y_true, y_pred, average=None, zero_division=0)
            f1_per_class = f1_score(y_true, y_pred, average=None, zero_division=0)
            
            self.metrics['per_class'] = {}
            for i, class_name in enumerate(class_names):
                self.metrics['per_class'][class_name] = {
                    'precision': float(precision_per_class[i]),
                    'recall': float(recall_per_class[i]),
                    'f1_score': float(f1_per_class[i])
                }
        
        # AUC if probabilities provided
        if y_proba is not None:
            try:
                if len(np.unique(y_true)) == 2:
                    # Binary classification
                    auc = roc_auc_score(y_true, y_proba[:, 1])
                    self.metrics['auc_roc'] = float(auc)
                else:
                    # Multi-class (OvR)
                    auc = roc_auc_score(y_true, y_proba, multi_class='ovr', average=average)
                    self.metrics['auc_roc'] = float(auc)
            except Exception as e:
                print(f"⚠️ Could not calculate AUC: {e}")
        
        # Print summary
        self._print_classification_summary(y_true, y_pred, class_names)
        
        return self.metrics
    
    def evaluate_regression(self, y_true, y_pred):
        """
        Evaluate regression model with comprehensive metrics
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of evaluation metrics
        """
        print(f"\n{'='*60}")
        print(f"Evaluating {self.model_name} (Regression)")
        print(f"{'='*60}\n")
        
        # Core regression metrics
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        # Additional metrics
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100 if np.all(y_true != 0) else np.nan
        
        self.metrics = {
            'model_name': self.model_name,
            'model_type': 'regression',
            'timestamp': self.timestamp,
            'mse': float(mse),
            'rmse': float(rmse),
            'mae': float(mae),
            'r2_score': float(r2),
            'mape': float(mape) if not np.isnan(mape) else None
        }
        
        # Print summary
        self._print_regression_summary()
        
        return self.metrics
    
    def _print_classification_summary(self, y_true, y_pred, class_names):
        """Print formatted classification metrics"""
        print("📊 Overall Metrics:")
        print(f"   Accuracy:  {self.metrics['accuracy']:.4f} ({self.metrics['accuracy']*100:.2f}%)")
        print(f"   Precision: {self.metrics['precision']:.4f}")
        print(f"   Recall:    {self.metrics['recall']:.4f}")
        print(f"   F1-Score:  {self.metrics['f1_score']:.4f}")
        
        if 'auc_roc' in self.metrics:
            print(f"   AUC-ROC:   {self.metrics['auc_roc']:.4f}")
        
        if 'per_class' in self.metrics:
            print("\n📋 Per-Class Metrics:")
            for class_name, metrics in self.metrics['per_class'].items():
                print(f"\n   {class_name}:")
                print(f"      Precision: {metrics['precision']:.4f}")
                print(f"      Recall:    {metrics['recall']:.4f}")
                print(f"      F1-Score:  {metrics['f1_score']:.4f}")
        
        print("\n📈 Classification Report:")
        report = classification_report(y_true, y_pred, target_names=class_names, zero_division=0)
        print(report)
    
    def _print_regression_summary(self):
        """Print formatted regression metrics"""
        print("📊 Regression Metrics:")
        print(f"   MSE (Mean Squared Error):      {self.metrics['mse']:.4f}")
        print(f"   RMSE (Root Mean Squared Error): {self.metrics['rmse']:.4f}")
        print(f"   MAE (Mean Absolute Error):     {self.metrics['mae']:.4f}")
        print(f"   R² Score:                      {self.metrics['r2_score']:.4f}")
        
        if self.metrics.get('mape'):
            print(f"   MAPE (Mean Absolute % Error):  {self.metrics['mape']:.2f}%")
    
    def save_confusion_matrix(self, y_true, y_pred, class_names, 
                             output_path="confusion_matrix.png"):
        """
        Generate and save confusion matrix visualization
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            class_names: Names of classes
            output_path: Path to save the plot
        """
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_names,
                   yticklabels=class_names,
                   cbar_kws={'label': 'Count'})
        
        plt.title(f'Confusion Matrix - {self.model_name}', fontsize=14, fontweight='bold')
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        
        # Add accuracy to plot
        accuracy = accuracy_score(y_true, y_pred)
        plt.text(0.5, -0.15, f'Overall Accuracy: {accuracy:.2%}',
                ha='center', va='center', transform=plt.gca().transAxes,
                fontsize=11, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Confusion matrix saved to: {output_path}")
    
    def save_roc_curve(self, y_true, y_proba, class_names=None,
                      output_path="roc_curve.png"):
        """
        Generate and save ROC curve visualization
        
        Args:
            y_true: True labels
            y_proba: Predicted probabilities
            class_names: Names of classes
            output_path: Path to save the plot
        """
        plt.figure(figsize=(10, 8))
        
        n_classes = y_proba.shape[1]
        
        if n_classes == 2:
            # Binary classification
            fpr, tpr, _ = roc_curve(y_true, y_proba[:, 1])
            auc = roc_auc_score(y_true, y_proba[:, 1])
            
            plt.plot(fpr, tpr, linewidth=2, 
                    label=f'ROC Curve (AUC = {auc:.3f})')
        else:
            # Multi-class (One-vs-Rest)
            from sklearn.preprocessing import label_binarize
            
            y_true_bin = label_binarize(y_true, classes=range(n_classes))
            
            for i in range(n_classes):
                fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_proba[:, i])
                auc = roc_auc_score(y_true_bin[:, i], y_proba[:, i])
                
                class_label = class_names[i] if class_names else f'Class {i}'
                plt.plot(fpr, tpr, linewidth=2,
                        label=f'{class_label} (AUC = {auc:.3f})')
        
        # Plot diagonal
        plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random Classifier')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title(f'ROC Curve - {self.model_name}', fontsize=14, fontweight='bold')
        plt.legend(loc='lower right', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ ROC curve saved to: {output_path}")
    
    def save_metrics_report(self, output_path="evaluation_report.txt"):
        """
        Save comprehensive metrics report to text file
        
        Args:
            output_path: Path to save the report
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write(f"Model Evaluation Report: {self.model_name}\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Evaluation Timestamp: {self.timestamp}\n")
            f.write(f"Model Type: {self.model_type}\n\n")
            
            f.write("-"*70 + "\n")
            f.write("PERFORMANCE METRICS\n")
            f.write("-"*70 + "\n\n")
            
            if self.model_type == 'classification':
                f.write(f"Accuracy:  {self.metrics['accuracy']:.4f} ({self.metrics['accuracy']*100:.2f}%)\n")
                f.write(f"Precision: {self.metrics['precision']:.4f}\n")
                f.write(f"Recall:    {self.metrics['recall']:.4f}\n")
                f.write(f"F1-Score:  {self.metrics['f1_score']:.4f}\n")
                
                if 'auc_roc' in self.metrics:
                    f.write(f"AUC-ROC:   {self.metrics['auc_roc']:.4f}\n")
                
                if 'per_class' in self.metrics:
                    f.write("\n" + "-"*70 + "\n")
                    f.write("PER-CLASS METRICS\n")
                    f.write("-"*70 + "\n\n")
                    
                    for class_name, metrics in self.metrics['per_class'].items():
                        f.write(f"{class_name}:\n")
                        f.write(f"  Precision: {metrics['precision']:.4f}\n")
                        f.write(f"  Recall:    {metrics['recall']:.4f}\n")
                        f.write(f"  F1-Score:  {metrics['f1_score']:.4f}\n\n")
            
            elif self.model_type == 'regression':
                f.write(f"MSE (Mean Squared Error):       {self.metrics['mse']:.4f}\n")
                f.write(f"RMSE (Root Mean Squared Error): {self.metrics['rmse']:.4f}\n")
                f.write(f"MAE (Mean Absolute Error):      {self.metrics['mae']:.4f}\n")
                f.write(f"R² Score:                       {self.metrics['r2_score']:.4f}\n")
                
                if self.metrics.get('mape'):
                    f.write(f"MAPE (Mean Absolute % Error):   {self.metrics['mape']:.2f}%\n")
            
            f.write("\n" + "="*70 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*70 + "\n")
        
        print(f"✅ Evaluation report saved to: {output_path}")
    
    def save_metrics_json(self, output_path="evaluation_metrics.json"):
        """
        Save metrics as JSON for programmatic access
        
        Args:
            output_path: Path to save JSON file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Metrics JSON saved to: {output_path}")
    
    def generate_full_report(self, y_true, y_pred, y_proba=None, 
                            class_names=None, output_dir="evaluation_results"):
        """
        Generate complete evaluation report with all visualizations
        
        Args:
            y_true: True labels/values
            y_pred: Predicted labels/values
            y_proba: Predicted probabilities (for classification)
            class_names: Names of classes (for classification)
            output_dir: Directory to save all outputs
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n🎯 Generating comprehensive evaluation report...")
        print(f"   Output directory: {output_dir}/")
        
        # Evaluate model
        if self.model_type == 'classification':
            self.evaluate_classification(y_true, y_pred, y_proba, class_names)
            
            # Generate visualizations
            cm_path = os.path.join(output_dir, f"{self.model_name}_confusion_matrix.png")
            self.save_confusion_matrix(y_true, y_pred, class_names, cm_path)
            
            if y_proba is not None:
                roc_path = os.path.join(output_dir, f"{self.model_name}_roc_curve.png")
                try:
                    self.save_roc_curve(y_true, y_proba, class_names, roc_path)
                except Exception as e:
                    print(f"⚠️ Could not generate ROC curve: {e}")
        
        else:  # regression
            self.evaluate_regression(y_true, y_pred)
        
        # Save reports
        txt_path = os.path.join(output_dir, f"{self.model_name}_evaluation_report.txt")
        json_path = os.path.join(output_dir, f"{self.model_name}_metrics.json")
        
        self.save_metrics_report(txt_path)
        self.save_metrics_json(json_path)
        
        print(f"\n✅ Full evaluation report generated successfully!")
        print(f"   Check the '{output_dir}/' directory for all outputs.\n")
        
        return self.metrics


def compare_models(evaluators, output_path="model_comparison.png"):
    """
    Compare multiple models side by side
    
    Args:
        evaluators: List of ModelEvaluator instances
        output_path: Path to save comparison plot
    """
    model_names = [e.model_name for e in evaluators]
    
    # Check if all models are same type
    model_types = set(e.model_type for e in evaluators)
    if len(model_types) > 1:
        print("⚠️ Cannot compare models of different types")
        return
    
    model_type = list(model_types)[0]
    
    if model_type == 'classification':
        metrics_to_plot = ['accuracy', 'precision', 'recall', 'f1_score']
        metric_data = {metric: [] for metric in metrics_to_plot}
        
        for evaluator in evaluators:
            for metric in metrics_to_plot:
                metric_data[metric].append(evaluator.metrics.get(metric, 0))
        
        # Create bar plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(model_names))
        width = 0.2
        
        for i, metric in enumerate(metrics_to_plot):
            offset = width * (i - 1.5)
            ax.bar(x + offset, metric_data[metric], width, 
                  label=metric.replace('_', ' ').title())
        
        ax.set_xlabel('Models', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Model Performance Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(model_names, rotation=45, ha='right')
        ax.legend()
        ax.set_ylim([0, 1.1])
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Model comparison saved to: {output_path}")
    
    else:  # regression
        metrics_to_plot = ['rmse', 'mae', 'r2_score']
        metric_data = {metric: [] for metric in metrics_to_plot}
        
        for evaluator in evaluators:
            for metric in metrics_to_plot:
                metric_data[metric].append(evaluator.metrics.get(metric, 0))
        
        # Create subplots for different scale metrics
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        for i, metric in enumerate(metrics_to_plot):
            axes[i].bar(model_names, metric_data[metric])
            axes[i].set_title(metric.upper().replace('_', ' '))
            axes[i].set_ylabel('Value')
            axes[i].tick_params(axis='x', rotation=45)
            axes[i].grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('Model Performance Comparison', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Model comparison saved to: {output_path}")


if __name__ == "__main__":
    print("Model Evaluation Metrics Module")
    print("Import this module to evaluate your ML models")
    print("\nExample usage:")
    print("  from model_evaluation import ModelEvaluator")
    print("  evaluator = ModelEvaluator('my_model', 'classification')")
    print("  metrics = evaluator.evaluate_classification(y_true, y_pred)")
