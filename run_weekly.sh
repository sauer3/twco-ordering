#!/bin/bash
# Wrapper used by the weekly scheduled job (launchd). Generates the report and
# emails it. Self-locating and conda-detecting so launchd can run it cleanly.
# Output is appended to output/weekly_run.log.

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
mkdir -p output

{
    echo "===== $(date) : weekly run starting ====="

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
        echo "ERROR: conda not found; cannot run."
        exit 1
    fi

    # shellcheck disable=SC1090
    source "$CONDA_SH"
    conda activate twco-vinosmith || { echo "ERROR: env activate failed"; exit 1; }

    TODAY="$(date +%Y-%m-%d)"
    OUT="output/reorder_report_${TODAY}.xlsx"
    python velocity_report.py --output "$OUT" --email
    echo "===== $(date) : weekly run finished (exit $?) ====="
    echo
} >> output/weekly_run.log 2>&1
