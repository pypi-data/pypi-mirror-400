import warnings
warnings.filterwarnings("ignore", message=".*ignore_implicit_zeros.*")
warnings.filterwarnings("ignore", message=".*n_quantiles.*")
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

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
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.pipeline import Pipeline
# ADDED METRICS
from sklearn.metrics import make_scorer, f1_score, roc_auc_score, average_precision_score, brier_score_loss
# ADDED FOR HOLM-BONFERRONI
from statsmodels.stats.multitest import multipletests

# Import the models
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
from src.linearboost.linear_boost import LinearBoostClassifier # Assuming this is in src.linearboost

# Import TabPFN
try:
    from tabpfn import TabPFNClassifier
    TABPFN_AVAILABLE = True
except ImportError:
    print("Warning: TabPFN not available. Install with: pip install tabpfn")
    TABPFN_AVAILABLE = False

# Suppress Optuna logging
optuna.logging.set_verbosity(optuna.logging.WARNING)


class ModelBenchmark:
    """
    Comprehensive benchmarking framework for ML models with statistical testing,
    memory profiling, and energy consumption estimation.
    
    Includes training and inference profiling, and advanced statistical analysis.
    """
    
    def __init__(self, X, y, categorical_cols, n_trials=200, cv_folds=10, 
                 n_runs=30, base_random_state=42):
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
        """
        self.X = X
        self.y = y
        self.categorical_cols = categorical_cols
        self.n_trials = n_trials
        self.cv_folds = cv_folds
        self.n_runs = n_runs
        self.base_random_state = base_random_state
        
        # Generate random seeds for each run
        np.random.seed(base_random_state)
        self.random_seeds = np.random.randint(0, 10000, size=n_runs)
        
        # Store results
        self.results = {}
        self.detailed_scores = defaultdict(lambda: defaultdict(list))
        self.best_params = {}
        self.resource_profiles = {}
        self.inference_profiles = {} # ADDED: To store inference results
        
        # System info for energy estimation
        self.system_info = self._get_system_info()
    
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
        return len(pickle.dumps(model))
    
    def profile_memory_and_time(self, func, *args, **kwargs):
        """
        Profile memory usage and execution time of a function.
        
        Returns:
        --------
        result: function output
        profile: dict with memory and timing information
        """
        # Get initial memory state
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Start memory tracing
        tracemalloc.start()
        
        # Monitor peak memory during execution
        peak_memory = initial_memory
        
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
        """
        Estimate energy consumption based on CPU time and memory usage.
        
        This is a simplified model based on typical TDP values:
        - CPU: ~65W for modern desktop CPUs
        - Memory: ~3W per 8GB
        
        Returns energy in Joules and CO2 equivalent.
        """
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
    
    def create_linearboost_preprocessor(self, n_jobs=-1):
        """Create preprocessor for LinearBoostClassifier."""
        return ColumnTransformer(
            transformers=[
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                make_column_selector(dtype_include=["object", "category"])),
            ],
            remainder="passthrough",
            n_jobs=n_jobs,
        )    
    
    def optimize_hyperparameters(self):
        """
        Perform hyperparameter optimization once for each model.
        This is done separately from the multiple runs evaluation.
        TabPFN requires no hyperparameter tuning.
        """
        print("\n" + "="*60)
        print("PHASE 1: HYPERPARAMETER OPTIMIZATION")
        print("="*60)
        print(f"Running {self.n_trials} trials per model...")
        
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
        
        print("\n✓ Hyperparameter optimization complete!")
        
    def _optimize_linearboost(self, cv):
        """Optimize LinearBoostClassifier with proper preprocessing."""
        
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
            
            preprocessor = self.create_linearboost_preprocessor()
            clf = LinearBoostClassifier(**params)
            pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
            
            try:
                scores = cross_validate(
                    pipe, self.X, self.y, 
                    scoring=make_scorer(f1_score, average='weighted'),
                    cv=cv, n_jobs=-1,
                    return_train_score=False
                )
                return scores['test_score'].mean()
            except Exception:
                return -np.inf
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
    
    def _optimize_xgboost(self, cv):
        """Optimize XGBoost."""
        
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
            }
            
            model = xgb.XGBClassifier(**params)
            scores = cross_validate(
                model, self.X, self.y,
                scoring=make_scorer(f1_score, average='weighted'),
                cv=cv, n_jobs=-1, 
                return_train_score=False
            )
            return scores['test_score'].mean()
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
    
    def _optimize_lightgbm(self, cv):
        """Optimize LightGBM."""
        
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
            }
            
            model = lgb.LGBMClassifier(**params)
            scores = cross_validate(
                model, self.X, self.y,
                scoring=make_scorer(f1_score, average='weighted'),
                cv=cv, n_jobs=-1, 
                return_train_score=False
            )
            return scores['test_score'].mean()
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
    
    def _optimize_catboost(self, cv):
        """Optimize CatBoost."""
        
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
            }
            
            model = CatBoostClassifier(**params)
            scores = cross_validate(
                model, self.X, self.y,
                scoring=make_scorer(f1_score, average='weighted'),
                cv=cv, n_jobs=-1,
                return_train_score=False
            )
            return scores['test_score'].mean()
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=self.n_trials, show_progress_bar=True)
        return study
    
    def evaluate_models_multiple_runs(self):
        """
        Evaluate all models using their best parameters across multiple runs.
        Each run uses a different random seed for CV splitting.
        """
        print("\n" + "="*60)
        print("PHASE 2: MULTI-RUN EVALUATION")
        print("="*60)
        print(f"Evaluating each model over {self.n_runs} runs × {self.cv_folds} folds = {self.n_runs * self.cv_folds} total evaluations")
        
        models_config = self._get_models_config()
        
        for model_name, model_getter in models_config.items():
            print(f"\n→ Evaluating {model_name}...")
            
            all_f1_scores = []
            all_roc_scores = []
            all_ap_scores = []    # ADDED
            all_brier_scores = [] # ADDED
            all_fit_times = []
            all_memory_usage = []
            
            # Progress tracking
            for run_idx, seed in enumerate(self.random_seeds):
                if (run_idx + 1) % 5 == 0:
                    print(f"  Run {run_idx + 1}/{self.n_runs}...", end='\r')
                
                # Create CV splitter with different seed for each run
                cv = StratifiedKFold(n_splits=self.cv_folds, shuffle=True, random_state=seed)
                
                # Get model with best parameters
                model = model_getter(seed)
                
                # Evaluate
                # ADDED new scorers
                scoring = {
                    'f1': make_scorer(f1_score, average='weighted'),
                    'roc_auc': 'roc_auc',
                    'avg_precision': make_scorer(average_precision_score, average='weighted', needs_proba=True),
                    'brier_score': make_scorer(brier_score_loss, needs_proba=True, greater_is_better=False) # lower is better
                }
                
                cv_results = cross_validate(
                    model, self.X, self.y,
                    scoring=scoring,
                    cv=cv,
                    n_jobs=-1,
                    return_train_score=False,
                    return_estimator=False
                )
                
                # Store results from this run
                all_f1_scores.extend(cv_results['test_f1'])
                all_roc_scores.extend(cv_results['test_roc_auc'])
                all_ap_scores.extend(cv_results['test_avg_precision']) # ADDED
                all_brier_scores.extend(cv_results['test_brier_score']) # ADDED
                all_fit_times.extend(cv_results['fit_time'])
            
            print(f"  ✓ Completed {self.n_runs} runs")
            
            # Store all scores for this model
            self.detailed_scores[model_name]['f1'] = np.array(all_f1_scores)
            self.detailed_scores[model_name]['roc_auc'] = np.array(all_roc_scores)
            self.detailed_scores[model_name]['avg_precision'] = np.array(all_ap_scores) # ADDED
            self.detailed_scores[model_name]['brier_score'] = np.array(all_brier_scores) # ADDED
            self.detailed_scores[model_name]['fit_times'] = np.array(all_fit_times)
            
            # Profile memory and resources for the best model
            # SKIP PROFILING FOR TABPFN (too slow on CPU)
            if model_name == 'TabPFN':
                print(f"  → Skipping resource profiling for {model_name} (CPU-intensive)")
                
                # Use dummy/estimated values for TabPFN
                self.resource_profiles[model_name] = {
                    'wall_time': np.mean(all_fit_times),
                    'cpu_time': np.mean(all_fit_times),
                    'memory_peak_mb': 0.0,  # Unknown
                    'memory_used_mb': 0.0,  # Unknown
                    'memory_increment_mb': 0.0,  # Unknown
                    'system_memory_before_mb': 0.0,  # Unknown
                    'system_memory_after_mb': 0.0,  # Unknown
                    'total_energy_joules': 0.0,  # Unknown
                    'cpu_energy_joules': 0.0,  # Unknown
                    'memory_energy_joules': 0.0,  # Unknown
                    'energy_kwh': 0.0,  # Unknown
                    'co2_kg': 0.0,  # Unknown
                    'co2_grams': 0.0,  # Unknown
                    'model_size_bytes': 0,  # Unknown
                    'model_size_mb': 0.0  # Unknown
                }
            else:
                print(f"  → Profiling training resources for {model_name}...")
                model_for_profile = model_getter(self.base_random_state)
                
                def train_model():
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
                # ADDED avg_precision stats
                'avg_precision_mean': np.mean(all_ap_scores),
                'avg_precision_std': np.std(all_ap_scores),
                'avg_precision_median': np.median(all_ap_scores),
                'avg_precision_q25': np.percentile(all_ap_scores, 25),
                'avg_precision_q75': np.percentile(all_ap_scores, 75),
                # ADDED brier_score stats (lower is better)
                'brier_score_mean': np.mean(all_brier_scores),
                'brier_score_std': np.std(all_brier_scores),
                'brier_score_median': np.median(all_brier_scores),
                'brier_score_q25': np.percentile(all_brier_scores, 25),
                'brier_score_q75': np.percentile(all_brier_scores, 75),
                'avg_fit_time': np.mean(all_fit_times),
                'std_fit_time': np.std(all_fit_times),
                'n_evaluations': len(all_f1_scores),
                **self.resource_profiles[model_name]
            }
                
    def evaluate_models_single_core(self):
        """Evaluate all models on a single core to measure algorithmic efficiency."""
        print("\n" + "="*60)
        print("PHASE 2.5: SINGLE-CORE EVALUATION")
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
                    model.fit(self.X, self.y)
                
                _, profile = self.profile_memory_and_time(train_single_core)
                single_core_times.append(profile['wall_time'])
                single_core_cpu_times.append(profile['cpu_time'])
            
            # Store average times
            self.results[model_name]['single_core_wall_time'] = np.mean(single_core_times)
            self.results[model_name]['single_core_cpu_time'] = np.mean(single_core_cpu_times)
            self.results[model_name]['single_core_wall_time_std'] = np.std(single_core_times)
            
            print(f"  ✓ Single-core wall time: {np.mean(single_core_times):.3f}±{np.std(single_core_times):.3f}s")
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # NEW METHOD: profile_inference (Phase 2.7)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def profile_inference(self):
        """
        Profile inference time and resource usage for all models.
        """
        print("\n" + "="*60)
        print("PHASE 2.7: INFERENCE PROFILING")
        print("="*60)
        print("Profiling .predict() and .predict_proba() on full dataset")
        
        for model_name in self.results.keys():
            if model_name == 'TabPFN':
                print(f"→ Skipping inference profiling for {model_name}")
                # Add dummy data
                self.results[model_name].update({
                    'inference_predict_wall_time': 0.0,
                    'inference_predict_cpu_time': 0.0,
                    'inference_predict_memory_peak_mb': 0.0,
                    'inference_predict_co2_grams': 0.0,
                    'inference_proba_wall_time': 0.0,
                    'inference_proba_cpu_time': 0.0,
                    'inference_proba_memory_peak_mb': 0.0,
                    'inference_proba_co2_grams': 0.0,
                })
                continue
            
            print(f"→ Profiling inference for {model_name}...")
            
            # 1. Get a fresh, trained model
            model = self._get_models_config()[model_name](self.base_random_state)
            
            # We must train it first (time not counted towards inference)
            try:
                model.fit(self.X, self.y)
            except Exception as e:
                print(f"  ✗ Error training model for inference profiling: {e}")
                continue

            # 2. Profile .predict()
            def infer_predict():
                return model.predict(self.X)
            
            _, predict_profile = self.profile_memory_and_time(infer_predict)
            predict_energy = self.estimate_energy_consumption(
                predict_profile['cpu_time'],
                predict_profile['memory_peak_mb'],
                f"{model_name}_predict"
            )
            
            # 3. Profile .predict_proba()
            def infer_predict_proba():
                return model.predict_proba(self.X)
            
            try:
                _, proba_profile = self.profile_memory_and_time(infer_predict_proba)
                proba_energy = self.estimate_energy_consumption(
                    proba_profile['cpu_time'],
                    proba_profile['memory_peak_mb'],
                    f"{model_name}_predict_proba"
                )
            except (AttributeError, NotImplementedError):
                print(f"  ! {model_name} does not support .predict_proba(). Skipping.")
                proba_profile = {k: 0.0 for k in predict_profile.keys()}
                proba_energy = {k: 0.0 for k in predict_energy.keys()}
            
            # 4. Store results
            inference_stats = {
                'inference_predict_wall_time': predict_profile['wall_time'],
                'inference_predict_cpu_time': predict_profile['cpu_time'],
                'inference_predict_memory_peak_mb': predict_profile['memory_peak_mb'],
                'inference_predict_co2_grams': predict_energy['co2_grams'],
                
                'inference_proba_wall_time': proba_profile['wall_time'],
                'inference_proba_cpu_time': proba_profile['cpu_time'],
                'inference_proba_memory_peak_mb': proba_profile['memory_peak_mb'],
                'inference_proba_co2_grams': proba_energy['co2_grams'],
            }
            
            self.inference_profiles[model_name] = inference_stats
            # Merge into main results dictionary
            self.results[model_name].update(inference_stats)
            
            print(f"  ✓ .predict(): {predict_profile['wall_time']:.4f}s, {predict_profile['memory_peak_mb']:.2f}MB")
            print(f"  ✓ .predict_proba(): {proba_profile['wall_time']:.4f}s, {proba_profile['memory_peak_mb']:.2f}MB")
            
            
    def _get_models_config(self, n_jobs=-1):
        """Get model configurations with best parameters."""
        models_config = {}
        
        # LinearBoost
        def get_linearboost(seed):
            preprocessor = self.create_linearboost_preprocessor()
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
                'thread_count': n_jobs if n_jobs != -1 else psutil.cpu_count(logical=True)
            })
            return CatBoostClassifier(**params)
        models_config['CatBoost'] = get_catboost
        
        # TabPFN - No hyperparameters, uses defaults
        if TABPFN_AVAILABLE:
            def get_tabpfn(seed):
                # TabPFN works best with default settings
                # Note: TabPFN has data size limitations (max 10k rows, 100 features)
                return TabPFNClassifier(device='cpu')
            models_config['TabPFN'] = get_tabpfn
        
        return models_config
    
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # UPDATED: statistical_comparison
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def statistical_comparison(self):
        """
        Perform comprehensive statistical tests between all models.
        Uses Friedman test for overall comparison and pairwise Wilcoxon
        with Holm-Bonferroni correction for post-hoc analysis.
        """
        print("\n" + "="*60)
        print("PHASE 3: STATISTICAL ANALYSIS")
        print("="*60)
        
        model_names = list(self.detailed_scores.keys())
        n_models = len(model_names)
        
        if n_models < 2:
            print("Need at least 2 models for comparison")
            return None
        
        results = {}
        
        # --- 1. Friedman Test ---
        print("\n→ Running Friedman tests...")
        
        # Prepare data matrices
        scores = {
            'f1': np.array([self.detailed_scores[name]['f1'] for name in model_names]),
            'roc_auc': np.array([self.detailed_scores[name]['roc_auc'] for name in model_names]),
            'avg_precision': np.array([self.detailed_scores[name]['avg_precision'] for name in model_names]),
            'brier_score': np.array([self.detailed_scores[name]['brier_score'] for name in model_names]),
        }
        
        results['friedman'] = {}
        for metric, data in scores.items():
            stat, pvalue = stats.friedmanchisquare(*data)
            results['friedman'][metric] = {
                'statistic': stat,
                'p_value': pvalue,
                'significant': pvalue < 0.05,
                'interpretation': 'Models differ significantly' if pvalue < 0.05 else 'No significant difference'
            }
        
        # --- 2. Post-hoc Nemenyi Test (for ranking) ---
        print("→ Calculating average ranks (for Nemenyi)...")
        
        # Calculate average ranks. Lower rank is better.
        # For brier_score, we rank directly (lower is better)
        # For others, we rank the negative (higher is better)
        ranks = {
            'f1': np.array([rankdata(-s) for s in scores['f1'].T]).T,
            'roc_auc': np.array([rankdata(-s) for s in scores['roc_auc'].T]).T,
            'avg_precision': np.array([rankdata(-s) for s in scores['avg_precision'].T]).T,
            'brier_score': np.array([rankdata(s) for s in scores['brier_score'].T]).T,
        }
        
        avg_ranks = {}
        for metric, data in ranks.items():
            avg_ranks[metric] = {name: rank for name, rank in zip(model_names, np.mean(data, axis=1))}
        
        results['average_ranks'] = avg_ranks
        
        # Critical difference for Nemenyi test
        k = n_models
        n = scores['f1'].shape[1]
        
        # Critical values for alpha=0.05 (from Nemenyi table)
        q_alpha = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850}
        q = q_alpha.get(k, 2.850)
        
        cd = q * np.sqrt((k * (k + 1)) / (6 * n))
        results['nemenyi_critical_difference'] = cd
        
        # --- 3. Pairwise Wilcoxon with Holm-Bonferroni Correction ---
        print("→ Running pairwise Wilcoxon tests with Holm-Bonferroni correction...")
        
        results['pairwise'] = {}
        n_comparisons = (n_models * (n_models - 1)) // 2
        
        for metric in scores.keys():
            pairwise_results = {}
            p_values_uncorrected = []
            pair_names_ordered = []
            
            for i in range(n_models):
                for j in range(i + 1, n_models):
                    model1, model2 = model_names[i], model_names[j]
                    pair_name = f"{model1}_vs_{model2}"
                    pair_names_ordered.append(pair_name)
                    
                    scores1 = self.detailed_scores[model1][metric]
                    scores2 = self.detailed_scores[model2][metric]
                    
                    # Wilcoxon test
                    try:
                        stat, p = stats.wilcoxon(scores1, scores2, alternative='two-sided')
                    except ValueError:
                        # Handle case where all differences are zero
                        stat, p = 0.0, 1.0
                        
                    p_values_uncorrected.append(p)
                    
                    # Determine better model
                    mean1, mean2 = np.mean(scores1), np.mean(scores2)
                    if metric == 'brier_score': # lower is better
                        better_model = model1 if mean1 < mean2 else model2
                    else: # higher is better
                        better_model = model1 if mean1 > mean2 else model2
                    
                    pairwise_results[pair_name] = {
                        'statistic': stat,
                        'p_value_uncorrected': p,
                        'better_model': better_model,
                        'mean_diff': mean1 - mean2,
                        'rank_diff': abs(avg_ranks[metric][model1] - avg_ranks[metric][model2]),
                        'nemenyi_significant': abs(avg_ranks[metric][model1] - avg_ranks[metric][model2]) > cd
                    }
            
            # Apply Holm-Bonferroni correction
            if p_values_uncorrected:
                reject_holm, p_values_holm, _, _ = multipletests(
                    p_values_uncorrected, alpha=0.05, method='holm'
                )
                
                # Add corrected results back to the dictionary
                for i, pair_name in enumerate(pair_names_ordered):
                    pairwise_results[pair_name]['p_value_holm'] = p_values_holm[i]
                    pairwise_results[pair_name]['significant_holm'] = reject_holm[i]
            
            results['pairwise'][metric] = pairwise_results
        
        # --- 4. Statistical Power Analysis ---
        print("→ Calculating statistical power...")
        
        results['statistical_power'] = {
            'n_samples_per_model': n,
            'alpha': 0.05,
            'correction_method': 'Holm-Bonferroni',
            'interpretation': f"With {n} samples per model, we have high statistical power to detect meaningful differences"
        }
        
        return results
    
    def profile_best_model_detailed(self):
        """
        Perform detailed profiling of the best model based on F1 score.
        """
        print("\n" + "="*60)
        print("PHASE 4: DETAILED PROFILING OF BEST MODEL")
        print("="*60)
        
        # Find best model based on F1
        if not self.results:
            print("  ✗ Error: No results available to determine best model.")
            return None
            
        best_model_name = max(self.results.keys(), 
                             key=lambda k: self.results[k].get('f1_mean', -1))
        
        print(f"\nBest model (by F1): {best_model_name}")
        print(f"F1 Score: {self.results[best_model_name].get('f1_mean', 0):.4f}")
        
        # Detailed profiling with different data sizes
        print("\n→ Profiling scalability...")
        
        data_fractions = [0.1, 0.25, 0.5, 0.75, 1.0]
        scaling_profiles = []
        
        for fraction in data_fractions:
            try:
                n_samples = int(len(self.X) * fraction)
                if n_samples < 2:
                    print(f"  {fraction*100:3.0f}% data: Skipped (too few samples)")
                    continue
                
                # Ensure we have at least one sample from each class for stratification
                # Simple slicing for this purpose
                X_subset = self.X.iloc[:n_samples].copy()
                y_subset = self.y[:n_samples].copy()
                
                # Check if we have both classes in the subset
                unique_classes = np.unique(y_subset)
                if len(unique_classes) < 2 and n_samples > 10:
                    print(f"  {fraction*100:3.0f}% data: Skipped (insufficient class diversity)")
                    continue
                
                # Get a fresh model instance for this subset
                models_config = self._get_models_config()
                if best_model_name not in models_config:
                    print(f"  ✗ Error: Best model {best_model_name} not in config.")
                    continue
                    
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
        
        if not scaling_profiles:
            print("  Warning: No successful scaling profiles generated")
        
        return detailed_profile
    
    def run_benchmark(self):
        """
        Run the complete benchmark suite.
        """
        # Phase 1: Hyperparameter optimization
        self.optimize_hyperparameters()
        
        # Phase 2: Multi-run evaluation
        self.evaluate_models_multiple_runs()
        
        # Phase 2.5: Single-core evaluation
        self.evaluate_models_single_core()
        
        # Phase 2.7: Inference Profiling (NEW)
        self.profile_inference()
        
        # Phase 3: Statistical testing
        stat_results = self.statistical_comparison()
        
        # Phase 4: Detailed profiling of best model
        detailed_profile = self.profile_best_model_detailed()
        
        return self.results, stat_results, detailed_profile
        
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # UPDATED: print_results
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def print_results(self, results, stat_results):
        """
        Print comprehensive benchmark results including resource usage.
        """
        print("\n" + "="*60)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*60)
        
        df = pd.DataFrame(results).T
        
        # Performance Summary
        print(f"\n### Performance Metrics ({self.n_runs} runs × {self.cv_folds} folds = {self.n_runs * self.cv_folds} evaluations per model)")
        print("-" * 80)
        
        # Create performance table
        perf_data = []
        for model in df.index:
            perf_data.append({
                'Model': model,
                'F1 Mean±Std': f"{df.loc[model, 'f1_mean']:.4f}±{df.loc[model, 'f1_std']:.4f}",
                'ROC Mean±Std': f"{df.loc[model, 'roc_auc_mean']:.4f}±{df.loc[model, 'roc_auc_std']:.4f}",
                'AvgPrec Mean±Std': f"{df.loc[model, 'avg_precision_mean']:.4f}±{df.loc[model, 'avg_precision_std']:.4f}",
                'Brier Mean±Std': f"{df.loc[model, 'brier_score_mean']:.4f}±{df.loc[model, 'brier_score_std']:.4f}",
            })
        
        perf_df = pd.DataFrame(perf_data)
        print(perf_df.to_string(index=False))
        
        # Best Models
        print("\n### Best Models")
        print("-" * 50)
        best_f1 = df['f1_mean'].idxmax()
        best_roc = df['roc_auc_mean'].idxmax()
        best_ap = df['avg_precision_mean'].idxmax()
        best_brier = df['brier_score_mean'].idxmin() # Lower is better
        
        print(f"Best F1 Score:  {best_f1} ({df.loc[best_f1, 'f1_mean']:.4f})")
        print(f"Best ROC-AUC:   {best_roc} ({df.loc[best_roc, 'roc_auc_mean']:.4f})")
        print(f"Best Avg. Prec: {best_ap} ({df.loc[best_ap, 'avg_precision_mean']:.4f})")
        print(f"Best Brier (Cal): {best_brier} ({df.loc[best_brier, 'brier_score_mean']:.4f})")
        
        # Resource Usage Summary
        print("\n### Resource Usage & Efficiency")
        print("-" * 80)
        
        # Training Efficiency
        print("\n#### Training Performance:")
        eff_data = []
        for model in df.index:
            multi_core_time = df.loc[model, 'wall_time']
            single_core_time = df.loc[model, 'single_core_wall_time']
            
            if multi_core_time > 1e-6:
                speedup = f"{(single_core_time / multi_core_time):.2f}x"
                cpu_efficiency = f"{(df.loc[model, 'cpu_time']/multi_core_time*100):.1f}%"
            else:
                speedup = "N/A"
                cpu_efficiency = "N/A"

            eff_data.append({
                'Model': model,
                'Train Time (Multi, s)': f"{multi_core_time:.3f}",
                'Train Time (Single, s)': f"{single_core_time:.3f}",
                'Total CPU Time (s)': f"{df.loc[model, 'cpu_time']:.3f}",
                'CPU Efficiency': cpu_efficiency,
                'Parallel Speedup': speedup,
            })
        
        eff_df = pd.DataFrame(eff_data)
        print(eff_df.to_string(index=False))
        
        # ADDED: Inference Performance
        print("\n#### Inference Performance (on full dataset):")
        infer_data = []
        for model in df.index:
            infer_data.append({
                'Model': model,
                '.predict() Time (s)': f"{df.loc[model, 'inference_predict_wall_time']:.4f}",
                '.predict() Peak Mem (MB)': f"{df.loc[model, 'inference_predict_memory_peak_mb']:.2f}",
                '.proba() Time (s)': f"{df.loc[model, 'inference_proba_wall_time']:.4f}",
                '.proba() Peak Mem (MB)': f"{df.loc[model, 'inference_proba_memory_peak_mb']:.2f}",
            })
        
        infer_df = pd.DataFrame(infer_data)
        print(infer_df.to_string(index=False))
        
        # Memory Usage
        print("\n#### Memory & Energy (Training):")
        mem_data = []
        for model in df.index:
            mem_data.append({
                'Model': model,
                'Peak Memory (MB)': f"{df.loc[model, 'memory_peak_mb']:.2f}",
                'Model Size (MB)': f"{df.loc[model, 'model_size_mb']:.2f}",
                'Total Energy (J)': f"{df.loc[model, 'total_energy_joules']:.1f}",
                'CO2 (grams)': f"{df.loc[model, 'co2_grams']:.3f}",
            })
        
        mem_df = pd.DataFrame(mem_data)
        print(mem_df.to_string(index=False))
        
        # System Information
        print("\n### System Information")
        print("-" * 50)
        print(f"CPU Count: {self.system_info['cpu_count']}")
        print(f"CPU Frequency: {self.system_info['cpu_freq']:.0f} MHz" if self.system_info['cpu_freq'] else "CPU Frequency: N/A")
        print(f"Total Memory: {self.system_info['total_memory']/(1024**3):.1f} GB")
        print(f"Platform: {self.system_info['platform']}")
        
        # Statistical Testing Results
        if stat_results:
            print("\n### Statistical Testing Results")
            print("-" * 80)
            
            # Friedman Test Results
            print("\n1. FRIEDMAN TEST (Overall Comparison)")
            for metric, res in stat_results['friedman'].items():
                print(f"   {metric.upper():<14}: χ² = {res['statistic']:.2f}, p = {res['p_value']:.4f} ({res['interpretation']})")

            # Average Ranks
            print("\n2. AVERAGE RANKS (lower is better)")
            rank_data = []
            for model in stat_results['average_ranks']['f1'].keys():
                rank_data.append({
                    'Model': model,
                    'F1 Rank': f"{stat_results['average_ranks']['f1'][model]:.2f}",
                    'ROC Rank': f"{stat_results['average_ranks']['roc_auc'][model]:.2f}",
                    'AP Rank': f"{stat_results['average_ranks']['avg_precision'][model]:.2f}",
                    'Brier Rank': f"{stat_results['average_ranks']['brier_score'][model]:.2f}",
                })
            rank_df = pd.DataFrame(rank_data).sort_values(by='F1 Rank')
            print(rank_df.to_string(index=False))
            
            # Nemenyi Critical Difference
            print(f"\n3. NEMENYI CRITICAL DIFFERENCE (for ranks)")
            print(f"   CD = {stat_results['nemenyi_critical_difference']:.3f} (Models with rank diff > CD are significantly different)")
            
            # Pairwise Comparisons
            print("\n4. PAIRWISE COMPARISONS (Wilcoxon + Holm-Bonferroni correction)")
            n_pairs = len(stat_results['pairwise']['f1'])
            
            for metric, pairs in stat_results['pairwise'].items():
                sig_holm = sum(1 for v in pairs.values() if v['significant_holm'])
                print(f"\n   {metric.upper()} Comparisons ({sig_holm}/{n_pairs} significant pairs):")
                
                sig_pairs_holm = [(k, v) for k, v in pairs.items() if v['significant_holm']]
                
                if sig_pairs_holm:
                    for pair_name, data in sig_pairs_holm:
                        print(f"   • {pair_name}:")
                        print(f"     - p-value (Holm): {data['p_value_holm']:.6f}")
                        print(f"     - Better model: {data['better_model']}")
                else:
                    print("     No significant differences after Holm-Bonferroni correction")

            # Statistical Power
            print("\n5. STATISTICAL POWER")
            print("-" * 50)
            print(f"   Sample size per model: {stat_results['statistical_power']['n_samples_per_model']}")
            print(f"   Correction: {stat_results['statistical_power']['correction_method']}")
            print(f"   {stat_results['statistical_power']['interpretation']}")
        
        return df
    
    def save_results(self, results, stat_results, filename_prefix="benchmark"):
        """
        Save comprehensive results to files for later analysis.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create results directory if it doesn't exist
        results_dir = Path("benchmark_results")
        results_dir.mkdir(exist_ok=True)
        
        # Save main results
        results_file = results_dir / f"{filename_prefix}_results_{timestamp}.json"
        with open(results_file, 'w') as f:
            serializable_results = {}
            for model, model_results in results.items():
                serializable_results[model] = {}
                for key, value in model_results.items():
                    if isinstance(value, pd.Timedelta):
                        serializable_results[model][key] = str(value)
                    elif isinstance(value, np.ndarray):
                        serializable_results[model][key] = value.tolist()
                    elif isinstance(value, (np.float32, np.float64)):
                        serializable_results[model][key] = float(value)
                    elif isinstance(value, (np.int32, np.int64)):
                        serializable_results[model][key] = int(value)
                    else:
                        serializable_results[model][key] = value
            
            json.dump(serializable_results, f, indent=2)
        
        # Save statistical results
        if stat_results:
            stat_file = results_dir / f"{filename_prefix}_statistics_{timestamp}.json"
            
            # Convert numpy types to Python types for JSON serialization
            def convert_numpy(obj):
                if isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, np.generic):
                    return obj.item()
                elif isinstance(obj, (np.float32, np.float64, np.float16)):
                    return float(obj)
                elif isinstance(obj, (np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64)):
                    return int(obj)
                elif isinstance(obj, np.bool_):
                    return bool(obj)
                elif isinstance(obj, dict):
                    return {k: convert_numpy(v) for k, v in obj.items()}
                elif isinstance(obj, (list, tuple)):
                    return [convert_numpy(item) for item in obj]
                elif hasattr(obj, 'tolist'):
                    return obj.tolist()
                return obj
            
            serializable_stats = convert_numpy(stat_results)
            
            with open(stat_file, 'w') as f:
                json.dump(serializable_stats, f, indent=2)
        
        # Save detailed scores for reproducibility
        scores_file = results_dir / f"{filename_prefix}_detailed_scores_{timestamp}.npz"
        scores_to_save = {}
        for model_name, scores_dict in self.detailed_scores.items():
            for metric_name, scores in scores_dict.items():
                key = f"{model_name}_{metric_name}"
                scores_to_save[key] = scores
        np.savez(scores_file, **scores_to_save)
        
        # Save summary DataFrame
        df = pd.DataFrame(results).T
        csv_file = results_dir / f"{filename_prefix}_summary_{timestamp}.csv"
        df.to_csv(csv_file)
        
        print(f"\n### Results saved to 'benchmark_results/' directory:")
        print(f"  - Main results: {results_file.name}")
        if stat_results:
            print(f"  - Statistical analysis: {stat_file.name}")
        print(f"  - Detailed scores: {scores_file.name}")
        print(f"  - Summary CSV: {csv_file.name}")
        
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # UPDATED: plot_results (now 3x3 grid)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def plot_results(self, results, stat_results, detailed_profile=None):
        """
        Create comprehensive visualization plots including resource usage,
        Pareto frontier, and scalability.
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Set style
            plt.style.use('seaborn-v0_8-darkgrid')
            sns.set_palette("husl")
            
            # Create figure with more subplots
            fig = plt.figure(figsize=(24, 20))
            gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)
            
            fig.suptitle(f'Comprehensive Model Benchmark ({self.n_runs} runs × {self.cv_folds} folds)', fontsize=20, y=1.02)
            
            model_names = list(self.detailed_scores.keys())
            colors = plt.cm.Set3(np.linspace(0, 1, len(model_names)))
            df = pd.DataFrame(results).T
            
            # --- Row 1: Performance Distributions ---
            
            # 1. F1 Score Distribution
            ax1 = fig.add_subplot(gs[0, 0])
            f1_data = [self.detailed_scores[name]['f1'] for name in model_names]
            bp1 = ax1.boxplot(f1_data, labels=model_names, patch_artist=True)
            ax1.set_title('F1 Score Distribution')
            ax1.set_ylabel('F1 Score (Higher is better)')
            ax1.tick_params(axis='x', rotation=45)
            for patch, color in zip(bp1['boxes'], colors):
                patch.set_facecolor(color)
            
            # 2. ROC-AUC Distribution
            ax2 = fig.add_subplot(gs[0, 1])
            roc_data = [self.detailed_scores[name]['roc_auc'] for name in model_names]
            bp2 = ax2.boxplot(roc_data, labels=model_names, patch_artist=True)
            ax2.set_title('ROC-AUC Distribution')
            ax2.set_ylabel('ROC-AUC (Higher is better)')
            ax2.tick_params(axis='x', rotation=45)
            for patch, color in zip(bp2['boxes'], colors):
                patch.set_facecolor(color)
            
            # 3. Avg. Precision Distribution
            ax3 = fig.add_subplot(gs[0, 2])
            ap_data = [self.detailed_scores[name]['avg_precision'] for name in model_names]
            bp3 = ax3.boxplot(ap_data, labels=model_names, patch_artist=True)
            ax3.set_title('Average Precision Distribution')
            ax3.set_ylabel('Avg. Precision (Higher is better)')
            ax3.tick_params(axis='x', rotation=45)
            for patch, color in zip(bp3['boxes'], colors):
                patch.set_facecolor(color)

            # --- Row 2: Resource Comparisons ---
            
            # 4. Training Time (Multi-Core)
            ax4 = fig.add_subplot(gs[1, 0])
            sns.barplot(x=df.index, y='wall_time', data=df, ax=ax4, palette=colors)
            ax4.set_title('Training Time (Multi-Core)')
            ax4.set_ylabel('Wall Time (seconds)')
            ax4.set_xlabel('Model')
            ax4.tick_params(axis='x', rotation=45)
            ax4.set_yscale('log')
            
            # 5. Training Peak Memory
            ax5 = fig.add_subplot(gs[1, 1])
            mem_data = df[['memory_peak_mb', 'model_size_mb']].reset_index()
            mem_data = mem_data.melt('index', var_name='Memory Type', value_name='MB')
            sns.barplot(x='index', y='MB', hue='Memory Type', data=mem_data, ax=ax5, palette='pastel')
            ax5.set_title('Training Memory & Model Size')
            ax5.set_ylabel('Memory (MB)')
            ax5.set_xlabel('Model')
            ax5.tick_params(axis='x', rotation=45)
            ax5.legend(title=None)
            
            # 6. Inference Time (predict_proba)
            ax6 = fig.add_subplot(gs[1, 2])
            sns.barplot(x=df.index, y='inference_proba_wall_time', data=df, ax=ax6, palette=colors)
            ax6.set_title('Inference Time (.predict_proba)')
            ax6.set_ylabel('Wall Time (seconds)')
            ax6.set_xlabel('Model')
            ax6.tick_params(axis='x', rotation=45)
            ax6.set_yscale('log')
            
            # --- Row 3: Scalability & Trade-offs ---
            
            # 7. NEW: Pareto Frontier (F1 vs. Training Time)
            ax7 = fig.add_subplot(gs[2, 0])
            sns.scatterplot(x='wall_time', y='f1_mean', data=df, hue=df.index, s=150, ax=ax7, palette=colors, legend=False)
            ax7.set_title('Pareto Frontier: F1 vs. Training Time')
            ax7.set_xlabel('Training Time (s) (Lower is better)')
            ax7.set_ylabel('F1 Score (Higher is better)')
            ax7.set_xscale('log')
            # Annotate points
            for i, row in df.iterrows():
                ax7.text(row['wall_time']*1.1, row['f1_mean'], row.name, fontsize=9)
            
            # 8. NEW: Scalability (Time)
            ax8 = fig.add_subplot(gs[2, 1])
            ax8.set_title('Best Model Scalability: Time')
            ax8.set_xlabel('Number of Samples')
            ax8.set_ylabel('Wall Time (s)')
            if detailed_profile and detailed_profile['scaling_profiles']:
                scale_df = pd.DataFrame(detailed_profile['scaling_profiles'])
                sns.lineplot(x='n_samples', y='wall_time', data=scale_df, ax=ax8, marker='o')
                ax8.set_title(f'Scalability: {detailed_profile["model_name"]} Time')
                
            # 9. NEW: Scalability (Memory)
            ax9 = fig.add_subplot(gs[2, 2])
            ax9.set_title('Best Model Scalability: Memory')
            ax9.set_xlabel('Number of Samples')
            ax9.set_ylabel('Peak Memory (MB)')
            if detailed_profile and detailed_profile['scaling_profiles']:
                scale_df = pd.DataFrame(detailed_profile['scaling_profiles'])
                sns.lineplot(x='n_samples', y='memory_peak_mb', data=scale_df, ax=ax9, marker='o', color='red')
                ax9.set_title(f'Scalability: {detailed_profile["model_name"]} Memory')

            plt.tight_layout()
            
            # Save plot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_dir = Path("benchmark_results")
            results_dir.mkdir(exist_ok=True)
            plot_file = results_dir / f"comprehensive_benchmark_{timestamp}.png"
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            print(f"\n### Comprehensive plots saved to: {plot_file}")
            
            plt.show()
            
        except ImportError:
            print("\n[Warning] matplotlib/seaborn not available for plotting")


# Example usage
if __name__ == "__main__":
    # Data loading
    from ucimlrepo import fetch_ucirepo
    from sklearn.preprocessing import LabelEncoder
    
    # The Haberman's Survival dataset from UCI
    dataset_id = 222
    dataset = fetch_ucirepo(id=dataset_id)
    
    # Data preparation
    X = dataset.data.features.copy()
    y_raw = dataset.data.targets
    
    # --- Prepare Data ---
    # Encode target
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw.values.ravel())
    
    # Convert problem to binary (1 = died within 5 yrs, 0 = survived)
    # Original: 1 = survived 5+ years, 2 = died within 5 years
    # We map 1 -> 0 and 2 -> 1
    y = np.where(y == 0, 0, 1) # 0 was '1' (survived), 1 was '2' (died)

    # Identify categorical columns (this dataset has none, let's create one)
    # For demonstration, let's discretize 'Age' into a categorical feature
    if 'Age' in X.columns:
        X['Age_Group'] = pd.cut(X['Age'], bins=[0, 40, 60, 100], labels=['Young', 'Mid', 'Old'])
    
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    
    # Convert categorical columns to 'category' dtype
    for col in categorical_cols:
        X[col] = X[col].astype("category")
    
    # Handle missing values
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    for col in numeric_cols:
        X[col] = X[col].fillna(X[col].median())
    
    for col in categorical_cols:
        if len(X[col].mode()) > 0:
            X[col] = X[col].fillna(X[col].mode()[0])
    
    print("="*60)
    print("MACHINE LEARNING MODEL BENCHMARKING FRAMEWORK")
    print("WITH RESOURCE PROFILING & ENERGY CONSUMPTION ANALYSIS")
    print("="*60)
    print(f"Dataset shape: {X.shape}")
    print(f"Target distribution (0=Survived, 1=Died): {np.bincount(y)}")
    print(f"Categorical features: {categorical_cols}")
    print(f"Numerical features: {numeric_cols}")
    
    if TABPFN_AVAILABLE:
        if X.shape[0] > 10000 or X.shape[1] > 100:
            print("\n✗ TabPFN is available but will be skipped (dataset too large)")
            TABPFN_AVAILABLE = False
        else:
            print(f"\n✓ TabPFN is available and will be included in benchmarks")
    else:
        print(f"\n✗ TabPFN is not available. Install with: pip install tabpfn")
    
    # Run comprehensive benchmark
    benchmark = ModelBenchmark(
        X=X, 
        y=y, 
        categorical_cols=categorical_cols,
        n_trials=200,    # Reduced for speed in example
        cv_folds=10,     # Reduced for speed in example
        n_runs=30,      # Reduced for speed in example
        base_random_state=42
    )
    
    # Execute benchmark with resource profiling
    results, stat_results, detailed_profile = benchmark.run_benchmark()
    
    # Print comprehensive results
    df_summary = benchmark.print_results(results, stat_results)
    
    # Save all results including resource profiles
    benchmark.save_results(results, stat_results)
    
    # Generate comprehensive plots including resource usage
    benchmark.plot_results(results, stat_results, detailed_profile)