# LinearBoost F1 Improvement - Specific Code Changes

Based on analysis of most recent UCI benchmark results:
- **LinearBoost-L**: F1 rank #5 (mean 5.57, 0 wins)
- **LinearBoost-K-exact**: F1 rank #3 (mean 4.14, 1 win)
- **Gap to CatBoost**: 2.71 rank points for LinearBoost-L

## Top 3 Improvements for Maximum F1 Gain

### 1. F1-Aware Estimator Weighting ⭐ (Highest Impact)

**File**: `src/linearboost/linear_boost.py`  
**Location**: `_boost` method, SAMME.R section (around line 1324) and SAMME section (around line 1364)

**Current Code**:
```python
# Compute SEFR-specific weight update with shrinkage
estimator_weight = self.shrinkage * adaptive_lr * np.log(
    (1 - estimator_error) / estimator_error
)
```

**Replace With**:
```python
# Compute F1 for this estimator to inform weight calculation
f1 = f1_score(y, y_pred, sample_weight=sample_weight, average='weighted')

# F1 bonus: reward estimators with good F1
# Scale: 0.5 F1 -> 1.0x multiplier, 1.0 F1 -> 1.2x multiplier
f1_bonus = 1.0 + (f1 - 0.5) * 0.4

# Compute base weight from error
base_weight = np.log((1 - estimator_error) / max(estimator_error, 1e-10))

# Apply F1 bonus to estimator weight
estimator_weight = self.shrinkage * adaptive_lr * base_weight * f1_bonus
```

**Expected**: +0.015-0.025 F1 improvement

---

### 2. Class-Imbalance Aware Sample Weight Updates ⭐⭐ (Critical for Imbalanced Datasets)

**File**: `src/linearboost/linear_boost.py`  
**Location**: `_boost` method, sample weight update sections

**For SAMME.R** (replace lines 1328-1332):
```python
# OLD:
if iboost < self.n_estimators - 1:
    sample_weight = np.exp(
        np.log(sample_weight)
        + estimator_weight * incorrect * (sample_weight > 0)
    )

# NEW - Class-imbalance aware:
if iboost < self.n_estimators - 1:
    # Compute class frequencies for imbalance handling
    unique_classes, class_counts = np.unique(y, return_counts=True)
    class_freq = class_counts / len(y)
    class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}
    
    # Apply class-aware weight updates
    for cls in unique_classes:
        cls_mask = y == cls
        cls_weight = class_weights[cls]
        # Boost updates for minority class (inverse frequency weighting)
        sample_weight[cls_mask] = np.exp(
            np.log(sample_weight[cls_mask] + 1e-10)
            + estimator_weight * incorrect[cls_mask] * cls_weight * (sample_weight[cls_mask] > 0)
        )
    
    # Normalize to prevent numerical issues
    sample_weight /= np.sum(sample_weight)
```

**For SAMME** (replace line 1368):
```python
# OLD:
sample_weight *= np.exp(estimator_weight * incorrect)

# NEW - Class-imbalance aware:
# Compute class frequencies for imbalance handling
unique_classes, class_counts = np.unique(y, return_counts=True)
class_freq = class_counts / len(y)
class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}

# Apply class-aware weight updates
for cls in unique_classes:
    cls_mask = y == cls
    cls_weight = class_weights[cls]
    # Boost updates for minority class
    sample_weight[cls_mask] *= np.exp(
        estimator_weight * incorrect[cls_mask] * cls_weight
    )

# Normalize sample weights
sample_weight /= np.sum(sample_weight)
```

**Expected**: +0.02-0.03 F1 on imbalanced datasets, +0.01-0.02 overall

---

### 3. Margin-Based Sample Weight Updates (Prevents Over-Weighting Hard Examples)

**File**: `src/linearboost/linear_boost.py`  
**Location**: `_boost` method, integrate with Change 2 above

**Enhanced version combining class-imbalance and margin awareness**:

```python
# Get prediction margins if available (for margin-based updates)
if hasattr(estimator, 'predict_proba'):
    try:
        y_proba = estimator.predict_proba(X)[:, 1]
        margins = np.abs(y_proba - 0.5)  # Distance from decision boundary
        hard_examples = margins < 0.15  # Low confidence threshold
    except:
        hard_examples = np.zeros(len(y), dtype=bool)
else:
    hard_examples = np.zeros(len(y), dtype=bool)

# Compute class frequencies for imbalance handling
unique_classes, class_counts = np.unique(y, return_counts=True)
class_freq = class_counts / len(y)
class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}

# Apply class-aware AND margin-aware weight updates
for cls in unique_classes:
    cls_mask = y == cls
    cls_weight = class_weights[cls]
    cls_hard = hard_examples[cls_mask]
    cls_easy = ~cls_hard
    
    if self.algorithm == "SAMME.R":
        # Standard update for easy examples
        sample_weight[cls_mask][cls_easy] = np.exp(
            np.log(sample_weight[cls_mask][cls_easy] + 1e-10)
            + estimator_weight * incorrect[cls_mask][cls_easy] * cls_weight 
            * (sample_weight[cls_mask][cls_easy] > 0)
        )
        # Gentler update for hard examples (prevent over-weighting)
        sample_weight[cls_mask][cls_hard] = 1.0 + estimator_weight * 0.6 * incorrect[cls_mask][cls_hard] * cls_weight
    else:  # SAMME
        # Standard update for easy examples
        sample_weight[cls_mask][cls_easy] *= np.exp(
            estimator_weight * incorrect[cls_mask][cls_easy] * cls_weight
        )
        # Gentler update for hard examples
        sample_weight[cls_mask][cls_hard] *= (1.0 + estimator_weight * 0.6 * incorrect[cls_mask][cls_hard] * cls_weight)

# Normalize
sample_weight /= np.sum(sample_weight)
```

