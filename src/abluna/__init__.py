"""
Abluna Sky Maps - Automated Sky Map Generation System
====================================================

A comprehensive system for generating high-resolution star maps using Stellarium automation.

Main Components:
- StellariumController: Handles Stellarium API communication
- SkyMapGenerator: Main generation engine
- SkyMapMetadata: Metadata and image processing
- NASAValidator: Cross-validation with NASA data
"""

__version__ = "1.0.0"
__author__ = "Abluna Sky Maps"

from .stellarium_controller import StellariumController
from .sky_map_generator import SkyMapGenerator
from .data_models import Location, SkyMapConfig, GenerationStats
from .utils import load_locations_from_csv, load_config, setup_logging, create_sample_csv

__all__ = [
    'StellariumController',
    'SkyMapGenerator', 
    'Location',
    'SkyMapConfig',
    'GenerationStats',
    'load_locations_from_csv',
    'load_config',
    'setup_logging',
    'create_sample_csv'
]

__all__ = [
    'StellariumController',
    'SkyMapGenerator', 
    'Location',
    'SkyMapConfig',
    'GenerationStats'
]
