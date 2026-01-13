# UCI Dataset Recommendations for LinearBoost Benchmarking

Based on analysis of today's F1-optimized benchmark results (December 26, 2025), this document recommends additional UCI datasets that align with the characteristics of datasets where LinearBoost variants perform well.

## Current Dataset Profile

**Today's Benchmarks (7 datasets):**
- **Average size**: 494 samples (range: 155-1372)
- **Average features**: 18 features (range: 3-34)
- **Feature types**: Mostly numeric (6/7), 1 mixed
- **Class balance**: Mostly balanced (5/7), 2 moderately imbalanced
- **Domains**: Medical (5), Pattern Recognition (1), Authentication (1)

**Current datasets:**
1. **Breast Cancer Wisconsin (Diagnostic)** - ID 17: 569 samples, 30 numeric features
2. **Haberman's Survival** - ID 43: 306 samples, 3 numeric features
3. **Heart Disease** - ID 45: 303 samples, 13 numeric features
4. **Hepatitis** - ID 46: 155 samples, 19 numeric features
5. **Ionosphere** - ID 52: 351 samples, 34 numeric features
6. **Banknote Authentication** - ID 267: 1372 samples, 4 numeric features
7. **Chronic Kidney Disease** - ID 336: 400 samples, 24 features (14 numeric, 10 categorical)

## Top Priority Recommendations (HIGH)

These datasets closely match current benchmark characteristics (100-500 samples):

### 1. **Sonar (Mines vs Rocks)** - ID 182
- **Samples**: 208
- **Features**: 60 (numeric)
- **Domain**: Pattern Recognition
- **Why**: High-dimensional numeric dataset like Ionosphere (ID 52), tests LinearBoost's ability to handle many features on small datasets
- **Expected performance**: Should perform similarly to Ionosphere

### 2. **Connectionist Bench (Sonar)** - ID 148
- **Samples**: 208
- **Features**: 60 (numeric)
- **Domain**: Pattern Recognition
- **Why**: Same as above - tests high-dimensional pattern recognition
- **Expected performance**: Should perform similarly to Ionosphere

### 3. **Parkinsons** - ID 158
- **Samples**: 197
- **Features**: 22 (numeric)
- **Domain**: Medical
- **Why**: Medical domain (aligns with 5 current medical datasets), small size like Hepatitis
- **Expected performance**: Should perform well given medical domain and balanced features

### 4. **Wine** - ID 109
- **Samples**: 178
- **Features**: 13 (numeric)
- **Domain**: Food/Chemistry
- **Why**: Small, numeric, balanced - ideal for LinearBoost's strengths
- **Expected performance**: Excellent - similar profile to Heart Disease

### 5. **Lymphography** - ID 329
- **Samples**: 148
- **Features**: 18 (mixed: numeric + categorical)
- **Domain**: Medical
- **Why**: Medical domain, mixed features like Chronic Kidney Disease, small size
- **Expected performance**: Good test of mixed feature handling

### 6. **Iris (Binary Version)** - ID 53
- **Samples**: 150
- **Features**: 4 (numeric)
- **Domain**: Botany
- **Why**: Classic small dataset, very few features (similar to Haberman's 3 features)
- **Expected performance**: Should be easy - very simple feature space

## Medium Priority Recommendations (MEDIUM)

These datasets are slightly larger (500-1500 samples) but still manageable:

### 7. **Statlog (Australian Credit Approval)** - ID 468
- **Samples**: 690
- **Features**: 14 (mixed)
- **Domain**: Finance
- **Why**: Similar size to Breast Cancer, mixed features, financial domain (new domain)
- **Expected performance**: Good - similar to current medium-sized datasets

### 8. **Breast Cancer Wisconsin (Original)** - ID 27
- **Samples**: 699
- **Features**: 9 (numeric)
- **Domain**: Medical
- **Why**: Related to current dataset 17, same domain, fewer features
- **Expected performance**: Should perform similarly to dataset 17

### 9. **Blood Transfusion Service Center** - ID 470
- **Samples**: 748
- **Features**: 4 (numeric)
- **Domain**: Medical
- **Why**: Medical domain, very few features like Banknote Authentication
- **Expected performance**: Excellent - simple feature space, medical domain

### 10. **Pima Indians Diabetes** - ID 142
- **Samples**: 768
- **Features**: 8 (numeric)
- **Domain**: Medical
- **Why**: Medical domain like Heart Disease, moderate imbalance
- **Expected performance**: Good - similar to Heart Disease profile

### 11. **Statlog (German Credit Data)** - ID 264
- **Samples**: 1000
- **Features**: 20 (mixed)
- **Domain**: Finance
- **Why**: Mixed features like Chronic Kidney Disease, financial domain
- **Expected performance**: Moderate - mixed features but larger size

### 12. **QSAR Biodegradation** - ID 445
- **Samples**: 1055
- **Features**: 41 (numeric)
- **Domain**: Chemistry
- **Why**: High-dimensional like Ionosphere, medium size
- **Expected performance**: Good test of scalability with many features

### 13. **Yeast** - ID 275
- **Samples**: 1484
- **Features**: 8 (numeric)
- **Domain**: Biology
- **Why**: Medium size like Banknote, numeric features
- **Expected performance**: Good - simple feature space, manageable size

## Lower Priority (Larger Datasets)

These may require sampling for hyperparameter tuning but provide scalability testing:

### 14. **Car Evaluation** - ID 21
- **Samples**: 1728
- **Features**: 6 (categorical)
- **Domain**: Decision Making
- **Why**: Tests LinearBoost's flexibility with categorical features
- **Note**: May need special handling for categorical-only features

### 15. **Wilt** - ID 469
- **Samples**: 4839
- **Features**: 5 (numeric)
- **Domain**: Remote Sensing
- **Why**: Few features, larger dataset for scalability
- **Note**: Will likely need sampling for HP tuning (>2000 threshold)

## Selection Strategy

Based on your current benchmark results showing good performance with:
- Small to medium datasets (155-1372 samples)
- Numeric or mixed features
- Medical and pattern recognition domains
- Balanced to moderately imbalanced classes

**Recommended testing order:**

1. **Start with HIGH priority datasets** (100-500 samples) - these match current profile exactly
2. **Add MEDIUM priority datasets** (500-1500 samples) - test scalability while maintaining similar characteristics
3. **Consider larger datasets** (>1500 samples) - only if you want to test scaling behavior

## Expected Benefits

Adding these datasets will:
1. **Validate robustness**: Test LinearBoost across more problem types
2. **Domain coverage**: Add finance, chemistry, and remote sensing domains
3. **Feature diversity**: Test categorical-only (Car) and very high-dimensional (Sonar)
4. **Size coverage**: Cover the full small-medium range (148-4839 samples)
5. **Maintain consistency**: All recommendations align with current success patterns

## Implementation Notes

When adding these datasets to your benchmark:
- Use the same F1 optimization approach that worked today
- Maintain the same hyperparameter tuning settings (200 trials, 5-fold CV, 30 runs)
- For datasets >2000 samples, use sampling for HP tuning (as configured)
- For categorical-only datasets (Car), ensure proper encoding is handled
- Consider domain groupings for analysis (medical vs. pattern recognition vs. finance)

## Quick Reference

**To add to benchmark, use these UCI ML Repository IDs:**
```
HIGH Priority: 182, 148, 158, 109, 329, 53
MEDIUM Priority: 468, 27, 470, 142, 264, 445, 275
LOW Priority: 21, 469
```

Generated: December 26, 2025  
Based on: Today's F1-optimized benchmark results (7 UCI datasets)

