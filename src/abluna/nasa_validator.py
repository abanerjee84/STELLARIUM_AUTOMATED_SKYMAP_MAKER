"""
NASA Validation Module for Abluna Sky Maps
Cross-references generated sky maps with NASA JPL Horizons data
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CelestialObject:
    """Represents a celestial object with position data"""
    name: str
    ra: float  # Right ascension in degrees
    dec: float  # Declination in degrees
    alt: float  # Altitude in degrees
    az: float  # Azimuth in degrees
    magnitude: Optional[float] = None
    distance: Optional[float] = None

class NASAValidator:
    """Validates sky map accuracy using NASA JPL Horizons API"""
    
    # JPL Horizons API endpoint
    HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
    
    # Major planet IDs for Horizons
    PLANET_IDS = {
        "mercury": "199",
        "venus": "299", 
        "mars": "499",
        "jupiter": "599",
        "saturn": "699",
        "uranus": "799",
        "neptune": "899",
        "moon": "301"
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Abluna-SkyMap-Validator/1.0'
        })
    
    def get_planet_position(self, planet: str, location: Tuple[float, float], 
                          datetime_str: str) -> Optional[CelestialObject]:
        """Get planet position from JPL Horizons"""
        
        if planet.lower() not in self.PLANET_IDS:
            logger.error(f"Unknown planet: {planet}")
            return None
            
        planet_id = self.PLANET_IDS[planet.lower()]
        lat, lon = location
        
        # Format datetime for Horizons API
        dt = datetime.fromisoformat(datetime_str.replace("T", " "))
        start_time = dt.strftime("%Y-%m-%d %H:%M")
        end_time = (dt + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
        
        params = {
            'format': 'json',
            'COMMAND': planet_id,
            'OBJ_DATA': 'YES',
            'MAKE_EPHEM': 'YES',
            'EPHEM_TYPE': 'OBSERVER',
            'CENTER': f'coord@399',  # Earth surface coordinates
            'COORD_TYPE': 'GEODETIC',
            'SITE_COORD': f'{lon},{lat},0',
            'START_TIME': start_time,
            'STOP_TIME': end_time,
            'STEP_SIZE': '1m',
            'QUANTITIES': '1,9,20,23,24',  # RA/Dec, Alt/Az, Magnitude
            'CAL_FORMAT': 'CAL',
            'TIME_DIGITS': 'MINUTES',
            'ANG_FORMAT': 'DEG',
            'APPARENT': 'AIRLESS',
            'RANGE_UNITS': 'AU',
            'SUPPRESS_RANGE_RATE': 'NO',
            'SKIP_DAYLT': 'NO',
            'SOLAR_ELONG': '0,180',
            'EXTRA_PREC': 'NO',
            'R_T_S_ONLY': 'NO'
        }
        
        try:
            response = self.session.get(self.HORIZONS_URL, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'result' not in data:
                logger.error(f"No result in Horizons response for {planet}")
                return None
                
            # Parse the ephemeris data
            lines = data['result'].split('\n')
            
            # Find the data section
            data_started = False
            for line in lines:
                if '$$SOE' in line:
                    data_started = True
                    continue
                elif '$$EOE' in line:
                    break
                elif data_started and line.strip():
                    # Parse the ephemeris line
                    parts = line.split()
                    if len(parts) >= 8:
                        try:
                            ra = float(parts[3])  # RA in degrees
                            dec = float(parts[4])  # Dec in degrees
                            alt = float(parts[5])  # Altitude
                            az = float(parts[6])   # Azimuth
                            mag = float(parts[7]) if parts[7] != 'n.a.' else None
                            
                            return CelestialObject(
                                name=planet.title(),
                                ra=ra,
                                dec=dec,
                                alt=alt,
                                az=az,
                                magnitude=mag
                            )
                        except (ValueError, IndexError):
                            continue
            
            logger.warning(f"Could not parse position data for {planet}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Horizons for {planet}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing Horizons data for {planet}: {e}")
            return None
    
    def get_sun_position(self, location: Tuple[float, float], 
                        datetime_str: str) -> Optional[CelestialObject]:
        """Get Sun position from JPL Horizons"""
        return self.get_planet_position("sun", location, datetime_str)
    
    def validate_stellarium_vs_nasa(self, stellarium_objects: List[CelestialObject],
                                   location: Tuple[float, float], 
                                   datetime_str: str) -> Dict[str, Dict]:
        """Compare Stellarium objects with NASA data"""
        
        validation_results = {}
        
        logger.info(f"Validating {len(stellarium_objects)} objects against NASA data")
        
        for obj in stellarium_objects:
            if obj.name.lower() in self.PLANET_IDS:
                nasa_obj = self.get_planet_position(obj.name, location, datetime_str)
                
                if nasa_obj:
                    # Calculate differences
                    ra_diff = abs(obj.ra - nasa_obj.ra)
                    dec_diff = abs(obj.dec - nasa_obj.dec)
                    alt_diff = abs(obj.alt - nasa_obj.alt)
                    az_diff = abs(obj.az - nasa_obj.az)
                    
                    # Handle azimuth wraparound
                    if az_diff > 180:
                        az_diff = 360 - az_diff
                    
                    validation_results[obj.name] = {
                        'stellarium': {
                            'ra': obj.ra,
                            'dec': obj.dec,
                            'alt': obj.alt,
                            'az': obj.az,
                            'magnitude': obj.magnitude
                        },
                        'nasa': {
                            'ra': nasa_obj.ra,
                            'dec': nasa_obj.dec,
                            'alt': nasa_obj.alt,
                            'az': nasa_obj.az,
                            'magnitude': nasa_obj.magnitude
                        },
                        'differences': {
                            'ra_degrees': ra_diff,
                            'dec_degrees': dec_diff,
                            'alt_degrees': alt_diff,
                            'az_degrees': az_diff
                        },
                        'accuracy': {
                            'excellent': all(d < 0.1 for d in [ra_diff, dec_diff, alt_diff, az_diff]),
                            'good': all(d < 0.5 for d in [ra_diff, dec_diff, alt_diff, az_diff]),
                            'acceptable': all(d < 1.0 for d in [ra_diff, dec_diff, alt_diff, az_diff])
                        }
                    }
                else:
                    validation_results[obj.name] = {
                        'error': 'Could not retrieve NASA data for comparison'
                    }
        
        return validation_results
    
    def generate_validation_report(self, validation_results: Dict[str, Dict], 
                                 output_file: str = None) -> str:
        """Generate a human-readable validation report"""
        
        report_lines = [
            "=" * 60,
            "ABLUNA SKY MAP VALIDATION REPORT",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Validated Objects: {len(validation_results)}",
            ""
        ]
        
        excellent_count = 0
        good_count = 0
        acceptable_count = 0
        poor_count = 0
        
        for obj_name, result in validation_results.items():
            if 'error' in result:
                report_lines.extend([
                    f"OBJECT: {obj_name}",
                    f"  Status: ERROR - {result['error']}",
                    ""
                ])
                continue
            
            accuracy = result['accuracy']
            if accuracy['excellent']:
                status = "EXCELLENT (< 0.1°)"
                excellent_count += 1
            elif accuracy['good']:
                status = "GOOD (< 0.5°)"
                good_count += 1
            elif accuracy['acceptable']:
                status = "ACCEPTABLE (< 1.0°)"
                acceptable_count += 1
            else:
                status = "POOR (> 1.0°)"
                poor_count += 1
            
            report_lines.extend([
                f"OBJECT: {obj_name}",
                f"  Accuracy: {status}",
                f"  Position Differences:",
                f"    RA:  {result['differences']['ra_degrees']:.3f}°",
                f"    Dec: {result['differences']['dec_degrees']:.3f}°", 
                f"    Alt: {result['differences']['alt_degrees']:.3f}°",
                f"    Az:  {result['differences']['az_degrees']:.3f}°",
                ""
            ])
        
        # Summary
        total = len(validation_results)
        report_lines.extend([
            "SUMMARY:",
            f"  Excellent: {excellent_count}/{total} ({excellent_count/total*100:.1f}%)",
            f"  Good:      {good_count}/{total} ({good_count/total*100:.1f}%)",
            f"  Acceptable: {acceptable_count}/{total} ({acceptable_count/total*100:.1f}%)",
            f"  Poor:      {poor_count}/{total} ({poor_count/total*100:.1f}%)",
            "",
            "CRITERIA:",
            "  Excellent: All coordinates within 0.1°",
            "  Good: All coordinates within 0.5°", 
            "  Acceptable: All coordinates within 1.0°",
            "  Poor: One or more coordinates > 1.0°",
        ])
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            try:
                with open(output_file, 'w') as f:
                    f.write(report_text)
                logger.info(f"Validation report saved to {output_file}")
            except Exception as e:
                logger.error(f"Error saving validation report: {e}")
        
        return report_text


class MoonPhaseValidator:
    """Validates moon phase calculations"""
    
    def __init__(self):
        self.nasa_validator = NASAValidator()
    
    def get_moon_illumination(self, location: Tuple[float, float], 
                            datetime_str: str) -> Optional[float]:
        """Get moon illumination percentage from NASA"""
        
        moon_data = self.nasa_validator.get_planet_position("moon", location, datetime_str)
        if not moon_data:
            return None
        
        # This would require additional calculation for illumination percentage
        # For now, return placeholder
        return 50.0  # Placeholder
    
    def validate_moon_phase(self, stellarium_phase: str, location: Tuple[float, float],
                          datetime_str: str) -> Dict[str, any]:
        """Validate moon phase against NASA data"""
        
        illumination = self.get_moon_illumination(location, datetime_str)
        
        if illumination is None:
            return {"error": "Could not retrieve NASA moon data"}
        
        # Convert illumination to phase name
        if illumination < 1:
            nasa_phase = "New Moon"
        elif illumination < 25:
            nasa_phase = "Waxing Crescent"
        elif illumination < 75:
            nasa_phase = "First Quarter" if illumination < 50 else "Waxing Gibbous"
        elif illumination < 99:
            nasa_phase = "Full Moon" if illumination > 95 else "Waning Gibbous"
        else:
            nasa_phase = "Waning Crescent"
        
        return {
            "stellarium_phase": stellarium_phase,
            "nasa_phase": nasa_phase,
            "nasa_illumination": illumination,
            "match": stellarium_phase.lower() == nasa_phase.lower()
        }


def validate_sky_map(config, stellarium_objects: List[CelestialObject]) -> Dict:
    """Main validation function for a sky map"""
    
    validator = NASAValidator()
    moon_validator = MoonPhaseValidator()
    
    location = (config.location.latitude, config.location.longitude)
    
    # Create datetime string
    month, day = config.date.split("-")
    hour, minute = config.time.split(":")
    datetime_str = f"{config.year}-{month.zfill(2)}-{day.zfill(2)}T{hour.zfill(2)}:{minute.zfill(2)}:00"
    
    # Validate planet positions
    planet_validation = validator.validate_stellarium_vs_nasa(
        stellarium_objects, location, datetime_str
    )
    
    # Validate moon phase (if moon data available)
    moon_validation = {}
    moon_objects = [obj for obj in stellarium_objects if obj.name.lower() == "moon"]
    if moon_objects:
        moon_validation = moon_validator.validate_moon_phase(
            "Unknown", location, datetime_str  # Stellarium phase would need to be extracted
        )
    
    return {
        "location": f"{config.location.name}, {config.location.country}",
        "datetime": datetime_str,
        "planet_validation": planet_validation,
        "moon_validation": moon_validation,
        "validation_timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    # Example usage
    from .data_models import Location, SkyMapConfig
    
    # Create test configuration
    chicago = Location(
        name="Chicago",
        country="USA", 
        latitude=41.8819,
        longitude=-87.6278
    )
    config = SkyMapConfig(
        location=chicago,
        date="04-21",
        time="21:00",
        season="spring",
        year=2025
    )
    
    # Create test objects (normally these would come from Stellarium)
    test_objects = [
        CelestialObject(name="Mars", ra=45.0, dec=15.0, alt=30.0, az=180.0, magnitude=1.5),
        CelestialObject(name="Jupiter", ra=120.0, dec=-10.0, alt=45.0, az=225.0, magnitude=-2.0)
    ]
    
    # Run validation
    results = validate_sky_map(config, test_objects)
    
    # Generate report
    validator = NASAValidator()
    report = validator.generate_validation_report(
        results["planet_validation"], 
        "validation_report.txt"
    )
    
    print(report)
