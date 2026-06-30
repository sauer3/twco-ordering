# Kickoff prompt for Claude Code

Open Claude Code in this project folder, then paste everything between the
horizontal rules below as your first message.

Before you paste, make sure you've already:
1. Run `conda activate twco-vinosmith` so the right environment is active
2. Created `.env` from `.env.example` and put your real token in it
3. (Optional) Run `python vinosmith_probe.py` once so the probe output exists

---

I'm building a tool to help our wine import business decide when to reorder
wine from European suppliers. Lead time from order to receipt is 12–16 weeks.

## The core problem we're solving

Our existing velocity report from Vinosmith (a wine distribution platform)
divides each wine's total trailing-12-month sales by 12 to compute an average
monthly sales rate. The problem: most of our SKUs were out of stock for part
of those 12 months (each vintage is a new SKU, so there's almost always either
a "vintage not arrived yet" gap at the start of the year, a "sold through"
gap at the end, or both). The reported average is therefore biased low, and
the derived "months of supply remaining" is biased high — telling us we have
more runway than we actually do.

## What I want this tool to do

1. Pull data from the Vinosmith API for our distributor account
2. Compute a true monthly velocity using only months the wine was actually
   in stock
3. Combine that with current on-hand inventory and on-order (in-transit)
   quantities
4. Produce an Excel report flagging wines that need to be reordered given
   the 12–16 week lead time, plus a configurable safety buffer

## What's already in place

This folder contains:

- `vinosmith_probe.py` — a read-only probe script that hits ~16 candidate
  endpoints on the Vinosmith API and dumps the response shapes to
  `output/probe/`. Read the script to understand the auth pattern and the
  endpoints we know about.
- `README.md` — full project context
- `requirements.txt` — `requests`, `pandas`, `openpyxl`, `python-dotenv`
- `.env.example` — template for the API token
- A conda environment called `twco-vinosmith` (Python 3.12) with deps installed

The original Vinosmith velocity CSV (the broken version we're replacing) is
available as a sample I can share — ask if you want to see its structure.

## Vinosmith API basics

- Docs: https://vinosmith.readme.io/reference/authentication-1
- Base URL: `https://vinosmith.com/api/distributor`
- Auth: `Authorization: Bearer <token>` header
- Documented distributor endpoints include: `/wines`, `/inventory`,
  `/producers`, `/regions`, `/supplier_orders`, `/purchase_orders`,
  `/tastings`, `/allocations`, `/accounts`, `/account_contacts`,
  `/countries`, `/users`, and per-wine endpoints like
  `/wines/<id>/inventory` and `/wines/<id>/pre_arrivals`.
- The docs do NOT clearly show a distributor-side endpoint for dated sales
  line items or for inventory transaction history. The probe script tries
  a few undocumented guesses (`/depletions`, `/orders`, `/invoices`,
  `/inventory_transactions`) so we can confirm whether any of those exist.

## How I'd like to proceed

Step 1: Look at the probe output in `output/probe/` (specifically
`_summary.json` and the per-endpoint files). Help me understand:
  - Which endpoints actually returned data
  - For each useful endpoint, what fields its records contain
  - Whether any endpoint provides dated sales data or historical inventory
    (the two things we'd need to perfectly identify out-of-stock months)
  - What date filtering / pagination parameters the API supports
  - If the probe hasn't been run yet, walk me through running it first

Step 2: Based on what's actually available, propose a methodology for
computing true monthly velocity. Two paths I can imagine, depending on what
the API gives us:
  - Best case: dated sales + dated inventory history → directly identify
    out-of-stock months
  - Fallback: only aggregated monthly sales available → infer out-of-stock
    months by stripping leading and trailing zero-sales months from each
    wine's 12-month sales series (this captures the "vintage arrived
    mid-year" and "sold through mid-year" cases, which are the dominant
    failure modes)

Step 3: Once we agree on the methodology, build it as a clean Python module
(`vinosmith_client.py` for the API layer, `velocity_report.py` for the
analysis), with an Excel output that's easy for my husband to scan when
deciding what to reorder.

Don't write any code yet. Start by reading the probe output (or telling me
to run the probe if it hasn't been run), then we'll discuss what we found
and decide on the approach together.
