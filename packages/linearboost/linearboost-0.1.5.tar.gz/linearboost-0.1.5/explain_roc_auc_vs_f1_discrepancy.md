# Why ROC-AUC = 1.0 but F1 = 0.80?

## The Issue

During hyperparameter optimization, you see:
```
Best value: 1  (ROC-AUC = 1.0)
```

But in final test results:
```
F1 Score: 0.80
```

## Root Cause

### What's Being Optimized
- **During optimization** (line 462): `scoring='roc_auc'`
- **Progress bar shows**: ROC-AUC score (can be 1.0 = perfect)

### What's Being Reported
- **During evaluation** (line 1005): F1 score at **default threshold 0.5**
- **F1 uses**: `make_scorer(f1_score, average="weighted")` which calls `predict()` with threshold 0.5

## Why They Differ

**ROC-AUC** (Area Under ROC Curve):
- Measures **separability** - can the model distinguish between classes?
- **Threshold-independent** - looks at all possible thresholds
- ROC-AUC = 1.0 means: "The model can perfectly separate the classes"
- **Does NOT guarantee** perfect predictions at threshold 0.5

**F1 Score**:
- Measures **precision and recall at a specific threshold** (0.5 by default)
- **Threshold-dependent** - depends on where you cut predictions
- F1 = 0.80 means: "At threshold 0.5, predictions are 80% accurate"

## Example Scenario

On a small HD dataset with 72-85 samples:
- Model learns to separate classes well → **ROC-AUC = 1.0**
- But the optimal threshold for F1 might be 0.3 or 0.7, not 0.5
- At threshold 0.5 → **F1 = 0.80** (suboptimal)

## Visual Example

```
Probability distribution:
Class 0: [0.1, 0.2, 0.3, 0.4]  ← low probabilities
Class 1: [0.6, 0.7, 0.8, 0.9]  ← high probabilities

ROC-AUC = 1.0 (perfect separation)

But at threshold 0.5:
- Some Class 0 samples have prob > 0.5 → misclassified
- F1 < 1.0

Optimal threshold might be 0.45 → better F1
```

## Solutions

### Option 1: Optimize for F1 Directly (Recommended)

Change optimization to use F1:

```python
# In _optimize_linearboost_linear (line 460-466)
scores = cross_validate(
    pipe, self.X_hp, self.y_hp,
    scoring='f1',  # Change from 'roc_auc' to 'f1'
    cv=cv, n_jobs=self.n_jobs,
    return_train_score=False
)
```

**Pros:**
- Optimizes for the metric you actually care about
- Progress bar will show F1 scores
- Parameters tuned for F1 performance

**Cons:**
- F1 optimization can be less stable than ROC-AUC
- Might need to specify `average` parameter

### Option 2: Optimize Threshold for F1

Add threshold optimization:

```python
from sklearn.metrics import f1_score

def objective_with_threshold(trial):
    # ... existing parameter optimization ...
    
    # Add threshold optimization
    threshold = trial.suggest_float("threshold", 0.1, 0.9)
    
    # After cross_validate, optimize threshold
    y_pred_proba = model.predict_proba(X_val)[:, 1]
    y_pred = (y_pred_proba >= threshold).astype(int)
    return f1_score(y_val, y_pred, average='weighted')
```

### Option 3: Use ROC-AUC but Report F1 with Optimal Threshold

Keep ROC-AUC optimization, but find optimal threshold for F1:

```python
# After optimization, find best threshold for F1
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_predict

y_proba = cross_val_predict(model, X, y, cv=cv, method='predict_proba')[:, 1]

# Find optimal threshold for F1
thresholds = np.linspace(0.1, 0.9, 100)
f1_scores = [f1_score(y, (y_proba >= t).astype(int), average='weighted') 
             for t in thresholds]
optimal_threshold = thresholds[np.argmax(f1_scores)]
optimal_f1 = max(f1_scores)
```

### Option 4: Use Balanced Metric

For imbalanced datasets, optimize for balanced metric:

```python
# Optimize for balanced accuracy or F1-macro
scoring = 'balanced_accuracy'  # or 'f1_macro'
```

## Recommendation

**For HD datasets with small sample sizes:**
1. **Keep ROC-AUC optimization** (more stable)
2. **Add threshold optimization for F1** after model selection
3. **Report both metrics** with their optimal thresholds

**For balanced datasets:**
1. **Optimize directly for F1** if F1 is your primary metric
2. This aligns optimization and evaluation

## Current Behavior (Expected)

The current setup is **working as designed**:
- ROC-AUC = 1.0 means model has perfect separability
- F1 = 0.80 means at threshold 0.5, performance is good but not perfect
- This is **normal** for small HD datasets where optimal threshold ≠ 0.5

## Code Location

- **Optimization metric**: `benchmark_2_hd.py` line 462
- **Evaluation F1**: `benchmark_2_hd.py` line 1005
- **Progress bar**: Shows `study.best_value` which is ROC-AUC (line 471)

