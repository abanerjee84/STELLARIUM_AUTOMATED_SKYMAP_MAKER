"""
Main Sky Map Generator for Abluna Sky Maps
"""

import os
import shutil
import glob
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from .data_models import Location, SkyMapConfig, GenerationStats
from .stellarium_controller import StellariumController
from .utils import load_config, ensure_output_directory

# Import metadata handler
try:
    from metadata_handler import SkyMapMetadata
    METADATA_AVAILABLE = True
except ImportError:
    METADATA_AVAILABLE = False

logger = logging.getLogger(__name__)

class SkyMapGenerator:
    """Main class for generating sky maps"""
    
    # Seasonal configurations
    SEASONAL_CONFIG = {
        "spring": {
            "date": "04-21",
            "milky_way": 0.3,
            "zodiacal": 0.2
        },
        "summer": {
            "date": "07-21", 
            "milky_way": 0.6,
            "zodiacal": 0.1
        },
        "autumn": {
            "date": "10-21",
            "milky_way": 0.4,
            "zodiacal": 0.2
        },
        "winter": {
            "date": "01-21",
            "milky_way": 0.2,
            "zodiacal": 0.1
        }
    }
    
    TIMES = ["21:00", "04:00"]  # 9 PM and 4 AM
    
    def __init__(self, output_dir: str = "output"):
        self.stellarium = StellariumController()
        self.output_dir = ensure_output_directory(output_dir)
        self.stats = GenerationStats()
        
        # Load configuration
        self.config = load_config()
        
        # Initialize metadata handler if available
        if METADATA_AVAILABLE:
            self.metadata_handler = SkyMapMetadata()
        else:
            self.metadata_handler = None

    def generate_filename(self, config: SkyMapConfig, sequence: int) -> str:
        """Generate filename according to ABL naming convention"""
        gen_date = datetime.now().strftime("%y%m%d")
        location_name = config.location.name.lower().replace(" ", "_").replace(",", "")
        country = config.location.country.lower().replace(" ", "_")
        
        # Convert time format
        hour = config.time.split(":")[0]
        time_suffix = "pm" if int(hour) >= 12 else "am"
        display_hour = str(int(hour) % 12) if int(hour) % 12 != 0 else "12"
        time_str = f"{display_hour}{time_suffix}"
        
        filename = f"ABL{gen_date}_{sequence:05d}_{location_name}_{country}_{config.date.replace('-', '_')}_{time_str}"
        return filename    
    
    def find_latest_screenshot(self, before_time: float) -> Optional[str]:
        """Find the most recent screenshot file (PNG or JPG format)"""
        username = os.getenv('USERNAME', 'User')
        
        search_locations = [
            f"C:/Users/{username}/Pictures/Stellarium",
            f"C:/Users/{username}/Pictures",
            f"C:/Users/{username}/Documents/Stellarium",
            f"C:/Users/{username}/AppData/Roaming/Stellarium",
            "./screenshots",
            "../screenshots",
            "./",  # Current directory
            "../"   # Parent directory
        ]
        
        newest_file = None
        newest_time = before_time
        
        for location in search_locations:
            if os.path.exists(location):
                try:
                    # Look for both PNG and JPG files
                    image_files = []
                    image_files.extend(glob.glob(os.path.join(location, "*.png")))
                    image_files.extend(glob.glob(os.path.join(location, "*.jpg")))
                    image_files.extend(glob.glob(os.path.join(location, "*.jpeg")))
                    
                    for image_file in image_files:
                        try:
                            file_time = os.path.getctime(image_file)
                            if file_time > newest_time:
                                newest_time = file_time
                                newest_file = image_file
                        except (OSError, PermissionError):
                            continue
                except (OSError, PermissionError):
                    continue
        
        if newest_file:
            logger.debug(f"Found screenshot: {newest_file}")
        else:
            logger.debug(f"No screenshots found newer than {before_time}")
            # List all search locations for debugging
            for location in search_locations:
                if os.path.exists(location):
                    try:
                        files = os.listdir(location)
                        logger.debug(f"Location {location} contains: {files[:10]}")  # First 10 files
                    except:
                        pass
        
        return newest_file

    def save_screenshot(self, config: SkyMapConfig, sequence: int) -> Optional[str]:
        """Capture and save screenshot with proper naming and metadata"""
        before_time = time.time()
        
        # Take screenshot
        if not self.stellarium.take_screenshot():
            logger.error("Failed to trigger screenshot")
            return None
            
        # Wait for file creation
        screenshot_wait = self.config.get("stellarium", {}).get("screenshot_wait_time", 5)
        time.sleep(screenshot_wait)
        
        # Find the new screenshot
        screenshot_file = self.find_latest_screenshot(before_time)
        if not screenshot_file:
            logger.error("Could not find new screenshot file")
            return None
              # Generate proper filename and copy
        filename = self.generate_filename(config, sequence)
        output_path = self.output_dir / f"{filename}.jpg"
        
        try:
            shutil.copy2(screenshot_file, output_path)
            logger.info(f"Screenshot saved: {output_path}")
              # Add metadata if handler is available
            if self.metadata_handler:
                visible_objects = self.stellarium.get_visible_objects()
                metadata = self.metadata_handler.prepare_metadata_dict(config, visible_objects)
                
                # Add IPTC metadata
                self.metadata_handler.add_iptc_metadata(str(output_path), metadata)
                
                # Create bordered version if configured
                if self.config.get("metadata", {}).get("include_border", False):
                    bordered_path = self.output_dir / f"{filename}_bordered.jpg"
                    self.metadata_handler.create_bordered_image(
                        str(output_path), metadata, str(bordered_path)
                    )
            
            return str(output_path)
        except Exception as e:
            logger.error(f"Error copying screenshot: {e}")
            return None

    def generate_single_map(self, config: SkyMapConfig, sequence: int) -> bool:
        """Generate a single sky map with full specification compliance"""
        logger.info(f"Generating map {sequence}: {config.location.name} - {config.season} {config.date} {config.time}")
        
        # Set high-resolution image first using config values
        resolution_config = self.config.get("output", {}).get("resolution", {})
        width = resolution_config.get("width", 7680)
        height = resolution_config.get("height", 4320)
        
        if not self.stellarium.set_image_resolution(width, height):
            logger.warning(f"Failed to set resolution to {width}x{height}, continuing with default")
            
        # Set location
        if not self.stellarium.set_location(config.location):
            logger.error(f"Failed to set location for {config.location.name}")
            return False
            
        # Set time
        if not self.stellarium.set_time(config.date, config.time, config.year):
            logger.error(f"Failed to set time to {config.date} {config.time}")
            return False
            
        # Configure sky settings according to specification
        if not self.stellarium.configure_sky_settings(config):
            logger.error("Failed to configure sky settings")
            return False
            
        # Wait for Stellarium to update and stabilize
        batch_delay = self.config.get("generation", {}).get("batch_delay", 3)
        logger.debug(f"Waiting {batch_delay} seconds for Stellarium to update...")
        time.sleep(batch_delay)
        
        # Take screenshot
        screenshot_path = self.save_screenshot(config, sequence)
        
        if screenshot_path:
            logger.info(f"Successfully generated map {sequence}: {screenshot_path}")
            return True
        else:
            logger.error(f"Failed to save screenshot for map {sequence}")
            return False

    def generate_maps_for_location(self, location: Location, seasons: List[str] = None, 
                                 times: List[str] = None, start_sequence: int = 1, year: int = None) -> int:
        """Generate all maps for a single location"""
        if seasons is None:
            seasons = list(self.SEASONAL_CONFIG.keys())
        if times is None:
            times = self.TIMES
        if year is None:
            year = self.config.get("generation", {}).get("default_year", 2025)
            
        sequence = start_sequence
        successful_count = 0
        
        for season in seasons:
            season_config = self.SEASONAL_CONFIG[season]
            
            for time_str in times:
                config = SkyMapConfig(
                    location=location,
                    date=season_config["date"],
                    time=time_str,
                    season=season,
                    year=year,
                    milky_way_brightness=season_config["milky_way"],
                    zodiacal_light=season_config["zodiacal"],
                    field_of_view=self.config.get("sky_settings", {}).get("field_of_view", 180.0),
                    initial_azimuth=self.config.get("sky_settings", {}).get("initial_azimuth", 180.0),
                    initial_altitude=self.config.get("sky_settings", {}).get("initial_altitude", 30.0)
                )
                
                if self.generate_single_map(config, sequence):
                    successful_count += 1
                    self.stats.successful_maps += 1
                else:
                    self.stats.failed_maps += 1
                    
                sequence += 1
                self.stats.total_maps += 1
                
        return successful_count

    def batch_generate(self, locations: List[Location], seasons: List[str] = None, 
                      times: List[str] = None, year: int = None) -> GenerationStats:
        """Generate sky maps for multiple locations"""
        self.stats = GenerationStats()
        self.stats.start_time = datetime.now()
        self.stats.total_locations = len(locations)
        
        if year is None:
            year = self.config.get("generation", {}).get("default_year", 2025)
        
        # Check Stellarium connection
        if not self.stellarium.check_connection():
            logger.error("Cannot connect to Stellarium. Please ensure it's running with Remote Control enabled.")
            return self.stats
            
        logger.info(f"Starting batch generation for {len(locations)} locations")
        
        sequence = 1
        for i, location in enumerate(locations, 1):
            logger.info(f"Processing location {i}/{len(locations)}: {location.name}")
            
            successful = self.generate_maps_for_location(location, seasons, times, sequence, year)
            
            # Update sequence counter
            maps_per_location = len(seasons or self.SEASONAL_CONFIG) * len(times or self.TIMES)
            sequence += maps_per_location
            
            logger.info(f"Completed {location.name}: {successful}/{maps_per_location} maps successful")
            
        self.stats.end_time = datetime.now()
        
        # Log final statistics
        duration = self.stats.end_time - self.stats.start_time
        logger.info(f"Batch generation completed in {duration}")
        logger.info(f"Total maps: {self.stats.total_maps}")
        logger.info(f"Successful: {self.stats.successful_maps}")
        logger.info(f"Failed: {self.stats.failed_maps}")
        
        return self.stats
