"""
Model Benchmark with Dual LinearBoost Variants
===============================================

This benchmark compares:
- LinearBoost-L: Linear kernel only (optimized for speed and model size)
- LinearBoost-K: Non-linear kernels (RBF, Poly, Sigmoid - optimized for accuracy)
- XGBoost
- LightGBM  
- CatBoost
- TabPFN (optional)

Author: Hamidreza Keshavarz
"""

import warnings
# Filter warnings to keep output clean
warnings.filterwarnings("ignore", message=".*ignore_implicit_zeros.*")
warnings.filterwarnings("ignore", message=".*n_quantiles.*")
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import time
import pickle
import json
import psutil
import tracemalloc
import os
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import rankdata
import optuna
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.pipeline import Pipeline
from sklearn.metrics import make_scorer, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier


# Import the models
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier

# Import Datasets 
import openml

# Import LinearBoost
try:
    from src.linearboost.linear_boost import LinearBoostClassifier
except ImportError:
    try:
        from linearboost import LinearBoostClassifier
    except ImportError:
        print("Warning: LinearBoostClassifier not found. Make sure path is correct.")
        class LinearBoostClassifier:
            def __init__(self, **kwargs): pass
            def fit(self, X, y): return self

# Import TabPFN (optional)
TABPFN_AVAILABLE = False
TABPFN_ERROR_MSG = ""
try:
    from tabpfn import TabPFNClassifier
    import torch  # Import torch explicitly
    
    # Set threads BEFORE any model initialization happens
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)

    _test_tabpfn = TabPFNClassifier(device='cpu')
    del _test_tabpfn
    TABPFN_AVAILABLE = True
except ImportError:
    TABPFN_ERROR_MSG = "TabPFN not installed. Install with: pip install tabpfn"
except Exception as e:
    error_str = str(e)
    if "401" in error_str or "Unauthorized" in error_str or "GatedRepoError" in error_str:
        TABPFN_ERROR_MSG = ("TabPFN requires HuggingFace authentication.")
    else:
        TABPFN_ERROR_MSG = f"TabPFN initialization failed: {error_str[:100]}"
    TABPFN_AVAILABLE = False

# Suppress Optuna logging
optuna.logging.set_verbosity(optuna.logging.WARNING)


