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
from sklearn.metrics import make_scorer, f1_score, roc_auc_score

# Import the models
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostClassifier
from src.linearboost.linear_boost import LinearBoostClassifier

# Suppress Optuna logging
optuna.logging.set_verbosity(optuna.logging.WARNING)


class ModelBenchmark:
    """
    Comprehensive benchmarking framework for ML models with statistical testing,
    memory profiling, and energy consumption estimation.
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
            n_jobs=n_jobs,  # Now configurable
        )    
    
    def optimize_hyperparameters(self):
        """
        Perform hyperparameter optimization once for each model.
        This is done separately from the multiple runs evaluation.
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
                scoring = {
                    'f1': make_scorer(f1_score, average='weighted'),
                    'roc_auc': 'roc_auc',
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
                all_fit_times.extend(cv_results['fit_time'])  # fit_time is automatically included
            
            print(f"  ✓ Completed {self.n_runs} runs")
            
            # Store all scores for this model
            self.detailed_scores[model_name]['f1'] = np.array(all_f1_scores)
            self.detailed_scores[model_name]['roc_auc'] = np.array(all_roc_scores)
            self.detailed_scores[model_name]['fit_times'] = np.array(all_fit_times)
            
            # Profile memory and resources for the best model
            print(f"  → Profiling resources for {model_name}...")
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
        
        n_single_core_runs = 5  # Multiple runs for stability
        
        for model_name in self.results.keys():
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

    def _get_models_config(self, n_jobs=-1): # Modify this method to accept n_jobs
        """Get model configurations with best parameters."""
        models_config = {}
        
        # LinearBoost (unaffected by n_jobs, but included for consistency)
        
        def get_linearboost(seed):
            preprocessor = self.create_linearboost_preprocessor()
            clf = LinearBoostClassifier(**self.best_params['LinearBoost'])
            pipe = Pipeline(steps=[("preprocess", preprocessor), ("model", clf)])
            # This line has an issue - should set n_jobs during preprocessor creation
            # pipe.set_params(preprocess__n_jobs=n_jobs)  # This won't work
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
                'n_jobs': n_jobs # Control XGBoost's threading
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
                'n_jobs': n_jobs # Control LightGBM's threading
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
                'thread_count': n_jobs if n_jobs != -1 else psutil.cpu_count(logical=True) # Control CatBoost's threading
            })
            return CatBoostClassifier(**params)
        models_config['CatBoost'] = get_catboost
        
        return models_config
    
    def statistical_comparison(self):
        """
        Perform comprehensive statistical tests between all models.
        With 30 runs × 10 folds = 300 data points per model, we have strong statistical power.
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
        
        # 1. Friedman Test (non-parametric test for multiple related samples)
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
        
        # 2. Post-hoc Nemenyi Test (if Friedman test is significant)
        print("→ Running post-hoc Nemenyi tests...")
        
        # Calculate average ranks for each model
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
        
        # Critical values for alpha=0.05 (from Nemenyi table)
        q_alpha = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850}
        q = q_alpha.get(k, 2.850)  # Use conservative value if k > 6
        
        cd = q * np.sqrt((k * (k + 1)) / (6 * n))
        results['nemenyi_critical_difference'] = cd
        
        # 3. Pairwise Comparisons with Wilcoxon signed-rank test
        print("→ Running pairwise Wilcoxon tests...")
        
        results['pairwise_f1'] = {}
        results['pairwise_roc'] = {}
        
        # Bonferroni correction for multiple comparisons
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
                
                # Effect size (Cliff's Delta)
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
                
                # Effect size
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
        
        # 4. Statistical Power Analysis
        print("→ Calculating statistical power...")
        
        # Calculate observed effect sizes and statistical power
        results['statistical_power'] = {
            'n_samples_per_model': n,
            'bonferroni_corrected_alpha': bonferroni_alpha,
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
        best_model_name = max(self.results.keys(), 
                             key=lambda k: self.results[k]['f1_mean'])
        
        print(f"\nBest model: {best_model_name}")
        print(f"F1 Score: {self.results[best_model_name]['f1_mean']:.4f}")
        
        # Detailed profiling with different data sizes
        print("\n→ Profiling scalability...")
        
        data_fractions = [0.1, 0.25, 0.5, 0.75, 1.0]
        scaling_profiles = []
        
        for fraction in data_fractions:
            try:
                n_samples = int(len(self.X) * fraction)
                if n_samples == 0:
                    n_samples = 1
                
                # Ensure we have at least one sample from each class for stratification
                X_subset = self.X.iloc[:n_samples].copy()
                y_subset = self.y[:n_samples].copy()
                
                # Check if we have both classes in the subset
                unique_classes = np.unique(y_subset)
                if len(unique_classes) < 2:
                    print(f"  {fraction*100:3.0f}% data: Skipped (insufficient class diversity)")
                    continue
                
                # Get a fresh model instance for this subset
                models_config = self._get_models_config()
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
        
        # Phase 2: Multi-run evaluation (this uses n_jobs=-1 by default)
        self.evaluate_models_multiple_runs()
        
        # Phase 2.5: Single-core evaluation
        self.evaluate_models_single_core()
        
        # Phase 3: Statistical testing
        stat_results = self.statistical_comparison()
        
        # Phase 4: Detailed profiling of best model
        detailed_profile = self.profile_best_model_detailed()
        
        return self.results, stat_results, detailed_profile
        
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
                'F1 Median [Q1,Q3]': f"{df.loc[model, 'f1_median']:.4f} [{df.loc[model, 'f1_q25']:.4f},{df.loc[model, 'f1_q75']:.4f}]",
                'ROC Mean±Std': f"{df.loc[model, 'roc_auc_mean']:.4f}±{df.loc[model, 'roc_auc_std']:.4f}",
                'ROC Median [Q1,Q3]': f"{df.loc[model, 'roc_auc_median']:.4f} [{df.loc[model, 'roc_auc_q25']:.4f},{df.loc[model, 'roc_auc_q75']:.4f}]",
            })
        
        perf_df = pd.DataFrame(perf_data)
        print(perf_df.to_string(index=False))
        
        # Best Models
        print("\n### Best Models")
        print("-" * 50)
        best_f1 = df['f1_mean'].idxmax()
        best_roc = df['roc_auc_mean'].idxmax()
        print(f"Best F1 Score:  {best_f1} ({df.loc[best_f1, 'f1_mean']:.4f}±{df.loc[best_f1, 'f1_std']:.4f})")
        print(f"Best ROC-AUC:   {best_roc} ({df.loc[best_roc, 'roc_auc_mean']:.4f}±{df.loc[best_roc, 'roc_auc_std']:.4f})")
        
        # Resource Usage Summary
        print("\n### Resource Usage & Efficiency")
        print("-" * 80)
        
        # Training Efficiency
        print("\n#### Training Performance:")
        eff_data = []
        for model in df.index:
            # Calculate parallelism speedup, handle division by zero
            multi_core_time = df.loc[model, 'wall_time']
            single_core_time = df.loc[model, 'single_core_wall_time']
            
            if multi_core_time > 0:
                speedup = f"{(single_core_time / multi_core_time):.2f}x"
                cpu_efficiency = f"{(df.loc[model, 'cpu_time']/multi_core_time*100):.1f}%"
            else:
                speedup = "N/A"
                cpu_efficiency = "N/A"

            eff_data.append({
                'Model': model,
                'Wall Time (Multi-Core, s)': f"{multi_core_time:.3f}",
                'Wall Time (Single-Core, s)': f"{single_core_time:.3f}",
                'Total CPU Time (s)': f"{df.loc[model, 'cpu_time']:.3f}",
                'CPU Efficiency': cpu_efficiency,
                'Parallelism Speedup': speedup,
            })
        
        eff_df = pd.DataFrame(eff_data)
        print(eff_df.to_string(index=False))
        
        # Memory Usage
        print("\n#### Memory Consumption:")
        mem_data = []
        for model in df.index:
            mem_data.append({
                'Model': model,
                'Peak Memory (MB)': f"{df.loc[model, 'memory_peak_mb']:.2f}",
                'Memory Used (MB)': f"{df.loc[model, 'memory_used_mb']:.2f}",
                'Model Size (MB)': f"{df.loc[model, 'model_size_mb']:.2f}",
                'Total Footprint (MB)': f"{df.loc[model, 'memory_peak_mb'] + df.loc[model, 'model_size_mb']:.2f}"
            })
        
        mem_df = pd.DataFrame(mem_data)
        print(mem_df.to_string(index=False))
        
        # Energy Consumption
        print("\n#### Estimated Energy Consumption:")
        energy_data = []
        for model in df.index:
            energy_data.append({
                'Model': model,
                'Total Energy (J)': f"{df.loc[model, 'total_energy_joules']:.1f}",
                'Energy (kWh)': f"{df.loc[model, 'energy_kwh']:.6f}",
                'CO2 (grams)': f"{df.loc[model, 'co2_grams']:.3f}",
                'Energy/Score': f"{df.loc[model, 'total_energy_joules']/df.loc[model, 'f1_mean']:.1f}"
            })
        
        energy_df = pd.DataFrame(energy_data)
        print(energy_df.to_string(index=False))
        
        # Best model detailed analysis
        print("\n### Best Model (F1) Detailed Resource Analysis")
        print("-" * 80)
        print(f"Model: {best_f1}")
        print(f"F1 Score: {df.loc[best_f1, 'f1_mean']:.4f}")
        print("\nResource Profile:")
        print(f"  • Training Time: {df.loc[best_f1, 'wall_time']:.3f} seconds")
        print(f"  • CPU Utilization: {(df.loc[best_f1, 'cpu_time']/df.loc[best_f1, 'wall_time']*100):.1f}%")
        print(f"  • Peak Memory: {df.loc[best_f1, 'memory_peak_mb']:.2f} MB")
        print(f"  • Model Size: {df.loc[best_f1, 'model_size_mb']:.2f} MB")
        print(f"  • Energy Used: {df.loc[best_f1, 'energy_kwh']:.6f} kWh")
        print(f"  • CO2 Emissions: {df.loc[best_f1, 'co2_grams']:.2f} grams")
        print(f"  • Efficiency Score (F1/Energy): {df.loc[best_f1, 'f1_mean']/df.loc[best_f1, 'total_energy_joules']*1000:.4f}")
        
        # System Information
        print("\n### System Information")
        print("-" * 50)
        print(f"CPU Count: {self.system_info['cpu_count']}")
        print(f"CPU Frequency: {self.system_info['cpu_freq']:.0f} MHz" if self.system_info['cpu_freq'] else "CPU Frequency: N/A")
        print(f"Total Memory: {self.system_info['total_memory']/(1024**3):.1f} GB")
        print(f"Platform: {self.system_info['platform']}")
        print(f"Python Version: {self.system_info['python_version']}")
        
        # Statistical Testing Results
        if stat_results:
            print("\n### Statistical Testing Results")
            print("-" * 80)
            
            # Friedman Test Results
            print("\n1. FRIEDMAN TEST (Overall Comparison)")
            print(f"   F1 Score:   χ² = {stat_results['friedman_f1']['statistic']:.2f}, p = {stat_results['friedman_f1']['p_value']:.4f}")
            print(f"               {stat_results['friedman_f1']['interpretation']}")
            print(f"   ROC-AUC:    χ² = {stat_results['friedman_roc']['statistic']:.2f}, p = {stat_results['friedman_roc']['p_value']:.4f}")
            print(f"               {stat_results['friedman_roc']['interpretation']}")
            
            # Average Ranks
            print("\n2. AVERAGE RANKS (lower is better)")
            rank_data = []
            for model in stat_results['average_ranks']['f1'].keys():
                rank_data.append({
                    'Model': model,
                    'F1 Rank': f"{stat_results['average_ranks']['f1'][model]:.2f}",
                    'ROC Rank': f"{stat_results['average_ranks']['roc_auc'][model]:.2f}"
                })
            rank_df = pd.DataFrame(rank_data)
            print(rank_df.to_string(index=False))
            
            # Nemenyi Critical Difference
            print(f"\n3. NEMENYI CRITICAL DIFFERENCE")
            print(f"   CD = {stat_results['nemenyi_critical_difference']:.3f}")
            print(f"   (Models with rank difference > {stat_results['nemenyi_critical_difference']:.3f} are significantly different)")
            
            # Significant Pairwise Differences
            print("\n4. PAIRWISE COMPARISONS (Wilcoxon signed-rank test)")
            print("-" * 80)
            
            # Count significant differences
            sig_f1_uncorrected = sum(1 for v in stat_results['pairwise_f1'].values() if v['significant_uncorrected'])
            sig_f1_bonferroni = sum(1 for v in stat_results['pairwise_f1'].values() if v['significant_bonferroni'])
            sig_roc_uncorrected = sum(1 for v in stat_results['pairwise_roc'].values() if v['significant_uncorrected'])
            sig_roc_bonferroni = sum(1 for v in stat_results['pairwise_roc'].values() if v['significant_bonferroni'])
            
            n_pairs = len(stat_results['pairwise_f1'])
            
            print(f"\n   F1 Score Comparisons:")
            print(f"   - Significant (p < 0.05): {sig_f1_uncorrected}/{n_pairs} pairs")
            print(f"   - Significant (Bonferroni corrected): {sig_f1_bonferroni}/{n_pairs} pairs")
            
            print(f"\n   ROC-AUC Comparisons:")
            print(f"   - Significant (p < 0.05): {sig_roc_uncorrected}/{n_pairs} pairs")
            print(f"   - Significant (Bonferroni corrected): {sig_roc_bonferroni}/{n_pairs} pairs")
            
            # Detailed pairwise results
            print("\n5. DETAILED PAIRWISE RESULTS")
            print("-" * 80)
            
            # F1 Score Pairwise
            print("\n   F1 Score (Bonferroni-corrected significant differences):")
            sig_pairs_f1 = [(k, v) for k, v in stat_results['pairwise_f1'].items() 
                            if v['significant_bonferroni']]
            if sig_pairs_f1:
                for pair_name, data in sig_pairs_f1:
                    print(f"   • {pair_name}:")
                    print(f"     - p-value: {data['p_value']:.6f}")
                    print(f"     - Better model: {data['better_model']}")
                    print(f"     - Effect size: {data['effect_size']:.3f}")
                    print(f"     - Nemenyi significant: {'Yes' if data['nemenyi_significant'] else 'No'}")
            else:
                print("     No significant differences after Bonferroni correction")
            
            # ROC-AUC Pairwise
            print("\n   ROC-AUC (Bonferroni-corrected significant differences):")
            sig_pairs_roc = [(k, v) for k, v in stat_results['pairwise_roc'].items() 
                             if v['significant_bonferroni']]
            if sig_pairs_roc:
                for pair_name, data in sig_pairs_roc:
                    print(f"   • {pair_name}:")
                    print(f"     - p-value: {data['p_value']:.6f}")
                    print(f"     - Better model: {data['better_model']}")
                    print(f"     - Effect size: {data['effect_size']:.3f}")
                    print(f"     - Nemenyi significant: {'Yes' if data['nemenyi_significant'] else 'No'}")
            else:
                print("     No significant differences after Bonferroni correction")
            
            # Statistical Power
            print("\n6. STATISTICAL POWER")
            print("-" * 50)
            print(f"   Sample size per model: {stat_results['statistical_power']['n_samples_per_model']}")
            print(f"   Bonferroni-corrected α: {stat_results['statistical_power']['bonferroni_corrected_alpha']:.6f}")
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
                    # Handle all numpy scalar types
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
                    # Catch any other numpy objects that have tolist method
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
        
    def plot_results(self, results, stat_results, detailed_profile=None):
        """
        Create comprehensive visualization plots including resource usage.
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Set style
            plt.style.use('seaborn-v0_8-darkgrid')
            sns.set_palette("husl")
            
            # Create figure with more subplots for resource metrics
            fig = plt.figure(figsize=(20, 15))
            gs = fig.add_gridspec(4, 4, hspace=0.3, wspace=0.3)
            
            fig.suptitle(f'Comprehensive Model Benchmark ({self.n_runs} runs × {self.cv_folds} folds)', fontsize=16)
            
            model_names = list(self.detailed_scores.keys())
            colors = plt.cm.Set3(np.linspace(0, 1, len(model_names)))
            
            # 1. F1 Score Distribution
            ax1 = fig.add_subplot(gs[0, 0])
            f1_data = [self.detailed_scores[name]['f1'] for name in model_names]
            bp1 = ax1.boxplot(f1_data, labels=model_names, patch_artist=True)
            ax1.set_title('F1 Score Distribution')
            ax1.set_ylabel('F1 Score')
            ax1.grid(True, alpha=0.3)
            for patch, color in zip(bp1['boxes'], colors):
                patch.set_facecolor(color)
            
            # 2. ROC-AUC Distribution
            ax2 = fig.add_subplot(gs[0, 1])
            roc_data = [self.detailed_scores[name]['roc_auc'] for name in model_names]
            bp2 = ax2.boxplot(roc_data, labels=model_names, patch_artist=True)
            ax2.set_title('ROC-AUC Distribution')
            ax2.set_ylabel('ROC-AUC')
            ax2.grid(True, alpha=0.3)
            for patch, color in zip(bp2['boxes'], colors):
                patch.set_facecolor(color)
            
            # 3. Training Time Distribution
            ax3 = fig.add_subplot(gs[0, 2])
            time_data = [self.detailed_scores[name]['fit_times'] for name in model_names]
            bp3 = ax3.boxplot(time_data, labels=model_names, patch_artist=True)
            ax3.set_title('Training Time Distribution')
            ax3.set_ylabel('Time (seconds)')
            ax3.grid(True, alpha=0.3)
            for patch, color in zip(bp3['boxes'], colors):
                patch.set_facecolor(color)
            
            # 4. Memory Usage Comparison
            ax4 = fig.add_subplot(gs[0, 3])
            df = pd.DataFrame(results).T
            memory_data = df[['memory_peak_mb', 'model_size_mb']].values
            x = np.arange(len(model_names))
            width = 0.35
            ax4.bar(x - width/2, df['memory_peak_mb'], width, label='Peak Memory', alpha=0.8)
            ax4.bar(x + width/2, df['model_size_mb'], width, label='Model Size', alpha=0.8)
            ax4.set_xlabel('Model')
            ax4.set_ylabel('Memory (MB)')
            ax4.set_title('Memory Usage Comparison')
            ax4.set_xticks(x)
            ax4.set_xticklabels(model_names, rotation=45)
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            # Continue with more plots...
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
    dataset_id = 43
    dataset = fetch_ucirepo(id=dataset_id)
    
    # Data preparation
    X = dataset.data.features.copy()
    y = dataset.data.targets
    
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y.values.ravel())
    y = np.where(np.isin(y, [2, 3, 4, 5]), 1, y)
    
    # Identify categorical columns
    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
    
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
    print(f"Target distribution: {np.bincount(y)}")
    print(f"Categorical features: {len(categorical_cols)}")
    print(f"Numerical features: {len(numeric_cols)}")
    
    # Run comprehensive benchmark
    benchmark = ModelBenchmark(
        X=X, 
        y=y, 
        categorical_cols=categorical_cols,
        n_trials=200,    # Number of Optuna trials for hyperparameter optimization
        cv_folds=10,     # Number of CV folds per run
        n_runs=30,       # Number of repeated runs for statistical significance
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