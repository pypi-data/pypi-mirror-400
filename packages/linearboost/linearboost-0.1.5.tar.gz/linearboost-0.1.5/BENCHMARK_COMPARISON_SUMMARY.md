# Benchmark Comparison: Most Recent vs Second Most Recent

**Date**: December 29, 2024  
**Datasets Compared**: 7 UCI datasets  
**Comparison**: Most recent benchmarks (after margin-based updates) vs. Second most recent (before margin-based updates)

---

## ⚠️ **CRITICAL FINDING: Performance Regression**

All LinearBoost variants show **significant regressions** in F1 score and rankings after implementing margin-based updates.

---

## 📊 **Performance Changes Summary**

### **LinearBoost-K-exact** (Previously Rank #1 for F1)

**Performance Changes:**
- **F1 Score**: -0.0209 ± 0.0236 (5 regressions, 2 improvements)
- **ROC-AUC**: -0.0074 ± 0.0356 (4 regressions, 1 improvement)
- **Training Time**: +0.1505 seconds (+100%)
- **Inference Time**: +4.53 ms

**Ranking Changes:**
- **F1**: #1 → **#7** (↓ -6 positions) ⚠️ **MAJOR REGRESSION**
- **ROC-AUC**: #6 → #7 (↓ -1 position)
- **Training Time**: #4 → #8 (↓ -4 positions)
- **Inference Time**: #7 → #8 (↓ -1 position)

**Verdict**: **Significant performance regression** - Lost its #1 F1 ranking.

---

### **LinearBoost-L**

**Performance Changes:**
- **F1 Score**: -0.0372 ± 0.0478 (5 regressions, 1 improvement)
- **ROC-AUC**: -0.0167 ± 0.0335 (4 regressions, 2 improvements)
- **Training Time**: +0.0671 seconds (+100%)
- **Inference Time**: +2.22 ms

**Ranking Changes:**
- **F1**: #7 → **#8** (↓ -1 position)
- **ROC-AUC**: #8 → #8 (→ no change)
- **Training Time**: #3 → #5 (↓ -2 positions)
- **Inference Time**: #5 → #7 (↓ -2 positions)

**Verdict**: **Performance regression** - Dropped 1 position in F1, became slower.

---

### **LinearBoost-K**

**Performance Changes:**
- **F1 Score**: -0.0388 ± 0.0554 (5 regressions, 0 improvements)
- **ROC-AUC**: -0.0646 ± 0.0512 (7 regressions, 0 improvements)
- **Training Time**: +0.0810 seconds (+100%)
- **Inference Time**: -0.087 ms (slightly faster)

**Ranking Changes:**
- **F1**: #9 → #9 (→ no change - still worst)
- **ROC-AUC**: #9 → #9 (→ no change - still worst)
- **Training Time**: #6 → #6 (→ no change)
- **Inference Time**: #8 → #6 (↑ -2 positions - improved)

**Verdict**: **Performance regression** but maintained position (already worst).

---

## 🏆 **Overall Algorithm Rankings**

### **F1 Score Rankings**

| Algorithm | Previous | Current | Change |
|-----------|----------|---------|--------|
| **CatBoost** | #2 | **#1** | ↑ -1 |
| **RandomForest** | #3 | **#2** | ↑ -1 |
| **XGBoost** | #6 | **#3** | ↑ -3 |
| LightGBM | #4 | #4 | → 0 |
| LogisticRegression | #5 | #5 | → 0 |
| **TabPFN** | #8 | **#6** | ↑ -2 |
| **LinearBoost-K-exact** | **#1** | **#7** | ↓ +6 ⚠️ |
| **LinearBoost-L** | #7 | **#8** | ↓ +1 |
| LinearBoost-K | #9 | #9 | → 0 |

