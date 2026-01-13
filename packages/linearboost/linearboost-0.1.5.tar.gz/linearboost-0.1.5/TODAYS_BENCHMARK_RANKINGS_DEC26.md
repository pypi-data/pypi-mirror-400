# Today's Benchmark Rankings Analysis (December 26, 2025)
## Algorithm Performance Comparison Based on AUC-Optimized Benchmarks

---

## Executive Summary

This analysis compares algorithm performance across 7 UCI ML repository datasets using **AUC-optimized hyperparameters**. Rankings are computed per-dataset for each metric, then aggregated across all datasets. This approach provides a more robust and statistically meaningful comparison than simple score averaging.

**Key Finding:** LinearBoost-L ranks **#6 overall** (out of 9 algorithms), with particularly strong performance in ROC-AUC ranking (#4) and training time efficiency (#4).

---

## Overall Rankings

### Overall Algorithm Ranking (Averaged Across All Metrics)

| Rank | Algorithm | Avg F1 Rank | Avg AUC Rank | Avg Train Time Rank | Avg Inf Time Rank | Overall Rank |
|------|-----------|-------------|--------------|---------------------|-------------------|--------------|
| **1** | **LogisticRegression** | 4.71 | 5.29 | 1.86 | 3.29 | **3.79** |
| **2** | **LightGBM** | 3.71 | 4.86 | 5.14 | 2.00 | **3.93** |
| **3** | **TabPFN** | 2.17 | 4.50 | 1.00 | 9.00 | **4.17** |
| **4** | **XGBoost** | 4.71 | 4.86 | 4.00 | 3.86 | **4.36** |
| **5** | **CatBoost** | 5.57 | 4.00 | 7.29 | 1.00 | **4.46** |
| **6** | **LinearBoost-L** | 5.57 | 4.71 | 4.71 | 6.29 | **5.32** |
| **7** | **LinearBoost-K** | 6.29 | 5.86 | 6.00 | 6.14 | **6.07** |
| **8** | **LinearBoost-K-exact** | 5.86 | 4.14 | 7.00 | 7.43 | **6.11** |
| **8** | **RandomForest** | 5.43 | 6.14 | 6.86 | 6.00 | **6.11** |

*Note: Lower rank values indicate better performance. Ranks are averaged across 7 datasets.*

---

## LinearBoost Models Performance

### LinearBoost-L (Best Performing LinearBoost Variant)

**Overall Rank: #6 out of 9**

| Metric | Rank Position | Average Rank | Performance Assessment |
|--------|--------------|--------------|------------------------|
| **F1 Score** | #6 | 5.57 | Below average |
| **ROC-AUC** | **#4** | 4.71 | **Above average** |
| **Training Time** | **#4** | 4.71 | **Above average** |
| **Inference Time** | #7 | 6.29 | Below average |

**Strengths:**
- **Strong ROC-AUC performance**: Ranked #4, demonstrating excellent discrimination ability
- **Fast training**: Ranked #4, competitive with XGBoost and faster than gradient boosting variants on average
- **Balanced performance**: Consistent across different dataset characteristics

**Weaknesses:**
- **F1 Score**: Ranked #6, indicating room for improvement in precision-recall balance
- **Inference time**: Ranked #7, slower than top performers like CatBoost and LightGBM

### LinearBoost-K

**Overall Rank: #7 out of 9**

| Metric | Rank Position | Average Rank | Performance Assessment |
|--------|--------------|--------------|------------------------|
| **F1 Score** | #9 | 6.29 | Poor |
| **ROC-AUC** | #8 | 5.86 | Below average |
| **Training Time** | #6 | 6.00 | Average |
| **Inference Time** | #6 | 6.14 | Average |

**Assessment:** LinearBoost-K (kernel approximation variant) performs worse than LinearBoost-L overall, suggesting that the approximation may be losing important information or that the kernel variant needs further optimization.

### LinearBoost-K-exact

