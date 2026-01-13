# F1 Score Optimization - Next Steps

**Current Status**:
- ✅ Adaptive learning rate - **Implemented**
- ✅ Early stopping on F1/ROC-AUC - **Implemented** (+0.0248 F1 improvement)
- ✅ F1-aware estimator weighting - **Implemented** (needs strengthening)
- **Current F1 Performance**: LinearBoost-L rank #5, LinearBoost-K-exact rank #3
- **Target**: Move to rank #1-2

---

## 🎯 **IMMEDIATE NEXT STEPS (Priority Order)**

### **Step 1: Strengthen F1 Bonus Multiplier** (2 minutes) ⚡ QUICK WIN

**Status**: Currently implemented with 0.4 multiplier (too weak)
**Action**: Increase to 0.6 or 0.8

**Why**: Analysis showed minimal impact. Current bonus is only 20% max (0.5 F1 → 1.0x, 1.0 F1 → 1.2x). Stronger bonus should have more effect.

**Implementation**:
- **File**: `src/linearboost/linear_boost.py`
- **Line 1380** (SAMME): Change `0.4` → `0.6`
- **Line 1330** (SAMME.R): Already has `0.6` ✓ (keep or increase to `0.8` for consistency)

**Change**:
```python
# SAMME section (line 1380):
f1_bonus = 1.0 + (f1 - 0.5) * 0.6  # Increase from 0.4 to 0.6

# SAMME.R section (line 1330):
f1_bonus = 1.0 + (f1 - 0.5) * 0.6  # Already at 0.6, or increase to 0.8
```

**Expected Impact**: +0.01-0.015 F1

---

### **Step 2: Implement Class-Imbalance Aware Sample Weight Updates** (45 minutes) ⭐ HIGHEST IMPACT

**Status**: NOT implemented
**Action**: Replace uniform weight updates with class-frequency-aware updates

**Why**: 
- Critical for imbalanced datasets (most benchmarks are imbalanced)
- CatBoost excels here (likely why it wins)
- Current implementation treats all misclassifications equally
- Minority class samples need higher weight boosts

**Expected Impact**: +0.02-0.03 F1 on imbalanced datasets, +0.01-0.02 overall

**Implementation**:
- **File**: `src/linearboost/linear_boost.py`
- **SAMME.R section**: Replace lines 1338-1347
- **SAMME section**: Replace line 1388

**Code for SAMME.R** (replace lines 1338-1347):
```python
if iboost < self.n_estimators - 1:
    # Compute class frequencies for imbalance handling
    unique_classes, class_counts = np.unique(y, return_counts=True)
    class_freq = class_counts / len(y)
    class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}
    
    # Apply class-aware weight updates (minority class gets higher boost)
    for cls in unique_classes:
        cls_mask = y == cls
        cls_weight = class_weights[cls]  # Inverse frequency weighting
        sample_weight[cls_mask] = np.exp(
            np.log(sample_weight[cls_mask] + 1e-10)
            + estimator_weight * incorrect[cls_mask] * cls_weight 
            * (sample_weight[cls_mask] > 0)
        )
    
    # Normalize to prevent numerical issues
    sample_weight /= np.sum(sample_weight)
```

**Code for SAMME** (replace line 1388):
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

---

### **Step 3: Add Margin-Based Updates** (30 minutes) 🛡️ STABILITY

**Status**: NOT implemented
**Action**: Integrate with Step 2 - use gentler updates for hard examples

**Why**:
- Prevents over-weighting of low-confidence predictions
- Improves training stability
- Better convergence

**Expected Impact**: +0.01-0.015 F1, improved stability

**Implementation**: Add margin calculation and conditional updates (combine with Step 2):

