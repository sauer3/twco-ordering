# Setup on a new Mac (from scratch)

This walks through getting the wine reorder report running on a Mac that has
**no developer tools installed**. You'll only need Terminal for a few copy-paste
commands. Terminal is in **Applications → Utilities → Terminal**.

Do the steps in order. Where a command is shown in a grey box, copy the whole
line, paste it into Terminal, and press Return.

---

## 1. Install Git

In Terminal, run:

```
xcode-select --install
```

A window pops up — click **Install** and wait for it to finish (a few minutes).
This gives you `git`. If it says it's "already installed," you're fine.

## 2. Install Miniconda (this also installs Python)

First find out which chip the Mac has: **Apple menu  → About This Mac → Chip**.

- If it says **Apple M1/M2/M3** (Apple Silicon), download:
  https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.pkg
- If it says **Intel**, download:
  https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.pkg

Double-click the downloaded `.pkg` and click through the installer (the defaults
are fine). When it's done, **close Terminal and open a new Terminal window** so
the `conda` command becomes available.

## 3. Download the project (clone the repo)

```
cd ~/Documents
git clone https://github.com/sauer3/twco-ordering.git
cd twco-ordering
```

(You can use a different folder than `~/Documents` if you prefer — just `cd`
there first.)

## 4. Create the Python environment and install dependencies

```
conda create -n twco-vinosmith python=3.12 -y
conda activate twco-vinosmith
pip install -r requirements.txt
```

## 5. Create the `.env` file (your private settings)

The `.env` file holds the Vinosmith token and email settings. It is **not** in
the repo (it's private), so you create it from the template:

```
cp .env.example .env
open -e .env
```

That opens `.env` in TextEdit. Fill in:

- **`VINOSMITH_TOKEN`** — paste the same token from Stephanie's `.env` (the
  Vinosmith distributor API token).
- **The `SMTP_*` and `EMAIL_*` lines** — only needed if you want the weekly
  emailed report (Step 7). For Gmail, `SMTP_PASSWORD` must be a Google **App
  Password** (not the normal password) — create one at
  https://myaccount.google.com/apppasswords . Put the recipients (his address +
  the business partner's) in `EMAIL_TO`, separated by commas.

Save and close TextEdit. If you're not setting up email yet, you can leave the
`SMTP_*` lines as-is for now.

## 6. Run the report on demand

Open the `twco-ordering` folder in Finder. **Right-click** `Run Wine Report.command`
→ **Open** → **Open** again (this first-time step clears macOS's "unidentified
developer" warning; after that you can just double-click it).

It generates the report and opens the spreadsheet automatically. Output lands in
the `output/` folder, named with the date.

## 7. (Optional) Turn on the weekly emailed report

Make sure the email settings in `.env` are filled in (Step 5), then in Finder
**right-click → Open** `Install Weekly Schedule.command`. It schedules the report
to be generated and emailed **every Monday at 8:00 AM**.

- The Mac must be awake at that time; if it's asleep, macOS runs the job at the
  next wake-up.
- To stop it later, open `Uninstall Weekly Schedule.command` the same way.

---

## Getting updates later

When the tool is improved, pull the latest version:

```
cd ~/Documents/twco-ordering
git pull
```

Your `.env` and the `output/` folder are left untouched.

**Do not delete `inventory_history.csv`.** It's the running record of what was in
stock each week and makes the velocity numbers more accurate over time.

## Quick troubleshooting

- **"conda: command not found"** — close Terminal and open a new window (Step 2),
  or you missed the Miniconda install.
- **The `.command` file won't open / "unidentified developer"** — right-click the
  file and choose **Open** instead of double-clicking the first time.
- **"VINOSMITH_TOKEN is not set"** — the `.env` file is missing or the token line
  is blank (Step 5).
