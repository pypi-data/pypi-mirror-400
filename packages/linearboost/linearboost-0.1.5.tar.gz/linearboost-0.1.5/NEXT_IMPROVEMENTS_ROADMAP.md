# LinearBoost Improvement Roadmap

**Last Updated**: December 29, 2024  
**Status**: Class-imbalance aware updates implemented (minimal impact observed)

---

## ✅ **Completed Improvements**

1. **Adaptive Learning Rate Schedule** - ✅ Implemented
   - Dynamically adjusts learning rate based on iteration and estimator error
   - Expected: Better convergence, improved F1

2. **Early Stopping on F1/ROC-AUC** - ✅ Implemented
   - Uses F1 or ROC-AUC instead of accuracy for early stopping
   - Result: +0.0248 F1 improvement observed

3. **F1-Aware Estimator Weighting** - ✅ Implemented
   - Rewards estimators with good F1 performance
   - Result: Minimal impact, may need strengthening

4. **Class-Imbalance Aware Sample Weight Updates** - ✅ Implemented
   - Gives higher weight boosts to minority class samples
   - Result: Minimal impact, neutral overall

---

## 🎯 **Next Proposed Improvements (Priority Order)**

### **Priority 1: Margin-Based Sample Weight Updates** (HIGHEST IMPACT - STABILITY)

**Status**: Not implemented  
**Expected Impact**: +0.01-0.015 F1, improved stability  
**Estimated Time**: 30 minutes  
**Complexity**: Medium

**Why This Is Important**:
- Current exponential weight updates can be too aggressive for hard examples
- Low-confidence predictions near decision boundary cause instability
- Gentler updates for hard examples prevent overshooting optimal weights
- Complements class-imbalance handling for better overall performance

**Implementation Details**:
- Compute prediction confidence (margin from decision boundary)
- Use standard exponential update for easy examples
- Use gentler linear update for hard examples (confidence < threshold)
- Integrate with existing class-imbalance aware updates

**Code Location**: `src/linearboost/linear_boost.py`
- SAMME.R section: lines 1338-1355
- SAMME section: lines 1402-1413

**Expected Benefits**:
- More stable training (reduced weight explosion)
- Better handling of borderline cases
- Synergistic with class-imbalance updates
- Potentially measurable F1 improvement when combined

---

### **Priority 2: Strengthen F1 Bonus Multiplier** (QUICK WIN)

**Status**: Partially implemented (inconsistent between SAMME and SAMME.R)  
**Expected Impact**: +0.01-0.015 F1  
**Estimated Time**: 2 minutes  
**Complexity**: Low

**Why This Is Important**:
- Current F1 bonus is too subtle (0.4-0.6 multiplier)
- Analysis showed minimal impact from F1-aware weighting
- Increasing multiplier should make effect more noticeable

**Current State**:
- SAMME.R: Uses 0.6 multiplier (line 1330)
- SAMME: Uses 0.4 multiplier (line 1394) - **Inconsistency!**

**Implementation**:
- Make both algorithms consistent
- Increase multiplier from 0.4-0.6 to 0.6-0.8 for stronger effect

**Code Changes**:
```python
# Line 1394 (SAMME): Change 0.4 → 0.6 (match SAMME.R)
f1_bonus = 1.0 + (f1 - 0.5) * 0.6  # Increase from 0.4

# Optional: Strengthen both to 0.8 for maximum effect
f1_bonus = 1.0 + (f1 - 0.5) * 0.8  # Max 1.4x multiplier
```

---

### **Priority 3: Strengthen Class-Imbalance Weighting** (ENHANCEMENT)

**Status**: Implemented but weak effect  
**Expected Impact**: +0.01-0.02 F1 on imbalanced datasets  
**Estimated Time**: 5 minutes  
**Complexity**: Low

**Why This Is Important**:
- Current implementation showed minimal impact
- May need stronger weighting to see measurable improvement
- Haberman's Survival showed positive signals (+0.0060 F1 for LinearBoost-L)

**Current Implementation**:
```python
class_weights = {cls: 1.0 / freq for cls, freq in zip(unique_classes, class_freq)}
```

