#!/bin/bash
# Start Celery GPU training worker with concurrency from config file

set -e

echo "=================================================================================="
echo "🚀 CELERY GPU WORKER STARTING - $(date -Iseconds)"
echo "=================================================================================="

# Set file descriptor limit for Celery worker
ulimit -n 65535
echo "📊 Set file descriptor limit to 65535"

# CRITICAL: Kill only TRULY orphaned DataLoader worker processes
# Must be careful not to kill workers belonging to active training jobs!
echo "🔫 Killing orphaned DataLoader workers (safely, not active ones)..."

KILLED_COUNT=0

# Get list of active training process PIDs (Celery workers and their children)
# These are processes we must NOT kill
ACTIVE_TRAINING_PIDS=()
if command -v celery >/dev/null 2>&1; then
    # Get Celery worker PIDs
    for pid in $(pgrep -f "celery.*worker.*gpu_training" 2>/dev/null || true); do
        ACTIVE_TRAINING_PIDS+=($pid)
        # Get all children of this Celery worker
        for child in $(pgrep -P $pid 2>/dev/null || true); do
            ACTIVE_TRAINING_PIDS+=($child)
        done
    done
fi

# Function to check if a PID is an active training process or its child
is_active_training() {
    local pid=$1
    # Check if it's in our active list
    for active_pid in "${ACTIVE_TRAINING_PIDS[@]}"; do
        if [ "$pid" = "$active_pid" ]; then
            return 0  # Is active
        fi
    done
    # Check if parent is active
    local ppid=$(ps -o ppid= -p $pid 2>/dev/null | tr -d ' ')
    if [ -n "$ppid" ]; then
        for active_pid in "${ACTIVE_TRAINING_PIDS[@]}"; do
            if [ "$ppid" = "$active_pid" ]; then
                return 0  # Parent is active
            fi
        done
    fi
    return 1  # Not active
}

# Method 1: Kill Python processes that are children of PID 1 (reparented orphans)
# These are workers whose parent training process died but workers survived
# This is the SAFEST method - only kills true orphans
for pid in $(ps -eo pid,ppid,cmd | grep -E '^\s*[0-9]+\s+1\s+.*python' | grep -v grep | awk '{print $1}' || true); do
    # Skip if this is an active training process
    if is_active_training $pid; then
        continue
    fi
    
    # Check if this is a worker process (has "multiprocessing" or "Spawn" in command)
    if ps -p $pid -o cmd= 2>/dev/null | grep -qE 'multiprocessing|Spawn'; then
        # Double-check: parent must be PID 1 (init) - truly orphaned
        ppid=$(ps -o ppid= -p $pid 2>/dev/null | tr -d ' ')
        if [ "$ppid" = "1" ]; then
            echo "   Killing orphaned worker PID $pid (reparented to init, not active)"
            kill -9 $pid 2>/dev/null || true
            KILLED_COUNT=$((KILLED_COUNT + 1))
        fi
    fi
done

# Method 2: Kill SpawnPoolWorker processes whose parent is dead
# Check each SpawnPoolWorker to see if its parent is still alive
for pid in $(pgrep -f "SpawnPoolWorker\|SpawnProcess" 2>/dev/null || true); do
    # Skip if this is an active training process
    if is_active_training $pid; then
        continue
    fi
    
    # Check if parent is still alive
    ppid=$(ps -o ppid= -p $pid 2>/dev/null | tr -d ' ')
    if [ -n "$ppid" ] && [ "$ppid" != "1" ]; then
        # Check if parent process exists
        if ! ps -p $ppid >/dev/null 2>&1; then
            # Parent is dead - this is an orphan
            echo "   Killing orphaned SpawnWorker PID $pid (parent $ppid is dead)"
            kill -9 $pid 2>/dev/null || true
            KILLED_COUNT=$((KILLED_COUNT + 1))
        fi
    elif [ "$ppid" = "1" ]; then
        # Already reparented to init - kill it (Method 1 should have caught this, but double-check)
        if ps -p $pid -o cmd= 2>/dev/null | grep -qE 'multiprocessing|Spawn'; then
            echo "   Killing orphaned SpawnWorker PID $pid (reparented to init)"
            kill -9 $pid 2>/dev/null || true
            KILLED_COUNT=$((KILLED_COUNT + 1))
        fi
    fi
done

if [ $KILLED_COUNT -gt 0 ]; then
    echo "✅ Killed $KILLED_COUNT orphaned worker processes"
    # Wait a moment for GPU memory to be released
    sleep 2
else
    echo "✅ No orphaned workers found"
fi

# Clear CUDA cache in case there's fragmentation
echo "🧹 Clearing CUDA cache..."
python3 -c "import torch; torch.cuda.empty_cache() if torch.cuda.is_available() else None" 2>/dev/null || true

# Source virtual environment
source /sphere/.venv/bin/activate

# CRITICAL: GPU training jobs MUST run serially (concurrency=1)
# Running multiple GPU training jobs concurrently on a single GPU causes:
# 1. CUDA OOM errors as jobs compete for VRAM
# 2. DataLoader worker crashes due to memory pressure
# 3. One job's cleanup killing another job's workers
# 
# Even with multiple GPUs, concurrent training jobs on the SAME GPU is broken.
# The only safe configuration is concurrency=1 per GPU.
#
# If you have multiple GPUs and want concurrent training, run separate
# Celery workers with different CUDA_VISIBLE_DEVICES settings.

# Check for override file (for testing only - should always be 1 in production)
CONFIG_FILE="/sphere/app/.celery_gpu_concurrency"
if [ -f "$CONFIG_FILE" ]; then
    CONCURRENCY=$(cat "$CONFIG_FILE" | tr -d '[:space:]')
    if [ "$CONCURRENCY" != "1" ]; then
        echo "⚠️  WARNING: Concurrency=$CONCURRENCY from config file"
        echo "   GPU training jobs should use concurrency=1 to avoid crashes"
        echo "   Set $CONFIG_FILE to 1 or delete the file"
    fi
else
    # Default: ALWAYS use concurrency=1 for GPU training
    CONCURRENCY=1
fi

# Safety check: Never allow concurrency > 1 for GPU training
if [ "$CONCURRENCY" -gt 1 ]; then
    echo "⚠️  OVERRIDING concurrency=$CONCURRENCY to 1 (GPU training requires serial execution)"
    CONCURRENCY=1
fi

echo "🎯 Starting Celery GPU worker with concurrency=$CONCURRENCY"

# Start Celery worker
exec celery -A celery_app worker \
    --loglevel=info \
    --concurrency=$CONCURRENCY \
    --queues=gpu_training \
    --hostname=celery-gpu_training@$(hostname -s) \
    --prefetch-multiplier=1

