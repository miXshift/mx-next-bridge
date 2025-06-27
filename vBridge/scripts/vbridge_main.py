"""
Streamlined VBridge Main

This module now serves as a simple wrapper around StreamlinedVBridgeProcessor.
The complex 4-step orchestration has been replaced with a single-pass processor.

Legacy VBridge class (238 lines) has been moved to legacy_backup/ folder.
"""

from streamlined_vbridge import StreamlinedVBridgeProcessor


class VBridge:
    """
    Simplified VBridge class that wraps StreamlinedVBridgeProcessor
    
    Maintained for backward compatibility with existing code that imports VBridge.
    """
    
    def __init__(self, output_dir: str = 'output', output_format: str = 'excel'):
        """
        Initialize VBridge with streamlined processor
        
        Args:
            output_dir: Directory to save output files
            output_format: Ignored - streamlined processor only generates Excel format
        """
        if output_format != 'excel':
            print(f"⚠️  Warning: output_format '{output_format}' ignored. Streamlined processor only generates Excel format.")
        
        self.processor = StreamlinedVBridgeProcessor(output_dir=output_dir)
        self.output_dir = output_dir
    
    def run_complete_analysis(self, csv_file_path: str, p1_start_date: str, p1_end_date: str,
                            p2_start_date: str, p2_end_date: str) -> dict:
        """
        Run the complete analysis using streamlined processor
        
        Args:
            csv_file_path: Path to the CSV data file
            p1_start_date: Start date for Period 1 (YYYY-MM-DD format)
            p1_end_date: End date for Period 1 (YYYY-MM-DD format)
            p2_start_date: Start date for Period 2 (YYYY-MM-DD format)
            p2_end_date: End date for Period 2 (YYYY-MM-DD format)
            
        Returns:
            Dictionary with the output file path
        """
        output_file = self.processor.process_complete_analysis(
            csv_file_path, p1_start_date, p1_end_date, p2_start_date, p2_end_date
        )
        
        return {
            'output_file': output_file,
            'message': 'Analysis completed using streamlined processor'
        }


# Example usage (maintained for compatibility)
if __name__ == '__main__':
    # Use streamlined processor directly for better performance
    processor = StreamlinedVBridgeProcessor(output_dir='output')
    
    csv_file_path = 'Hydrapak YTD - campaign.csv'
    p1_start_date = '2025-01-01'
    p1_end_date = '2025-01-31'
    p2_start_date = '2025-02-01'
    p2_end_date = '2025-02-28'
    
    output_file = processor.process_complete_analysis(
        csv_file_path, p1_start_date, p1_end_date, p2_start_date, p2_end_date
    )