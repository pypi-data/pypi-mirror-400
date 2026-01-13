# Why LinearBoost-Auto Underperforms Individual Variants

## Problem Statement

After increasing trials to 500 and adding pruning, LinearBoost-Auto still doesn't achieve the best F1 scores on several datasets. The individual variants (LinearBoost-L, LinearBoost-K, LinearBoost-K-exact) consistently outperform Auto on the three datasets analyzed:

1. **Hepatitis**: LinearBoost-L best (F1=0.8394) vs Auto (F1=0.8345) - Gap: 0.49%
2. **Banknote**: LinearBoost-K-exact best (F1=0.9989) vs Auto (F1=0.9878) - Gap: 1.10%
3. **Kidney**: LinearBoost-K best (F1=0.9870) vs Auto (F1=0.9230) - Gap: 6.40%

## Root Cause Analysis

### 1. **Trial Budget Division**

**The Fundamental Issue:** LinearBoost-Auto must divide its optimization budget across TWO search spaces, while specialized variants use their full budget on a single space.

| Variant | Search Space | Effective Trials per Space |
|---------|-------------|---------------------------|
| LinearBoost-Auto | Linear + Non-linear | ~250 trials per space |
| LinearBoost-L | Linear only | ~500 trials |
| LinearBoost-K | Non-linear (approx) only | ~500 trials |
| LinearBoost-K-exact | Non-linear (exact) only | ~500 trials |

### 2. **Search Space Complexity**

**LinearBoost-Auto Search Space:**
```
Top-level choice: kernel_type ∈ {linear, non_linear}  # 2 options

If linear:
  - n_estimators: [10, 500]
  - learning_rate: log[0.01, 1.0]
  - algorithm: {SAMME, SAMME.R}
  - scaler: {minmax, robust, quantile-uniform, standard}
  - early_stopping: {True, False}
  - subsample: [0.5, 1.0]
  - Early stopping params (conditional)
  
If non_linear:
  - All linear params PLUS:
  - kernel_subtype: {rbf, poly, sigmoid}  # 3 options
  - gamma: log[1e-3, 10.0]
  - use_approx: {True, False}  # 2 options
  - If approx: approx_type, n_components
  - If poly/sigmoid: degree, coef0
```

**LinearBoost-L Search Space:**
```
  - n_estimators: [10, 500]
  - learning_rate: log[0.01, 1.0]
  - algorithm: {SAMME, SAMME.R}
  - scaler: {minmax, robust, quantile-uniform, quantile-normal, standard}
  - early_stopping: {True, False}
  - subsample: [0.5, 1.0]
  - Early stopping params (conditional)
  # Focused only on linear kernel optimization
```

### 3. **How Optuna Distributes Trials**

Optuna uses TPE (Tree-structured Parzen Estimator) which:
- Explores categorical choices **uniformly** initially
- Then focuses on promising regions
- For `kernel_type ∈ {linear, non_linear}`, roughly 50% of trials go to each initially
- As optimization progresses, it may shift more trials to the better-performing option
- BUT: Early exploration is split, meaning fewer trials to discover optimal configurations in each space

### 4. **Pruning Amplifies the Problem**

The MedianPruner with `n_startup_trials=5` and `n_warmup_steps=2`:
- Needs at least 5 trials before pruning
- Needs 2 CV folds before pruning within a trial
- This means Auto needs ~5 trials for linear AND ~5 trials for non-linear before meaningful pruning
- Specialized variants can prune more aggressively since they're exploring a single focused space

## Evidence from Results

### Hepatitis Dataset (n=155, small)
- **Auto choice**: `kernel_type='linear'` → F1=0.8345
- **Best**: LinearBoost-L → F1=0.8394 (gap: 0.49%)
- **Analysis**: Auto chose linear (correct choice!) but couldn't find the optimal linear configuration because it spent ~50% of trials exploring non-linear space

