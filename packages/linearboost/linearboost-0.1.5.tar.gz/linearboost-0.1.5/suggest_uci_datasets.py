#!/usr/bin/env python3
"""
Script to analyze today's benchmark datasets and suggest additional UCI datasets
with similar characteristics that would maintain good results for LinearBoost variants.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

def get_today_date_string() -> str:
    """Get today's date in YYYYMMDD format."""
    return datetime.now().strftime("%Y%m%d")

def analyze_todays_datasets() -> List[Dict]:
    """Analyze today's UCI benchmark datasets."""
    results_dir = "benchmark_results"
    results_path = Path(results_dir)
    today = get_today_date_string()
    
    datasets_info = []
    
    for file_path in results_path.glob(f"uci_*_{today}*.json"):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Extract dataset info from first model's results (all models have same dataset info)
            if 'results' in data and len(data['results']) > 0:
                first_model = list(data['results'].keys())[0]
                model_data = data['results'][first_model]
                
                dataset_info = {
                    'name': model_data.get('dataset_name', 'Unknown'),
                    'id': model_data.get('dataset_id', 0),
                    'n_samples': model_data.get('n_samples', 0),
                    'n_features': model_data.get('n_features', 0),
                    'n_numeric': model_data.get('n_numeric', 0),
                    'n_categorical': model_data.get('n_categorical', 0),
                    'feature_type': model_data.get('feature_type', 'unknown'),
                    'imbalance_ratio': model_data.get('imbalance_ratio', 0),
                    'imbalance_category': model_data.get('imbalance_category', 'unknown'),
                    'dataset_size': model_data.get('dataset_size', 'unknown'),
                }
                datasets_info.append(dataset_info)
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")
    
    return sorted(datasets_info, key=lambda x: x['id'])

