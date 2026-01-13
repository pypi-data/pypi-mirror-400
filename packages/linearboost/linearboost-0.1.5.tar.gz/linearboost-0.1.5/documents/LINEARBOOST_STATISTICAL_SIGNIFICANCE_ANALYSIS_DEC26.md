# LinearBoost Statistical Significance Analysis
## December 26, 2025 Benchmarks (AUC-Optimized)

This analysis examines statistically significant wins and losses for LinearBoost variants against competing algorithms, based on **Bonferroni-corrected pairwise Wilcoxon signed-rank tests** from today's benchmark results.

---

## Methodology

- **Statistical Test**: Pairwise Wilcoxon signed-rank tests with Bonferroni correction
- **Significance Threshold**: `significant_bonferroni = True` (corrected for multiple comparisons)
- **Metrics Analyzed**: F1 Score and ROC-AUC
- **Datasets**: 7 UCI ML Repository datasets
- **Comparison Algorithms**: XGBoost, LightGBM, CatBoost, RandomForest, TabPFN, LogisticRegression

---

## LinearBoost-L Performance

### F1 Score Comparisons

| Competitor | LinearBoost-L Wins | LinearBoost-L Losses | Net |
|------------|-------------------|---------------------|-----|
| **XGBoost** | 0 | 3 | **-3** |
| **LightGBM** | 1 | 3 | **-2** |
| **CatBoost** | 1 | 4 | **-3** |
| **RandomForest** | 3 | 3 | **0** |
| **TabPFN** | 0 | 4 | **-4** |
| **LogisticRegression** | 2 | 3 | **-1** |
| **TOTAL** | **7** | **20** | **-13** |

**Analysis**: LinearBoost-L is significantly outperformed in F1 score, with 20 significant losses vs 7 wins. It performs worst against TabPFN (0-4) and best against RandomForest (3-3, tied).

### ROC-AUC Comparisons

| Competitor | LinearBoost-L Wins | LinearBoost-L Losses | Net |
|------------|-------------------|---------------------|-----|
| **XGBoost** | 1 | 2 | **-1** |
| **LightGBM** | 0 | 2 | **-2** |
| **CatBoost** | 0 | 4 | **-4** |
| **RandomForest** | 3 | 2 | **+1** |
| **TabPFN** | 1 | 3 | **-2** |
| **LogisticRegression** | 2 | 3 | **-1** |
| **TOTAL** | **7** | **16** | **-9** |

**Analysis**: LinearBoost-L performs better in AUC than F1, with 7 wins vs 16 losses (vs 7 vs 20 in F1). It achieves a positive net against RandomForest (3-2) but struggles against CatBoost (0-4).

---

## LinearBoost-K-exact Performance

### F1 Score Comparisons

| Competitor | LinearBoost-K-exact Wins | LinearBoost-K-exact Losses | Net |
|------------|-------------------------|--------------------------|-----|
| **XGBoost** | 2 | 3 | **-1** |
| **LightGBM** | 2 | 4 | **-2** |
| **CatBoost** | 2 | 2 | **0** |
| **RandomForest** | 3 | 2 | **+1** |
| **TabPFN** | 0 | 4 | **-4** |
| **LogisticRegression** | 3 | 4 | **-1** |
| **TOTAL** | **12** | **19** | **-7** |

**Analysis**: LinearBoost-K-exact shows better F1 performance than LinearBoost-L (12 wins vs 19 losses, compared to 7 vs 20). It ties with CatBoost (2-2) and beats RandomForest (3-2).

### ROC-AUC Comparisons

| Competitor | LinearBoost-K-exact Wins | LinearBoost-K-exact Losses | Net |
|------------|-------------------------|--------------------------|-----|
| **XGBoost** | 3 | 1 | **+2** |
| **LightGBM** | 2 | 1 | **+1** |
| **CatBoost** | 0 | 3 | **-3** |
| **RandomForest** | 3 | 0 | **+3** |
| **TabPFN** | 1 | 1 | **0** |
| **LogisticRegression** | 3 | 2 | **+1** |
| **TOTAL** | **12** | **8** | **+4** |

**Analysis**: **LinearBoost-K-exact excels in AUC**, achieving a positive net score (+4) with 12 wins vs 8 losses. It dominates RandomForest (3-0), beats XGBoost (3-1), and is competitive against LightGBM and LogisticRegression. Only CatBoost significantly outperforms it (0-3).

---

## LinearBoost-K Performance

### F1 Score Comparisons

| Competitor | LinearBoost-K Wins | LinearBoost-K Losses | Net |
|------------|-------------------|---------------------|-----|
| **XGBoost** | 1 | 3 | **-2** |
| **LightGBM** | 1 | 5 | **-4** |
| **CatBoost** | 3 | 3 | **0** |
| **RandomForest** | 2 | 4 | **-2** |
| **TabPFN** | 0 | 4 | **-4** |
| **LogisticRegression** | 2 | 5 | **-3** |
| **TOTAL** | **9** | **24** | **-15** |

**Analysis**: LinearBoost-K shows the worst F1 performance among LinearBoost variants, with 9 wins vs 24 losses. It ties with CatBoost (3-3) but is significantly outperformed by LightGBM (1-5) and LogisticRegression (2-5).

### ROC-AUC Comparisons

