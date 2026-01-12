# Issue #178: Train ML Model on Real User Data

## Summary

Currently the ML model is trained on synthetic (fake) data. Implement a pipeline to train the model on real exam data collected from actual users for more accurate predictions.

## Current Behavior

- Model trained on synthetic data generated in `train_sample_model()`
- Random scores, ages, and labels
- May not reflect real EQ patterns

```python
# Current: Synthetic data generation
X_synthetic = np.random.rand(1000, 8)  # Random features
y_synthetic = np.random.randint(0, 3, 1000)  # Random labels
```

## Proposed Behavior

- Train on actual data from `scores` table
- Use historical exam results with labeled outcomes
- Periodic retraining as more data accumulates

```python
# Proposed: Real data from database
scores_df = pd.read_sql("SELECT * FROM scores", connection)
X_real = prepare_features_from_scores(scores_df)
y_real = compute_risk_labels(scores_df)  # Based on score thresholds
```

## Risk Labeling Strategy

Based on EQ research, assign risk labels:

| Score Range | Percentage | Risk Label |
| ----------- | ---------- | ---------- |
| 32-40       | 80-100%    | 0 (Low)    |
| 20-31       | 50-79%     | 1 (Medium) |
| 0-19        | 0-49%      | 2 (High)   |

Sentiment score adjustments:

- Positive sentiment (>30) → Lower risk by 1 level
- Negative sentiment (<-30) → Raise risk by 1 level

## Implementation Steps

- [ ] Create `prepare_training_data()` function in predictor.py
- [ ] Implement risk labeling logic based on scores + sentiment
- [ ] Add data validation (minimum samples, class balance)
- [ ] Create training CLI script (`scripts/train_model.py`)
- [ ] Add model evaluation metrics logging
- [ ] Schedule periodic retraining (optional)
- [ ] Keep versioning for model rollback

## Data Requirements

- Minimum 100 exam records for initial training
- Balanced classes (may need oversampling for rare risk levels)
- Feature engineering from existing columns

## Files to Modify

- `app/ml/predictor.py` - Add real data training methods
- `scripts/train_model.py` - New CLI training script
- `app/db.py` - Add training data query helpers

## Model Versioning

Each training run should:

1. Save new model version (e.g., v1.1.0)
2. Log training metrics (accuracy, F1, confusion matrix)
3. Compare with previous version
4. Allow rollback if new model performs worse

## Labels

`enhancement`, `machine-learning`, `data-science`
