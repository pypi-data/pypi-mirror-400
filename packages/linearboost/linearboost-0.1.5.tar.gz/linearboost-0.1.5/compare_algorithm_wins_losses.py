#!/usr/bin/env python3
"""
Script to compare algorithm wins and losses based on statistical significance tests
from benchmark results JSON files from yesterday (only files starting with 'uci').

This script:
1. Reads JSON files starting with 'uci' in benchmark_results folder from yesterday
2. Extracts pairwise statistical comparisons (F1 and ROC-AUC)
3. Counts wins and losses based on Bonferroni-corrected significance or Nemenyi test
4. Focuses on LinearBoost variants vs other algorithms
5. Prints a summary of wins/losses for LinearBoost variants
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple

def get_yesterday_date_string() -> str:
    """Get yesterday's date in YYYYMMDD format."""
    yesterday = datetime.now() - timedelta(days=0)
    return yesterday.strftime("%Y%m%d")

def get_yesterdays_uci_json_files(results_dir: str) -> List[Path]:
    """Get JSON files starting with 'uci' from yesterday's date in the benchmark_results folder."""
    results_path = Path(results_dir)
    yesterday = get_yesterday_date_string()
    json_files = []
    
    for file_path in results_path.glob("*.json"):
        # Check if file starts with 'uci' and contains yesterday's date
        if file_path.name.startswith("uci") and yesterday in file_path.name:
            json_files.append(file_path)
    
    return sorted(json_files)

