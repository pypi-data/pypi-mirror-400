#!/usr/bin/env python3
"""
Analyze HD dataset benchmark results and provide recommendations for improving LinearBoost variants.
"""

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd

def load_hd_results():
    """Load all HD benchmark result files."""
    results_dir = Path("benchmark_results")
    hd_files = sorted(results_dir.glob("hd_*.json"))
    
    all_results = []
    for file_path in hd_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            all_results.append({
                'file': file_path.name,
                'dataset': file_path.stem,
                'data': data
            })
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
    
    return all_results

def analyze_performance(results_list):
    """Analyze LinearBoost performance across all HD datasets."""
    analysis = {
        'datasets': [],
        'linearboost_l': [],
        'linearboost_k': [],
        'linearboost_k_exact': [],
        'xgboost': [],
        'lightgbm': [],
        'catboost': [],
        'randomforest': [],
        'logisticregression': [],
        'tabpfn': []
    }
    
    for result in results_list:
        dataset_name = result['dataset']
        data = result['data']
        
        if 'results' not in data:
            continue
        
        results = data['results']
        dataset_info = {
            'name': dataset_name,
            'n_samples': results.get('LinearBoost-L', {}).get('n_samples', 0),
            'n_features': results.get('LinearBoost-L', {}).get('n_features', 0)
        }
        analysis['datasets'].append(dataset_info)
        
        # Extract metrics for each model
        for model_key, model_list in analysis.items():
            if model_key == 'datasets':
                continue
            
            # Map model names
            model_name_map = {
                'linearboost_l': 'LinearBoost-L',
                'linearboost_k': 'LinearBoost-K',
                'linearboost_k_exact': 'LinearBoost-K-exact',
                'xgboost': 'XGBoost',
                'lightgbm': 'LightGBM',
                'catboost': 'CatBoost',
                'randomforest': 'RandomForest',
                'logisticregression': 'LogisticRegression',
                'tabpfn': 'TabPFN'
            }
            
            model_name = model_name_map[model_key]
            
            if model_name in results:
                model_data = results[model_name]
                model_list.append({
                    'dataset': dataset_name,
                    'f1_mean': model_data.get('f1_mean', 0),
                    'f1_std': model_data.get('f1_std', 0),
                    'roc_auc_mean': model_data.get('roc_auc_mean', 0),
                    'roc_auc_std': model_data.get('roc_auc_std', 0),
                    'single_core_wall_time': model_data.get('single_core_wall_time', 0),
                    'model_size_mb': model_data.get('model_size_mb', 0),
                    'best_params': model_data.get('best_params', {})
                })
            else:
                model_list.append(None)
    
    return analysis

def extract_statistical_comparisons(results_list):
    """Extract pairwise statistical comparisons."""
    comparisons = []
    
    for result in results_list:
        data = result['data']
        
        if 'statistical_results' not in data:
            continue
        
        stats = data['statistical_results']
        dataset = result['dataset']
        
        # Extract pairwise comparisons for LinearBoost variants
        for metric in ['pairwise_f1', 'pairwise_roc']:
            if metric in stats:
                for pair_name, comparison in stats[metric].items():
                    if 'LinearBoost' in pair_name and comparison.get('nemenyi_significant', False):
                        model1, model2 = pair_name.split('_vs_')
                        comparisons.append({
                            'dataset': dataset,
                            'metric': metric.replace('pairwise_', ''),
                            'model1': model1,
                            'model2': model2,
                            'better_model': comparison.get('better_model'),
                            'significant': comparison.get('nemenyi_significant', False),
                            'rank_difference': comparison.get('rank_difference', 0),
                            'cohens_d': comparison.get('cohens_d', 0)
                        })
    
    return comparisons

def analyze_parameter_patterns(analysis):
    """Analyze parameter patterns for LinearBoost variants."""
    patterns = {
        'LinearBoost-L': {
            'n_estimators': [],
            'learning_rate': [],
            'algorithm': [],
            'scaler': [],
            'subsample': []
        },
        'LinearBoost-K': {
            'n_estimators': [],
            'learning_rate': [],
            'algorithm': [],
            'scaler': [],
            'kernel': [],
            'gamma': [],
            'kernel_approx': [],
            'n_components': [],
            'subsample': []
        },
        'LinearBoost-K-exact': {
            'n_estimators': [],
            'learning_rate': [],
            'algorithm': [],
            'scaler': [],
            'kernel': [],
            'gamma': [],
            'subsample': []
        }
    }
    
    for model_key in ['linearboost_l', 'linearboost_k', 'linearboost_k_exact']:
        model_name_map = {
            'linearboost_l': 'LinearBoost-L',
            'linearboost_k': 'LinearBoost-K',
            'linearboost_k_exact': 'LinearBoost-K-exact'
        }
        model_name = model_name_map[model_key]
        
        for result in analysis[model_key]:
            if result and 'best_params' in result:
                params = result['best_params']
                for param_name in patterns[model_name]:
                    if param_name in params:
                        patterns[model_name][param_name].append(params[param_name])
    
    return patterns

