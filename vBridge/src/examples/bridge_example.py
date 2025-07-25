#!/usr/bin/env python3
"""
Example demonstrating the new bridge calculator architecture.

This script shows how to use the BridgeOrchestrator to calculate
contributions for different types of metrics.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.core.orchestrator import BridgeOrchestrator
from src.config.bridge_mappings import get_bridge_configuration, get_metrics_by_bridge_type
from src.models.bridge_types import BridgeType


def create_sample_data():
    """Create sample campaign data for demonstration."""
    # Sample campaign data
    campaigns = ['Campaign A', 'Campaign B', 'Campaign C']
    
    data = {
        'Campaign': campaigns,
        
        # Absolute metrics (Type 1: Mix Bridge)
        'Spend - January 2025': [1000, 2000, 1500],
        'Spend - February 2025': [1200, 1800, 2000],
        'Total Ad Sales - January 2025': [5000, 8000, 4500],
        'Total Ad Sales - February 2025': [6000, 7500, 6000],
        'Clicks - January 2025': [100, 200, 150],
        'Clicks - February 2025': [120, 180, 200],
        'Impressions - January 2025': [10000, 15000, 12000],
        'Impressions - February 2025': [12000, 14000, 16000],
        
        # We'll calculate rate metrics from these base values
    }
    
    df = pd.DataFrame(data)
    
    # Calculate rate metrics
    # ROAS (Type 2: MixRate Bridge)
    df['ROAS - January 2025'] = df['Total Ad Sales - January 2025'] / df['Spend - January 2025']
    df['ROAS - February 2025'] = df['Total Ad Sales - February 2025'] / df['Spend - February 2025']
    
    # CTR (Type 2: MixRate Bridge)
    df['CTR - January 2025'] = (df['Clicks - January 2025'] / df['Impressions - January 2025']) * 100
    df['CTR - February 2025'] = (df['Clicks - February 2025'] / df['Impressions - February 2025']) * 100
    
    # ACoS (Type 3: MixRate Infinity)
    df['ACoS - January 2025'] = (df['Spend - January 2025'] / df['Total Ad Sales - January 2025']) * 100
    df['ACoS - February 2025'] = (df['Spend - February 2025'] / df['Total Ad Sales - February 2025']) * 100
    
    # Create total row
    total_row = pd.DataFrame([{
        'Campaign': 'Total',
        'Spend - January 2025': df['Spend - January 2025'].sum(),
        'Spend - February 2025': df['Spend - February 2025'].sum(),
        'Total Ad Sales - January 2025': df['Total Ad Sales - January 2025'].sum(),
        'Total Ad Sales - February 2025': df['Total Ad Sales - February 2025'].sum(),
        'Clicks - January 2025': df['Clicks - January 2025'].sum(),
        'Clicks - February 2025': df['Clicks - February 2025'].sum(),
        'Impressions - January 2025': df['Impressions - January 2025'].sum(),
        'Impressions - February 2025': df['Impressions - February 2025'].sum(),
    }])
    
    # Calculate total rate metrics
    total_row['ROAS - January 2025'] = (
        total_row['Total Ad Sales - January 2025'] / total_row['Spend - January 2025']
    )
    total_row['ROAS - February 2025'] = (
        total_row['Total Ad Sales - February 2025'] / total_row['Spend - February 2025']
    )
    
    total_row['CTR - January 2025'] = (
        total_row['Clicks - January 2025'] / total_row['Impressions - January 2025']
    ) * 100
    total_row['CTR - February 2025'] = (
        total_row['Clicks - February 2025'] / total_row['Impressions - February 2025']
    ) * 100
    
    total_row['ACoS - January 2025'] = (
        total_row['Spend - January 2025'] / total_row['Total Ad Sales - January 2025']
    ) * 100
    total_row['ACoS - February 2025'] = (
        total_row['Spend - February 2025'] / total_row['Total Ad Sales - February 2025']
    ) * 100
    
    return df, total_row


def demonstrate_bridge_types():
    """Demonstrate each bridge type calculation."""
    # Create sample data
    campaign_data, total_row = create_sample_data()
    
    # Initialize orchestrator
    orchestrator = BridgeOrchestrator(precision=12)
    
    print("=" * 80)
    print("BRIDGE CALCULATOR ARCHITECTURE DEMONSTRATION")
    print("=" * 80)
    
    # Demonstrate each bridge type
    metrics_to_demo = [
        ("Spend", "Type 1: Traditional Mix Bridge"),
        ("ROAS", "Type 2: Standard MixRate Bridge"),
        ("ACoS", "Type 3: MixRate with Infinity Error")
    ]
    
    for metric, description in metrics_to_demo:
        print(f"\n{description}")
        print("-" * 40)
        
        # Get configuration
        config = get_bridge_configuration(metric)
        print(f"Metric: {metric}")
        print(f"Bridge Type: {config.bridge_type.name}")
        print(f"Contribution Unit: {config.contribution_unit.value}")
        if config.mix_determinant:
            print(f"Mix Determinant: {config.mix_determinant}")
        if config.inverse_metric:
            print(f"Inverse Metric: {config.inverse_metric}")
        
        # Calculate contributions
        results = orchestrator.calculate_metric(
            campaign_data=campaign_data,
            total_row=total_row,
            metric=metric
        )
        
        # Display results
        print(f"\nContributions:")
        for i, (campaign, contrib, formatted) in enumerate(zip(
            campaign_data['Campaign'],
            results['contributions'],
            results['formatted_contributions']
        )):
            print(f"  {campaign}: {formatted}")
        
        # Show metadata
        metadata = results['metadata']
        print(f"\nMetadata:")
        print(f"  Total Change: {metadata['total_change']:.2f}")
        print(f"  Total Contributions: {metadata['total_contributions']:.2f}")
        print(f"  Mathematical Consistency: {metadata['mathematical_consistency']}")


def demonstrate_batch_processing():
    """Demonstrate batch processing of multiple metrics."""
    print("\n" + "=" * 80)
    print("BATCH PROCESSING DEMONSTRATION")
    print("=" * 80)
    
    # Create sample data
    campaign_data, total_row = create_sample_data()
    
    # Initialize orchestrator
    orchestrator = BridgeOrchestrator()
    
    # Calculate all metrics at once
    all_results = orchestrator.calculate_all_metrics(
        campaign_data=campaign_data,
        total_row=total_row,
        metrics=["Spend", "Total Ad Sales", "ROAS", "CTR", "ACoS"]
    )
    
    # Display summary
    summary = all_results['summary']
    print(f"\nProcessing Summary:")
    print(f"  Total Metrics: {summary['total_metrics']}")
    print(f"  Successful: {summary['successful_calculations']}")
    print(f"  Failed: {summary['failed_calculations']}")
    print(f"  Success Rate: {summary['success_rate']:.1f}%")
    
    print(f"\nMetrics by Bridge Type:")
    for bridge_type, metrics in summary['metrics_by_type'].items():
        print(f"  {bridge_type}: {', '.join(metrics)}")
    
    print(f"\nConsistency Check:")
    for metric, status in summary['consistency_check'].items():
        print(f"  {metric}: {status}")


def demonstrate_validation():
    """Demonstrate validation capabilities."""
    print("\n" + "=" * 80)
    print("VALIDATION DEMONSTRATION")
    print("=" * 80)
    
    # Create sample data with intentional issue
    campaign_data, total_row = create_sample_data()
    
    # Create output dataframe structure
    output_df = campaign_data.copy()
    
    # Add contribution columns
    for metric in ["Spend", "ROAS", "ACoS"]:
        output_df[f"{metric} - Contribution"] = 0.0
    
    # Initialize orchestrator and apply calculations
    orchestrator = BridgeOrchestrator()
    output_df = orchestrator.apply_to_dataframe(
        output_df=output_df,
        total_row=total_row,
        metrics=["Spend", "ROAS", "ACoS"]
    )
    
    # Validate contributions
    validation_results = orchestrator.validate_all_contributions(
        output_df=output_df,
        total_row=total_row,
        tolerance=0.01
    )
    
    print("\nValidation Results:")
    for metric, is_valid in validation_results.items():
        status = "✓ PASS" if is_valid else "✗ FAIL"
        print(f"  {metric}: {status}")


if __name__ == "__main__":
    # Run demonstrations
    demonstrate_bridge_types()
    demonstrate_batch_processing()
    demonstrate_validation()
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)