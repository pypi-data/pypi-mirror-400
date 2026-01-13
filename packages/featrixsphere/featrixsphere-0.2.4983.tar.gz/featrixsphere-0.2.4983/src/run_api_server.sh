#!/bin/bash
#
# Simple FastAPI Server Startup Script
# 
# This script just starts the FastAPI backend server on churro
# Referenced in supervisord-watchers.conf
#

set -e

# Configuration
APP_DIR="/sphere/app"
VENV_PATH="/sphere/.venv" 
API_HOST="0.0.0.0"
API_PORT="8000"

echo "=================================================================================="
echo "🚀 API SERVER STARTING - $(date -Iseconds)"
echo "=================================================================================="
echo "🚀 Starting Featrix Sphere FastAPI Server..."

# Change to app directory
cd "$APP_DIR"

# Activate virtual environment if it exists
if [ -f "$VENV_PATH/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
else
    echo "Warning: Virtual environment not found at $VENV_PATH"
fi

# Check if port 8000 is already in use and clear it if needed
check_port() {
    local port_in_use=false
    local pid=""
    
    # Try multiple methods to check if port is in use
    if command -v lsof >/dev/null 2>&1; then
        # Use lsof to check if port is in use
        pid=$(lsof -ti:$API_PORT 2>/dev/null || true)
        if [ -n "$pid" ]; then
            port_in_use=true
        fi
    elif command -v netstat >/dev/null 2>&1; then
        # Fallback to netstat
        if netstat -tuln 2>/dev/null | grep -q ":$API_PORT "; then
            port_in_use=true
            # Try to get PID from netstat (may not work on all systems)
            pid=$(netstat -tulnp 2>/dev/null | grep ":$API_PORT " | awk '{print $7}' | cut -d'/' -f1 | head -1 || true)
        fi
    elif command -v ss >/dev/null 2>&1; then
        # Fallback to ss
        if ss -tuln 2>/dev/null | grep -q ":$API_PORT "; then
            port_in_use=true
        fi
    fi
    
    if [ "$port_in_use" = true ]; then
        echo "⚠️  Port $API_PORT is already in use"
        
        # First, try to kill any uvicorn processes matching our pattern
        echo "   Checking for existing uvicorn processes..."
        if pkill -f "uvicorn.*api:create_app" 2>/dev/null; then
            echo "   ✅ Killed existing uvicorn processes"
            sleep 2
        fi
        
        # Get ALL PIDs holding the port (lsof can return multiple, one per line)
        # Handle both single PID and multiple PIDs
        local all_pids=""
        if [ -n "$pid" ]; then
            # If we got a PID from lsof, get ALL PIDs (lsof -ti returns all, one per line)
            if command -v lsof >/dev/null 2>&1; then
                all_pids=$(lsof -ti:$API_PORT 2>/dev/null | tr '\n' ' ' || true)
            else
                all_pids="$pid"
            fi
        fi
        
        # Kill all processes holding the port
        if [ -n "$all_pids" ]; then
            echo "   Found process(es) on port $API_PORT: $all_pids"
            for pid_to_kill in $all_pids; do
                if kill -0 "$pid_to_kill" 2>/dev/null; then
                    # Check if it's a uvicorn/python process or orphaned multiprocessing worker
                    cmd=$(ps -p "$pid_to_kill" -o cmd= 2>/dev/null || echo "")
                    if echo "$cmd" | grep -qE "uvicorn|python|multiprocessing"; then
                        echo "   Killing process $pid_to_kill..."
                        kill -TERM "$pid_to_kill" 2>/dev/null || true
                    else
                        echo "   ⚠️  Port is in use by non-uvicorn process (PID: $pid_to_kill) - may need manual intervention"
                    fi
                fi
            done
            sleep 2
            # Force kill any remaining processes
            for pid_to_kill in $all_pids; do
                if kill -0 "$pid_to_kill" 2>/dev/null; then
                    echo "   Process $pid_to_kill still running - force killing..."
                    kill -KILL "$pid_to_kill" 2>/dev/null || true
                fi
            done
            sleep 1
            echo "   ✅ Cleared port $API_PORT"
        else
            # Port might be in TIME_WAIT state - wait a moment
            echo "   Port may be in TIME_WAIT state - waiting 2 seconds..."
            sleep 2
        fi
    fi
}

# Check and clear port before starting
check_port

# CRITICAL: Force CPU-only mode for API workers
# API workers should NEVER use GPU - that's for training jobs
# Each worker would allocate ~600MB GPU memory, wasting 2.4GB+ for nothing
export CUDA_VISIBLE_DEVICES=''
echo "🚫 GPU disabled for API workers (CUDA_VISIBLE_DEVICES='')"

# Start the FastAPI server
echo "Starting FastAPI server on $API_HOST:$API_PORT..."
echo "App directory: $APP_DIR"
echo "Python path: $(which python)"

# Use uvicorn with the factory pattern as defined in supervisord config
# Suppress uvicorn access logs - we have custom logging middleware in api.py
# No --reload flag in production - code changes require proper deployment/restart
# 
# CRITICAL: Use 4 workers to handle concurrent requests
# Even with asyncio.to_thread(), multiple concurrent slow requests can exhaust workers
# 4 workers = can handle 4 slow requests simultaneously without blocking new requests
NUM_WORKERS=4

echo "Starting uvicorn with $NUM_WORKERS workers for better concurrency..."
exec uvicorn --factory api:create_app --host="$API_HOST" --port="$API_PORT" \
    --workers="$NUM_WORKERS" --no-access-log --log-level info 