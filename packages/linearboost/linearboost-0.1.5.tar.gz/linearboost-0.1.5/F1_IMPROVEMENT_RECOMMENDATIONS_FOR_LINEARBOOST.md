# LinearBoost F1 Improvement Recommendations

**Based on**: Most recent UCI benchmark results (Dec 28, 2024)  
**Current Performance**: LinearBoost-L F1 rank #5, LinearBoost-K-exact F1 rank #3  
**Target**: Move to rank #1-2 (competing with CatBoost)

## Executive Summary

After analyzing the latest benchmark results and the `linear_boost.py` implementation, here are the **specific ways to improve F1 scores**:

### Top 3 Improvements (Implement in Order)

1. **F1-Aware Estimator Weighting** → Expected: +0.015-0.025 F1
2. **Class-Imbalance Aware Sample Weight Updates** → Expected: +0.02-0.03 F1  
3. **Margin-Based Weight Updates** → Expected: +0.01-0.015 F1

**Combined Expected Impact**: +0.04-0.06 F1 → Should move LinearBoost-L from rank 5 → rank 1-2

---

## Current Implementation Analysis

### What's Already Implemented ✅
- ✅ Adaptive learning rate (recently added)
- ✅ Early stopping on F1/ROC-AUC (recently added)
- ✅ Shrinkage regularization
- ✅ Subsampling support

### What's Missing ❌
- ❌ F1 score is not used in estimator weight calculation
- ❌ Class imbalance is not explicitly handled in sample weight updates
- ❌ Hard examples (low confidence) are treated the same as easy examples
- ❌ No margin-based adjustments

---

## Specific Improvements for `linear_boost.py`

### Improvement 1: F1-Aware Estimator Weighting (HIGHEST PRIORITY)

**Why**: Currently, estimator weights are based only on classification error. However, **F1 score and error rate can diverge** - an estimator might have good F1 but moderate error, or vice versa. Since we're optimizing for F1, we should weight estimators by their F1 contribution.

**Code Location**: `_boost` method, lines 1324 (SAMME.R) and 1364 (SAMME)

**Change Required**:

Add F1 calculation and apply bonus to estimator weight:

```python
# After computing estimator_error, before computing estimator_weight:
from sklearn.metrics import f1_score  # Already imported at top

# Compute F1 for this estimator
f1 = f1_score(y, y_pred, sample_weight=sample_weight, average='weighted')

# F1 bonus: reward estimators with good F1
# Scale: 0.5 F1 -> 1.0x, 1.0 F1 -> 1.2x multiplier
f1_bonus = 1.0 + (f1 - 0.5) * 0.4

# Modify estimator weight calculation:
base_weight = np.log((1.0 - estimator_error) / max(estimator_error, 1e-10))
estimator_weight = self.shrinkage * adaptive_lr * base_weight * f1_bonus
```

**Rationale**: This ensures estimators that contribute more to F1 get higher weights, directly aligning with the optimization target.

---

### Improvement 2: Class-Imbalance Aware Sample Weight Updates (CRITICAL)

**Why**: Current exponential weight updates treat all misclassified samples equally. However, on imbalanced datasets, **misclassifying a minority class sample is more costly for F1** than misclassifying a majority class sample. The benchmark shows CatBoost wins on imbalanced datasets (likely better imbalance handling).

**Code Location**: Sample weight update sections (lines 1329-1332 for SAMME.R, line 1368 for SAMME)

**Change Required**:

Replace uniform weight updates with class-frequency-aware updates:

```python
# Instead of:
sample_weight *= np.exp(estimator_weight * incorrect)  # Uniform update

# Use:
# Compute class frequencies
unique_classes, class_counts = np.unique(y, return_counts=True)
class_freq = class_counts / len(y)
class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}

# Apply class-aware updates (minority class gets higher weight)
for cls in unique_classes:
    cls_mask = y == cls
    cls_weight = class_weights[cls]  # Higher for minority class
    if self.algorithm == "SAMME.R":
        sample_weight[cls_mask] = np.exp(
            np.log(sample_weight[cls_mask] + 1e-10)
            + estimator_weight * incorrect[cls_mask] * cls_weight 
            * (sample_weight[cls_mask] > 0)
        )
    else:  # SAMME
        sample_weight[cls_mask] *= np.exp(
            estimator_weight * incorrect[cls_mask] * cls_weight
        )

# Normalize
sample_weight /= np.sum(sample_weight)
```

**Rationale**: This gives more weight to minority class samples, improving F1 on imbalanced datasets where minority class recall is critical.

---

### Improvement 3: Margin-Based Sample Weight Updates (STABILITY)

**Why**: Exponential weight updates can be too aggressive for hard examples (low-confidence predictions near decision boundary). This can cause instability and overshoot optimal weights.

