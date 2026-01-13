#!/usr/bin/env python3
"""
Analyze most recent UCI benchmark results and rank algorithms by:
- F1 Score
- ROC-AUC
- Training Time
- Inference Time

Aggregates rankings across all datasets.
"""

import json
from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd

def get_most_recent_uci_results(results_dir="benchmark_results", prefix="uci"):
    """Get the most recent UCI benchmark result files."""
    results_path = Path(results_dir)
    
    # Get all UCI JSON files
    json_files = sorted(results_path.glob(f"{prefix}_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Group by dataset (first part of filename)
    datasets = defaultdict(list)
    for file_path in json_files:
        # Extract dataset identifier (e.g., "uci_17_Breast" from "uci_17_Breast Cancer Wisconsin (Diagnostic)_20251227_200216.json")
        parts = file_path.stem.split('_')
        if len(parts) >= 3:
            dataset_key = '_'.join(parts[:3])  # e.g., "uci_17_Breast"
        else:
            dataset_key = file_path.stem.split('_')[0] + '_' + file_path.stem.split('_')[1] if '_' in file_path.stem else file_path.stem
        
        datasets[dataset_key].append(file_path)
    
    # Get most recent file for each dataset
    most_recent = {}
    for dataset_key, files in datasets.items():
        most_recent[dataset_key] = max(files, key=lambda x: x.stat().st_mtime)
    
    return most_recent

def load_and_extract_metrics(result_files):
    """Load all result files and extract metrics."""
    all_results = []
    
    for dataset_key, file_path in result_files.items():
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if 'results' not in data:
                continue
            
            results = data['results']
            dataset_name = file_path.stem.split('_', 2)[-1].split('_2025')[0] if '_2025' in file_path.stem else file_path.stem
            
            for model_name, model_data in results.items():
                all_results.append({
                    'dataset': dataset_name,
                    'dataset_key': dataset_key,
                    'model': model_name,
                    'f1_mean': model_data.get('f1_mean', 0),
                    'f1_std': model_data.get('f1_std', 0),
                    'roc_auc_mean': model_data.get('roc_auc_mean', 0),
                    'roc_auc_std': model_data.get('roc_auc_std', 0),
                    'avg_fit_time': model_data.get('avg_fit_time', 0),
                    'std_fit_time': model_data.get('std_fit_time', 0),
                    'avg_score_time': model_data.get('avg_score_time', 0),
                    'std_score_time': model_data.get('std_score_time', 0),
                })
        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")
            continue
    
    return pd.DataFrame(all_results)

def compute_rankings(df):
    """Compute rankings for each metric across datasets."""
    rankings = defaultdict(lambda: defaultdict(list))
    
    # Get unique datasets and models
    datasets = df['dataset'].unique()
    models = df['model'].unique()
    
    # For each dataset, rank models by each metric
    for dataset in datasets:
        dataset_df = df[df['dataset'] == dataset]
        
        if len(dataset_df) == 0:
            continue
        
        # F1 Score ranking (higher is better)
        f1_ranked = dataset_df.sort_values('f1_mean', ascending=False)
        for rank, (idx, row) in enumerate(f1_ranked.iterrows(), 1):
            rankings['f1'][row['model']].append(rank)
        
        # ROC-AUC ranking (higher is better)
        roc_ranked = dataset_df.sort_values('roc_auc_mean', ascending=False)
        for rank, (idx, row) in enumerate(roc_ranked.iterrows(), 1):
            rankings['roc_auc'][row['model']].append(rank)
        
        # Training time ranking (lower is better, so we reverse)
        train_ranked = dataset_df.sort_values('avg_fit_time', ascending=True)
        for rank, (idx, row) in enumerate(train_ranked.iterrows(), 1):
            rankings['train_time'][row['model']].append(rank)
        
        # Inference time ranking (lower is better, so we reverse)
        infer_ranked = dataset_df.sort_values('avg_score_time', ascending=True)
        for rank, (idx, row) in enumerate(infer_ranked.iterrows(), 1):
            rankings['inference_time'][row['model']].append(rank)
    
    return rankings

def aggregate_rankings(rankings):
    """Aggregate rankings across all datasets."""
    aggregated = {}
    
    for metric, model_ranks in rankings.items():
        aggregated[metric] = {}
        for model, ranks in model_ranks.items():
            if len(ranks) > 0:
                aggregated[metric][model] = {
                    'mean_rank': np.mean(ranks),
                    'median_rank': np.median(ranks),
                    'std_rank': np.std(ranks),
                    'min_rank': np.min(ranks),
                    'max_rank': np.max(ranks),
                    'n_datasets': len(ranks),
                    'wins': sum(1 for r in ranks if r == 1),  # Number of first places
                    'top3': sum(1 for r in ranks if r <= 3),  # Number of top 3 finishes
                }
    
    return aggregated

def print_rankings(df, rankings, aggregated):
    """Print comprehensive ranking analysis."""
    print("=" * 120)
    print("ALGORITHM RANKINGS - MOST RECENT UCI BENCHMARK RESULTS")
    print("=" * 120)
    print()
    
    # Summary
    datasets = df['dataset'].unique()
    models = df['model'].unique()
    print(f"Datasets analyzed: {len(datasets)}")
    print(f"Algorithms compared: {len(models)}")
    print()
    
    # Per-dataset rankings
    print("PER-DATASET RANKINGS:")
    print("-" * 120)
    
    for dataset in sorted(datasets):
        dataset_df = df[df['dataset'] == dataset].copy()
        if len(dataset_df) == 0:
            continue
        
        print(f"\n{dataset}:")
        print(f"{'Model':<25} {'F1':<10} {'ROC-AUC':<10} {'Train(s)':<12} {'Infer(s)':<12} {'F1 Rank':<8} {'AUC Rank':<8} {'Train Rank':<10} {'Infer Rank':<10}")
        print("-" * 120)
        
        # Sort by F1 score
        dataset_df = dataset_df.sort_values('f1_mean', ascending=False)
        
        for _, row in dataset_df.iterrows():
            # Get rankings for this dataset
            f1_rank = next((r for r, (idx, r_row) in enumerate(
                dataset_df.sort_values('f1_mean', ascending=False).iterrows(), 1) 
                if r_row['model'] == row['model']), len(dataset_df) + 1)
            auc_rank = next((r for r, (idx, r_row) in enumerate(
                dataset_df.sort_values('roc_auc_mean', ascending=False).iterrows(), 1) 
                if r_row['model'] == row['model']), len(dataset_df) + 1)
            train_rank = next((r for r, (idx, r_row) in enumerate(
                dataset_df.sort_values('avg_fit_time', ascending=True).iterrows(), 1) 
                if r_row['model'] == row['model']), len(dataset_df) + 1)
            infer_rank = next((r for r, (idx, r_row) in enumerate(
                dataset_df.sort_values('avg_score_time', ascending=True).iterrows(), 1) 
                if r_row['model'] == row['model']), len(dataset_df) + 1)
            
            print(f"{row['model']:<25} {row['f1_mean']:<10.4f} {row['roc_auc_mean']:<10.4f} "
                  f"{row['avg_fit_time']:<12.4f} {row['avg_score_time']:<12.6f} "
                  f"{f1_rank:<8} {auc_rank:<8} {train_rank:<10} {infer_rank:<10}")
    
    # Aggregated rankings
    print("\n" + "=" * 120)
    print("AGGREGATED RANKINGS ACROSS ALL DATASETS")
    print("=" * 120)
    
    for metric in ['f1', 'roc_auc', 'train_time', 'inference_time']:
        metric_name = {
            'f1': 'F1 Score',
            'roc_auc': 'ROC-AUC',
            'train_time': 'Training Time (lower is better)',
            'inference_time': 'Inference Time (lower is better)'
        }[metric]
        
        print(f"\n{metric_name.upper()}:")
        print("-" * 120)
        print(f"{'Model':<25} {'Mean Rank':<12} {'Median':<10} {'Std':<10} {'Wins':<6} {'Top-3':<6} {'Min':<6} {'Max':<6} {'N':<4}")
        print("-" * 120)
        
        # Sort by mean rank (lower is better)
        metric_aggregated = aggregated[metric]
        sorted_models = sorted(
            metric_aggregated.items(), 
            key=lambda x: x[1]['mean_rank']
        )
        
        for model, stats in sorted_models:
            print(f"{model:<25} {stats['mean_rank']:<12.2f} {stats['median_rank']:<10.1f} "
                  f"{stats['std_rank']:<10.2f} {stats['wins']:<6} {stats['top3']:<6} "
                  f"{stats['min_rank']:<6.0f} {stats['max_rank']:<6.0f} {stats['n_datasets']:<4}")
    
    # Overall ranking (average of all metrics)
    print("\n" + "=" * 120)
    print("OVERALL RANKING (Average of F1, ROC-AUC, Train Time, Inference Time Rankings)")
    print("=" * 120)
    print(f"{'Model':<25} {'Overall Rank':<15} {'F1 Rank':<12} {'AUC Rank':<12} {'Train Rank':<12} {'Infer Rank':<12}")
    print("-" * 120)
    
    # Calculate overall ranking
    all_models = set()
    for metric in aggregated.values():
        all_models.update(metric.keys())
    
    overall_ranks = []
    for model in all_models:
        mean_ranks = []
        for metric in ['f1', 'roc_auc', 'train_time', 'inference_time']:
            if model in aggregated[metric]:
                mean_ranks.append(aggregated[metric][model]['mean_rank'])
        
        if mean_ranks:
            overall_mean = np.mean(mean_ranks)
            overall_ranks.append({
                'model': model,
                'overall': overall_mean,
                'f1': aggregated['f1'].get(model, {}).get('mean_rank', np.nan),
                'roc_auc': aggregated['roc_auc'].get(model, {}).get('mean_rank', np.nan),
                'train_time': aggregated['train_time'].get(model, {}).get('mean_rank', np.nan),
                'inference_time': aggregated['inference_time'].get(model, {}).get('mean_rank', np.nan),
            })
    
    # Sort by overall rank
    overall_ranks = sorted(overall_ranks, key=lambda x: x['overall'])
    
    for rank, item in enumerate(overall_ranks, 1):
        print(f"{item['model']:<25} {item['overall']:<15.2f} {item['f1']:<12.2f} "
              f"{item['roc_auc']:<12.2f} {item['train_time']:<12.2f} {item['inference_time']:<12.2f}")

def save_rankings_to_csv(df, aggregated, output_file="algorithm_rankings.csv"):
    """Save rankings to CSV file."""
    # Create a comprehensive dataframe
    rows = []
    
    for metric in ['f1', 'roc_auc', 'train_time', 'inference_time']:
        metric_name = {
            'f1': 'F1_Score',
            'roc_auc': 'ROC_AUC',
            'train_time': 'Train_Time',
            'inference_time': 'Inference_Time'
        }[metric]
        
        for model, stats in aggregated[metric].items():
            rows.append({
                'Metric': metric_name,
                'Model': model,
                'Mean_Rank': stats['mean_rank'],
                'Median_Rank': stats['median_rank'],
                'Std_Rank': stats['std_rank'],
                'Wins': stats['wins'],
                'Top3': stats['top3'],
                'Min_Rank': stats['min_rank'],
                'Max_Rank': stats['max_rank'],
                'N_Datasets': stats['n_datasets'],
            })
    
    rank_df = pd.DataFrame(rows)
    rank_df.to_csv(output_file, index=False)
    print(f"\n✓ Rankings saved to {output_file}")

if __name__ == "__main__":
    # Get most recent results
    print("Loading most recent UCI benchmark results...")
    result_files = get_most_recent_uci_results()
    
    print(f"Found {len(result_files)} datasets:")
    for dataset_key, file_path in sorted(result_files.items()):
        print(f"  - {dataset_key}: {file_path.name}")
    print()
    
    if len(result_files) == 0:
        print("No UCI benchmark results found!")
        exit(1)
    
    # Load and extract metrics
    df = load_and_extract_metrics(result_files)
    
    if len(df) == 0:
        print("No metrics found in results!")
        exit(1)
    
    print(f"Loaded {len(df)} model-dataset combinations")
    print()
    
    # Compute rankings
    rankings = compute_rankings(df)
    
    # Aggregate rankings
    aggregated = aggregate_rankings(rankings)
    
    # Print analysis
    print_rankings(df, rankings, aggregated)
    
    # Save to CSV
    save_rankings_to_csv(df, aggregated)
    
    # Also save aggregated JSON
    import json
    with open('algorithm_rankings_aggregated.json', 'w') as f:
        json.dump(aggregated, f, indent=2, default=str)
    print(f"✓ Aggregated rankings saved to algorithm_rankings_aggregated.json")