**Key Changes:**
- LinearBoost-K-exact dropped from **#1 to #7** (worst regression)
- CatBoost took over #1 spot
- XGBoost improved significantly (#6 → #3)
- All LinearBoost variants now rank #7, #8, #9 (bottom 3)

---

### **ROC-AUC Rankings**

| Algorithm | Previous | Current | Change |
|-----------|----------|---------|--------|
| RandomForest | #1 | #1 | → 0 |
| **CatBoost** | #3 | **#2** | ↑ -1 |
| **LightGBM** | #2 | **#3** | ↓ +1 |
| XGBoost | #4 | #4 | → 0 |
| TabPFN | #5 | #5 | → 0 |
| **LogisticRegression** | #7 | **#6** | ↑ -1 |
| **LinearBoost-K-exact** | #6 | **#7** | ↓ +1 |
| LinearBoost-L | #8 | #8 | → 0 |
| LinearBoost-K | #9 | #9 | → 0 |

**Key Changes:**
- LinearBoost-K-exact dropped from #6 to #7
- All LinearBoost variants still in bottom 3 for ROC-AUC

---

### **Training Time Rankings** (Lower is Better)

| Algorithm | Previous | Current | Change |
|-----------|----------|---------|--------|
| LogisticRegression | #1 | #1 | → 0 |
| TabPFN | #2 | #2 | → 0 |
| **CatBoost** | #9 | **#3** | ↓ -6 |
| RandomForest | #5 | #4 | ↓ -1 |
| **LinearBoost-L** | #3 | **#5** | ↑ +2 |
| LinearBoost-K | #6 | #6 | → 0 |
| XGBoost | #7 | #7 | → 0 |
| **LinearBoost-K-exact** | #4 | **#8** | ↑ +4 |
| LightGBM | #8 | #9 | ↑ +1 |

**Key Changes:**
- LinearBoost variants became slower (moved down in rankings)
- CatBoost became much faster (moved from #9 to #3)

---

### **Inference Time Rankings** (Lower is Better)

| Algorithm | Previous | Current | Change |
|-----------|----------|---------|--------|
| CatBoost | #1 | #1 | → 0 |
| LightGBM | #2 | #2 | → 0 |
| LogisticRegression | #3 | #3 | → 0 |
| XGBoost | #4 | #4 | → 0 |
| RandomForest | #6 | #5 | ↓ -1 |
| **LinearBoost-K** | #8 | **#6** | ↓ -2 |
| **LinearBoost-L** | #5 | **#7** | ↑ +2 |
| **LinearBoost-K-exact** | #7 | **#8** | ↑ +1 |
| TabPFN | #9 | #9 | → 0 |

**Key Changes:**
- LinearBoost-L and K-exact became slower
- LinearBoost-K became faster (only positive change)

---

## 🔍 **Analysis & Interpretation**

### **Why the Regression?**

The margin-based updates appear to have **hurt performance** rather than helped. Possible reasons:

1. **Too Conservative Updates**: The 60% reduction in weight updates for hard examples may be too conservative, preventing the algorithm from learning from difficult cases.

2. **Margin Threshold Too Low**: The 0.15 threshold for "hard examples" may be categorizing too many examples as hard, reducing the learning signal.

3. **Interaction with Class-Imbalance**: The combination of margin-based and class-imbalance updates may be conflicting rather than synergistic.

4. **Implementation Issue**: There may be a bug in the margin calculation or weight update logic.

### **What Worked Before**

The previous implementation (before margin-based updates) had:
- **LinearBoost-K-exact ranked #1 for F1** - This is a significant achievement
- Good balance between performance and speed
- Stable rankings across datasets

---

## 📋 **Recommendations**

### **Option 1: Revert Margin-Based Updates** ⚠️ (RECOMMENDED)

**Rationale:**
- Clear performance regression across all variants
- LinearBoost-K-exact lost its #1 F1 ranking
- Training and inference times increased
- The previous implementation was working well

**Action**: Remove margin-based updates, keep class-imbalance aware updates.

### **Option 2: Tune Margin-Based Parameters**

If keeping margin-based updates:
1. Increase margin threshold from 0.15 to 0.20-0.25 (fewer examples marked as hard)
2. Increase hard example update strength from 0.6 to 0.8 (less conservative)
3. Test incrementally to find optimal parameters

### **Option 3: Investigate Implementation**

Check for potential bugs:
1. Verify margin calculation is correct
2. Ensure weight updates are being applied correctly
3. Check if margin-based logic is interfering with class-imbalance logic

---

## 📈 **Impact Summary**

| Metric | LinearBoost-K-exact | LinearBoost-L | LinearBoost-K |
|--------|---------------------|---------------|---------------|
| **F1 Ranking Change** | ↓ -6 (#1→#7) | ↓ -1 (#7→#8) | → 0 (#9→#9) |
| **F1 Mean Δ** | -0.0209 | -0.0372 | -0.0388 |
| **ROC-AUC Ranking** | ↓ -1 (#6→#7) | → 0 (#8→#8) | → 0 (#9→#9) |
| **Training Time** | ↑ +4 positions | ↑ +2 positions | → 0 |
| **Inference Time** | ↑ +1 position | ↑ +2 positions | ↓ -2 positions |

**Overall Verdict**: **Significant performance regression** - Margin-based updates should be **reverted**.

---

## ✅ **Next Steps**

1. **IMMEDIATE**: Revert margin-based updates to restore previous performance
2. **Investigate**: Review margin-based implementation for potential bugs
3. **Alternative**: If keeping margin-based, test with adjusted parameters (threshold 0.25, strength 0.8)
4. **Focus**: Continue with other improvements (confidence-based weighting, ensemble pruning) that don't affect core boosting logic

---

**Conclusion**: The margin-based sample weight updates have caused a **significant performance regression** across all LinearBoost variants, particularly for LinearBoost-K-exact which lost its #1 F1 ranking. **Recommendation: REVERT** the margin-based updates and return to the previous implementation.
