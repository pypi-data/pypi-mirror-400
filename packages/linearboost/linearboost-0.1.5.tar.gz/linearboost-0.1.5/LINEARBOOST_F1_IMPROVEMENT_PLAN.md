# LinearBoost F1 Improvement Plan - Based on Recent Benchmark Analysis

**Analysis Date**: 2024-12-28  
**Current Status**: LinearBoost-L F1 rank #5 (mean rank 5.57), LinearBoost-K-exact rank #3 (mean rank 4.14)  
**Target**: Improve to rank #1-2 (competing with CatBoost at rank #1)

## Current Performance Gaps

### F1 Score Analysis
- **LinearBoost-L**: Mean rank 5.57 (0 wins, 3 top-3 finishes)
- **LinearBoost-K-exact**: Mean rank 4.14 (1 win, 4 top-3 finishes)
- **LinearBoost-K**: Mean rank 6.00 (1 win, 1 top-3 finish)

### Key Observations
1. **LinearBoost-K-exact** performs best but still 1.28 rank points behind CatBoost
2. **LinearBoost-L** has no wins despite ranking #3 overall (due to speed advantage)
3. **Error-based weighting** doesn't directly optimize F1 (it optimizes accuracy/error rate)
4. **Sample weight updates** are exponential and may overshoot for hard examples
5. **Class imbalance** handling is basic (only through class_weight parameter)

---

## Improvement Strategy for `linear_boost.py`

### 🔴 **Priority 1: F1-Aware Estimator Weighting** (Expected: +0.015-0.025 F1)

**Problem**: Currently, estimator weights are based on classification error, not F1 score. This means estimators that improve F1 but don't minimize error get lower weights.

**Current Code** (lines 1324, 1364):
```python
estimator_weight = self.shrinkage * adaptive_lr * np.log(
    (1.0 - estimator_error) / max(estimator_error, 1e-10)
)
```

**Solution**: Add F1 score bonus to estimator weight calculation.

**Implementation** (modify `_boost` method):

```python
# After computing estimator_error, add F1 calculation
from sklearn.metrics import f1_score

# Compute F1 for this estimator
f1 = f1_score(y, y_pred, sample_weight=sample_weight, average='weighted')

# F1 bonus: reward estimators with good F1
# Scale: 0.5 F1 -> 1.0x, 1.0 F1 -> 1.2x
f1_bonus = 1.0 + (f1 - 0.5) * 0.4

# Modify estimator weight calculation
base_weight = np.log((1.0 - estimator_error) / max(estimator_error, 1e-10))
estimator_weight = self.shrinkage * adaptive_lr * base_weight * f1_bonus
```

**Location**: 
- Line 1324 (SAMME.R section)
- Line 1364 (SAMME section)

**Expected Impact**: +0.015-0.025 F1 improvement

---

### 🔴 **Priority 2: Class-Imbalance Aware Sample Weight Updates** (Expected: +0.02-0.03 F1)

**Problem**: Current exponential weight updates treat all misclassified samples equally, regardless of class. This hurts performance on imbalanced datasets.

**Current Code** (lines 1329-1332, 1368):
```python
# SAMME.R:
sample_weight = np.exp(
    np.log(sample_weight)
    + estimator_weight * incorrect * (sample_weight > 0)
)

# SAMME:
sample_weight *= np.exp(estimator_weight * incorrect)
```

**Solution**: Apply class-specific weighting based on class frequency.

**Implementation**:

```python
# Compute class frequencies for imbalance handling
unique_classes, class_counts = np.unique(y, return_counts=True)
class_freq = class_counts / len(y)
class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}

# Apply class-aware weight updates
for cls in unique_classes:
    cls_mask = y == cls
    cls_weight = class_weights[cls]
    # Boost updates for minority class (higher weight)
    if self.algorithm == "SAMME.R":
        sample_weight[cls_mask] = np.exp(
            np.log(sample_weight[cls_mask] + 1e-10)
            + estimator_weight * incorrect[cls_mask] * cls_weight * (sample_weight[cls_mask] > 0)
        )
    else:  # SAMME
        sample_weight[cls_mask] *= np.exp(
            estimator_weight * incorrect[cls_mask] * cls_weight
        )

# Normalize
sample_weight /= np.sum(sample_weight)
```

**Location**:
- After line 1332 (SAMME.R section, replace existing update)
- After line 1368 (SAMME section, replace existing update)

**Expected Impact**: +0.02-0.03 F1 on imbalanced datasets

---

### 🟡 **Priority 3: Margin-Based Sample Weight Updates** (Expected: +0.01-0.015 F1)

**Problem**: Exponential weight updates can be too aggressive for hard examples (low confidence predictions), causing instability.

**Solution**: Use gentler updates for hard examples based on prediction confidence.

**Implementation**:

```python
# Get prediction margins if available
if hasattr(estimator, 'predict_proba'):
    try:
        y_proba = estimator.predict_proba(X)[:, 1]
        margins = np.abs(y_proba - 0.5)  # Distance from decision boundary
        hard_examples = margins < 0.15  # Low confidence threshold
        
        # Gentler update for hard examples
        if self.algorithm == "SAMME.R":
            weight_update = np.ones_like(sample_weight)
            weight_update[~hard_examples] = np.exp(
                np.log(sample_weight[~hard_examples] + 1e-10)
                + estimator_weight * incorrect[~hard_examples] * (sample_weight[~hard_examples] > 0)
            )
            weight_update[hard_examples] = 1.0 + estimator_weight * 0.6 * incorrect[hard_examples]
            sample_weight = weight_update
        else:  # SAMME
            weight_update = np.ones_like(sample_weight)
            weight_update[~hard_examples] = np.exp(estimator_weight * incorrect[~hard_examples])
            weight_update[hard_examples] = 1.0 + estimator_weight * 0.6 * incorrect[hard_examples]
            sample_weight *= weight_update
    except:
        # Fallback to standard update
        sample_weight *= np.exp(estimator_weight * incorrect)
else:
    # No probabilities available, use standard update
    sample_weight *= np.exp(estimator_weight * incorrect)
```

