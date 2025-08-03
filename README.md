# Abluna Sky Maps - Ultra High Resolution Astronomical Map Generator

An advanced Python application that generates ultra-high resolution sky maps using Stellarium for multiple locations, seasons, and times. Capable of producing professional-grade astronomical images up to 8K UHD resolution for commercial printing and high-quality applications.

## Features

- 🌟 **Automated Sky Map Generation**: Batch generate sky maps for multiple locations with intelligent processing
- 📅 **Seasonal Coverage**: Generate maps for all four seasons with astronomical accuracy
- 🕘 **Flexible Time Points**: Create maps for any time of day with configurable intervals
- 🌍 **Global Locations**: Support for any location worldwide with GPS coordinates
- �️ **Ultra High Resolution Output**: Multiple resolution presets from HD to 8K UHD
  - **8K UHD**: 15360×8640 pixels (132.7 MP) - Ultimate quality for large format printing
  - **4K UHD**: 7680×4320 pixels (33.2 MP) - Professional quality (default)
  - **A3 300DPI**: 3510×4950 pixels (17.4 MP) - Optimized for A3 print format
  - **FHD**: 1920×1080 pixels (2.1 MP) - Standard HD quality
- ⚙️ **Dynamic Resolution Management**: Easy switching between quality presets
- 🎛️ **Advanced Configuration**: Comprehensive settings via JSON configuration
- 📊 **NASA Integration**: Built-in astronomical data validation using NASA APIs
- 🎯 **Commercial Grade**: Professional quality output suitable for commercial applications
- 🚀 **PowerShell Automation**: Streamlined generation scripts for Windows environments
- 📈 **Performance Optimized**: Intelligent API handling with multiple resolution setting methods

## Prerequisites

### Software Requirements

1. **Stellarium** (v0.21.0 or later)
   - Download from: https://stellarium.org/
   - Enable Remote Control plugin in Stellarium
   - Configure Remote Control to run on `localhost:8090`

2. **Python** (3.8 or later)
   - Download from: https://python.org/

### Stellarium Setup

1. Install and launch Stellarium
2. Go to Configuration (F2) → Plugins → Remote Control
3. Enable the plugin and set:
   - Port: `8090`
   - Enable at startup: ✓
4. Restart Stellarium
5. Verify the Remote Control is active (check the toolbar for the plugin icon)

## Installation

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd skymap
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test Stellarium connection:**
   ```bash
   python main.py --test-connection
   ```
   You should see: `✓ Stellarium connection successful`

## Quick Start

### 1. Create Sample Data
```bash
python main.py --create-sample
```
This creates `sample_locations.csv` with example locations (Tokyo, New York, London).

### 2. Configure Resolution (Optional)
```bash
# Show current resolution settings
python configure_resolution.py --info

# List available resolution presets
python configure_resolution.py --list

# Set to ultra-high 8K resolution
python configure_resolution.py --preset 8K_UHD

# Set custom resolution
python configure_resolution.py --custom 3840 2160
```

### 3. Generate Sky Maps

#### Using Python Script
```bash
# Generate maps for all locations, seasons, and times (default year 2025)
python main.py --csv sample_locations.csv

# Generate for specific year
python main.py --csv sample_locations.csv --year 2024

# Generate for specific seasons only
python main.py --csv sample_locations.csv --seasons spring summer

# Generate for specific times only
python main.py --csv sample_locations.csv --times "21:00" "04:00"

# Custom output directory
python main.py --csv sample_locations.csv --output high_res_maps
```

#### Using PowerShell Script (Windows)
```powershell
# Generate with current settings
.\run_high_res.ps1

# Set resolution and generate
.\run_high_res.ps1 -Resolution 8K_UHD

# Custom CSV file and output
.\run_high_res.ps1 -CsvFile custom.csv -OutputDir custom_output

# Show available options
.\run_high_res.ps1 -Help

# Test Stellarium connection
.\run_high_res.ps1 -TestConnection
```

### 4. Check Results
Generated maps will be saved in the specified output directory with the naming convention:
```
ABL[YYMMDD]_[SEQUENCE]_[LOCATION]_[COUNTRY]_[DATE]_[TIME].jpg
```

Example: `ABL250530_00001_tokyo_japan_04_21_9pm.jpg`

## Configuration

### Location CSV Format

Create a CSV file with the following columns:
```csv
name,country,latitude,longitude,region
Tokyo,Japan,35.6762,139.6503,Asia
New York,USA,40.7128,-74.0060,North America
London,UK,51.5074,-0.1278,Europe
```

### Configuration File (`config.json`)

The application is highly configurable through `config.json`:

```json
{
  "stellarium": {
    "base_url": "http://localhost:8090",
    "connection_timeout": 10,
    "screenshot_wait_time": 5
  },
  "output": {
    "directory": "output",
    "format": "jpg",
    "resolution": {
      "width": 7680,
      "height": 4320,
      "preset": "4K_UHD"
    },
    "quality": 95,
    "dpi": 300,
    "target_format": "4K_UHD",
    "alternative_resolutions": {
      "8K_UHD": {
        "width": 15360,
        "height": 8640
      },
      "4K_UHD": {
        "width": 7680,
        "height": 4320
      },
      "A3_300DPI": {
        "width": 3510,
        "height": 4950
      },
      "FHD": {
        "width": 1920,
        "height": 1080
      }
    }
  },
  "sky_settings": {
    "sky_culture": "modern",
    "constellation_lines": true,
    "constellation_labels": true,
    "projection": "stereographic",
    "field_of_view": 180.0,
    "initial_azimuth": 180.0,
    "initial_altitude": 30.0
  },
  "seasonal_config": {
    "spring": {
      "date": "04-21",
      "milky_way_brightness": 0.3,
      "zodiacal_light": 0.2
    },
    "summer": {
      "date": "07-21",
      "milky_way_brightness": 0.6,
      "zodiacal_light": 0.1
    },
    "autumn": {
      "date": "10-21",
      "milky_way_brightness": 0.4,
      "zodiacal_light": 0.15
    },
    "winter": {
      "date": "01-21",
      "milky_way_brightness": 0.2,
      "zodiacal_light": 0.3
    }
  },
  "generation": {
    "default_times": ["21:00", "04:00"],
    "default_year": 2025,
    "batch_delay": 3
  }
}
```

#### Key Settings Explained:

**Resolution Settings:**
- **width/height**: Current active resolution in pixels
- **preset**: Currently active resolution preset name
- **alternative_resolutions**: Available resolution presets for easy switching
- **quality**: JPEG compression quality (1-100, higher = better quality/larger files)
- **dpi**: Dots per inch for print applications

**Sky Settings:**
- **field_of_view**: Controls how much of the sky is visible (degrees)
- **initial_azimuth**: Horizontal direction (0°=North, 90°=East, 180°=South, 270°=West)
- **initial_altitude**: Vertical angle (0°=horizon, 90°=zenith)
- **projection**: `stereographic`, `orthographic`, `perspective`, or `hammer`

**Generation Settings:**
- **batch_delay**: Pause between generations (seconds)
- **screenshot_wait_time**: Time to wait for Stellarium to render (seconds)

### Resolution Presets

| Preset | Resolution | Megapixels | Use Case |
|--------|------------|------------|----------|
| **8K_UHD** | 15360×8640 | 132.7 MP | Ultra-high quality, large format printing, commercial applications |
| **4K_UHD** | 7680×4320 | 33.2 MP | Professional quality, standard large prints (default) |
| **A3_300DPI** | 3510×4950 | 17.4 MP | Optimized for A3 paper format at 300 DPI |
| **FHD** | 1920×1080 | 2.1 MP | Standard HD, web use, quick previews |

### Seasonal Configurations

Each season has preset dates and celestial brightness settings:

- **Spring**: April 21st - Moderate Milky Way visibility
- **Summer**: July 21st - Peak Milky Way visibility  
- **Autumn**: October 21st - Good Milky Way visibility
- **Winter**: January 21st - Minimal Milky Way visibility

## Command Line Reference

### Main Generator (`main.py`)

```bash
python main.py [OPTIONS]
```

#### Required Arguments
- `--csv PATH` - Path to CSV file containing location data

#### Optional Arguments
- `--output DIR` - Output directory for generated maps (default: `output`)
- `--seasons [SEASONS...]` - Seasons to generate. Choose from:
  - `spring` (April 21st)
  - `summer` (July 21st) 
  - `autumn` (October 21st)
  - `winter` (January 21st)
  - Default: All seasons
- `--times [TIMES...]` - Times in 24-hour HH:MM format (e.g., "21:00" "04:00")
  - Default: `["21:00", "04:00"]`
- `--year YEAR` - Year for sky map generation (default: 2025)

#### Utility Commands
- `--create-sample` - Create sample CSV file with example locations
- `--test-connection` - Test connection to Stellarium Remote Control
- `--help` - Show help message and exit

#### Examples
```bash
# Basic generation with all defaults
python main.py --csv locations.csv

# Generate spring maps only for 2024
python main.py --csv locations.csv --seasons spring --year 2024

# Generate for multiple specific times
python main.py --csv locations.csv --times "20:00" "22:00" "00:00" "06:00"

# Custom output directory
python main.py --csv locations.csv --output "premium_maps"

# Generate for specific seasons and times
python main.py --csv locations.csv --seasons spring summer --times "21:00"

# Create sample data
python main.py --create-sample

# Test Stellarium connection
python main.py --test-connection
```