**Proposed Strengthening**:
```python
# Option A: Square root (moderate)
class_weights = {cls: np.sqrt(1.0 / freq) for cls, freq in zip(unique_classes, class_freq)}

# Option B: Power 1.5 (stronger)
class_weights = {cls: (1.0 / freq) ** 1.5 for cls, freq in zip(unique_classes, class_freq)}

# Option C: Adaptive based on imbalance severity
imbalance_ratio = min(class_freq) / max(class_freq)
if imbalance_ratio < 0.3:  # Severely imbalanced
    power = 1.5
elif imbalance_ratio < 0.5:  # Moderately imbalanced
    power = 1.25
else:  # Relatively balanced
    power = 1.0
class_weights = {cls: (1.0 / freq) ** power for cls, freq in zip(unique_classes, class_freq)}
```

**Recommendation**: Start with Option C (adaptive) - strongest on severely imbalanced datasets, moderate on others.

---

### **Priority 4: Confidence-Based Estimator Weighting** (ADVANCED)

**Status**: Not implemented  
**Expected Impact**: +0.01-0.015 F1  
**Estimated Time**: 45 minutes  
**Complexity**: Medium-High

**Why This Is Important**:
- Current estimator weighting uses error rate and F1 score
- Adding confidence (prediction certainty) can help identify high-quality estimators
- Low-confidence estimators may be noisy or unreliable

**Implementation Details**:
- Compute average prediction confidence for each estimator
- Apply confidence bonus to estimator weight (in addition to F1 bonus)
- High-confidence estimators get higher weights

**Code Location**: `src/linearboost/linear_boost.py`, `_boost` method
- After F1 bonus calculation
- For both SAMME and SAMME.R

**Code Concept**:
```python
# Compute average confidence
if hasattr(estimator, 'predict_proba'):
    y_proba = estimator.predict_proba(X)[:, 1]
    confidence = np.abs(y_proba - 0.5)  # Distance from decision boundary
    avg_confidence = np.average(confidence, weights=sample_weight)
    confidence_bonus = 0.9 + avg_confidence * 0.4  # 0.9x to 1.3x multiplier
    estimator_weight *= confidence_bonus
```

---

### **Priority 5: Ensemble Pruning** (OPTIMIZATION)

**Status**: Not implemented  
**Expected Impact**: +0.005-0.01 F1, reduced model size  
**Estimated Time**: 30 minutes  
**Complexity**: Medium

**Why This Is Important**:
- Remove weak estimators that contribute little or negatively
- Smaller models are faster and sometimes more accurate
- Reduces overfitting from too many weak estimators

**Implementation Details**:
- At end of `fit()` method, prune weak estimators
- Remove estimators with weights below threshold (e.g., 2% of max weight)
- Update estimator_weights_ and estimators_ arrays

**Code Location**: `src/linearboost/linear_boost.py`, end of `fit()` method

**Code Concept**:
```python
# At end of fit(), after all boosting iterations
if len(self.estimators_) > 5:  # Only prune if we have enough estimators
    weights = np.array(self.estimator_weights_)
    max_weight = np.max(weights)
    min_weight_threshold = max_weight * 0.02  # 2% of max
    
    keep_mask = weights >= min_weight_threshold
    self.estimators_ = [est for i, est in enumerate(self.estimators_) if keep_mask[i]]
    self.estimator_weights_ = weights[keep_mask].tolist()
    
    # Renormalize weights
    total_weight = sum(self.estimator_weights_)
    if total_weight > 0:
        self.estimator_weights_ = [w / total_weight for w in self.estimator_weights_]
```

---

### **Priority 6: Multi-Objective Optimization** (ADVANCED)

**Status**: Not implemented  
**Expected Impact**: Better balance between F1 and ROC-AUC  
**Estimated Time**: 2-3 hours  
**Complexity**: High

**Why This Is Important**:
- Early stopping on F1 improved F1 but may have slight ROC-AUC trade-off
- Optimize for both metrics simultaneously
- Better overall performance profile