def generate_recommendations(analysis, comparisons):
    """Generate recommendations based on analysis."""
    recommendations = []
    
    # Calculate average performance
    lb_l_perf = [r['roc_auc_mean'] for r in analysis['linearboost_l'] if r]
    lb_k_perf = [r['roc_auc_mean'] for r in analysis['linearboost_k'] if r]
    lb_kx_perf = [r['roc_auc_mean'] for r in analysis['linearboost_k_exact'] if r]
    xgb_perf = [r['roc_auc_mean'] for r in analysis['xgboost'] if r]
    lgb_perf = [r['roc_auc_mean'] for r in analysis['lightgbm'] if r]
    cat_perf = [r['roc_auc_mean'] for r in analysis['catboost'] if r]
    
    # Performance gaps
    if lb_l_perf and xgb_perf:
        avg_lb_l = np.mean(lb_l_perf)
        avg_xgb = np.mean(xgb_perf)
        gap_l = avg_xgb - avg_lb_l
        recommendations.append(f"LinearBoost-L is {gap_l:.4f} ROC-AUC behind XGBoost on average")
    
    if lb_k_perf and xgb_perf:
        avg_lb_k = np.mean(lb_k_perf)
        avg_xgb = np.mean(xgb_perf)
        gap_k = avg_xgb - avg_lb_k
        recommendations.append(f"LinearBoost-K is {gap_k:.4f} ROC-AUC behind XGBoost on average")
    
    if lb_kx_perf and xgb_perf:
        avg_lb_kx = np.mean(lb_kx_perf)
        avg_xgb = np.mean(xgb_perf)
        gap_kx = avg_xgb - avg_lb_kx
        recommendations.append(f"LinearBoost-K-exact is {gap_kx:.4f} ROC-AUC behind XGBoost on average")
    
    # Analyze losses
    lb_losses = defaultdict(int)
    for comp in comparisons:
        if comp['better_model'] != comp['model1'] and 'LinearBoost' in comp['model1']:
            lb_losses[comp['model1']] += 1
        elif comp['better_model'] != comp['model2'] and 'LinearBoost' in comp['model2']:
            lb_losses[comp['model2']] += 1
    
    # Analyze parameter patterns
    patterns = analyze_parameter_patterns(analysis)
    
    return recommendations, patterns, lb_losses

