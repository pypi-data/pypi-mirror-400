# Next Steps for F1 Score Optimization

**Current Status**: 
- ✅ Adaptive learning rate - **Implemented**
- ✅ Early stopping on F1/ROC-AUC - **Implemented** (+0.0248 F1 improvement)
- ✅ F1-aware estimator weighting - **Implemented** (minimal impact, may need strengthening)
- **Current F1 Rank**: LinearBoost-L #5, LinearBoost-K-exact #3

**Target**: Move LinearBoost-L from rank #5 → rank #1-2 (competing with CatBoost)

---

## 🎯 **Priority 1: Class-Imbalance Aware Sample Weight Updates** (HIGHEST IMPACT)

**Expected Impact**: +0.02-0.03 F1 on imbalanced datasets, +0.01-0.02 overall

**Why This Is Critical:**
- Current sample weight updates treat all misclassified samples equally
- On imbalanced datasets, misclassifying minority class is more costly for F1
- CatBoost wins on imbalanced datasets (likely better imbalance handling)
- Benchmark analysis shows LinearBoost struggles on imbalanced datasets

**Implementation Location**: `src/linearboost/linear_boost.py`, `_boost` method
- SAMME.R section: lines 1328-1337 (sample weight update)
- SAMME section: line 1368 (sample weight update)

**What To Do:**
1. Replace uniform weight updates with class-frequency-aware updates
2. Give higher weight boosts to minority class samples when misclassified
3. Implement in both SAMME.R and SAMME algorithms

**Code Changes Needed** (see `LINEARBOOST_F1_IMPROVEMENT_CODE_CHANGES.md` for full code):

```python
# Replace:
sample_weight *= np.exp(estimator_weight * incorrect)

# With:
unique_classes, class_counts = np.unique(y, return_counts=True)
class_freq = class_counts / len(y)
class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}

for cls in unique_classes:
    cls_mask = y == cls
    cls_weight = class_weights[cls]  # Higher for minority class
    sample_weight[cls_mask] *= np.exp(estimator_weight * incorrect[cls_mask] * cls_weight)
```

**Estimated Time**: 30-45 minutes

---

## 🎯 **Priority 2: Strengthen F1-Aware Estimator Weighting** (QUICK WIN)

**Expected Impact**: +0.01-0.015 F1

**Why This Is Important:**
- Current F1 bonus is too subtle (only 20% max multiplier)
- Analysis showed minimal impact (essentially no change)
- Increasing the multiplier should make the effect more noticeable

**Implementation Location**: `src/linearboost/linear_boost.py`, lines 1330 and 1380

**What To Do:**
1. Increase F1 bonus multiplier from 0.4 to 0.6 or 0.8
2. This increases max bonus from 1.2x to 1.3x or 1.4x

**Code Changes Needed**:

```python
# Current:
f1_bonus = 1.0 + (f1 - 0.5) * 0.4  # Max 1.2x

# Change to:
f1_bonus = 1.0 + (f1 - 0.5) * 0.6  # Max 1.3x (moderate)
# OR
f1_bonus = 1.0 + (f1 - 0.5) * 0.8  # Max 1.4x (strong)
```

**Estimated Time**: 2 minutes

---

## 🎯 **Priority 3: Margin-Based Sample Weight Updates** (STABILITY)

**Expected Impact**: +0.01-0.015 F1, improved stability

**Why This Helps:**
- Current exponential updates can be too aggressive for hard examples
- Low-confidence predictions near decision boundary cause instability
- Gentler updates for hard examples prevent overshooting optimal weights

**Implementation Location**: Integrate with Priority 1 above

**What To Do:**
1. Compute prediction confidence (margin from decision boundary)
2. Use standard exponential update for easy examples
3. Use gentler linear update for hard examples (confidence < threshold)

**Code Integration** (combine with Priority 1):

```python
# Get prediction margins
if hasattr(estimator, 'predict_proba'):
    y_proba = estimator.predict_proba(X)[:, 1]
    margins = np.abs(y_proba - 0.5)
    hard_examples = margins < 0.15  # Low confidence threshold
else:
    hard_examples = np.zeros(len(y), dtype=bool)

# Apply class-aware AND margin-aware updates
for cls in unique_classes:
    cls_mask = y == cls
    cls_weight = class_weights[cls]
    cls_hard = hard_examples[cls_mask]
    cls_easy = ~cls_hard
    
    # Standard exponential for easy examples
    sample_weight[cls_mask][cls_easy] *= np.exp(
        estimator_weight * incorrect[cls_mask][cls_easy] * cls_weight
    )
    # Gentler linear update for hard examples
    sample_weight[cls_mask][cls_hard] *= (
        1.0 + estimator_weight * 0.6 * incorrect[cls_mask][cls_hard] * cls_weight
    )
```

**Estimated Time**: 30 minutes (when combined with Priority 1)

---

## 📋 **Implementation Plan**

### Phase 1: Quick Wins (Today - 1 hour)
1. ✅ **Strengthen F1 bonus** (Priority 2) - 2 minutes
   - Simple multiplier change
   - Immediate impact testable

2. **Class-imbalance aware updates** (Priority 1) - 45 minutes
   - Highest expected impact
   - Critical for imbalanced datasets

### Phase 2: Refinements (Tomorrow - 30 minutes)
3. **Margin-based updates** (Priority 3) - 30 minutes
   - Integrate with Priority 1
   - Improves stability

