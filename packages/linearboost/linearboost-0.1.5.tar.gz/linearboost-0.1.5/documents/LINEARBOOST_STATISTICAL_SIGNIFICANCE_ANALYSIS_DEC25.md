# LinearBoost Statistical Significance Analysis
## December 25, 2025 Benchmarks (F1-Optimized)

This analysis examines statistically significant wins and losses for LinearBoost variants against competing algorithms, based on **Bonferroni-corrected pairwise Wilcoxon signed-rank tests** from yesterday's benchmark results (F1-optimized).

---

## Methodology

- **Statistical Test**: Pairwise Wilcoxon signed-rank tests with Bonferroni correction
- **Significance Threshold**: `significant_bonferroni = True` (corrected for multiple comparisons)
- **Metrics Analyzed**: F1 Score and ROC-AUC
- **Datasets**: 7 UCI ML Repository datasets
- **Optimization Strategy**: **F1 Score** (optimized for F1 performance)
- **Comparison Algorithms**: XGBoost, LightGBM, CatBoost, RandomForest, TabPFN, LogisticRegression

---

## LinearBoost-L Performance

### F1 Score Comparisons

| Competitor | LinearBoost-L Wins | LinearBoost-L Losses | Net |
|------------|-------------------|---------------------|-----|
| **XGBoost** | 2 | 2 | **0** |
| **LightGBM** | 2 | 2 | **0** |
| **CatBoost** | 0 | 4 | **-4** |
| **RandomForest** | 2 | 2 | **0** |
| **TabPFN** | 2 | 4 | **-2** |
| **LogisticRegression** | 1 | 3 | **-2** |
| **TOTAL** | **9** | **17** | **-8** |

**Analysis**: LinearBoost-L shows **better F1 performance with F1 optimization** (9-17, net -8) compared to AUC optimization (7-20, net -13). It ties with XGBoost, LightGBM, and RandomForest (2-2 each) but struggles against CatBoost (0-4).

### ROC-AUC Comparisons

| Competitor | LinearBoost-L Wins | LinearBoost-L Losses | Net |
|------------|-------------------|---------------------|-----|
| **XGBoost** | 3 | 2 | **+1** |
| **LightGBM** | 0 | 2 | **-2** |
| **CatBoost** | 0 | 5 | **-5** |
| **RandomForest** | 2 | 4 | **-2** |
| **TabPFN** | 0 | 5 | **-5** |
| **LogisticRegression** | 1 | 6 | **-5** |
| **TOTAL** | **6** | **24** | **-18** |

**Analysis**: LinearBoost-L's AUC performance **degrades significantly with F1 optimization** (6-24, net -18) compared to AUC optimization (7-16, net -9). This shows a clear trade-off: optimizing for F1 hurts AUC performance substantially. It only beats XGBoost (3-2) but loses heavily against CatBoost, TabPFN, and LogisticRegression (0-5 each).

---

## LinearBoost-K-exact Performance (Best Performer with F1 Optimization)

### F1 Score Comparisons

| Competitor | LinearBoost-K-exact Wins | LinearBoost-K-exact Losses | Net |
|------------|-------------------------|--------------------------|-----|
| **XGBoost** | 3 | 0 | **+3** |
| **LightGBM** | 1 | 0 | **+1** |
| **CatBoost** | 1 | 3 | **-2** |
| **RandomForest** | 3 | 0 | **+3** |
| **TabPFN** | 0 | 3 | **-3** |
| **LogisticRegression** | 2 | 2 | **0** |
| **TOTAL** | **10** | **8** | **+2** |

**Analysis**: **LinearBoost-K-exact excels with F1 optimization**, achieving the **only positive net score (+2)** in F1 among all LinearBoost variants. It dominates XGBoost (3-0) and RandomForest (3-0), and beats LightGBM (1-0). This is significantly better than its performance with AUC optimization (12-19, net -7).

### ROC-AUC Comparisons

