#!/usr/bin/env python3
"""
Abluna Sky Maps - Main Entry Point
Automated Stellarium Sky Map Generator
"""

import argparse
import logging
from src.abluna import (
    SkyMapGenerator, 
    StellariumController, 
    setup_logging, 
    create_sample_csv,
    load_locations_from_csv
)

# Setup logging
setup_logging()

def create_sample():
    """Create a sample CSV file for testing"""
    create_sample_csv()  # Use utility function
    print("Created sample_locations.csv")

def main():
    parser = argparse.ArgumentParser(description="Abluna Sky Map Generator")
    parser.add_argument("--csv", help="CSV file with locations")
    parser.add_argument("--output", default="output", help="Output directory")
    parser.add_argument("--seasons", nargs="+", choices=["spring", "summer", "autumn", "winter"], 
                       help="Seasons to generate (default: all)")
    parser.add_argument("--times", nargs="+", help="Times to generate (HH:MM format)")
    parser.add_argument("--year", type=int, help="Year for sky map generation (default: from config)")
    parser.add_argument("--create-sample", action="store_true", help="Create sample CSV file")
    parser.add_argument("--test-connection", action="store_true", help="Test Stellarium connection")
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample()
        return
        
    if args.test_connection:
        controller = StellariumController()
        if controller.check_connection():
            print("✓ Stellarium connection successful")
        else:
            print("✗ Cannot connect to Stellarium")
        return
    
    if not args.csv:
        print("Please provide a CSV file with --csv or use --create-sample to create a sample file")
        return
        
    # Initialize generator
    generator = SkyMapGenerator(args.output)
    
    # Load locations
    locations = load_locations_from_csv(args.csv)
    if not locations:
        print("No locations loaded from CSV file")
        return
        
    # Generate maps
    stats = generator.batch_generate(locations, args.seasons, args.times, args.year)
    
    print(f"\nGeneration completed:")
    print(f"Total maps: {stats.total_maps}")
    print(f"Successful: {stats.successful_maps}")
    print(f"Failed: {stats.failed_maps}")
    
    if stats.start_time and stats.end_time:
        duration = stats.end_time - stats.start_time
        print(f"Duration: {duration}")

if __name__ == "__main__":
    main()
