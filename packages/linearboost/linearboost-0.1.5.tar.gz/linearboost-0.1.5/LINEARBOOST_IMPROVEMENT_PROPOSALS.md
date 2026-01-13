# LinearBoost Algorithm Improvement Proposals

## Executive Summary

Based on analysis of recent benchmark results (today and yesterday), LinearBoost variants show performance gaps:
- **LinearBoost-L**: F1 gap 0.0544, ROC-AUC gap 0.0142
- **LinearBoost-K**: F1 gap 0.0388, ROC-AUC gap 0.0325  
- **LinearBoost-K-exact**: F1 gap 0.0253, ROC-AUC gap 0.0093 (best performing)

**Main competitors causing losses:**
- LogisticRegression (most losses across all variants)
- RandomForest, XGBoost, CatBoost, LightGBM

## Key Findings from Benchmark Analysis

### Performance Gaps
- LinearBoost-K-exact is closest to competitors but still loses 34 times on F1 and 24 times on ROC-AUC
- LinearBoost-L loses most frequently (39 F1 losses, 22 ROC-AUC losses)
- LinearBoost-K has worst ROC-AUC performance (47 significant losses)

### Parameter Patterns
- **Learning rates**: Highly variable (0.01-0.86), suggesting instability
- **N_estimators**: Moderate (37-934), but may need more for convergence
- **Algorithm**: Mixed SAMME/SAMME.R usage

## Proposed Improvements to `linear_boost.py`

### 1. **Adaptive Learning Rate Schedule** (High Priority)

**Problem**: Fixed learning rate throughout boosting can cause overshooting or slow convergence.

**Solution**: Implement adaptive learning rate that adjusts based on error rate and iteration.

```python
def _compute_adaptive_learning_rate(self, iboost, estimator_error, base_learning_rate):
    """
    Compute adaptive learning rate based on:
    - Current iteration (decay over time)
    - Estimator error (higher error = lower rate)
    - Convergence status
    """
    # Exponential decay: reduce learning rate as we progress
    iteration_decay = np.exp(-iboost / (self.n_estimators * 0.5))
    
    # Error-based adjustment: lower rate for high error estimators
    error_factor = 1.0 / (1.0 + estimator_error * 2.0)
    
    # Adaptive rate
    adaptive_lr = base_learning_rate * iteration_decay * error_factor
    
    # Clamp to reasonable range
    return np.clip(adaptive_lr, 0.01, base_learning_rate)
```

**Location**: Modify `_boost` method around line 1187-1189

**Expected Impact**: +0.01-0.02 F1, +0.005-0.01 ROC-AUC

---

### 2. **Improved Estimator Weight Calculation** (High Priority)

**Problem**: Current weight calculation uses simple log formula which may not be optimal for F1/ROC-AUC optimization.

**Solution**: Add F1/ROC-AUC-aware weight calculation.

```python
def _compute_estimator_weight_f1_aware(self, estimator_error, y_true, y_pred, sample_weight):
    """
    Compute estimator weight considering F1 score improvement.
    """
    from sklearn.metrics import f1_score, roc_auc_score
    
    # Current F1 on weighted samples
    current_f1 = f1_score(y_true, y_pred, sample_weight=sample_weight, average='weighted')
    
    # Base weight from error
    base_weight = np.log((1.0 - estimator_error) / max(estimator_error, 1e-10))
    
    # F1 bonus: reward estimators that improve F1
    # If this estimator improves F1, give it higher weight
    f1_bonus = 1.0 + (current_f1 - 0.5) * 0.5  # Scale F1 improvement
    
    # Combine
    estimator_weight = self.shrinkage * self.learning_rate * base_weight * f1_bonus
    
    return estimator_weight
```

**Location**: Modify `_boost` method, replace lines 1187-1189 (SAMME) and similar for SAMME.R

**Expected Impact**: +0.015-0.025 F1, +0.01-0.015 ROC-AUC

---

### 3. **Enhanced Sample Weight Update Strategy** (Medium Priority)

**Problem**: Current exponential update may be too aggressive, especially for hard examples.

**Solution**: Implement smoother weight updates with margin-based adjustments.