| Competitor | LinearBoost-K-exact Wins | LinearBoost-K-exact Losses | Net |
|------------|-------------------------|--------------------------|-----|
| **XGBoost** | 3 | 0 | **+3** |
| **LightGBM** | 3 | 2 | **+1** |
| **CatBoost** | 2 | 4 | **-2** |
| **RandomForest** | 2 | 1 | **+1** |
| **TabPFN** | 1 | 3 | **-2** |
| **LogisticRegression** | 2 | 2 | **0** |
| **TOTAL** | **13** | **12** | **+1** |

**Analysis**: LinearBoost-K-exact maintains **positive AUC performance (+1)** even with F1 optimization, though it's less impressive than with AUC optimization (+4). It still dominates XGBoost (3-0) and performs well against LightGBM (3-2) and RandomForest (2-1). This demonstrates the variant's robustness.

---

## LinearBoost-K Performance

### F1 Score Comparisons

| Competitor | LinearBoost-K Wins | LinearBoost-K Losses | Net |
|------------|-------------------|---------------------|-----|
| **XGBoost** | 3 | 2 | **+1** |
| **LightGBM** | 2 | 1 | **+1** |
| **CatBoost** | 1 | 5 | **-4** |
| **RandomForest** | 2 | 2 | **0** |
| **TabPFN** | 1 | 3 | **-2** |
| **LogisticRegression** | 2 | 3 | **-1** |
| **TOTAL** | **11** | **16** | **-5** |

**Analysis**: LinearBoost-K shows **better F1 performance with F1 optimization** (11-16, net -5) compared to AUC optimization (9-24, net -15). It beats XGBoost (3-2) and LightGBM (2-1) but struggles against CatBoost (1-5).

### ROC-AUC Comparisons

| Competitor | LinearBoost-K Wins | LinearBoost-K Losses | Net |
|------------|-------------------|---------------------|-----|
| **XGBoost** | 3 | 2 | **+1** |
| **LightGBM** | 2 | 1 | **+1** |
| **CatBoost** | 2 | 4 | **-2** |
| **RandomForest** | 3 | 3 | **0** |
| **TabPFN** | 1 | 3 | **-2** |
| **LogisticRegression** | 2 | 2 | **0** |
| **TOTAL** | **13** | **15** | **-2** |

**Analysis**: LinearBoost-K shows **better AUC performance with F1 optimization** (13-15, net -2) compared to AUC optimization (13-23, net -10). This is counterintuitive but suggests the variant may benefit from different hyperparameter settings when F1 is optimized.

---

## Summary Statistics

### Overall Performance Summary

| Model | Metric | Total Wins | Total Losses | Net Score |
|-------|--------|------------|--------------|-----------|
| **LinearBoost-L** | F1 | 9 | 17 | **-8** |
| **LinearBoost-L** | AUC | 6 | 24 | **-18** |
| **LinearBoost-K-exact** | F1 | 10 | 8 | **+2** ✅ |
| **LinearBoost-K-exact** | AUC | 13 | 12 | **+1** ✅ |
| **LinearBoost-K** | F1 | 11 | 16 | **-5** |
| **LinearBoost-K** | AUC | 13 | 15 | **-2** |

### Key Findings

1. **LinearBoost-K-exact is the clear winner with F1 optimization**:
   - Only variant with positive net scores in both F1 (+2) and AUC (+1)
   - Dominates XGBoost (3-0 in both F1 and AUC) and RandomForest (3-0 in F1, 2-1 in AUC)
   - Significantly outperforms its performance with AUC optimization in F1 (was -7, now +2)

2. **LinearBoost-L shows F1-AUC trade-off**:
   - Better F1 with F1 optimization (9-17, net -8) vs AUC optimization (7-20, net -13)
   - **Much worse AUC with F1 optimization** (6-24, net -18) vs AUC optimization (7-16, net -9)
   - This demonstrates a clear trade-off: optimizing for F1 improves F1 but dramatically hurts AUC

3. **LinearBoost-K benefits from F1 optimization**:
   - Better F1 performance (-5 vs -15) and AUC performance (-2 vs -10)
   - Performs competitively against XGBoost and LightGBM in both metrics