def suggest_uci_datasets(current_datasets: List[Dict]) -> List[Dict]:
    """
    Suggest additional UCI datasets based on characteristics of current datasets.
    
    Characteristics to match:
    - Small to medium size (100-2000 samples)
    - Binary classification
    - Mostly numeric features (or mixed with few categorical)
    - Balanced to moderately imbalanced
    - Medical/health, pattern recognition, or similar domains
    """
    
    # Calculate average characteristics
    avg_samples = sum(d['n_samples'] for d in current_datasets) / len(current_datasets)
    avg_features = sum(d['n_features'] for d in current_datasets) / len(current_datasets)
    
    print(f"\nCurrent Dataset Characteristics:")
    print(f"  Average samples: {avg_samples:.0f}")
    print(f"  Average features: {avg_features:.0f}")
    print(f"  Size range: {min(d['n_samples'] for d in current_datasets)} - {max(d['n_samples'] for d in current_datasets)}")
    print(f"  Feature range: {min(d['n_features'] for d in current_datasets)} - {max(d['n_features'] for d in current_datasets)}")
    
    # Suggested UCI datasets with similar characteristics
    suggestions = [
        {
            'id': 21,
            'name': 'Car Evaluation',
            'n_samples': 1728,
            'n_features': 6,
            'feature_type': 'categorical',
            'domain': 'Decision making',
            'reason': 'Similar size to Banknote, categorical features test LinearBoost flexibility'
        },
        {
            'id': 27,
            'name': 'Breast Cancer Wisconsin (Original)',
            'n_samples': 699,
            'n_features': 9,
            'feature_type': 'numeric',
            'domain': 'Medical',
            'reason': 'Related to dataset 17, similar medical domain'
        },
        {
            'id': 53,
            'name': 'Iris (binary version)',
            'n_samples': 150,
            'n_features': 4,
            'feature_type': 'numeric',
            'domain': 'Botany',
            'reason': 'Classic small dataset, similar to Hepatitis size'
        },
        {
            'id': 109,
            'name': 'Wine',
            'n_samples': 178,
            'n_features': 13,
            'feature_type': 'numeric',
            'domain': 'Food/Chemistry',
            'reason': 'Small, numeric, balanced - good for LinearBoost'
        },
        {
            'id': 142,
            'name': 'Pima Indians Diabetes',
            'n_samples': 768,
            'n_features': 8,
            'feature_type': 'numeric',
            'domain': 'Medical',
            'reason': 'Medical domain like Heart Disease, moderate imbalance'
        },
        {
            'id': 148,
            'name': 'Connectionist Bench (Sonar, Mines vs Rocks)',
            'n_samples': 208,
            'n_features': 60,
            'feature_type': 'numeric',
            'domain': 'Pattern Recognition',
            'reason': 'Similar to Ionosphere (high-dimensional numeric)'
        },
        {
            'id': 158,
            'name': 'Parkinsons',
            'n_samples': 197,
            'n_features': 22,
            'feature_type': 'numeric',
            'domain': 'Medical',
            'reason': 'Medical domain, small size like Hepatitis'
        },
        {
            'id': 182,
            'name': 'Sonar (Mines vs Rocks)',
            'n_samples': 208,
            'n_features': 60,
            'feature_type': 'numeric',
            'domain': 'Pattern Recognition',
            'reason': 'High-dimensional like Ionosphere'
        },
        {
            'id': 264,
            'name': 'Statlog (German Credit Data)',
            'n_samples': 1000,
            'n_features': 20,
            'feature_type': 'mixed',
            'domain': 'Finance',
            'reason': 'Mixed features like Chronic Kidney Disease, financial domain'
        },
        {
            'id': 275,
            'name': 'Yeast',
            'n_samples': 1484,
            'n_features': 8,
            'feature_type': 'numeric',
            'domain': 'Biology',
            'reason': 'Medium size like Banknote, numeric features'
        },
        {
            'id': 329,
            'name': 'Lymphography',
            'n_samples': 148,
            'n_features': 18,
            'feature_type': 'mixed',
            'domain': 'Medical',
            'reason': 'Medical domain, small size, mixed features'
        },
        {
            'id': 350,
            'name': 'Adult',
            'n_samples': 48842,
            'n_features': 14,
            'feature_type': 'mixed',
            'domain': 'Demographics',
            'reason': 'Larger dataset for scalability test (though may need sampling)'
        },
        {
            'id': 445,
            'name': 'QSAR Biodegradation',
            'n_samples': 1055,
            'n_features': 41,
            'feature_type': 'numeric',
            'domain': 'Chemistry',
            'reason': 'Similar to Ionosphere (high-dimensional), medium size'
        },
        {
            'id': 450,
            'name': 'EEG Eye State',
            'n_samples': 14980,
            'n_features': 14,
            'feature_type': 'numeric',
            'domain': 'Biomedical',
            'reason': 'Larger dataset, biomedical domain (may need sampling)'
        },
        {
            'id': 457,
            'name': 'Phishing Websites',
            'n_samples': 11055,
            'n_features': 30,
            'feature_type': 'mixed',
            'domain': 'Cybersecurity',
            'reason': 'Mixed features, similar feature count to Breast Cancer (may need sampling)'
        },
        {
            'id': 468,
            'name': 'Statlog (Australian Credit Approval)',
            'n_samples': 690,
            'n_features': 14,
            'feature_type': 'mixed',
            'domain': 'Finance',
            'reason': 'Similar size to Breast Cancer, mixed features, financial domain'
        },
        {
            'id': 469,
            'name': 'Wilt',
            'n_samples': 4839,
            'n_features': 5,
            'feature_type': 'numeric',
            'domain': 'Remote Sensing',
            'reason': 'Medium size, few features (may need sampling)'
        },
        {
            'id': 470,
            'name': 'Blood Transfusion Service Center',
            'n_samples': 748,
            'n_features': 4,
            'feature_type': 'numeric',
            'domain': 'Medical',
            'reason': 'Medical domain, similar to Banknote (few features)'
        },
    ]
    
    # Filter suggestions based on size constraints (similar to current datasets)
    filtered_suggestions = [
        s for s in suggestions 
        if 100 <= s['n_samples'] <= 2000  # Focus on small-medium like current datasets
    ]
    
    # Add a few larger ones for diversity
    larger_suggestions = [
        s for s in suggestions 
        if 2000 < s['n_samples'] <= 5000  # Medium-large for scalability
    ]
    
    return filtered_suggestions + larger_suggestions[:3]  # Add top 3 larger ones