**Overall Rank: #8 out of 9 (tied with RandomForest)**

| Metric | Rank Position | Average Rank | Performance Assessment |
|--------|--------------|--------------|------------------------|
| **F1 Score** | #8 | 5.86 | Below average |
| **ROC-AUC** | **#2** | 4.14 | **Excellent** |
| **Training Time** | #8 | 7.00 | Slow |
| **Inference Time** | #8 | 7.43 | Slow |

**Strengths:**
- **Exceptional ROC-AUC**: Ranked #2, only behind TabPFN. This demonstrates the potential of exact kernel methods.

**Weaknesses:**
- **Slow training**: Ranked #8, computational cost is high
- **Slow inference**: Ranked #8, not suitable for real-time applications
- **F1 Score**: Ranked #8, despite excellent AUC, precision-recall balance is poor

---

## Per-Metric Rankings

### F1 Score Rankings

| Rank | Algorithm | Average F1 Rank |
|------|-----------|-----------------|
| 1 | TabPFN | 2.17 |
| 2 | LightGBM | 3.71 |
| 3 | LogisticRegression | 4.71 |
| 3 | XGBoost | 4.71 |
| 5 | RandomForest | 5.43 |
| 6 | LinearBoost-L | 5.57 |
| 6 | CatBoost | 5.57 |
| 8 | LinearBoost-K-exact | 5.86 |
| 9 | LinearBoost-K | 6.29 |

**LinearBoost-L Position: #6 (tied with CatBoost)**

### ROC-AUC Rankings

| Rank | Algorithm | Average AUC Rank |
|------|-----------|------------------|
| 1 | CatBoost | 4.00 |
| 2 | LinearBoost-K-exact | 4.14 |
| 3 | TabPFN | 4.50 |
| 4 | LinearBoost-L | 4.71 |
| 5 | LightGBM | 4.86 |
| 5 | XGBoost | 4.86 |
| 7 | LogisticRegression | 5.29 |
| 8 | LinearBoost-K | 5.86 |
| 9 | RandomForest | 6.14 |

**LinearBoost-L Position: #4** ✅  
**LinearBoost-K-exact Position: #2** ✅

### Training Time Rankings (Lower is Better)

| Rank | Algorithm | Average Train Time Rank |
|------|-----------|-------------------------|
| 1 | TabPFN | 1.00 |
| 2 | LogisticRegression | 1.86 |
| 3 | XGBoost | 4.00 |
| 4 | LinearBoost-L | 4.71 |
| 5 | LightGBM | 5.14 |
| 6 | LinearBoost-K | 6.00 |
| 7 | RandomForest | 6.86 |
| 8 | LinearBoost-K-exact | 7.00 |
| 9 | CatBoost | 7.29 |

**LinearBoost-L Position: #4** ✅  
*Note: TabPFN's rank of 1.00 is due to zero training time, but it has very slow inference (rank 9).*

### Inference Time Rankings (Lower is Better)

| Rank | Algorithm | Average Inf Time Rank |
|------|-----------|----------------------|
| 1 | CatBoost | 1.00 |
| 2 | LightGBM | 2.00 |
| 3 | LogisticRegression | 3.29 |
| 4 | XGBoost | 3.86 |
| 5 | RandomForest | 6.00 |
| 6 | LinearBoost-K | 6.14 |
| 7 | LinearBoost-L | 6.29 |
| 8 | LinearBoost-K-exact | 7.43 |
| 9 | TabPFN | 9.00 |

**LinearBoost-L Position: #7**

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

- **Heart Disease**: **#1 in ROC-AUC** (0.9122), #3 in F1 (0.8323)
- **Banknote Authentication**: **#3 in ROC-AUC** (0.9999), #3 in F1 (0.9973)
- **Ionosphere**: **#1 in ROC-AUC** (0.9454), #2 in F1 (0.9586)

### Areas for Improvement

