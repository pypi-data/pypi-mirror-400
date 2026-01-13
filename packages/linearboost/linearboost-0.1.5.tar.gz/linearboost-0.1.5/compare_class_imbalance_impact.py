#!/usr/bin/env python3
"""
Compare UCI benchmark results before and after class-imbalance aware updates.
Most recent files = after implementation
Second most recent files = before implementation
"""

import json
from pathlib import Path
from datetime import datetime
import numpy as np
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

def extract_metrics(data):
    """Extract F1 and ROC-AUC metrics from benchmark results."""
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
            }
    return metrics

def is_linearboost(model_name):
    """Check if model is a LinearBoost variant."""
    return 'LinearBoost' in model_name

def compare_results(new_files_dict, previous_files_dict):
    """Compare new (most recent) vs previous (second most recent) results."""
    comparison = {
        'datasets': [],
        'linearboost_variants': defaultdict(lambda: {
            'f1_deltas': [],
            'roc_deltas': [],
            'f1_improvements': 0,
            'f1_regressions': 0,
            'roc_improvements': 0,
            'roc_regressions': 0,
        }),
        'other_models': defaultdict(lambda: {
            'f1_deltas': [],
            'roc_deltas': [],
        }),
        'summary': {}
    }
    
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
        
        new_metrics = extract_metrics(new_data)
        previous_metrics = extract_metrics(previous_data)
        
        comparison['datasets'].append(dataset)
        
        # Compare all models
        all_models = set(new_metrics.keys()) & set(previous_metrics.keys())
        
        for model_name in all_models:
            f1_delta = new_metrics[model_name]['f1_mean'] - previous_metrics[model_name]['f1_mean']
            roc_delta = new_metrics[model_name]['roc_auc_mean'] - previous_metrics[model_name]['roc_auc_mean']
            
            if is_linearboost(model_name):
                comparison['linearboost_variants'][model_name]['f1_deltas'].append(f1_delta)
                comparison['linearboost_variants'][model_name]['roc_deltas'].append(roc_delta)
                
                if f1_delta > 0.001:  # Significant improvement
                    comparison['linearboost_variants'][model_name]['f1_improvements'] += 1
                elif f1_delta < -0.001:  # Significant regression
                    comparison['linearboost_variants'][model_name]['f1_regressions'] += 1
                
                if roc_delta > 0.001:
                    comparison['linearboost_variants'][model_name]['roc_improvements'] += 1
                elif roc_delta < -0.001:
                    comparison['linearboost_variants'][model_name]['roc_regressions'] += 1
            else:
                comparison['other_models'][model_name]['f1_deltas'].append(f1_delta)
                comparison['other_models'][model_name]['roc_deltas'].append(roc_delta)
    
    # Calculate summary statistics
    for variant, stats_dict in comparison['linearboost_variants'].items():
        if len(stats_dict['f1_deltas']) > 0:
            stats_dict['f1_mean_delta'] = np.mean(stats_dict['f1_deltas'])
            stats_dict['f1_std_delta'] = np.std(stats_dict['f1_deltas'])
            stats_dict['roc_mean_delta'] = np.mean(stats_dict['roc_deltas'])
            stats_dict['roc_std_delta'] = np.std(stats_dict['roc_deltas'])
            
            # Statistical significance test
            if len(stats_dict['f1_deltas']) >= 3:
                try:
                    _, p_value = stats.wilcoxon(stats_dict['f1_deltas'])
                    stats_dict['f1_p_value'] = p_value
                    stats_dict['f1_significant'] = p_value < 0.05
                except:
                    stats_dict['f1_p_value'] = None
                    stats_dict['f1_significant'] = False
    
    return comparison

