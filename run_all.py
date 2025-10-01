#!/usr/bin/env python3
"""
Run the full institutional-grade pipeline chain end-to-end:
- free_data_ingestion → ingest → features → models_baseline → models_nn → econ_impact

Enhanced with FREE_DATA_SOURCES for zero-cost institutional intelligence:
- USDA agricultural data
- CFTC positioning analysis
- Weather intelligence from multiple regions
- News sentiment analysis
- FX and macro factors
- Brazil/Argentina supply data
- China demand intelligence

Usage:
  python run_all.py
  python run_all.py --skip-free-data  # Skip free data refresh for faster runs

Exits non-zero if any stage fails. Prints JSON status lines per stage.
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime

# Enhanced pipeline stages with institutional-grade data ingestion and bulletproof components
STAGES = [
    ("bulletproof_init", "core.bulletproof_integration", "initialize_systems"),
    ("free_data_ingestion", "FREE_DATA_SOURCES", "main"),
    ("ingest", "pipelines.ingest", "main"),
    ("features", "pipelines.features", "run"),
    ("models_baseline", "pipelines.models_baseline", "run"),
    ("models_nn", "pipelines.models_nn", "run"),
    ("econ_impact", "pipelines.econ_impact", "run"),
    ("bulletproof_cleanup", "core.bulletproof_integration", "cleanup_resources"),
]


def run_stage(name: str, module_name: str, func_name: str) -> None:
    start = datetime.utcnow().isoformat()
    try:
        mod = importlib.import_module(module_name)
        func = getattr(mod, func_name)
        func()
        print(json.dumps({"stage": name, "status": "ok", "ts": start}))
    except SystemExit as e:
        # If a stage calls argparse and exits, normalize to error if non-zero
        code = int(getattr(e, "code", 1))
        if code != 0:
            print(json.dumps({"stage": name, "status": "error", "code": code, "ts": start}))
            raise
        else:
            print(json.dumps({"stage": name, "status": "ok", "ts": start}))
    except Exception as e:
        print(json.dumps({"stage": name, "status": "error", "error": str(e), "ts": start}))
        raise


def main() -> int:
    """
    Main pipeline execution with enhanced institutional-grade data processing
    """
    parser = argparse.ArgumentParser(description="Run institutional-grade CBI-V13 pipeline")
    parser.add_argument("--skip-free-data", action="store_true",
                       help="Skip free data ingestion (faster for development)")
    parser.add_argument("--stages", nargs="+",
                       help="Run specific stages only (e.g., --stages features models_baseline)")
    args = parser.parse_args()

    # Determine which stages to run
    stages_to_run = STAGES

    if args.skip_free_data:
        stages_to_run = [(name, module, func) for name, module, func in STAGES
                        if name != "free_data_ingestion"]
        print(json.dumps({"note": "Skipping free data ingestion", "ts": datetime.utcnow().isoformat()}))

    if args.stages:
        requested_stages = set(args.stages)
        stages_to_run = [(name, module, func) for name, module, func in stages_to_run
                        if name in requested_stages]
        print(json.dumps({"note": f"Running selected stages: {args.stages}",
                         "ts": datetime.utcnow().isoformat()}))

    if not stages_to_run:
        print(json.dumps({"error": "No stages to run", "ts": datetime.utcnow().isoformat()}))
        return 1

    # Execute pipeline stages
    print(json.dumps({"status": "starting", "pipeline": "institutional_grade",
                     "stages": len(stages_to_run), "ts": datetime.utcnow().isoformat()}))

    success_count = 0
    for (name, module_name, func_name) in stages_to_run:
        try:
            run_stage(name, module_name, func_name)
            success_count += 1
        except Exception as e:
            print(json.dumps({"error": f"Pipeline failed at stage {name}: {str(e)}",
                             "completed_stages": success_count,
                             "ts": datetime.utcnow().isoformat()}))
            return 1

    print(json.dumps({"status": "completed", "pipeline": "institutional_grade",
                     "completed_stages": success_count, "total_stages": len(stages_to_run),
                     "ts": datetime.utcnow().isoformat()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
