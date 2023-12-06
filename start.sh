#!/bin/bash
# Launch the flask app and direct the output to nohup.out

# Function to start the application
start_app() {
    nohup python3 app.py > ./nohup.out 2>&1 &
}

# Function to check if the application is already running
is_app_running() {
    pgrep -f "python3 app.py" > /dev/null
}

# Main logic
if is_app_running; then
    echo "Application is already running. Restarting..."
    pkill -f "python3 app.py"
    sleep 2  # Wait for the process to terminate
fi

start_app

echo "Application started. Check ./nohup.out for logs."