def print_comparison(comparison):
    """Print formatted comparison results."""
    print("=" * 80)
    print("CLASS-IMBALANCE AWARE UPDATES: IMPACT ANALYSIS")
    print("=" * 80)
    print(f"\nDatasets compared: {len(comparison['datasets'])}")
    print(f"Dataset names: {', '.join([d.replace('uci_', '') for d in comparison['datasets']])}\n")
    
    print("\n" + "=" * 80)
    print("LINEARBOOST VARIANTS PERFORMANCE CHANGES")
    print("=" * 80)
    
    for variant in sorted(comparison['linearboost_variants'].keys()):
        stats_dict = comparison['linearboost_variants'][variant]
        
        if len(stats_dict['f1_deltas']) == 0:
            continue
        
        print(f"\n{variant}:")
        print(f"  F1 Score:")
        print(f"    Mean Δ: {stats_dict.get('f1_mean_delta', 0):+.4f} ± {stats_dict.get('f1_std_delta', 0):.4f}")
        print(f"    Improvements: {stats_dict['f1_improvements']} datasets")
        print(f"    Regressions: {stats_dict['f1_regressions']} datasets")
        if 'f1_p_value' in stats_dict and stats_dict['f1_p_value'] is not None:
            sig = "✓ SIGNIFICANT" if stats_dict.get('f1_significant', False) else "✗ Not significant"
            print(f"    Statistical test: p={stats_dict['f1_p_value']:.4f} ({sig})")
        
        print(f"  ROC-AUC:")
        print(f"    Mean Δ: {stats_dict.get('roc_mean_delta', 0):+.4f} ± {stats_dict.get('roc_std_delta', 0):.4f}")
        print(f"    Improvements: {stats_dict['roc_improvements']} datasets")
        print(f"    Regressions: {stats_dict['roc_regressions']} datasets")
        
        # Show per-dataset changes
        print(f"  Per-Dataset Changes:")
        for i, dataset in enumerate(comparison['datasets']):
            if i < len(stats_dict['f1_deltas']):
                f1_delta = stats_dict['f1_deltas'][i]
                roc_delta = stats_dict['roc_deltas'][i]
                dataset_short = dataset.replace('uci_', '')
                print(f"    {dataset_short:<40} F1: {f1_delta:+7.4f}  ROC: {roc_delta:+7.4f}")
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    
    all_f1_deltas = []
    all_roc_deltas = []
    for variant, stats_dict in comparison['linearboost_variants'].items():
        all_f1_deltas.extend(stats_dict['f1_deltas'])
        all_roc_deltas.extend(stats_dict['roc_deltas'])
    
    if len(all_f1_deltas) > 0:
        print(f"\nAll LinearBoost Variants Combined:")
        print(f"  F1 Score: {np.mean(all_f1_deltas):+.4f} ± {np.std(all_f1_deltas):.4f}")
        print(f"  ROC-AUC:  {np.mean(all_roc_deltas):+.4f} ± {np.std(all_roc_deltas):.4f}")
        print(f"  Total F1 improvements: {sum(1 for d in all_f1_deltas if d > 0.001)}")
        print(f"  Total F1 regressions: {sum(1 for d in all_f1_deltas if d < -0.001)}")
        print(f"  Neutral changes: {sum(1 for d in all_f1_deltas if -0.001 <= d <= 0.001)}")
    
    # Compare with other models for context
    print(f"\nOther Models (for context - random_state may vary):")
    for model_name in sorted(comparison['other_models'].keys()):
        deltas = comparison['other_models'][model_name]['f1_deltas']
        if len(deltas) > 0:
            mean_delta = np.mean(deltas)
            print(f"  {model_name:<30} F1 Δ: {mean_delta:+.4f}")

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
    
    comparison = compare_results(new_files_dict, previous_files_dict)
    
    print_comparison(comparison)
    
    # Save comparison to file
    comparison_file = Path(results_dir) / "class_imbalance_impact_comparison.json"
    
    # Convert to JSON-serializable format
    json_comparison = {
        'datasets': comparison['datasets'],
        'linearboost_variants': {
            k: {
                'f1_deltas': v['f1_deltas'],
                'roc_deltas': v['roc_deltas'],
                'f1_mean_delta': float(np.mean(v['f1_deltas'])) if len(v['f1_deltas']) > 0 else 0,
                'roc_mean_delta': float(np.mean(v['roc_deltas'])) if len(v['roc_deltas']) > 0 else 0,
            }
            for k, v in comparison['linearboost_variants'].items()
        }
    }
    
    with open(comparison_file, 'w') as f:
        json.dump(json_comparison, f, indent=2)
    
    print(f"\n\nComparison saved to: {comparison_file}")

if __name__ == "__main__":
    main()
