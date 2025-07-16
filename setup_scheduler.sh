#!/bin/bash

# WeChat Daily Report Scheduler Setup Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

echo "Setting up WeChat Daily Report Scheduler..."
echo "Script directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"

# Create cron job
setup_cron() {
    local cron_time="${1:-08:00}"
    local hour=$(echo $cron_time | cut -d: -f1)
    local minute=$(echo $cron_time | cut -d: -f2)
    
    echo "Setting up cron job to run at $cron_time daily..."
    
    # Ask for proxy settings
    read -p "Do you want to use a proxy for AI services? (y/n): " use_proxy
    local proxy_env=""
    if [[ "$use_proxy" =~ ^[Yy]$ ]]; then
        read -p "Enter proxy URL (e.g., http://127.0.0.1:1080): " proxy_url
        if [[ -n "$proxy_url" ]]; then
            proxy_env="export HTTP_PROXY=$proxy_url; export HTTPS_PROXY=$proxy_url; "
        fi
    fi
    
    # Create cron entry with optional proxy
    local cron_entry="$minute $hour * * * cd $SCRIPT_DIR && ${proxy_env}$PYTHON_PATH $MAIN_SCRIPT >> $SCRIPT_DIR/logs/cron.log 2>&1"
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
    
    echo "✅ Cron job added successfully!"
    echo "Command: $cron_entry"
}

# Create systemd timer (alternative to cron)
setup_systemd_timer() {
    local service_name="wechat-daily-report"
    local time="${1:-08:00}"
    
    echo "Setting up systemd timer to run at $time daily..."
    
    # Ask for proxy settings
    read -p "Do you want to use a proxy for AI services? (y/n): " use_proxy
    local proxy_env=""
    if [[ "$use_proxy" =~ ^[Yy]$ ]]; then
        read -p "Enter proxy URL (e.g., http://127.0.0.1:1080): " proxy_url
        if [[ -n "$proxy_url" ]]; then
            proxy_env="Environment=HTTP_PROXY=$proxy_url
Environment=HTTPS_PROXY=$proxy_url"
        fi
    fi
    
    # Create service file with optional proxy
    sudo tee /etc/systemd/system/$service_name.service > /dev/null <<EOF
[Unit]
Description=WeChat Daily Report Generator
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$SCRIPT_DIR
${proxy_env}
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
}

# Show menu
show_menu() {
    echo ""
    echo "Choose scheduling method:"
    echo "1) Cron job (recommended for most users)"
    echo "2) Systemd timer (for systems with systemd)"
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
    echo "1. Cron Job Setup:"
    echo "   Run: crontab -e"
    echo "   Add: 0 8 * * * cd $SCRIPT_DIR && $PYTHON_PATH $MAIN_SCRIPT"
    echo "   With proxy: 0 8 * * * cd $SCRIPT_DIR && export HTTP_PROXY=http://127.0.0.1:1080; export HTTPS_PROXY=http://127.0.0.1:1080; $PYTHON_PATH $MAIN_SCRIPT"
    echo ""
    echo "2. Test the script:"
    echo "   cd $SCRIPT_DIR"
    echo "   $PYTHON_PATH $MAIN_SCRIPT --test"
    echo ""
    echo "3. Run manually:"
    echo "   cd $SCRIPT_DIR"
    echo "   $PYTHON_PATH $MAIN_SCRIPT"
    echo ""
    echo "4. Run with proxy manually:"
    echo "   cd $SCRIPT_DIR"
    echo "   export HTTP_PROXY=http://127.0.0.1:1080"
    echo "   export HTTPS_PROXY=http://127.0.0.1:1080"
    echo "   $PYTHON_PATH $MAIN_SCRIPT"
    echo ""
}

# Main execution
main() {
    # Create logs directory
    mkdir -p "$SCRIPT_DIR/logs"
    
    # Check if config exists
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        echo "⚠️  Configuration file .env not found!"
        echo "Please copy .env.example to .env and configure it first."
        echo "cp .env.example .env"
        exit 1
    fi
    
    while true; do
        show_menu
        read -p "Enter your choice (1-4): " choice
        
        case $choice in
            1)
                read -p "Enter time (HH:MM, default 08:00): " time_input
                setup_cron "${time_input:-08:00}"
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
if [ "$1" = "--cron" ]; then
    setup_cron "$2"
elif [ "$1" = "--systemd" ]; then
    setup_systemd_timer "$2"
else
    main
fi