class ModelBenchmark:
    """
    Comprehensive benchmarking framework for ML models with:
    - Dual LinearBoost variants (Linear and Kernel)
    - Statistical testing (Friedman, Wilcoxon, Nemenyi)
    - Memory profiling
    - Energy consumption estimation
    - Single-core timing for fair speed comparison
    """
    
    def __init__(self, X, y, categorical_cols, n_trials=200, cv_folds=10, 
                 n_runs=30, base_random_state=42, n_jobs=4,
                 hp_sample_threshold=2000, hp_sample_size=1500,
                 include_tabpfn=False):
        """
        Initialize the benchmark framework.
        
        Parameters
        ----------
        X : pd.DataFrame
            Feature matrix
        y : np.ndarray
            Target vector
        categorical_cols : list
            List of categorical column names
        n_trials : int
            Number of Optuna trials for hyperparameter optimization
        cv_folds : int
            Number of cross-validation folds per run
        n_runs : int
            Number of repeated runs with different random seeds
        base_random_state : int
            Base random seed for reproducibility
        n_jobs : int
            Number of threads allowed per model
        hp_sample_threshold : int
            If dataset has more records than this, use stratified sampling for HP tuning
        hp_sample_size : int
            Number of records to use for HP tuning when sampling is applied
        include_tabpfn : bool
            Whether to include TabPFN in benchmarks (can be slow)
        """
        # Preprocess data
        self.X = self._preprocess_data(X.copy(), categorical_cols)
        self.y = y
        self.categorical_cols = categorical_cols
        self.n_trials = n_trials
        self.cv_folds = cv_folds
        self.n_runs = n_runs
        self.base_random_state = base_random_state
        self.n_jobs = n_jobs
        self.include_tabpfn = include_tabpfn and TABPFN_AVAILABLE
        
        # Stratified sampling parameters
        self.hp_sample_threshold = hp_sample_threshold
        self.hp_sample_size = hp_sample_size
        
        # Create stratified sample for HP tuning if dataset is large
        self.X_hp, self.y_hp = self._create_hp_sample()
        
        # Generate random seeds for each run
        np.random.seed(base_random_state)
        self.random_seeds = np.random.randint(0, 10000, size=n_runs)
        
        # Store results
        self.results = {}
        self.detailed_scores = defaultdict(lambda: defaultdict(list))
        self.best_params = {}
        self.resource_profiles = {}
        
        # System info
        self.system_info = self._get_system_info()
        
        # Define model list
        self.model_names = [
            'LinearBoost-L',   # Linear kernel
            'LinearBoost-K',   # Non-linear kernels
            'LogisticRegression',
            'RandomForest',
            'XGBoost',
            'LightGBM',
            'CatBoost'
        ]
        if self.include_tabpfn:
            self.model_names.append('TabPFN')
    
    def _preprocess_data(self, X, categorical_cols):
        """Preprocess data to handle NaN values properly for all models."""
        X = X.copy()
        
        # Handle NaN in categorical columns
        for col in categorical_cols:
            if col in X.columns:
                X[col] = X[col].astype(str).replace('nan', 'missing').replace('None', 'missing')
                X[col] = X[col].astype('category')
        
        # Handle object columns
        object_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in object_cols:
            if X[col].isna().any():
                X[col] = X[col].fillna('missing')
            X[col] = X[col].astype(str).replace('nan', 'missing').replace('None', 'missing')
            X[col] = X[col].astype('category')
        
        # Handle NaN in numeric columns
        numeric_cols = X.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
        for col in numeric_cols:
            if X[col].isna().any():
                X[col] = X[col].fillna(X[col].median())
        
        print(f"\nData preprocessing complete:")
        print(f"  - Categorical columns ({len(categorical_cols)}): NaN -> 'missing'")
        print(f"  - Numeric columns ({len(numeric_cols)}): NaN -> median")
        print(f"  - Total NaN remaining: {X.isna().sum().sum()}")
        
        return X
    
    def _create_hp_sample(self):
        """Create a stratified sample for hyperparameter tuning if dataset is large."""
        n_samples = len(self.X)
        
        if n_samples > self.hp_sample_threshold:
            print(f"\n{'='*60}")
            print(f"DATASET SIZE: {n_samples} records (> {self.hp_sample_threshold} threshold)")
            print(f"Using stratified sample of {self.hp_sample_size} records for HP tuning")
            print(f"{'='*60}")
            
            X_hp, _, y_hp, _ = train_test_split(
                self.X, self.y,
                train_size=self.hp_sample_size,
                stratify=self.y,
                random_state=self.base_random_state
            )
            
            # Verify class distribution
            original_dist = np.bincount(self.y) / len(self.y)
            sample_dist = np.bincount(y_hp) / len(y_hp)
            
            print(f"\nClass distribution verification:")
            print(f"  Original: {dict(enumerate(original_dist.round(4)))}")
            print(f"  Sample:   {dict(enumerate(sample_dist.round(4)))}")
            
            return X_hp.reset_index(drop=True), y_hp
        else:
            print(f"\n{'='*60}")
            print(f"DATASET SIZE: {n_samples} records")
            print(f"Using full dataset for HP tuning and evaluation")
            print(f"{'='*60}")
            return self.X, self.y
    
    def _get_system_info(self):
        """Get system information for resource monitoring."""
        return {
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'total_memory': psutil.virtual_memory().total,
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': platform.python_version()
        }
    
    def get_model_size(self, model) -> int:
        """Calculate model size in bytes."""
        try:
            return len(pickle.dumps(model))
        except Exception:
            return 0
    
    def profile_memory_and_time(self, func, *args, **kwargs):
        """Profile memory usage and execution time of a function."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        tracemalloc.start()
        
        start_time = time.perf_counter()
        start_cpu = time.process_time()
        
        result = func(*args, **kwargs)
        
        end_cpu = time.process_time()
        end_time = time.perf_counter()
        
        current, peak_traced = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        final_memory = process.memory_info().rss / 1024 / 1024
        
        profile = {
            'wall_time': end_time - start_time,
            'cpu_time': end_cpu - start_cpu,
            'memory_peak_mb': peak_traced / 1024 / 1024,
            'memory_used_mb': current / 1024 / 1024,
            'memory_increment_mb': final_memory - initial_memory,
            'system_memory_before_mb': initial_memory,
            'system_memory_after_mb': final_memory
        }
        
        return result, profile
    
    def estimate_energy_consumption(self, cpu_time, memory_mb, model_name):
        """Estimate energy consumption based on CPU time and memory usage."""
        cpu_power = 65  # Typical TDP in Watts
        memory_power = (memory_mb / 8192) * 3
        
        cpu_energy = cpu_power * cpu_time
        memory_energy = memory_power * cpu_time
        total_energy = cpu_energy + memory_energy
        
        co2_kg = (total_energy / 3600000) * 0.5
        
        return {
            'total_energy_joules': total_energy,
            'cpu_energy_joules': cpu_energy,
            'memory_energy_joules': memory_energy,
            'energy_kwh': total_energy / 3600000,
            'co2_kg': co2_kg,
            'co2_grams': co2_kg * 1000
        }
    
    def create_linearboost_preprocessor(self, n_jobs=None):
        """Create preprocessor for LinearBoostClassifier."""
        jobs = n_jobs if n_jobs is not None else self.n_jobs
        return ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                make_column_selector(dtype_include=["object", "category"])),
            ],
            remainder="passthrough",
            n_jobs=jobs,
        )
    def create_logreg_preprocessor(self, n_jobs=None):
        """Preprocessor for LogisticRegression (scale numeric, OHE for categorical)."""
        jobs = n_jobs if n_jobs is not None else self.n_jobs

        numeric_selector = make_column_selector(
            dtype_include=["int64", "float64", "int32", "float32"]
        )
        categorical_selector = make_column_selector(
            dtype_include=["object", "category"]
        )
        return ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), numeric_selector),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_selector),
            ],
            remainder="drop",  # we handle both num + cat explicitly
            n_jobs=jobs,
        )

    # =========================================================================
    # HYPERPARAMETER OPTIMIZATION METHODS
    # =========================================================================
    
    def optimize_hyperparameters(self):
        """Perform hyperparameter optimization for all models."""
        print("\n" + "="*60)
        print(f"PHASE 1: HYPERPARAMETER OPTIMIZATION")
        print("="*60)
        print(f"Running {self.n_trials} trials per model...")
        print(f"HP tuning dataset size: {len(self.X_hp)} records")
        
        opt_seed = self.random_seeds[0]
        cv_opt = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=opt_seed)
        
        # LinearBoost-L (Linear kernel only)
        print("\n→ Optimizing LinearBoost-L (Linear kernel)...")
        lb_linear_study = self._optimize_linearboost_linear(cv_opt)
        self.best_params['LinearBoost-L'] = lb_linear_study.best_params
        print(f"  Best F1: {lb_linear_study.best_value:.4f}")
        
        # LinearBoost-K (Non-linear kernels)
        print("\n→ Optimizing LinearBoost-K (RBF/Poly/Sigmoid kernels)...")
        lb_kernel_study = self._optimize_linearboost_kernel(cv_opt)
        self.best_params['LinearBoost-K'] = lb_kernel_study.best_params
        print(f"  Best F1: {lb_kernel_study.best_value:.4f}")
        print(f"  Best kernel: {lb_kernel_study.best_params.get('kernel', 'N/A')}")
        
        # XGBoost
        print("\n→ Optimizing XGBoost...")
        xgboost_study = self._optimize_xgboost(cv_opt)
        self.best_params['XGBoost'] = xgboost_study.best_params
        print(f"  Best F1: {xgboost_study.best_value:.4f}")
        
        # LightGBM
        print("\n→ Optimizing LightGBM...")
        lightgbm_study = self._optimize_lightgbm(cv_opt)
        self.best_params['LightGBM'] = lightgbm_study.best_params
        print(f"  Best F1: {lightgbm_study.best_value:.4f}")
        
        # CatBoost
        print("\n→ Optimizing CatBoost...")
        catboost_study = self._optimize_catboost(cv_opt)
        self.best_params['CatBoost'] = catboost_study.best_params
        print(f"  Best F1: {catboost_study.best_value:.4f}")
        
                # Logistic Regression
        print("\n→ Optimizing LogisticRegression...")
        logreg_study = self._optimize_logistic_regression(cv_opt)
        self.best_params['LogisticRegression'] = logreg_study.best_params
        print(f"  Best F1: {logreg_study.best_value:.4f}")

        # Random Forest
        print("\n→ Optimizing RandomForest...")
        rf_study = self._optimize_random_forest(cv_opt)
        self.best_params['RandomForest'] = rf_study.best_params
        print(f"  Best F1: {rf_study.best_value:.4f}")

        # TabPFN (no tuning needed)
        if self.include_tabpfn:
            print("\n→ TabPFN: No hyperparameter tuning required")
            self.best_params['TabPFN'] = {}
        
        print("\n✓ Hyperparameter optimization complete!")
    
    def _optimize_linearboost_linear(self, cv):
        """Optimize LinearBoost with LINEAR kernel only."""
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 10, 500),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 1.0, log=True),
                "algorithm": trial.suggest_categorical("algorithm", ["SAMME", "SAMME.R"]),
                "scaler": trial.suggest_categorical(
                    "scaler", ["minmax", "robust", "quantile-uniform", "quantile-normal", "standard"]
                ),
                "kernel": "linear",  # FIXED to linear
            }
            
            preprocessor = self.create_linearboost_preprocessor(n_jobs=1)
            clf = LinearBoostClassifier(**params)
            pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
            
            try:
                scores = cross_validate(
                    pipe, self.X_hp, self.y_hp,
                    scoring=make_scorer(f1_score, average='weighted'),
                    cv=cv, n_jobs=1,
                    return_train_score=False
                )
                return scores['test_score'].mean()
            except Exception as e:
                return -np.inf
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
    
    def _optimize_linearboost_kernel(self, cv):
        """Optimize LinearBoost with NON-LINEAR kernels (RBF, Poly, Sigmoid)."""
        def objective(trial):
            kernel = trial.suggest_categorical("kernel", ["rbf", "poly", "sigmoid"])
            
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 10, 500),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 1.0, log=True),
                "algorithm": trial.suggest_categorical("algorithm", ["SAMME", "SAMME.R"]),
                "scaler": trial.suggest_categorical(
                    "scaler", ["minmax", "robust", "quantile-uniform", "quantile-normal", "standard"]
                ),
                "kernel": kernel,
                "gamma": trial.suggest_float("gamma", 1e-3, 10.0, log=True),
            }
            
            # Kernel-specific parameters
            if kernel == "poly":
                params["degree"] = trial.suggest_int("degree", 2, 5)
            if kernel in ["poly", "sigmoid"]:
                params["coef0"] = trial.suggest_float("coef0", 0.0, 1.0)
            
            preprocessor = self.create_linearboost_preprocessor(n_jobs=1)
            clf = LinearBoostClassifier(**params)
            pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
            
            try:
                scores = cross_validate(
                    pipe, self.X_hp, self.y_hp,
                    scoring=make_scorer(f1_score, average='weighted'),
                    cv=cv, n_jobs=1,
                    return_train_score=False
                )
                return scores['test_score'].mean()
            except Exception as e:
                return -np.inf
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
    
    def _optimize_xgboost(self, cv):
        """Optimize XGBoost hyperparameters."""
        def objective(trial):
            params = {
                "objective": "binary:logistic",
                "use_label_encoder": False,
                "n_estimators": trial.suggest_int("n_estimators", 20, 1000),
                "max_depth": trial.suggest_int("max_depth", 1, 20),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.7, log=True),
                "gamma": trial.suggest_float("gamma", 1e-8, 1.0, log=True),
                "min_child_weight": trial.suggest_int("min_child_weight", 1, 10),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 1.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 1.0, log=True),
                "enable_categorical": True,
                "eval_metric": "logloss",
                "n_jobs": self.n_jobs,
            }
            
            model = xgb.XGBClassifier(**params)
            scores = cross_validate(
                model, self.X_hp, self.y_hp,
                scoring=make_scorer(f1_score, average='weighted'),
                cv=cv, n_jobs=1,
                return_train_score=False
            )
            return scores['test_score'].mean()
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
    
    def _optimize_lightgbm(self, cv):
        """Optimize LightGBM hyperparameters."""
        def objective(trial):
            params = {
                "objective": "binary",
                "metric": "binary_logloss",
                "boosting_type": trial.suggest_categorical("boosting_type", ["gbdt", "dart", "goss"]),
                "num_leaves": trial.suggest_int("num_leaves", 2, 256),
                "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.3, log=True),
                "n_estimators": trial.suggest_int("n_estimators", 20, 1000),
                "max_depth": trial.suggest_int("max_depth", 1, 20),
                "min_child_samples": trial.suggest_int("min_child_samples", 1, 100),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
                "reg_alpha": trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
                "reg_lambda": trial.suggest_float("reg_lambda", 1e-8, 10.0, log=True),
                "min_split_gain": trial.suggest_float("min_split_gain", 1e-8, 1.0, log=True),
                "verbosity": -1,
                "n_jobs": self.n_jobs,
            }
            
            model = lgb.LGBMClassifier(**params)
            scores = cross_validate(
                model, self.X_hp, self.y_hp,
                scoring=make_scorer(f1_score, average='weighted'),
                cv=cv, n_jobs=1,
                return_train_score=False
            )
            return scores['test_score'].mean()
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
    
    def _optimize_catboost(self, cv):
        """Optimize CatBoost hyperparameters."""
        def objective(trial):
            params = {
                "iterations": trial.suggest_int("iterations", 50, 500),
                "depth": trial.suggest_int("depth", 1, 16),
                "learning_rate": trial.suggest_float("learning_rate", 1e-3, 0.5, log=True),
                "l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1e-8, 10.0, log=True),
                "random_strength": trial.suggest_float("random_strength", 1e-8, 10.0, log=True),
                "bagging_temperature": trial.suggest_float("bagging_temperature", 0.1, 10.0, log=True),
                "border_count": trial.suggest_int("border_count", 32, 255),
                "grow_policy": trial.suggest_categorical(
                    "grow_policy", ["SymmetricTree", "Depthwise", "Lossguide"]
                ),
                "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 1, 100),
                "rsm": trial.suggest_float("rsm", 0.1, 1.0),
                "loss_function": "Logloss",
                "eval_metric": "F1",
                "cat_features": self.categorical_cols,
                "verbose": 0,
                "thread_count": self.n_jobs,
            }
            
            model = CatBoostClassifier(**params)
            scores = cross_validate(
                model, self.X_hp, self.y_hp,
                scoring=make_scorer(f1_score, average='weighted'),
                cv=cv, n_jobs=1,
                return_train_score=False
            )
            return scores['test_score'].mean()
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
    def _optimize_logistic_regression(self, cv):
        """Optimize LogisticRegression hyperparameters (numerically stable)."""
        def objective(trial):
            params = {
                "C": trial.suggest_float("C", 1e-3, 1.0, log=True),  # smaller upper bound
                "fit_intercept": trial.suggest_categorical("fit_intercept", [True, False]),
                "class_weight": trial.suggest_categorical("class_weight", [None, "balanced"]),
                "solver": "lbfgs",
                "penalty": "l2",
                "max_iter": 2000,
                "n_jobs": 1,  # inner loop uses 1 core; outer CV handles parallelism
            }

            preprocessor = self.create_logreg_preprocessor(n_jobs=1)
            clf = LogisticRegression(**params)
            pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])

            try:
                scores = cross_validate(
                    pipe, self.X_hp, self.y_hp,
                    scoring=make_scorer(f1_score, average='weighted'),
                    cv=cv, n_jobs=1,
                    return_train_score=False
                )
                mean_score = scores['test_score'].mean()
                # guard against NaNs
                if not np.isfinite(mean_score):
                    return -np.inf
                return mean_score
            except Exception:
                return -np.inf

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
            
    def _optimize_random_forest(self, cv):
        """Optimize RandomForest hyperparameters."""
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 500),
                "max_depth": trial.suggest_int("max_depth", 2, 30),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 20),
                "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
                "bootstrap": trial.suggest_categorical("bootstrap", [True, False]),
                "class_weight": trial.suggest_categorical("class_weight", [None, "balanced"]),
                "n_jobs": self.n_jobs,
                "random_state": 42,
            }

            preprocessor = self.create_linearboost_preprocessor(n_jobs=1)
            clf = RandomForestClassifier(**params)
            pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])

            try:
                scores = cross_validate(
                    pipe, self.X_hp, self.y_hp,
                    scoring=make_scorer(f1_score, average='weighted'),
                    cv=cv, n_jobs=1,
                    return_train_score=False
                )
                return scores['test_score'].mean()
            except Exception:
                return -np.inf

        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study

    # =========================================================================
    # MODEL EVALUATION METHODS
    # =========================================================================
    
    def _get_models_config(self, n_jobs=1):
        """Get model configurations with best parameters."""
        models_config = {}
        
        # LinearBoost-L (Linear kernel)
        def get_linearboost_linear(seed):
            preprocessor = self.create_linearboost_preprocessor(n_jobs=n_jobs)
            params = self.best_params['LinearBoost-L'].copy()
            params['kernel'] = 'linear'  # Ensure linear
            clf = LinearBoostClassifier(**params)
            return Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
        models_config['LinearBoost-L'] = get_linearboost_linear
        
        # LinearBoost-K (Non-linear kernels)
        def get_linearboost_kernel(seed):
            preprocessor = self.create_linearboost_preprocessor(n_jobs=n_jobs)
            params = self.best_params['LinearBoost-K'].copy()
            clf = LinearBoostClassifier(**params)
            return Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
        models_config['LinearBoost-K'] = get_linearboost_kernel

        # Logistic Regression
        def get_logistic_regression(seed):
            preprocessor = self.create_logreg_preprocessor(n_jobs=n_jobs)
            params = self.best_params['LogisticRegression'].copy()
            params.update({
                "solver": "lbfgs",
                "penalty": "l2",
                "max_iter": 2000,
                "n_jobs": n_jobs,
                "random_state": seed,
            })
            clf = LogisticRegression(**params)
            return Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
        models_config['LogisticRegression'] = get_logistic_regression


        # Random Forest
        def get_random_forest(seed):
            preprocessor = self.create_linearboost_preprocessor(n_jobs=n_jobs)
            params = self.best_params['RandomForest'].copy()
            params.update({
                "n_jobs": n_jobs,
                "random_state": seed,
            })
            clf = RandomForestClassifier(**params)
            return Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
        models_config['RandomForest'] = get_random_forest

        
        # XGBoost
        def get_xgboost(seed):
            params = self.best_params['XGBoost'].copy()
            params.update({
                'objective': 'binary:logistic',
                'use_label_encoder': False,
                'enable_categorical': True,
                'eval_metric': 'logloss',
                'random_state': seed,
                'n_jobs': n_jobs
            })
            return xgb.XGBClassifier(**params)
        models_config['XGBoost'] = get_xgboost
        
        # LightGBM
        def get_lightgbm(seed):
            params = self.best_params['LightGBM'].copy()
            params.update({
                'objective': 'binary',
                'metric': 'binary_logloss',
                'verbosity': -1,
                'random_state': seed,
                'n_jobs': n_jobs
            })
            return lgb.LGBMClassifier(**params)
        models_config['LightGBM'] = get_lightgbm
        
        # CatBoost
        def get_catboost(seed):
            params = self.best_params['CatBoost'].copy()
            params.update({
                'loss_function': 'Logloss',
                'eval_metric': 'F1',
                'cat_features': self.categorical_cols,
                'verbose': 0,
                'random_state': seed,
                'thread_count': n_jobs if n_jobs != -1 else psutil.cpu_count(logical=True)
            })
            return CatBoostClassifier(**params)
        models_config['CatBoost'] = get_catboost
        
        # TabPFN
        if self.include_tabpfn:
            def get_tabpfn(seed):
                return TabPFNClassifier(device='cpu')
            models_config['TabPFN'] = get_tabpfn
        
        return models_config
    
    def evaluate_models_multiple_runs(self):
        """Evaluate all models using their best parameters across multiple runs."""
        print("\n" + "="*60)
        print("PHASE 2: MULTI-RUN EVALUATION (FULL DATASET)")
        print("="*60)
        print(f"Evaluating each model over {self.n_runs} runs × {self.cv_folds} folds")
        print(f"Evaluation dataset size: {len(self.X)} records")
        
        models_config = self._get_models_config(n_jobs=self.n_jobs)
        
        for model_name in self.model_names:
            if model_name not in models_config:
                continue

            print(f"\n→ Evaluating {model_name}...")

            model_getter = models_config[model_name]
            all_f1_scores = []
            all_roc_scores = []
            all_fit_times = []
            all_score_times = []

            # Special-case smaller evaluation for TabPFN
            #if model_name == "TabPFN":
                #local_n_runs = min(3, self.n_runs)     # e.g. 3 runs
                #local_cv_folds = min(5, self.cv_folds) # e.g. 5-fold CV
            #else:
            local_n_runs = self.n_runs
            local_cv_folds = self.cv_folds

            for run_idx, seed in enumerate(self.random_seeds[:local_n_runs]):
                if (run_idx + 1) % 1 == 0:
                    print(f"  Run {run_idx + 1}/{local_n_runs}...", end="\r")

                cv = StratifiedKFold(
                    n_splits=local_cv_folds, shuffle=True, random_state=seed
                )
                model = model_getter(seed)

                scoring = {
                    "f1": make_scorer(f1_score, average="weighted"),
                    "roc_auc": "roc_auc",
                }

                cv_results = cross_validate(
                    model, self.X, self.y,
                    scoring=scoring,
                    cv=cv,
                    n_jobs=1,
                    return_train_score=False,
                    return_estimator=False,
                )

                all_f1_scores.extend(cv_results["test_f1"])
                all_roc_scores.extend(cv_results["test_roc_auc"])
                all_fit_times.extend(cv_results["fit_time"])
                all_score_times.extend(cv_results["score_time"])
            
            print(f"  ✓ Completed {self.n_runs} runs")
            
            # Store detailed scores
            self.detailed_scores[model_name]['f1'] = np.array(all_f1_scores)
            self.detailed_scores[model_name]['roc_auc'] = np.array(all_roc_scores)
            self.detailed_scores[model_name]['fit_times'] = np.array(all_fit_times)
            
            # Profile resources
            if model_name == 'No-Model':#'TabPFN':
                print(f"  → Skipping resource profiling for {model_name}")
                self.resource_profiles[model_name] = {
                    'wall_time': np.mean(all_fit_times),
                    'cpu_time': np.mean(all_fit_times),
                    'memory_peak_mb': 0.0, 'memory_used_mb': 0.0,
                    'memory_increment_mb': 0.0, 'system_memory_before_mb': 0.0,
                    'system_memory_after_mb': 0.0, 'total_energy_joules': 0.0,
                    'cpu_energy_joules': 0.0, 'memory_energy_joules': 0.0,
                    'energy_kwh': 0.0, 'co2_kg': 0.0, 'co2_grams': 0.0,
                    'model_size_bytes': 0, 'model_size_mb': 0.0
                }
            else:
                print(f"  → Profiling resources for {model_name}...")
                model_for_profile = model_getter(self.base_random_state)
                
                def train_model():
                    return model_for_profile.fit(self.X, self.y)
                
                fitted_model, memory_profile = self.profile_memory_and_time(train_model)
                model_size = self.get_model_size(fitted_model)
                
                energy_profile = self.estimate_energy_consumption(
                    memory_profile['cpu_time'],
                    memory_profile['memory_peak_mb'],
                    model_name
                )
                
                self.resource_profiles[model_name] = {
                    **memory_profile,
                    **energy_profile,
                    'model_size_bytes': model_size,
                    'model_size_mb': model_size / (1024 * 1024)
                }
            
            # Store summary statistics
            self.results[model_name] = {
                'best_params': self.best_params[model_name],
                'f1_mean': np.mean(all_f1_scores),
                'f1_std': np.std(all_f1_scores),
                'f1_median': np.median(all_f1_scores),
                'f1_q25': np.percentile(all_f1_scores, 25),
                'f1_q75': np.percentile(all_f1_scores, 75),
                'roc_auc_mean': np.mean(all_roc_scores),
                'roc_auc_std': np.std(all_roc_scores),
                'roc_auc_median': np.median(all_roc_scores),
                'roc_auc_q25': np.percentile(all_roc_scores, 25),
                'roc_auc_q75': np.percentile(all_roc_scores, 75),
                'avg_fit_time': np.mean(all_fit_times),
                'std_fit_time': np.std(all_fit_times),
                'avg_score_time': np.mean(all_score_times), # Batch inference time
                'std_score_time': np.std(all_score_times),
                'n_evaluations': len(all_f1_scores),
                **self.resource_profiles[model_name]
            }
    
    def evaluate_models_single_core(self):
        """Evaluate all models on a single core for fair speed comparison."""
        print("\n" + "="*60)
        print("PHASE 2.5: SINGLE-CORE EVALUATION")
        print("="*60)
        
        n_single_core_runs = 5
        
        for model_name in self.model_names:
            if model_name not in self.results:
                continue
                
            if model_name == 'TabPFN':
                print(f"→ Skipping single-core evaluation for {model_name}")
                self.results[model_name]['single_core_wall_time'] = 0.0
                self.results[model_name]['single_core_cpu_time'] = 0.0
                self.results[model_name]['single_core_wall_time_std'] = 0.0
                continue
            
            print(f"→ Evaluating {model_name} on single core...")
            
            single_core_train_times = []
            inference_times_batch = []      # Time to predict full X
            inference_times_single = []     # Time to predict 1 row (averaged)
            
            for run in range(n_single_core_runs):
                models_config = self._get_models_config(n_jobs=1)
                model = models_config[model_name](self.base_random_state + run)
                
                # 1. Measure Training Time
                start_train = time.perf_counter()
                model.fit(self.X, self.y)
                single_core_train_times.append(time.perf_counter() - start_train)
                
                # 2. Measure Batch Inference (Throughput)
                # Predict the whole dataset
                start_batch = time.perf_counter()
                model.predict(self.X)
                batch_time = time.perf_counter() - start_batch
                inference_times_batch.append(batch_time)

                # 3. Measure Single-Row Latency (Simulated)
                # We predict single rows 1000 times to get a stable average
                # This simulates real-time API usage
                sample_row = self.X.iloc[[0]] # Take first row as DataFrame
                start_single = time.perf_counter()
                for _ in range(100): # Run 100 times to avg out overhead
                    model.predict(sample_row)
                end_single = time.perf_counter()
                
                # Time per single prediction in milliseconds
                avg_single_ms = ((end_single - start_single) / 100) * 1000
                inference_times_single.append(avg_single_ms)
            
            # Store results
            self.results[model_name]['single_core_wall_time'] = np.mean(single_core_train_times)
            self.results[model_name]['single_core_wall_time_std'] = np.std(single_core_train_times)
            
            # NEW METRICS
            self.results[model_name]['inference_batch_sec'] = np.mean(inference_times_batch)
            self.results[model_name]['inference_single_ms'] = np.mean(inference_times_single)
            
            print(f"  ✓ Train: {np.mean(single_core_train_times):.3f}s | "
                f"Infer (Full): {np.mean(inference_times_batch):.3f}s | "
                f"Latency: {np.mean(inference_times_single):.3f}ms/row")
    
    # =========================================================================
    # STATISTICAL ANALYSIS
    # =========================================================================
    
    def statistical_comparison(self):
        """Perform comprehensive statistical tests between all models."""
        print("\n" + "="*60)
        print("PHASE 3: STATISTICAL ANALYSIS")
        print("="*60)
        
        model_names = list(self.detailed_scores.keys())
        n_models = len(model_names)
        
        if n_models < 2:
            print("Need at least 2 models for comparison")
            return None
        
        results = {}
        
        # Prepare data matrices
        f1_scores = np.array([self.detailed_scores[name]['f1'] for name in model_names])
        roc_scores = np.array([self.detailed_scores[name]['roc_auc'] for name in model_names])
        
        # 1. Friedman Test
        print("\n→ Running Friedman tests...")
        
        f1_stat, f1_pvalue = stats.friedmanchisquare(*f1_scores)
        results['friedman_f1'] = {
            'statistic': f1_stat,
            'p_value': f1_pvalue,
            'significant': f1_pvalue < 0.05,
            'interpretation': 'Models differ significantly' if f1_pvalue < 0.05 else 'No significant difference'
        }
        
        roc_stat, roc_pvalue = stats.friedmanchisquare(*roc_scores)
        results['friedman_roc'] = {
            'statistic': roc_stat,
            'p_value': roc_pvalue,
            'significant': roc_pvalue < 0.05,
            'interpretation': 'Models differ significantly' if roc_pvalue < 0.05 else 'No significant difference'
        }
        
        # 2. Calculate average ranks
        print("→ Calculating average ranks...")
        
        f1_ranks = np.array([rankdata(-scores) for scores in f1_scores.T]).T
        roc_ranks = np.array([rankdata(-scores) for scores in roc_scores.T]).T
        
        avg_f1_ranks = np.mean(f1_ranks, axis=1)
        avg_roc_ranks = np.mean(roc_ranks, axis=1)
        
        results['average_ranks'] = {
            'f1': {name: rank for name, rank in zip(model_names, avg_f1_ranks)},
            'roc_auc': {name: rank for name, rank in zip(model_names, avg_roc_ranks)}
        }
        
        # Nemenyi critical difference
        k = n_models
        n = f1_scores.shape[1]
        q_alpha = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 7: 2.949, 8: 3.031}
        q = q_alpha.get(k, 3.031)
        cd = q * np.sqrt((k * (k + 1)) / (6 * n))
        results['nemenyi_critical_difference'] = cd
        
        # 3. Pairwise Wilcoxon tests
        print("→ Running pairwise Wilcoxon tests...")
        
        results['pairwise_f1'] = {}
        results['pairwise_roc'] = {}
        
        n_comparisons = (n_models * (n_models - 1)) // 2
        bonferroni_alpha = 0.05 / n_comparisons
        
        for i in range(n_models):
            for j in range(i+1, n_models):
                model1, model2 = model_names[i], model_names[j]
                pair_name = f"{model1}_vs_{model2}"
                
                # F1 comparison
                f1_stat, f1_p = stats.wilcoxon(
                    self.detailed_scores[model1]['f1'],
                    self.detailed_scores[model2]['f1'],
                    alternative='two-sided'
                )
                f1_diff = self.detailed_scores[model1]['f1'] - self.detailed_scores[model2]['f1']
                f1_effect_size = np.mean(np.sign(f1_diff))
                
                results['pairwise_f1'][pair_name] = {
                    'statistic': f1_stat,
                    'p_value': f1_p,
                    'significant_uncorrected': f1_p < 0.05,
                    'significant_bonferroni': f1_p < bonferroni_alpha,
                    'effect_size': f1_effect_size,
                    'better_model': model1 if np.mean(self.detailed_scores[model1]['f1']) > 
                                              np.mean(self.detailed_scores[model2]['f1']) else model2,
                    'rank_difference': abs(avg_f1_ranks[i] - avg_f1_ranks[j]),
                    'nemenyi_significant': abs(avg_f1_ranks[i] - avg_f1_ranks[j]) > cd
                }
                
                # ROC-AUC comparison
                roc_stat, roc_p = stats.wilcoxon(
                    self.detailed_scores[model1]['roc_auc'],
                    self.detailed_scores[model2]['roc_auc'],
                    alternative='two-sided'
                )
                roc_diff = self.detailed_scores[model1]['roc_auc'] - self.detailed_scores[model2]['roc_auc']
                roc_effect_size = np.mean(np.sign(roc_diff))
                
                results['pairwise_roc'][pair_name] = {
                    'statistic': roc_stat,
                    'p_value': roc_p,
                    'significant_uncorrected': roc_p < 0.05,
                    'significant_bonferroni': roc_p < bonferroni_alpha,
                    'effect_size': roc_effect_size,
                    'better_model': model1 if np.mean(self.detailed_scores[model1]['roc_auc']) > 
                                             np.mean(self.detailed_scores[model2]['roc_auc']) else model2,
                    'rank_difference': abs(avg_roc_ranks[i] - avg_roc_ranks[j]),
                    'nemenyi_significant': abs(avg_roc_ranks[i] - avg_roc_ranks[j]) > cd
                }
        
        results['statistical_power'] = {
            'n_samples_per_model': n,
            'bonferroni_corrected_alpha': bonferroni_alpha,
            'n_comparisons': n_comparisons,
            'interpretation': f"With {n} samples per model, we have high statistical power"
        }
        
        return results
    
    # =========================================================================
    # DETAILED PROFILING
    # =========================================================================
    
    def profile_best_model_detailed(self):
        """Perform detailed profiling of the best model based on F1 score."""
        print("\n" + "="*60)
        print("PHASE 4: DETAILED PROFILING")
        print("="*60)
        
        best_model_name = max(self.results.keys(), 
                             key=lambda k: self.results[k]['f1_mean'])
        
        print(f"\nBest model: {best_model_name}")
        print(f"F1 Score: {self.results[best_model_name]['f1_mean']:.4f}")
        
        print("\n→ Profiling scalability...")
        data_fractions = [0.1, 0.25, 0.5, 0.75, 1.0]
        scaling_profiles = []
        
        for fraction in data_fractions:
            try:
                n_samples = int(len(self.X) * fraction)
                if n_samples == 0:
                    n_samples = 1
                
                X_subset = self.X.iloc[:n_samples].copy()
                y_subset = self.y[:n_samples].copy()
                
                unique_classes = np.unique(y_subset)
                if len(unique_classes) < 2:
                    print(f"  {fraction*100:3.0f}% data: Skipped (insufficient class diversity)")
                    continue
                
                models_config = self._get_models_config(n_jobs=self.n_jobs)
                model_for_subset = models_config[best_model_name](self.base_random_state)
                
                def train_subset():
                    return model_for_subset.fit(X_subset, y_subset)
                
                _, profile = self.profile_memory_and_time(train_subset)
                profile['data_size'] = fraction
                profile['n_samples'] = n_samples
                scaling_profiles.append(profile)
                
                print(f"  {fraction*100:3.0f}% data: {profile['wall_time']:.3f}s, {profile['memory_peak_mb']:.1f}MB")
                
            except Exception as e:
                print(f"  {fraction*100:3.0f}% data: Error - {str(e)[:50]}...")
                continue
        
        detailed_profile = {
            'model_name': best_model_name,
            'scaling_profiles': scaling_profiles,
            'best_params': self.best_params[best_model_name]
        }
        
        return detailed_profile
    
    # =========================================================================
    # MAIN BENCHMARK RUNNER
    # =========================================================================
    
    def run_benchmark(self):
        """Run the complete benchmark pipeline."""
        print("\n" + "="*70)
        print("  LINEARBOOST DUAL-VARIANT BENCHMARK")
        print("  LinearBoost-L (Linear) vs LinearBoost-K (Kernel) vs Competitors")
        print("="*70)
        
        self.optimize_hyperparameters()
        self.evaluate_models_multiple_runs()
        self.evaluate_models_single_core()
        stat_results = self.statistical_comparison()
        detailed_profile = self.profile_best_model_detailed()
        
        return self.results, stat_results, detailed_profile
    
    def print_results(self, results, stat_results):
        """Print benchmark results summary."""
        print("\n" + "="*70)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*70)
        
        # Dataset info
        print(f"\nDataset Configuration:")
        print(f"  - Total records: {len(self.X)}")
        print(f"  - HP tuning records: {len(self.X_hp)}")
        print(f"  - Features: {self.X.shape[1]}")
        
        df = pd.DataFrame(results).T
        
        # Performance Summary
        print(f"\n### Performance Metrics ({self.n_runs} runs × {self.cv_folds} folds)")
        print("-" * 90)
        
        perf_data = []
        for model in df.index:
            perf_data.append({
                'Model': model,
                'F1 Mean±Std': f"{df.loc[model, 'f1_mean']:.4f}±{df.loc[model, 'f1_std']:.4f}",
                'ROC Mean±Std': f"{df.loc[model, 'roc_auc_mean']:.4f}±{df.loc[model, 'roc_auc_std']:.4f}",
                'Train Time (s)': f"{df.loc[model, 'single_core_wall_time']:.4f}",#
                'Latency (ms)': f"{df.loc[model, 'inference_single_ms']:.3f}",
                'Size (MB)': f"{df.loc[model, 'model_size_mb']:.3f}",
            })
        
        perf_df = pd.DataFrame(perf_data)
        print(perf_df.to_string(index=False))
        
        # Rank Summary
        if stat_results and 'average_ranks' in stat_results:
            print("\n### Average Ranks (lower is better)")
            print("-" * 50)
            f1_ranks = stat_results['average_ranks']['f1']
            roc_ranks = stat_results['average_ranks']['roc_auc']
            
            for model in f1_ranks:
                print(f"  {model:15s}  F1: {f1_ranks[model]:.2f}  ROC: {roc_ranks[model]:.2f}")
        
        # LinearBoost comparison
        print("\n### LinearBoost Variant Comparison")
        print("-" * 50)
        if 'LinearBoost-L' in df.index and 'LinearBoost-K' in df.index:
            lb_l = df.loc['LinearBoost-L']
            lb_k = df.loc['LinearBoost-K']
            
            print(f"  {'Metric':<20} {'LinearBoost-L':>15} {'LinearBoost-K':>15} {'Winner':>12}")
            print(f"  {'-'*62}")
            
            # F1
            f1_winner = 'L' if lb_l['f1_mean'] > lb_k['f1_mean'] else 'K'
            print(f"  {'F1 Score':<20} {lb_l['f1_mean']:>15.4f} {lb_k['f1_mean']:>15.4f} {f1_winner:>12}")
            
            # ROC
            roc_winner = 'L' if lb_l['roc_auc_mean'] > lb_k['roc_auc_mean'] else 'K'
            print(f"  {'ROC-AUC':<20} {lb_l['roc_auc_mean']:>15.4f} {lb_k['roc_auc_mean']:>15.4f} {roc_winner:>12}")
            
            # Speed
            speed_winner = 'L' if lb_l['single_core_wall_time'] < lb_k['single_core_wall_time'] else 'K'
            speedup = lb_k['single_core_wall_time'] / lb_l['single_core_wall_time'] if lb_l['single_core_wall_time'] > 0 else 0
            print(f"  {'Train Time (s)':<20} {lb_l['single_core_wall_time']:>15.4f} {lb_k['single_core_wall_time']:>15.4f} {speed_winner:>12}")
            
            # Size
            size_winner = 'L' if lb_l['model_size_mb'] < lb_k['model_size_mb'] else 'K'
            size_ratio = lb_k['model_size_mb'] / lb_l['model_size_mb'] if lb_l['model_size_mb'] > 0 else 0
            print(f"  {'Model Size (MB)':<20} {lb_l['model_size_mb']:>15.3f} {lb_k['model_size_mb']:>15.3f} {size_winner:>12}")
            
            print(f"\n  Summary:")
            print(f"    - LinearBoost-L is {speedup:.1f}x faster than LinearBoost-K")
            print(f"    - LinearBoost-L is {size_ratio:.1f}x smaller than LinearBoost-K")
        
        return df
    
    def save_results(self, results, stat_results, filename_prefix="benchmark_dual_lb"):
        """Save results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("benchmark_results")
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / f"{filename_prefix}_{timestamp}.json"
        
        def default_serializer(obj):
            if isinstance(obj, (np.integer, np.floating, np.bool_)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Timedelta):
                return str(obj)
            return str(obj)
        
        results_with_meta = {
            'metadata': {
                'total_records': len(self.X),
                'n_features': self.X.shape[1],
                'hp_tuning_records': len(self.X_hp),
                'hp_sample_threshold': self.hp_sample_threshold,
                'hp_sample_size': self.hp_sample_size,
                'used_sampling': len(self.X_hp) < len(self.X),
                'n_trials': self.n_trials,
                'cv_folds': self.cv_folds,
                'n_runs': self.n_runs,
                'models_compared': list(results.keys()),
                'timestamp': timestamp
            },
            'results': results,
            'statistical_results': stat_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(results_with_meta, f, indent=2, default=default_serializer)
        
        print(f"\nResults saved to {results_file}")
        return results_file
    
    def plot_results(self, results, stat_results, detailed_profile=None):
        """Generate visualization plots."""
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            plt.style.use('seaborn-v0_8-whitegrid')
            
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            
            model_names = list(self.detailed_scores.keys())
            colors = plt.cm.Set2(np.linspace(0, 1, len(model_names)))
            
            # Highlight LinearBoost variants
            color_map = {}
            for i, name in enumerate(model_names):
                if 'LinearBoost-L' in name:
                    color_map[name] = '#2ecc71'  # Green
                elif 'LinearBoost-K' in name:
                    color_map[name] = '#3498db'  # Blue
                else:
                    color_map[name] = colors[i]
            
            # 1. F1 Score Distribution
            ax1 = axes[0, 0]
            f1_data = [self.detailed_scores[name]['f1'] for name in model_names]
            bp1 = ax1.boxplot(f1_data, labels=model_names, patch_artist=True)
            for patch, name in zip(bp1['boxes'], model_names):
                patch.set_facecolor(color_map[name])
            ax1.set_title('F1 Score Distribution')
            ax1.set_ylabel('F1 Score')
            ax1.tick_params(axis='x', rotation=45)
            
            # 2. ROC-AUC Distribution
            ax2 = axes[0, 1]
            roc_data = [self.detailed_scores[name]['roc_auc'] for name in model_names]
            bp2 = ax2.boxplot(roc_data, labels=model_names, patch_artist=True)
            for patch, name in zip(bp2['boxes'], model_names):
                patch.set_facecolor(color_map[name])
            ax2.set_title('ROC-AUC Distribution')
            ax2.set_ylabel('ROC-AUC')
            ax2.tick_params(axis='x', rotation=45)
            
            # 3. Training Time Comparison
            ax3 = axes[1, 0]
            times = [results[name]['single_core_wall_time'] for name in model_names]
            bars = ax3.bar(model_names, times, color=[color_map[n] for n in model_names])
            ax3.set_title('Single-Core Training Time')
            ax3.set_ylabel('Time (seconds)')
            ax3.tick_params(axis='x', rotation=45)
            
            # 4. Model Size Comparison
            ax4 = axes[1, 1]
            sizes = [results[name]['model_size_mb'] for name in model_names]
            bars = ax4.bar(model_names, sizes, color=[color_map[n] for n in model_names])
            ax4.set_title('Model Size')
            ax4.set_ylabel('Size (MB)')
            ax4.tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            
            # Save plot
            results_dir = Path("benchmark_results")
            results_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_file = results_dir / f"benchmark_dual_lb_plot_{timestamp}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            print(f"Plot saved to {plot_file}")
            
            plt.close()
            
        except ImportError:
            print("\n[Warning] matplotlib/seaborn not available for plotting")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

# =============================================================================
# OPENML DATASET ITERATOR & MAIN EXECUTION
# =============================================================================

def get_binary_openml_datasets(n_datasets=5, min_samples=500, max_samples=10000):
    """
    Fetches metadata for active binary classification datasets from OpenML 
    that meet size constraints.
    """
    print(f"Querying OpenML for binary datasets ({min_samples} < samples < {max_samples})...")
    
    # List datasets with specific filters
    # NumberOfClasses=2 ensures binary classification
    datasets_df = openml.datasets.list_datasets(
        output_format="dataframe",
        status="active",
        number_classes=2,
        number_missing_values=0  # Optional: skip messy data for smoother benchmarking
    )
    
    # Filter by size
    mask = (datasets_df['NumberOfInstances'] >= min_samples) & \
           (datasets_df['NumberOfInstances'] <= max_samples)
    filtered_df = datasets_df[mask]
    
    # Sort by size or pick random
    filtered_df = filtered_df.sort_values(by='NumberOfInstances', ascending=True)
    
    # Select top N
    selected_datasets = filtered_df.head(n_datasets)
    
    dataset_ids = selected_datasets['did'].tolist()
    dataset_names = selected_datasets['name'].tolist()
    
    print(f"Found {len(dataset_ids)} datasets: {list(zip(dataset_ids, dataset_names))}")
    return list(zip(dataset_ids, dataset_names))

def process_openml_data(dataset_id):
    """
    Downloads and formats a specific OpenML dataset for the benchmark.
    """
    dataset = openml.datasets.get_dataset(dataset_id)
    
    # Get the data (handle categorical features automatically)
    X, y, categorical_indicator, attribute_names = dataset.get_data(
        dataset_format="dataframe",
        target=dataset.default_target_attribute
    )
    
    # Identify categorical columns based on OpenML metadata
    categorical_cols = [
        attr for attr, is_cat in zip(attribute_names, categorical_indicator) 
        if is_cat and attr in X.columns
    ]
    
    # 1. Handle Target Encoding (Ensure binary 0/1)
    # OpenML targets are often strings (e.g., 'P', 'N'). We force them to 0/1.
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Ensure it's strictly binary
    if len(le.classes_) != 2:
        raise ValueError(f"Dataset {dataset_id} is not binary. Found classes: {le.classes_}")
        
    return X, y_encoded, categorical_cols

if __name__ == "__main__":
    # Configuration for OpenML fetching
    N_DATASETS_TO_RUN = 10       # How many datasets to iterate over
    MIN_SAMPLES = 1000          # Minimum rows
    MAX_SAMPLES = 20000         # Maximum rows (keep reasonable for benchmark speed)
    
    # 1. Fetch Dataset IDs
    try:
        target_datasets = get_binary_openml_datasets(
            n_datasets=N_DATASETS_TO_RUN, 
            min_samples=MIN_SAMPLES, 
            max_samples=MAX_SAMPLES
        )
    except Exception as e:
        print(f"Failed to query OpenML: {e}")
        target_datasets = []

    # Store master results across all datasets
    master_results = []

    # 2. Iterate over Datasets
    for ds_id, ds_name in target_datasets:
        print("\n" + "#"*80)
        print(f"  PROCESSING DATASET: {ds_name} (ID: {ds_id})")
        print("#"*80)
        
        try:
            # Load Data
            X, y, categorical_cols = process_openml_data(ds_id)
            
            print(f"Shape: {X.shape}")
            print(f"Categorical Features: {len(categorical_cols)}")
            print(f"Class Balance: {np.bincount(y)}")

            # Initialize Benchmark
            benchmark = ModelBenchmark(
                X=X,
                y=y,
                categorical_cols=categorical_cols,
                n_trials=200,              # Reduced trials for speed during iteration
                cv_folds=5,               # Reduced folds for speed
                n_runs=30,                 # Reduced runs for speed
                n_jobs=8,
                hp_sample_threshold=2000,
                hp_sample_size=1000,
                include_tabpfn=False      # Optional
            )
            
            # Run Benchmark
            results, stat_results, detailed_profile = benchmark.run_benchmark()
            
            # Print and Save individual dataset results
            benchmark.print_results(results, stat_results)
            filename = benchmark.save_results(results, stat_results, filename_prefix=f"bench_openml_{ds_id}_{ds_name}")
            
            # Aggregate for Master Summary
            for model_name, metrics in results.items():
                master_results.append({
                    'Dataset_ID': ds_id,
                    'Dataset_Name': ds_name,
                    'Model': model_name,
                    'F1_Mean': metrics.get('f1_mean', 0),
                    'ROC_AUC_Mean': metrics.get('roc_auc_mean', 0),
                    'Time_Train_Sec': metrics.get('single_core_wall_time', 0),
                    'Model_Size_MB': metrics.get('model_size_mb', 0)
                })

            # Optional: Clear memory
            del X, y, benchmark
            import gc
            gc.collect()

        except Exception as e:
            print(f"\n[ERROR] Failed to benchmark dataset {ds_name} (ID: {ds_id})")
            print(f"Reason: {e}")
            continue

    # 3. Save Master Summary
    if master_results:
        summary_df = pd.DataFrame(master_results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_path = f"benchmark_results/MASTER_SUMMARY_{timestamp}.csv"
        summary_df.to_csv(summary_path, index=False)
        print("\n" + "="*80)
        print(f"ALL BENCHMARKS COMPLETE.")
        print(f"Master summary saved to: {summary_path}")
        print("="*80)