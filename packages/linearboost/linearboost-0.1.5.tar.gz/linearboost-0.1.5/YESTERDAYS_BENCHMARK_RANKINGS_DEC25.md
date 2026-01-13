# Yesterday's Benchmark Rankings Analysis (December 25, 2025)
## Algorithm Performance Comparison Based on F1-Optimized Benchmarks

---

## Executive Summary

This analysis compares algorithm performance across 7 UCI ML repository datasets using **F1-optimized hyperparameters**. Rankings are computed per-dataset for each metric, then aggregated across all datasets. This approach provides a more robust and statistically meaningful comparison than simple score averaging.

**Key Finding:** LinearBoost-L ranks **#6 overall** (out of 9 algorithms), with strong performance in **training time efficiency (rank #3)** but weaker AUC performance (rank #9). This highlights the trade-off between F1 and AUC optimization.

---

## Overall Rankings

### Overall Algorithm Ranking (Averaged Across All Metrics)

| Rank | Algorithm | Avg F1 Rank | Avg AUC Rank | Avg Train Time Rank | Avg Inf Time Rank | Overall Rank |
|------|-----------|-------------|--------------|---------------------|-------------------|--------------|
| **1** | **CatBoost** | 2.14 | 3.14 | 6.43 | 1.00 | **3.18** |
| **2** | **LogisticRegression** | 4.57 | 5.00 | 1.86 | 3.29 | **3.68** |
| **3** | **TabPFN** | 3.83 | 3.00 | 1.00 | 8.67 | **4.12** |
| **4** | **LightGBM** | 5.00 | 5.00 | 4.86 | 2.00 | **4.21** |
| **5** | **XGBoost** | 6.14 | 5.71 | 4.29 | 4.00 | **5.04** |
| **6** | **LinearBoost-L** | 5.43 | 6.71 | 4.29 | 4.86 | **5.32** |
| **7** | **LinearBoost-K-exact** | 4.17 | 4.83 | 7.17 | 7.17 | **5.83** |
| **8** | **RandomForest** | 6.00 | 4.57 | 6.43 | 6.57 | **5.89** |
| **9** | **LinearBoost-K** | 6.00 | 5.17 | 7.17 | 7.00 | **6.33** |

*Note: Lower rank values indicate better performance. Ranks are averaged across 7 datasets. These benchmarks were optimized for F1 score.*

---

## LinearBoost Models Performance

### LinearBoost-L (Best Performing LinearBoost Variant)

**Overall Rank: #6 out of 9**

| Metric | Rank Position | Average Rank | Performance Assessment |
|--------|--------------|--------------|------------------------|
| **F1 Score** | #6 | 5.43 | Average |
| **ROC-AUC** | #9 | 6.71 | **Below average** |
| **Training Time** | **#3** | 4.29 | **Excellent** |
| **Inference Time** | #5 | 4.86 | Average |

**Strengths:**
- **Excellent training speed**: Ranked #3, only behind TabPFN (zero training time) and LogisticRegression
- **Competitive F1 performance**: Ranked #6, close to top performers
- **Reasonable inference time**: Ranked #5, acceptable for most applications

**Weaknesses:**
- **Poor ROC-AUC performance**: Ranked #9 (last), indicating that F1 optimization may be sacrificing AUC performance
- **F1-AUC trade-off**: The optimization for F1 score appears to reduce the model's ability to discriminate classes (AUC)

### LinearBoost-K-exact

**Overall Rank: #7 out of 9**

| Metric | Rank Position | Average Rank | Performance Assessment |
|--------|--------------|--------------|------------------------|
| **F1 Score** | **#3** | 4.17 | **Above average** |
| **ROC-AUC** | #4 | 4.83 | Good |
| **Training Time** | #8 | 7.17 | Slow |
| **Inference Time** | #8 | 7.17 | Slow |

**Strengths:**
- **Strong F1 performance**: Ranked #3, the best among LinearBoost variants
- **Good ROC-AUC**: Ranked #4, better than LinearBoost-L
- **Balanced accuracy metrics**: Better balance between F1 and AUC than LinearBoost-L

**Weaknesses:**
- **Slow training**: Ranked #8, computational cost is high
- **Slow inference**: Ranked #8, not suitable for real-time applications

### LinearBoost-K

**Overall Rank: #9 out of 9 (Last Place)**

| Metric | Rank Position | Average Rank | Performance Assessment |
|--------|--------------|--------------|------------------------|
| **F1 Score** | #7 | 6.00 | Below average |
| **ROC-AUC** | #7 | 5.17 | Average |
| **Training Time** | #8 | 7.17 | Slow |
| **Inference Time** | #7 | 7.00 | Slow |

**Assessment:** LinearBoost-K (kernel approximation variant) performs the worst overall, suggesting that the approximation method needs significant improvement or that the F1 optimization strategy is not suitable for this variant.

---

## Per-Metric Rankings