def print_analysis(analysis, comparisons):
    """Print comprehensive analysis."""
    print("=" * 100)
    print("HD DATASET BENCHMARK ANALYSIS FOR LINEARBOOST IMPROVEMENTS")
    print("=" * 100)
    print()
    
    # Dataset information
    print("DATASETS ANALYZED:")
    print("-" * 100)
    for ds in analysis['datasets']:
        print(f"  - {ds['name']}: {ds['n_samples']} samples, {ds['n_features']} features")
    print()
    
    # Performance summary
    print("PERFORMANCE SUMMARY (ROC-AUC Mean):")
    print("-" * 100)
    print(f"{'Model':<25} {'Mean ROC-AUC':<15} {'Std ROC-AUC':<15} {'Mean F1':<15} {'Mean Time (s)':<15}")
    print("-" * 100)
    
    model_map = {
        'linearboost_l': 'LinearBoost-L',
        'linearboost_k': 'LinearBoost-K',
        'linearboost_k_exact': 'LinearBoost-K-exact',
        'xgboost': 'XGBoost',
        'lightgbm': 'LightGBM',
        'catboost': 'CatBoost',
        'randomforest': 'RandomForest',
        'logisticregression': 'LogisticRegression',
        'tabpfn': 'TabPFN'
    }
    
    for key, name in model_map.items():
        results = [r for r in analysis[key] if r]
        if results:
            roc_aucs = [r['roc_auc_mean'] for r in results]
            f1_scores = [r['f1_mean'] for r in results]
            times = [r['single_core_wall_time'] for r in results if r['single_core_wall_time'] > 0]
            
            print(f"{name:<25} {np.mean(roc_aucs):<15.4f} {np.std(roc_aucs):<15.4f} "
                  f"{np.mean(f1_scores):<15.4f} {np.mean(times) if times else 0:<15.4f}")
    print()
    
    # Statistical comparison summary
    print("LINEARBOOST VARIANTS vs OTHER ALGORITHMS (Significant Comparisons Only):")
    print("-" * 100)
    
    lb_vs_others = defaultdict(lambda: {'wins': 0, 'losses': 0})
    
    for comp in comparisons:
        if 'LinearBoost' in comp['model1'] and 'LinearBoost' not in comp['model2']:
            if comp['better_model'] == comp['model1']:
                lb_vs_others[comp['model1']]['wins'] += 1
            else:
                lb_vs_others[comp['model1']]['losses'] += 1
        elif 'LinearBoost' in comp['model2'] and 'LinearBoost' not in comp['model1']:
            if comp['better_model'] == comp['model2']:
                lb_vs_others[comp['model2']]['wins'] += 1
            else:
                lb_vs_others[comp['model2']]['losses'] += 1
    
    for lb_variant, stats in lb_vs_others.items():
        total = stats['wins'] + stats['losses']
        if total > 0:
            win_rate = stats['wins'] / total * 100
            print(f"{lb_variant}: {stats['wins']} wins, {stats['losses']} losses ({win_rate:.1f}% win rate)")
    print()
    
    # Parameter analysis
    patterns = analyze_parameter_patterns(analysis)
    print("PARAMETER PATTERNS:")
    print("-" * 100)
    
    for model_name, params in patterns.items():
        print(f"\n{model_name}:")
        for param_name, values in params.items():
            if values:
                if isinstance(values[0], (int, float)):
                    print(f"  {param_name}: mean={np.mean(values):.4f}, std={np.std(values):.4f}, "
                          f"min={np.min(values):.4f}, max={np.max(values):.4f}")
                elif isinstance(values[0], str) or isinstance(values[0], bool):
                    from collections import Counter
                    counts = Counter(values)
                    print(f"  {param_name}: {dict(counts)}")
    
    print()
    
    # Generate recommendations
    recs, patterns, losses = generate_recommendations(analysis, comparisons)
    
    print("RECOMMENDATIONS FOR IMPROVING LINEARBOOST:")
    print("=" * 100)
    
    # Analyze where LinearBoost loses
    print("\n1. COMPETITIVE ANALYSIS:")
    print("-" * 100)
    for lb_variant in ['LinearBoost-L', 'LinearBoost-K', 'LinearBoost-K-exact']:
        if lb_variant in losses:
            print(f"   {lb_variant} has {losses[lb_variant]} significant losses against other algorithms")
    
    # Performance gaps
    print("\n2. PERFORMANCE GAPS:")
    print("-" * 100)
    for rec in recs:
        print(f"   - {rec}")
    
    # Parameter recommendations
    print("\n3. PARAMETER TUNING RECOMMENDATIONS:")
    print("-" * 100)
    
    # Analyze what works best
    for model_name, params in patterns.items():
        print(f"\n   {model_name}:")
        
        # Learning rate analysis
        if 'learning_rate' in params and params['learning_rate']:
            lr_values = params['learning_rate']
            avg_lr = np.mean(lr_values)
            if avg_lr < 0.1:
                print(f"     → Consider higher learning rates (current avg: {avg_lr:.4f})")
            elif avg_lr > 0.3:
                print(f"     → Consider lower learning rates for better convergence (current avg: {avg_lr:.4f})")
        
        # N_estimators analysis
        if 'n_estimators' in params and params['n_estimators']:
            n_est_values = params['n_estimators']
            avg_n_est = np.mean(n_est_values)
            print(f"     → Average n_estimators: {avg_n_est:.1f} (range: {np.min(n_est_values):.0f}-{np.max(n_est_values):.0f})")
            if avg_n_est < 100:
                print(f"       Consider more estimators for better performance")
        
        # Algorithm preference
        if 'algorithm' in params and params['algorithm']:
            from collections import Counter
            algo_counts = Counter(params['algorithm'])
            print(f"     → Algorithm preference: {dict(algo_counts)}")
        
        # Scaler preference
        if 'scaler' in params and params['scaler']:
            from collections import Counter
            scaler_counts = Counter(params['scaler'])
            print(f"     → Scaler preference: {dict(scaler_counts)}")
            most_common = scaler_counts.most_common(1)[0][0]
            print(f"       Most common: {most_common}")
        
        # For LinearBoost-K: kernel analysis
        if model_name.startswith('LinearBoost-K'):
            if 'kernel' in params and params['kernel']:
                from collections import Counter
                kernel_counts = Counter(params['kernel'])
                print(f"     → Kernel preference: {dict(kernel_counts)}")
            
            if 'kernel_approx' in params and params['kernel_approx']:
                from collections import Counter
                approx_counts = Counter(params['kernel_approx'])
                print(f"     → Kernel approximation preference: {dict(approx_counts)}")
            
            if 'gamma' in params and params['gamma']:
                gamma_values = params['gamma']
                print(f"     → Gamma range: {np.min(gamma_values):.4f} - {np.max(gamma_values):.4f} "
                      f"(mean: {np.mean(gamma_values):.4f})")
    
    print("\n4. SPECIFIC IMPROVEMENT RECOMMENDATIONS:")
    print("-" * 100)
    
    # Compare with best performers
    best_models = {}
    for model_key, name in model_map.items():
        results = [r for r in analysis[model_key] if r]
        if results:
            roc_aucs = [r['roc_auc_mean'] for r in results]
            best_models[name] = np.mean(roc_aucs)
    
    sorted_models = sorted(best_models.items(), key=lambda x: x[1], reverse=True)
    
    print("\n   Model Rankings (by ROC-AUC):")
    for i, (model, score) in enumerate(sorted_models, 1):
        print(f"     {i}. {model}: {score:.4f}")
    
    # Find where LinearBoost variants rank
    lb_ranks = {}
    for lb_variant in ['LinearBoost-L', 'LinearBoost-K', 'LinearBoost-K-exact']:
        if lb_variant in best_models:
            rank = next(i for i, (m, _) in enumerate(sorted_models, 1) if m == lb_variant)
            lb_ranks[lb_variant] = rank
    
    print("\n   LinearBoost Rankings:")
    for variant, rank in sorted(lb_ranks.items(), key=lambda x: x[1]):
        print(f"     {variant}: Rank {rank}/{len(sorted_models)}")
    
    # Specific recommendations
    print("\n   Key Recommendations:")
    
    # Find best performing non-LinearBoost model
    non_lb_models = [(m, s) for m, s in sorted_models if not m.startswith('LinearBoost')]
    if non_lb_models:
        best_non_lb = non_lb_models[0]
        print(f"     → Best competitor: {best_non_lb[0]} (ROC-AUC: {best_non_lb[1]:.4f})")
        
        for lb_variant in ['LinearBoost-L', 'LinearBoost-K', 'LinearBoost-K-exact']:
            if lb_variant in best_models:
                gap = best_non_lb[1] - best_models[lb_variant]
                if gap > 0.01:  # Significant gap
                    print(f"     → {lb_variant} is {gap:.4f} behind {best_non_lb[0]}")
    
    # Check if kernel approximation helps or hurts
    if 'LinearBoost-K' in best_models and 'LinearBoost-K-exact' in best_models:
        k_perf = best_models['LinearBoost-K']
        kx_perf = best_models['LinearBoost-K-exact']
        if kx_perf > k_perf:
            print(f"\n     → LinearBoost-K-exact performs better than LinearBoost-K")
            print(f"       (gap: {kx_perf - k_perf:.4f}), suggesting kernel approximation")
            print(f"       may be limiting performance. Consider:")
            print(f"       - Using exact kernels for critical datasets")
            print(f"       - Improving approximation quality (more components)")
            print(f"       - Adaptive approximation based on dataset size")
        else:
            print(f"\n     → LinearBoost-K performs better than LinearBoost-K-exact")
            print(f"       (gap: {k_perf - kx_perf:.4f}), suggesting approximation")
            print(f"       helps with overfitting or computational benefits")
    
    # Check algorithm preference
    print("\n     → Algorithm Selection:")
    for model_name in ['LinearBoost-L', 'LinearBoost-K', 'LinearBoost-K-exact']:
        if model_name in patterns and 'algorithm' in patterns[model_name]:
            algo_counts = Counter(patterns[model_name]['algorithm'])
            if algo_counts:
                most_common_algo = algo_counts.most_common(1)[0][0]
                print(f"       {model_name}: Prefers {most_common_algo} "
                      f"({algo_counts[most_common_algo]}/{sum(algo_counts.values())} times)")
    
    # Feature scaling recommendations
    print("\n     → Feature Scaling:")
    for model_name in ['LinearBoost-L', 'LinearBoost-K', 'LinearBoost-K-exact']:
        if model_name in patterns and 'scaler' in patterns[model_name]:
            scaler_counts = Counter(patterns[model_name]['scaler'])
            if scaler_counts:
                print(f"       {model_name}: {dict(scaler_counts)}")
    
    print("\n" + "=" * 100)

if __name__ == "__main__":
    results_list = load_hd_results()
    
    if not results_list:
        print("No HD result files found in benchmark_results folder.")
        exit(1)
    
    print(f"Found {len(results_list)} HD result file(s)")
    for r in results_list:
        print(f"  - {r['file']}")
    print()
    
    analysis = analyze_performance(results_list)
    comparisons = extract_statistical_comparisons(results_list)
    
    print_analysis(analysis, comparisons)

