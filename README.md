# Abluna Sky Maps

Python automation for generating high-resolution astronomical sky maps through Stellarium.

The application controls Stellarium through its Remote Control interface, applies location and sky-view parameters, and batch-generates map images for multiple locations, dates, seasons and times.

## Core Capabilities

- batch sky-map generation for multiple geographic locations;
- Stellarium Remote Control integration;
- configurable dates, times and seasonal presets;
- stereographic and other supported projection settings;
- resolution presets from Full HD through very large print-oriented outputs;
- CSV-driven location input;
- JSON-based configuration;
- automated Windows workflows through PowerShell;
- optional astronomical-data validation components.

## Architecture

```text
Location CSV + config.json
          |
          v
   Python orchestration
          |
          +------> resolution/config management
          |
          +------> astronomical validation
          |
          v
Stellarium Remote Control API
          |
          v
 Sky configuration + rendering
          |
          v
   Generated image files
```

## Requirements

### Stellarium

Install Stellarium and enable the **Remote Control** plugin.

Typical configuration:

```text
Host: localhost
Port: 8090
```

Enable the plugin at startup if you plan to run repeated batch jobs.

### Python

Python 3.8 or later is recommended for the current codebase.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Quick Start

Test the Stellarium connection:

```bash
python main.py --test-connection
```

Create an example location file:

```bash
python main.py --create-sample
```

Generate maps:

```bash
python main.py --csv sample_locations.csv
```

Generate only selected seasons or times:

```bash
python main.py \
  --csv sample_locations.csv \
  --seasons spring summer \
  --times "21:00" "04:00"
```

Select an output directory:

```bash
python main.py --csv sample_locations.csv --output generated_maps
```

## Location Input

Location data is supplied as CSV:

```csv
name,country,latitude,longitude,region
Tokyo,Japan,35.6762,139.6503,Asia
New York,USA,40.7128,-74.0060,North America
London,UK,51.5074,-0.1278,Europe
```

## Resolution Management

Inspect configured presets:

```bash
python configure_resolution.py --list
```

Show the active configuration:

```bash
python configure_resolution.py --info
```

Select a preset:

```bash
python configure_resolution.py --preset 4K_UHD
```

Or specify a custom size:

```bash
python configure_resolution.py --custom 3840 2160
```

The repository includes presets such as FHD, A3-oriented output, 4K and higher-resolution modes.

## PowerShell Workflow

Windows users can run the batch helper:

```powershell
.\run_high_res.ps1
```

Example:

```powershell
.\run_high_res.ps1 -Resolution 4K_UHD -CsvFile "sample_locations.csv" -OutputDir "output"
```

## Output Naming

Generated files use an Abluna-style naming convention:

```text
ABL[GenerationDate]_[Sequence]_[Location]_[Country]_[SkyDate]_[Time].jpg
```

Example:

```text
ABL250530_00001_tokyo_japan_04_21_9pm.jpg
```

## Configuration

The primary configuration file is `config.json`. It controls:

- Stellarium connection settings;
- output directory and image format;
- resolution presets;
- JPEG quality;
- sky culture;
- constellation labels and lines;
- projection;
- field of view;
- azimuth and altitude;
- seasonal dates;
- default generation times;
- batch delays.

## Project Components

The codebase contains components for:

- `SkyMapGenerator` — batch orchestration;
- `StellariumController` — communication with Stellarium;
- `Location` — geographic input representation;
- `SkyMapConfig` — per-map configuration;
- `ResolutionManager` — resolution selection and configuration;
- `NASAValidator` — astronomical validation support where used by the workflow.

## Troubleshooting

If the application cannot connect to Stellarium:

1. confirm Stellarium is running;
2. confirm the Remote Control plugin is enabled;
3. verify the configured port;
4. check local firewall rules.

If map output is missing or incomplete, inspect the project log and confirm that Stellarium has permission to write screenshots to its configured directory.

## Intended Use

This repository is designed for automated production of repeatable astronomical map renders, including batch generation for multiple locations and print-oriented workflows.

## License

This repository identifies the project as proprietary software developed for Abluna Sky Maps. Review the repository terms before reuse or redistribution.