### F1 Score Rankings (Optimization Target)

| Rank | Algorithm | Average F1 Rank |
|------|-----------|-----------------|
| 1 | CatBoost | 2.14 |
| 2 | TabPFN | 3.83 |
| 3 | LinearBoost-K-exact | 4.17 |
| 4 | LogisticRegression | 4.57 |
| 5 | LightGBM | 5.00 |
| 6 | LinearBoost-L | 5.43 |
| 7 | RandomForest | 6.00 |
| 7 | LinearBoost-K | 6.00 |
| 9 | XGBoost | 6.14 |

**LinearBoost-L Position: #6**  
**LinearBoost-K-exact Position: #3** ✅

*Note: Despite optimizing for F1, LinearBoost-L ranks only #6 in F1, while LinearBoost-K-exact achieves #3.*

### ROC-AUC Rankings

| Rank | Algorithm | Average AUC Rank |
|------|-----------|------------------|
| 1 | TabPFN | 3.00 |
| 2 | CatBoost | 3.14 |
| 3 | RandomForest | 4.57 |
| 4 | LinearBoost-K-exact | 4.83 |
| 5 | LogisticRegression | 5.00 |
| 5 | LightGBM | 5.00 |
| 7 | LinearBoost-K | 5.17 |
| 8 | XGBoost | 5.71 |
| 9 | LinearBoost-L | 6.71 |

**LinearBoost-L Position: #9** ⚠️ (Last)  
**LinearBoost-K-exact Position: #4** ✅

*Note: F1 optimization has a strong negative impact on LinearBoost-L's AUC performance.*

### Training Time Rankings (Lower is Better)

| Rank | Algorithm | Average Train Time Rank |
|------|-----------|-------------------------|
| 1 | TabPFN | 1.00 |
| 2 | LogisticRegression | 1.86 |
| 3 | LinearBoost-L | 4.29 |
| 3 | XGBoost | 4.29 |
| 5 | LightGBM | 4.86 |
| 6 | CatBoost | 6.43 |
| 6 | RandomForest | 6.43 |
| 8 | LinearBoost-K-exact | 7.17 |
| 8 | LinearBoost-K | 7.17 |

**LinearBoost-L Position: #3** ✅ (Excellent)  
*Note: LinearBoost-L is tied with XGBoost for #3 position in training speed.*

### Inference Time Rankings (Lower is Better)

| Rank | Algorithm | Average Inf Time Rank |
|------|-----------|----------------------|
| 1 | CatBoost | 1.00 |
| 2 | LightGBM | 2.00 |
| 3 | LogisticRegression | 3.29 |
| 4 | XGBoost | 4.00 |
| 5 | LinearBoost-L | 4.86 |
| 6 | RandomForest | 6.57 |
| 7 | LinearBoost-K | 7.00 |
| 8 | LinearBoost-K-exact | 7.17 |
| 9 | TabPFN | 8.67 |

**LinearBoost-L Position: #5** (Average)

---

## Per-Dataset Performance Highlights

### Datasets Analyzed

1. **Breast Cancer Wisconsin (Diagnostic)**
2. **Banknote Authentication**
3. **Chronic Kidney Disease**
4. **Haberman's Survival**
5. **Heart Disease**
6. **Hepatitis**
7. **Ionosphere**

### Notable LinearBoost-L Performances

- **Haberman's Survival**: **#1 in F1** (0.7258) - Best F1 performance on this dataset
- **Breast Cancer Wisconsin**: **#3 in F1** (0.9743), #3 in ROC-AUC (0.9937), **#3 in Training Time**
- **Banknote Authentication**: **#3 in Training Time**

### Areas for Weakness

- **Chronic Kidney Disease**: #9 in F1 (0.9609), #7 in ROC-AUC (0.9898) - Poor performance despite F1 optimization
- **Ionosphere**: #9 in F1 (0.8717), #9 in ROC-AUC (0.8925) - Worst performance across all datasets
- **Heart Disease**: #7 in F1 (0.8273), #9 in ROC-AUC (0.8900)

---

## Key Insights

### 1. **F1 Optimization Trade-offs**