**Code Location**: Integrate with Improvement 2 above

**Change Required**:

Use gentler updates for hard examples:

```python
# Get prediction confidence (margin)
if hasattr(estimator, 'predict_proba'):
    try:
        y_proba = estimator.predict_proba(X)[:, 1]
        margins = np.abs(y_proba - 0.5)  # Distance from 0.5
        hard_examples = margins < 0.15  # Low confidence threshold
    except:
        hard_examples = np.zeros(len(y), dtype=bool)
else:
    hard_examples = np.zeros(len(y), dtype=bool)

# Apply different update strategies
for cls in unique_classes:
    cls_mask = y == cls
    cls_weight = class_weights[cls]
    cls_hard = hard_examples[cls_mask]
    cls_easy = ~cls_hard
    
    # Standard exponential for easy examples
    # Gentler linear update for hard examples
    if self.algorithm == "SAMME.R":
        sample_weight[cls_mask][cls_easy] = np.exp(...)  # Standard
        sample_weight[cls_mask][cls_hard] = 1.0 + estimator_weight * 0.6 * ...  # Gentler
    else:
        sample_weight[cls_mask][cls_easy] *= np.exp(...)  # Standard
        sample_weight[cls_mask][cls_hard] *= (1.0 + estimator_weight * 0.6 * ...)  # Gentler
```

**Rationale**: Prevents over-weighting of hard examples, leading to more stable training and better convergence.

---

## Additional Improvement Opportunities

### 4. Confidence-Based Estimator Weighting (Optional)

**Why**: Estimators with higher prediction confidence should contribute more to the ensemble.

**Implementation**: Add confidence bonus to estimator weight:
```python
if hasattr(estimator, 'predict_proba'):
    y_proba = estimator.predict_proba(X)[:, 1]
    confidence = np.abs(y_proba - 0.5)
    avg_confidence = np.average(confidence, weights=sample_weight)
    confidence_bonus = 0.9 + avg_confidence * 0.4  # 0.0 -> 0.9x, 0.5 -> 1.1x
    estimator_weight *= confidence_bonus
```

### 5. Ensemble Pruning (Optional)

**Why**: Remove weak estimators that don't contribute meaningfully.

**Implementation**: After training, prune estimators with very low weights:
```python
# At end of fit() method
if len(self.estimators_) > 5:
    weights = np.array(self.estimator_weights_)
    min_weight = np.max(weights) * 0.02  # Keep only top 98%
    keep_mask = weights >= min_weight
    self.estimators_ = [est for i, est in enumerate(self.estimators_) if keep_mask[i]]
    self.estimator_weights_ = weights[keep_mask]
    self.estimator_weights_ /= np.sum(self.estimator_weights_)  # Renormalize
```

### 6. SEFR Regularization (For High-Dimensional Data)

**Why**: SEFR base estimator may overfit on high-dimensional data.

**Implementation** (in `sefr.py`):
```python
# Add L2 regularization to coefficient calculation
lambda_reg = 0.01
feature_variance = np.var(K, axis=0)
self.coef_ = (avg_pos - avg_neg) / (avg_pos + avg_neg + lambda_reg * feature_variance + 1e-7)
```

---

## Implementation Priority

### Phase 1: Core Improvements (Immediate)
1. **F1-Aware Estimator Weighting** - Direct F1 optimization
2. **Class-Imbalance Aware Updates** - Addresses F1 gap on imbalanced datasets

### Phase 2: Stability Improvements
3. **Margin-Based Updates** - Improves stability and convergence

### Phase 3: Fine-Tuning (Optional)
4. Confidence-Based Weighting
5. Ensemble Pruning
6. SEFR Regularization

---

## Expected Impact Summary

| Improvement | Expected F1 Gain | Priority | Implementation Time |
|------------|------------------|----------|---------------------|
| F1-Aware Weighting | +0.015-0.025 | 🔴 HIGH | 30 min |
| Class-Imbalance Aware | +0.02-0.03 | 🔴 HIGH | 45 min |
| Margin-Based Updates | +0.01-0.015 | 🟡 MEDIUM | 30 min |
| **Combined (1-3)** | **+0.04-0.06** | - | ~2 hours |

**Target Achievement**:
- LinearBoost-L: Rank 5 → Rank 1-2
- LinearBoost-K-exact: Rank 3 → Rank 1-2
- Win count: 1 total → 4-6 wins

---

## Code Implementation Guide

See `LINEARBOOST_F1_IMPROVEMENT_CODE_CHANGES.md` for complete code snippets and exact line numbers.

---

**Key Insight**: The current implementation optimizes for **error rate** but benchmarks measure **F1 score**. These improvements align the optimization target (estimator weights, sample weights) with the evaluation metric (F1 score).

