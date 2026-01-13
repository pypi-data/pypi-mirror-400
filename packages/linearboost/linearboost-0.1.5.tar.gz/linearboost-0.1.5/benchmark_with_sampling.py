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

# Import the models
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
# Assuming source is available, otherwise replace with standard import
try:
    from src.linearboost.linear_boost import LinearBoostClassifier
except ImportError:
    # Fallback or placeholder if specific src path isn't found in this context
    print("Warning: LinearBoostClassifier not found in src.linearboost. Make sure path is correct.") 
    # Mocking for syntax validity if user copies this without the file
    class LinearBoostClassifier:
        def __init__(self, **kwargs): pass
        def fit(self, X, y): return self

# Import TabPFN
TABPFN_AVAILABLE = False
TABPFN_ERROR_MSG = ""
try:
    from tabpfn import TabPFNClassifier
    # Try to instantiate to check if model can be downloaded
    # This will fail if HuggingFace authentication is not set up
    _test_tabpfn = TabPFNClassifier(device='cpu')
    del _test_tabpfn
    TABPFN_AVAILABLE = False
except ImportError:
    TABPFN_ERROR_MSG = "TabPFN not installed. Install with: pip install tabpfn"
    print(f"Warning: {TABPFN_ERROR_MSG}")
except Exception as e:
    # Catches HuggingFace authentication errors, download errors, etc.
    error_str = str(e)
    if "401" in error_str or "Unauthorized" in error_str or "GatedRepoError" in error_str:
        TABPFN_ERROR_MSG = ("TabPFN requires HuggingFace authentication. "
                           "Run 'huggingface-cli login' or set HF_TOKEN environment variable. "
                           "You also need to accept the model license at: "
                           "https://huggingface.co/Prior-Labs/tabpfn_2_5")
    else:
        TABPFN_ERROR_MSG = f"TabPFN initialization failed: {error_str[:100]}"
    print(f"Warning: {TABPFN_ERROR_MSG}")
    TABPFN_AVAILABLE = False

# Suppress Optuna logging
optuna.logging.set_verbosity(optuna.logging.WARNING)


