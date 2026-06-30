#!/usr/bin/env python3
"""
Vinosmith API probe.

Goal: hit each endpoint we *might* need to solve the OOS-aware velocity problem,
save the raw responses to disk, and print a short summary so we can see what's
actually available in your account.

This script does NOT modify anything. Every call is a GET. The script writes
the responses to ./output/probe/ so we can inspect them after.

Usage:
    # First, put your token in a .env file in this directory:
    #   VINOSMITH_TOKEN=your-token-here
    #
    # Then run:
    python3 vinosmith_probe.py
"""

import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

BASE_URL = "https://vinosmith.com/api/distributor"
OUTPUT_DIR = Path("./output/probe")
TIMEOUT_SEC = 30

# Endpoints to probe. Each entry: (label, path, query_params_to_try).
# We try a small page size where possible so we don't pull the whole catalog
# during a probe. If a param isn't supported, the API will just ignore it.
ENDPOINTS = [
    ("countries",            "/countries",            {}),
    ("users",                "/users",                {}),
    ("accounts",             "/accounts",             {"per_page": 5, "page": 1, "limit": 5}),
    ("wines",                "/wines",                {"per_page": 5, "page": 1, "limit": 5}),
    ("inventory",            "/inventory",            {"per_page": 5, "page": 1, "limit": 5}),
    ("producers",            "/producers",            {"per_page": 5, "page": 1, "limit": 5}),
    ("regions",              "/regions",              {}),
    ("supplier_orders",      "/supplier_orders",      {"per_page": 5, "page": 1, "limit": 5}),
    ("purchase_orders",      "/purchase_orders",      {"per_page": 5, "page": 1, "limit": 5}),
    ("tastings",             "/tastings",             {"per_page": 5, "page": 1, "limit": 5}),
    ("allocations",          "/allocations",          {"per_page": 5, "page": 1, "limit": 5}),
    ("account_contacts",     "/account_contacts",     {"per_page": 5, "page": 1, "limit": 5}),
    # Long shots: these aren't documented under Distributor but might exist.
    # If they 404, that's useful information.
    ("depletions_guess",     "/depletions",           {"per_page": 5}),
    ("orders_guess",         "/orders",               {"per_page": 5}),
    ("invoices_guess",       "/invoices",             {"per_page": 5}),
    ("inventory_transactions_guess", "/inventory_transactions", {"per_page": 5}),
]


def get_token():
    load_dotenv()  # Reads .env from current directory
    token = os.environ.get("VINOSMITH_TOKEN", "").strip()
    if not token:
        print("ERROR: VINOSMITH_TOKEN is not set.", file=sys.stderr)
        print("Create a .env file in this directory containing:", file=sys.stderr)
        print("  VINOSMITH_TOKEN=your-token-here", file=sys.stderr)
        sys.exit(1)
    return token


def probe(label, path, params, headers):
    url = BASE_URL + path
    full_url = url + ("?" + urlencode(params) if params else "")
    result = {
        "label": label,
        "url": full_url,
        "status": None,
        "ok": False,
        "error": None,
        "top_level_keys": None,
        "record_count": None,
        "sample_record": None,
        "all_response": None,
    }
    try:
        r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT_SEC)
        result["status"] = r.status_code
        if r.status_code == 200:
            result["ok"] = True
            try:
                body = r.json()
                result["all_response"] = body
                if isinstance(body, dict):
                    result["top_level_keys"] = list(body.keys())
                    # Vinosmith pattern from docs: {"status": "ok", "data": {...}}
                    data = body.get("data", body)
                    if isinstance(data, dict):
                        # Find the first list inside data and use that as "records"
                        for k, v in data.items():
                            if isinstance(v, list):
                                result["record_count"] = len(v)
                                if v:
                                    result["sample_record"] = v[0]
                                break
                    elif isinstance(data, list):
                        result["record_count"] = len(data)
                        if data:
                            result["sample_record"] = data[0]
            except ValueError:
                result["error"] = "Response was not JSON. First 500 chars: " + r.text[:500]
        else:
            # Capture body for non-200 so we can see error messages
            result["error"] = r.text[:500]
    except requests.RequestException as e:
        result["error"] = f"Request failed: {e}"
    return result


def main():
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Probing {len(ENDPOINTS)} endpoints against {BASE_URL}")
    print(f"Writing full responses to: {OUTPUT_DIR.resolve()}")
    print("-" * 70)

    summary_rows = []
    for label, path, params in ENDPOINTS:
        print(f"\n[{label}] GET {path}  params={params or '{}'}")
        result = probe(label, path, params, headers)

        # Save full response (or error) to a file
        out_path = OUTPUT_DIR / f"{label}.json"
        try:
            with open(out_path, "w") as f:
                json.dump(result, f, indent=2, default=str)
        except Exception as e:
            print(f"  (could not write {out_path}: {e})")

        if result["ok"]:
            keys = result["top_level_keys"]
            n = result["record_count"]
            print(f"  ✓ 200 OK   top-level keys: {keys}   record count in first list: {n}")
            if result["sample_record"] is not None:
                sr = result["sample_record"]
                if isinstance(sr, dict):
                    print(f"  sample record fields: {list(sr.keys())}")
                else:
                    print(f"  sample record: {str(sr)[:200]}")
        else:
            print(f"  ✗ status={result['status']}   error: {(result['error'] or '')[:200]}")

        summary_rows.append({
            "label": label,
            "path": path,
            "status": result["status"],
            "ok": result["ok"],
            "record_count": result["record_count"],
            "top_level_keys": result["top_level_keys"],
            "sample_fields": list(result["sample_record"].keys()) if isinstance(result["sample_record"], dict) else None,
        })

        # Be polite to the API
        time.sleep(0.4)

    # Write a summary file too
    summary_path = OUTPUT_DIR / "_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary_rows, f, indent=2, default=str)

    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  Reachable (200 OK): {sum(1 for r in summary_rows if r['ok'])}")
    print(f"  Failed:             {sum(1 for r in summary_rows if not r['ok'])}")
    print(f"\nAll responses saved in: {OUTPUT_DIR.resolve()}")
    print("Open _summary.json for a high-level view of what's available.")


if __name__ == "__main__":
    main()
