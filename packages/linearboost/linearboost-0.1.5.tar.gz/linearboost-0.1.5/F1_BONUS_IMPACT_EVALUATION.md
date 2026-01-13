# F1 Bonus Strengthening (0.6 → 0.8): Impact Evaluation

**Date**: December 29, 2024  
**Change**: F1 bonus multiplier increased from 0.6 to 0.8  
**Datasets Compared**: 7 UCI datasets  
**Comparison**: Most recent (after change) vs. Second most recent (before change)

---

## ⚠️ **CRITICAL FINDING: Mixed Results with Negative Impact on Best Performer**

The strengthened F1 bonus (0.6 → 0.8) had **mixed results**, but **significantly hurt LinearBoost-K-exact**, which was previously ranked #1 for F1.

---

## 📊 **Detailed Performance Changes**

### **LinearBoost-K-exact** ⚠️ **MAJOR CONCERN**

**Previous State**: Ranked #1 for F1

**Performance Changes:**
- **F1 Score**: -0.0079 ± 0.0098 (6 regressions, 1 improvement)
- **ROC-AUC**: -0.0121 ± 0.0249 (4 regressions, 2 improvements)
- **Training Time**: +0.0431 seconds (slower)
- **Inference Time**: +0.6072 ms (slower)

**Ranking Changes:**
- **F1**: #1 → **#6** (↓ -5 positions) ⚠️ **SIGNIFICANT REGRESSION**
- **ROC-AUC**: #6 → #8 (↓ -2 positions)
- **Training Time**: #4 → #6 (↓ -2 positions)
- **Inference Time**: #7 → #8 (↓ -1 position)

**Verdict**: **Significant performance regression** - Lost #1 F1 ranking

**Per-Dataset Breakdown:**
| Dataset | F1 Δ | ROC-AUC Δ |
|---------|------|-----------|
| Breast Cancer Wisconsin | -0.0075 | +0.0110 |
| Banknote Authentication | -0.0043 | -0.0004 |
| Chronic Kidney Disease | -0.0030 | -0.0023 |
| Haberman's Survival | -0.0031 | +0.0072 |
| Heart Disease | **-0.0213** | **-0.0227** |
| Hepatitis | +0.0067 | -0.0677 |
| Ionosphere | **-0.0227** | -0.0101 |

**Key Insight**: 6 out of 7 datasets regressed in F1, with Heart Disease and Ionosphere showing significant regressions (-0.0213 and -0.0227).

---

### **LinearBoost-L**

**Performance Changes:**
- **F1 Score**: -0.0004 ± 0.0052 (essentially neutral)
- **ROC-AUC**: -0.0113 ± 0.0259 (3 regressions, 1 improvement)
- **Training Time**: -0.0550 seconds (faster) ✅
- **Inference Time**: -2.0274 ms (faster) ✅

**Ranking Changes:**
- **F1**: #7 → #8 (↓ -1 position)
- **ROC-AUC**: #8 → #9 (↓ -1 position)
- **Training Time**: #3 → #2 (↑ +1 position) ✅
- **Inference Time**: #5 → #5 (→ no change)

**Verdict**: **Neutral to slightly negative** - Minimal F1 change but rankings dropped

---

### **LinearBoost-K**

**Performance Changes:**
- **F1 Score**: +0.0140 ± 0.0523 (high variance, 3 improvements, 4 regressions)
- **ROC-AUC**: +0.0081 ± 0.0471 (3 improvements, 2 regressions)
- **Training Time**: -0.0488 seconds (faster) ✅
- **Inference Time**: -2.5391 ms (faster) ✅

**Ranking Changes:**
- **F1**: #9 → #7 (↑ +2 positions) ✅
- **ROC-AUC**: #9 → #7 (↑ +2 positions) ✅
- **Training Time**: #6 → #4 (↑ +2 positions) ✅
- **Inference Time**: #8 → #6 (↑ +2 positions) ✅

**Verdict**: **Positive** - Improved from worst position, but high variance suggests instability

**Notable**: Large improvement on Haberman's Survival (+0.1378 F1) but regression on Breast Cancer (-0.0382 F1)

---

## 🏆 **Overall Algorithm Rankings (F1)**

| Algorithm | Previous | Current | Change |
|-----------|----------|---------|--------|
| **CatBoost** | #2 | **#1** | ↑ -1 |
| **LightGBM** | #4 | **#2** | ↑ -2 |
| RandomForest | #3 | #3 | → 0 |
| LogisticRegression | #5 | #4 | ↑ -1 |
| XGBoost | #6 | #5 | ↑ -1 |
| **LinearBoost-K-exact** | **#1** | **#6** | ↓ +5 ⚠️ |
| **LinearBoost-L** | #7 | #8 | ↓ +1 |
| **LinearBoost-K** | #9 | #7 | ↑ -2 |
| TabPFN | #8 | #9 | ↓ +1 |

