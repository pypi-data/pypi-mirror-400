import warnings
warnings.filterwarnings("ignore")

import time
import pickle
import json
import psutil
import tracemalloc
import os
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import rankdata
import optuna
from sklearn.model_selection import StratifiedKFold, cross_validate, StratifiedShuffleSplit
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.pipeline import Pipeline
from sklearn.metrics import make_scorer, f1_score, roc_auc_score
from sklearn.impute import SimpleImputer

import minio
import inspect

print(f"--- DIAGNOSTICS ---")
print(f"Minio Version Loaded: {getattr(minio, '__version__', 'Unknown')}")
print(f"Minio Location: {minio.__file__}")

# This will fail/print 'False' if the loaded version is too old
has_headers = 'request_headers' in inspect.signature(minio.Minio.fget_object).parameters
print(f"Has 'request_headers' support? {has_headers}")
print(f"-------------------")
# --- OPENML IMPORT ---
try:
    import openml
except ImportError as e:
    print(f"CRITICAL: 'openml' library not found. Error: {e}")
    print(f"Full traceback:")
    import traceback
    traceback.print_exc()
    exit(1)

# Import Models
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier

# Placeholder for your LinearBoost (Replace with actual import)
try:
    from src.linearboost.linear_boost import LinearBoostClassifier
except ImportError:
    # Dummy class for syntax validation if file is missing
    class LinearBoostClassifier:
        def __init__(self, **kwargs): pass
        def fit(self, X, y): return self

# TabPFN
try:
    from tabpfn import TabPFNClassifier
    TABPFN_AVAILABLE = True
except ImportError:
    TABPFN_AVAILABLE = False

optuna.logging.set_verbosity(optuna.logging.WARNING)

