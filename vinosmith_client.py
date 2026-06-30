#!/usr/bin/env python3
"""
Vinosmith API client.

A thin read-only wrapper over the Vinosmith distributor API, exposing just the
three things the reorder report needs:

    - get_wines()            -> the wine catalog (for created_at, name, unit_set)
    - get_inventory()        -> current on_hand / on_order per wine
    - get_supplier_orders()  -> dated sales line items over an arbitrary window

Auth follows the same pattern as vinosmith_probe.py: a bearer token read from
VINOSMITH_TOKEN in a local .env file.

Notes on the API (discovered empirically — see the probe):
    - /wines and /inventory return their full list in a single call; there is no
      working pagination param.
    - /supplier_orders filters by `delivery_at` and caps each response at roughly
      a 60-day window: if you ask for a wider range the server silently clamps the
      start date. To cover a longer window we walk backward in <=55-day chunks and
      concatenate. Each chunk returns its whole list at once (no pagination).
"""

import os
import sys
import time
from datetime import date, timedelta

import requests
from dotenv import load_dotenv

BASE_URL = "https://vinosmith.com/api/distributor"
TIMEOUT_SEC = 120

# The server clamps /supplier_orders to ~60 days. Stay comfortably under that.
CHUNK_DAYS = 55
# Be polite between chunked requests.
SLEEP_BETWEEN_CHUNKS_SEC = 0.4


def get_token():
    """Read VINOSMITH_TOKEN from .env / environment, matching the probe."""
    load_dotenv()
    token = os.environ.get("VINOSMITH_TOKEN", "").strip()
    if not token:
        print("ERROR: VINOSMITH_TOKEN is not set.", file=sys.stderr)
        print("Create a .env file in this directory containing:", file=sys.stderr)
        print("  VINOSMITH_TOKEN=your-token-here", file=sys.stderr)
        sys.exit(1)
    return token


class VinosmithClient:
    def __init__(self, token=None):
        self.token = token or get_token()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
            }
        )

    def _get(self, path, params=None):
        url = BASE_URL + path
        r = self.session.get(url, params=params or {}, timeout=TIMEOUT_SEC)
        r.raise_for_status()
        return r.json()

    def get_wines(self):
        """Return the list of wine records (catalog)."""
        body = self._get("/wines")
        return body.get("data", {}).get("wines", [])

    def get_inventory(self):
        """Return the list of inventory records (one per wine/warehouse)."""
        body = self._get("/inventory")
        return body.get("data", {}).get("inventory", [])

    def get_supplier_orders(self, start_date, end_date, verbose=True):
        """
        Return a flat list of supplier-order records whose delivery_at falls in
        [start_date, end_date]. Walks backward in <=CHUNK_DAYS chunks because the
        server caps each request at ~60 days.

        start_date / end_date are datetime.date objects.
        """
        orders = []
        seen_ids = set()
        chunk_end = end_date
        while chunk_end >= start_date:
            chunk_start = max(start_date, chunk_end - timedelta(days=CHUNK_DAYS))
            params = {
                "delivery_start_date": chunk_start.isoformat(),
                "delivery_end_date": chunk_end.isoformat(),
            }
            body = self._get("/supplier_orders", params=params)
            rows = body.get("data", {}).get("supplier_orders", [])
            new = 0
            for row in rows:
                oid = row.get("supplier_order", {}).get("id")
                # Dedupe across chunk boundaries (chunks share an edge day).
                if oid is not None and oid in seen_ids:
                    continue
                if oid is not None:
                    seen_ids.add(oid)
                orders.append(row)
                new += 1
            if verbose:
                print(
                    f"  supplier_orders {chunk_start} .. {chunk_end}: "
                    f"{len(rows)} rows ({new} new)"
                )
            # Step back one day past the chunk start to avoid re-fetching the edge.
            chunk_end = chunk_start - timedelta(days=1)
            time.sleep(SLEEP_BETWEEN_CHUNKS_SEC)
        return orders