def print_recommendations(current_datasets: List[Dict], suggestions: List[Dict]):
    """Print formatted recommendations."""
    print("\n" + "=" * 100)
    print("UCI DATASET RECOMMENDATIONS FOR LINEARBOOST BENCHMARKING")
    print("=" * 100)
    
    print("\n📊 CURRENT DATASETS (Today's Benchmarks):")
    print("-" * 100)
    print(f"{'ID':<6} {'Name':<40} {'Samples':<10} {'Features':<10} {'Type':<12} {'Imbalance':<12}")
    print("-" * 100)
    for d in current_datasets:
        print(f"{d['id']:<6} {d['name']:<40} {d['n_samples']:<10} {d['n_features']:<10} "
              f"{d['feature_type']:<12} {d['imbalance_category']:<12}")
    
    print("\n\n🎯 RECOMMENDED ADDITIONAL DATASETS:")
    print("-" * 100)
    print(f"{'ID':<6} {'Name':<40} {'Samples':<10} {'Features':<10} {'Type':<12} {'Domain':<20} {'Priority':<10}")
    print("-" * 100)
    
    # Sort by priority (smaller, similar characteristics first)
    sorted_suggestions = sorted(suggestions, key=lambda x: (abs(x['n_samples'] - 500), x['n_samples']))
    
    for i, s in enumerate(sorted_suggestions, 1):
        # Determine priority
        if s['n_samples'] <= 500:
            priority = "HIGH"
        elif s['n_samples'] <= 1500:
            priority = "MEDIUM"
        else:
            priority = "LOW"
        
        print(f"{s['id']:<6} {s['name']:<40} {s['n_samples']:<10} {s['n_features']:<10} "
              f"{s['feature_type']:<12} {s['domain']:<20} {priority:<10}")
        print(f"       └─ Reason: {s['reason']}")
    
    print("\n\n📋 TOP PRIORITY RECOMMENDATIONS:")
    print("-" * 100)
    top_priority = [s for s in sorted_suggestions if 100 <= s['n_samples'] <= 500]
    for i, s in enumerate(top_priority[:10], 1):
        print(f"{i}. Dataset ID {s['id']}: {s['name']}")
        print(f"   - {s['n_samples']} samples, {s['n_features']} features ({s['feature_type']})")
        print(f"   - Domain: {s['domain']}")
        print(f"   - Reason: {s['reason']}")
        print()
    
    print("\n💡 USAGE NOTES:")
    print("-" * 100)
    print("1. Small datasets (100-500 samples): Best match for current benchmarks")
    print("2. Medium datasets (500-2000 samples): Good for scalability testing")
    print("3. Larger datasets (>2000 samples): May need sampling for HP tuning")
    print("4. Focus on datasets with numeric or mixed features")
    print("5. Prefer balanced to moderately imbalanced datasets")
    print("6. Medical/health datasets align well with current dataset themes")

if __name__ == "__main__":
    print("Analyzing today's benchmark datasets...")
    current_datasets = analyze_todays_datasets()
    
    if not current_datasets:
        print("No datasets found for today. Make sure benchmarks have been run.")
        exit(1)
    
    print(f"\nFound {len(current_datasets)} datasets from today's benchmarks.")
    
    suggestions = suggest_uci_datasets(current_datasets)
    print_recommendations(current_datasets, suggestions)

