#!/usr/bin/env python3
"""
Repo/App connection diagnostics for CBI-V13.

Runs a series of checks and prints results with clear next actions.
Usage:
  python scripts/diagnose.py

Or via Makefile:
  make diagnose
"""
from __future__ import annotations

import json
import os
import platform
import socket
import subprocess
import sys
from typing import Any, Dict

import importlib

RESULTS: Dict[str, Any] = {"checks": []}


def add_result(name: str, ok: bool, details: str = "", extra: Dict[str, Any] | None = None) -> None:
    RESULTS["checks"].append({"name": name, "ok": ok, "details": details, **(extra or {})})


def check_python_env() -> None:
    required = ["streamlit", "sqlalchemy", "psycopg2", "pandas", "requests"]
    missing = []
    for mod in required:
        try:
            importlib.import_module(mod)
        except Exception:
            missing.append(mod)
    ok = len(missing) == 0
    add_result(
        "python_env",
        ok,
        details=("All required packages available" if ok else f"Missing: {', '.join(missing)}"),
        extra={
            "python": sys.version.split(" ")[0],
            "platform": platform.platform(),
        },
    )


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def check_git() -> None:
    try:
        inside = run(["git", "rev-parse", "--is-inside-work-tree"]).stdout.strip()
        if inside != "true":
            add_result("git_repo", False, "Not inside a git working tree.")
            return
        remotes = run(["git", "remote", "-v"]).stdout.strip()
        ok = bool(remotes)
        add_result("git_remote", ok, details=(remotes or "No remotes configured."))
        if ok:
            fetch = run(["git", "fetch", "--dry-run"])  # dry-run to test connectivity
            ok_fetch = fetch.returncode == 0
            add_result(
                "git_fetch",
                ok_fetch,
                details=("OK" if ok_fetch else f"Fetch error: {fetch.stderr.strip() or fetch.stdout.strip()}"),
            )
    except FileNotFoundError:
        add_result("git_cli", False, "git CLI not found in PATH.")


def check_network() -> None:
    # DNS
    try:
        socket.gethostbyname("github.com")
        dns_ok = True
    except Exception as e:
        dns_ok = False
        dns_err = str(e)
    add_result("dns_github", dns_ok, details=("OK" if dns_ok else dns_err))

    # HTTPS
    try:
        import requests

        r = requests.get("https://api.github.com", timeout=10)
        https_ok = r.ok
        details = f"HTTP {r.status_code}"
    except Exception as e:
        https_ok = False
        details = str(e)
    add_result("https_outbound", https_ok, details)


def check_db() -> None:
    from db.session import get_engine

    db_url = os.getenv("DATABASE_URL", "")
    use_iam = os.getenv("USE_IAM_AUTH", "false").lower() in ("1", "true", "yes")

    hints = []
    if ("neon.tech" in db_url or "neon" in db_url) and "sslmode=" not in db_url:
        hints.append("Add ?sslmode=require to your Neon DATABASE_URL")
    if use_iam and not os.getenv("CLOUD_SQL_CONNECTION_NAME"):
        hints.append("Set CLOUD_SQL_CONNECTION_NAME for Google Cloud SQL IAM auth")

    mode = "DATABASE_URL" if db_url else ("CloudSQL_IAM" if use_iam else "unconfigured")

    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        ok = True
        details = f"Connected via {mode}"
    except Exception as e:
        ok = False
        details = f"DB connection failed via {mode}: {e}"
    extra = {"mode": mode}
    if hints:
        extra["hints"] = hints
    add_result("database", ok, details, extra)


def check_permissions() -> None:
    cwd = os.getcwd()
    writable = os.access(cwd, os.W_OK)
    add_result("filesystem_writable", writable, details=f"cwd={cwd}")


def main() -> int:
    check_python_env()
    check_git()
    check_network()
    check_db()
    check_permissions()

    # Print human-readable summary
    print("\n== CBI-V13 Diagnostics ==")
    failures = 0
    for c in RESULTS["checks"]:
        status = "OK" if c["ok"] else "FAIL"
        print(f"- {c['name']}: {status} — {c.get('details','')}")
        if not c["ok"]:
            failures += 1
    print("\nJSON:")
    print(json.dumps(RESULTS, indent=2))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