### Phase 3: Testing & Validation (After implementation)
4. Run benchmarks on UCI datasets
5. Compare before/after results
6. Verify F1 improvements
7. Check for ROC-AUC trade-offs

---

## 🎯 **Expected Combined Impact**

Implementing **Priorities 1-3** should yield:
- **F1 improvement**: +0.04-0.06 overall
- **Imbalanced datasets**: +0.02-0.03 F1 specifically
- **Stability**: Improved convergence and consistency

**Target Achievement**:
- LinearBoost-L: F1 rank #5 → #1-2
- LinearBoost-K-exact: F1 rank #3 → #1-2
- Win count: 1 total → 4-6 wins per variant

---

## 🔧 **Implementation Details**

### Step 1: Strengthen F1 Bonus (2 minutes)

**File**: `src/linearboost/linear_boost.py`

**Change line 1330** (SAMME.R):
```python
# FROM:
f1_bonus = 1.0 + (f1 - 0.5) * 0.4

# TO:
f1_bonus = 1.0 + (f1 - 0.5) * 0.6  # Stronger bonus
```

**Change line 1380** (SAMME):
```python
# Same change
f1_bonus = 1.0 + (f1 - 0.5) * 0.6
```

### Step 2: Class-Imbalance Aware Updates (45 minutes)

**File**: `src/linearboost/linear_boost.py`

**For SAMME.R** (replace lines 1328-1337):
```python
if iboost < self.n_estimators - 1:
    # Compute class frequencies for imbalance handling
    unique_classes, class_counts = np.unique(y, return_counts=True)
    class_freq = class_counts / len(y)
    class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}
    
    # Apply class-aware weight updates
    for cls in unique_classes:
        cls_mask = y == cls
        cls_weight = class_weights[cls]
        sample_weight[cls_mask] = np.exp(
            np.log(sample_weight[cls_mask] + 1e-10)
            + estimator_weight * incorrect[cls_mask] * cls_weight 
            * (sample_weight[cls_mask] > 0)
        )
    
    # Normalize
    sample_weight /= np.sum(sample_weight)
```

**For SAMME** (replace line 1368):
```python
# Compute class frequencies for imbalance handling
unique_classes, class_counts = np.unique(y, return_counts=True)
class_freq = class_counts / len(y)
class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}

# Apply class-aware weight updates
for cls in unique_classes:
    cls_mask = y == cls
    cls_weight = class_weights[cls]
    sample_weight[cls_mask] *= np.exp(
        estimator_weight * incorrect[cls_mask] * cls_weight
    )

# Normalize
sample_weight /= np.sum(sample_weight)
```

### Step 3: Add Margin-Based Updates (integrate with Step 2)

Add margin calculation before the class-aware loop:
```python
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
```

Then modify the class loop to handle easy/hard examples differently (see Priority 3 code above).

---

## 📊 **Success Metrics**

After implementation, measure:
1. **F1 Score Rankings**: Should improve from #5 → #1-2
2. **Win Count**: Should increase from 1 → 4-6 wins
3. **Imbalanced Datasets**: Should see +0.02-0.03 F1 improvement
4. **ROC-AUC**: Should maintain or improve (not regress significantly)

---

## 🔍 **Alternative Approaches (If Needed)**

If the above don't provide enough improvement:

### Option A: Adaptive F1 Bonus
Make F1 bonus adaptive based on dataset characteristics:
```python
# Stronger bonus on imbalanced datasets
imbalance_ratio = min(class_counts) / max(class_counts)
f1_bonus_strength = 0.4 + (1 - imbalance_ratio) * 0.4  # 0.4 to 0.8
f1_bonus = 1.0 + (f1 - 0.5) * f1_bonus_strength
```

### Option B: Confidence-Based Estimator Weighting
Add confidence bonus in addition to F1 bonus:
```python
if hasattr(estimator, 'predict_proba'):
    y_proba = estimator.predict_proba(X)[:, 1]
    confidence = np.abs(y_proba - 0.5)
    avg_confidence = np.average(confidence, weights=sample_weight)
    confidence_bonus = 0.9 + avg_confidence * 0.4
    estimator_weight *= confidence_bonus
```

### Option C: Ensemble Pruning
Remove weak estimators:
```python
# At end of fit(), prune weak estimators
if len(self.estimators_) > 5:
    weights = np.array(self.estimator_weights_)
    min_weight = np.max(weights) * 0.02
    keep_mask = weights >= min_weight
    self.estimators_ = [est for i, est in enumerate(self.estimators_) if keep_mask[i]]
```

---

## ✅ **Implementation Checklist**

- [ ] Step 1: Strengthen F1 bonus multiplier (2 min)
- [ ] Step 2: Implement class-imbalance aware updates for SAMME.R (20 min)
- [ ] Step 3: Implement class-imbalance aware updates for SAMME (15 min)
- [ ] Step 4: Add margin-based logic (15 min)
- [ ] Step 5: Test on single dataset (10 min)
- [ ] Step 6: Run full benchmark suite
- [ ] Step 7: Compare results to baseline
- [ ] Step 8: Adjust parameters if needed

---

**Total Estimated Time**: 1-2 hours for implementation + testing

**Expected Result**: LinearBoost should move to rank #1-2 for F1 score, making it competitive with or superior to CatBoost.