### Resolution Configuration (`configure_resolution.py`)

```bash
python configure_resolution.py [OPTIONS]
```

#### Commands
- `--info` - Show current resolution configuration and megapixel count
- `--list` - List all available resolution presets with specifications
- `--preset PRESET` - Set resolution to a specific preset:
  - `8K_UHD` - 15360×8640 pixels (132.7 MP) - Ultra high definition
  - `4K_UHD` - 7680×4320 pixels (33.2 MP) - High definition (default)
  - `A3_300DPI` - 3510×4950 pixels (17.4 MP) - A3 print format
  - `FHD` - 1920×1080 pixels (2.1 MP) - Standard HD
- `--custom WIDTH HEIGHT` - Set custom resolution (width and height in pixels)
- `--help` - Show help message

#### Examples
```bash
# Show current settings
python configure_resolution.py --info

# List all available presets
python configure_resolution.py --list

# Set to 8K ultra-high resolution
python configure_resolution.py --preset 8K_UHD

# Set to A3 print format
python configure_resolution.py --preset A3_300DPI

# Set custom 4K resolution
python configure_resolution.py --custom 3840 2160
```

### PowerShell Generator (`run_high_res.ps1`)

```powershell
.\run_high_res.ps1 [OPTIONS]
```

#### Parameters
- `-CsvFile <path>` - CSV file with location data (default: `sample_locations.csv`)
- `-OutputDir <path>` - Output directory (default: `output`)
- `-Resolution <preset>` - Set resolution preset before generation:
  - `8K_UHD`, `4K_UHD`, `A3_300DPI`, `FHD`
- `-Seasons <array>` - Array of seasons (default: `@("04", "07", "10", "01")`)
- `-Times <array>` - Array of times (default: `@("9pm", "4am")`)

#### Switches
- `-Help` - Show detailed help and usage examples
- `-ListResolutions` - Display available resolution presets
- `-ShowInfo` - Show current resolution configuration
- `-TestConnection` - Test Stellarium connection

#### Examples
```powershell
# Generate with current settings
.\run_high_res.ps1

# Set to 8K resolution and generate
.\run_high_res.ps1 -Resolution 8K_UHD

# Use custom CSV file and output directory
.\run_high_res.ps1 -CsvFile "custom_locations.csv" -OutputDir "ultra_hd"

# Generate for specific seasons only
.\run_high_res.ps1 -Seasons @("04", "10") -Times @("21:00")

# Show available resolution options
.\run_high_res.ps1 -ListResolutions

# Check current configuration
.\run_high_res.ps1 -ShowInfo

# Test Stellarium connection
.\run_high_res.ps1 -TestConnection

# Show detailed help
.\run_high_res.ps1 -Help
```

## Command Line Options

## Output Files

### Naming Convention
Files are named using the ABL (Abluna) convention:
```
ABL[GenerationDate]_[Sequence]_[Location]_[Country]_[SkyDate]_[Time].jpg
```

Where:
- `GenerationDate`: When the file was created (YYMMDD)
- `Sequence`: Sequential number (00001, 00002, etc.)
- `Location`: Location name (lowercase, spaces→underscores)
- `Country`: Country name (lowercase, spaces→underscores)
- `SkyDate`: Sky date (MM_DD format)
- `Time`: Time with AM/PM (9pm, 4am, etc.)

### Map Specifications

- **Resolution**: Configurable from FHD (1920×1080) to 8K UHD (15360×8640)
- **Current Default**: 4K UHD (7680×4320 pixels) at 300 DPI
- **Format**: JPEG with 95% quality (configurable)
- **Projection**: Stereographic (configurable)
- **Orientation**: South-centered view at 30° elevation
- **Features**: Constellation lines, labels, planets, Milky Way
- **Aspect Ratio**: Maintained across all resolution presets
- **Color Depth**: 24-bit RGB
- **File Size**: Varies by resolution:
  - 8K UHD: ~200-500 MB per image
  - 4K UHD: ~50-150 MB per image  
  - A3 300DPI: ~25-75 MB per image
  - FHD: ~2-5 MB per image

## Troubleshooting

### Common Issues

1. **"Cannot connect to Stellarium"**
   - Ensure Stellarium is running
   - Check Remote Control plugin is enabled
   - Verify port 8090 is not blocked by firewall

2. **"No screenshots found"**
   - Check Stellarium screenshot directory permissions
   - Increase `screenshot_wait_time` in config.json
   - Verify disk space availability

3. **"Failed to set location"**
   - Check CSV format and coordinate validity
   - Ensure latitude/longitude are numeric
   - Verify location names don't contain special characters

4. **Maps have wrong orientation**
   - Adjust `field_of_view`, `initial_azimuth`, `initial_altitude` in config.json
   - Try different projection types

### Logs

