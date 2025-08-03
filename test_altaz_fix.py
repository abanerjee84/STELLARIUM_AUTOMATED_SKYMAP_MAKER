#!/usr/bin/env python3
"""
Test script to verify the altAz JSON format fix
"""

import logging
from src.abluna.stellarium_controller import StellariumController

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_altaz_fix():
    """Test the altAz JSON format fix"""
    controller = StellariumController()
    
    # Test connection first
    logger.info("Testing Stellarium connection...")
    if not controller.check_connection():
        logger.error("Cannot connect to Stellarium. Make sure it's running with Remote Control plugin enabled.")
        return False
    
    logger.info("✓ Connected to Stellarium")
    
    # Test the viewing direction setting with the JSON fix
    logger.info("Testing viewing direction setting with JSON format...")
    result = controller._set_viewing_direction(azimuth=180.0, altitude=30.0)
    
    if result:
        logger.info("✓ Viewing direction set successfully using JSON format")
        return True
    else:
        logger.error("✗ Failed to set viewing direction")
        return False

if __name__ == "__main__":
    test_altaz_fix()
