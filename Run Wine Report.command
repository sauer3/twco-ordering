#!/bin/bash
# Double-click this file to generate the wine reorder report and open it.
# No Terminal commands needed -- it runs everything and opens the spreadsheet.

# Always work from the folder this file lives in.
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

echo "Transparent Wine Co. — generating reorder report..."
echo

# Find conda (a double-clicked .command doesn't load your shell profile, so we
# look in the usual install locations).
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
    echo "ERROR: Could not find conda. Is Miniconda/Anaconda installed?"
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

# Name the output with today's date so reports don't overwrite each other.
TODAY="$(date +%Y-%m-%d)"
OUT="output/reorder_report_${TODAY}.xlsx"

python velocity_report.py --output "$OUT"
STATUS=$?

echo
if [ $STATUS -eq 0 ] && [ -f "$OUT" ]; then
    echo "Done. Opening $OUT ..."
    open "$OUT"
else
    echo "Something went wrong (the report was not created). See messages above."
    echo "Press any key to close."
    read -n 1 -s
fi