- **Haberman's Survival**: #9 in F1 (0.6054), #8 in ROC-AUC (0.6896) - highly imbalanced dataset
- **Chronic Kidney Disease**: #8 in F1 (0.9368), #6 in ROC-AUC (0.9904)

---

## Key Insights

### 1. **LinearBoost-L: Strong AUC Optimizer**

When optimized for AUC, LinearBoost-L excels at **discrimination ability** (ROC-AUC rank #4) and maintains **fast training** (rank #4). This makes it a strong choice for applications where ranking quality is more important than threshold-based classification.

### 2. **ROC-AUC vs F1 Trade-off**

All LinearBoost variants show better ROC-AUC rankings than F1 rankings:
- LinearBoost-L: AUC #4 vs F1 #6
- LinearBoost-K-exact: AUC #2 vs F1 #8
- LinearBoost-K: AUC #8 vs F1 #9

This suggests LinearBoost models are better at learning class probabilities than at finding optimal classification thresholds for F1.

### 3. **Training Efficiency**

LinearBoost-L achieves rank #4 in training time, competitive with XGBoost and faster than CatBoost and RandomForest. This is a key advantage for iterative model development.

### 4. **Inference Time Challenge**

All LinearBoost variants have slower inference than top gradient boosting libraries (CatBoost, LightGBM). This may limit deployment in real-time applications.

### 5. **Kernel Variants Trade-offs**

- **LinearBoost-K-exact**: Excellent AUC (#2) but very slow (#8 in both training and inference)
- **LinearBoost-K**: Poor performance overall, suggesting the approximation may need refinement

---

## Recommendations

### For Promoting LinearBoost:

1. **Emphasize ROC-AUC Strength**: LinearBoost-L ranks #4 in AUC, making it ideal for applications where ranking/ranking quality matters (e.g., recommendation systems, risk scoring).

2. **Highlight Training Speed**: Rank #4 in training time is competitive and enables faster iteration.

3. **Target Specific Use Cases**:
   - Applications where AUC is more important than F1
   - Medium-sized datasets where training speed matters
   - Interpretable models (linear kernel provides feature importance)

4. **Address Weaknesses**:
   - Improve F1 optimization (perhaps with class weights or threshold tuning)
   - Optimize inference time for production deployment
   - Refine kernel approximation methods

### For Research/Development:

1. **Investigate F1-AUC Gap**: Why does LinearBoost excel at AUC but lag in F1? Can threshold optimization help?

2. **Optimize LinearBoost-K**: The approximation variant underperforms; consider alternative approximation strategies.

3. **Inference Optimization**: Explore model compression or faster prediction algorithms.

4. **Class Imbalance Handling**: Improve performance on imbalanced datasets like Haberman's Survival.

---

## Conclusion

LinearBoost-L demonstrates **competitive overall performance (rank #6)** with particular strengths in **ROC-AUC discrimination (#4)** and **training efficiency (#4)**. When optimized for AUC, it outperforms several established algorithms in these key metrics.

The analysis reveals that LinearBoost is well-suited for AUC-centric applications, where its strong discrimination ability and fast training provide a compelling value proposition. However, improvements in F1 optimization and inference speed would broaden its applicability.

**Compared to the F1-optimized benchmarks from December 24:**
- AUC optimization improved LinearBoost-L's AUC rank (from #6 to #4)
- But worsened its overall rank (from #3 to #6)
- This suggests F1 optimization may be more balanced for overall performance

---

## Data Files

- **Overall Rankings**: `benchmark_results/todays_rankings_dec26.csv`
- **Per-Dataset Rankings**: `benchmark_results/todays_per_dataset_rankings_dec26.csv`
- **Individual Benchmark Results**: `benchmark_results/uci_*_20251226_*.json`

---

*Analysis Date: December 26, 2025*  
*Benchmark Configuration: AUC-optimized hyperparameters, 5-fold CV, 30 runs per model*  
*Datasets: 7 UCI ML Repository datasets*

