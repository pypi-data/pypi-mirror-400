#!/usr/bin/env python3
"""
Compare most recent UCI benchmark results with second most recent.
Analyze F1, AUC, training time, and inference time changes.
Compare algorithm rankings before and after.
"""

import json
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd
from collections import defaultdict
from scipy import stats

def get_most_recent_uci_json_files(results_dir: str, num_days: int = 2):
    """Get the most recent N sets of UCI JSON files, grouped by dataset."""
    results_path = Path(results_dir)
    all_uci_files = sorted(results_path.glob("uci_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    # Group by dataset name (everything before the date)
    datasets = defaultdict(list)
    for file in all_uci_files:
        # Extract dataset name: "uci_XX_Dataset Name_YYYYMMDD_HHMMSS.json"
        parts = file.stem.split('_')
        # Find where date starts (YYYYMMDD format)
        date_idx = None
        for i, part in enumerate(parts):
            if len(part) == 8 and part.isdigit() and part.startswith('2025'):
                date_idx = i
                break
        
        if date_idx:
            dataset_name = '_'.join(parts[:date_idx])
            datasets[dataset_name].append(file)
    
    # For each dataset, get the most recent N files
    recent_files_by_dataset = {}
    for dataset_name, files in datasets.items():
        # Files are already sorted by modification time (most recent first)
        recent_files_by_dataset[dataset_name] = files[:num_days]
    
    return recent_files_by_dataset

def load_json_file(file_path: Path):
    """Load a JSON benchmark result file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def extract_all_metrics(data):
    """Extract all metrics from benchmark results."""
    if not data or 'results' not in data:
        return {}
    
    metrics = {}
    for model_name, model_results in data['results'].items():
        if isinstance(model_results, dict):
            metrics[model_name] = {
                'f1_mean': model_results.get('f1_mean', 0),
                'f1_std': model_results.get('f1_std', 0),
                'roc_auc_mean': model_results.get('roc_auc_mean', 0),
                'roc_auc_std': model_results.get('roc_auc_std', 0),
                'avg_fit_time': model_results.get('avg_fit_time', 0),
                'avg_score_time': model_results.get('avg_score_time', 0),
                'inference_single_ms': model_results.get('inference_single_ms', 0),
            }
    return metrics

def calculate_rankings(metrics_dict):
    """Calculate rankings for each metric."""
    rankings = {
        'f1': {},
        'roc_auc': {},
        'fit_time': {},  # Lower is better
        'score_time': {},  # Lower is better
    }
    
    # F1 rankings (higher is better)
    f1_scores = {name: m.get('f1_mean', 0) for name, m in metrics_dict.items()}
    f1_ranks = {name: rank for rank, name in enumerate(sorted(f1_scores, key=f1_scores.get, reverse=True), 1)}
    rankings['f1'] = f1_ranks
    
    # ROC-AUC rankings (higher is better)
    roc_scores = {name: m.get('roc_auc_mean', 0) for name, m in metrics_dict.items() if m.get('roc_auc_mean', 0) > 0}
    roc_ranks = {name: rank for rank, name in enumerate(sorted(roc_scores, key=roc_scores.get, reverse=True), 1)}
    rankings['roc_auc'] = roc_ranks
    
    # Training time rankings (lower is better)
    fit_times = {name: m.get('fit_time_mean', 0) for name, m in metrics_dict.items() if m.get('fit_time_mean', 0) > 0}
    if not fit_times:  # Fallback to avg_fit_time
        fit_times = {name: m.get('avg_fit_time', 0) for name, m in metrics_dict.items() if m.get('avg_fit_time', 0) > 0}
    fit_ranks = {name: rank for rank, name in enumerate(sorted(fit_times, key=fit_times.get), 1)}
    rankings['fit_time'] = fit_ranks
    
    # Inference time rankings (lower is better)
    score_times = {name: m.get('score_time_mean', 0) for name, m in metrics_dict.items() if m.get('score_time_mean', 0) > 0}
    if not score_times:
        score_times = {name: m.get('inference_single_ms', 0) for name, m in metrics_dict.items() if m.get('inference_single_ms', 0) > 0}
    if not score_times:  # Fallback to avg_score_time
        score_times = {name: m.get('avg_score_time', 0) * 1000 for name, m in metrics_dict.items() if m.get('avg_score_time', 0) > 0}
    score_ranks = {name: rank for rank, name in enumerate(sorted(score_times, key=score_times.get), 1)}
    rankings['score_time'] = score_ranks
    
    return rankings

def aggregate_metrics_across_datasets(all_new_metrics, all_previous_metrics):
    """Aggregate metrics across all datasets for each model."""
    aggregated_new = defaultdict(lambda: {
        'f1': [], 'roc_auc': [], 'fit_time': [], 'score_time': []
    })
    aggregated_previous = defaultdict(lambda: {
        'f1': [], 'roc_auc': [], 'fit_time': [], 'score_time': []
    })
    
    # Collect all metrics for each model across datasets
    for dataset_metrics in all_new_metrics.values():
        for model_name, metrics in dataset_metrics.items():
            aggregated_new[model_name]['f1'].append(metrics['f1_mean'])
            aggregated_new[model_name]['roc_auc'].append(metrics['roc_auc_mean'])
            aggregated_new[model_name]['fit_time'].append(metrics['avg_fit_time'])
            score_time = metrics.get('inference_single_ms', 0)
            if score_time == 0:
                score_time = metrics.get('avg_score_time', 0) * 1000
            aggregated_new[model_name]['score_time'].append(score_time)
    
    for dataset_metrics in all_previous_metrics.values():
        for model_name, metrics in dataset_metrics.items():
            aggregated_previous[model_name]['f1'].append(metrics['f1_mean'])
            aggregated_previous[model_name]['roc_auc'].append(metrics['roc_auc_mean'])
            aggregated_previous[model_name]['fit_time'].append(metrics['avg_fit_time'])
            score_time = metrics.get('inference_single_ms', 0)
            if score_time == 0:
                score_time = metrics.get('avg_score_time', 0) * 1000
            aggregated_previous[model_name]['score_time'].append(score_time)
    
    # Calculate means
    def calc_means(agg_dict):
        result = {}
        for model_name, values in agg_dict.items():
            result[model_name] = {
                'f1_mean': np.mean(values['f1']) if values['f1'] else 0,
                'roc_auc_mean': np.mean(values['roc_auc']) if values['roc_auc'] else 0,
                'fit_time_mean': np.mean(values['fit_time']) if values['fit_time'] else 0,
                'score_time_mean': np.mean(values['score_time']) if values['score_time'] else 0,
            }
        return result
    
    return calc_means(aggregated_new), calc_means(aggregated_previous)

def compare_results(new_files_dict, previous_files_dict):
    """Compare new (most recent) vs previous (second most recent) results."""
    comparison = defaultdict(lambda: {
        'f1_deltas': [],
        'roc_deltas': [],
        'fit_time_deltas': [],
        'score_time_deltas': [],
        'datasets': [],
    })
    
    all_new_metrics = {}
    all_previous_metrics = {}
    
    # Find common datasets
    common_datasets = set(new_files_dict.keys()) & set(previous_files_dict.keys())
    
    for dataset in sorted(common_datasets):
        new_files = new_files_dict[dataset]
        previous_files = previous_files_dict[dataset]
        
        if len(new_files) == 0 or len(previous_files) == 0:
            continue
        
        # Use most recent file for new, second most recent for previous
        new_file = new_files[0] if len(new_files) > 0 else None
        previous_file = previous_files[1] if len(previous_files) > 1 else previous_files[0] if len(previous_files) > 0 else None
        
        if not new_file or not previous_file:
            continue
        
        new_data = load_json_file(new_file)
        previous_data = load_json_file(previous_file)
        
        if not new_data or not previous_data:
            continue
        
        new_metrics = extract_all_metrics(new_data)
        previous_metrics = extract_all_metrics(previous_data)
        
        all_new_metrics[dataset] = new_metrics
        all_previous_metrics[dataset] = previous_metrics
        
        # Compare all models
        all_models = set(new_metrics.keys()) & set(previous_metrics.keys())
        
        for model_name in all_models:
            f1_delta = new_metrics[model_name]['f1_mean'] - previous_metrics[model_name]['f1_mean']
            roc_delta = new_metrics[model_name]['roc_auc_mean'] - previous_metrics[model_name]['roc_auc_mean']
            fit_time_delta = new_metrics[model_name]['avg_fit_time'] - previous_metrics[model_name]['avg_fit_time']
            score_time_new = new_metrics[model_name].get('inference_single_ms', 0)
            if score_time_new == 0:
                score_time_new = new_metrics[model_name].get('avg_score_time', 0) * 1000
            score_time_previous = previous_metrics[model_name].get('inference_single_ms', 0)
            if score_time_previous == 0:
                score_time_previous = previous_metrics[model_name].get('avg_score_time', 0) * 1000
            score_time_delta = score_time_new - score_time_previous
            
            comparison[model_name]['f1_deltas'].append(f1_delta)
            comparison[model_name]['roc_deltas'].append(roc_delta)
            comparison[model_name]['fit_time_deltas'].append(fit_time_delta)
            comparison[model_name]['score_time_deltas'].append(score_time_delta)
            comparison[model_name]['datasets'].append(dataset)
    
    # Calculate aggregate metrics and rankings
    new_aggregated, previous_aggregated = aggregate_metrics_across_datasets(all_new_metrics, all_previous_metrics)
    new_rankings = calculate_rankings(new_aggregated)
    previous_rankings = calculate_rankings(previous_aggregated)
    
    # Add summary statistics
    for model_name in comparison:
        if len(comparison[model_name]['f1_deltas']) > 0:
            comparison[model_name]['f1_mean_delta'] = np.mean(comparison[model_name]['f1_deltas'])
            comparison[model_name]['f1_std_delta'] = np.std(comparison[model_name]['f1_deltas'])
            comparison[model_name]['roc_mean_delta'] = np.mean(comparison[model_name]['roc_deltas'])
            comparison[model_name]['roc_std_delta'] = np.std(comparison[model_name]['roc_deltas'])
            comparison[model_name]['fit_time_mean_delta'] = np.mean(comparison[model_name]['fit_time_deltas'])
            comparison[model_name]['score_time_mean_delta'] = np.mean(comparison[model_name]['score_time_deltas'])
            
            # Rankings
            comparison[model_name]['new_rankings'] = {
                'f1': new_rankings['f1'].get(model_name, '-'),
                'roc_auc': new_rankings['roc_auc'].get(model_name, '-'),
                'fit_time': new_rankings['fit_time'].get(model_name, '-'),
                'score_time': new_rankings['score_time'].get(model_name, '-'),
            }
            comparison[model_name]['previous_rankings'] = {
                'f1': previous_rankings['f1'].get(model_name, '-'),
                'roc_auc': previous_rankings['roc_auc'].get(model_name, '-'),
                'fit_time': previous_rankings['fit_time'].get(model_name, '-'),
                'score_time': previous_rankings['score_time'].get(model_name, '-'),
            }
    
    return comparison, new_rankings, previous_rankings

def is_linearboost(model_name):
    """Check if model is a LinearBoost variant."""
    return 'LinearBoost' in model_name

def print_comparison(comparison, new_rankings, previous_rankings):
    """Print formatted comparison results."""
    print("=" * 100)
    print("BENCHMARK COMPARISON: MOST RECENT vs SECOND MOST RECENT")
    print("=" * 100)
    
    # Separate LinearBoost variants from other models
    linearboost_models = {k: v for k, v in comparison.items() if is_linearboost(k)}
    other_models = {k: v for k, v in comparison.items() if not is_linearboost(k)}
    
    print(f"\nTotal datasets compared: {len(comparison[list(comparison.keys())[0]]['datasets'])}")
    print(f"Datasets: {', '.join([d.replace('uci_', '') for d in comparison[list(comparison.keys())[0]]['datasets']])}\n")
    
    print("\n" + "=" * 100)
    print("LINEARBOOST VARIANTS - PERFORMANCE CHANGES & RANKINGS")
    print("=" * 100)
    
    for model_name in sorted(linearboost_models.keys()):
        stats_dict = comparison[model_name]
        
        if len(stats_dict['f1_deltas']) == 0:
            continue
        
        print(f"\n{'='*100}")
        print(f"{model_name}")
        print(f"{'='*100}")
        
        # Performance Changes
        print(f"\n📊 PERFORMANCE CHANGES:")
        print(f"  F1 Score:")
        print(f"    Mean Δ: {stats_dict.get('f1_mean_delta', 0):+.4f} ± {stats_dict.get('f1_std_delta', 0):.4f}")
        improvements = sum(1 for d in stats_dict['f1_deltas'] if d > 0.001)
        regressions = sum(1 for d in stats_dict['f1_deltas'] if d < -0.001)
        print(f"    Improvements: {improvements} datasets, Regressions: {regressions} datasets")
        
        print(f"  ROC-AUC:")
        print(f"    Mean Δ: {stats_dict.get('roc_mean_delta', 0):+.4f} ± {stats_dict.get('roc_std_delta', 0):.4f}")
        improvements = sum(1 for d in stats_dict['roc_deltas'] if d > 0.001)
        regressions = sum(1 for d in stats_dict['roc_deltas'] if d < -0.001)
        print(f"    Improvements: {improvements} datasets, Regressions: {regressions} datasets")
        
        print(f"  Training Time:")
        fit_delta = stats_dict.get('fit_time_mean_delta', 0)
        fit_pct = (fit_delta / max(abs(stats_dict.get('fit_time_mean_delta', 1e-10)), 1e-10)) * 100 if stats_dict.get('fit_time_mean_delta', 0) != 0 else 0
        print(f"    Mean Δ: {fit_delta:+.4f} seconds ({fit_pct:+.1f}%)")
        improvements = sum(1 for d in stats_dict['fit_time_deltas'] if d < -0.001)  # Lower is better
        regressions = sum(1 for d in stats_dict['fit_time_deltas'] if d > 0.001)
        print(f"    Faster: {improvements} datasets, Slower: {regressions} datasets")
        
        print(f"  Inference Time:")
        score_delta = stats_dict.get('score_time_mean_delta', 0)
        print(f"    Mean Δ: {score_delta:+.4f} ms")
        improvements = sum(1 for d in stats_dict['score_time_deltas'] if d < -0.001)  # Lower is better
        regressions = sum(1 for d in stats_dict['score_time_deltas'] if d > 0.001)
        print(f"    Faster: {improvements} datasets, Slower: {regressions} datasets")
        
        # Rankings
        print(f"\n🏆 RANKINGS COMPARISON:")
        prev_ranks = stats_dict.get('previous_rankings', {})
        new_ranks = stats_dict.get('new_rankings', {})
        
        for metric in ['f1', 'roc_auc', 'fit_time', 'score_time']:
            prev_rank = prev_ranks.get(metric, '-')
            new_rank = new_ranks.get(metric, '-')
            if prev_rank != '-' and new_rank != '-':
                rank_change = new_rank - prev_rank
                arrow = "↑" if rank_change < 0 else "↓" if rank_change > 0 else "→"
                print(f"  {metric.upper():12} Previous: #{prev_rank:2} → Current: #{new_rank:2} {arrow} ({rank_change:+d})")
            elif prev_rank != '-':
                print(f"  {metric.upper():12} Previous: #{prev_rank:2} → Current: {new_rank}")
            elif new_rank != '-':
                print(f"  {metric.upper():12} Previous: {prev_rank} → Current: #{new_rank:2}")
    
    print("\n" + "=" * 100)
    print("OVERALL ALGORITHM RANKINGS - BEFORE vs AFTER")
    print("=" * 100)
    
    # Show overall rankings table
    all_models = sorted(set(list(new_rankings['f1'].keys()) + list(previous_rankings['f1'].keys())))
    
    print("\nF1 Score Rankings:")
    print(f"{'Algorithm':<25} {'Previous':<12} {'Current':<12} {'Change':<10}")
    print("-" * 60)
    for model in all_models:
        prev = previous_rankings['f1'].get(model, '-')
        new = new_rankings['f1'].get(model, '-')
        if prev != '-' and new != '-':
            change = new - prev
            arrow = "↑" if change < 0 else "↓" if change > 0 else "→"
            print(f"{model:<25} #{prev:<11} #{new:<11} {arrow} {change:+d}")
    
    print("\nROC-AUC Rankings:")
    print(f"{'Algorithm':<25} {'Previous':<12} {'Current':<12} {'Change':<10}")
    print("-" * 60)
    for model in all_models:
        prev = previous_rankings['roc_auc'].get(model, '-')
        new = new_rankings['roc_auc'].get(model, '-')
        if prev != '-' and new != '-':
            change = new - prev
            arrow = "↑" if change < 0 else "↓" if change > 0 else "→"
            print(f"{model:<25} #{prev:<11} #{new:<11} {arrow} {change:+d}")
    
    print("\nTraining Time Rankings (lower is better):")
    print(f"{'Algorithm':<25} {'Previous':<12} {'Current':<12} {'Change':<10}")
    print("-" * 60)
    for model in all_models:
        prev = previous_rankings['fit_time'].get(model, '-')
        new = new_rankings['fit_time'].get(model, '-')
        if prev != '-' and new != '-':
            change = new - prev
            arrow = "↓" if change < 0 else "↑" if change > 0 else "→"
            print(f"{model:<25} #{prev:<11} #{new:<11} {arrow} {change:+d}")
    
    print("\nInference Time Rankings (lower is better):")
    print(f"{'Algorithm':<25} {'Previous':<12} {'Current':<12} {'Change':<10}")
    print("-" * 60)
    for model in all_models:
        prev = previous_rankings['score_time'].get(model, '-')
        new = new_rankings['score_time'].get(model, '-')
        if prev != '-' and new != '-':
            change = new - prev
            arrow = "↓" if change < 0 else "↑" if change > 0 else "→"
            print(f"{model:<25} #{prev:<11} #{new:<11} {arrow} {change:+d}")

def main():
    results_dir = "benchmark_results"
    
    # Get most recent and second most recent files
    all_files = get_most_recent_uci_json_files(results_dir, num_days=2)
    
    if len(all_files) == 0:
        print("No UCI benchmark results found.")
        return
    
    # Separate into new (most recent) and previous (second most recent)
    new_files_dict = {}
    previous_files_dict = {}
    
    for dataset, files in all_files.items():
        if len(files) >= 1:
            new_files_dict[dataset] = [files[0]]  # Most recent
        if len(files) >= 2:
            previous_files_dict[dataset] = files[1:]  # Second most recent and older
    
    comparison, new_rankings, previous_rankings = compare_results(new_files_dict, previous_files_dict)
    
    print_comparison(comparison, new_rankings, previous_rankings)
    
    # Save comparison to file
    comparison_file = Path(results_dir) / "benchmark_comparison_latest.json"
    
    # Convert to JSON-serializable format
    json_comparison = {
        'datasets': comparison[list(comparison.keys())[0]]['datasets'] if comparison else [],
        'models': {
            k: {
                'f1_mean_delta': float(v.get('f1_mean_delta', 0)),
                'roc_mean_delta': float(v.get('roc_mean_delta', 0)),
                'fit_time_mean_delta': float(v.get('fit_time_mean_delta', 0)),
                'score_time_mean_delta': float(v.get('score_time_mean_delta', 0)),
                'previous_rankings': v.get('previous_rankings', {}),
                'new_rankings': v.get('new_rankings', {}),
            }
            for k, v in comparison.items()
        }
    }
    
    with open(comparison_file, 'w') as f:
        json.dump(json_comparison, f, indent=2)
    
    print(f"\n\nComparison saved to: {comparison_file}")

if __name__ == "__main__":
    main()