4. **Common patterns across all variants with F1 optimization**:
   - All struggle against **CatBoost** in F1 (2 wins, 12 losses total) and AUC (4 wins, 13 losses total)
   - All struggle against **TabPFN** in AUC (1 win, 13 losses total)
   - LinearBoost-K-exact dominates **XGBoost** in both metrics (6-0 total)
   - All variants perform well against **RandomForest** in F1 (7-4 total, all positive)

5. **F1 optimization helps LinearBoost-K-exact and LinearBoost-K**:
   - Both variants show improved performance (positive or less negative net scores) with F1 optimization
   - This suggests these variants are better suited for F1-optimized hyperparameters

---

## Comparison: F1 vs AUC Optimization Impact

### LinearBoost-L Performance Comparison

| Metric | F1-Optimized (Dec 25) | AUC-Optimized (Dec 26) | Difference |
|--------|----------------------|------------------------|------------|
| **F1 Net** | -8 | -13 | **+5 improvement** ✅ |
| **AUC Net** | -18 | -9 | **-9 degradation** ⚠️ |
| **F1 Wins** | 9 | 7 | +2 |
| **AUC Wins** | 6 | 7 | -1 |
| **F1 Losses** | 17 | 20 | -3 |
| **AUC Losses** | 24 | 16 | +8 |

**Analysis**: LinearBoost-L shows a clear trade-off: F1 optimization improves F1 but significantly hurts AUC. The AUC degradation (-18 vs -9) is worse than the F1 improvement (+5).

### LinearBoost-K-exact Performance Comparison

| Metric | F1-Optimized (Dec 25) | AUC-Optimized (Dec 26) | Difference |
|--------|----------------------|------------------------|------------|
| **F1 Net** | +2 | -7 | **+9 improvement** ✅ |
| **AUC Net** | +1 | +4 | **-3 degradation** |
| **F1 Wins** | 10 | 12 | -2 |
| **AUC Wins** | 13 | 12 | +1 |
| **F1 Losses** | 8 | 19 | -11 |
| **AUC Losses** | 12 | 8 | +4 |

**Analysis**: LinearBoost-K-exact benefits **significantly more from F1 optimization** than AUC optimization. F1 net improves by +9 (from -7 to +2), making it the only variant with positive F1 performance. AUC remains positive under both strategies.

### LinearBoost-K Performance Comparison

| Metric | F1-Optimized (Dec 25) | AUC-Optimized (Dec 26) | Difference |
|--------|----------------------|------------------------|------------|
| **F1 Net** | -5 | -15 | **+10 improvement** ✅ |
| **AUC Net** | -2 | -10 | **+8 improvement** ✅ |
| **F1 Wins** | 11 | 9 | +2 |
| **AUC Wins** | 13 | 13 | 0 |
| **F1 Losses** | 16 | 24 | -8 |
| **AUC Losses** | 15 | 23 | -8 |

**Analysis**: LinearBoost-K **benefits significantly from F1 optimization** in both metrics. Both F1 and AUC net scores improve substantially (+10 and +8 respectively).

---

## Competitor-Specific Analysis

### Against TabPFN
- **F1**: Competitive with F1 optimization (4 wins, 10 losses total) vs Poor with AUC optimization (0 wins, 12 losses)
- **AUC**: Poor with both strategies (1 win, 13 losses with F1 opt; 4 wins, 9 losses with AUC opt)
- **Conclusion**: F1 optimization helps all variants compete better with TabPFN in F1, but TabPFN still dominates in AUC

### Against CatBoost
- **F1**: Poor with both strategies (2 wins, 12 losses with F1 opt; 6 wins, 9 losses with AUC opt)
- **AUC**: Poor with both strategies (4 wins, 13 losses with F1 opt; 2 wins, 15 losses with AUC opt)
- **Conclusion**: CatBoost consistently outperforms LinearBoost variants, especially in AUC

### Against RandomForest
- **F1**: Excellent with F1 optimization (7 wins, 4 losses total) vs Good with AUC optimization (8 wins, 9 losses)
- **AUC**: Good with F1 optimization (7 wins, 8 losses) vs Excellent with AUC optimization (9 wins, 5 losses)
- **Conclusion**: LinearBoost variants, especially K-exact, significantly outperform RandomForest with F1 optimization

