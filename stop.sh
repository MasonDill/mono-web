#!/bin/bash
# Launch the flask app and direct the output to nohup.out

# Function to check if the application is already running
is_app_running() {
    pgrep -f "python3 app.py" > /dev/null
}

# Main logic
if is_app_running; then
    echo "Application halted"
    pkill -f "python3 app.py"
    sleep 2  # Wait for the process to terminate
fi