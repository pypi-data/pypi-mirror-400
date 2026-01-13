# Algorithm Rankings on UCI Datasets (December 24, 2024)

This document presents algorithm rankings based on AUC (Area Under ROC Curve) and training time across 6 UCI datasets.

## Datasets Analyzed

1. 17_Breast Cancer Wisconsin (Diagnostic)
2. 267_Banknote Authentication
3. 43_Haberman's Survival
4. 45_Heart Disease
5. 46_Hepatitis
6. 52_Ionosphere

---

## 1. AUC Rankings (Higher is Better)

Rankings are based on average rank across all 6 datasets. Lower average rank indicates better performance.

| Rank | Algorithm | Average Rank | Average AUC |
|------|-----------|--------------|-------------|
| 1 | TabPFN | 1.80 | 0.8933 |
| 2 | CatBoost | 3.83 | 0.9036 |
| 3 | LinearBoost-L | 4.33 | 0.8922 |
| 4 | RandomForest | 4.67 | 0.9070 |
| 5 | LogisticRegression | 4.83 | 0.8964 |
| 6 | LightGBM | 5.17 | 0.8929 |
| 7 | LinearBoost-K-exact | 5.17 | 0.8919 |
| 8 | XGBoost | 6.67 | 0.8949 |
| 9 | LinearBoost-K | 7.33 | 0.8621 |

### Detailed AUC Results by Dataset

| Algorithm | 17_Breast Cancer Wisconsin (Diagnostic) | 267_Banknote Authentication | 43_Haberman's Survival | 45_Heart Disease | 46_Hepatitis | 52_Ionosphere | Average |
|-----------|---|---|---|---|---|---|---------|
| CatBoost | 0.9938 | 1.0000 | 0.6788 | 0.9126 | 0.8659 | 0.9706 | 0.9036 |
| LightGBM | 0.9933 | 1.0000 | 0.6449 | 0.8909 | 0.8513 | 0.9772 | 0.8929 |
| LinearBoost-K | 0.9510 | 0.9662 | 0.6987 | 0.8248 | 0.7595 | 0.9723 | 0.8621 |
| LinearBoost-K-exact | 0.9917 | 0.9999 | 0.7019 | 0.8320 | 0.8442 | 0.9818 | 0.8919 |
| LinearBoost-L | 0.9941 | 1.0000 | 0.6875 | 0.9119 | 0.8611 | 0.8986 | 0.8922 |
| LogisticRegression | 0.9956 | 0.9996 | 0.6854 | 0.9055 | 0.8864 | 0.9061 | 0.8964 |
| RandomForest | 0.9910 | 0.9998 | 0.7197 | 0.9080 | 0.8507 | 0.9730 | 0.9070 |
| TabPFN | 0.9968 | N/A | 0.7063 | 0.9080 | 0.8697 | 0.9856 | 0.8933 |
| XGBoost | 0.9922 | 0.9998 | 0.6613 | 0.9050 | 0.8387 | 0.9721 | 0.8949 |

---

## 2. Training Time Rankings (Lower is Better)

Rankings are based on average rank across all 6 datasets. Lower average rank indicates faster training.

| Rank | Algorithm | Average Rank | Average Time (seconds) |
|------|-----------|--------------|----------------------|
| 1 | TabPFN | 1.00 | 0.0000 |
| 2 | LogisticRegression | 1.83 | 0.0024 |
| 3 | XGBoost | 3.83 | 0.0422 |
| 4 | LinearBoost-L | 4.50 | 0.0409 |
| 5 | LightGBM | 6.00 | 0.0581 |
| 6 | LinearBoost-K-exact | 6.00 | 0.1386 |
| 7 | CatBoost | 6.50 | 0.0884 |
| 8 | RandomForest | 6.83 | 0.1508 |
| 9 | LinearBoost-K | 7.17 | 0.1479 |

### Detailed Training Time Results by Dataset

| Algorithm | 17_Breast Cancer Wisconsin (Diagnostic) | 267_Banknote Authentication | 43_Haberman's Survival | 45_Heart Disease | 46_Hepatitis | 52_Ionosphere | Average |
|-----------|---|---|---|---|---|---|---------|
| CatBoost | 0.1102 | 0.0704 | 0.0347 | 0.0895 | 0.0533 | 0.1722 | 0.0884 |
| LightGBM | 0.0415 | 0.0418 | 0.0536 | 0.0320 | 0.0572 | 0.1226 | 0.0581 |
| LinearBoost-K | 0.3982 | 0.0903 | 0.0295 | 0.1914 | 0.0566 | 0.1213 | 0.1479 |
| LinearBoost-K-exact | 0.2881 | 0.2444 | 0.0126 | 0.1995 | 0.0193 | 0.0675 | 0.1386 |
| LinearBoost-L | 0.0281 | 0.0154 | 0.0077 | 0.0831 | 0.0889 | 0.0222 | 0.0409 |
| LogisticRegression | 0.0032 | 0.0023 | 0.0018 | 0.0019 | 0.0021 | 0.0030 | 0.0024 |
| RandomForest | 0.2132 | 0.3531 | 0.0562 | 0.1359 | 0.0375 | 0.1090 | 0.1508 |
| TabPFN | 0.0000 | N/A | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| XGBoost | 0.0895 | 0.0102 | 0.0041 | 0.0074 | 0.0331 | 0.1090 | 0.0422 |

---

## 3. Combined Performance Analysis

### Top Performers by AUC

1. **TabPFN**: Average AUC = 0.8933, Average Rank = 1.80
2. **CatBoost**: Average AUC = 0.9036, Average Rank = 3.83
3. **LinearBoost-L**: Average AUC = 0.8922, Average Rank = 4.33

### Fastest Algorithms

1. **TabPFN**: Average Time = 0.0000s, Average Rank = 1.00
2. **LogisticRegression**: Average Time = 0.0024s, Average Rank = 1.83
3. **XGBoost**: Average Time = 0.0422s, Average Rank = 3.83

---

## Summary

- **Best AUC Performance**: TabPFN achieves the highest average AUC with an average rank of 1.80
- **Fastest Training**: TabPFN is also the fastest with an average rank of 1.00
- **Best Balance**: LinearBoost-L ranks 3rd in AUC (4.33) and 4th in training time (4.50), showing good balance

*Generated from benchmark results dated December 24, 2024*