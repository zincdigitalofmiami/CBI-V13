#!/usr/bin/env python3
"""
DEPRECATED: Neon is no longer part of this project's scope.

This script was previously used to provision Neon Postgres via the Neon API.
It is retained only for historical context and should not be used.

Use your chosen managed Postgres provider's console or Terraform to create a database,
then set DATABASE_URL in your environment and apply sql/schema.sql.
"""
import argparse
import os
import sys
import time
import requests

API_BASE = "https://api.neon.tech/v2"


def neon_request(method: str, path: str, **kwargs):
    api_key = os.getenv("NEON_API_KEY")
    if not api_key:
        raise SystemExit("NEON_API_KEY not set in environment")
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {api_key}"
    headers["Accept"] = "application/json"
    if method.upper() in ("POST", "PATCH", "PUT"):
        headers.setdefault("Content-Type", "application/json")
    resp = requests.request(method, f"{API_BASE}{path}", headers=headers, timeout=30, **kwargs)
    if not resp.ok:
        raise SystemExit(f"Neon API error {resp.status_code}: {resp.text}")
    return resp.json()


def create_project(name: str, region: str):
    # See Neon API docs for payload details
    payload = {
        "project": {
            "name": name,
            "region_id": region,
        }
    }
    data = neon_request("POST", "/projects", json=payload)
    return data["project"]


def get_connection_uris(project_id: str):
    data = neon_request("GET", f"/projects/{project_id}")
    # Many Neon responses include connection_uris in roles/endpoints.
    # Try to fetch endpoints listing with connection URIs.
    endpoints = neon_request("GET", f"/projects/{project_id}/endpoints")
    roles = neon_request("GET", f"/projects/{project_id}/roles")
    databases = neon_request("GET", f"/projects/{project_id}/databases")
    return {
        "project": data.get("project", {}),
        "endpoints": endpoints.get("endpoints", []),
        "roles": roles.get("roles", []),
        "databases": databases.get("databases", []),
    }


def create_role_db(project_id: str, role: str, database: str):
    neon_request("POST", f"/projects/{project_id}/roles", json={"role": {"name": role}})
    neon_request("POST", f"/projects/{project_id}/databases", json={"database": {"name": database, "owner_name": role}})


def pick_endpoint(endpoints):
    # Prefer read-write endpoint
    for ep in endpoints:
        if ep.get("type") == "read_write":
            return ep
    return endpoints[0] if endpoints else None


def build_sqlalchemy_url(endpoint, role: str, database: str):
    # Neon endpoint has fields like host, port. Role requires password reset to get password.
    host = endpoint.get("host") or endpoint.get("hostname")
    port = endpoint.get("port", 5432)
    user = role
    # For security, we do not attempt to pull passwords via API. Ask user to set a password in the Neon console.
    password = os.getenv("NEON_DB_PASSWORD", "<set-password-in-neon-console>")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}?sslmode=require"


def main():
    print("DEPRECATED: Neon is no longer in the project scope. Use your managed Postgres provider instead.")
    sys.exit(1)
    p = argparse.ArgumentParser()
    p.add_argument("--project-name", required=True)
    p.add_argument("--region", default="aws-us-east-1", help="Neon region id (e.g., aws-us-east-1)")
    p.add_argument("--role", default="app")
    p.add_argument("--database", default="cbi")
    args = p.parse_args()

    print("Creating Neon project...", flush=True)
    project = create_project(args.project_name, args.region)
    project_id = project["id"]
    print(f"Project created: {project_id}")

    # Neon can take a few seconds to bring endpoints up
    time.sleep(5)

    print("Creating role and database...", flush=True)
    create_role_db(project_id, args.role, args.database)

    print("Fetching connection details...", flush=True)
    details = get_connection_uris(project_id)
    endpoint = pick_endpoint(details.get("endpoints", []))
    if not endpoint:
        print("No endpoints found yet; retry in a few seconds from now or check the Neon console.")
        sys.exit(1)

    db_url = build_sqlalchemy_url(endpoint, args.role, args.database)
    print("\nSUCCESS — Paste this into your .env as DATABASE_URL:")
    print(db_url)
    print("\nIMPORTANT:")
    print("- Set or reset the password for role '" + args.role + "' in the Neon console, or set NEON_DB_PASSWORD before running this script.")
    print("- Ensure sslmode=require remains in the URL.")


if __name__ == "__main__":
    main()