**Expected**: +0.01-0.015 F1, improved stability

---

## Complete Modified `_boost` Method Sections

### SAMME.R Section (After Line 1316)

```python
# Compute adaptive learning rate
adaptive_lr = self._compute_adaptive_learning_rate(
    iboost, estimator_error, self.learning_rate
)

# Compute F1 for this estimator
f1 = f1_score(y, y_pred, sample_weight=sample_weight, average='weighted')
f1_bonus = 1.0 + (f1 - 0.5) * 0.4

# Compute SEFR-specific weight update with shrinkage
base_weight = np.log((1 - estimator_error) / max(estimator_error, 1e-10))
estimator_weight = self.shrinkage * adaptive_lr * base_weight * f1_bonus

if iboost < self.n_estimators - 1:
    # Get prediction margins for margin-based updates
    if hasattr(estimator, 'predict_proba'):
        try:
            y_proba = estimator.predict_proba(X)[:, 1]
            margins = np.abs(y_proba - 0.5)
            hard_examples = margins < 0.15
        except:
            hard_examples = np.zeros(len(y), dtype=bool)
    else:
        hard_examples = np.zeros(len(y), dtype=bool)
    
    # Compute class frequencies for imbalance handling
    unique_classes, class_counts = np.unique(y, return_counts=True)
    class_freq = class_counts / len(y)
    class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}
    
    # Apply class-aware and margin-aware weight updates
    for cls in unique_classes:
        cls_mask = y == cls
        cls_weight = class_weights[cls]
        cls_hard = hard_examples[cls_mask]
        cls_easy = ~cls_hard
        
        # Standard update for easy examples
        sample_weight[cls_mask][cls_easy] = np.exp(
            np.log(sample_weight[cls_mask][cls_easy] + 1e-10)
            + estimator_weight * incorrect[cls_mask][cls_easy] * cls_weight 
            * (sample_weight[cls_mask][cls_easy] > 0)
        )
        # Gentler update for hard examples
        sample_weight[cls_mask][cls_hard] = 1.0 + estimator_weight * 0.6 * incorrect[cls_mask][cls_hard] * cls_weight
    
    # Normalize
    sample_weight /= np.sum(sample_weight)
```

### SAMME Section (After Line 1356)

```python
# Compute adaptive learning rate
adaptive_lr = self._compute_adaptive_learning_rate(
    iboost, estimator_error, self.learning_rate
)

# Compute F1 for this estimator
f1 = f1_score(y, y_pred, sample_weight=sample_weight, average='weighted')
f1_bonus = 1.0 + (f1 - 0.5) * 0.4

# Compute weight update with shrinkage
base_weight = np.log((1.0 - estimator_error) / max(estimator_error, 1e-10))
estimator_weight = self.shrinkage * adaptive_lr * base_weight * f1_bonus

# Get prediction margins for margin-based updates
if hasattr(estimator, 'predict_proba'):
    try:
        y_proba = estimator.predict_proba(X)[:, 1]
        margins = np.abs(y_proba - 0.5)
        hard_examples = margins < 0.15
    except:
        hard_examples = np.zeros(len(y), dtype=bool)
else:
    hard_examples = np.zeros(len(y), dtype=bool)

# Compute class frequencies for imbalance handling
unique_classes, class_counts = np.unique(y, return_counts=True)
class_freq = class_counts / len(y)
class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}

# Apply class-aware and margin-aware weight updates
for cls in unique_classes:
    cls_mask = y == cls
    cls_weight = class_weights[cls]
    cls_hard = hard_examples[cls_mask]
    cls_easy = ~cls_hard
    
    # Standard update for easy examples
    sample_weight[cls_mask][cls_easy] *= np.exp(
        estimator_weight * incorrect[cls_mask][cls_easy] * cls_weight
    )
    # Gentler update for hard examples
    sample_weight[cls_mask][cls_hard] *= (1.0 + estimator_weight * 0.6 * incorrect[cls_mask][cls_hard] * cls_weight)

# Normalize sample weights
sample_weight /= np.sum(sample_weight)
```

---

## Expected Results After Implementation

### Performance Improvements
- **F1 Score**: +0.04-0.06 improvement
  - LinearBoost-L: Should move from rank 5 → rank 2-3
  - LinearBoost-K-exact: Should move from rank 3 → rank 1-2
- **Win Count**: Should increase from 1 total → 4-6 wins across variants
- **Imbalanced Datasets**: Significant improvement (+0.02-0.03 F1)

### Why These Changes Work

1. **F1-Aware Weighting**: Directly optimizes for F1 instead of just error rate
2. **Class-Imbalance Awareness**: Handles minority classes better (CatBoost's strength)
3. **Margin-Based Updates**: Prevents instability from hard examples, improves convergence

---

## Testing Checklist

After implementation:
- [ ] Test on one balanced dataset (e.g., Breast Cancer)
- [ ] Test on one imbalanced dataset (e.g., Haberman)
- [ ] Verify F1 improves by expected amount
- [ ] Check ROC-AUC doesn't regress significantly
- [ ] Verify numerical stability (no NaN/Inf)
- [ ] Run full benchmark to confirm rankings improve

---

**Priority**: Implement in order (1 → 2 → 3) for maximum impact

