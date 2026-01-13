#!/usr/bin/env python3
"""
Compare benchmark results before and after F1-aware estimator weighting.
Most recent = after, Second most recent = before
"""

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd

def get_uci_results_by_recency(results_dir="benchmark_results", prefix="uci"):
    """Get UCI results grouped by dataset, sorted by recency."""
    results_path = Path(results_dir)
    
    # Get all UCI JSON files sorted by modification time
    json_files = sorted(results_path.glob(f"{prefix}_*.json"), key=lambda x: x.stat().st_mtime)
    
    # Group by dataset (extract dataset identifier)
    datasets = defaultdict(list)
    for file_path in json_files:
        # Extract dataset key (e.g., "uci_17_Breast" from "uci_17_Breast Cancer Wisconsin...")
        parts = file_path.stem.split('_')
        if len(parts) >= 3:
            dataset_key = '_'.join(parts[:3])
        else:
            dataset_key = '_'.join(parts[:2]) if len(parts) >= 2 else parts[0]
        
        datasets[dataset_key].append(file_path)
    
    # For each dataset, get most recent (after) and second most recent (before)
    after_files = {}
    before_files = {}
    
    for dataset_key, files in datasets.items():
        if len(files) >= 2:
            # Sort by modification time (most recent last)
            sorted_files = sorted(files, key=lambda x: x.stat().st_mtime)
            after_files[dataset_key] = sorted_files[-1]  # Most recent
            before_files[dataset_key] = sorted_files[-2]  # Second most recent
    
    return after_files, before_files

def load_results(file_dict):
    """Load results from files."""
    results = defaultdict(lambda: defaultdict(dict))
    
    for dataset_key, file_path in file_dict.items():
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if 'results' not in data:
                continue
            
            dataset_name = file_path.stem.split('_', 2)[-1].split('_2025')[0] if '_2025' in file_path.stem else file_path.stem
            
            for model_name, model_data in data['results'].items():
                results[dataset_key][model_name] = {
                    'dataset': dataset_name,
                    'f1_mean': model_data.get('f1_mean', 0),
                    'f1_std': model_data.get('f1_std', 0),
                    'roc_auc_mean': model_data.get('roc_auc_mean', 0),
                    'roc_auc_std': model_data.get('roc_auc_std', 0),
                    'avg_fit_time': model_data.get('avg_fit_time', 0),
                    'avg_score_time': model_data.get('avg_score_time', 0),
                    'file': file_path.name
                }
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
            continue
    
    return results

def compare_results(before_results, after_results):
    """Compare before and after results."""
    comparison = {}
    
    # Get common datasets
    common_datasets = set(before_results.keys()).intersection(set(after_results.keys()))
    
    # Get all models
    all_models = set()
    for dataset_results in before_results.values():
        all_models.update(dataset_results.keys())
    for dataset_results in after_results.values():
        all_models.update(dataset_results.keys())
    
    # Compare each model across datasets
    for model_name in all_models:
        model_comparison = {
            'datasets': [],
            'f1_deltas': [],
            'roc_deltas': [],
            'f1_improvements': 0,
            'f1_regressions': 0,
            'roc_improvements': 0,
            'roc_regressions': 0,
        }
        
        for dataset_key in common_datasets:
            if model_name not in before_results[dataset_key] or model_name not in after_results[dataset_key]:
                continue
            
            before = before_results[dataset_key][model_name]
            after = after_results[dataset_key][model_name]
            
            f1_delta = after['f1_mean'] - before['f1_mean']
            roc_delta = after['roc_auc_mean'] - before['roc_auc_mean']
            
            model_comparison['datasets'].append(before['dataset'])
            model_comparison['f1_deltas'].append(f1_delta)
            model_comparison['roc_deltas'].append(roc_delta)
            
            if f1_delta > 0.001:  # Significant improvement
                model_comparison['f1_improvements'] += 1
            elif f1_delta < -0.001:  # Significant regression
                model_comparison['f1_regressions'] += 1
            
            if roc_delta > 0.001:
                model_comparison['roc_improvements'] += 1
            elif roc_delta < -0.001:
                model_comparison['roc_regressions'] += 1
        
        if len(model_comparison['f1_deltas']) > 0:
            model_comparison['f1_mean_delta'] = np.mean(model_comparison['f1_deltas'])
            model_comparison['f1_std_delta'] = np.std(model_comparison['f1_deltas'])
            model_comparison['roc_mean_delta'] = np.mean(model_comparison['roc_deltas'])
            model_comparison['roc_std_delta'] = np.std(model_comparison['roc_deltas'])
            model_comparison['n_datasets'] = len(model_comparison['f1_deltas'])
            
            comparison[model_name] = model_comparison
    
    return comparison

