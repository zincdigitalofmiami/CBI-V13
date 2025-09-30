#!/usr/bin/env python3
"""
Run the full pipeline chain end-to-end:
- ingest → features → models_baseline → models_nn → econ_impact

Usage:
  python run_all.py

Exits non-zero if any stage fails. Prints JSON status lines per stage.
"""
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime

STAGES = [
    ("ingest", "pipelines.ingest", "main"),
    ("features", "pipelines.features", "run"),
    ("models_baseline", "pipelines.models_baseline", "run"),
    ("models_nn", "pipelines.models_nn", "run"),
    ("econ_impact", "pipelines.econ_impact", "run"),
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
    for (name, module_name, func_name) in STAGES:
        try:
            run_stage(name, module_name, func_name)
        except Exception:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
