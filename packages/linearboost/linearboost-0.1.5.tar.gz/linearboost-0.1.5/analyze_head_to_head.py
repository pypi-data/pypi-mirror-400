#!/usr/bin/env python3
"""
Analyze head-to-head wins/losses between algorithms based on UCI benchmark results.
Treats all LinearBoost variants as one classifier.
"""

import json
from pathlib import Path
from collections import defaultdict
import pandas as pd
import numpy as np

def get_most_recent_uci_results(results_dir="benchmark_results", prefix="uci"):
    """Get the most recent UCI benchmark result files."""
    results_path = Path(results_dir)
    
    # Get all UCI JSON files
    json_files = sorted(results_path.glob(f"{prefix}_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Group by dataset (first part of filename)
    datasets = defaultdict(list)
    for file_path in json_files:
        # Extract dataset identifier
        parts = file_path.stem.split('_')
        if len(parts) >= 3:
            dataset_key = '_'.join(parts[:3])
        else:
            dataset_key = file_path.stem.split('_')[0] + '_' + file_path.stem.split('_')[1] if '_' in file_path.stem else file_path.stem
        
        datasets[dataset_key].append(file_path)
    
    # Get most recent file for each dataset
    most_recent = {}
    for dataset_key, files in datasets.items():
        most_recent[dataset_key] = max(files, key=lambda x: x.stat().st_mtime)
    
    return most_recent

def normalize_algorithm_name(name):
    """Normalize algorithm names, grouping LinearBoost variants."""
    if name.startswith('LinearBoost'):
        return 'LinearBoost'
    return name

def load_results(result_files):
    """Load all result files and extract metrics."""
    all_results = {}
    
    for dataset_key, file_path in result_files.items():
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if 'results' not in data:
                continue
            
            results = data['results']
            dataset_name = file_path.stem.split('_', 2)[-1].split('_2025')[0] if '_2025' in file_path.stem else file_path.stem
            
            # For LinearBoost variants, take the best performing one per dataset
            linearboost_results = {}
            other_results = {}
            
            for model_name, model_data in results.items():
                normalized_name = normalize_algorithm_name(model_name)
                
                if normalized_name == 'LinearBoost':
                    linearboost_results[model_name] = model_data
                else:
                    other_results[normalized_name] = model_data
            
            # Select best LinearBoost variant per dataset (by F1 score)
            if linearboost_results:
                best_linearboost = max(linearboost_results.items(), 
                                      key=lambda x: x[1].get('f1_mean', 0))
                other_results['LinearBoost'] = best_linearboost[1]
            
            all_results[dataset_name] = other_results
            
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
            continue
    
    return all_results

def compare_algorithms_pairwise(all_results, metric='f1_mean'):
    """Compare algorithms pairwise and count wins/losses."""
    # Get all unique algorithms
    all_algorithms = set()
    for dataset_results in all_results.values():
        all_algorithms.update(dataset_results.keys())
    
    all_algorithms = sorted(list(all_algorithms))
    
    # Initialize win/loss matrices
    wins = defaultdict(lambda: defaultdict(int))
    losses = defaultdict(lambda: defaultdict(int))
    ties = defaultdict(lambda: defaultdict(int))
    comparisons = defaultdict(lambda: defaultdict(int))
    
    # Compare on each dataset
    for dataset_name, dataset_results in all_results.items():
        # Filter algorithms that have results for this dataset
        available_algorithms = [alg for alg in all_algorithms if alg in dataset_results]
        
        # Pairwise comparison
        for i, alg1 in enumerate(available_algorithms):
            for j, alg2 in enumerate(available_algorithms):
                if i >= j:
                    continue
                
                score1 = dataset_results[alg1].get(metric, 0)
                score2 = dataset_results[alg2].get(metric, 0)
                
                comparisons[alg1][alg2] += 1
                comparisons[alg2][alg1] += 1
                
                if score1 > score2:
                    wins[alg1][alg2] += 1
                    losses[alg2][alg1] += 1
                elif score1 < score2:
                    wins[alg2][alg1] += 1
                    losses[alg1][alg2] += 1
                else:
                    ties[alg1][alg2] += 1
                    ties[alg2][alg1] += 1
    
    return all_algorithms, wins, losses, ties, comparisons

def print_comparison_matrix(algorithms, wins, losses, ties, comparisons, metric_name="F1"):
    """Print a comparison matrix."""
    print(f"\n{'='*80}")
    print(f"HEAD-TO-HEAD COMPARISON: {metric_name.upper()}")
    print(f"{'='*80}\n")
    
    # Create matrix
    n = len(algorithms)
    
    # Header
    header = f"{'Algorithm':<25} | "
    for alg in algorithms:
        header += f"{alg:<15} | "
    print(header)
    print("-" * len(header))
    
    # Rows
    for alg1 in algorithms:
        row = f"{alg1:<25} | "
        for alg2 in algorithms:
            if alg1 == alg2:
                row += f"{'--':<15} | "
            else:
                w = wins[alg1][alg2]
                l = losses[alg1][alg2]
                t = ties[alg1][alg2]
                total = comparisons[alg1][alg2]
                
                if total > 0:
                    row += f"{w}-{l}-{t:<3}({total}) | "
                else:
                    row += f"{'--':<15} | "
        print(row)

def print_summary_statistics(algorithms, wins, losses, ties, comparisons):
    """Print summary statistics."""
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}\n")
    
    summary_data = []
    for alg in algorithms:
        total_wins = sum(wins[alg].values())
        total_losses = sum(losses[alg].values())
        total_ties = sum(ties[alg].values())
        total_comparisons = total_wins + total_losses + total_ties
        
        win_rate = (total_wins / total_comparisons * 100) if total_comparisons > 0 else 0
        
        summary_data.append({
            'Algorithm': alg,
            'Wins': total_wins,
            'Losses': total_losses,
            'Ties': total_ties,
            'Total': total_comparisons,
            'Win Rate (%)': f"{win_rate:.1f}"
        })
    
    df = pd.DataFrame(summary_data)
    df = df.sort_values('Win Rate (%)', ascending=False, key=lambda x: x.str.rstrip('%').astype(float))
    
    print(df.to_string(index=False))
    
    return df

def main():
    print("Analyzing head-to-head comparisons from UCI benchmark results...")
    print("Treating all LinearBoost variants as one classifier\n")
    
    # Load results
    result_files = get_most_recent_uci_results()
    print(f"Found {len(result_files)} datasets\n")
    
    all_results = load_results(result_files)
    print(f"Loaded results for {len(all_results)} datasets")
    
    # Analyze for different metrics
    metrics = {
        'f1_mean': 'F1 Score',
        'roc_auc_mean': 'ROC-AUC'
    }
    
    for metric, metric_name in metrics.items():
        algorithms, wins, losses, ties, comparisons = compare_algorithms_pairwise(all_results, metric)
        
        print_comparison_matrix(algorithms, wins, losses, ties, comparisons, metric_name)
        summary_df = print_summary_statistics(algorithms, wins, losses, ties, comparisons)
        
        # Save to CSV
        output_file = f'head_to_head_{metric}.csv'
        summary_df.to_csv(output_file, index=False)
        print(f"\nSaved summary to {output_file}")

if __name__ == "__main__":
    main()
