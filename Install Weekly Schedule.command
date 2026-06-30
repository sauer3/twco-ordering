#!/bin/bash
# Double-click to schedule the weekly emailed report (Mondays at 8:00 AM).
# Re-run this any time to change the schedule. To stop it, double-click
# "Uninstall Weekly Schedule.command".

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

LABEL="com.twco.weeklyreport"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
WRAPPER="$(pwd)/run_weekly.sh"
chmod +x "$WRAPPER"

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${WRAPPER}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Weekday</key><integer>1</integer>
        <key>Hour</key><integer>8</integer>
        <key>Minute</key><integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$(pwd)/output/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>$(pwd)/output/launchd.err.log</string>
</dict>
</plist>
EOF

# Reload so changes take effect.
launchctl unload "$PLIST" 2>/dev/null
launchctl load "$PLIST"

echo "Scheduled: the report will be generated and emailed every Monday at 8:00 AM."
echo "(Your Mac needs to be awake at that time; if it's asleep, macOS runs the"
echo " job at the next wake-up.)"
echo
echo "Plist installed at: $PLIST"
echo "Press any key to close."
read -n 1 -s