When optimized for F1 score, LinearBoost-L shows:
- **Maintains fast training** (rank #3) ✅
- **Average F1 performance** (rank #6) - Not optimal despite F1 optimization
- **Poor AUC performance** (rank #9) ⚠️ - Significant trade-off

This suggests that F1 optimization for LinearBoost-L may not be as effective as AUC optimization for overall performance.

### 2. **LinearBoost-K-exact: The F1 Winner**

LinearBoost-K-exact achieves **rank #3 in F1** when optimized for F1, demonstrating that:
- The exact kernel variant benefits more from F1 optimization
- It achieves better balance between F1 (#3) and AUC (#4)
- However, it suffers from slow training (#8) and inference (#8)

### 3. **Training Efficiency Maintained**

LinearBoost-L maintains excellent training speed (rank #3) regardless of optimization metric, which is a consistent strength.

### 4. **AUC Performance Degradation**

LinearBoost-L's AUC rank drops from #4 (with AUC optimization) to #9 (with F1 optimization), indicating a strong trade-off. This suggests:
- LinearBoost-L's hyperparameters may need different tuning strategies for F1 vs AUC
- The F1 optimization may be selecting thresholds that reduce discrimination ability

### 5. **Variant Comparison**

- **LinearBoost-L**: Fastest, but struggles with AUC under F1 optimization
- **LinearBoost-K-exact**: Best F1 (#3) and AUC (#4) balance, but slow
- **LinearBoost-K**: Poor performance across all metrics

---

## Comparison: F1 vs AUC Optimization Impact

### LinearBoost-L Performance Comparison

| Metric | F1-Optimized (Dec 25) | AUC-Optimized (Dec 26) | Difference |
|--------|----------------------|------------------------|------------|
| **Overall Rank** | #6 | #6 | Same |
| **F1 Rank** | #6 | #6 | Same |
| **AUC Rank** | #9 | #4 | **+5 positions** ✅ |
| **Train Time Rank** | #3 | #4 | -1 position |
| **Inf Time Rank** | #5 | #7 | -2 positions |

**Key Finding:** AUC optimization significantly improves AUC performance (+5 positions) while maintaining the same overall rank (#6) and F1 rank (#6).

### Overall Algorithm Rankings Comparison

**F1-Optimized (Dec 25):**
1. CatBoost (3.18)
2. LogisticRegression (3.68)
3. TabPFN (4.12)
4. LightGBM (4.21)
5. XGBoost (5.04)
6. LinearBoost-L (5.32)

**AUC-Optimized (Dec 26):**
1. LogisticRegression (3.79)
2. LightGBM (3.93)
3. TabPFN (4.17)
4. XGBoost (4.36)
5. CatBoost (4.46)
6. LinearBoost-L (5.32)

**Observation:** LinearBoost-L maintains the same overall rank (#6) under both optimization strategies, but AUC optimization improves its AUC performance significantly without hurting overall position.

---

## Recommendations

### For Promoting LinearBoost:

1. **Use AUC Optimization**: AUC optimization improves LinearBoost-L's AUC rank from #9 to #4 while maintaining the same overall rank and F1 performance. This is clearly the better choice.

2. **Emphasize Training Speed**: Rank #3-4 in training time is a consistent strength that differentiates LinearBoost-L from slower alternatives.

3. **Highlight Specific Use Cases**:
   - Applications where AUC/ranking quality matters (e.g., recommendation systems, risk scoring)
   - Fast model iteration and development (fast training)
   - Medium-sized datasets

4. **Address Weaknesses**:
   - Investigate why F1 optimization doesn't improve F1 rank significantly
   - Improve AUC performance when F1 is the primary metric (better hyperparameter tuning strategies)
   - Optimize inference time for production deployment

### For Research/Development:

1. **Investigate F1-AUC Trade-off**: Why does F1 optimization hurt AUC so much for LinearBoost-L? Can we develop a multi-objective optimization strategy?

2. **Improve LinearBoost-K**: The approximation variant consistently underperforms; needs significant refinement.

3. **Hyperparameter Tuning Strategies**: Develop optimization strategies that maintain good AUC while optimizing for F1 (or vice versa).

4. **Dataset-Specific Analysis**: Investigate why LinearBoost-L struggles on specific datasets (e.g., Ionosphere, Chronic Kidney Disease) even with F1 optimization.

---

## Conclusion

LinearBoost-L demonstrates **consistent overall performance (rank #6)** under both F1 and AUC optimization strategies. However, **AUC optimization is clearly superior** for LinearBoost-L, as it:

- Improves AUC rank from #9 to #4 (significant improvement)
- Maintains the same overall rank (#6)
- Maintains the same F1 rank (#6)
- Preserves fast training speed (rank #3-4)

**Key Takeaway:** For promoting LinearBoost, **use AUC optimization** as it provides better balance and stronger performance in the metric that LinearBoost naturally excels at (discrimination ability).

The analysis also reveals that **LinearBoost-K-exact performs better under F1 optimization** (rank #3 in F1), suggesting different variants may benefit from different optimization strategies.

---

## Data Files

- **Overall Rankings**: `benchmark_results/yesterdays_rankings_dec25.csv`
- **Per-Dataset Rankings**: `benchmark_results/yesterdays_per_dataset_rankings_dec25.csv`
- **Individual Benchmark Results**: `benchmark_results/uci_*_20251225_*.json`

---

*Analysis Date: December 26, 2025*  
*Benchmark Configuration: F1-optimized hyperparameters, 5-fold CV, 30 runs per model*  
*Datasets: 7 UCI ML Repository datasets*  
*Comparison: This analysis complements the AUC-optimized benchmark analysis from December 26, 2025*