**Implementation Details**:
- Combine F1 and ROC-AUC scores for early stopping decision
- Weighted combination: `score = 0.7 * f1 + 0.3 * roc_auc`
- Adjustable weights based on preference

---

### **Priority 7: SEFR Regularization** (COMPONENT-LEVEL)

**Status**: Not implemented  
**Expected Impact**: +0.01-0.02 F1, reduced overfitting  
**Estimated Time**: 1-2 hours  
**Complexity**: High (requires modifying `sefr.py`)

**Why This Is Important**:
- SEFR is the base estimator for LinearBoost
- Adding regularization to SEFR can improve base estimator quality
- Better base estimators → better ensemble

**Implementation Details**:
- Add L1/L2 regularization to SEFR loss function
- Hyperparameter: `regularization` parameter
- Requires modifying `src/linearboost/sefr.py`

---

## 📋 **Recommended Implementation Order**

### **Phase 1: Quick Wins (Today - 1 hour)**
1. ✅ **Fix F1 bonus inconsistency** (2 min) - Priority 2
2. ✅ **Implement margin-based updates** (30 min) - Priority 1
3. ✅ **Strengthen class-imbalance weighting** (5 min) - Priority 3

**Expected Combined Impact**: +0.02-0.04 F1 improvement

### **Phase 2: Advanced Features (This Week)**
4. **Confidence-based estimator weighting** (45 min) - Priority 4
5. **Ensemble pruning** (30 min) - Priority 5

**Expected Combined Impact**: +0.015-0.025 additional F1 improvement

### **Phase 3: Research & Optimization (Next Week)**
6. **Multi-objective optimization** (2-3 hours) - Priority 6
7. **SEFR regularization** (1-2 hours) - Priority 7

---

## 🎯 **Target Performance Goals**

### Current State:
- LinearBoost-L: F1 rank #5
- LinearBoost-K-exact: F1 rank #3
- Goal: Move to rank #1-2

### Expected After Phase 1:
- F1 improvement: +0.02-0.04
- Should move LinearBoost-L to rank #3-4
- Should move LinearBoost-K-exact to rank #1-2

### Expected After Phase 2:
- F1 improvement: +0.035-0.065 total
- Should move LinearBoost-L to rank #1-2
- Should consolidate LinearBoost-K-exact at rank #1

---

## 🔍 **Testing Strategy**

After each phase:
1. Run benchmarks on UCI datasets
2. Compare before/after results
3. Check for ROC-AUC regressions
4. Verify improvements are statistically significant
5. Adjust parameters if needed

**Key Metrics to Monitor**:
- F1 score (primary)
- ROC-AUC (secondary, should maintain or improve)
- Training time (should not significantly increase)
- Model size (may decrease with pruning)

---

## 📝 **Implementation Checklist**

### Phase 1 (Priority):
- [ ] Fix F1 bonus multiplier inconsistency (SAMME: 0.4 → 0.6)
- [ ] Implement margin-based sample weight updates
- [ ] Strengthen class-imbalance weighting (adaptive power)
- [ ] Test on single dataset
- [ ] Run full benchmark suite
- [ ] Compare results and document impact

### Phase 2 (Next):
- [ ] Implement confidence-based estimator weighting
- [ ] Implement ensemble pruning
- [ ] Test and benchmark
- [ ] Evaluate cumulative improvements

### Phase 3 (Research):
- [ ] Research multi-objective optimization approaches
- [ ] Implement and test
- [ ] Evaluate SEFR regularization feasibility
- [ ] Decide on implementation priority

---

## 💡 **Quick Start: Next Immediate Action**

**Right Now**: Implement Priority 1 (Margin-Based Updates) + Priority 2 (Fix F1 Bonus)

This combination should take ~35 minutes and provide measurable F1 improvement.

**Estimated Impact**: +0.02-0.03 F1 improvement  
**Risk**: Low (additive improvements, no breaking changes)  
**Complexity**: Medium (requires careful integration with existing code)

---

**Last Analysis**: Class-imbalance aware updates showed minimal impact, suggesting we need stronger/more synergistic improvements to see measurable gains.
