#!/usr/bin/env python3
"""
Analyze recent benchmark results (today and yesterday) to identify LinearBoost improvement opportunities.
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

def load_recent_results(days_back=2):
    """Load benchmark results from today and yesterday."""
    results_dir = Path("benchmark_results")
    all_results = []
    
    for days_ago in range(days_back):
        date_str = get_date_string(days_ago)
        json_files = sorted(results_dir.glob(f"*{date_str}*.json"))
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                all_results.append({
                    'file': file_path.name,
                    'date': date_str,
                    'days_ago': days_ago,
                    'data': data
                })
            except Exception as e:
                print(f"Error loading {file_path.name}: {e}")
    
    return all_results

def analyze_linearboost_performance(results_list):
    """Analyze LinearBoost performance across all recent results."""
    analysis = {
        'datasets': [],
        'linearboost_l': [],
        'linearboost_k': [],
        'linearboost_k_exact': [],
        'competitors': defaultdict(list)
    }
    
    for result in results_list:
        data = result['data']
        date = result['date']
        
        if 'results' not in data:
            continue
        
        results = data['results']
        
        # Extract dataset info
        dataset_name = result['file'].split('_')[0] if '_' in result['file'] else result['file']
        dataset_info = {
            'name': dataset_name,
            'date': date,
            'file': result['file']
        }
        
        # Try to get dataset characteristics
        if 'LinearBoost-L' in results:
            dataset_info['n_samples'] = results['LinearBoost-L'].get('n_samples', 0)
            dataset_info['n_features'] = results['LinearBoost-L'].get('n_features', 0)
        
        analysis['datasets'].append(dataset_info)
        
        # Extract LinearBoost metrics
        for lb_variant in ['LinearBoost-L', 'LinearBoost-K', 'LinearBoost-K-exact']:
            if lb_variant in results:
                model_data = results[lb_variant]
                key = lb_variant.lower().replace('-', '_')
                analysis[key].append({
                    'dataset': dataset_name,
                    'date': date,
                    'f1_mean': model_data.get('f1_mean', 0),
                    'f1_std': model_data.get('f1_std', 0),
                    'roc_auc_mean': model_data.get('roc_auc_mean', 0),
                    'roc_auc_std': model_data.get('roc_auc_std', 0),
                    'best_params': model_data.get('best_params', {}),
                    'n_samples': model_data.get('n_samples', 0),
                    'n_features': model_data.get('n_features', 0)
                })
        
        # Extract competitor metrics
        competitors = ['XGBoost', 'LightGBM', 'CatBoost', 'RandomForest', 'LogisticRegression']
        for comp in competitors:
            if comp in results:
                comp_data = results[comp]
                analysis['competitors'][comp].append({
                    'dataset': dataset_name,
                    'date': date,
                    'f1_mean': comp_data.get('f1_mean', 0),
                    'roc_auc_mean': comp_data.get('roc_auc_mean', 0)
                })
    
    return analysis

def extract_statistical_comparisons(results_list):
    """Extract where LinearBoost loses significantly."""
    losses = defaultdict(lambda: {'f1': [], 'roc_auc': []})
    
    for result in results_list:
        data = result['data']
        
        if 'statistical_results' not in data:
            continue
        
        stats = data['statistical_results']
        
        # Check pairwise comparisons
        for metric in ['pairwise_f1', 'pairwise_roc']:
            if metric not in stats:
                continue
            
            metric_name = metric.replace('pairwise_', '').replace('_', '')
            if metric_name == 'roc':
                metric_name = 'roc_auc'
            
            for pair_name, comparison in stats[metric].items():
                if not comparison.get('nemenyi_significant', False):
                    continue
                
                model1, model2 = pair_name.split('_vs_')
                better_model = comparison.get('better_model')
                
                # Track LinearBoost losses
                if 'LinearBoost' in model1 and better_model == model2:
                    losses[model1][metric_name].append({
                        'against': model2,
                        'effect_size': comparison.get('effect_size', 0),
                        'cohens_d': comparison.get('cohens_d', 0),
                        'rank_diff': comparison.get('rank_difference', 0)
                    })
                elif 'LinearBoost' in model2 and better_model == model1:
                    losses[model2][metric_name].append({
                        'against': model1,
                        'effect_size': comparison.get('effect_size', 0),
                        'cohens_d': comparison.get('cohens_d', 0),
                        'rank_diff': comparison.get('rank_difference', 0)
                    })
    
    return losses

def generate_improvement_insights(analysis, losses):
    """Generate specific improvement insights."""
    insights = {
        'performance_gaps': {},
        'parameter_patterns': {},
        'loss_patterns': {},
        'recommendations': []
    }
    
    # Calculate average performance gaps
    competitors_avg = {}
    for comp, results in analysis['competitors'].items():
        if results:
            competitors_avg[comp] = {
                'f1': np.mean([r['f1_mean'] for r in results]),
                'roc_auc': np.mean([r['roc_auc_mean'] for r in results])
            }
    
    for lb_variant in ['linearboost_l', 'linearboost_k', 'linearboost_k_exact']:
        if analysis[lb_variant]:
            lb_results = analysis[lb_variant]
            lb_avg_f1 = np.mean([r['f1_mean'] for r in lb_results])
            lb_avg_roc = np.mean([r['roc_auc_mean'] for r in lb_results])
            
            insights['performance_gaps'][lb_variant] = {
                'f1': lb_avg_f1,
                'roc_auc': lb_avg_roc
            }
            
            # Find best competitor
            best_comp_f1 = max([v['f1'] for v in competitors_avg.values()]) if competitors_avg else 0
            best_comp_roc = max([v['roc_auc'] for v in competitors_avg.values()]) if competitors_avg else 0
            
            insights['performance_gaps'][lb_variant]['f1_gap'] = best_comp_f1 - lb_avg_f1
            insights['performance_gaps'][lb_variant]['roc_gap'] = best_comp_roc - lb_avg_roc
    
    # Analyze parameter patterns
    for lb_variant in ['linearboost_l', 'linearboost_k', 'linearboost_k_exact']:
        if analysis[lb_variant]:
            params_list = [r['best_params'] for r in analysis[lb_variant] if r.get('best_params')]
            if params_list:
                param_patterns = {}
                for params in params_list:
                    for key, value in params.items():
                        if key not in param_patterns:
                            param_patterns[key] = []
                        param_patterns[key].append(value)
                
                insights['parameter_patterns'][lb_variant] = {}
                for key, values in param_patterns.items():
                    if isinstance(values[0], (int, float)):
                        insights['parameter_patterns'][lb_variant][key] = {
                            'mean': np.mean(values),
                            'std': np.std(values),
                            'min': np.min(values),
                            'max': np.max(values)
                        }
                    else:
                        from collections import Counter
                        insights['parameter_patterns'][lb_variant][key] = dict(Counter(values))
    
    # Analyze loss patterns
    for lb_variant, variant_losses in losses.items():
        insights['loss_patterns'][lb_variant] = {}
        for metric, loss_list in variant_losses.items():
            if loss_list:
                # Count losses by opponent
                opponent_counts = defaultdict(int)
                for loss in loss_list:
                    opponent_counts[loss['against']] += 1
                
                insights['loss_patterns'][lb_variant][metric] = {
                    'total_losses': len(loss_list),
                    'opponents': dict(opponent_counts),
                    'avg_effect_size': np.mean([abs(l['effect_size']) for l in loss_list]),
                    'avg_cohens_d': np.mean([abs(l['cohens_d']) for l in loss_list])
                }
    
    return insights

def print_analysis(analysis, losses, insights):
    """Print comprehensive analysis."""
    print("=" * 100)
    print("LINEARBOOST PERFORMANCE ANALYSIS - RECENT BENCHMARKS")
    print("=" * 100)
    print()
    
    # Dataset summary
    print(f"Datasets analyzed: {len(analysis['datasets'])}")
    for ds in analysis['datasets'][:10]:  # Show first 10
        print(f"  - {ds['name']} ({ds.get('n_samples', '?')} samples, {ds.get('n_features', '?')} features) - {ds['date']}")
    if len(analysis['datasets']) > 10:
        print(f"  ... and {len(analysis['datasets']) - 10} more")
    print()
    
    # Performance summary
    print("PERFORMANCE SUMMARY:")
    print("-" * 100)
    print(f"{'Model':<25} {'Avg F1':<12} {'Avg ROC-AUC':<12} {'F1 Gap':<12} {'ROC Gap':<12}")
    print("-" * 100)
    
    # LinearBoost variants
    for lb_variant in ['linearboost_l', 'linearboost_k', 'linearboost_k_exact']:
        if lb_variant in insights['performance_gaps']:
            pg = insights['performance_gaps'][lb_variant]
            name = lb_variant.replace('_', '-').title()
            print(f"{name:<25} {pg['f1']:<12.4f} {pg['roc_auc']:<12.4f} "
                  f"{pg.get('f1_gap', 0):<12.4f} {pg.get('roc_gap', 0):<12.4f}")
    
    # Competitors
    from collections import defaultdict
    comp_avg = defaultdict(lambda: {'f1': [], 'roc_auc': []})
    for comp, results in analysis['competitors'].items():
        for r in results:
            comp_avg[comp]['f1'].append(r['f1_mean'])
            comp_avg[comp]['roc_auc'].append(r['roc_auc_mean'])
    
    for comp, values in comp_avg.items():
        if values['f1']:
            avg_f1 = np.mean(values['f1'])
            avg_roc = np.mean(values['roc_auc'])
            print(f"{comp:<25} {avg_f1:<12.4f} {avg_roc:<12.4f} {'-':<12} {'-':<12}")
    print()
    
    # Loss analysis
    print("SIGNIFICANT LOSSES:")
    print("-" * 100)
    for lb_variant, variant_losses in losses.items():
        print(f"\n{lb_variant}:")
        for metric, loss_list in variant_losses.items():
            if loss_list:
                print(f"  {metric.upper()}: {len(loss_list)} significant losses")
                opponent_counts = defaultdict(int)
                for loss in loss_list:
                    opponent_counts[loss['against']] += 1
                for opponent, count in sorted(opponent_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"    - vs {opponent}: {count} losses")
    print()
    
    # Parameter patterns
    print("PARAMETER PATTERNS:")
    print("-" * 100)
    for lb_variant, patterns in insights['parameter_patterns'].items():
        print(f"\n{lb_variant.replace('_', '-').title()}:")
        for param, value in patterns.items():
            if isinstance(value, dict) and 'mean' in value:
                print(f"  {param}: mean={value['mean']:.4f}, range=[{value['min']:.4f}, {value['max']:.4f}]")
            elif isinstance(value, dict):
                print(f"  {param}: {value}")
    print()
    
    return insights

if __name__ == "__main__":
    results_list = load_recent_results(days_back=2)
    
    if not results_list:
        print("No recent result files found.")
        exit(1)
    
    print(f"Found {len(results_list)} result file(s) from today and yesterday")
    print()
    
    analysis = analyze_linearboost_performance(results_list)
    losses = extract_statistical_comparisons(results_list)
    insights = generate_improvement_insights(analysis, losses)
    
    print_analysis(analysis, losses, insights)
    
    # Save insights for later use
    import json
    with open('linearboost_analysis_insights.json', 'w') as f:
        json.dump(insights, f, indent=2, default=str)
    
    print("\n✓ Analysis saved to linearboost_analysis_insights.json")

