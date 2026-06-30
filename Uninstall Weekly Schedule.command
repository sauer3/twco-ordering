#!/bin/bash
# Double-click to stop the weekly emailed report.

LABEL="com.twco.weeklyreport"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"

launchctl unload "$PLIST" 2>/dev/null
rm -f "$PLIST"

echo "The weekly schedule has been removed. No more automatic emails."
echo "(You can still run the report any time with 'Run Wine Report.command'.)"
echo "Press any key to close."
read -n 1 -s