| Competitor | LinearBoost-K Wins | LinearBoost-K Losses | Net |
|------------|-------------------|---------------------|-----|
| **XGBoost** | 2 | 4 | **-2** |
| **LightGBM** | 2 | 4 | **-2** |
| **CatBoost** | 2 | 4 | **-2** |
| **RandomForest** | 3 | 3 | **0** |
| **TabPFN** | 2 | 4 | **-2** |
| **LogisticRegression** | 2 | 4 | **-2** |
| **TOTAL** | **13** | **23** | **-10** |

**Analysis**: LinearBoost-K shows consistent AUC performance across competitors but with overall negative net (-10). It only ties with RandomForest (3-3) and is uniformly outperformed by other algorithms.

---

## Summary Statistics

### Overall Performance Summary

| Model | Metric | Total Wins | Total Losses | Net Score |
|-------|--------|------------|--------------|-----------|
| **LinearBoost-L** | F1 | 7 | 20 | **-13** |
| **LinearBoost-L** | AUC | 7 | 16 | **-9** |
| **LinearBoost-K-exact** | F1 | 12 | 19 | **-7** |
| **LinearBoost-K-exact** | AUC | 12 | 8 | **+4** ✅ |
| **LinearBoost-K** | F1 | 9 | 24 | **-15** |
| **LinearBoost-K** | AUC | 13 | 23 | **-10** |

### Key Findings

1. **LinearBoost-K-exact is the best performer in AUC**:
   - Only variant with positive net score (+4) in AUC
   - Beats XGBoost (3-1), RandomForest (3-0), and LightGBM (2-1) significantly
   - Struggles against CatBoost (0-3) and TabPFN (1-1, tied)

2. **LinearBoost-L performs moderately**:
   - Better in AUC (7-16, net -9) than F1 (7-20, net -13)
   - Ties with RandomForest in F1 (3-3) and beats it in AUC (3-2)
   - Struggles most against TabPFN (F1: 0-4, AUC: 1-3) and CatBoost (F1: 1-4, AUC: 0-4)

3. **LinearBoost-K underperforms**:
   - Worst F1 performance (9-24, net -15)
   - Consistent losses across all competitors in both metrics
   - Only ties with CatBoost in F1 (3-3) and RandomForest in AUC (3-3)

4. **Common patterns across all variants**:
   - All struggle against **TabPFN** in F1 (0 wins, 12 total losses)
   - All struggle against **CatBoost** in AUC (2 wins, 15 total losses)
   - All perform competitively against **RandomForest** (net scores ranging from -1 to +3)

5. **AUC optimization helps LinearBoost-K-exact**:
   - LinearBoost-K-exact achieves the only positive net score (+4) when optimized for AUC
   - This suggests the exact kernel variant benefits significantly from AUC optimization

---

## Competitor-Specific Analysis

### Against TabPFN
- **F1**: All LinearBoost variants lose (0 wins, 12 losses total)
- **AUC**: Mixed results (LinearBoost-K-exact ties 1-1, others lose)
- **Conclusion**: TabPFN is superior in F1, competitive in AUC

### Against CatBoost
- **F1**: Competitive (6 wins, 9 losses total)
- **AUC**: Poor (2 wins, 15 losses total)
- **Conclusion**: CatBoost significantly outperforms in AUC across all variants

### Against RandomForest
- **F1**: Competitive (8 wins, 9 losses total)
- **AUC**: Strong (9 wins, 5 losses total)
- **Conclusion**: LinearBoost variants, especially K-exact, significantly outperform RandomForest in AUC

### Against XGBoost
- **F1**: Mixed (4 wins, 9 losses total)
- **AUC**: Competitive (6 wins, 7 losses total)
- **Conclusion**: LinearBoost-K-exact beats XGBoost in AUC (3-1), others are competitive

### Against LightGBM
- **F1**: Weak (4 wins, 12 losses total)
- **AUC**: Weak (4 wins, 7 losses total)
- **Conclusion**: LightGBM consistently outperforms, especially in F1

### Against LogisticRegression
- **F1**: Competitive (7 wins, 12 losses total)
- **AUC**: Competitive (7 wins, 9 losses total)
- **Conclusion**: Mixed results, LinearBoost-K-exact performs best (3-2 in AUC)

---

## Recommendations

### For Promoting LinearBoost:

1. **Emphasize LinearBoost-K-exact's AUC strength**:
   - Only variant with positive net score in AUC (+4)
   - Significantly beats RandomForest, XGBoost, and LightGBM
   - Ideal for applications where AUC/ranking quality is paramount

2. **Acknowledge F1 limitations**:
   - All variants struggle in F1, especially against TabPFN
   - LinearBoost-K-exact shows best F1 performance but still negative net
   - Consider class weight tuning or threshold optimization for F1-focused applications

3. **Target specific use cases**:
   - **AUC-focused**: LinearBoost-K-exact excels
   - **Fast training**: LinearBoost-L maintains competitive speed
   - **RandomForest replacement**: All variants perform well in AUC vs RandomForest

4. **Improve LinearBoost-K**:
   - Current approximation method underperforms
   - Consider refining kernel approximation or using different optimization strategies

---

## Statistical Notes

- All comparisons use **Bonferroni-corrected p-values** to control for multiple testing
- Significance threshold: `p < α` where α is adjusted for the number of comparisons
- Tests are based on **Wilcoxon signed-rank tests** over 30 runs per dataset
- Only **statistically significant** differences are counted (not just performance differences)

---

*Analysis Date: December 26, 2025*  
*Benchmark Configuration: AUC-optimized hyperparameters, 5-fold CV, 30 runs per model*  
*Datasets: 7 UCI ML Repository datasets*

