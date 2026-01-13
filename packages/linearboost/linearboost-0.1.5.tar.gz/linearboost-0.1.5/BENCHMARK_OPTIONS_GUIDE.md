# Available Benchmark Options for LinearBoost

**Date**: December 29, 2024  
**Purpose**: Guide to available benchmark suites and datasets for evaluating LinearBoost

---

## 📊 **Current Benchmark Scripts**

### **1. `benchmark_2_openml.py`** ✅ (Just Adapted)
**Status**: Ready to use  
**Source**: OpenML (general binary classification datasets)

**Features**:
- Automatically queries OpenML for binary classification datasets
- Configurable filters (sample size, feature count, exclude images)
- Iterates over all matching datasets
- Saves results as `openml_{id}_{name}.json`

**Configuration**:
```python
N_DATASETS_TO_RUN = None  # None = all matching, or set number
MIN_SAMPLES = 100
MAX_SAMPLES = 50000
MIN_FEATURES = 2
MAX_FEATURES = 10000
EXCLUDE_IMAGE = True
```

**Pros**:
- Large variety of datasets
- Automatic discovery
- Well-maintained by OpenML community

**Cons**:
- May include noisy or problematic datasets
- No curation (unlike CC-18)

---

### **2. `benchmark_2.py`** ✅ (Currently Active)
**Status**: In use  
**Source**: UCI ML Repository

**Features**:
- Uses specific UCI dataset IDs: [336, 267, 46, 17, 45, 43, 52]
- Well-curated, reliable datasets
- Results saved as `uci_{id}_{name}.json`

**Pros**:
- High-quality, curated datasets
- Consistent format
- Well-documented

**Cons**:
- Limited to 7 datasets
- Manual dataset selection

---

### **3. `benchmark_2_hd.py`** ✅ (Currently Active)
**Status**: In use  
**Source**: Local `.mat` files from `hd-datasets` folder

**Features**:
- High-dimensional datasets (typically >1000 features)
- Loads from `.mat` files
- Results saved as `hd_{name}_{name}.json`

**Pros**:
- Tests on high-dimensional data
- Real-world genomics/medical datasets
- Tests scalability

**Cons**:
- Requires local dataset files
- Limited to available `.mat` files

---

### **4. `benchmark_with_sampling_linear_kernel_openml.py`** 📋 (Available)
**Status**: Exists but may need updates  
**Source**: OpenML CC-18 Suite (Suite ID 99)

**Features**:
- Uses OpenML CC-18 benchmark suite (curated collection)
- Filters for binary classification only
- Well-established benchmark suite

**Pros**:
- Curated, high-quality datasets
- Standard benchmark suite (CC-18 is widely used)
- Balanced selection

**Cons**:
- May need updates to match current benchmark structure
- CC-18 may have fewer binary datasets

---

## 🎯 **Recommended Benchmark Suites**

### **Option 1: OpenML CC-18 Suite** ⭐ RECOMMENDED

**What it is**: Curated benchmark suite from OpenML (Suite ID 99)  
**Why use it**: Standard benchmark suite used in ML research

**Implementation**:
- Already exists in `benchmark_with_sampling_linear_kernel_openml.py`
- May need adaptation to match `benchmark_2_openml.py` structure
- Filters for binary classification

**Expected Datasets**: ~20-30 binary classification datasets

**Code Reference**:
```python
# From benchmark_with_sampling_linear_kernel_openml.py
suite = openml.study.get_suite(suite_id=99)  # CC-18 suite
tasks = suite.tasks
# Filter for binary classification (number_classes=2)
```

---

### **Option 2: OpenML Studies** 📚

**Available Studies**:
1. **CC-18** (Suite ID 99) - Curated classification datasets
2. **CC-19** (Suite ID 98) - Extended version
3. **AutoML Benchmark** (Suite ID 271) - AutoML-focused
4. **Tabular Benchmarks** (various suite IDs)

**How to Use**:
```python
import openml

# Get any study/suite
suite = openml.study.get_suite(suite_id=99)  # CC-18
tasks = suite.tasks

# Filter for binary classification
for task_id in tasks:
    task = openml.tasks.get_task(task_id)
    if len(task.class_labels) == 2:
        # Process binary task
        pass
```

---

### **Option 3: OpenML Task Collections** 🔍

**Task-Based Approach**:
- Query OpenML tasks directly (not datasets)
- Tasks include train/test splits
- More standardized evaluation

**Example**:
```python
# List tasks with specific properties
tasks = openml.tasks.list_tasks(
    output_format="dataframe",
    task_type_id=1,  # Supervised classification
    number_classes=2,  # Binary
    status="active"
)
```

---

### **Option 4: Custom Dataset Collections** 📁

**Local File-Based**:
- `benchmark_file.py` - Loads from CSV files
- `benchmark_hd.py` - Loads from `.mat` files
- Can be adapted for any local dataset collection

**Kaggle Datasets**:
- `benchmark_kaggle.py` - Uses Kaggle API
- Requires Kaggle authentication
- Access to Kaggle competition datasets

---

## 🚀 **Recommended Next Steps**

### **Priority 1: Adapt CC-18 Suite** ⭐ HIGHEST PRIORITY

