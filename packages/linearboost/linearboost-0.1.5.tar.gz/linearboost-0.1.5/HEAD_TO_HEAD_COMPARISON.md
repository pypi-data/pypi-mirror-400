# Head-to-Head Algorithm Comparison

**Analysis Date**: December 30, 2024  
**Source**: Most recent UCI benchmark results (7 datasets)  
**Note**: All LinearBoost variants (LinearBoost-L, LinearBoost-K, LinearBoost-K-exact) are treated as one classifier, using the best performing variant per dataset.

---

## 📊 **F1 Score Comparison**

### **Win/Loss Matrix (Format: Wins-Losses-Ties (Total Comparisons))**

| Algorithm | CatBoost | LightGBM | LinearBoost | LogisticRegression | RandomForest | TabPFN | XGBoost |
|-----------|----------|----------|-------------|-------------------|--------------|--------|---------|
| **CatBoost** | -- | 5-2-0 (7) | 4-3-0 (7) | 4-3-0 (7) | 7-0-0 (7) | 2-4-0 (6) | 5-2-0 (7) |
| **LightGBM** | 2-5-0 (7) | -- | 3-4-0 (7) | 2-5-0 (7) | 4-3-0 (7) | 1-5-0 (6) | 5-2-0 (7) |
| **LinearBoost** | 3-4-0 (7) | 4-3-0 (7) | -- | 4-3-0 (7) | 6-1-0 (7) | 3-3-0 (6) | 5-2-0 (7) |
| **LogisticRegression** | 3-4-0 (7) | 5-2-0 (7) | 3-4-0 (7) | -- | 4-3-0 (7) | 3-3-0 (6) | 5-2-0 (7) |
| **RandomForest** | 0-7-0 (7) | 3-4-0 (7) | 1-6-0 (7) | 3-4-0 (7) | -- | 2-4-0 (6) | 3-4-0 (7) |
| **TabPFN** | 4-2-0 (6) | 5-1-0 (6) | 3-3-0 (6) | 3-3-0 (6) | 4-2-0 (6) | -- | 5-1-0 (6) |
| **XGBoost** | 2-5-0 (7) | 2-5-0 (7) | 2-5-0 (7) | 2-5-0 (7) | 4-3-0 (7) | 1-5-0 (6) | -- |

### **F1 Score Summary Statistics**

| Algorithm | Wins | Losses | Ties | Total | Win Rate (%) |
|-----------|------|--------|------|-------|--------------|
| **TabPFN** | 24 | 12 | 0 | 36 | **66.7%** |
| **CatBoost** | 27 | 14 | 0 | 41 | **65.9%** |
| **LinearBoost** | 25 | 16 | 0 | 41 | **61.0%** |
| **LogisticRegression** | 23 | 18 | 0 | 41 | **56.1%** |
| **LightGBM** | 17 | 24 | 0 | 41 | **41.5%** |
| **XGBoost** | 13 | 28 | 0 | 41 | **31.7%** |
| **RandomForest** | 12 | 29 | 0 | 41 | **29.3%** |

### **Key F1 Observations**:

1. **TabPFN** leads with 66.7% win rate (24 wins, 12 losses)
2. **CatBoost** is second with 65.9% win rate (27 wins, 14 losses)
3. **LinearBoost** ranks **3rd** with **61.0% win rate** (25 wins, 16 losses)
4. **LinearBoost vs. Key Competitors (F1)**:
   - vs. CatBoost: **3 wins, 4 losses** (43% win rate)
   - vs. LightGBM: **4 wins, 3 losses** (57% win rate)
   - vs. XGBoost: **5 wins, 2 losses** (71% win rate) ⭐
   - vs. RandomForest: **6 wins, 1 loss** (86% win rate) ⭐
   - vs. LogisticRegression: **4 wins, 3 losses** (57% win rate)
   - vs. TabPFN: **3 wins, 3 losses** (50% win rate)

---

## 📈 **ROC-AUC Comparison**

### **Win/Loss Matrix (Format: Wins-Losses-Ties (Total Comparisons))**

| Algorithm | CatBoost | LightGBM | LinearBoost | LogisticRegression | RandomForest | TabPFN | XGBoost |
|-----------|----------|----------|-------------|-------------------|--------------|--------|---------|
| **CatBoost** | -- | 2-5-0 (7) | 3-4-0 (7) | 4-3-0 (7) | 3-4-0 (7) | 1-5-0 (6) | 2-5-0 (7) |
| **LightGBM** | 5-2-0 (7) | -- | 2-5-0 (7) | 4-3-0 (7) | 5-2-0 (7) | 2-4-0 (6) | 4-3-0 (7) |
| **LinearBoost** | 4-3-0 (7) | 5-2-0 (7) | -- | 3-4-0 (7) | 4-3-0 (7) | 2-4-0 (6) | 5-2-0 (7) |
| **LogisticRegression** | 3-4-0 (7) | 3-4-0 (7) | 4-3-0 (7) | -- | 2-5-0 (7) | 2-4-0 (6) | 3-4-0 (7) |
| **RandomForest** | 4-3-0 (7) | 2-5-0 (7) | 3-4-0 (7) | 5-2-0 (7) | -- | 3-3-0 (6) | 3-4-0 (7) |
| **TabPFN** | 5-1-0 (6) | 4-2-0 (6) | 4-2-0 (6) | 4-2-0 (6) | 3-3-0 (6) | -- | 4-2-0 (6) |
| **XGBoost** | 5-2-0 (7) | 3-4-0 (7) | 2-5-0 (7) | 4-3-0 (7) | 4-3-0 (7) | 2-4-0 (6) | -- |

