#!/usr/bin/env python3
"""
Audit repository and data readiness for local go-live.

Outputs a human-readable summary and writes audit_status.json at repo root.

Checks:
- Python env (import key modules)
- DB connectivity
- Presence and row counts for key tables
- Presence of expected Streamlit pages and pipeline scripts
- Hints for next actions
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Dict, Any


# Local imports
try:
    from db.session import ping, get_engine
except Exception:
    ping = None  # type: ignore
    get_engine = None  # type: ignore


EXPECTED_PAGES = [
    "app/pages/0_🩺_Health.py",
    "app/pages/1_📊_Sentiment_&_Market_Intelligence.py",
    "app/pages/2_🗺️_Strategy_Lab_&_Supply_Chain_Map.py",
    "app/pages/3_🔧_Admin.py",
    "app/pages/4_🌐_Trade_Intelligence.py",
]

EXPECTED_PIPELINES = [
    "pipelines/ingest.py",
    "pipelines/features.py",
    "pipelines/models_baseline.py",
    "pipelines/models_nn.py",
    "pipelines/econ_impact.py",
]

KEY_TABLES = {
    "curated.prices_daily": "SELECT COUNT(*) AS n FROM curated.prices_daily",
    "features.technical": "SELECT COUNT(*) AS n FROM features.technical",
    "forecasts.price_baseline": "SELECT COUNT(*) AS n FROM forecasts.price_baseline",
    "app.signals_today": "SELECT COUNT(*) AS n FROM app.signals_today",
    # Trade Intelligence (optional)
    "curated.trade_policy_probs": "SELECT COUNT(*) AS n FROM curated.trade_policy_probs",
    "curated.trade_timeline": "SELECT COUNT(*) AS n FROM curated.trade_timeline",
    "curated.congress_votes": "SELECT COUNT(*) AS n FROM curated.congress_votes",
    "curated.country_intel": "SELECT COUNT(*) AS n FROM curated.country_intel",
}


def check_fs(paths):
    out = {}
    for p in paths:
        out[p] = os.path.exists(p)
    return out


def check_db_tables():
    if ping is None or get_engine is None:
        return {"ok": False, "details": "db.session not importable", "tables": {}}
    ok = False
    details = ""
    tables: Dict[str, Any] = {}
    try:
        ok = bool(ping())
    except Exception as e:
        details = f"Ping error: {e}"
        ok = False
    if not ok:
        return {"ok": False, "details": details or "Database not reachable", "tables": {}}
    try:
        engine = get_engine()
        # lazy import of sqlalchemy.text to avoid static analyzer issues if not installed
        from importlib import import_module
        try:
            sqlalchemy_mod = import_module("sqlalchemy")  # type: ignore
            _text = getattr(getattr(sqlalchemy_mod, "sql"), "text")  # type: ignore[attr-defined]
        except Exception as e:
            return {"ok": False, "details": f"sqlalchemy unavailable: {e}", "tables": {}}
        with engine.begin() as conn:
            for tbl, q in KEY_TABLES.items():
                try:
                    n = conn.execute(_text(q)).scalar()
                    tables[tbl] = int(n or 0)
                except Exception as e:  # table may not exist yet
                    tables[tbl] = f"ERR: {e}"  # include reason
        return {"ok": True, "details": "Connected", "tables": tables}
    except Exception as e:
        return {"ok": False, "details": str(e), "tables": {}}


def main() -> int:
    report: Dict[str, Any] = {
        "ts": datetime.utcnow().isoformat(),
        "env": {
            "python": os.environ.get("PYTHON_VERSION", "unknown"),
            "database_url_set": bool(os.getenv("DATABASE_URL")),
            "use_iam_auth": os.getenv("USE_IAM_AUTH", "false").lower() in ("1", "true", "yes"),
        },
        "pages_present": check_fs(EXPECTED_PAGES),
        "pipelines_present": check_fs(EXPECTED_PIPELINES),
    }

    db_status = check_db_tables()
    report["db"] = db_status

    # Hints
    hints = []
    if not any(report["pages_present"].values()):
        hints.append("No Streamlit pages found — check working directory.")
    if not report["env"]["database_url_set"] and not report["env"]["use_iam_auth"]:
        hints.append("Set DATABASE_URL (include ?sslmode=require if needed) or USE_IAM_AUTH=true with Cloud SQL vars.")
    if db_status.get("ok"):
        t = db_status.get("tables", {})
        if t.get("curated.prices_daily", 0) == 0:
            hints.append("Run pipelines/ingest.py to populate curated.prices_daily.")
        if t.get("features.technical", 0) == 0:
            hints.append("Run pipelines/features.py to populate features.technical.")
        if t.get("forecasts.price_baseline", 0) == 0:
            hints.append("Run pipelines/models_baseline.py to populate forecasts.price_baseline.")
        if t.get("app.signals_today", 0) == 0:
            hints.append("Run pipelines/econ_impact.py to write app.signals_today.")
    else:
        hints.append("Database not reachable — check .env and apply schema with make init-db.")

    report["hints"] = hints

    # Write JSON
    with open("audit_status.json", "w") as f:
        json.dump(report, f, indent=2)

    # Human-readable output
    print("== Go-Live Audit ==")
    print(f"Time: {report['ts']}")
    print(f"DB reachable: {db_status.get('ok')} — {db_status.get('details')}")
    print("Pages:")
    for p, ok in report["pages_present"].items():
        print(f"  - {p}: {'OK' if ok else 'MISSING'}")
    print("Pipelines:")
    for p, ok in report["pipelines_present"].items():
        print(f"  - {p}: {'OK' if ok else 'MISSING'}")
    print("Tables (counts or ERR):")
    for tbl, cnt in report.get("db", {}).get("tables", {}).items():
        print(f"  - {tbl}: {cnt}")
    if hints:
        print("\nHints:")
        for h in hints:
            print(f"- {h}")
    print("\nWrote audit_status.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