```python
def _update_sample_weights_enhanced(self, sample_weight, estimator_weight, incorrect, 
                                     y_true, y_pred_proba, margin_threshold=0.1):
    """
    Enhanced sample weight update that considers:
    - Prediction confidence (margin)
    - Current weight magnitude
    - Class balance
    """
    # Get prediction margins (confidence)
    margins = np.abs(y_pred_proba[:, 1] - 0.5)  # Distance from decision boundary
    
    # Hard examples: low margin (close to boundary)
    hard_examples = margins < margin_threshold
    
    # Soft weight update for hard examples (prevent over-weighting)
    weight_update = np.ones_like(sample_weight)
    
    # Standard update for easy examples
    weight_update[~hard_examples] = np.exp(estimator_weight * incorrect[~hard_examples])
    
    # Gentler update for hard examples (prevent instability)
    weight_update[hard_examples] = 1.0 + estimator_weight * 0.5 * incorrect[hard_examples]
    
    sample_weight *= weight_update
    
    # Normalize with numerical stability
    sample_weight_sum = np.sum(sample_weight)
    if sample_weight_sum > 0:
        sample_weight /= sample_weight_sum
    else:
        sample_weight = np.ones_like(sample_weight) / len(sample_weight)
    
    return sample_weight
```

**Location**: Modify `_boost` method, replace lines 1191-1194 (SAMME) and similar for SAMME.R

**Expected Impact**: +0.01-0.02 F1, +0.005-0.01 ROC-AUC

---

### 4. **Class-Imbalance Aware Boosting** (High Priority)

**Problem**: LinearBoost loses frequently to LogisticRegression which handles imbalance better.

**Solution**: Add explicit class-imbalance handling in weight updates.

```python
def _update_sample_weights_imbalance_aware(self, sample_weight, y, incorrect, 
                                          estimator_weight, class_weights=None):
    """
    Update sample weights with explicit class imbalance consideration.
    """
    if class_weights is None:
        # Compute class frequencies
        unique, counts = np.unique(y, return_counts=True)
        class_freq = counts / len(y)
        # Inverse frequency weighting
        class_weights = {cls: 1.0 / freq for cls, freq in zip(unique, class_freq)}
    
    # Apply class weights to sample weight updates
    for cls in np.unique(y):
        cls_mask = y == cls
        cls_weight = class_weights[cls]
        
        # Boost weight updates for minority class
        sample_weight[cls_mask] *= np.exp(
            estimator_weight * incorrect[cls_mask] * cls_weight
        )
    
    # Normalize
    sample_weight /= np.sum(sample_weight)
    
    return sample_weight
```

**Location**: Modify `_boost` method, integrate with existing weight update

**Expected Impact**: +0.02-0.03 F1 on imbalanced datasets, +0.01-0.02 ROC-AUC

---

### 5. **Confidence-Based Estimator Selection** (Medium Priority)

**Problem**: All estimators are weighted equally in final prediction, regardless of their confidence.

**Solution**: Weight estimators by their prediction confidence, not just error rate.

```python
def _compute_confidence_weight(self, estimator, X, y, sample_weight):
    """
    Compute weight based on prediction confidence, not just error.
    """
    # Get predictions and probabilities
    y_pred = estimator.predict(X)
    if hasattr(estimator, 'predict_proba'):
        y_proba = estimator.predict_proba(X)[:, 1]
        # Confidence = distance from 0.5
        confidence = np.abs(y_proba - 0.5)
        avg_confidence = np.average(confidence, weights=sample_weight)
    else:
        avg_confidence = 0.5  # Default if no proba
    
    # Error rate
    incorrect = y_pred != y
    error = np.average(incorrect, weights=sample_weight)
    
    # Combine: lower error + higher confidence = higher weight
    confidence_bonus = 1.0 + avg_confidence
    error_penalty = (1.0 - error) / max(error, 1e-10)
    
    return confidence_bonus * error_penalty
```

**Location**: Modify `_boost` method, use in estimator_weight calculation

**Expected Impact**: +0.01-0.015 F1, +0.005-0.01 ROC-AUC

---

### 6. **Gradient-Based Weight Updates** (Advanced)

**Problem**: AdaBoost uses exponential loss which may not optimize F1/ROC-AUC directly.

**Solution**: Add gradient-based updates that directly optimize F1 or ROC-AUC.