def load_json_file(file_path: Path) -> dict:
    """Load a JSON file and return its contents."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load {file_path.name}: {e}")
        return {}

def extract_pairwise_comparisons(data: dict, use_nemenyi: bool = False) -> List[Tuple[str, str, str, str]]:
    """
    Extract pairwise comparisons from JSON data.
    
    Returns list of tuples: (model1, model2, better_model, metric, is_significant)
    where metric is 'f1' or 'roc_auc'
    """
    comparisons = []
    
    if 'statistical_results' not in data:
        return comparisons
    
    stats = data['statistical_results']
    
    # Process F1 comparisons
    if 'pairwise_f1' in stats:
        for pair_name, comparison in stats['pairwise_f1'].items():
            if 'better_model' in comparison:
                # Use Nemenyi if requested, otherwise Bonferroni
                is_significant = comparison.get('nemenyi_significant', False) if use_nemenyi else comparison.get('significant_bonferroni', False)
                if is_significant:
                    model1, model2 = pair_name.split('_vs_')
                    better_model = comparison['better_model']
                    comparisons.append((model1, model2, better_model, 'f1', True))
    
    # Process ROC-AUC comparisons
    if 'pairwise_roc' in stats:
        for pair_name, comparison in stats['pairwise_roc'].items():
            if 'better_model' in comparison:
                # Use Nemenyi if requested, otherwise Bonferroni
                is_significant = comparison.get('nemenyi_significant', False) if use_nemenyi else comparison.get('significant_bonferroni', False)
                if is_significant:
                    model1, model2 = pair_name.split('_vs_')
                    better_model = comparison['better_model']
                    comparisons.append((model1, model2, better_model, 'roc_auc', True))
    
    return comparisons

def is_linearboost_variant(algorithm: str) -> bool:
    """Check if an algorithm is a LinearBoost variant."""
    return algorithm.startswith("LinearBoost")

def get_linearboost_variants(comparisons: List[Tuple[str, str, str, str, bool]]) -> set:
    """Extract all LinearBoost variant names from comparisons."""
    variants = set()
    for model1, model2, _, _, _ in comparisons:
        if is_linearboost_variant(model1):
            variants.add(model1)
        if is_linearboost_variant(model2):
            variants.add(model2)
    return variants

def count_linearboost_vs_others(comparisons: List[Tuple[str, str, str, str, bool]]) -> Dict[str, Dict[str, Dict[str, int]]]:
    """
    Count wins and losses for LinearBoost variants vs other algorithms.
    
    Returns a dictionary: {
        variant: {
            'vs_others': {'wins': int, 'losses': int, 'wins_f1': int, 'wins_roc': int, 
                         'losses_f1': int, 'losses_roc': int},
            'vs_specific': {other_algorithm: {'wins': int, 'losses': int}}
        }
    }
    """
    stats = defaultdict(lambda: {
        'vs_others': {
            'wins': 0,
            'losses': 0,
            'wins_f1': 0,
            'wins_roc': 0,
            'losses_f1': 0,
            'losses_roc': 0
        },
        'vs_specific': defaultdict(lambda: {'wins': 0, 'losses': 0})
    })
    
    for model1, model2, better_model, metric, is_significant in comparisons:
        if not is_significant:
            continue
        
        # Check if this is a LinearBoost vs other comparison
        lb_variant = None
        other_algorithm = None
        
        if is_linearboost_variant(model1) and not is_linearboost_variant(model2):
            lb_variant = model1
            other_algorithm = model2
        elif is_linearboost_variant(model2) and not is_linearboost_variant(model1):
            lb_variant = model2
            other_algorithm = model1
        else:
            # Skip LinearBoost vs LinearBoost comparisons or non-LinearBoost comparisons
            continue
        
        # Determine winner
        lb_won = (better_model == lb_variant)
        
        # Update overall stats
        if lb_won:
            stats[lb_variant]['vs_others']['wins'] += 1
        else:
            stats[lb_variant]['vs_others']['losses'] += 1
        
        # Update metric-specific stats
        if metric == 'f1':
            if lb_won:
                stats[lb_variant]['vs_others']['wins_f1'] += 1
            else:
                stats[lb_variant]['vs_others']['losses_f1'] += 1
        elif metric == 'roc_auc':
            if lb_won:
                stats[lb_variant]['vs_others']['wins_roc'] += 1
            else:
                stats[lb_variant]['vs_others']['losses_roc'] += 1
        
        # Update specific algorithm stats
        if lb_won:
            stats[lb_variant]['vs_specific'][other_algorithm]['wins'] += 1
        else:
            stats[lb_variant]['vs_specific'][other_algorithm]['losses'] += 1
    
    # Convert defaultdict to regular dict
    result = {}
    for variant, variant_stats in stats.items():
        result[variant] = {
            'vs_others': variant_stats['vs_others'],
            'vs_specific': dict(variant_stats['vs_specific'])
        }
    
    return result

def count_wins_losses(comparisons: List[Tuple[str, str, str, str, bool]]) -> Dict[str, Dict[str, int]]:
    """
    Count wins and losses for each algorithm.
    
    Returns a dictionary: {algorithm: {'wins': int, 'losses': int, 'wins_f1': int, 'wins_roc': int, 
                                      'losses_f1': int, 'losses_roc': int}}
    """
    stats = defaultdict(lambda: {
        'wins': 0,
        'losses': 0,
        'wins_f1': 0,
        'wins_roc': 0,
        'losses_f1': 0,
        'losses_roc': 0
    })
    
    for model1, model2, better_model, metric, is_significant in comparisons:
        if not is_significant:
            continue
        
        if better_model == model1:
            winner = model1
            loser = model2
        else:
            winner = model2
            loser = model1
        
        # Update overall wins/losses
        stats[winner]['wins'] += 1
        stats[loser]['losses'] += 1
        
        # Update metric-specific wins/losses
        if metric == 'f1':
            stats[winner]['wins_f1'] += 1
            stats[loser]['losses_f1'] += 1
        elif metric == 'roc_auc':
            stats[winner]['wins_roc'] += 1
            stats[loser]['losses_roc'] += 1
    
    return dict(stats)

def print_linearboost_summary(lb_stats: Dict[str, Dict[str, Dict[str, int]]], use_nemenyi: bool = False):
    """Print a formatted summary of LinearBoost variants vs other algorithms."""
    test_type = "Nemenyi" if use_nemenyi else "Bonferroni-corrected"
    
    print("=" * 90)
    print(f"LINEARBOOST VARIANTS vs OTHER ALGORITHMS (Based on {test_type} Significance Tests)")
    print("=" * 90)
    print()
    
    if not lb_stats:
        print("No LinearBoost vs other algorithm comparisons found.")
        return
    
    # Print overall summary for each LinearBoost variant
    print("OVERALL SUMMARY: LinearBoost Variants vs All Other Algorithms")
    print("-" * 90)
    print(f"{'LinearBoost Variant':<30} {'Wins':<8} {'Losses':<8} {'Win Rate':<12} {'F1 Wins':<10} {'F1 Losses':<12} {'ROC Wins':<10} {'ROC Losses':<10}")
    print("-" * 90)
    
    # Sort variants by win rate
    sorted_variants = sorted(
        lb_stats.items(),
        key=lambda x: x[1]['vs_others']['wins'] / max(x[1]['vs_others']['wins'] + x[1]['vs_others']['losses'], 1),
        reverse=True
    )
    
    for variant, stats in sorted_variants:
        vs_others = stats['vs_others']
        total = vs_others['wins'] + vs_others['losses']
        win_rate = (vs_others['wins'] / total * 100) if total > 0 else 0.0
        
        print(f"{variant:<30} {vs_others['wins']:<8} {vs_others['losses']:<8} {win_rate:>8.1f}%     "
              f"{vs_others['wins_f1']:<10} {vs_others['losses_f1']:<12} {vs_others['wins_roc']:<10} {vs_others['losses_roc']:<10}")
    
    print()
    print("=" * 90)
    print()
    
    # Print detailed breakdown by metric
    print("DETAILED BREAKDOWN BY METRIC:")
    print("-" * 90)
    
    print("\nF1 Score: LinearBoost Variants vs Other Algorithms")
    print(f"{'LinearBoost Variant':<30} {'Wins':<8} {'Losses':<8} {'Win Rate':<12}")
    print("-" * 70)
    f1_sorted = sorted(
        lb_stats.items(),
        key=lambda x: x[1]['vs_others']['wins_f1'] / max(x[1]['vs_others']['wins_f1'] + x[1]['vs_others']['losses_f1'], 1),
        reverse=True
    )
    for variant, stats in f1_sorted:
        vs_others = stats['vs_others']
        total_f1 = vs_others['wins_f1'] + vs_others['losses_f1']
        win_rate_f1 = (vs_others['wins_f1'] / total_f1 * 100) if total_f1 > 0 else 0.0
        print(f"{variant:<30} {vs_others['wins_f1']:<8} {vs_others['losses_f1']:<8} {win_rate_f1:>8.1f}%")
    
    print("\nROC-AUC: LinearBoost Variants vs Other Algorithms")
    print(f"{'LinearBoost Variant':<30} {'Wins':<8} {'Losses':<8} {'Win Rate':<12}")
    print("-" * 70)
    roc_sorted = sorted(
        lb_stats.items(),
        key=lambda x: x[1]['vs_others']['wins_roc'] / max(x[1]['vs_others']['wins_roc'] + x[1]['vs_others']['losses_roc'], 1),
        reverse=True
    )
    for variant, stats in roc_sorted:
        vs_others = stats['vs_others']
        total_roc = vs_others['wins_roc'] + vs_others['losses_roc']
        win_rate_roc = (vs_others['wins_roc'] / total_roc * 100) if total_roc > 0 else 0.0
        print(f"{variant:<30} {vs_others['wins_roc']:<8} {vs_others['losses_roc']:<8} {win_rate_roc:>8.1f}%")
    
    print()
    print("=" * 90)
    print()
    
    # Print breakdown by specific algorithm
    print("DETAILED BREAKDOWN: LinearBoost Variants vs Specific Algorithms")
    print("-" * 90)
    
    for variant, stats in sorted_variants:
        vs_specific = stats['vs_specific']
        if not vs_specific:
            continue
        
        print(f"\n{variant}:")
        print(f"{'Opponent Algorithm':<35} {'Wins':<8} {'Losses':<8} {'Win Rate':<12}")
        print("-" * 70)
        
        # Sort by win rate
        sorted_opponents = sorted(
            vs_specific.items(),
            key=lambda x: x[1]['wins'] / max(x[1]['wins'] + x[1]['losses'], 1),
            reverse=True
        )
        
        for opponent, opponent_stats in sorted_opponents:
            total = opponent_stats['wins'] + opponent_stats['losses']
            win_rate = (opponent_stats['wins'] / total * 100) if total > 0 else 0.0
            print(f"{opponent:<35} {opponent_stats['wins']:<8} {opponent_stats['losses']:<8} {win_rate:>8.1f}%")
    
    print()

def print_summary(stats: Dict[str, Dict[str, int]], use_nemenyi: bool = False):
    """Print a formatted summary of wins and losses (legacy function for all algorithms)."""
    test_type = "Nemenyi" if use_nemenyi else "Bonferroni-corrected"
    
    print("=" * 80)
    print(f"ALL ALGORITHM WINS AND LOSSES (Based on {test_type} Significance Tests)")
    print("=" * 80)
    print()
    
    # Sort algorithms by win rate (wins / (wins + losses))
    sorted_algorithms = sorted(
        stats.items(),
        key=lambda x: x[1]['wins'] / max(x[1]['wins'] + x[1]['losses'], 1),
        reverse=True
    )
    
    print(f"{'Algorithm':<30} {'Wins':<8} {'Losses':<8} {'Win Rate':<10} {'F1 Wins':<10} {'F1 Losses':<12} {'ROC Wins':<10} {'ROC Losses':<10}")
    print("-" * 110)
    
    for algorithm, counts in sorted_algorithms:
        total = counts['wins'] + counts['losses']
        win_rate = (counts['wins'] / total * 100) if total > 0 else 0.0
        
        print(f"{algorithm:<30} {counts['wins']:<8} {counts['losses']:<8} {win_rate:>6.1f}%     "
              f"{counts['wins_f1']:<10} {counts['losses_f1']:<12} {counts['wins_roc']:<10} {counts['losses_roc']:<10}")

def main():
    """Main function to process benchmark results and print summary."""
    # Get yesterday's UCI JSON files
    results_dir = "benchmark_results"
    json_files = get_yesterdays_uci_json_files(results_dir)
    
    if not json_files:
        yesterday = get_yesterday_date_string()
        print(f"No JSON files starting with 'uci' found for yesterday ({yesterday}) in {results_dir}/")
        print("Make sure benchmark results have been generated yesterday.")
        return
    
    yesterday = get_yesterday_date_string()
    print(f"Found {len(json_files)} JSON file(s) starting with 'uci' for yesterday ({yesterday}):")
    for f in json_files:
        print(f"  - {f.name}")
    print()
    
    # Process all files
    all_comparisons_bonferroni = []
    all_comparisons_nemenyi = []
    
    for json_file in json_files:
        data = load_json_file(json_file)
        if data:
            comparisons_bonf = extract_pairwise_comparisons(data, use_nemenyi=False)
            comparisons_nem = extract_pairwise_comparisons(data, use_nemenyi=True)
            all_comparisons_bonferroni.extend(comparisons_bonf)
            all_comparisons_nemenyi.extend(comparisons_nem)
    
    if not all_comparisons_bonferroni and not all_comparisons_nemenyi:
        print("No pairwise comparisons found in the JSON files.")
        return
    
    # Count LinearBoost vs others
    lb_stats_bonferroni = count_linearboost_vs_others(all_comparisons_bonferroni)
    lb_stats_nemenyi = count_linearboost_vs_others(all_comparisons_nemenyi)
    
    # Count all wins/losses (for optional full summary)
    all_stats_bonferroni = count_wins_losses(all_comparisons_bonferroni)
    all_stats_nemenyi = count_wins_losses(all_comparisons_nemenyi)
    
    # Print LinearBoost-focused summaries
    if lb_stats_bonferroni:
        print_linearboost_summary(lb_stats_bonferroni, use_nemenyi=False)
        print()
    
    if lb_stats_nemenyi and lb_stats_nemenyi != lb_stats_bonferroni:
        print_linearboost_summary(lb_stats_nemenyi, use_nemenyi=True)
        print()
    
    # Optionally print full summary (uncomment if needed)
    # print("=" * 80)
    # print("FULL SUMMARY (All Algorithms)")
    # print("=" * 80)
    # if all_stats_bonferroni:
    #     print_summary(all_stats_bonferroni, use_nemenyi=False)
    #     print()
    # if all_stats_nemenyi and all_stats_nemenyi != all_stats_bonferroni:
    #     print_summary(all_stats_nemenyi, use_nemenyi=True)

if __name__ == "__main__":
    main()

