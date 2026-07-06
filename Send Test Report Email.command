#!/bin/bash
# Double-click to run the report AND email it right now (same thing the weekly
# schedule does, but immediately). Use this to verify the email settings work
# without waiting for Monday.

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

echo "Generating the report and emailing it now..."
echo

CONDA_SH=""
for base in "$HOME/miniconda3" "$HOME/anaconda3" "$HOME/opt/miniconda3" \
            "$HOME/opt/anaconda3" "/opt/miniconda3" "/opt/anaconda3" \
            "/opt/homebrew/Caskroom/miniconda/base"; do
    if [ -f "$base/etc/profile.d/conda.sh" ]; then
        CONDA_SH="$base/etc/profile.d/conda.sh"
        break
    fi
done

if [ -z "$CONDA_SH" ]; then
    echo "ERROR: Could not find conda. Is Miniconda installed?"
    echo "Press any key to close."
    read -n 1 -s
    exit 1
fi

# shellcheck disable=SC1090
source "$CONDA_SH"
conda activate twco-vinosmith || {
    echo "ERROR: Could not activate the 'twco-vinosmith' environment."
    echo "Press any key to close."
    read -n 1 -s
    exit 1
}

TODAY="$(date +%Y-%m-%d)"
OUT="output/reorder_report_${TODAY}.xlsx"

python velocity_report.py --output "$OUT" --email
STATUS=$?

echo
if [ $STATUS -eq 0 ]; then
    echo "Success — check the inbox(es) in EMAIL_TO for the report."
else
    echo "Something failed — read the error above. Most common causes:"
    echo "  - .env is missing the SMTP_/EMAIL_ settings"
    echo "  - SMTP_PASSWORD is not a valid Gmail App Password"
fi
echo "Press any key to close."
read -n 1 -s