**Key Changes:**
- LinearBoost-K-exact dropped from **#1 to #6** (worst regression)
- CatBoost took over #1 spot
- LinearBoost-K improved from #9 to #7 (was already worst)
- All LinearBoost variants still in bottom half (#6, #7, #8)

---

## 📈 **Overall Assessment**

### **Combined Metrics (All LinearBoost Variants):**
- **F1 Score**: +0.0019 ± 0.0322 (essentially neutral)
- **ROC-AUC**: -0.0051 ± 0.0355 (slight regression)
- **Total F1 Improvements**: 7 datasets
- **Total F1 Regressions**: 12 datasets

### **Statistical Significance:**
- LinearBoost-K-exact: p=0.1094 (not significant, but 6/7 datasets regressed)
- LinearBoost-L: p=0.9375 (not significant, neutral)
- LinearBoost-K: p=1.0000 (not significant, high variance)

---

## ⚠️ **Critical Analysis**

### **Why LinearBoost-K-exact Regressed:**

The strengthened F1 bonus (0.8) appears to be **too aggressive** for LinearBoost-K-exact:
1. **Over-weighting**: Higher F1 bonus may be over-weighting estimators, causing instability
2. **Parameter sensitivity**: LinearBoost-K-exact may be more sensitive to estimator weight changes
3. **Diminishing returns**: The previous 0.6 multiplier may have been optimal for this variant

### **Why LinearBoost-K Improved:**

LinearBoost-K benefited, but this may be because:
1. **Starting from worst position**: Had more room to improve
2. **Different algorithm characteristics**: May respond better to stronger F1 signal
3. **High variance**: The improvement (+0.0140) has high variance (±0.0523), suggesting instability

---

## 🎯 **RECOMMENDATION: REVERT** ❌

### **Primary Reason:**
**LinearBoost-K-exact dropped from #1 to #6 in F1 rankings** - This is unacceptable. We should not sacrifice the performance of our best variant to marginally improve the worst one.

### **Supporting Reasons:**

1. **Net Negative Impact**: 
   - 12 regressions vs 7 improvements across all variants
   - LinearBoost-K-exact (best performer) hurt significantly
   - LinearBoost-L (middle performer) neutral to slightly negative

2. **Ranking Degradation**:
   - LinearBoost-K-exact: #1 → #6 (lost leadership position)
   - LinearBoost-L: #7 → #8 (further from top)
   - Only LinearBoost-K improved, but from worst position (#9 → #7)

3. **ROC-AUC Trade-off**:
   - Combined ROC-AUC decreased by -0.0051
   - LinearBoost-K-exact and LinearBoost-L both regressed in ROC-AUC

4. **Unclear Benefit**:
   - Overall F1 improvement is minimal (+0.0019) and within noise
   - Statistical tests not significant
   - High variance in results

---

## 📋 **Alternative Recommendations**

### **Option 1: REVERT to 0.6** (RECOMMENDED)
**Rationale**: Restore LinearBoost-K-exact to #1 ranking

**Action**: Change multiplier back to 0.6

**Expected**: LinearBoost-K-exact returns to #1 F1 ranking

---

### **Option 2: Variant-Specific Multipliers**
**Rationale**: Different variants may need different F1 bonus strengths

**Implementation**:
- LinearBoost-K-exact: Keep at 0.6 (was optimal)
- LinearBoost-L: Try 0.7 (moderate increase)
- LinearBoost-K: Keep at 0.8 (seems to benefit)

**Complexity**: Medium (requires conditional logic per variant)

**Expected**: Optimize each variant independently

---

### **Option 3: Adaptive F1 Bonus**
**Rationale**: Adjust F1 bonus based on dataset characteristics or training progress

**Implementation**: Dynamic multiplier based on:
- Iteration number (start high, decrease over time)
- Dataset imbalance ratio
- Current ensemble performance

**Complexity**: High

**Expected**: Better adaptation to different scenarios

---

## ✅ **Final Recommendation**

### **REVERT the F1 bonus multiplier from 0.8 back to 0.6** ❌

**Primary Justification**:
- LinearBoost-K-exact lost its #1 F1 ranking (#1 → #6)
- This is the primary goal violation - we should not hurt our best performer
- The improvement for LinearBoost-K is not worth the cost

**Secondary Justification**:
- Overall impact is minimal (+0.0019 F1)
- More regressions (12) than improvements (7)
- Statistical tests not significant
- ROC-AUC also regressed

**Action Items**:
1. Revert multiplier to 0.6 in both SAMME.R and SAMME algorithms
2. Run benchmarks to verify restoration of LinearBoost-K-exact #1 ranking
3. Consider variant-specific multipliers if we want to optimize LinearBoost-K independently

---

## 📊 **Summary Table**

| Metric | LinearBoost-K-exact | LinearBoost-L | LinearBoost-K | Overall |
|--------|---------------------|---------------|---------------|---------|
| **F1 Mean Δ** | -0.0079 ⚠️ | -0.0004 | +0.0140 | +0.0019 |
| **F1 Ranking** | #1→#6 ⚠️ | #7→#8 | #9→#7 ✅ | - |
| **ROC-AUC Δ** | -0.0121 | -0.0113 | +0.0081 | -0.0051 |
| **Regressions** | 6/7 ⚠️ | 2/7 | 4/7 | 12/21 |
| **Improvements** | 1/7 | 3/7 | 3/7 | 7/21 |
| **Verdict** | ❌ Revert | ➡️ Neutral | ✅ Keep | ❌ Revert |

---

**Conclusion**: The strengthened F1 bonus (0.8) **hurt our best performer** (LinearBoost-K-exact) significantly, causing it to drop from #1 to #6. The marginal improvement for LinearBoost-K does not justify this cost. **Recommendation: REVERT to 0.6**.