**Location**: Replace sample weight update sections (lines 1329-1332, 1368)

**Expected Impact**: +0.01-0.015 F1, improved stability

---

### 🟡 **Priority 4: Confidence-Based Estimator Weighting** (Expected: +0.01-0.015 F1)

**Problem**: Estimator weights are based only on error rate, not prediction confidence. High-confidence correct predictions should be weighted more.

**Solution**: Incorporate prediction confidence into weight calculation.

**Implementation**:

```python
# Compute confidence-based weight adjustment
if hasattr(estimator, 'predict_proba'):
    try:
        y_proba = estimator.predict_proba(X)[:, 1]
        # Confidence = distance from decision boundary
        confidence = np.abs(y_proba - 0.5)
        avg_confidence = np.average(confidence, weights=sample_weight)
        
        # Confidence bonus: higher confidence -> higher weight
        # Scale: 0.0 confidence -> 0.9x, 0.5 confidence -> 1.1x
        confidence_bonus = 0.9 + avg_confidence * 0.4
    except:
        confidence_bonus = 1.0
else:
    confidence_bonus = 1.0

# Apply to estimator weight
base_weight = np.log((1.0 - estimator_error) / max(estimator_error, 1e-10))
estimator_weight = self.shrinkage * adaptive_lr * base_weight * f1_bonus * confidence_bonus
```

**Location**: After F1 bonus calculation in estimator weight computation

**Expected Impact**: +0.01-0.015 F1

---

### 🟢 **Priority 5: SEFR Regularization** (Expected: +0.01-0.02 F1 on high-dim data)

**Problem**: SEFR base estimator may overfit, especially on high-dimensional data. No regularization in coefficient calculation.

**Current Code** (sefr.py, line 304):
```python
self.coef_ = (avg_pos - avg_neg) / (avg_pos + avg_neg + 1e-7)
```

**Solution**: Add L2 regularization term.

**Implementation** (modify `sefr.py`):

```python
# Add small regularization term
lambda_reg = 0.01  # Could be a parameter, but keep simple for now
# Use variance as regularization factor
feature_variance = np.var(K, axis=0)
regularization = lambda_reg * feature_variance + 1e-7

self.coef_ = (avg_pos - avg_neg) / (avg_pos + avg_neg + regularization)
```

**Location**: `src/linearboost/sefr.py`, line 304

**Expected Impact**: +0.01-0.02 F1 on high-dimensional datasets

---

## Complete Implementation Order

### Phase 1: Quick Wins (1-2 hours)
1. ✅ **Adaptive Learning Rate** - Already implemented
2. **F1-Aware Estimator Weighting** - Priority 1
3. **Class-Imbalance Aware Updates** - Priority 2

### Phase 2: Refinements (2-3 hours)
4. **Margin-Based Updates** - Priority 3
5. **Confidence-Based Weighting** - Priority 4

### Phase 3: Advanced (Optional)
6. **SEFR Regularization** - Priority 5

---

## Expected Combined Impact

Implementing **Priorities 1-3** should yield:
- **F1 improvement**: +0.04-0.06 (should move LinearBoost-L from rank 5 → rank 1-2)
- **Stability improvement**: More consistent performance
- **Imbalanced dataset improvement**: +0.02-0.03 F1 on imbalanced datasets

This would make LinearBoost **competitive with or superior to CatBoost** on F1 score.

---

## Specific Code Changes Needed

### Change 1: Add F1 Calculation and Bonus (Lines 1324 & 1364)

**In SAMME.R section** (after line 1305, before line 1324):
```python
# Compute F1 for this estimator
from sklearn.metrics import f1_score
f1 = f1_score(y, y_pred, sample_weight=sample_weight, average='weighted')
f1_bonus = 1.0 + (f1 - 0.5) * 0.4
```

**In SAMME section** (after line 1342, before line 1364):
```python
# Compute F1 for this estimator
from sklearn.metrics import f1_score
f1 = f1_score(y, y_pred, sample_weight=sample_weight, average='weighted')
f1_bonus = 1.0 + (f1 - 0.5) * 0.4
```

Then modify weight calculation:
```python
base_weight = np.log((1.0 - estimator_error) / max(estimator_error, 1e-10))
estimator_weight = self.shrinkage * adaptive_lr * base_weight * f1_bonus
```

### Change 2: Class-Imbalance Aware Updates (Replace lines 1329-1332 & 1368)

Replace sample weight update with class-aware version (see Priority 2 above).

### Change 3: Margin-Based Updates (Integrate with Change 2)

Add margin calculation and conditional updates (see Priority 3 above).

---

## Testing Strategy

After each change:
1. Run on one benchmark dataset
2. Compare F1 before/after
3. Verify no regression in ROC-AUC
4. Check for numerical stability

**Target Metrics**:
- LinearBoost-L: F1 rank improve from 5.57 → <3.0
- LinearBoost-K-exact: F1 rank improve from 4.14 → <2.5
- Win count: Increase from 1 total → 3+ wins per variant

---

**Note**: These improvements build on the adaptive learning rate already implemented and the early stopping on F1/ROC-AUC. Together, they should significantly improve F1 performance.

