# ML Data Split Strategy

## Overview

This document outlines the robust data splitting strategy implemented in the SoulSense ML pipeline (`scripts/ml_training_pipeline.py`).

## Core Strategy: Stratified 70/10/20 Split

We use a **Stratified Random Split** to ensure that the distribution of risk classes (Low, Moderate, High) is preserved across all subsets. This is crucial for medical/psychometric data where "High Risk" cases may be rare.

### 1. Test Set (20%)

- **Purpose:** Final model evaluation only.
- **Isolation:** This data is NEVER seen during training or hyperparameter tuning.
- **Method:** `train_test_split(..., test_size=0.2, stratify=y)`

### 2. Validation Set (10%)

- **Purpose:** Intermediate evaluation during development and model selection.
- **Method:** `train_test_split(..., test_size=0.125, stratify=y_train)` (0.125 of remaining 80% = 10% of total)

### 3. Training Set (70%)

- **Purpose:** Model parameter learning.
- **Method:** Remaining data after Test and Validation splits.

## Cross-Validation (Robustness)

Within the Training Set (70%), we employ **5-Fold Stratified Cross-Validation** during grid search (`GridSearchCV`).

- The training data is split into 5 folds.
- The model is trained on 4 folds and validated on the 5th, rotating 5 times.
- This ensures the selected hyperparameters are robust and not overfit to a specific subset of the training data.

## Future Considerations: Time-Series Split

If the application is deployed and we collect user history over months, we may switch to a **Time-Series Split** to simulate predicting future risk based on past history. Currently, assuming independent sessions, Random Stratified Split is optimal.
