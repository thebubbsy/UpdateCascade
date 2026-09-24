#!/usr/bin/env python3
"""
UpdateCascade Build and Validation Pipeline
Author: Matthew Bubb <matt@onyachamp.com>
License: MIT
"""

import sys
import shutil
import argparse
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

def run_pipeline(sync_onyachamp=False):
    print("=== UpdateCascade Build & Validation Pipeline ===")
    
    # 1. Sync cascade.ps1 -> cascade
    ps1_file = REPO_ROOT / "cascade.ps1"
    raw_file = REPO_ROOT / "cascade"
    print(f"[BUILD] Synchronizing {ps1_file.name} -> {raw_file.name}...")
    shutil.copyfile(ps1_file, raw_file)
    print("  Sync completed.")

    # 2. Run Verification Suite
    test_runner = REPO_ROOT / "tests" / "test_cascade.py"
    print(f"[TEST] Executing test suite: {test_runner.name}...")
    import subprocess
    res = subprocess.run([sys.executable, str(test_runner)], check=False)
    if res.returncode != 0:
        print("[BUILD ERROR] Test suite failed. Halting build.")
        sys.exit(res.returncode)

    # 3. Optional sync to onyachamp
    if sync_onyachamp:
        onyachamp_dir = Path("C:/src/onyachamp")
        if onyachamp_dir.exists():
            print(f"[DEPLOY] Syncing cascade artifacts to {onyachamp_dir}...")
            shutil.copyfile(ps1_file, onyachamp_dir / "cascade.ps1")
            shutil.copyfile(raw_file, onyachamp_dir / "cascade")
            print("  Successfully copied cascade.ps1 and cascade to onyachamp.")
        else:
            print(f"[DEPLOY WARNING] Directory {onyachamp_dir} not found; skipping onyachamp sync.")

    print("\n=== BUILD AND VALIDATION SUCCESSFUL ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UpdateCascade Build Pipeline")
    parser.add_argument("--sync-onyachamp", action="store_true", help="Sync cascade artifacts to C:/src/onyachamp")
    args = parser.parse_args()
    run_pipeline(sync_onyachamp=args.sync_onyachamp)