### **ROC-AUC Summary Statistics**

| Algorithm | Wins | Losses | Ties | Total | Win Rate (%) |
|-----------|------|--------|------|-------|--------------|
| **TabPFN** | 24 | 12 | 0 | 36 | **66.7%** |
| **LinearBoost** | 23 | 18 | 0 | 41 | **56.1%** |
| **LightGBM** | 22 | 19 | 0 | 41 | **53.7%** |
| **RandomForest** | 20 | 21 | 0 | 41 | **48.8%** |
| **XGBoost** | 20 | 21 | 0 | 41 | **48.8%** |
| **LogisticRegression** | 17 | 24 | 0 | 41 | **41.5%** |
| **CatBoost** | 15 | 26 | 0 | 41 | **36.6%** |

### **Key ROC-AUC Observations**:

1. **TabPFN** leads with 66.7% win rate (24 wins, 12 losses)
2. **LinearBoost** ranks **2nd** with **56.1% win rate** (23 wins, 18 losses) ⭐
3. **LightGBM** is third with 53.7% win rate (22 wins, 19 losses)
4. **LinearBoost vs. Key Competitors (ROC-AUC)**:
   - vs. CatBoost: **4 wins, 3 losses** (57% win rate) ⭐
   - vs. LightGBM: **5 wins, 2 losses** (71% win rate) ⭐
   - vs. XGBoost: **5 wins, 2 losses** (71% win rate) ⭐
   - vs. RandomForest: **4 wins, 3 losses** (57% win rate)
   - vs. LogisticRegression: **3 wins, 4 losses** (43% win rate)
   - vs. TabPFN: **2 wins, 4 losses** (33% win rate)

---

## 🎯 **Overall Summary**

### **Combined Performance (F1 + ROC-AUC)**

| Algorithm | F1 Win Rate | ROC-AUC Win Rate | Average Win Rate |
|-----------|-------------|------------------|------------------|
| **TabPFN** | 66.7% | 66.7% | **66.7%** |
| **CatBoost** | 65.9% | 36.6% | 51.3% |
| **LinearBoost** | 61.0% | 56.1% | **58.6%** |
| **LightGBM** | 41.5% | 53.7% | 47.6% |
| **LogisticRegression** | 56.1% | 41.5% | 48.8% |
| **XGBoost** | 31.7% | 48.8% | 40.3% |
| **RandomForest** | 29.3% | 48.8% | 39.1% |

### **LinearBoost Highlights**:

✅ **F1 Score**: 3rd place (61.0% win rate)
- Strong wins against XGBoost (5-2) and RandomForest (6-1)
- Competitive with TabPFN (3-3 tie)
- Slight edge over LightGBM (4-3)

✅ **ROC-AUC**: 2nd place (56.1% win rate)
- Strong wins against LightGBM (5-2) and XGBoost (5-2)
- Beats CatBoost (4-3)
- Competitive with RandomForest (4-3)

✅ **Overall**: 3rd place (58.6% average win rate)
- Only TabPFN and CatBoost (F1-focused) perform better
- Consistently outperforms traditional tree-based methods (XGBoost, RandomForest)
- Competitive with modern gradient boosting (LightGBM)

---

## 📝 **Detailed Pairwise Comparisons**

### **LinearBoost vs. Each Algorithm (F1 Score)**

1. **vs. RandomForest**: 6-1 (86% win rate) - **Strong Advantage** ⭐
2. **vs. XGBoost**: 5-2 (71% win rate) - **Strong Advantage** ⭐
3. **vs. LightGBM**: 4-3 (57% win rate) - **Slight Advantage**
4. **vs. LogisticRegression**: 4-3 (57% win rate) - **Slight Advantage**
5. **vs. CatBoost**: 3-4 (43% win rate) - **Slight Disadvantage**
6. **vs. TabPFN**: 3-3 (50% win rate) - **Even**

### **LinearBoost vs. Each Algorithm (ROC-AUC)**

1. **vs. LightGBM**: 5-2 (71% win rate) - **Strong Advantage** ⭐
2. **vs. XGBoost**: 5-2 (71% win rate) - **Strong Advantage** ⭐
3. **vs. CatBoost**: 4-3 (57% win rate) - **Slight Advantage**
4. **vs. RandomForest**: 4-3 (57% win rate) - **Slight Advantage**
5. **vs. LogisticRegression**: 3-4 (43% win rate) - **Slight Disadvantage**
6. **vs. TabPFN**: 2-4 (33% win rate) - **Disadvantage**

---

## 💡 **Key Insights**

1. **LinearBoost is competitive**: Ranks 3rd overall, with strong performance against traditional methods
2. **ROC-AUC strength**: LinearBoost performs better on ROC-AUC (2nd place) than F1 (3rd place)
3. **Tree-based advantage**: Consistently beats XGBoost and RandomForest on both metrics
4. **Modern methods challenge**: TabPFN and CatBoost remain strong competitors
5. **Balanced performance**: LinearBoost shows consistent performance across both metrics, unlike some competitors (e.g., CatBoost strong on F1 but weak on ROC-AUC)

---

## 📂 **Files Generated**

- `head_to_head_f1_mean.csv` - Detailed F1 comparison data
- `head_to_head_roc_auc_mean.csv` - Detailed ROC-AUC comparison data
- `HEAD_TO_HEAD_COMPARISON.md` - This summary document