**Why**: CC-18 is a standard benchmark suite used in ML research

**Action**: Create `benchmark_2_cc18.py` based on `benchmark_2_openml.py`:
1. Use CC-18 suite (ID 99) instead of general OpenML query
2. Filter for binary classification
3. Use same benchmark structure as `benchmark_2_openml.py`

**Expected Impact**: 
- Standardized, comparable results
- ~20-30 high-quality datasets
- Widely recognized benchmark suite

---

### **Priority 2: Expand OpenML Query** 📈

**Enhance `benchmark_2_openml.py`**:
1. Add filtering by dataset quality metrics
2. Add filtering by domain (medical, finance, etc.)
3. Add filtering by data type (tabular only)
4. Prioritize datasets with more downloads/usage

**Example Enhancements**:
```python
# Filter by quality
datasets_df = datasets_df[datasets_df['NumberOfDownloads'] > 100]

# Filter by domain
medical_keywords = ['medical', 'health', 'disease', 'patient']
datasets_df = datasets_df[
    datasets_df['name'].str.lower().str.contains('|'.join(medical_keywords))
]
```

---

### **Priority 3: Multi-Class Support** 🔄

**Adapt for Multi-Class**:
- Modify `get_binary_openml_datasets()` to support multi-class
- Add parameter: `number_classes=None` (all) or `number_classes=3` (multi-class)
- Test LinearBoost on multi-class problems

---

## 📋 **Comparison of Benchmark Options**

| Benchmark Suite | Datasets | Quality | Curation | Standardization | Status |
|----------------|----------|---------|----------|-----------------|--------|
| **OpenML CC-18** | ~20-30 | High | ✅ Curated | ✅ Standard | ⭐ Recommended |
| **OpenML General** | 100+ | Mixed | ❌ Not curated | ⚠️ Variable | ✅ Available |
| **UCI ML Repo** | 7 | High | ✅ Curated | ✅ Standard | ✅ Active |
| **HD-datasets** | ~10 | High | ✅ Curated | ⚠️ Custom | ✅ Active |
| **Kaggle** | Many | Mixed | ⚠️ Varies | ⚠️ Varies | 📋 Available |

---

## 🎯 **Specific Recommendations**

### **For Comprehensive Evaluation**:
1. **CC-18 Suite** - Standard benchmark (highest priority)
2. **UCI ML Repo** - Current active benchmark (keep)
3. **HD-datasets** - High-dimensional testing (keep)

### **For Research Publication**:
1. **CC-18 Suite** - Required for comparability
2. **OpenML General** - Broader coverage
3. **UCI ML Repo** - Baseline comparison

### **For Algorithm Development**:
1. **UCI ML Repo** - Quick iteration (small datasets)
2. **HD-datasets** - Test scalability
3. **OpenML General** - Test generalization

---

## 🔧 **Implementation Guide**

### **Quick Start: CC-18 Suite**

To adapt `benchmark_2_openml.py` for CC-18:

1. **Replace `get_binary_openml_datasets()`**:
```python
def get_binary_cc18_datasets():
    """Get binary classification datasets from OpenML CC-18 suite."""
    suite = openml.study.get_suite(suite_id=99)
    tasks = suite.tasks
    
    binary_datasets = []
    for task_id in tasks:
        task = openml.tasks.get_task(task_id, download_data=False)
        if len(task.class_labels) == 2:
            dataset_id = task.dataset_id
            dataset_meta = openml.datasets.get_dataset(dataset_id, download_data=False)
            binary_datasets.append((dataset_id, dataset_meta.name))
    
    return binary_datasets
```

2. **Update main execution**:
```python
target_datasets = get_binary_cc18_datasets()
```

3. **Update file naming**:
```python
filename_prefix=f"cc18_{dataset_id}_{safe_name}"
```

---

## 📊 **Dataset Characteristics by Source**

### **OpenML CC-18**:
- **Size**: Small to medium (100-10,000 samples)
- **Features**: Low to medium (2-100 features)
- **Quality**: High (curated)
- **Domains**: Mixed (various domains)

### **OpenML General**:
- **Size**: Very small to very large (10-1M+ samples)
- **Features**: Low to very high (2-10,000+ features)
- **Quality**: Variable
- **Domains**: All domains

### **UCI ML Repo**:
- **Size**: Small to medium (100-5,000 samples)
- **Features**: Low to medium (2-50 features)
- **Quality**: High (curated)
- **Domains**: Mixed (classic ML datasets)

### **HD-datasets**:
- **Size**: Small to medium (50-500 samples)
- **Features**: Very high (1,000-20,000+ features)
- **Quality**: High (real-world genomics)
- **Domains**: Medical/genomics

---

## ✅ **Action Items**

1. **Create `benchmark_2_cc18.py`** - Adapt for CC-18 suite
2. **Enhance `benchmark_2_openml.py`** - Add quality/domain filters
3. **Document dataset selection criteria** - For reproducibility
4. **Create benchmark comparison script** - Compare results across suites

---

**Conclusion**: The **OpenML CC-18 Suite** is the most recommended addition for standardized, comparable benchmarks. It provides a curated set of high-quality datasets that are widely used in ML research.
