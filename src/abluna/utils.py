"""
Utility functions for Abluna Sky Maps
"""

import os
import csv
import json
import logging
from pathlib import Path
from typing import List, Dict
from .data_models import Location

logger = logging.getLogger(__name__)

def load_locations_from_csv(csv_file: str) -> List[Location]:
    """Load locations from CSV file"""
    locations = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                location = Location(
                    name=row['name'],
                    country=row['country'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    region=row.get('region', ''),
                    altitude=float(row.get('altitude', 0))
                )
                locations.append(location)
                
    except Exception as e:
        logger.error(f"Error loading CSV file {csv_file}: {e}")
        return []
        
    logger.info(f"Loaded {len(locations)} locations from {csv_file}")
    return locations

def load_config(config_file: str = "config.json") -> Dict:
    """Load configuration from JSON file"""
    try:
        with open(config_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.warning(f"{config_file} not found, using defaults")
        return {}
    except Exception as e:
        logger.error(f"Error loading {config_file}: {e}")
        return {}

def setup_logging(log_file: str = "abluna_skymap.log", level: int = logging.INFO):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def create_sample_csv(filename: str = "sample_locations.csv"):
    """Create a sample CSV file for testing"""
    sample_data = [
        {"name": "New York", "country": "USA", "latitude": 40.7128, "longitude": -74.0060, "region": "New York", "altitude": 10},
        {"name": "London", "country": "UK", "latitude": 51.5074, "longitude": -0.1278, "region": "England", "altitude": 35},
        {"name": "Tokyo", "country": "Japan", "latitude": 35.6762, "longitude": 139.6503, "region": "Kanto", "altitude": 40},
        {"name": "Sydney", "country": "Australia", "latitude": -33.8688, "longitude": 151.2093, "region": "NSW", "altitude": 58},
        {"name": "Chicago", "country": "USA", "latitude": 41.8819, "longitude": -87.6278, "region": "Illinois", "altitude": 181},
        {"name": "Paris", "country": "France", "latitude": 48.8566, "longitude": 2.3522, "region": "Île-de-France", "altitude": 35},
        {"name": "Berlin", "country": "Germany", "latitude": 52.5200, "longitude": 13.4050, "region": "Berlin", "altitude": 34},
        {"name": "Moscow", "country": "Russia", "latitude": 55.7558, "longitude": 37.6176, "region": "Moscow", "altitude": 156},
        {"name": "Toronto", "country": "Canada", "latitude": 43.6532, "longitude": -79.3832, "region": "Ontario", "altitude": 76}
    ]
    
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "country", "latitude", "longitude", "region", "altitude"])
        writer.writeheader()
        writer.writerows(sample_data)
    
    logger.info(f"Created {filename} with {len(sample_data)} sample locations")

def ensure_output_directory(output_dir: str) -> Path:
    """Ensure output directory exists and return Path object"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    return output_path

def format_duration(start_time, end_time) -> str:
    """Format duration between two datetime objects"""
    if not start_time or not end_time:
        return "Unknown"
    
    duration = end_time - start_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"
