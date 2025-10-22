#!/usr/bin/env python3
"""
Script để trích xuất tọa độ cho toàn bộ dataset
"""

import sys
import os

# Add tools directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

from extract_coordinates import CoordinateExtractor

def extract_all_coordinates():
    """
    Trích xuất tọa độ cho toàn bộ dataset
    """
    print("Starting coordinate extraction for all records...")
    print("This may take several minutes...")
    
    # Initialize extractor
    csv_file = "Phuong_TPHCM_Formatted.CSV"
    output_file = "Phuong_TPHCM_With_Coordinates.CSV"
    extractor = CoordinateExtractor(csv_file, output_file)
    
    # Set delay to 1.5 seconds to be safe with API limits
    extractor.delay = 1.5
    
    try:
        # Extract coordinates
        stats = extractor.extract_coordinates(dry_run=False)
        
        print("\nExtraction completed!")
        print(f"Total records: {stats['total']}")
        print(f"Processed: {stats['processed']}")
        print(f"Found coordinates: {stats['found']}")
        print(f"Not found: {stats['not_found']}")
        print(f"Errors: {stats['errors']}")
        
        success_rate = (stats['found'] / stats['processed']) * 100 if stats['processed'] > 0 else 0
        print(f"Success rate: {success_rate:.1f}%")
        
    except KeyboardInterrupt:
        print("\nExtraction stopped by user")
    except Exception as e:
        print(f"Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_all_coordinates()