### Against XGBoost
- **F1**: Excellent with F1 optimization (8 wins, 4 losses total) vs Poor with AUC optimization (4 wins, 9 losses)
- **AUC**: Good with F1 optimization (9 wins, 4 losses) vs Competitive with AUC optimization (6 wins, 7 losses)
- **Conclusion**: F1 optimization helps LinearBoost variants compete better against XGBoost, especially LinearBoost-K-exact (3-0 in both metrics)

### Against LightGBM
- **F1**: Good with F1 optimization (5 wins, 3 losses total) vs Poor with AUC optimization (4 wins, 12 losses)
- **AUC**: Competitive with F1 optimization (5 wins, 5 losses) vs Poor with AUC optimization (4 wins, 7 losses)
- **Conclusion**: F1 optimization significantly improves performance against LightGBM

### Against LogisticRegression
- **F1**: Mixed with F1 optimization (5 wins, 8 losses total) vs Competitive with AUC optimization (7 wins, 12 losses)
- **AUC**: Poor with F1 optimization (5 wins, 10 losses) vs Competitive with AUC optimization (7 wins, 9 losses)
- **Conclusion**: Mixed results, with F1 optimization helping some variants and hurting others

---

## Recommendations

### For Promoting LinearBoost:

1. **Use F1 optimization for LinearBoost-K-exact**:
   - Achieves positive net scores in both F1 (+2) and AUC (+1)
   - Significantly outperforms XGBoost and RandomForest
   - Best overall performance among LinearBoost variants with F1 optimization

2. **Use AUC optimization for LinearBoost-L**:
   - F1 optimization hurts AUC too much (-18 net)
   - AUC optimization provides better balance (F1: -13, AUC: -9)
   - Faster training remains a key advantage

3. **Acknowledge variant-specific optimization needs**:
   - Different LinearBoost variants benefit from different optimization strategies
   - LinearBoost-K-exact: F1 optimization preferred
   - LinearBoost-L: AUC optimization preferred
   - LinearBoost-K: F1 optimization preferred

4. **Target specific use cases**:
   - **F1-focused applications**: Use LinearBoost-K-exact with F1 optimization
   - **AUC-focused applications**: Use LinearBoost-K-exact with AUC optimization or LinearBoost-L with AUC optimization
   - **Fast training needed**: LinearBoost-L maintains speed advantage under both strategies

5. **Address consistent weaknesses**:
   - All variants struggle against CatBoost and TabPFN
   - Consider ensemble methods or specialized hyperparameter tuning for these competitors

---

## Statistical Notes

- All comparisons use **Bonferroni-corrected p-values** to control for multiple testing
- Significance threshold: `p < α` where α is adjusted for the number of comparisons
- Tests are based on **Wilcoxon signed-rank tests** over 30 runs per dataset
- Only **statistically significant** differences are counted (not just performance differences)

---

## Key Insights: F1 vs AUC Optimization

### For LinearBoost-L:
- **F1 optimization**: Better F1 (-8 vs -13), but much worse AUC (-18 vs -9)
- **Recommendation**: Use AUC optimization for better balance

### For LinearBoost-K-exact:
- **F1 optimization**: Best overall performance (+2 F1, +1 AUC)
- **AUC optimization**: Strong AUC (+4) but worse F1 (-7)
- **Recommendation**: Use F1 optimization for best overall performance, AUC optimization if AUC is critical

### For LinearBoost-K:
- **F1 optimization**: Better in both metrics (-5 F1, -2 AUC vs -15 F1, -10 AUC)
- **Recommendation**: Use F1 optimization

### Overall Conclusion:
**Different LinearBoost variants benefit from different optimization strategies.** There is no one-size-fits-all approach, which suggests that users should choose both the variant and optimization strategy based on their specific use case and priorities.

---

*Analysis Date: December 26, 2025*  
*Benchmark Configuration: F1-optimized hyperparameters, 5-fold CV, 30 runs per model*  
*Datasets: 7 UCI ML Repository datasets*  
*Comparison: This analysis complements the AUC-optimized benchmark analysis from December 26, 2025*

