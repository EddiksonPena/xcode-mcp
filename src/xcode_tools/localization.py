"""Localization and internationalization tools."""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List


def extract_strings(project_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Extract localizable strings from code using genstrings."""
    project_dir = Path(project_path).parent if project_path.endswith(('.xcodeproj', '.xcworkspace')) else Path(project_path)
    
    if not project_dir.exists():
        return {"success": False, "error": f"Project path not found: {project_path}"}
    
    output_file = Path(output_path) if output_path else project_dir / "Localizable.strings"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Find Swift files
        swift_files = list(project_dir.rglob("*.swift"))
        
        if not swift_files:
            return {"success": False, "error": "No Swift files found"}
        
        # Use genstrings to extract NSLocalizedString calls
        cmd = ["genstrings", "-o", str(output_file.parent), str(swift_files[0])]
        
        # Add all Swift files
        for swift_file in swift_files[1:10]:  # Limit to first 10 for performance
            cmd.append(str(swift_file))
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0 or output_file.exists():
            # Count extracted strings
            string_count = 0
            if output_file.exists():
                content = output_file.read_text()
                string_count = len(re.findall(r'^".*"', content, re.MULTILINE))
            
            return {
                "success": True,
                "output_file": str(output_file),
                "strings_extracted": string_count,
                "files_processed": len(swift_files[:10])
            }
        else:
            return {"success": False, "error": result.stderr}
    except FileNotFoundError:
        return {"success": False, "error": "genstrings not found. Install Xcode Command Line Tools."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_localizations(project_path: str) -> Dict[str, Any]:
    """Validate localization files for missing translations."""
    project_dir = Path(project_path).parent if project_path.endswith(('.xcodeproj', '.xcworkspace')) else Path(project_path)
    
    # Find base localization
    base_strings = None
    localizations = {}
    
    try:
        # Find all .lproj directories
        for lproj_dir in project_dir.rglob("*.lproj"):
            locale = lproj_dir.stem
            strings_file = lproj_dir / "Localizable.strings"
            
            if strings_file.exists():
                localizations[locale] = {
                    "path": str(strings_file),
                    "keys": []
                }
                
                # Parse strings file
                content = strings_file.read_text()
                keys = re.findall(r'^"([^"]+)"', content, re.MULTILINE)
                localizations[locale]["keys"] = keys
                
                if locale == "en" or locale == "Base":
                    base_strings = set(keys)
        
        if not base_strings:
            return {"success": False, "error": "Base localization (en or Base) not found"}
        
        # Check for missing translations
        issues = []
        for locale, loc_data in localizations.items():
            if locale in ["en", "Base"]:
                continue
            
            missing_keys = base_strings - set(loc_data["keys"])
            if missing_keys:
                issues.append({
                    "locale": locale,
                    "missing_keys": list(missing_keys),
                    "missing_count": len(missing_keys)
                })
        
        return {
            "success": True,
            "localizations": list(localizations.keys()),
            "base_keys_count": len(base_strings),
            "issues": issues,
            "is_valid": len(issues) == 0
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_localization_coverage(project_path: str) -> Dict[str, Any]:
    """Check translation coverage percentage."""
    validation_result = validate_localizations(project_path)
    
    if not validation_result.get("success"):
        return validation_result
    
    base_keys_count = validation_result.get("base_keys_count", 0)
    if base_keys_count == 0:
        return {"success": False, "error": "No base localization keys found"}
    
    coverage = {}
    total_coverage = 0
    
    for locale in validation_result.get("localizations", []):
        if locale in ["en", "Base"]:
            coverage[locale] = 100.0
            continue
        
        # Find missing keys for this locale
        locale_issues = [issue for issue in validation_result.get("issues", []) if issue["locale"] == locale]
        missing_count = locale_issues[0]["missing_count"] if locale_issues else 0
        translated_count = base_keys_count - missing_count
        locale_coverage = (translated_count / base_keys_count * 100) if base_keys_count > 0 else 0
        
        coverage[locale] = round(locale_coverage, 2)
        total_coverage += locale_coverage
    
    avg_coverage = total_coverage / (len(coverage) - 1) if len(coverage) > 1 else 100.0
    
    return {
        "success": True,
        "coverage_by_locale": coverage,
        "average_coverage": round(avg_coverage, 2),
        "base_keys_count": base_keys_count
    }


def list_localizations(project_path: str) -> Dict[str, Any]:
    """List all supported locales in project."""
    project_dir = Path(project_path).parent if project_path.endswith(('.xcodeproj', '.xcworkspace')) else Path(project_path)
    
    locales = []
    
    try:
        # Find all .lproj directories
        for lproj_dir in project_dir.rglob("*.lproj"):
            locale = lproj_dir.stem
            locales.append({
                "locale": locale,
                "path": str(lproj_dir),
                "has_strings": (lproj_dir / "Localizable.strings").exists()
            })
        
        return {
            "success": True,
            "locales": locales,
            "locale_count": len(locales)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