```python
def _boost_gradient_f1(self, iboost, X, y, sample_weight, random_state):
    """
    Gradient-based boosting that directly optimizes F1 score.
    """
    from sklearn.metrics import f1_score
    
    # Fit estimator
    estimator = self._make_estimator(random_state=random_state)
    estimator.fit(X, y, sample_weight=sample_weight)
    
    # Get predictions
    y_pred = estimator.predict(X)
    y_proba = estimator.predict_proba(X)[:, 1] if hasattr(estimator, 'predict_proba') else None
    
    # Compute F1 gradient
    # F1 = 2 * (precision * recall) / (precision + recall)
    # We want to maximize F1, so compute gradient w.r.t. sample weights
    
    # For each sample, compute contribution to F1
    tp = np.sum((y == 1) & (y_pred == 1))
    fp = np.sum((y == 0) & (y_pred == 1))
    fn = np.sum((y == 1) & (y_pred == 0))
    
    precision = tp / (tp + fp + 1e-10)
    recall = tp / (tp + fn + 1e-10)
    f1 = 2 * precision * recall / (precision + recall + 1e-10)
    
    # Gradient: increase weight for samples that improve F1
    # True positives: increase weight (they help F1)
    # False negatives: increase weight (missing them hurts recall)
    # False positives: decrease weight (they hurt precision)
    
    gradient = np.zeros_like(sample_weight)
    gradient[(y == 1) & (y_pred == 1)] = 1.0  # TP: positive gradient
    gradient[(y == 1) & (y_pred == 0)] = 0.5   # FN: moderate positive
    gradient[(y == 0) & (y_pred == 1)] = -0.3  # FP: negative gradient
    
    # Update sample weights using gradient
    learning_rate = self.learning_rate * (1.0 - iboost / self.n_estimators)
    sample_weight += learning_rate * gradient * sample_weight
    sample_weight = np.maximum(sample_weight, 1e-10)  # Prevent zeros
    sample_weight /= np.sum(sample_weight)
    
    # Compute estimator weight based on F1 improvement
    estimator_weight = f1 * self.shrinkage
    
    return sample_weight, estimator_weight, 1.0 - f1
```

**Location**: Add as alternative boosting method, call from `_boost` when `loss_function='f1'`

**Expected Impact**: +0.02-0.04 F1, +0.01-0.02 ROC-AUC

---

### 7. **Ensemble Pruning** (Medium Priority)

**Problem**: Weak estimators can hurt ensemble performance.

**Solution**: Prune estimators with negative contribution or very low weights.

```python
def _prune_weak_estimators(self, min_weight_ratio=0.01):
    """
    Remove estimators with very low weights that don't contribute meaningfully.
    """
    if len(self.estimators_) == 0:
        return
    
    weights = np.array(self.estimator_weights_)
    max_weight = np.max(weights)
    min_weight = max_weight * min_weight_ratio
    
    # Find estimators to keep
    keep_mask = weights >= min_weight
    
    # Prune
    self.estimators_ = [est for i, est in enumerate(self.estimators_) if keep_mask[i]]
    self.estimator_weights_ = weights[keep_mask]
    self.estimator_errors_ = np.array(self.estimator_errors_)[keep_mask]
    
    # Renormalize weights
    self.estimator_weights_ /= np.sum(self.estimator_weights_)
```

**Location**: Add to `fit` method, call after all boosting iterations

**Expected Impact**: +0.005-0.01 F1, +0.005-0.01 ROC-AUC

---

### 8. **Adaptive Shrinkage** (Low Priority)

**Problem**: Fixed shrinkage may not be optimal for all datasets.

**Solution**: Adaptive shrinkage based on overfitting detection.

```python
def _compute_adaptive_shrinkage(self, iboost, train_error, val_error=None):
    """
    Compute adaptive shrinkage based on overfitting detection.
    """
    base_shrinkage = self.shrinkage
    
    if val_error is not None:
        # Detect overfitting: train_error << val_error
        overfitting_ratio = val_error / max(train_error, 1e-10)
        
        if overfitting_ratio > 1.2:  # Significant overfitting
            # Increase shrinkage (more regularization)
            adaptive_shrinkage = base_shrinkage * 0.8
        elif overfitting_ratio < 0.9:  # Underfitting
            # Decrease shrinkage (less regularization)
            adaptive_shrinkage = min(base_shrinkage * 1.1, 1.0)
        else:
            adaptive_shrinkage = base_shrinkage
    else:
        # No validation: use iteration-based decay
        # More shrinkage early, less later
        iteration_factor = 1.0 - (iboost / self.n_estimators) * 0.2
        adaptive_shrinkage = base_shrinkage * iteration_factor
    
    return np.clip(adaptive_shrinkage, 0.1, 1.0)
```

