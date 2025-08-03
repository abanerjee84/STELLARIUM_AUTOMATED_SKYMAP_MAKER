"""
Stellarium Remote Control API Interface for Abluna Sky Maps
"""

import requests
import logging
from typing import Dict, List, Optional
from .data_models import Location, SkyMapConfig

logger = logging.getLogger(__name__)

class StellariumController:
    """Handles communication with Stellarium Remote Control API"""
    
    def __init__(self, base_url: str = "http://localhost:8090"):
        self.base_url = base_url
        
    def send_command(self, endpoint: str, params: Optional[Dict] = None, method: str = "GET") -> Optional[Dict]:
        """Send a command to Stellarium Remote Control API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, data=params, timeout=10)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None

            response.raise_for_status()
            
            try:
                return response.json()
            except ValueError:
                return {"text": response.text}
                
        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to Stellarium at {url}")
            logger.error("Ensure Stellarium is running and Remote Control plugin is enabled")
            return None
        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error with {endpoint}: {e}")
            return None

    def check_connection(self) -> bool:
        """Check if Stellarium is accessible"""
        result = self.send_command("/api/main/status")
        return result is not None

    def set_location(self, location: Location) -> bool:
        """Set Stellarium location"""
        params = {
            "latitude": str(location.latitude),
            "longitude": str(location.longitude),
            "altitude": str(location.altitude),
            "name": location.name
        }
          # Try different endpoints
        for endpoint in ["/api/location/setlocationfields", "/api/location/setlocation"]:
            result = self.send_command(endpoint, params, "POST")
            if result:
                logger.info(f"Location set to {location.name}, {location.country}")
                return True
                
        logger.error(f"Failed to set location to {location.name}")
        return False

    def set_time(self, date_str: str, time_str: str, year: int) -> bool: # Removed default year
        """Set Stellarium date and time"""
        # Convert to ISO format that Stellarium expects
        month, day = date_str.split("-")
        hour, minute = time_str.split(":")
        
        # Create ISO datetime string (fixed indentation)
        iso_time = f"{year}-{month.zfill(2)}-{day.zfill(2)}T{hour.zfill(2)}:{minute.zfill(2)}:00"
        
        params = {"time": iso_time}
        result = self.send_command("/api/main/time", params, "POST")
        
        if result:
            logger.info(f"Time set to {iso_time} (from {date_str} {time_str})")
            return True
        else:
            logger.error(f"Failed to set time to {date_str} {time_str} (ISO: {iso_time})")
            # Try alternative time setting methods
            return self._try_alternative_time_methods(iso_time, date_str, time_str)
    
    def _try_alternative_time_methods(self, iso_time: str, date_str: str, time_str: str) -> bool:
        """Try alternative methods to set time in Stellarium"""
        alternative_methods = [
            ("/api/main/time", {"time": iso_time, "utc": "false"}),
            ("/api/main/time", {"time": iso_time, "format": "iso"}),
            ("/api/stelaction/do", {"id": "actionSet_Time_To_Now"}),  # Fallback to current time
        ]
        
        for endpoint, params in alternative_methods:
            result = self.send_command(endpoint, params, "POST")
            if result:
                logger.info(f"Time set using alternative method: {endpoint}")
                return True
        
        logger.error(f"All time setting methods failed for {date_str} {time_str}")
        return False

    def verify_time_setting(self, expected_iso_time: str) -> bool:
        """Verify that Stellarium time was set correctly"""
        try:
            result = self.send_command("/api/main/status")
            if result and 'time' in result:
                current_time = result['time']
                logger.info(f"Stellarium current time: {current_time}")
                logger.info(f"Expected time: {expected_iso_time}")
                return True
            else:
                # Try alternative status endpoint
                result = self.send_command("/api/main/time")
                if result:
                    logger.info(f"Time verification result: {result}")
                    return True
        except Exception as e:
            logger.warning(f"Could not verify time setting: {e}")
        
        return False

    def configure_sky_settings(self, config: SkyMapConfig) -> bool:
        """Configure Stellarium sky display settings according to project specification"""
        settings = [
            # Sky Culture - Set to Modern (as per specification)
            ("/api/stelproperty/set", {"id": "StelCore.currentSkyculture", "value": "modern"}),
            
            # Constellation Settings
            ("/api/stelproperty/set", {"id": "ConstellationMgr.linesDisplayed", "value": str(config.constellation_lines).lower()}),
            ("/api/stelproperty/set", {"id": "ConstellationMgr.namesDisplayed", "value": str(config.constellation_labels).lower()}),
            ("/api/stelproperty/set", {"id": "ConstellationMgr.artDisplayed", "value": "false"}),
            
            # Sky Display Settings
            ("/api/stelproperty/set", {"id": "LandscapeMgr.atmosphereDisplayed", "value": "false"}),
            ("/api/stelproperty/set", {"id": "LandscapeMgr.landscapeDisplayed", "value": "false"}),
            ("/api/stelproperty/set", {"id": "GridLinesMgr.cardinalPointsDisplayed", "value": "true"}),
            
            # Celestial Objects
            ("/api/stelproperty/set", {"id": "SolarSystem.planetsDisplayed", "value": "true"}),
            ("/api/stelproperty/set", {"id": "SolarSystem.moonDisplayed", "value": "true"}),
            ("/api/stelproperty/set", {"id": "StarMgr.starsDisplayed", "value": "true"}),
            
            # Milky Way Settings (brightness varies by season)
            ("/api/stelproperty/set", {"id": "MilkyWay.displayed", "value": "true"}),
            ("/api/stelproperty/set", {"id": "MilkyWay.intensity", "value": str(config.milky_way_brightness)}),
            
            # Zodiacal Light Settings (optional, varies by season)
            ("/api/stelproperty/set", {"id": "ZodiacalLight.displayed", "value": "true"}),
            ("/api/stelproperty/set", {"id": "ZodiacalLight.intensity", "value": str(config.zodiacal_light)}),
            
            # Projection Settings - Stereographic (default) as per specification
            ("/api/stelproperty/set", {"id": "StelCore.currentProjectionType", "value": config.projection}),
            
            # Additional Display Settings for clean maps
            ("/api/stelproperty/set", {"id": "StelGui.visible", "value": "false"}),
            ("/api/stelproperty/set", {"id": "StelGui.guiVisible", "value": "false"}),
            
            # Time/Date display off for clean maps
            ("/api/stelproperty/set", {"id": "LabelMgr.dateTimeDisplayed", "value": "false"}),            # Ensure high-quality rendering
            ("/api/stelproperty/set", {"id": "StelCore.usePixelShader", "value": "true"}),
        ]
        
        success = True
        for endpoint, params in settings:
            result = self.send_command(endpoint, params, "POST")
            if not result:
                logger.warning(f"Failed to set property: {params}")
                # Don't fail completely for individual property failures
            else:
                logger.debug(f"Set property: {params}")
        
        # Set projection specifically if the config includes it
        if hasattr(config, 'projection') and config.projection:
            if not self._set_projection(config.projection):
                success = False
        
        # Set field of view and viewing direction
        if hasattr(config, 'field_of_view'):
            if not self._set_field_of_view(config.field_of_view):
                success = False
        
        if hasattr(config, 'initial_azimuth') and hasattr(config, 'initial_altitude'):
            if not self._set_viewing_direction(config.initial_azimuth, config.initial_altitude):
                success = False
        
        # Return True even if some settings failed, as long as core settings succeeded
        return True

    def _set_field_of_view(self, fov_degrees: float) -> bool:
        """Set Stellarium field of view"""
        params = {"id": "StelMovementMgr.currentFov", "value": str(fov_degrees)}
        result = self.send_command("/api/stelproperty/set", params, "POST")
        
        if result:
            logger.info(f"Field of view set to {fov_degrees} degrees")
            return True
        else:
            logger.warning(f"Failed to set field of view to {fov_degrees} degrees")
            return False

    def _set_viewing_direction(self, azimuth: float, altitude: float) -> bool:
        """Set Stellarium viewing direction using azimuth and altitude"""
        # Try multiple approaches for setting viewing direction
        approaches = [
            # Approach 1: Use main/view with proper JSON array format
            ("/api/main/view", {"altAz": [altitude, azimuth, 0]}),
            # Approach 2: Use stelproperty to set view direction
            ("/api/stelproperty/set", {"id": "StelMovementMgr.viewDirectionJ2000", 
                                       "value": f"[{azimuth},{altitude}]"}),
            # Approach 3: Use action to point to specific direction
            ("/api/stelaction/do", {"id": "actionGoto_Selected_Object"}),
        ]
          for endpoint, params in approaches:
            result = self.send_command(endpoint, params, "POST")
            if result:
                logger.info(f"Viewing direction set to azimuth={azimuth}, altitude={altitude} using {endpoint}")
                return True
            else:
                logger.debug(f"Failed to set viewing direction using {endpoint}")
        
        logger.warning(f"Failed to set viewing direction to azimuth={azimuth}, altitude={altitude}")
        return False

    def set_image_resolution(self, width: int = None, height: int = None) -> bool:
        """Set Stellarium screenshot resolution with fallback options"""
        from .utils import load_config
        
        # Use config values if not provided
        if width is None or height is None:
            config = load_config()
            resolution = config.get("output", {}).get("resolution", {})
            width = resolution.get("width", 7680)  # 4K UHD width
            height = resolution.get("height", 4320)  # 4K UHD height
        
        logger.info(f"Attempting to set resolution to {width}x{height}")
        
        # Multiple approaches for setting resolution
        resolution_methods = [
            # Method 1: Standard screenshot properties
            [
                ("/api/stelproperty/set", {"id": "MainView.screenShotWidth", "value": str(width)}),
                ("/api/stelproperty/set", {"id": "MainView.screenShotHeight", "value": str(height)}),
                ("/api/stelproperty/set", {"id": "MainView.screenShotFormat", "value": "jpg"}),
            ],
            # Method 2: Alternative screenshot properties
            [
                ("/api/stelproperty/set", {"id": "StelMainView.screenShotWidth", "value": str(width)}),
                ("/api/stelproperty/set", {"id": "StelMainView.screenShotHeight", "value": str(height)}),
            ],
            # Method 3: Core screenshot settings
            [
                ("/api/stelproperty/set", {"id": "StelCore.screenShotWidth", "value": str(width)}),
                ("/api/stelproperty/set", {"id": "StelCore.screenShotHeight", "value": str(height)}),
            ],
            # Method 4: Main view dimensions
            [
                ("/api/stelproperty/set", {"id": "MainView.width", "value": str(width)}),
                ("/api/stelproperty/set", {"id": "MainView.height", "value": str(height)}),
            ],
        ]
        
        success = False
        for method_idx, settings in enumerate(resolution_methods, 1):
            logger.debug(f"Trying resolution method {method_idx}")
            method_success = True
            
            for endpoint, params in settings:
                result = self.send_command(endpoint, params, "POST")
                if not result:
                    logger.debug(f"Failed property in method {method_idx}: {params}")
                    method_success = False
                else:
                    logger.debug(f"Set property: {params}")
            
            if method_success:
                logger.info(f"Resolution set successfully using method {method_idx}")
                success = True
                break
        
        # Also try to set window size as fallback
        window_params = {"width": str(width), "height": str(height)}
        window_result = self.send_command("/api/main/view", window_params, "POST")
        if window_result:
            logger.debug("Set window size via main/view")
            success = True
        
        if success:
            logger.info(f"Resolution configured for {width}x{height}")
        else:
            logger.warning(f"Could not set resolution to {width}x{height} - using Stellarium default")
            logger.info("Note: You may need to manually set Stellarium window size and screenshot resolution")
        
        return success

    def _set_projection(self, projection: str) -> bool:
        """Set Stellarium projection type"""
        # Map our projection names to Stellarium values
        projection_map = {
            "stereographic": "ProjectionStereographic",
            "orthographic": "ProjectionOrthographic", 
            "perspective": "ProjectionPerspective",
            "hammer": "ProjectionHammer"
        }
        stellarium_projection = projection_map.get(projection.lower(), "ProjectionStereographic")
        
        params = {"id": "StelCore.currentProjectionType", "value": stellarium_projection}
        result = self.send_command("/api/stelproperty/set", params, "POST")
        
        if result:
            logger.info(f"Projection set to {projection} ({stellarium_projection})")
            return True
        else:
            logger.error(f"Failed to set projection to {projection}")
            return False

    def take_screenshot(self) -> bool:
        """Trigger Stellarium screenshot with multiple API attempts"""
        # Try multiple screenshot API endpoints
        screenshot_apis = [
            ("/api/stelaction/do", {"id": "actionSave_Screenshot_Global"}),
            ("/api/main/screenshot", {}),
            ("/api/screenshots/screenshot", {}),
            ("/api/stelaction/do", {"id": "actionScreenshot"}),
        ]
        
        for endpoint, params in screenshot_apis:
            result = self.send_command(endpoint, params, "POST")
            if result:
                logger.debug(f"Screenshot triggered via {endpoint}")
                return True
            else:
                logger.debug(f"Screenshot attempt failed via {endpoint}")
        
        logger.error("All screenshot API attempts failed")
        return False

    def get_visible_objects(self) -> List[str]:
        """Get list of visible celestial objects"""
        # This would require additional API calls to get object information
        # For now, return a placeholder - would need to be implemented based on
        # Stellarium's specific API for object queries
        return ["Placeholder - implement object detection"]
