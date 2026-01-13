#!/usr/bin/env python3
"""
Compare benchmark results before and after implementing early stopping on F1/ROC-AUC.
Yesterday = before, Today = after
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import pandas as pd

def get_date_string(days_ago=0):
    """Get date string in YYYYMMDD format."""
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y%m%d")

def load_results_by_date(days_ago, prefix="uci"):
    """Load all JSON files with given prefix from specified date."""
    results_dir = Path("benchmark_results")
    date_str = get_date_string(days_ago)
    
    results = []
    for file_path in sorted(results_dir.glob(f"{prefix}_*{date_str}*.json")):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            results.append({
                'file': file_path.name,
                'date': date_str,
                'data': data
            })
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
    
    return results

def extract_dataset_key(filename):
    """Extract dataset identifier from filename."""
    # Extract UCI ID and dataset name (e.g., "uci_17_Breast Cancer Wisconsin")
    parts = filename.split('_')
    if len(parts) >= 3:
        return '_'.join(parts[:3])  # uci_17_Breast
    return filename.split('_')[0] + '_' + filename.split('_')[1] if '_' in filename else filename

def extract_model_metrics(results_list):
    """Extract metrics for LinearBoost variants and competitors."""
    metrics = defaultdict(lambda: {
        'f1_scores': [],
        'roc_auc_scores': [],
        'datasets': [],
        'dataset_keys': []
    })
    
    for result in results_list:
        data = result['data']
        file_name = result['file']
        dataset_key = extract_dataset_key(file_name)
        
        if 'results' not in data:
            continue
        
        results = data['results']
        
        for model_name in results:
            model_data = results[model_name]
            
            if 'f1_mean' in model_data and 'roc_auc_mean' in model_data:
                metrics[model_name]['f1_scores'].append(model_data['f1_mean'])
                metrics[model_name]['roc_auc_scores'].append(model_data['roc_auc_mean'])
                metrics[model_name]['datasets'].append(file_name)
                metrics[model_name]['dataset_keys'].append(dataset_key)
    
    return metrics

def analyze_improvements(before_metrics, after_metrics):
    """Analyze improvements between before and after."""
    analysis = {}
    
    for model_name in set(list(before_metrics.keys()) + list(after_metrics.keys())):
        if model_name not in before_metrics or model_name not in after_metrics:
            continue
        
        before_f1 = np.array(before_metrics[model_name]['f1_scores'])
        after_f1 = np.array(after_metrics[model_name]['f1_scores'])
        before_roc = np.array(before_metrics[model_name]['roc_auc_scores'])
        after_roc = np.array(after_metrics[model_name]['roc_auc_scores'])
        
        # Match datasets by dataset key
        before_keys = before_metrics[model_name]['dataset_keys']
        after_keys = after_metrics[model_name]['dataset_keys']
        
        # Create mapping from key to indices
        before_key_to_indices = defaultdict(list)
        for i, key in enumerate(before_keys):
            before_key_to_indices[key].append(i)
        
        after_key_to_indices = defaultdict(list)
        for i, key in enumerate(after_keys):
            after_key_to_indices[key].append(i)
        
        common_keys = set(before_keys).intersection(set(after_keys))
        
        if len(common_keys) == 0:
            continue
        
        # Get indices for common datasets (take first match if multiple)
        before_indices = []
        after_indices = []
        for key in sorted(common_keys):  # Sort for consistency
            if before_key_to_indices[key] and after_key_to_indices[key]:
                before_indices.append(before_key_to_indices[key][0])
                after_indices.append(after_key_to_indices[key][0])
        
        if len(before_indices) == 0:
            continue
        
        before_f1_common = before_f1[before_indices]
        after_f1_common = after_f1[after_indices]
        before_roc_common = before_roc[before_indices]
        after_roc_common = after_roc[after_indices]
        
        if len(before_f1_common) == 0:
            continue
        
        f1_improvement = after_f1_common - before_f1_common
        roc_improvement = after_roc_common - before_roc_common
        
        analysis[model_name] = {
            'n_datasets': len(common_keys),
            'f1_before_mean': np.mean(before_f1_common),
            'f1_after_mean': np.mean(after_f1_common),
            'f1_improvement_mean': np.mean(f1_improvement),
            'f1_improvement_std': np.std(f1_improvement),
            'f1_improved_count': np.sum(f1_improvement > 0),
            'f1_worsened_count': np.sum(f1_improvement < 0),
            'roc_before_mean': np.mean(before_roc_common),
            'roc_after_mean': np.mean(after_roc_common),
            'roc_improvement_mean': np.mean(roc_improvement),
            'roc_improvement_std': np.std(roc_improvement),
            'roc_improved_count': np.sum(roc_improvement > 0),
            'roc_worsened_count': np.sum(roc_improvement < 0),
            'f1_max_improvement': np.max(f1_improvement) if len(f1_improvement) > 0 else 0,
            'roc_max_improvement': np.max(roc_improvement) if len(roc_improvement) > 0 else 0,
        }
    
    return analysis

def extract_parameter_patterns(results_list, model_prefix="LinearBoost"):
    """Extract parameter patterns from best_params."""
    patterns = defaultdict(lambda: defaultdict(list))
    
    for result in results_list:
        data = result['data']
        
        if 'results' not in data:
            continue
        
        results = data['results']
        
        for model_name in results:
            if not model_name.startswith(model_prefix):
                continue
            
            model_data = results[model_name]
            if 'best_params' not in model_data:
                continue
            
            params = model_data['best_params']
            
            for param_name, param_value in params.items():
                patterns[model_name][param_name].append(param_value)
    
    return patterns

def analyze_parameter_changes(before_patterns, after_patterns):
    """Analyze changes in parameter patterns."""
    analysis = {}
    
    for model_name in set(list(before_patterns.keys()) + list(after_patterns.keys())):
        if model_name not in before_patterns or model_name not in after_patterns:
            continue
        
        changes = {}
        
        for param_name in set(list(before_patterns[model_name].keys()) + list(after_patterns[model_name].keys())):
            before_vals = before_patterns[model_name].get(param_name, [])
            after_vals = after_patterns[model_name].get(param_name, [])
            
            if len(before_vals) == 0 or len(after_vals) == 0:
                continue
            
            # For numeric parameters
            if isinstance(before_vals[0], (int, float)) and isinstance(after_vals[0], (int, float)):
                before_mean = np.mean(before_vals)
                after_mean = np.mean(after_vals)
                changes[param_name] = {
                    'before_mean': before_mean,
                    'after_mean': after_mean,
                    'change': after_mean - before_mean,
                    'change_pct': ((after_mean - before_mean) / before_mean * 100) if before_mean != 0 else 0
                }
            else:
                # For categorical parameters
                from collections import Counter
                before_counts = Counter(before_vals)
                after_counts = Counter(after_vals)
                changes[param_name] = {
                    'before_dist': dict(before_counts),
                    'after_dist': dict(after_counts)
                }
        
        if changes:
            analysis[model_name] = changes
    
    return analysis

def print_analysis(before_metrics, after_metrics, improvements, param_changes):
    """Print comprehensive analysis."""
    print("=" * 100)
    print("COMPARISON: BEFORE vs AFTER EARLY STOPPING ON F1/ROC-AUC")
    print("=" * 100)
    print()
    
    print(f"Before (Yesterday): {len(before_metrics)} models, datasets: {sum(len(m['datasets']) for m in before_metrics.values())}")
    print(f"After (Today): {len(after_metrics)} models, datasets: {sum(len(m['datasets']) for m in after_metrics.values())}")
    print()
    
    # LinearBoost variants first
    lb_models = [m for m in improvements.keys() if 'LinearBoost' in m]
    other_models = [m for m in improvements.keys() if 'LinearBoost' not in m]
    
    print("LINEARBOOST VARIANTS - PERFORMANCE CHANGES:")
    print("-" * 100)
    print(f"{'Model':<25} {'F1 Before':<12} {'F1 After':<12} {'F1 Δ':<10} {'ROC Before':<12} {'ROC After':<12} {'ROC Δ':<10}")
    print("-" * 100)
    
    for model_name in sorted(lb_models):
        imp = improvements[model_name]
        print(f"{model_name:<25} {imp['f1_before_mean']:<12.4f} {imp['f1_after_mean']:<12.4f} "
              f"{imp['f1_improvement_mean']:+10.4f} {imp['roc_before_mean']:<12.4f} "
              f"{imp['roc_after_mean']:<12.4f} {imp['roc_improvement_mean']:+10.4f}")
    print()
    
    print("COMPETITOR MODELS - PERFORMANCE CHANGES:")
    print("-" * 100)
    for model_name in sorted(other_models):
        imp = improvements[model_name]
        print(f"{model_name:<25} F1: {imp['f1_before_mean']:.4f} → {imp['f1_after_mean']:.4f} "
              f"({imp['f1_improvement_mean']:+.4f}), ROC: {imp['roc_before_mean']:.4f} → "
              f"{imp['roc_after_mean']:.4f} ({imp['roc_improvement_mean']:+.4f})")
    print()
    
    # Detailed LinearBoost analysis
    print("LINEARBOOST VARIANTS - DETAILED ANALYSIS:")
    print("-" * 100)
    for model_name in sorted(lb_models):
        imp = improvements[model_name]
        print(f"\n{model_name}:")
        print(f"  Datasets compared: {imp['n_datasets']}")
        print(f"  F1 Improvement: {imp['f1_improvement_mean']:+.4f} ± {imp['f1_improvement_std']:.4f}")
        print(f"    - Improved: {imp['f1_improved_count']}, Worsened: {imp['f1_worsened_count']}")
        print(f"    - Max improvement: {imp['f1_max_improvement']:+.4f}")
        print(f"  ROC-AUC Improvement: {imp['roc_improvement_mean']:+.4f} ± {imp['roc_improvement_std']:.4f}")
        print(f"    - Improved: {imp['roc_improved_count']}, Worsened: {imp['roc_worsened_count']}")
        print(f"    - Max improvement: {imp['roc_max_improvement']:+.4f}")
    
    # Parameter analysis
    if param_changes:
        print("\n" + "=" * 100)
        print("PARAMETER PATTERN CHANGES:")
        print("=" * 100)
        
        for model_name in sorted(param_changes.keys()):
            if 'LinearBoost' not in model_name:
                continue
            
            print(f"\n{model_name}:")
            for param_name, change_data in param_changes[model_name].items():
                if 'change' in change_data:
                    print(f"  {param_name}: {change_data['before_mean']:.4f} → {change_data['after_mean']:.4f} "
                          f"({change_data['change']:+.4f}, {change_data['change_pct']:+.1f}%)")
                else:
                    print(f"  {param_name}:")
                    print(f"    Before: {change_data['before_dist']}")
                    print(f"    After:  {change_data['after_dist']}")

def generate_recommendations(improvements, param_changes):
    """Generate recommendations based on analysis."""
    recommendations = []
    
    # Analyze LinearBoost variants
    lb_models = {k: v for k, v in improvements.items() if 'LinearBoost' in k}
    
    if not lb_models:
        return ["No LinearBoost data found for comparison"]
    
    # Overall performance
    total_f1_improvement = sum(imp['f1_improvement_mean'] for imp in lb_models.values())
    total_roc_improvement = sum(imp['roc_improvement_mean'] for imp in lb_models.values())
    
    recommendations.append(f"Early stopping on F1/ROC-AUC showed:")
    recommendations.append(f"  - Average F1 improvement: {total_f1_improvement / len(lb_models):+.4f}")
    recommendations.append(f"  - Average ROC-AUC improvement: {total_roc_improvement / len(lb_models):+.4f}")
    recommendations.append("")
    
    # Check which variant improved most
    best_improver = max(lb_models.items(), key=lambda x: x[1]['f1_improvement_mean'] + x[1]['roc_improvement_mean'])
    recommendations.append(f"Best improvement: {best_improver[0]} "
                          f"(F1: {best_improver[1]['f1_improvement_mean']:+.4f}, "
                          f"ROC: {best_improver[1]['roc_improvement_mean']:+.4f})")
    recommendations.append("")
    
    # Analyze gaps vs competitors
    competitors = {k: v for k, v in improvements.items() if 'LinearBoost' not in k}
    if competitors:
        best_lb_f1 = max(imp['f1_after_mean'] for imp in lb_models.values())
        best_lb_roc = max(imp['roc_after_mean'] for imp in lb_models.values())
        best_comp_f1 = max(imp['f1_after_mean'] for imp in competitors.values())
        best_comp_roc = max(imp['roc_after_mean'] for imp in competitors.values())
        
        f1_gap = best_comp_f1 - best_lb_f1
        roc_gap = best_comp_roc - best_lb_roc
        
        recommendations.append("PERFORMANCE GAPS vs BEST COMPETITOR:")
        recommendations.append(f"  F1 gap: {f1_gap:+.4f} (LinearBoost best: {best_lb_f1:.4f}, Competitor best: {best_comp_f1:.4f})")
        recommendations.append(f"  ROC-AUC gap: {roc_gap:+.4f} (LinearBoost best: {roc_gap:.4f}, Competitor best: {best_comp_roc:.4f})")
        recommendations.append("")
    
    # Parameter-based recommendations
    if param_changes:
        recommendations.append("PARAMETER-BASED INSIGHTS:")
        for model_name in sorted(param_changes.keys()):
            if 'LinearBoost' not in model_name:
                continue
            
            for param_name, change_data in param_changes[model_name].items():
                if 'change' in change_data and abs(change_data['change_pct']) > 10:
                    recommendations.append(f"  {model_name} - {param_name}: "
                                        f"Changed by {change_data['change_pct']:+.1f}% "
                                        f"({change_data['before_mean']:.4f} → {change_data['after_mean']:.4f})")
        recommendations.append("")
    
    # Next steps
    recommendations.append("RECOMMENDED NEXT STEPS:")
    
    if f1_gap > 0.02:
        recommendations.append("1. HIGH PRIORITY: Implement adaptive learning rate (from IMPLEMENTATION_GUIDE)")
        recommendations.append("   - Expected: +0.01-0.02 F1 improvement")
    
    if roc_gap > 0.01:
        recommendations.append("2. HIGH PRIORITY: Implement class-imbalance aware boosting")
        recommendations.append("   - Expected: +0.02-0.03 F1 on imbalanced datasets")
    
    recommendations.append("3. MEDIUM PRIORITY: Implement F1-aware estimator weighting")
    recommendations.append("   - Expected: +0.015-0.025 F1 improvement")
    
    recommendations.append("4. MEDIUM PRIORITY: Implement margin-based sample weight updates")
    recommendations.append("   - Expected: +0.01-0.015 F1 improvement")
    
    recommendations.append("5. Consider ensemble pruning for weak estimators")
    recommendations.append("   - Expected: +0.005-0.01 F1 improvement")
    
    return recommendations

if __name__ == "__main__":
    # Load results
    print("Loading results...")
    yesterday_results = load_results_by_date(days_ago=1, prefix="uci")
    today_results = load_results_by_date(days_ago=0, prefix="uci")
    
    print(f"Found {len(yesterday_results)} files from yesterday (before)")
    print(f"Found {len(today_results)} files from today (after)")
    print()
    
    if len(yesterday_results) == 0 or len(today_results) == 0:
        print("Error: Not enough results to compare. Need both yesterday and today results.")
        exit(1)
    
    # Extract metrics
    before_metrics = extract_model_metrics(yesterday_results)
    after_metrics = extract_model_metrics(today_results)
    
    # Analyze improvements
    improvements = analyze_improvements(before_metrics, after_metrics)
    
    # Analyze parameter patterns
    before_params = extract_parameter_patterns(yesterday_results)
    after_params = extract_parameter_patterns(today_results)
    param_changes = analyze_parameter_changes(before_params, after_params)
    
    # Print analysis
    print_analysis(before_metrics, after_metrics, improvements, param_changes)
    
    # Generate recommendations
    print("\n" + "=" * 100)
    print("RECOMMENDATIONS:")
    print("=" * 100)
    recs = generate_recommendations(improvements, param_changes)
    for rec in recs:
        print(rec)
    
    # Save detailed analysis
    analysis_output = {
        'improvements': {k: {key: float(val) if isinstance(val, (np.integer, np.floating)) else val 
                            for key, val in v.items()} 
                        for k, v in improvements.items()},
        'recommendations': recs
    }
    
    with open('early_stopping_analysis.json', 'w') as f:
        json.dump(analysis_output, f, indent=2, default=str)
    
    print("\n✓ Detailed analysis saved to early_stopping_analysis.json")