**Enhanced version** (for both SAMME.R and SAMME):
```python
# Get prediction margins for margin-based updates
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
        # Standard exponential for easy examples
        sample_weight[cls_mask][cls_easy] = np.exp(
            np.log(sample_weight[cls_mask][cls_easy] + 1e-10)
            + estimator_weight * incorrect[cls_mask][cls_easy] * cls_weight 
            * (sample_weight[cls_mask][cls_easy] > 0)
        )
        # Gentler linear update for hard examples
        sample_weight[cls_mask][cls_hard] = 1.0 + estimator_weight * 0.6 * incorrect[cls_mask][cls_hard] * cls_weight
    else:  # SAMME
        # Standard exponential for easy examples
        sample_weight[cls_mask][cls_easy] *= np.exp(
            estimator_weight * incorrect[cls_mask][cls_easy] * cls_weight
        )
        # Gentler linear update for hard examples
        sample_weight[cls_mask][cls_hard] *= (
            1.0 + estimator_weight * 0.6 * incorrect[cls_mask][cls_hard] * cls_weight
        )

# Normalize
sample_weight /= np.sum(sample_weight)
```

---

## 📊 **Implementation Timeline**

### **Today (1-2 hours)**
1. ✅ Fix F1 bonus multiplier inconsistency (2 min)
   - Line 1380: Change 0.4 → 0.6 (match SAMME.R)
   - Optionally increase both to 0.8 for stronger effect

2. ✅ Implement class-imbalance aware updates (45 min)
   - Highest impact improvement
   - Replace sample weight update sections

3. ✅ Add margin-based logic (30 min)
   - Integrate with class-imbalance updates
   - Improve stability

### **Tomorrow (Testing)**
4. Run benchmarks on UCI datasets
5. Compare to baseline results
6. Verify F1 improvements
7. Check for ROC-AUC regressions

---

## 🎯 **Expected Results After Implementation**

### Combined Impact (Steps 1-3):
- **F1 improvement**: +0.04-0.06 overall
- **Imbalanced datasets**: +0.02-0.03 F1 specifically
- **Stability**: Better convergence

### Performance Targets:
- **LinearBoost-L**: F1 rank #5 → #1-2
- **LinearBoost-K-exact**: F1 rank #3 → #1-2
- **Win count**: 1 total → 4-6 wins across variants
- **ROC-AUC**: Maintain or slight improvement

---

## 🔍 **Implementation Checklist**

### Quick Fix (2 minutes)
- [ ] Fix SAMME F1 bonus multiplier (line 1380: 0.4 → 0.6)
- [ ] Optionally strengthen both to 0.8 for maximum effect

### Class-Imbalance Updates (45 minutes)
- [ ] Implement for SAMME.R section (lines 1338-1347)
- [ ] Implement for SAMME section (line 1388)
- [ ] Test basic functionality

### Margin-Based Updates (30 minutes)
- [ ] Add margin calculation logic
- [ ] Integrate with class-imbalance updates
- [ ] Test with hard/easy example handling

### Testing (30 minutes)
- [ ] Test on single dataset
- [ ] Verify numerical stability
- [ ] Run full benchmark suite
- [ ] Compare results to baseline

---

## 🔧 **Quick Start: Minimal Viable Change**

If you want to see immediate impact with minimal code changes:

**Just do Step 1 + Step 2** (class-imbalance aware updates):

1. Fix F1 bonus (2 min): Line 1380, change `0.4` → `0.6`
2. Add class-imbalance logic (30 min): Replace sample weight updates

This combination should give you **+0.03-0.04 F1 improvement** and can be implemented in ~30 minutes.

---

## 📈 **Why These Steps Will Work**

1. **Strengthened F1 Bonus**: Current 0.4 multiplier is too weak. Increasing to 0.6-0.8 should make the F1 optimization more noticeable.

2. **Class-Imbalance Handling**: This is CatBoost's strength - explicit handling of minority classes. LinearBoost needs this to compete.

3. **Margin-Based Updates**: Prevents instability from hard examples, leading to better convergence and higher F1.

4. **Combined Effect**: All three work together synergistically - class-imbalance helps on imbalanced datasets, margin-based prevents overfitting, stronger F1 bonus aligns optimization.

---

## 🚨 **Important Notes**

- **Test incrementally**: Implement Step 1 first, test, then add Step 2, test, etc.
- **Monitor ROC-AUC**: Ensure we're not sacrificing ROC-AUC for F1 gains
- **Check stability**: Watch for numerical issues, NaN/Inf values
- **Benchmark comparison**: Always compare to other algorithms to account for random variation

---

**Files to modify**: `src/linearboost/linear_boost.py`  
**Estimated total time**: 1-2 hours  
**Expected result**: LinearBoost-L moves to rank #1-2 for F1 score