### Banknote Authentication (n=1372, medium)
- **Auto choice**: `kernel_type='non_linear'` (sigmoid with approximation) → F1=0.9878
- **Best**: LinearBoost-K-exact (rbf, exact) → F1=0.9989 (gap: 1.10%)
- **Analysis**: Auto explored non-linear but:
  1. Didn't find exact kernel (used approximation)
  2. Chose sigmoid instead of optimal rbf
  3. Had less budget to fine-tune within non-linear space

### Chronic Kidney Disease (n=400, small)
- **Auto choice**: `kernel_type='non_linear'` (rbf with approximation) → F1=0.9230
- **Best**: LinearBoost-K (rbf with approximation) → F1=0.9870 (gap: 6.40%)
- **Analysis**: Auto found the right kernel type (rbf) and approximation approach, but:
  1. Couldn't find optimal hyperparameters due to split budget
  2. LinearBoost-K had full 500 trials to fine-tune within the approximation space

## Solutions

### Option 1: Increase Trials for Auto (Simple)
```python
# In benchmark_3.py, make Auto use more trials
if model_name == 'LinearBoost-Auto':
    n_trials = 1000  # 2x budget to compensate for split
else:
    n_trials = 500
```

**Pros:**
- Simple to implement
- Maintains fairness in total optimization time
- Addresses the budget division issue

**Cons:**
- Takes longer to optimize
- May still underperform due to search space complexity

### Option 2: Multi-Stage Optimization (Better)
```python
def _optimize_linearboost_auto_multistage(self, cv):
    """Two-stage optimization for LinearBoost-Auto."""
    # Stage 1: Quick comparison between linear and non-linear (50 trials each)
    linear_study = self._optimize_linearboost_linear_quick(cv, n_trials=50)
    non_linear_study = self._optimize_non_linear_quick(cv, n_trials=50)
    
    # Stage 2: Deep optimization of best type (remaining 400 trials)
    if linear_study.best_value >= non_linear_study.best_value:
        return self._optimize_linearboost_linear(cv, n_trials=400)
    else:
        return self._optimize_non_linear_deep(cv, n_trials=400)
```

**Pros:**
- Allocates budget intelligently
- Should match or exceed specialized variant performance
- Still uses same total trials (500)

**Cons:**
- More complex implementation
- Requires creating "quick" optimization variants

### Option 3: Hierarchical Optimization (Best but Complex)
```python
def _optimize_linearboost_auto_hierarchical(self, cv):
    """Hierarchical optimization with adaptive budget allocation."""
    # Use Optuna's MultiObjectiveStudy or implement custom budget allocation
    # that dynamically shifts trials toward promising kernel types
```

**Pros:**
- Most theoretically sound
- Adapts budget allocation based on progress

**Cons:**
- Complex to implement
- May require custom Optuna integration

### Option 4: Ensemble Approach (Alternative)
Instead of optimizing Auto separately, use the best of all variants:
```python
# In evaluation, pick best variant per dataset
best_linearboost = max(
    results['LinearBoost-L'],
    results['LinearBoost-K'],
    results['LinearBoost-K-exact'],
    key=lambda x: x['f1_mean']
)
```

**Pros:**
- Always gets best performance
- Simple to implement

**Cons:**
- Doesn't solve Auto optimization
- Requires running all variants

## Recommendation

**Immediate Fix**: Implement **Option 2 (Multi-Stage Optimization)**
- Gives Auto fair shot at finding optimal configuration
- Maintains same total optimization budget
- Should close the performance gap

**Long-term**: Consider **Option 3** for production use, or accept that Auto is a convenience method that may sacrifice ~1-2% F1 for automatic kernel selection.

## Impact Assessment

The performance gaps observed:
- **Hepatitis**: 0.49% - Negligible
- **Banknote**: 1.10% - Small, but noticeable
- **Kidney**: 6.40% - Significant

The Kidney dataset gap is concerning and suggests the multi-stage approach is necessary for datasets where the optimal configuration requires fine-tuning within a specific kernel type space.
