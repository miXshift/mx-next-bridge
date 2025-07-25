#!/usr/bin/env python3
"""
Campaign Bridge Analysis Tool - Modular Version
Replicates the campaign tab of the Excel bridge report using CSV source data
"""

import warnings

try:
    from ..data.processor import OptimizedDataProcessor as DataProcessor
    from .bridge_calculator import BridgeCalculator
    from ..output.formatter import OutputFormatter
except ImportError:
    # Backwards compatibility fallback
    try:
        from .data_processor import DataProcessor
        from .bridge_calculator import BridgeCalculator
        from .output_formatter import OutputFormatter
    except ImportError:
        from data_processor import DataProcessor
        from bridge_calculator import BridgeCalculator
        from output_formatter import OutputFormatter

warnings.filterwarnings('ignore')


class CampaignBridge:
    """Main campaign bridge analysis class using modular components"""
    
    def __init__(self, csv_path):
        """Initialize with path to source CSV data"""
        self.csv_path = csv_path
        self.data_processor = DataProcessor(csv_path)
        self.bridge_data = None
        
    def load_data(self):
        """Load and filter the source CSV data"""
        return self.data_processor.load_data()
        
    def calculate_bridge(self, validate=True):
        """
        Calculate the bridge between January and February data with delta assignment zero baseline handling
        
        Args:
            validate: Enable validation checks
            
        Returns:
            DataFrame with calculated bridge metrics
        """
        print("\nAggregating January data...")
        jan_data, feb_data = self.data_processor.load_data()
        jan_agg = self.data_processor.aggregate_period_data(jan_data)
        
        print("Aggregating February data...")
        feb_agg = self.data_processor.aggregate_period_data(feb_data)
        
        # Get all unique campaigns from both periods
        all_campaigns = self.data_processor.get_all_campaigns(jan_agg, feb_agg)
        
        # Merge data for both periods
        bridge_data = self.data_processor.merge_period_data(all_campaigns, jan_agg, feb_agg)
        
        # Calculate bridge metrics with delta assignment zero baseline handling
        print("Calculating bridge metrics using delta assignment strategy...")
        self.bridge_data = BridgeCalculator.calculate_bridge(bridge_data, validate)
        
        # Store strategy for saving
        self.last_strategy = 'delta_assignment'
        
        return self.bridge_data
    
    def save_to_csv(self, output_path=None, use_enhanced_naming=True):
        """
        Save the bridge data to CSV format with enhanced naming and metadata
        
        Args:
            output_path: Optional explicit output path (for backward compatibility)
            use_enhanced_naming: Use enhanced semantic naming system
        """
        if self.bridge_data is None:
            raise ValueError("No bridge data to save. Run calculate_bridge() first.")
        
        # Use enhanced naming if available and enabled
        if use_enhanced_naming and output_path is None:
            try:
                # Use delta assignment strategy
                result = BridgeCalculator.save_bridge_analysis(
                    result_df=self.bridge_data,
                    periods={'p1': 'jan2025', 'p2': 'feb2025'},
                    metadata={'data_source': self.csv_path}
                )
                
                # Handle different return formats (new vs legacy)
                if len(result) == 3:
                    latest_path, timestamped_path, previous_path = result
                    return latest_path, None  # Return latest file as CSV path, None as meta
                else:
                    csv_path, meta_path = result
                    return csv_path, meta_path
                
            except ImportError:
                # Fallback to traditional naming
                output_path = output_path or 'output/period_comparison.csv'
                OutputFormatter.save_to_csv(self.bridge_data, output_path)
                return output_path, None
        else:
            # Traditional save method
            output_path = output_path or 'output/period_comparison.csv'
            OutputFormatter.save_to_csv(self.bridge_data, output_path)
            return output_path, None


def main():
    """Main execution function with enhanced zero baseline handling"""
    import sys
    
    # Use delta assignment strategy for maximum accuracy
    validate = True
        
    if '--no-validate' in sys.argv:
        validate = False
    
    print("Using zero baseline strategy: delta_assignment")
    print(f"Validation enabled: {validate}")
    
    # Initialize the bridge calculator
    bridge = CampaignBridge('data/Hydrapak YTD - campaign.csv')
    
    # Load and process data
    bridge.load_data()
    
    # Calculate bridge with delta assignment handling
    print("\nCalculating bridge metrics...")
    bridge_df = bridge.calculate_bridge(validate=validate)
    
    # Save to CSV with enhanced naming
    print("\nSaving analysis results...")
    csv_path, meta_path = bridge.save_to_csv()
    
    print(f"\nTotal campaigns analyzed: {len(bridge_df) - 1}")
    print("Bridge calculation complete!")
    print(f"Results saved to: {csv_path}")
    if meta_path:
        print(f"Metadata saved to: {meta_path}")
    
    # Print calculation summary if enhanced calculator is available
    try:
        from enhanced_mixbridge_calculator import EnhancedMixBridgeCalculator
        from mixbridge_config import get_config
        
        config = get_config()
        calculator = EnhancedMixBridgeCalculator()
        
        # Generate summary for the first few rows (excluding total row)
        campaign_data = bridge_df.iloc[1:6] if len(bridge_df) > 1 else bridge_df
        summary = calculator.get_calculation_summary(campaign_data, bridge_df.iloc[0:1])
        
        print(f"\nCalculation Summary:")
        print(f"Strategy used: {summary['strategy_used']}")
        print(f"Zero baseline campaigns found:")
        for metric, count in summary['zero_baseline_campaigns'].items():
            if count > 0:
                print(f"  {metric}: {count} campaigns")
                
    except ImportError:
        print("Enhanced summary not available - using basic calculation")


if __name__ == "__main__":
    main()