class ModelBenchmark:
    def __init__(self, X, y, dataset_name, categorical_cols, 
                 n_trials=50,          # Reduced default trials
                 cv_folds=10, 
                 n_runs=5,             # Reduced runs for OpenML speed
                 base_random_state=42, 
                 n_jobs=4,
                 optimization_subsample=0.2): # <--- NEW: Use only 20% data for tuning
        """
        optimization_subsample (float): Fraction of data to use for Hyperparameter Tuning.
                                        1.0 = use all data (slow).
                                        0.2 = use 20% data (fast).
        """
        self.X = X
        self.y = y
        self.dataset_name = dataset_name
        self.categorical_cols = categorical_cols
        self.n_trials = n_trials
        self.cv_folds = cv_folds
        self.n_runs = n_runs
        self.base_random_state = base_random_state
        self.n_jobs = n_jobs
        self.optimization_subsample = optimization_subsample
        
        np.random.seed(base_random_state)
        self.random_seeds = np.random.randint(0, 10000, size=n_runs)
        
        self.results = {}
        self.detailed_scores = defaultdict(lambda: defaultdict(list))
        self.best_params = {}
        
    def create_preprocessor(self):
        # Handle both numerical and categorical
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median'))
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='most_frequent')),
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
        ])

        return ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, make_column_selector(dtype_include=["int64", "float64"])),
                ("cat", categorical_transformer, make_column_selector(dtype_include=["object", "category", "bool"]))
            ],
            n_jobs=self.n_jobs
        )

    def optimize_hyperparameters(self):
        print(f"\n--- Phase 1: Tuning on '{self.dataset_name}' ---")
        
        # --- NEW: Subsampling Logic ---
        if self.optimization_subsample < 1.0 and len(self.X) > 1000:
            print(f"    Subsampling data to {self.optimization_subsample*100}% for fast tuning...")
            sss = StratifiedShuffleSplit(n_splits=1, test_size=1.0-self.optimization_subsample, random_state=42)
            train_idx, _ = next(sss.split(self.X, self.y))
            X_opt = self.X.iloc[train_idx]
            y_opt = self.y[train_idx]
        else:
            X_opt = self.X
            y_opt = self.y
            
        print(f"    Tuning Data Shape: {X_opt.shape}")
        
        # Use a smaller CV for optimization (3 folds is standard for tuning)
        cv_opt = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        
        # 1. LinearBoost
        print("    -> LinearBoost")
        self.best_params['LinearBoost'] = self._optimize_linearboost(X_opt, y_opt, cv_opt)
        
        # 2. XGBoost
        print("    -> XGBoost")
        self.best_params['XGBoost'] = self._optimize_xgboost(X_opt, y_opt, cv_opt)
        
        # 3. CatBoost
        print("    -> CatBoost")
        self.best_params['CatBoost'] = self._optimize_catboost(X_opt, y_opt, cv_opt)
        
        # TabPFN (No tuning)
        if TABPFN_AVAILABLE:
            self.best_params['TabPFN'] = {}

    def _optimize_linearboost(self, X, y, cv):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 10, 300), # Reduced max for speed
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 1.0, log=True),
                "algorithm": trial.suggest_categorical("algorithm", ["SAMME", "SAMME.R"]),
            }
            preprocessor = self.create_preprocessor()
            clf = LinearBoostClassifier(**params)
            pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
            
            try:
                # n_jobs=1 because we want sequential trials to avoid freezing
                return cross_validate(pipe, X, y, scoring='f1_weighted', cv=cv, n_jobs=1)['test_score'].mean()
            except:
                return -np.inf
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=False)
        return study.best_params

    def _optimize_xgboost(self, X, y, cv):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 20, 300),
                "max_depth": trial.suggest_int("max_depth", 1, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.5, log=True),
                "n_jobs": self.n_jobs,
                "verbosity": 0
            }
            # Add early preprocessing to handle cats for XGB without pipeline overhead if desired
            # But standard pipeline is safer for benchmarking
            model = xgb.XGBClassifier(**params)
            # Simple encoding for XGB
            X_enc = pd.get_dummies(X, drop_first=True)
            return cross_validate(model, X_enc, y, scoring='f1_weighted', cv=cv, n_jobs=1)['test_score'].mean()
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=False)
        return study.best_params

    def _optimize_catboost(self, X, y, cv):
        def objective(trial):
            params = {
                "iterations": trial.suggest_int("iterations", 50, 300),
                "depth": trial.suggest_int("depth", 1, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.5, log=True),
                "cat_features": self.categorical_cols,
                "verbose": 0,
                "thread_count": self.n_jobs,
                "allow_writing_files": False
            }
            model = CatBoostClassifier(**params)
            return cross_validate(model, X, y, scoring='f1_weighted', cv=cv, n_jobs=1)['test_score'].mean()

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=False)
        return study.best_params

    def evaluate_models(self):
        print(f"\n--- Phase 2: Final Evaluation on '{self.dataset_name}' (Full Data) ---")
        
        results_summary = {}
        
        # Define model factories
        model_factories = {
            'LinearBoost': lambda p: Pipeline([('prep', self.create_preprocessor()), ('clf', LinearBoostClassifier(**p))]),
            'XGBoost': lambda p: xgb.XGBClassifier(**p, n_jobs=self.n_jobs), # XGB handles internal encoding or we prep
            'CatBoost': lambda p: CatBoostClassifier(**p, cat_features=self.categorical_cols, verbose=0, thread_count=self.n_jobs)
        }
        if TABPFN_AVAILABLE:
            model_factories['TabPFN'] = lambda p: TabPFNClassifier(device='cpu')

        for name, factory in model_factories.items():
            if name == 'XGBoost':
                # Quick dirty fix for XGBoost categorical requirement
                X_eval = pd.get_dummies(self.X, drop_first=True)
                params = self.best_params[name]
            elif name == 'LinearBoost':
                 X_eval = self.X # Pipeline handles it
                 params = self.best_params[name]
            else:
                X_eval = self.X
                params = self.best_params[name]

            f1_scores = []
            times = []
            
            print(f"    Evaluating {name}...", end=" ")
            
            for seed in self.random_seeds:
                cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=seed)
                model = factory(params)
                
                # Full evaluation using 100% data
                scores = cross_validate(model, X_eval, self.y, scoring='f1_weighted', cv=cv, n_jobs=1)
                f1_scores.extend(scores['test_score'])
                times.extend(scores['fit_time'])
            
            print(f"Mean F1: {np.mean(f1_scores):.4f}")
            
            results_summary[name] = {
                'f1_mean': np.mean(f1_scores),
                'f1_std': np.std(f1_scores),
                'time_mean': np.mean(times)
            }
            
        return results_summary


