"""
Metadata handler for adding IPTC data to sky map images
"""

import os
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import logging

logger = logging.getLogger(__name__)

try:
    from iptcinfo3 import IPTCInfo
    IPTC_AVAILABLE = True
except ImportError:
    logger.warning("iptcinfo3 not available. Install with: pip install iptcinfo3")
    IPTC_AVAILABLE = False

class SkyMapMetadata:
    """Handles metadata operations for sky map images"""
    
    def __init__(self):
        self.border_color = (248, 247, 243)  # F8F7F3
        
    def add_iptc_metadata(self, image_path: str, metadata: Dict[str, str]) -> bool:
        """Add IPTC metadata to image file"""
        if not IPTC_AVAILABLE:
            logger.warning("IPTC metadata not available - skipping")
            return False
            
        try:
            # For PNG files, iptcinfo3 may have issues. Let's handle this gracefully.
            # Create IPTC info with safer parameters
            info = IPTCInfo(image_path, force=True, inp_charset='utf-8')
            
            # Add metadata fields with proper encoding
            if 'headline' in metadata:
                info['headline'] = str(metadata['headline'])
            if 'caption' in metadata:
                info['caption/abstract'] = str(metadata['caption'])
            if 'keywords' in metadata:
                info['keywords'] = metadata['keywords']
            if 'city' in metadata:
                info['city'] = str(metadata['city'])
            if 'region' in metadata:
                info['province/state'] = str(metadata['region'])
            if 'country' in metadata:
                info['country/primary location name'] = str(metadata['country'])
            if 'coordinates' in metadata:
                info['special instructions'] = str(metadata['coordinates'])
            
            info['category'] = 'Astronomy'
            info['supplemental category'] = ['Sky Map', 'Stellarium', 'Abluna']
            
            # Custom fields for astronomical data
            if 'visible_objects' in metadata:
                info['object name'] = str(metadata['visible_objects'])
            info['copyright notice'] = 'Abluna Sky Maps'
            
            # Save metadata with better error handling
            info.save()
            logger.info(f"IPTC metadata added to {image_path}")
            return True
            
        except Exception as e:
            # Log the error but don't fail the entire process
            logger.error(f"Error adding IPTC metadata to {image_path}: {e}")
            logger.info("Continuing without IPTC metadata for this image")
            return False
    
    def create_bordered_image(self, image_path: str, metadata: Dict[str, str], 
                            output_path: str) -> bool:
        """Create version with border and metadata text"""
        try:
            # Open original image
            img = Image.open(image_path)
            img_width, img_height = img.size
            
            # Calculate border dimensions
            border_height = 200  # Height for text area
            total_height = img_height + border_height
            
            # Create new image with border
            bordered_img = Image.new('RGB', (img_width, total_height), self.border_color)
            
            # Paste original image
            bordered_img.paste(img, (0, 0))
            
            # Add text to border
            draw = ImageDraw.Draw(bordered_img)
            
            # Try to load a font
            try:
                font_size = 24
                font = ImageFont.truetype("arial.ttf", font_size)
                small_font = ImageFont.truetype("arial.ttf", 18)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Prepare text
            text_y = img_height + 20
            line_height = 30
            
            # Location and coordinates
            location_text = f"{metadata.get('location', '')}, {metadata.get('country', '')}"
            coords_text = f"Lat: {metadata.get('latitude', '')}, Lon: {metadata.get('longitude', '')}"
            
            # Date and time info
            season_text = f"Season: {metadata.get('season', '')}"
            date_text = f"Date: {metadata.get('date', '')}"
            time_text = f"Time: {metadata.get('time', '')}"
            
            # Visible objects
            objects_text = f"Visible: {metadata.get('visible_objects', '')}"
            
            # Tagline
            tagline = metadata.get('tagline', 'Abluna — Timeless Sky Map')
            
            # Draw text lines
            text_color = (50, 50, 50)  # Dark gray
            
            draw.text((20, text_y), location_text, fill=text_color, font=font)
            draw.text((20, text_y + line_height), coords_text, fill=text_color, font=small_font)
            draw.text((20, text_y + line_height * 2), f"{season_text} | {date_text} | {time_text}", 
                     fill=text_color, font=small_font)
            draw.text((20, text_y + line_height * 3), objects_text, fill=text_color, font=small_font)
            draw.text((20, text_y + line_height * 4.5), tagline, fill=text_color, font=small_font)
            
            # Save bordered image
            bordered_img.save(output_path, quality=95)
            logger.info(f"Bordered image created: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating bordered image: {e}")
            return False
    
    def get_visible_objects_text(self, objects: List[str]) -> str:
        """Format visible objects list as text"""
        if not objects or objects == ["Placeholder - implement object detection"]:
            return "Stars, Planets, Constellations"
        
        # Limit to reasonable length
        if len(objects) > 10:
            return ", ".join(objects[:10]) + f" (+{len(objects)-10} more)"
        else:
            return ", ".join(objects)
    
    def prepare_metadata_dict(self, config, visible_objects: List[str]) -> Dict[str, str]:
        """Prepare metadata dictionary from config"""
        from datetime import datetime
        
        # Format coordinates
        lat = config.location.latitude
        lon = config.location.longitude
        lat_str = f"{abs(lat):.4f}°{'N' if lat >= 0 else 'S'}"
        lon_str = f"{abs(lon):.4f}°{'E' if lon >= 0 else 'W'}"
        
        # Format date for tagline
        month_names = {
            "01": "January", "04": "April", "07": "July", "10": "October"
        }
        month, day = config.date.split("-")
        date_display = f"{month_names.get(month, month)} {int(day)}"
        
        # Format time display
        hour = int(config.time.split(":")[0])
        time_display = f"{hour % 12 if hour % 12 != 0 else 12}:00 {'PM' if hour >= 12 else 'AM'}"
        
        metadata = {
            'headline': f"Sky Map - {config.location.name}, {config.location.country}",
            'caption': f"Sky map for {config.location.name} showing the night sky on {date_display} at {time_display}",
            'keywords': [
                'sky map', 'astronomy', 'stellarium', 'stars', 'constellations',
                config.location.name, config.location.country, config.season
            ],
            'city': config.location.name,
            'region': config.location.region,
            'country': config.location.country,
            'coordinates': f"{lat_str}, {lon_str}",
            'location': config.location.name,
            'latitude': lat_str,
            'longitude': lon_str,
            'season': config.season.title(),
            'date': date_display,
            'time': time_display,
            'visible_objects': self.get_visible_objects_text(visible_objects),
            'tagline': f"The sky on {date_display} looks nearly the same every year. Abluna — Timeless Sky Map."
        }
        
        return metadata
