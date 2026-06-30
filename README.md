# TWco Ordering

Tooling to help decide when to order wine from European suppliers, given a
12–16 week lead time from order to receipt.

## The problem

Vinosmith's velocity report (`# Qty Sold / month` over the trailing 12 months,
plus an "Average Qty Sold / Interval" and "Estimated Intervals Supply
Remaining") doesn't account for months when a wine was out of stock. The
reported average divides total sales by 12 regardless of how many of those
months the wine was actually available to sell.

Because each vintage is a new SKU and most wines have at least some out-of-stock
period during the trailing year (either before the vintage arrived or after it
sold through), the "Average Qty Sold / Interval" column is systematically too
low, and the "Estimated Intervals Supply Remaining" column is therefore
systematically too high. With a 12–16 week lead time from Europe, being
optimistic about runway is exactly the wrong direction to be wrong.

## What this project does

Pulls data from the Vinosmith API and produces a corrected reorder report:

- True monthly velocity (computed only over months the wine was in stock)
- Realistic months-of-supply remaining
- Inclusion of on-order (in-transit) quantities
- A reorder flag for wines that need attention given the lead time

## Project status

In progress. Currently at the **probe** stage — confirming what the Vinosmith
API actually exposes for our distributor account before building the full
pipeline.

## Setup (one time)

```bash
# Create and activate the conda env
conda create -n twco-vinosmith python=3.12 -y
conda activate twco-vinosmith

# Install dependencies
pip install -r requirements.txt

# Set up your token
cp .env.example .env
# then edit .env and paste your real token after the = sign
```

## Run the probe

```bash
conda activate twco-vinosmith
python vinosmith_probe.py
```

Output goes to `./output/probe/`. Open `_summary.json` to see which endpoints
returned data and which fields each record contains. This tells us which
endpoints to use for the real pipeline.

## File layout

```
twco-ordering/
├── .env                   # your token (gitignored, never committed)
├── .env.example           # template — safe to commit
├── .gitignore
├── README.md              # this file
├── requirements.txt
├── vinosmith_probe.py     # probe stage: maps the API
├── vinosmith_client.py    # (todo) reusable API client
├── velocity_report.py     # (todo) the corrected reorder report
└── output/                # generated output (gitignored)
```

## Vinosmith API reference

https://vinosmith.readme.io/reference/authentication-1

Base URL: `https://vinosmith.com/api/distributor`
Auth: `Authorization: Bearer <token>` header