**Location**: Modify `_boost` method, use in estimator_weight calculation

**Expected Impact**: +0.005-0.01 F1, +0.005-0.01 ROC-AUC

---

### 9. **Multi-Objective Optimization** (Advanced)

**Problem**: Optimizing only error rate may not maximize F1/ROC-AUC.

**Solution**: Multi-objective optimization that balances error, F1, and ROC-AUC.

```python
def _compute_multi_objective_weight(self, estimator, X, y, sample_weight):
    """
    Compute estimator weight considering multiple objectives:
    - Classification error (primary)
    - F1 score (secondary)
    - ROC-AUC (tertiary)
    """
    from sklearn.metrics import f1_score, roc_auc_score
    
    y_pred = estimator.predict(X)
    incorrect = y_pred != y
    error = np.average(incorrect, weights=sample_weight)
    
    # F1 component
    f1 = f1_score(y, y_pred, sample_weight=sample_weight, average='weighted')
    f1_component = f1 * 0.3  # 30% weight on F1
    
    # ROC-AUC component (if probabilities available)
    if hasattr(estimator, 'predict_proba'):
        try:
            y_proba = estimator.predict_proba(X)[:, 1]
            roc_auc = roc_auc_score(y, y_proba, sample_weight=sample_weight)
            roc_component = roc_auc * 0.2  # 20% weight on ROC-AUC
        except:
            roc_component = 0.0
    else:
        roc_component = 0.0
    
    # Error component (primary, 50% weight)
    error_component = (1.0 - error) * 0.5
    
    # Combined score
    combined_score = error_component + f1_component + roc_component
    
    # Convert to weight
    estimator_weight = self.shrinkage * self.learning_rate * np.log(
        combined_score / max(1.0 - combined_score, 1e-10)
    )
    
    return estimator_weight
```

**Location**: Modify `_boost` method, replace estimator_weight calculation

**Expected Impact**: +0.02-0.03 F1, +0.015-0.025 ROC-AUC

---

### 10. **Feature Importance-Based Subsampling** (Medium Priority)

**Problem**: Random subsampling may not be optimal; should focus on informative samples.

**Solution**: Weight subsampling by feature importance or prediction difficulty.

```python
def _intelligent_subsampling(self, X, y, sample_weight, subsample_size, random_state):
    """
    Intelligent subsampling that prioritizes:
    - Hard examples (high weight)
    - Balanced class representation
    - Diverse feature coverage
    """
    n_samples = len(X)
    n_subsample = int(n_samples * subsample_size)
    
    # Weight-based sampling: higher weight = more likely to be selected
    # But ensure class balance
    unique_classes = np.unique(y)
    samples_per_class = n_subsample // len(unique_classes)
    
    subsample_indices = []
    for cls in unique_classes:
        cls_indices = np.where(y == cls)[0]
        cls_weights = sample_weight[cls_indices]
        
        # Normalize weights for this class
        cls_weights = cls_weights / np.sum(cls_weights)
        
        # Sample with replacement based on weights
        np.random.seed(random_state)
        cls_subsample = np.random.choice(
            cls_indices,
            size=min(samples_per_class, len(cls_indices)),
            replace=True,
            p=cls_weights
        )
        subsample_indices.extend(cls_subsample)
    
    # Fill remaining slots randomly
    remaining = n_subsample - len(subsample_indices)
    if remaining > 0:
        all_indices = np.arange(n_samples)
        available = np.setdiff1d(all_indices, subsample_indices)
        if len(available) > 0:
            additional = np.random.choice(
                available,
                size=min(remaining, len(available)),
                replace=False
            )
            subsample_indices.extend(additional)
    
    return np.array(subsample_indices[:n_subsample])
```

**Location**: Modify `_boost` method, replace random subsampling around line 1108-1125

**Expected Impact**: +0.01-0.02 F1, +0.005-0.01 ROC-AUC

