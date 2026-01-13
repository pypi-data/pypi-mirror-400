#!/usr/bin/env python3
"""
Evaluate the impact of strengthened F1 bonus (0.6 → 0.8) change.
Compare most recent results with second most recent (before the change).
"""

import json
from pathlib import Path
import numpy as np
from collections import defaultdict
from scipy import stats

def get_most_recent_uci_json_files(results_dir: str, num_days: int = 2):
    """Get the most recent N sets of UCI JSON files, grouped by dataset."""
    results_path = Path(results_dir)
    all_uci_files = sorted(results_path.glob("uci_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    datasets = defaultdict(list)
    for file in all_uci_files:
        parts = file.stem.split('_')
        date_idx = None
        for i, part in enumerate(parts):
            if len(part) == 8 and part.isdigit() and part.startswith('2025'):
                date_idx = i
                break
        
        if date_idx:
            dataset_name = '_'.join(parts[:date_idx])
            datasets[dataset_name].append(file)
    
    recent_files_by_dataset = {}
    for dataset_name, files in datasets.items():
        recent_files_by_dataset[dataset_name] = files[:num_days]
    
    return recent_files_by_dataset

def load_json_file(file_path: Path):
    """Load a JSON benchmark result file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
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

def is_linearboost(model_name):
    """Check if model is a LinearBoost variant."""
    return 'LinearBoost' in model_name

def aggregate_across_datasets(all_new_metrics, all_previous_metrics):
    """Aggregate metrics across all datasets for each model."""
    aggregated_new = defaultdict(lambda: {
        'f1': [], 'roc_auc': [], 'fit_time': [], 'score_time': []
    })
    aggregated_previous = defaultdict(lambda: {
        'f1': [], 'roc_auc': [], 'fit_time': [], 'score_time': []
    })
    
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
    
    common_datasets = set(new_files_dict.keys()) & set(previous_files_dict.keys())
    
    for dataset in sorted(common_datasets):
        new_files = new_files_dict[dataset]
        previous_files = previous_files_dict[dataset]
        
        if len(new_files) == 0 or len(previous_files) == 0:
            continue
        
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
    
    for model_name in comparison:
        if len(comparison[model_name]['f1_deltas']) > 0:
            comparison[model_name]['f1_mean_delta'] = np.mean(comparison[model_name]['f1_deltas'])
            comparison[model_name]['f1_std_delta'] = np.std(comparison[model_name]['f1_deltas'])
            comparison[model_name]['roc_mean_delta'] = np.mean(comparison[model_name]['roc_deltas'])
            comparison[model_name]['roc_std_delta'] = np.std(comparison[model_name]['roc_deltas'])
            comparison[model_name]['fit_time_mean_delta'] = np.mean(comparison[model_name]['fit_time_deltas'])
            comparison[model_name]['score_time_mean_delta'] = np.mean(comparison[model_name]['score_time_deltas'])
            
            # Statistical test
            if len(comparison[model_name]['f1_deltas']) >= 3:
                try:
                    _, p_value = stats.wilcoxon(comparison[model_name]['f1_deltas'])
                    comparison[model_name]['f1_p_value'] = p_value
                    comparison[model_name]['f1_significant'] = p_value < 0.05
                except:
                    comparison[model_name]['f1_p_value'] = None
                    comparison[model_name]['f1_significant'] = False
    
    return comparison

def print_detailed_comparison(comparison):
    """Print detailed comparison focused on LinearBoost variants."""
    print("=" * 100)
    print("F1 BONUS STRENGTHENING (0.6 → 0.8): IMPACT EVALUATION")
    print("=" * 100)
    print(f"\nChange: F1 bonus multiplier increased from 0.6 to 0.8")
    print(f"Expected: +0.01-0.015 F1 improvement")
    print()
    
    linearboost_models = {k: v for k, v in comparison.items() if is_linearboost(k)}
    
    if not linearboost_models:
        print("No LinearBoost variants found in comparison.")
        return
    
    print("\n" + "=" * 100)
    print("LINEARBOOST VARIANTS - PERFORMANCE CHANGES")
    print("=" * 100)
    
    for model_name in sorted(linearboost_models.keys()):
        stats_dict = comparison[model_name]
        
        if len(stats_dict['f1_deltas']) == 0:
            continue
        
        print(f"\n{model_name}:")
        print("-" * 100)
        
        # F1 Score
        f1_delta = stats_dict.get('f1_mean_delta', 0)
        f1_std = stats_dict.get('f1_std_delta', 0)
        improvements = sum(1 for d in stats_dict['f1_deltas'] if d > 0.001)
        regressions = sum(1 for d in stats_dict['f1_deltas'] if d < -0.001)
        
        print(f"F1 Score:")
        print(f"  Mean Δ: {f1_delta:+.4f} ± {f1_std:.4f}")
        print(f"  Improvements: {improvements} datasets, Regressions: {regressions} datasets")
        if 'f1_p_value' in stats_dict and stats_dict['f1_p_value'] is not None:
            sig = "✓ SIGNIFICANT" if stats_dict.get('f1_significant', False) else "✗ Not significant"
            print(f"  Statistical test: p={stats_dict['f1_p_value']:.4f} ({sig})")
        
        # ROC-AUC
        roc_delta = stats_dict.get('roc_mean_delta', 0)
        roc_std = stats_dict.get('roc_std_delta', 0)
        roc_improvements = sum(1 for d in stats_dict['roc_deltas'] if d > 0.001)
        roc_regressions = sum(1 for d in stats_dict['roc_deltas'] if d < -0.001)
        
        print(f"\nROC-AUC:")
        print(f"  Mean Δ: {roc_delta:+.4f} ± {roc_std:.4f}")
        print(f"  Improvements: {roc_improvements} datasets, Regressions: {roc_regressions} datasets")
        
        # Training Time
        fit_delta = stats_dict.get('fit_time_mean_delta', 0)
        fit_improvements = sum(1 for d in stats_dict['fit_time_deltas'] if d < -0.001)
        fit_regressions = sum(1 for d in stats_dict['fit_time_deltas'] if d > 0.001)
        
        print(f"\nTraining Time:")
        print(f"  Mean Δ: {fit_delta:+.4f} seconds")
        print(f"  Faster: {fit_improvements} datasets, Slower: {fit_regressions} datasets")
        
        # Inference Time
        score_delta = stats_dict.get('score_time_mean_delta', 0)
        score_improvements = sum(1 for d in stats_dict['score_time_deltas'] if d < -0.001)
        score_regressions = sum(1 for d in stats_dict['score_time_deltas'] if d > 0.001)
        
        print(f"\nInference Time:")
        print(f"  Mean Δ: {score_delta:+.4f} ms")
        print(f"  Faster: {score_improvements} datasets, Slower: {score_regressions} datasets")
        
        # Per-dataset breakdown
        print(f"\nPer-Dataset Changes:")
        for i, dataset in enumerate(stats_dict['datasets']):
            if i < len(stats_dict['f1_deltas']):
                f1_d = stats_dict['f1_deltas'][i]
                roc_d = stats_dict['roc_deltas'][i]
                dataset_short = dataset.replace('uci_', '')
                print(f"  {dataset_short:<45} F1: {f1_d:+7.4f}  ROC: {roc_d:+7.4f}")
    
    # Overall summary
    print("\n" + "=" * 100)
    print("OVERALL ASSESSMENT")
    print("=" * 100)
    
    all_f1_deltas = []
    all_roc_deltas = []
    for model_name, stats_dict in linearboost_models.items():
        all_f1_deltas.extend(stats_dict['f1_deltas'])
        all_roc_deltas.extend(stats_dict['roc_deltas'])
    
    if len(all_f1_deltas) > 0:
        print(f"\nAll LinearBoost Variants Combined:")
        print(f"  F1 Score: {np.mean(all_f1_deltas):+.4f} ± {np.std(all_f1_deltas):.4f}")
        print(f"  ROC-AUC:  {np.mean(all_roc_deltas):+.4f} ± {np.std(all_roc_deltas):.4f}")
        print(f"  Total F1 improvements: {sum(1 for d in all_f1_deltas if d > 0.001)}")
        print(f"  Total F1 regressions: {sum(1 for d in all_f1_deltas if d < -0.001)}")
        
        # Recommendation
        print(f"\n{'='*100}")
        print("RECOMMENDATION")
        print(f"{'='*100}")
        
        mean_f1_delta = np.mean(all_f1_deltas)
        mean_roc_delta = np.mean(all_roc_deltas)
        total_improvements = sum(1 for d in all_f1_deltas if d > 0.001)
        total_regressions = sum(1 for d in all_f1_deltas if d < -0.001)
        
        if mean_f1_delta > 0.005 and total_improvements > total_regressions:
            print("\n✅ RECOMMENDATION: KEEP the strengthened F1 bonus (0.8)")
            print(f"   Rationale:")
            print(f"   - F1 improved by {mean_f1_delta:+.4f} on average")
            print(f"   - {total_improvements} datasets improved vs {total_regressions} regressed")
            if mean_roc_delta >= -0.01:
                print(f"   - ROC-AUC maintained (Δ: {mean_roc_delta:+.4f})")
            else:
                print(f"   - ROC-AUC trade-off acceptable (Δ: {mean_roc_delta:+.4f})")
        elif mean_f1_delta > 0.001:
            print("\n⚠️  RECOMMENDATION: MARGINAL - Consider keeping but monitor")
            print(f"   Rationale:")
            print(f"   - F1 improved slightly by {mean_f1_delta:+.4f} on average")
            print(f"   - {total_improvements} datasets improved vs {total_regressions} regressed")
            print(f"   - Change is small, may be within noise")
        elif mean_f1_delta < -0.005:
            print("\n❌ RECOMMENDATION: REVERT the strengthened F1 bonus (back to 0.6)")
            print(f"   Rationale:")
            print(f"   - F1 regressed by {abs(mean_f1_delta):.4f} on average")
            print(f"   - {total_regressions} datasets regressed vs {total_improvements} improved")
            print(f"   - Change caused performance degradation")
        else:
            print("\n➡️  RECOMMENDATION: NEUTRAL - Either keep or revert")
            print(f"   Rationale:")
            print(f"   - F1 change is essentially neutral ({mean_f1_delta:+.4f})")
            print(f"   - {total_improvements} improvements vs {total_regressions} regressions")
            print(f"   - Change had minimal measurable impact")

def main():
    results_dir = "benchmark_results"
    
    all_files = get_most_recent_uci_json_files(results_dir, num_days=2)
    
    if len(all_files) == 0:
        print("No UCI benchmark results found.")
        return
    
    new_files_dict = {}
    previous_files_dict = {}
    
    for dataset, files in all_files.items():
        if len(files) >= 1:
            new_files_dict[dataset] = [files[0]]
        if len(files) >= 2:
            previous_files_dict[dataset] = files[1:]
    
    comparison = compare_results(new_files_dict, previous_files_dict)
    print_detailed_comparison(comparison)

if __name__ == "__main__":
    main()