class ModelBenchmark:
    """
    Comprehensive benchmarking framework for ML models with statistical testing,
    memory profiling, and energy consumption estimation.
    """
    
    def __init__(self, X, y, categorical_cols, n_trials=200, cv_folds=10, 
                 n_runs=30, base_random_state=42, n_jobs=4,
                 hp_sample_threshold=2000, hp_sample_size=1500):
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
            Number of threads allowed per model. 
            Reduced default (4) to prevent OS freezing on large datasets.
        hp_sample_threshold : int
            If dataset has more records than this, use stratified sampling for HP tuning
        hp_sample_size : int
            Number of records to use for HP tuning when sampling is applied
        """
        # Preprocess data to handle NaN in categorical columns (required for CatBoost)
        self.X = self._preprocess_data(X.copy(), categorical_cols)
        self.y = y
        self.categorical_cols = categorical_cols
        self.n_trials = n_trials
        self.cv_folds = cv_folds
        self.n_runs = n_runs
        self.base_random_state = base_random_state
        self.n_jobs = n_jobs  # Resource Cap
        
        # Stratified sampling parameters for hyperparameter tuning
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
        
        # System info for energy estimation
        self.system_info = self._get_system_info()
    
    def _preprocess_data(self, X, categorical_cols):
        """
        Preprocess data to handle NaN values properly for all models.
        
        CatBoost requires categorical features to be strings or integers, not NaN.
        This method converts NaN values in categorical columns to the string "missing".
        
        Parameters
        ----------
        X : pd.DataFrame
            Feature matrix
        categorical_cols : list
            List of categorical column names
            
        Returns
        -------
        pd.DataFrame
            Preprocessed feature matrix
        """
        X = X.copy()
        
        # Handle NaN in categorical columns
        for col in categorical_cols:
            if col in X.columns:
                # Convert to string type and fill NaN with "missing"
                X[col] = X[col].astype(str).replace('nan', 'missing').replace('None', 'missing')
                X[col] = X[col].astype('category')
        
        # Also check for any object columns that might have been missed
        object_cols = X.select_dtypes(include=['object', 'category']).columns.tolist()
        for col in object_cols:
            if X[col].isna().any():
                X[col] = X[col].fillna('missing')
            # Ensure proper string conversion for any remaining nan-like values
            X[col] = X[col].astype(str).replace('nan', 'missing').replace('None', 'missing')
            X[col] = X[col].astype('category')
        
        # Handle NaN in numeric columns (fill with median)
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
        """
        Create a stratified sample for hyperparameter tuning if dataset is large.
        
        Returns
        -------
        X_hp : pd.DataFrame
            Feature matrix for HP tuning (sampled or full)
        y_hp : np.ndarray
            Target vector for HP tuning (sampled or full)
        """
        n_samples = len(self.X)
        
        if n_samples > self.hp_sample_threshold:
            print(f"\n{'='*60}")
            print(f"DATASET SIZE: {n_samples} records (> {self.hp_sample_threshold} threshold)")
            print(f"Using stratified sample of {self.hp_sample_size} records for HP tuning")
            print(f"Full dataset will be used for final benchmarking")
            print(f"{'='*60}")
            
            # Calculate the fraction to keep
            sample_fraction = self.hp_sample_size / n_samples
            
            # Use train_test_split for stratified sampling
            # We keep the "train" portion as our sample
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
            print(f"  Original dataset: {dict(enumerate(original_dist.round(4)))}")
            print(f"  HP tuning sample: {dict(enumerate(sample_dist.round(4)))}")
            
            return X_hp.reset_index(drop=True), y_hp
        else:
            print(f"\n{'='*60}")
            print(f"DATASET SIZE: {n_samples} records (<= {self.hp_sample_threshold} threshold)")
            print(f"Using full dataset for both HP tuning and benchmarking")
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
        # Get initial memory state
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Start memory tracing
        tracemalloc.start()
        
        # Monitor peak memory during execution
        
        # Execute function with timing
        start_time = time.perf_counter()
        start_cpu = time.process_time()
        
        result = func(*args, **kwargs)
        
        end_cpu = time.process_time()
        end_time = time.perf_counter()
        
        # Get memory statistics
        current, peak_traced = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        profile = {
            'wall_time': end_time - start_time,
            'cpu_time': end_cpu - start_cpu,
            'memory_peak_mb': peak_traced / 1024 / 1024,
            'memory_used_mb': (current / 1024 / 1024),
            'memory_increment_mb': final_memory - initial_memory,
            'system_memory_before_mb': initial_memory,
            'system_memory_after_mb': final_memory
        }
        
        return result, profile
    
    def estimate_energy_consumption(self, cpu_time, memory_mb, model_name):
        """Estimate energy consumption based on CPU time and memory usage."""
        # Base power consumption estimates (in Watts)
        cpu_power = 65  # Typical TDP for modern CPUs
        memory_power = (memory_mb / 8192) * 3  # ~3W per 8GB
        
        # Energy = Power × Time
        cpu_energy = cpu_power * cpu_time  # Joules
        memory_energy = memory_power * cpu_time  # Joules
        total_energy = cpu_energy + memory_energy
        
        # CO2 emissions (using global average of 0.5 kg CO2/kWh)
        co2_kg = (total_energy / 3600000) * 0.5  # Convert J to kWh, then to CO2
        
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
        # Use safe n_jobs if not specified
        jobs = n_jobs if n_jobs is not None else self.n_jobs
        return ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                make_column_selector(dtype_include=["object", "category"])),
            ],
            remainder="passthrough",
            n_jobs=jobs,
        )    
    
    def optimize_hyperparameters(self):
        """
        Perform hyperparameter optimization once for each model.
        Uses stratified sample if dataset is large.
        """
        print("\n" + "="*60)
        print(f"PHASE 1: HYPERPARAMETER OPTIMIZATION (Threads per model capped at {self.n_jobs})")
        print("="*60)
        print(f"Running {self.n_trials} trials per model...")
        print(f"HP tuning dataset size: {len(self.X_hp)} records")
        
        # Use first random seed for optimization
        opt_seed = self.random_seeds[0]
        cv_opt = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=opt_seed)
        
        # Optimize LinearBoost
        print("\n→ Optimizing LinearBoostClassifier...")
        linearboost_study = self._optimize_linearboost(cv_opt)
        self.best_params['LinearBoost'] = linearboost_study.best_params
        
        # Optimize XGBoost
        print("\n→ Optimizing XGBoost...")
        xgboost_study = self._optimize_xgboost(cv_opt)
        self.best_params['XGBoost'] = xgboost_study.best_params
        
        # Optimize LightGBM
        print("\n→ Optimizing LightGBM...")
        lightgbm_study = self._optimize_lightgbm(cv_opt)
        self.best_params['LightGBM'] = lightgbm_study.best_params
        
        # Optimize CatBoost
        print("\n→ Optimizing CatBoost...")
        catboost_study = self._optimize_catboost(cv_opt)
        self.best_params['CatBoost'] = catboost_study.best_params
        
        # TabPFN - No hyperparameter tuning needed
        if TABPFN_AVAILABLE:
            print("\n→ TabPFN: No hyperparameter tuning required (using default settings)")
            self.best_params['TabPFN'] = {}
        else:
            print(f"\n→ TabPFN: SKIPPED - {TABPFN_ERROR_MSG}")
        
        print("\n✓ Hyperparameter optimization complete!")
        
    def _optimize_linearboost(self, cv):
        def objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 10, 500),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 1.0, log=True),
                "algorithm": trial.suggest_categorical("algorithm", ["SAMME", "SAMME.R"]),
                "scaler": trial.suggest_categorical(
                    "scaler", ["minmax", "robust", "quantile-uniform", "quantile-normal", "standard"]
                ),
                "kernel": trial.suggest_categorical("kernel", ["linear", "rbf", "poly", "sigmoid"]),
            }
            
            if params["kernel"] != "linear":
                params["gamma"] = trial.suggest_float("gamma", 1e-3, 10.0, log=True)
            if params["kernel"] == "poly":
                params["degree"] = trial.suggest_int("degree", 2, 5)
            if params["kernel"] in ["poly", "sigmoid"]:
                params["coef0"] = trial.suggest_float("coef0", 0.0, 1.0)
            
            # Use 1 job for preprocessing during optimization to avoid contention
            preprocessor = self.create_linearboost_preprocessor(n_jobs=1)
            clf = LinearBoostClassifier(**params)
            pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
            
            try:
                # Use HP sample (self.X_hp, self.y_hp) for optimization
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
    
    def _optimize_xgboost(self, cv):
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
            # Use HP sample for optimization
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
            # Use HP sample for optimization
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
            # Use HP sample for optimization
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
    
    def evaluate_models_multiple_runs(self):
        """
        Evaluate all models using their best parameters across multiple runs.
        Uses the FULL dataset for evaluation.
        """
        print("\n" + "="*60)
        print("PHASE 2: MULTI-RUN EVALUATION (FULL DATASET)")
        print("="*60)
        print(f"Evaluating each model over {self.n_runs} runs × {self.cv_folds} folds")
        print(f"Evaluation dataset size: {len(self.X)} records (FULL)")
        print(f"NOTE: Cross-validation is running SEQUENTIALLY (n_jobs=1) to prevent OS freeze.")
        print(f"      Models are limited to {self.n_jobs} threads each.")
        
        # Pass the safe n_jobs cap here
        models_config = self._get_models_config(n_jobs=self.n_jobs)
        
        for model_name, model_getter in models_config.items():
            print(f"\n→ Evaluating {model_name}...")
            
            all_f1_scores = []
            all_roc_scores = []
            all_fit_times = []
            
            # Progress tracking
            for run_idx, seed in enumerate(self.random_seeds):
                if (run_idx + 1) % 5 == 0:
                    print(f"  Run {run_idx + 1}/{self.n_runs}...", end='\r')
                
                # Create CV splitter with different seed for each run
                cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=seed)
                
                # Get model with best parameters
                model = model_getter(seed)
                
                # Evaluate
                scoring = {
                    'f1': make_scorer(f1_score, average='weighted'),
                    'roc_auc': 'roc_auc',
                }
                
                # Use FULL dataset (self.X, self.y) for evaluation
                cv_results = cross_validate(
                    model, self.X, self.y,
                    scoring=scoring,
                    cv=cv,
                    n_jobs=1,
                    return_train_score=False,
                    return_estimator=False
                )
                
                # Store results from this run
                all_f1_scores.extend(cv_results['test_f1'])
                all_roc_scores.extend(cv_results['test_roc_auc'])
                all_fit_times.extend(cv_results['fit_time'])
            
            print(f"  ✓ Completed {self.n_runs} runs")
            
            # Store all scores for this model
            self.detailed_scores[model_name]['f1'] = np.array(all_f1_scores)
            self.detailed_scores[model_name]['roc_auc'] = np.array(all_roc_scores)
            self.detailed_scores[model_name]['fit_times'] = np.array(all_fit_times)
            
            # Profile memory and resources for the best model
            if model_name == 'TabPFN':
                print(f"  → Skipping resource profiling for {model_name} (CPU-intensive)")
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
                    # Profile on FULL dataset
                    return model_for_profile.fit(self.X, self.y)
                
                fitted_model, memory_profile = self.profile_memory_and_time(train_model)
                model_size = self.get_model_size(fitted_model)
                
                # Estimate energy consumption
                energy_profile = self.estimate_energy_consumption(
                    memory_profile['cpu_time'],
                    memory_profile['memory_peak_mb'],
                    model_name
                )
                
                # Store resource profiles
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
                'n_evaluations': len(all_f1_scores),
                **self.resource_profiles[model_name]
            }
                
    def evaluate_models_single_core(self):
        """Evaluate all models on a single core to measure algorithmic efficiency."""
        print("\n" + "="*60)
        print("PHASE 2.5: SINGLE-CORE EVALUATION (FULL DATASET)")
        print("="*60)
        
        n_single_core_runs = 5
        
        for model_name in self.results.keys():
            if model_name == 'TabPFN':
                print(f"→ Skipping single-core evaluation for {model_name}")
                self.results[model_name]['single_core_wall_time'] = 0.0
                self.results[model_name]['single_core_cpu_time'] = 0.0
                self.results[model_name]['single_core_wall_time_std'] = 0.0
                continue
            
            print(f"→ Evaluating {model_name} on a single core...")
            
            single_core_times = []
            single_core_cpu_times = []
            
            for run in range(n_single_core_runs):
                models_config = self._get_models_config(n_jobs=1)
                model = models_config[model_name](self.base_random_state + run)
                
                def train_single_core():
                    # Train on FULL dataset
                    model.fit(self.X, self.y)
                
                _, profile = self.profile_memory_and_time(train_single_core)
                single_core_times.append(profile['wall_time'])
                single_core_cpu_times.append(profile['cpu_time'])
            
            # Store average times
            self.results[model_name]['single_core_wall_time'] = np.mean(single_core_times)
            self.results[model_name]['single_core_cpu_time'] = np.mean(single_core_cpu_times)
            self.results[model_name]['single_core_wall_time_std'] = np.std(single_core_times)
            
            print(f"  ✓ Single-core wall time: {np.mean(single_core_times):.3f}±{np.std(single_core_times):.3f}s")

    def _get_models_config(self, n_jobs=1):
        """Get model configurations with best parameters."""
        models_config = {}
        
        # LinearBoost
        def get_linearboost(seed):
            preprocessor = self.create_linearboost_preprocessor(n_jobs=n_jobs)
            clf = LinearBoostClassifier(**self.best_params['LinearBoost'])
            pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
            return pipe
        models_config['LinearBoost'] = get_linearboost
        
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
                # Safe thread count if n_jobs is -1 (defaults to all cores)
                'thread_count': n_jobs if n_jobs != -1 else psutil.cpu_count(logical=True)
            })
            return CatBoostClassifier(**params)
        models_config['CatBoost'] = get_catboost
        
        # TabPFN
        if TABPFN_AVAILABLE:
            def get_tabpfn(seed):
                return TabPFNClassifier(device='cpu')
            models_config['TabPFN'] = get_tabpfn
        
        return models_config
    
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
        
        # 1. Friedman Test
        print("\n→ Running Friedman tests...")
        
        # Prepare data matrices
        f1_scores = np.array([self.detailed_scores[name]['f1'] for name in model_names])
        roc_scores = np.array([self.detailed_scores[name]['roc_auc'] for name in model_names])
        
        # Friedman test for F1
        f1_stat, f1_pvalue = stats.friedmanchisquare(*f1_scores)
        results['friedman_f1'] = {
            'statistic': f1_stat,
            'p_value': f1_pvalue,
            'significant': f1_pvalue < 0.05,
            'interpretation': 'Models differ significantly' if f1_pvalue < 0.05 else 'No significant difference'
        }
        
        # Friedman test for ROC-AUC
        roc_stat, roc_pvalue = stats.friedmanchisquare(*roc_scores)
        results['friedman_roc'] = {
            'statistic': roc_stat,
            'p_value': roc_pvalue,
            'significant': roc_pvalue < 0.05,
            'interpretation': 'Models differ significantly' if roc_pvalue < 0.05 else 'No significant difference'
        }
        
        # 2. Post-hoc Nemenyi Test
        print("→ Running post-hoc Nemenyi tests...")
        
        # Calculate average ranks
        f1_ranks = np.array([rankdata(-scores) for scores in f1_scores.T]).T
        roc_ranks = np.array([rankdata(-scores) for scores in roc_scores.T]).T
        
        avg_f1_ranks = np.mean(f1_ranks, axis=1)
        avg_roc_ranks = np.mean(roc_ranks, axis=1)
        
        results['average_ranks'] = {
            'f1': {name: rank for name, rank in zip(model_names, avg_f1_ranks)},
            'roc_auc': {name: rank for name, rank in zip(model_names, avg_roc_ranks)}
        }
        
        # Critical difference for Nemenyi test
        k = n_models
        n = f1_scores.shape[1]
        q_alpha = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850}
        q = q_alpha.get(k, 2.850)
        cd = q * np.sqrt((k * (k + 1)) / (6 * n))
        results['nemenyi_critical_difference'] = cd
        
        # 3. Pairwise Comparisons
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
            'interpretation': f"With {n} samples per model, we have high statistical power"
        }
        
        return results
    
    def profile_best_model_detailed(self):
        """Perform detailed profiling of the best model based on F1 score."""
        print("\n" + "="*60)
        print("PHASE 4: DETAILED PROFILING OF BEST MODEL (FULL DATASET)")
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
                if n_samples == 0: n_samples = 1
                
                X_subset = self.X.iloc[:n_samples].copy()
                y_subset = self.y[:n_samples].copy()
                
                unique_classes = np.unique(y_subset)
                if len(unique_classes) < 2:
                    print(f"  {fraction*100:3.0f}% data: Skipped (insufficient class diversity)")
                    continue
                
                # Get a fresh model instance with Safe n_jobs
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
    
    def run_benchmark(self):
        self.optimize_hyperparameters()
        self.evaluate_models_multiple_runs()
        self.evaluate_models_single_core()
        stat_results = self.statistical_comparison()
        detailed_profile = self.profile_best_model_detailed()
        return self.results, stat_results, detailed_profile
        
    def print_results(self, results, stat_results):
        print("\n" + "="*60)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*60)
        
        # Print dataset info
        print(f"\nDataset Configuration:")
        print(f"  - Total records: {len(self.X)}")
        print(f"  - HP tuning records: {len(self.X_hp)}" + 
              (" (stratified sample)" if len(self.X_hp) < len(self.X) else " (full dataset)"))
        print(f"  - Evaluation records: {len(self.X)} (full dataset)")
        
        df = pd.DataFrame(results).T
        
        # Performance Summary
        print(f"\n### Performance Metrics ({self.n_runs} runs × {self.cv_folds} folds)")
        print("-" * 80)
        
        perf_data = []
        for model in df.index:
            perf_data.append({
                'Model': model,
                'F1 Mean±Std': f"{df.loc[model, 'f1_mean']:.4f}±{df.loc[model, 'f1_std']:.4f}",
                'ROC Mean±Std': f"{df.loc[model, 'roc_auc_mean']:.4f}±{df.loc[model, 'roc_auc_std']:.4f}",
                'Fit Time (s)': f"{df.loc[model, 'avg_fit_time']:.3f}",
            })
        
        perf_df = pd.DataFrame(perf_data)
        print(perf_df.to_string(index=False))
        
        # Resource Usage Summary
        print("\n### Resource Usage & Efficiency")
        print("-" * 80)
        
        mem_data = []
        for model in df.index:
            mem_data.append({
                'Model': model,
                'Peak Mem (MB)': f"{df.loc[model, 'memory_peak_mb']:.2f}",
                'Energy (J)': f"{df.loc[model, 'total_energy_joules']:.1f}",
            })
        mem_df = pd.DataFrame(mem_data)
        print(mem_df.to_string(index=False))
        
        return df
    
    def save_results(self, results, stat_results, filename_prefix="benchmark"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("benchmark_results")
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / f"{filename_prefix}_results_{timestamp}.json"
        
        # Simple serialization helper
        def default_serializer(obj):
            if isinstance(obj, (np.integer, np.floating, np.bool_)):
                return obj.item()
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.Timedelta):
                return str(obj)
            return str(obj)

        # Add metadata about sampling
        results_with_meta = {
            'metadata': {
                'total_records': len(self.X),
                'hp_tuning_records': len(self.X_hp),
                'hp_sample_threshold': self.hp_sample_threshold,
                'hp_sample_size': self.hp_sample_size,
                'used_sampling': len(self.X_hp) < len(self.X)
            },
            'results': results,
            'statistical_results': stat_results
        }

        with open(results_file, 'w') as f:
            json.dump(results_with_meta, f, indent=2, default=default_serializer)
            
        print(f"\nResults saved to {results_file}")

    def plot_results(self, results, stat_results, detailed_profile=None):
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            plt.style.use('seaborn-v0_8-darkgrid')
            
            # Simplified plotting logic for brevity
            fig, ax = plt.subplots(figsize=(12, 6))
            model_names = list(self.detailed_scores.keys())
            f1_data = [self.detailed_scores[name]['f1'] for name in model_names]
            
            ax.boxplot(f1_data, labels=model_names, patch_artist=True)
            ax.set_title(f'F1 Score Distribution ({self.n_jobs} threads per model)\n'
                        f'HP Tuning: {len(self.X_hp)} samples | Evaluation: {len(self.X)} samples')
            ax.set_ylabel('F1 Score')
            
            results_dir = Path("benchmark_results")
            results_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_file = results_dir / f"benchmark_plot_{timestamp}.png"
            plt.savefig(plot_file, dpi=300)
            print(f"Plot saved to {plot_file}")
            
        except ImportError:
            print("\n[Warning] matplotlib/seaborn not available for plotting")


if __name__ == "__main__":
    from ucimlrepo import fetch_ucirepo
    
    # 1. Load Data
    print("Loading dataset...")
    try:
        dataset = fetch_ucirepo(id=17) # Haberman's Survival
        X = dataset.data.features.copy()
        y = dataset.data.targets
        
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y.values.ravel())
        # Ensure binary
        if len(np.unique(y)) > 2:
            y = np.where(y > 0, 1, 0)
        
        # Identify categorical columns (preprocessing is handled by ModelBenchmark)
        categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
            
        print(f"Dataset Loaded: {X.shape}")
        print(f"Categorical columns: {categorical_cols}")
        print(f"Class distribution: {np.bincount(y)}")
        
    except Exception as e:
        print(f"Error loading UCI dataset: {e}")
        # Fallback to synthetic data for testing
        from sklearn.datasets import make_classification
        X_np, y = make_classification(n_samples=1000, n_features=20, random_state=42)
        X = pd.DataFrame(X_np, columns=[f"feat_{i}" for i in range(20)])
        categorical_cols = []
        print("Using Synthetic Dataset")

    # 2. Run Benchmark with Safe Defaults
    benchmark = ModelBenchmark(
        X=X, 
        y=y, 
        categorical_cols=categorical_cols,
        n_trials=200,               # Low for testing, increase for real paper
        cv_folds=10,               # Standard
        n_runs=30,                 # Standard
        n_jobs=4,                 # Resource cap
        hp_sample_threshold=2000, # If dataset > 2000 records, sample for HP tuning
        hp_sample_size=1500       # Use 1500 records for HP tuning
    )
    
    results, stat_results, detailed_profile = benchmark.run_benchmark()
    benchmark.print_results(results, stat_results)
    benchmark.save_results(results, stat_results)
    benchmark.plot_results(results, stat_results, detailed_profile)