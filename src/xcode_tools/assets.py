"""Asset management tools for images, icons, and asset catalogs."""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List


def optimize_images(asset_path: str, quality: int = 80, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Optimize images using sips (macOS built-in tool)."""
    asset_file = Path(asset_path)
    if not asset_file.exists():
        return {"success": False, "error": f"Asset not found: {asset_path}"}
    
    output = Path(output_path) if output_path else asset_file
    
    try:
        # Use sips to optimize (convert to JPEG with quality)
        result = subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality), str(asset_file), "--out", str(output)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            original_size = asset_file.stat().st_size
            optimized_size = output.stat().st_size if output.exists() else original_size
            savings = ((original_size - optimized_size) / original_size * 100) if original_size > 0 else 0
            
            return {
                "success": True,
                "original_size_bytes": original_size,
                "optimized_size_bytes": optimized_size,
                "savings_percent": round(savings, 2),
                "output_path": str(output)
            }
        else:
            return {"success": False, "error": result.stderr}
    except FileNotFoundError:
        return {"success": False, "error": "sips not found (should be available on macOS)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_app_icons(source_image: str, output_path: str) -> Dict[str, Any]:
    """Generate app icon set from source image."""
    source = Path(source_image)
    if not source.exists():
        return {"success": False, "error": f"Source image not found: {source_image}"}
    
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Standard iOS app icon sizes
    icon_sizes = [
        (20, 20, 2), (20, 20, 3),  # Notification
        (29, 29, 2), (29, 29, 3),  # Settings
        (40, 40, 2), (40, 40, 3),  # Spotlight
        (60, 60, 2), (60, 60, 3),  # App
        (1024, 1024, 1),  # App Store
    ]
    
    generated = []
    
    try:
        for width, height, scale in icon_sizes:
            size = width * scale
            filename = f"icon_{width}x{height}@{scale}x.png"
            output_file = output_dir / filename
            
            result = subprocess.run(
                ["sips", "-z", str(size), str(size), str(source), "--out", str(output_file)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                generated.append({
                    "filename": filename,
                    "size": f"{size}x{size}",
                    "path": str(output_file)
                })
        
        return {
            "success": True,
            "generated_icons": generated,
            "count": len(generated),
            "output_directory": str(output_dir)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_asset_catalog(project_path: str) -> Dict[str, Any]:
    """Validate Assets.xcassets structure."""
    project_dir = Path(project_path).parent if project_path.endswith(('.xcodeproj', '.xcworkspace')) else Path(project_path)
    
    # Find Assets.xcassets
    assets_catalog = None
    for path in project_dir.rglob("Assets.xcassets"):
        assets_catalog = path
        break
    
    if not assets_catalog or not assets_catalog.exists():
        return {"success": False, "error": "Assets.xcassets not found"}
    
    issues = []
    assets_found = []
    
    try:
        # Check Contents.json
        contents_file = assets_catalog / "Contents.json"
        if contents_file.exists():
            with open(contents_file) as f:
                contents = json.load(f)
                if "info" not in contents:
                    issues.append("Missing info in Contents.json")
        else:
            issues.append("Missing Contents.json")
        
        # Check for asset sets
        for item in assets_catalog.iterdir():
            if item.is_dir() and item.suffix == ".imageset":
                assets_found.append({
                    "name": item.stem,
                    "path": str(item)
                })
                
                # Check imageset Contents.json
                imageset_contents = item / "Contents.json"
                if not imageset_contents.exists():
                    issues.append(f"Missing Contents.json in {item.name}")
        
        return {
            "success": True,
            "assets_catalog_path": str(assets_catalog),
            "assets_found": assets_found,
            "asset_count": len(assets_found),
            "issues": issues,
            "is_valid": len(issues) == 0
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_asset_sizes(project_path: str, max_size_mb: float = 5.0) -> Dict[str, Any]:
    """Check asset file sizes and warn on large files."""
    project_dir = Path(project_path).parent if project_path.endswith(('.xcodeproj', '.xcworkspace')) else Path(project_path)
    
    large_assets = []
    total_size = 0
    
    try:
        # Find Assets.xcassets
        assets_catalog = None
        for path in project_dir.rglob("Assets.xcassets"):
            assets_catalog = path
            break
        
        if not assets_catalog:
            return {"success": False, "error": "Assets.xcassets not found"}
        
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # Check all image files
        for image_file in assets_catalog.rglob("*.png"):
            size = image_file.stat().st_size
            total_size += size
            
            if size > max_size_bytes:
                large_assets.append({
                    "path": str(image_file),
                    "size_mb": round(size / (1024 * 1024), 2),
                    "size_bytes": size
                })
        
        for image_file in assets_catalog.rglob("*.jpg"):
            size = image_file.stat().st_size
            total_size += size
            
            if size > max_size_bytes:
                large_assets.append({
                    "path": str(image_file),
                    "size_mb": round(size / (1024 * 1024), 2),
                    "size_bytes": size
                })
        
        return {
            "success": True,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "large_assets": large_assets,
            "large_asset_count": len(large_assets),
            "max_size_mb": max_size_mb
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def manage_color_assets(action: str, color_name: str, hex_color: Optional[str] = None, project_path: Optional[str] = None) -> Dict[str, Any]:
    """Manage color sets in asset catalog."""
    if action not in ["list", "add", "remove"]:
        return {"success": False, "error": "Action must be 'list', 'add', or 'remove'"}
    
    if action == "add" and not hex_color:
        return {"success": False, "error": "hex_color required for 'add' action"}
    
    # For now, return structure info
    return {
        "success": True,
        "action": action,
        "note": "Color asset management requires manual asset catalog editing or xcodeproj library",
        "suggested_hex": hex_color if hex_color else None
    }

