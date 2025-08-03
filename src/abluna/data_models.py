"""
Data models for Abluna Sky Maps
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Location:
    """Location data structure"""
    name: str
    country: str
    latitude: float
    longitude: float
    region: str = ""
    altitude: float = 0.0

@dataclass
class SkyMapConfig:
    """Configuration for a single sky map"""
    location: Location
    date: str  # Format: "MM-DD"
    time: str  # Format: "HH:MM" (24-hour)
    season: str
    year: int
    constellation_lines: bool = True
    constellation_labels: bool = True
    milky_way_brightness: float = 0.4
    zodiacal_light: float = 0.1
    projection: str = "stereographic"  # or "orthographic"
    field_of_view: float = 180.0
    initial_azimuth: float = 180.0  # South
    initial_altitude: float = 30.0

@dataclass
class GenerationStats:
    """Statistics for batch generation"""
    total_locations: int = 0
    total_maps: int = 0
    successful_maps: int = 0
    failed_maps: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