class OpenMLBenchmarkSuite:
    def __init__(self, limit_datasets=None):
        self.limit = limit_datasets
        
    def get_binary_cc18_datasets(self):
        print("\nFetching OpenML CC-18 Benchmark Suite (Binary Only)...")
        # Get the CC-18 suite (ID 99)
        suite = openml.study.get_suite(suite_id=99)
        
        tasks = suite.tasks
        datasets = []
        
        count = 0
        
        # Download task metadata in bulk first (faster)
        # We need to filter tasks where the target has exactly 2 classes
        for task_id in tasks:
            if self.limit and count >= self.limit: break
            
            try:
                # 1. Get Task Metadata (lightweight)
                task = openml.tasks.get_task(task_id, download_data=False)
                
                # 2. Get Dataset Metadata (lightweight)
                ds_meta = openml.datasets.get_dataset(task.dataset_id, download_data=False)
                
                # 3. Check Class Count
                # We need to look at the 'NumberOfClasses' quality if available, 
                # or download the qualities specifically.
                # A more robust way for CC-18 is checking the class_labels in the task
                class_labels = task.class_labels
                
                if class_labels is None:
                    # Some regression tasks might sneak in, skip them
                    continue
                    
                n_classes = len(class_labels)
                
                if n_classes != 2:
                    # Skip multiclass
                    print(f"  Skipping {ds_meta.name} (Classes: {n_classes})")
                    continue
                
                # 4. Filter out heavy image datasets (optional but recommended for CPU)
                if ds_meta.name in ['Fashion-MNIST', 'Kuzushiji-MNIST', 'cifar10', 'mnist_784']: 
                    print(f"  Skipping {ds_meta.name} (Image/Too Large)")
                    continue

                # 5. Now actually download the data
                print(f"  ✓ ACCPETED: {ds_meta.name}")
                full_dataset = openml.datasets.get_dataset(task.dataset_id, download_data=True)
                datasets.append(full_dataset)
                count += 1
                
            except Exception as e:
                print(f"  Error inspecting task {task_id}: {e}")
                
        print(f"\nTotal Binary Datasets Loaded: {len(datasets)}")
        return datasets

    def process_dataset(self, dataset):
        X, y, categorical_indicator, attribute_names = dataset.get_data(
            target=dataset.default_target_attribute, dataset_format='dataframe'
        )
        
        # Convert categoricals
        cat_cols = [col for col, is_cat in zip(X.columns, categorical_indicator) if is_cat]
        for col in cat_cols:
            X[col] = X[col].astype('category')
            
        # Encode target
        le = LabelEncoder()
        y = le.fit_transform(y)
        
        return X, y, dataset.name, cat_cols

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    
    # Initialize Suite
    suite = OpenMLBenchmarkSuite(limit_datasets=None) # Set None to get ALL binary datasets
    
    # CALL THE BINARY FILTER METHOD
    datasets = suite.get_binary_cc18_datasets()    
    global_results = []

    # 2. Iterate through Datasets
    for ds in datasets:
        print(f"\n{'='*60}")
        print(f"PROCESSING DATASET: {ds.name}")
        print(f"{'='*60}")
        
        try:
            X, y, name, cat_cols = suite.process_dataset(ds)
            
            # Check size constraints
            if len(X) > 100000:
                print("Skipping (too large for laptop demo)")
                continue

            # Initialize Benchmark
            # NOTE: optimization_subsample=0.2 means we tune on 20% data
            benchmark = ModelBenchmark(
                X, y, name, cat_cols, 
                n_trials=20,          # Low for testing
                cv_folds=5, 
                n_runs=3, 
                n_jobs=4,             # Safe cap
                optimization_subsample=0.2 
            )
            
            # Phase 1: Optimize
            benchmark.optimize_hyperparameters()
            
            # Phase 2: Evaluate
            summary = benchmark.evaluate_models()
            
            # Flatten results for global tracking
            for model_name, metrics in summary.items():
                row = {
                    'dataset': name,
                    'model': model_name,
                    **metrics
                }
                global_results.append(row)
                
        except Exception as e:
            print(f"Failed on {ds.name}: {e}")
            import traceback
            traceback.print_exc()

    # 3. Global Summary
    print("\n" + "="*60)
    print("GLOBAL CC-18 BENCHMARK RESULTS")
    print("="*60)
    
    df_global = pd.DataFrame(global_results)
    
    # Calculate Average Rank
    # We pivot so index=dataset, columns=model, values=f1_mean
    pivot_df = df_global.pivot(index='dataset', columns='model', values='f1_mean')
    
    # Rank (higher score = rank 1, so we use ascending=False)
    ranks = pivot_df.rank(axis=1, ascending=False)
    avg_ranks = ranks.mean().sort_values()
    
    print("\nAverage Ranks (Lower is Better):")
    print(avg_ranks)
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d")
    df_global.to_csv(f"openml_cc18_results_{timestamp}.csv", index=False)
    print(f"\nFull results saved to openml_cc18_results_{timestamp}.csv")