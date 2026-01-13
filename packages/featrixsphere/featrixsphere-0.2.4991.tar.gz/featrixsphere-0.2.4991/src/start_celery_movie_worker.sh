#!/bin/bash
# Start Celery Movie Generation worker (dedicated, concurrency=1)

set -e

echo "=================================================================================="
echo "🎬 CELERY MOVIE GENERATION WORKER STARTING - $(date -Iseconds)"
echo "=================================================================================="

# Source virtual environment
source /sphere/.venv/bin/activate

# Start Celery worker with concurrency=1 (movies get 1 dedicated slot)
exec celery -A celery_app worker \
    --loglevel=info \
    --concurrency=1 \
    --queues=movie_generation \
    --hostname=celery-movie_generation@$(hostname -s) \
    --prefetch-multiplier=1

