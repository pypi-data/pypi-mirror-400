# Latest UCI Benchmark Rankings - Algorithm Comparison

**Analysis Date**: 2024-12-28  
**Datasets**: 7 UCI datasets (most recent results)  
**Algorithms**: 9 algorithms compared

## Executive Summary

Based on the most recent UCI benchmark results, here are the key findings:

### 🏆 Overall Rankings (Best to Worst)

1. **CatBoost** - 3.04 (Best overall performance)
2. **LogisticRegression** - 3.82 (Fastest training, good accuracy)
3. **LinearBoost-L** - 4.86 (Best LinearBoost variant, fast training)
4. **TabPFN** - 4.92 (Good accuracy, slow inference)
5. **LightGBM** - 5.11 (Fast inference, slower training)
6. **LinearBoost-K-exact** - 5.21 (Good accuracy, slower)
7. **XGBoost** - 5.68 (Slower training)
8. **RandomForest** - 5.79 (Balanced performance)
9. **LinearBoost-K** - 6.00 (Needs improvement)

### Key Insights

- ✅ **LinearBoost-L is the best LinearBoost variant** (ranked #3 overall)
- ⚠️ **LinearBoost-K-exact is competitive** (ranked #6 overall)
- ⚠️ **LinearBoost-K needs work** (ranked #9 overall)
- 🚀 **CatBoost dominates** - best F1, fastest inference, 2 wins
- ⚡ **LogisticRegression is fastest** for training (1.29 mean rank)
- 🐌 **TabPFN is slowest** for inference (9.00 mean rank)

---

## Detailed Rankings by Metric

### 1. F1 Score Rankings

| Rank | Model | Mean Rank | Wins | Top-3 | Median |
|------|-------|-----------|------|-------|--------|
| 1 | **CatBoost** | 2.86 | 2 | 4 | 3.0 |
| 2 | **TabPFN** | 3.50 | 2 | 4 | 2.0 |
| 3 | **LinearBoost-K-exact** | 4.14 | 1 | 4 | 3.0 |
| 4 | **LogisticRegression** | 4.29 | 1 | 3 | 4.0 |
| 5 | **LinearBoost-L** | 5.57 | 0 | 3 | 5.0 |
| 6 | **RandomForest** | 5.71 | 0 | 0 | 5.0 |
| 7 | **LinearBoost-K** | 6.00 | 1 | 1 | 6.0 |
| 8 | **LightGBM** | 6.00 | 0 | 1 | 6.0 |
| 9 | **XGBoost** | 6.14 | 0 | 1 | 7.0 |

**Insights:**
- CatBoost and TabPFN lead with 2 wins each
- LinearBoost-K-exact is competitive (rank 3, 1 win, 4 top-3 finishes)
- LinearBoost-L needs improvement (rank 5, no wins)
- LinearBoost-K performs poorly (rank 7, 1 win but high mean rank)

### 2. ROC-AUC Rankings

| Rank | Model | Mean Rank | Wins | Top-3 | Median |
|------|-------|-----------|------|-------|--------|
| 1 | **TabPFN** | 3.17 | 1 | 3 | 3.0 |
| 2 | **CatBoost** | 3.86 | 1 | 3 | 4.0 |
| 3 | **LinearBoost-K-exact** | 4.57 | 2 | 3 | 6.0 |
| 4 | **LightGBM** | 4.71 | 0 | 3 | 4.0 |
| 5 | **RandomForest** | 4.71 | 2 | 2 | 5.0 |
| 6 | **LogisticRegression** | 4.86 | 0 | 2 | 5.0 |
| 7 | **XGBoost** | 5.71 | 1 | 2 | 7.0 |
| 8 | **LinearBoost-K** | 6.29 | 0 | 2 | 8.0 |
| 9 | **LinearBoost-L** | 6.29 | 0 | 1 | 7.0 |

**Insights:**
- TabPFN leads ROC-AUC (but slow inference)
- LinearBoost-K-exact has 2 wins on ROC-AUC (tied for most)
- LinearBoost variants struggle with ROC-AUC (ranks 3 and 8-9)
- This suggests the F1 optimization may be hurting ROC-AUC

### 3. Training Time Rankings (Lower is Better)

| Rank | Model | Mean Rank | Wins | Top-3 | Median |
|------|-------|-----------|------|-------|--------|
| 1 | **LogisticRegression** | 1.29 | 6 | 7 | 1.0 |
| 2 | **LinearBoost-L** | 2.57 | 0 | 6 | 2.0 |
| 3 | **TabPFN** | 4.00 | 0 | 1 | 4.0 |
| 4 | **CatBoost** | 4.43 | 1 | 3 | 5.0 |
| 5 | **RandomForest** | 5.29 | 0 | 1 | 6.0 |
| 6 | **LinearBoost-K** | 5.43 | 0 | 1 | 6.0 |
| 7 | **LinearBoost-K-exact** | 5.71 | 0 | 2 | 7.0 |
| 8 | **LightGBM** | 7.57 | 0 | 0 | 8.0 |
| 9 | **XGBoost** | 8.00 | 0 | 0 | 8.0 |

**Insights:**
- LogisticRegression is fastest (6 wins, mean rank 1.29)
- **LinearBoost-L is 2nd fastest** - excellent training speed!
- LinearBoost variants are generally fast (ranks 2, 6, 7)
- XGBoost and LightGBM are slowest (ranks 8-9)

### 4. Inference Time Rankings (Lower is Better)

| Rank | Model | Mean Rank | Wins | Top-3 | Median |
|------|-------|-----------|------|-------|--------|
| 1 | **CatBoost** | 1.00 | 7 | 7 | 1.0 |
| 2 | **LightGBM** | 2.14 | 0 | 7 | 2.0 |
| 3 | **XGBoost** | 2.86 | 0 | 7 | 3.0 |
| 4 | **LogisticRegression** | 4.86 | 0 | 0 | 5.0 |
| 5 | **LinearBoost-L** | 5.00 | 0 | 0 | 5.0 |
| 6 | **LinearBoost-K** | 6.29 | 0 | 0 | 7.0 |
| 7 | **LinearBoost-K-exact** | 6.43 | 0 | 0 | 6.0 |
| 8 | **RandomForest** | 7.43 | 0 | 0 | 7.0 |
| 9 | **TabPFN** | 9.00 | 0 | 0 | 9.0 |

**Insights:**
- CatBoost dominates inference (7 wins, perfect 1.0 mean rank)
- Tree-based methods (CatBoost, LightGBM, XGBoost) are fastest
- LinearBoost variants are moderate (ranks 5, 6, 7)
- TabPFN is extremely slow (rank 9, 9-15 seconds per prediction!)

---

## Performance Highlights

### 🎯 Best Performers by Dataset

**Banknote Authentication:**
- F1: CatBoost (0.9988)
- ROC-AUC: Multiple tied (1.0000)
- Fastest Train: LogisticRegression (0.032s)
- Fastest Infer: CatBoost (0.0023s)

**Breast Cancer Wisconsin:**
- F1: LogisticRegression (0.9820)
- ROC-AUC: TabPFN (0.9968)
- Fastest Train: LogisticRegression (0.032s)
- Fastest Infer: CatBoost (0.0022s)

**Chronic Kidney Disease:**
- F1: TabPFN (0.9940)
- ROC-AUC: LinearBoost-K-exact (0.9927) 🏆
- Fastest Train: LogisticRegression (0.028s)
- Fastest Infer: CatBoost (0.0030s)

**Haberman's Survival:**
- F1: LinearBoost-K-exact (0.7365) 🏆
- ROC-AUC: RandomForest (0.7182)
- Fastest Train: CatBoost (0.0054s)
- Fastest Infer: CatBoost (0.0014s)

**Heart Disease:**
- F1: TabPFN (0.8398)
- ROC-AUC: XGBoost (0.9098)
- Fastest Train: LogisticRegression (0.032s)
- Fastest Infer: CatBoost (0.0016s)

**Hepatitis:**
- F1: CatBoost (0.8522)
- ROC-AUC: RandomForest (0.8791)
- Fastest Train: LogisticRegression (0.032s)
- Fastest Infer: CatBoost (0.0019s)

**Ionosphere:**
- F1: LinearBoost-K (0.9530) 🏆
- ROC-AUC: LinearBoost-K-exact (0.9860) 🏆
- Fastest Train: LogisticRegression (0.034s)
- Fastest Infer: CatBoost (0.0023s)

### 🏆 LinearBoost Wins

- **LinearBoost-K-exact**: 3 wins (Haberman F1, Ionosphere ROC-AUC, Chronic Kidney ROC-AUC)
- **LinearBoost-K**: 1 win (Ionosphere F1)
- **LinearBoost-L**: 0 wins (but good overall rank #3)

---

## Recommendations for LinearBoost Improvement

### Immediate Priorities

1. **Improve LinearBoost-K** (Rank #9 overall)
   - Currently worst-performing variant
   - F1 rank: 7, ROC-AUC rank: 8
   - Consider: Better kernel approximation tuning or parameter ranges

2. **Improve ROC-AUC for LinearBoost-L** (ROC-AUC rank: 9)
   - F1 performance is decent (rank 5)
   - ROC-AUC needs work (rank 9)
   - Consider: Multi-objective optimization balancing F1 and ROC-AUC

3. **Leverage LinearBoost-L's Speed Advantage**
   - Rank #2 for training time (only behind LogisticRegression)
   - Rank #5 for inference (good but could be better)
   - This is a key differentiator - emphasize speed in positioning

### Strengths to Build On

- ✅ **LinearBoost-K-exact** shows promise (3 wins, rank #6 overall)
- ✅ **LinearBoost-L** is very fast for training
- ✅ **Good F1 performance** on some datasets (Haberman, Ionosphere)
- ✅ **Adaptive learning rate** recently implemented should help

### Gap Analysis

**vs CatBoost (Best Overall):**
- F1 gap: LinearBoost-L rank 5 vs CatBoost rank 1 (gap: 2.71 rank points)
- ROC-AUC gap: LinearBoost-K-exact rank 3 vs CatBoost rank 2 (gap: 0.71 rank points)
- Training speed: LinearBoost-L rank 2 vs CatBoost rank 4 (advantage!)
- Inference speed: LinearBoost-L rank 5 vs CatBoost rank 1 (gap: 4.00 rank points)

**Key Gaps:**
1. **F1 performance** - Need +0.01-0.02 improvement to match CatBoost
2. **Inference speed** - Tree methods are faster, but LinearBoost is acceptable
3. **ROC-AUC** - Needs improvement for LinearBoost-L

---

## Next Implementation Steps

Based on these rankings and the previous analysis:

### 🔴 High Priority (Address Major Gaps)

1. **F1-Aware Estimator Weighting** 
   - Addresses F1 gap vs CatBoost
   - Expected: +0.015-0.025 F1
   - Should improve LinearBoost-L from rank 5 → rank 3-4

2. **Class-Imbalance Aware Boosting**
   - Helps on imbalanced datasets (Haberman, Hepatitis)
   - Expected: +0.02-0.03 F1 on imbalanced datasets
   - LinearBoost-K-exact already won Haberman - this could help more

3. **Multi-Objective Optimization**
   - Addresses ROC-AUC gap
   - Balance F1 and ROC-AUC (currently optimized only for F1)
   - Expected: Maintain F1, improve ROC-AUC by +0.01-0.02

### 🟡 Medium Priority

4. **Margin-Based Sample Weight Updates**
   - Stabilize training, improve convergence
   - Expected: +0.01-0.015 F1

5. **Ensemble Pruning**
   - Remove weak estimators
   - Expected: +0.005-0.01 F1

---

## Summary Table: LinearBoost Variants

| Variant | Overall Rank | F1 Rank | ROC-AUC Rank | Train Time Rank | Infer Time Rank | Wins | Strengths | Weaknesses |
|---------|--------------|---------|--------------|-----------------|-----------------|------|-----------|------------|
| **LinearBoost-L** | 3 | 5 | 9 | **2** | 5 | 0 | Very fast training | ROC-AUC performance |
| **LinearBoost-K-exact** | 6 | 3 | 3 | 7 | 7 | 3 | Good F1 & AUC | Slower training |
| **LinearBoost-K** | 9 | 7 | 8 | 6 | 6 | 1 | Fast | Overall performance |

**Key Finding**: LinearBoost-L ranks **#3 overall** primarily due to its excellent training speed (#2) and decent F1 performance (#5). However, ROC-AUC performance (#9) is a major weakness.

---

**Files Generated:**
- `algorithm_rankings.csv` - Detailed rankings in CSV format
- `algorithm_rankings_aggregated.json` - Aggregated rankings in JSON format
- `LATEST_UCI_BENCHMARK_RANKINGS.md` - This summary document