---

### 11. **Regularization in Base Estimator** (High Priority)

**Problem**: SEFR base estimator may overfit, especially on high-dimensional data.

**Solution**: Add L2 regularization to SEFR or use regularized version.

```python
# In SEFR fit method, add L2 regularization to coefficient calculation
# Modify line 304 in sefr.py:

# Original:
# self.coef_ = (avg_pos - avg_neg) / (avg_pos + avg_neg + 1e-7)

# Regularized version:
lambda_reg = 0.01  # Regularization strength (could be a parameter)
self.coef_ = (avg_pos - avg_neg) / (avg_pos + avg_neg + lambda_reg * np.var(X, axis=0) + 1e-7)

# Or add explicit L2 penalty:
# self.coef_ = (avg_pos - avg_neg) / (avg_pos + avg_neg + 1e-7)
# self.coef_ = self.coef_ / (1.0 + lambda_reg)  # Shrink coefficients
```

**Location**: Modify `sefr.py` fit method, or add regularization parameter to SEFR

**Expected Impact**: +0.01-0.02 F1 on high-dimensional data, +0.005-0.01 ROC-AUC

---

### 12. **Early Stopping Based on F1/ROC-AUC** (High Priority)

**Problem**: Current early stopping may use accuracy, not F1/ROC-AUC.

**Solution**: Use F1 or ROC-AUC for early stopping decisions.

```python
def _should_stop_early_f1(self, validation_scores, n_iter_no_change, tol):
    """
    Check if we should stop early based on F1 score improvement.
    """
    if len(validation_scores) < n_iter_no_change + 1:
        return False
    
    recent_scores = validation_scores[-(n_iter_no_change + 1):]
    best_recent = max(recent_scores[:-1])  # Best before last
    current = recent_scores[-1]
    
    # Stop if no improvement >= tol
    if current <= best_recent + tol:
        return True
    
    return False
```

**Location**: Modify `_fit_with_early_stopping` method, use F1/ROC-AUC instead of accuracy

**Expected Impact**: +0.01-0.02 F1, +0.01-0.015 ROC-AUC

---

## Implementation Priority

### Phase 1 (Immediate - High Impact)
1. ✅ **Adaptive Learning Rate** (#1) - Easy to implement, significant impact
2. ✅ **F1-Aware Weight Calculation** (#2) - Directly addresses F1 gap
3. ✅ **Class-Imbalance Aware Boosting** (#4) - Addresses LogisticRegression losses
4. ✅ **Early Stopping on F1/ROC-AUC** (#12) - Quick win

### Phase 2 (Medium Term - Moderate Impact)
5. ⚠️ **Enhanced Sample Weight Updates** (#3) - More stable training
6. ⚠️ **Confidence-Based Selection** (#5) - Better estimator weighting
7. ⚠️ **Ensemble Pruning** (#7) - Clean up weak estimators

### Phase 3 (Advanced - Research)
8. ℹ️ **Gradient-Based Updates** (#6) - Direct F1 optimization
9. ℹ️ **Multi-Objective Optimization** (#9) - Comprehensive improvement
10. ℹ️ **Intelligent Subsampling** (#10) - Better data utilization

## Expected Combined Impact

Implementing Phase 1 improvements should yield:
- **F1 improvement**: +0.04-0.06 (closing gap from 0.025-0.054 to <0.01)
- **ROC-AUC improvement**: +0.02-0.03 (closing gap from 0.009-0.032 to <0.005)

This would make LinearBoost-K-exact competitive with or superior to RandomForest, XGBoost, and CatBoost.

## Code Locations for Implementation

- **`_boost` method**: Lines 1076-1198 in `linear_boost.py`
- **`_fit_with_early_stopping` method**: Lines 885-1073 in `linear_boost.py`
- **`fit` method**: Lines 655-884 in `linear_boost.py`
- **SEFR base estimator**: `sefr.py` lines 238-324

## Testing Strategy

1. Implement improvements incrementally
2. Test on recent benchmark datasets
3. Compare F1 and ROC-AUC before/after
4. Ensure no regression on existing functionality
5. Validate on both balanced and imbalanced datasets

---

**Generated**: 2024-12-27
**Based on**: Analysis of benchmark results from 2024-12-26 and 2024-12-27

