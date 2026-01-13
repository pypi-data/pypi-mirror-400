#!/usr/bin/env python3
"""
CLI tool to check and repair model integrity.

Usage:
    python3 repair_model.py <predictor_path>
    python3 repair_model.py <predictor_path> --force  # Force repair even if no issues
"""

import sys
import argparse
import logging
from pathlib import Path

# Add lib to path - works for both src/lib (dev) and /sphere/app/lib (nodes) structures
script_dir = Path(__file__).parent
lib_path = script_dir / "lib"

# On nodes: script is in /sphere/app/, lib is in /sphere/app/lib/
# In dev: script is in src/, lib is in src/lib/
if lib_path.exists() and str(lib_path.resolve()) not in sys.path:
    sys.path.insert(0, str(lib_path.resolve()))

from lib.model_repair import check_and_repair_model

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Check and repair model integrity")
    parser.add_argument("predictor_path", type=str, help="Path to predictor pickle file")
    parser.add_argument("--force", action="store_true", help="Force repair even if no issues found")
    parser.add_argument("--check-only", action="store_true", help="Only check, don't repair")
    
    args = parser.parse_args()
    
    predictor_path = Path(args.predictor_path)
    
    if not predictor_path.exists():
        logger.error(f"❌ Predictor file not found: {predictor_path}")
        sys.exit(1)
    
    logger.info(f"🔍 Checking model: {predictor_path}")
    
    # Run check and repair
    result = check_and_repair_model(str(predictor_path), force_repair=args.force and not args.check_only)
    
    # Print results
    print("\n" + "="*60)
    print("MODEL INTEGRITY REPORT")
    print("="*60)
    
    if result.is_valid:
        print("✅ Status: VALID")
    else:
        print("❌ Status: INVALID")
    
    if result.issues_found:
        print(f"\n⚠️  Issues Found ({len(result.issues_found)}):")
        for i, issue in enumerate(result.issues_found, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ No issues found")
    
    if result.repairs_made:
        print(f"\n🔧 Repairs Made ({len(result.repairs_made)}):")
        for i, repair in enumerate(result.repairs_made, 1):
            print(f"   {i}. {repair}")
        if result.repaired_path:
            print(f"\n💾 Repaired model saved to: {result.repaired_path}")
    else:
        print("\nℹ️  No repairs were needed or possible")
    
    print("="*60 + "\n")
    
    # Exit code
    if result.is_valid:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