Check `abluna_skymap.log` for detailed execution logs:
```bash
tail -f abluna_skymap.log
```

## Workflow Examples

### Complete High-Resolution Workflow

```bash
# 1. Test Stellarium connection
python main.py --test-connection

# 2. Create sample locations (if needed)
python main.py --create-sample

# 3. Check current resolution settings
python configure_resolution.py --info

# 4. Set to ultra-high resolution for commercial printing
python configure_resolution.py --preset 8K_UHD

# 5. Generate maps for all locations and seasons
python main.py --csv sample_locations.csv --output ultra_hd_maps

# 6. Generate specific configurations
python main.py --csv custom_locations.csv --seasons spring summer --times "20:00" "22:00" --year 2024
```

### PowerShell Automated Workflow

```powershell
# All-in-one high-resolution generation
.\run_high_res.ps1 -Resolution 8K_UHD -CsvFile "premium_locations.csv" -OutputDir "commercial_prints"

# Quick quality check with lower resolution
.\run_high_res.ps1 -Resolution FHD -CsvFile "test_locations.csv" -OutputDir "previews"

# Seasonal campaign generation
.\run_high_res.ps1 -Resolution 4K_UHD -Seasons @("04", "07") -Times @("21:00")
```

### Commercial Production Workflow

```bash
# 1. Set maximum quality
python configure_resolution.py --preset 8K_UHD

# 2. Generate for multiple client locations
python main.py --csv client_locations.csv --output client_delivery --year 2024

# 3. Generate preview versions
python configure_resolution.py --preset FHD
python main.py --csv client_locations.csv --output client_previews --year 2024

# 4. Reset to standard quality
python configure_resolution.py --preset 4K_UHD
```

## Advanced Usage

### Custom Sky Settings

You can create custom configurations for specific requirements:

```python
# Example: Create a config for southern hemisphere viewing
config = SkyMapConfig(
    location=sydney,
    date="12-21",  # Summer solstice in southern hemisphere
    time="21:00",
    season="summer",
    year=2024,
    field_of_view=120.0,
    initial_azimuth=0.0,    # North
    initial_altitude=45.0
)
```

### Batch Processing Scripts

For convenience, use the provided automation scripts:

**PowerShell (Windows):**
```powershell
# High-resolution generator with preset management
.\run_high_res.ps1

# Legacy batch file
run_batch_generator.bat

# Alternative PowerShell script
.\run_generator.ps1
```

**Quick Resolution Management:**
```bash
# Check current resolution
python configure_resolution.py --info

# Switch to 8K for ultra-high quality
python configure_resolution.py --preset 8K_UHD

# Generate with new resolution
python main.py --csv sample_locations.csv
```

### NASA Validation

The application includes NASA astronomical data validation:

```python
from src.abluna import NASAValidator

validator = NASAValidator()
planet_data = validator.get_planet_positions(date, location)
```

## API Reference

### Core Classes

- **`SkyMapGenerator`**: Main generation orchestrator with resolution management
- **`StellariumController`**: Enhanced Stellarium API interface with multiple resolution setting methods
- **`Location`**: Geographic location data structure
- **`SkyMapConfig`**: Configuration for individual maps with resolution support
- **`NASAValidator`**: Astronomical data validation
- **`ResolutionManager`**: Handles resolution presets and configuration management

### Key Methods

```python
# Generate maps with current resolution settings
generator = SkyMapGenerator("output_dir")
stats = generator.batch_generate(locations, seasons, times, year)

# Enhanced Stellarium controller with resolution support
controller = StellariumController()
is_connected = controller.check_connection()
resolution_set = controller.set_image_resolution(7680, 4320)

# Create location with validation
location = Location(
    name="Paris",
    country="France", 
    latitude=48.8566,
    longitude=2.3522
)

# Resolution management
from configure_resolution import ResolutionManager
manager = ResolutionManager()
manager.set_preset("8K_UHD")
current_config = manager.get_current_resolution()
```

### Resolution Configuration API

```python
# Set resolution programmatically
import json

config = json.load(open('config.json'))
config['output']['resolution'] = {
    'width': 15360,
    'height': 8640,
    'preset': '8K_UHD'
}
json.dump(config, open('config.json', 'w'), indent=2)

# Available preset configurations
PRESETS = {
    "8K_UHD": {"width": 15360, "height": 8640},
    "4K_UHD": {"width": 7680, "height": 4320},
    "A3_300DPI": {"width": 3510, "height": 4950},
    "FHD": {"width": 1920, "height": 1080}
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is proprietary software developed for Abluna Sky Maps.

## Support

For technical support or questions:
- Check the troubleshooting section above
- Review the log files for error details
- Ensure all prerequisites are properly installed

---

**Abluna Sky Maps** - Creating timeless astronomical art for special moments.
