"""
Resolution Configuration Script for Abluna Sky Maps
Allows easy switching between different resolution presets
"""

import json
import argparse
import sys
from pathlib import Path

def load_config():
    """Load the current configuration"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config.json")
        sys.exit(1)

def save_config(config):
    """Save the configuration back to file"""
    try:
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        print("✓ Configuration saved successfully")
    except Exception as e:
        print(f"Error saving configuration: {e}")
        sys.exit(1)

def list_presets(config):
    """List available resolution presets"""
    print("\nAvailable Resolution Presets:")
    print("=" * 50)
    
    current = config["output"]["resolution"]
    alternatives = config["output"]["alternative_resolutions"]
    
    # Show current resolution
    current_preset = current.get("preset", "Custom")
    print(f"Current: {current['width']}x{current['height']} ({current_preset})")
    print()
    
    # Show all available presets
    for preset_name, resolution in alternatives.items():
        width, height = resolution["width"], resolution["height"]
        megapixels = round((width * height) / 1_000_000, 1)
        print(f"{preset_name:15} {width:>5}x{height:<5} ({megapixels:>4.1f} MP)")

def set_resolution_preset(config, preset_name):
    """Set resolution to a specific preset"""
    alternatives = config["output"]["alternative_resolutions"]
    
    if preset_name not in alternatives:
        print(f"Error: Preset '{preset_name}' not found")
        print("Available presets:", ", ".join(alternatives.keys()))
        sys.exit(1)
    
    resolution = alternatives[preset_name]
    config["output"]["resolution"]["width"] = resolution["width"]
    config["output"]["resolution"]["height"] = resolution["height"]
    config["output"]["resolution"]["preset"] = preset_name
    
    width, height = resolution["width"], resolution["height"]
    megapixels = round((width * height) / 1_000_000, 1)
    print(f"✓ Resolution set to {width}x{height} ({preset_name}, {megapixels} MP)")

def set_custom_resolution(config, width, height):
    """Set a custom resolution"""
    config["output"]["resolution"]["width"] = width
    config["output"]["resolution"]["height"] = height
    config["output"]["resolution"]["preset"] = "Custom"
    
    megapixels = round((width * height) / 1_000_000, 1)
    print(f"✓ Resolution set to {width}x{height} (Custom, {megapixels} MP)")

def get_resolution_info(config):
    """Display current resolution information"""
    resolution = config["output"]["resolution"]
    width, height = resolution["width"], resolution["height"]
    preset = resolution.get("preset", "Custom")
    megapixels = round((width * height) / 1_000_000, 1)
    
    print(f"\nCurrent Resolution Configuration:")
    print(f"  Size: {width}x{height}")
    print(f"  Preset: {preset}")
    print(f"  Megapixels: {megapixels} MP")
    print(f"  Aspect Ratio: {width/height:.2f}:1")
    
    # Estimate file size (rough calculation)
    estimated_mb = (width * height * 3 * 0.95) / (1024 * 1024)  # 95% quality JPEG
    print(f"  Estimated file size: {estimated_mb:.1f} MB")

def main():
    parser = argparse.ArgumentParser(description="Configure resolution for Abluna Sky Maps")
    parser.add_argument("--list", action="store_true", help="List available resolution presets")
    parser.add_argument("--preset", help="Set resolution to a specific preset")
    parser.add_argument("--custom", nargs=2, type=int, metavar=("WIDTH", "HEIGHT"), 
                       help="Set custom resolution (width height)")
    parser.add_argument("--info", action="store_true", help="Show current resolution info")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if args.list:
        list_presets(config)
    elif args.preset:
        set_resolution_preset(config, args.preset)
        save_config(config)
    elif args.custom:
        width, height = args.custom
        set_custom_resolution(config, width, height)
        save_config(config)
    elif args.info:
        get_resolution_info(config)
    else:
        # Show current info by default
        get_resolution_info(config)
        print("\nUse --help to see available options")

if __name__ == "__main__":
    main()
