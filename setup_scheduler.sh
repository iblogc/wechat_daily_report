#!/bin/bash

# WeChat Daily Report Scheduler Setup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

echo "Setting up WeChat Daily Report Scheduler..."
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"

# Create launchd job (macOS native scheduler)
setup_launchd() {
    local schedule_time="${1:-08:00}"
    local hour=$(echo $schedule_time | cut -d: -f1)
    local minute=$(echo $schedule_time | cut -d: -f2)
    
    echo "Setting up launchd job to run at $schedule_time daily..."
    
    # Remove leading zeros to avoid octal interpretation
    hour=$(echo $hour | sed 's/^0*//')
    minute=$(echo $minute | sed 's/^0*//')
    
    # Handle empty values (when time is 00:xx)
    [ -z "$hour" ] && hour=0
    [ -z "$minute" ] && minute=0
    
    local plist_name="com.wechat.dailyreport"
    local plist_path="$HOME/Library/LaunchAgents/$plist_name.plist"
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$HOME/Library/LaunchAgents"
    
    # Create plist file
    cat > "$plist_path" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$plist_name</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$MAIN_SCRIPT</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>$hour</integer>
        <key>Minute</key>
        <integer>$minute</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/launchd.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

    # Load the job
    launchctl unload "$plist_path" 2>/dev/null || true
    launchctl load "$plist_path"
    
    echo "✅ Launchd job created and loaded successfully!"
    echo "Plist file: $plist_path"
    echo "Will run daily at $schedule_time"
    echo "💡 Proxy settings can be configured in .env.prod file (PROXY_ENABLED, PROXY_HTTP, PROXY_HTTPS)"
    echo ""
    echo "Useful commands:"
    echo "  Check status: launchctl list | grep $plist_name"
    echo "  Unload job:   launchctl unload $plist_path"
    echo "  Reload job:   launchctl unload $plist_path && launchctl load $plist_path"
}

# Create systemd timer (alternative to cron)
setup_systemd_timer() {
    local service_name="wechat-daily-report"
    local time="${1:-08:00}"
    
    echo "Setting up systemd timer to run at $time daily..."
    
    # Create service file
    sudo tee /etc/systemd/system/$service_name.service > /dev/null <<EOF
[Unit]
Description=WeChat Daily Report Generator
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$PYTHON_PATH $MAIN_SCRIPT
StandardOutput=append:$SCRIPT_DIR/logs/systemd.log
StandardError=append:$SCRIPT_DIR/logs/systemd.log

[Install]
WantedBy=multi-user.target
EOF

    # Create timer file
    sudo tee /etc/systemd/system/$service_name.timer > /dev/null <<EOF
[Unit]
Description=Run WeChat Daily Report Generator daily
Requires=$service_name.service

[Timer]
OnCalendar=*-*-* $time:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

    # Reload systemd and enable timer
    sudo systemctl daemon-reload
    sudo systemctl enable $service_name.timer
    sudo systemctl start $service_name.timer
    
    echo "✅ Systemd timer created and started!"
    echo "Check status with: systemctl status $service_name.timer"
    echo "💡 Proxy settings can be configured in .env.prod file (PROXY_ENABLED, PROXY_HTTP, PROXY_HTTPS)"
}

# Show menu
show_menu() {
    echo ""
    echo "Choose scheduling method:"
    echo "1) Launchd (recommended for macOS)"
    echo "2) Systemd timer (for Linux systems with systemd)"
    echo "3) Manual setup instructions"
    echo "4) Exit"
    echo ""
}

# Manual setup instructions
show_manual_instructions() {
    echo ""
    echo "Manual Setup Instructions:"
    echo "========================="
    echo ""
    echo "1. Launchd Setup (macOS):"
    echo "   Create plist file at: ~/Library/LaunchAgents/com.wechat.dailyreport.plist"
    echo "   Load with: launchctl load ~/Library/LaunchAgents/com.wechat.dailyreport.plist"
    echo ""
    echo "2. Cron Job Setup (Linux/Unix):"
    echo "   Run: crontab -e"
    echo "   Add: 0 8 * * * cd $SCRIPT_DIR && $PYTHON_PATH $MAIN_SCRIPT"
    echo ""
    echo "3. Test the script:"
    echo "   cd $SCRIPT_DIR"
    echo "   $PYTHON_PATH $MAIN_SCRIPT --test"
    echo ""
    echo "4. Run manually:"
    echo "   cd $SCRIPT_DIR"
    echo "   $PYTHON_PATH $MAIN_SCRIPT"
    echo ""
    echo "5. Proxy Configuration:"
    echo "   Edit .env.prod file and set:"
    echo "   PROXY_ENABLED=true"
    echo "   PROXY_HTTP=http://127.0.0.1:1080"
    echo "   PROXY_HTTPS=http://127.0.0.1:1080"
    echo ""
}

# Main execution
main() {
    # Create logs directory
    mkdir -p "$SCRIPT_DIR/logs"
    
    # Check if config exists
    if [ ! -f "$SCRIPT_DIR/.env.prod" ]; then
        echo "⚠️  Configuration file .env.prod not found!"
        echo "Please copy .env.example to .env.prod and configure it first."
        echo "cp .env.example .env.prod"
        exit 1
    fi
    
    while true; do
        show_menu
        read -p "Enter your choice (1-4): " choice
        
        case $choice in
            1)
                read -p "Enter time (HH:MM, default 08:00): " time_input
                setup_launchd "${time_input:-08:00}"
                break
                ;;
            2)
                read -p "Enter time (HH:MM, default 08:00): " time_input
                setup_systemd_timer "${time_input:-08:00}"
                break
                ;;
            3)
                show_manual_instructions
                break
                ;;
            4)
                echo "Exiting..."
                exit 0
                ;;
            *)
                echo "Invalid choice. Please try again."
                ;;
        esac
    done
}

# Check if running with options
if [ "$1" = "--launchd" ]; then
    setup_launchd "$2"
elif [ "$1" = "--systemd" ]; then
    setup_systemd_timer "$2"
else
    main
fi