def print_analysis(comparison):
    """Print comprehensive analysis."""
    print("=" * 120)
    print("F1-AWARE ESTIMATOR WEIGHTING: BEFORE vs AFTER COMPARISON")
    print("=" * 120)
    print()
    
    # LinearBoost variants first
    lb_models = [m for m in comparison.keys() if 'LinearBoost' in m]
    other_models = [m for m in comparison.keys() if 'LinearBoost' not in m]
    
    print("LINEARBOOST VARIANTS - PERFORMANCE CHANGES:")
    print("-" * 120)
    print(f"{'Model':<25} {'F1 Δ':<12} {'F1 ±σ':<12} {'ROC Δ':<12} {'ROC ±σ':<12} {'F1 ↑':<6} {'F1 ↓':<6} {'N':<4}")
    print("-" * 120)
    
    for model_name in sorted(lb_models):
        comp = comparison[model_name]
        print(f"{model_name:<25} {comp['f1_mean_delta']:+12.6f} {comp['f1_std_delta']:<12.6f} "
              f"{comp['roc_mean_delta']:+12.6f} {comp['roc_std_delta']:<12.6f} "
              f"{comp['f1_improvements']:<6} {comp['f1_regressions']:<6} {comp['n_datasets']:<4}")
    print()
    
    print("COMPETITOR MODELS - PERFORMANCE CHANGES (For Reference):")
    print("-" * 120)
    for model_name in sorted(other_models):
        comp = comparison[model_name]
        print(f"{model_name:<25} F1: {comp['f1_mean_delta']:+8.6f} ± {comp['f1_std_delta']:.6f}, "
              f"ROC: {comp['roc_mean_delta']:+8.6f} ± {comp['roc_std_delta']:.6f} "
              f"(↑{comp['f1_improvements']}, ↓{comp['f1_regressions']}, N={comp['n_datasets']})")
    print()
    
    # Detailed LinearBoost analysis
    print("LINEARBOOST VARIANTS - DETAILED BREAKDOWN:")
    print("-" * 120)
    for model_name in sorted(lb_models):
        comp = comparison[model_name]
        print(f"\n{model_name}:")
        print(f"  Average F1 change: {comp['f1_mean_delta']:+.6f} ± {comp['f1_std_delta']:.6f}")
        print(f"  Average ROC change: {comp['roc_mean_delta']:+.6f} ± {comp['roc_std_delta']:.6f}")
        print(f"  Datasets improved (F1): {comp['f1_improvements']}/{comp['n_datasets']}")
        print(f"  Datasets regressed (F1): {comp['f1_regressions']}/{comp['n_datasets']}")
        
        if len(comp['f1_deltas']) > 0:
            max_improvement = max(comp['f1_deltas'])
            max_regression = min(comp['f1_deltas'])
            max_improvement_idx = comp['f1_deltas'].index(max_improvement)
            max_regression_idx = comp['f1_deltas'].index(max_regression)
            
            print(f"  Max F1 improvement: {max_improvement:+.6f} ({comp['datasets'][max_improvement_idx]})")
            print(f"  Max F1 regression: {max_regression:+.6f} ({comp['datasets'][max_regression_idx]})")
    
    # Statistical significance check
    print("\n" + "=" * 120)
    print("STATISTICAL ANALYSIS:")
    print("-" * 120)
    
    # Check if LinearBoost improvements are statistically significant
    for model_name in sorted(lb_models):
        comp = comparison[model_name]
        if comp['n_datasets'] >= 3:
            # One-sample t-test against zero
            mean_delta = comp['f1_mean_delta']
            std_delta = comp['f1_std_delta']
            n = comp['n_datasets']
            
            # Approximate t-test (assuming normal distribution)
            if std_delta > 0:
                t_stat = mean_delta / (std_delta / np.sqrt(n))
                # For n=7, critical t at 95% confidence ≈ 2.365
                significant = abs(t_stat) > 2.365 if n == 7 else abs(t_stat) > 2.0
            
                print(f"{model_name}:")
                print(f"  F1 change: {mean_delta:+.6f} ± {std_delta:.6f}")
                print(f"  t-statistic: {t_stat:+.4f}")
                print(f"  Statistically significant: {'YES' if significant and mean_delta > 0 else 'NO'}")
                print()
    
    # Overall recommendation
    print("=" * 120)
    print("RECOMMENDATION:")
    print("-" * 120)
    
    # Calculate overall impact for LinearBoost variants
    lb_f1_improvements = []
    lb_roc_improvements = []
    lb_f1_regressions = []
    
    for model_name in lb_models:
        comp = comparison[model_name]
        lb_f1_improvements.append(comp['f1_mean_delta'])
        lb_roc_improvements.append(comp['roc_mean_delta'])
        if comp['f1_mean_delta'] < 0:
            lb_f1_regressions.append(comp['f1_mean_delta'])
    
    avg_lb_f1_improvement = np.mean(lb_f1_improvements) if lb_f1_improvements else 0
    avg_lb_roc_improvement = np.mean(lb_roc_improvements) if lb_roc_improvements else 0
    
    # Compare to competitor changes (account for random variation)
    other_f1_changes = [comparison[m]['f1_mean_delta'] for m in other_models if m in comparison]
    avg_other_f1_change = np.mean(other_f1_changes) if other_f1_changes else 0
    
    print(f"LinearBoost Average F1 Change: {avg_lb_f1_improvement:+.6f}")
    print(f"LinearBoost Average ROC Change: {avg_lb_roc_improvement:+.6f}")
    print(f"Other Algorithms Average F1 Change: {avg_other_f1_change:+.6f}")
    print(f"Relative F1 Improvement: {avg_lb_f1_improvement - avg_other_f1_change:+.6f}")
    print()
    
    # Decision logic
    if avg_lb_f1_improvement > 0.005:  # Clear improvement > 0.5%
        recommendation = "KEEP"
        reason = f"Clear F1 improvement (+{avg_lb_f1_improvement:.6f})"
    elif avg_lb_f1_improvement > 0.001 and avg_lb_f1_improvement > avg_other_f1_change:
        recommendation = "KEEP"
        reason = f"F1 improvement (+{avg_lb_f1_improvement:.6f}) better than random variation"
    elif avg_lb_f1_improvement < -0.005:  # Clear regression
        recommendation = "REVERT"
        reason = f"Clear F1 regression ({avg_lb_f1_improvement:.6f})"
    elif avg_lb_f1_improvement < -0.001:
        recommendation = "REVERT"
        reason = f"F1 regression ({avg_lb_f1_improvement:.6f})"
    else:
        recommendation = "KEEP (MARGINAL)"
        reason = "No significant change, but no harm"
    
    print(f"DECISION: {recommendation}")
    print(f"Reason: {reason}")
    print()
    
    # Additional context
    total_improvements = sum(comparison[m]['f1_improvements'] for m in lb_models if m in comparison)
    total_regressions = sum(comparison[m]['f1_regressions'] for m in lb_models if m in comparison)
    total_datasets = sum(comparison[m]['n_datasets'] for m in lb_models if m in comparison)
    
    print(f"Overall: {total_improvements} dataset improvements, {total_regressions} regressions out of {total_datasets} total")
    
    if total_improvements > total_regressions * 1.5:
        print("✓ Improvements clearly outweigh regressions")
    elif total_regressions > total_improvements * 1.5:
        print("⚠ Regressions outweigh improvements")
    else:
        print("≈ Mixed results, consider other factors")
    
    return recommendation, avg_lb_f1_improvement

if __name__ == "__main__":
    print("Loading benchmark results...")
    
    # Get before and after files
    after_files, before_files = get_uci_results_by_recency()
    
    print(f"Found {len(after_files)} datasets with before/after comparisons")
    print(f"  Most recent (AFTER): {[f.name for f in after_files.values()]}")
    print(f"  Second most recent (BEFORE): {[f.name for f in before_files.values()]}")
    print()
    
    if len(after_files) == 0 or len(before_files) == 0:
        print("Error: Need at least 2 benchmark runs per dataset for comparison")
        exit(1)
    
    # Load results
    after_results = load_results(after_files)
    before_results = load_results(before_files)
    
    # Compare
    comparison = compare_results(before_results, after_results)
    
    # Print analysis
    recommendation, avg_improvement = print_analysis(comparison)
    
    # Save detailed comparison
    with open('f1_aware_weighting_comparison.json', 'w') as f:
        json.dump(comparison, f, indent=2, default=str)
    print(f"\n✓ Detailed comparison saved to f1_aware_weighting_comparison.json")
    
    print(f"\n{'='*120}")
    print(f"FINAL RECOMMENDATION: {recommendation}")
    print(f"{'='*120}")

