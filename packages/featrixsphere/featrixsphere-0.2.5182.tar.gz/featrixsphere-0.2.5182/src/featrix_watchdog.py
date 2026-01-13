#!/usr/bin/env python3
"""
Featrix Training Watchdog
Monitors training jobs for stuck conditions:
- GPU RAM full (>95%)
- CPU/GPU utilization low (<10%)
- No epoch progress for extended period

If all conditions are met, restarts worker-train_es via supervisorctl.
"""

import argparse
import json
import logging
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)-8s] %(name)-45s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Add src to path for imports
src_path = Path(__file__).parent
if str(src_path.resolve()) not in sys.path:
    sys.path.insert(0, str(src_path.resolve()))

try:
    from config import config
    from lib.job_manager import JobStatus
    from lib.job_manager import load_job
    from slack import send_slack_message
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

# Try to import redis for checking worker heartbeats
try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

# Try to import requests for pinging sphere-api
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    logger.warning("requests not available - cannot ping sphere-api")


# ============================================================================
# Redis Heartbeat Check for DataLoader Workers
# ============================================================================
# DataLoader workers post heartbeats to Redis. We check before killing any
# process to make sure it's not an active worker.

HEARTBEAT_KEY_PREFIX = "dataloader:heartbeat:"
HEARTBEAT_MAX_AGE_SECONDS = 360  # Heartbeats older than this are considered stale (6 minutes)


def check_worker_heartbeat(pid: int) -> dict | None:
    """
    Check if a process has an active heartbeat in Redis.
    
    DataLoader workers post heartbeats every 5 minutes with a 6 minute TTL.
    If we find a heartbeat, the process is an active worker and should NOT be killed.
    
    Args:
        pid: Process ID to check
        
    Returns:
        Heartbeat data dict if found and recent, None if not found/expired
    """
    if not HAS_REDIS:
        return None
    
    try:
        # Use same Redis db as dataloader_utils.py (db 2)
        client = redis.Redis(
            host='localhost',
            port=6379,
            db=2,
            decode_responses=True,
            socket_timeout=1.0,
            socket_connect_timeout=1.0,
        )
        
        key = f"{HEARTBEAT_KEY_PREFIX}{pid}"
        data = client.get(key)
        if data:
            heartbeat = json.loads(data)
            # Verify heartbeat is recent (within TTL)
            last_heartbeat = heartbeat.get('last_heartbeat', 0)
            age = time.time() - last_heartbeat
            if age < HEARTBEAT_MAX_AGE_SECONDS:
                return heartbeat
            else:
                logger.debug(f"Heartbeat for PID {pid} is stale ({age:.1f}s old)")
        return None
    except Exception as e:
        logger.debug(f"Error checking heartbeat for PID {pid}: {e}")
        return None


class TrainingWatchdog:
    def __init__(self, check_interval: int = 60, stuck_threshold: int = 300):
        """
        Initialize the training watchdog.
        
        Args:
            check_interval: How often to check for stuck jobs (seconds)
            stuck_threshold: How long without epoch progress before considering stuck (seconds)
        """
        self.check_interval = check_interval
        self.stuck_threshold = stuck_threshold
        self.last_epoch_check: Dict[str, Tuple[int, float]] = {}  # job_id -> (epoch, timestamp)
        self.last_restart_time: Dict[str, float] = {}  # job_id -> timestamp of last restart
        self.last_announce_time = 0.0  # Last time we pinged sphere-api
        self.announce_interval = 30  # Ping sphere-api every 30 seconds
        self.last_slack_notification: Dict[str, float] = {}  # issue_type -> timestamp of last Slack notification
        self.slack_notification_interval = 900  # 15 minutes in seconds
        self.last_api_health_check = 0.0  # Last time we checked API health
        self.api_health_check_interval = 30  # Check API health every 30 seconds
        self.last_api_restart_time = 0.0  # Last time we restarted API server
        
        # Get node name from hostname
        try:
            hostname = socket.gethostname()
            hostname_lower = hostname.lower()
            # Map hostname to node name (e.g., "taco", "churro", "burrito")
            # Hostname mappings for nodes with IP-based hostnames
            if 'taco' in hostname_lower:
                self.node_name = 'taco'
            elif 'churro' in hostname_lower:
                self.node_name = 'churro'
            elif 'burrito' in hostname_lower:
                self.node_name = 'burrito'
            else:
                self.node_name = hostname.split('.')[0]  # Use first part of hostname
        except Exception:
            self.node_name = 'unknown'
        
        logger.info(f"Training watchdog initialized")
        logger.info(f"  Check interval: {check_interval}s")
        logger.info(f"  Stuck threshold: {stuck_threshold}s")
        logger.info(f"  Node name: {self.node_name}")

    def get_gpu_stats(self) -> Optional[Dict]:
        """Get GPU memory and utilization stats using nvidia-smi."""
        try:
            cmd = [
                'nvidia-smi',
                '--query-gpu=utilization.gpu,memory.used,memory.total',
                '--format=csv,noheader,nounits'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.debug("nvidia-smi command failed - GPU stats not available")
                return None
            
            lines = result.stdout.strip().split('\n')
            if not lines or not lines[0]:
                return None
            
            # Get first GPU stats (or average if multiple)
            parts = [p.strip() for p in lines[0].split(',')]
            if len(parts) >= 3:
                gpu_util = float(parts[0]) if parts[0] != '[Not Supported]' else 0.0
                mem_used = float(parts[1])
                mem_total = float(parts[2])
                mem_percent = (mem_used / mem_total * 100) if mem_total > 0 else 0
                
                return {
                    'gpu_utilization': gpu_util,
                    'memory_used_mb': mem_used,
                    'memory_total_mb': mem_total,
                    'memory_percent': mem_percent
                }
        except FileNotFoundError:
            logger.debug("nvidia-smi not found - GPU monitoring disabled")
            return None
        except Exception as e:
            logger.debug(f"Error getting GPU stats: {e}")
            return None
        
        return None

    def get_cpu_stats(self) -> Optional[Dict]:
        """Get CPU utilization stats using psutil."""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            return {
                'cpu_percent': cpu_percent
            }
        except ImportError:
            logger.debug("psutil not available - CPU monitoring disabled")
            return None
        except Exception as e:
            logger.debug(f"Error getting CPU stats: {e}")
            return None

    def get_latest_epoch(self, job_output_dir: Path) -> Optional[int]:
        """Get the latest epoch number from checkpoint files."""
        try:
            checkpoint_files = list(job_output_dir.glob("training_state_e-*.pth"))
            if not checkpoint_files:
                return None
            
            latest_epoch = -1
            for checkpoint_file in checkpoint_files:
                # Extract epoch from filename like "training_state_e-42.pth"
                match = re.search(r'training_state_e-(\d+)\.pth', checkpoint_file.name)
                if match:
                    epoch = int(match.group(1))
                    if epoch > latest_epoch:
                        latest_epoch = epoch
            
            return latest_epoch if latest_epoch >= 0 else None
        except Exception as e:
            logger.debug(f"Error getting latest epoch from {job_output_dir}: {e}")
            return None

    def get_worker_train_es_pids(self) -> list:
        """Get PIDs of worker-train_es processes."""
        pids = []
        try:
            result = subprocess.run(
                ['supervisorctl', 'status', 'worker-train_es'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse PID from output like "worker-train_es RUNNING pid 12345, uptime 1:23:45"
                for line in result.stdout.split('\n'):
                    if 'pid' in line.lower():
                        import re
                        match = re.search(r'pid\s+(\d+)', line)
                        if match:
                            pids.append(int(match.group(1)))
        except Exception as e:
            logger.debug(f"Error getting worker-train_es PIDs: {e}")
        return pids

    def find_orphaned_multiprocess_workers(self) -> list:
        """
        Find orphaned multiprocessing processes that don't belong to current worker-train_es.
        Detects both pt_data_worker processes and multiprocessing spawn/resource_tracker processes.
        
        Returns:
            List of (pid, ppid, reason) tuples for orphaned workers
        """
        orphaned = []
        try:
            import psutil
            
            # Get current worker-train_es PIDs and their process groups
            worker_pids = self.get_worker_train_es_pids()
            worker_pgids = set()
            worker_children = set()
            
            for worker_pid in worker_pids:
                try:
                    worker_proc = psutil.Process(worker_pid)
                    # pgid is a property, not a method
                    try:
                        pgid = worker_proc.pgid
                        worker_pgids.add(pgid)
                    except AttributeError:
                        # Fallback: try to get pgid from process info
                        try:
                            proc_info = worker_proc.as_dict(['pgid'])
                            if 'pgid' in proc_info:
                                worker_pgids.add(proc_info['pgid'])
                        except (AttributeError, KeyError):
                            logger.debug(f"Could not get pgid for process {worker_pid}")
                    # Get all descendants
                    for child in worker_proc.children(recursive=True):
                        worker_children.add(child.pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Find all orphaned multiprocessing processes
            # Use safer pattern: iterate without pre-fetching pgid, get it per-process
            # This avoids exceptions from transient/unreadable processes during iteration
            attrs = ['pid', 'ppid', 'name', 'cmdline']
            proc_iter = psutil.process_iter(attrs)
            
            for proc in proc_iter:
                try:
                    proc_info = proc.info
                    cmdline_list = proc_info.get('cmdline') or []
                    cmdline = ' '.join(cmdline_list).lower() if cmdline_list else ''
                    
                    # Check if it's a multiprocessing-related process
                    is_pt_worker = 'pt_data_worker' in cmdline or proc_info.get('name', '').lower() == 'pt_data_worker'
                    is_multiprocessing_spawn = 'multiprocessing.spawn' in cmdline and 'spawn_main' in cmdline
                    is_multiprocessing_tracker = 'multiprocessing.resource_tracker' in cmdline and 'main' in cmdline
                    
                    if is_pt_worker or is_multiprocessing_spawn or is_multiprocessing_tracker:
                        pid = proc_info['pid']
                        ppid = proc_info['ppid']
                        
                        # Get pgid per-process with exception handling (safer than pre-fetching)
                        # This avoids exceptions from transient/unreadable processes during iteration
                        pgid = None
                        try:
                            pgid = proc.pgid  # pgid is a property, not a method
                        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                            # pgid not available for this process or on this platform
                            pass
                        
                        # Check if it belongs to current worker
                        if pid in worker_children:
                            continue  # Legitimate child process
                        
                        # Check pgid if we successfully got it
                        if pgid is not None and pgid in worker_pgids:
                            continue  # Same process group as worker
                        
                        # Check parent
                        try:
                            parent = psutil.Process(ppid)
                            parent_cmdline_list = parent.cmdline() or []
                            parent_cmdline = ' '.join(parent_cmdline_list) if parent_cmdline_list else ''
                            parent_cmdline_lower = parent_cmdline.lower()
                            
                            # Check if parent is a legitimate process that spawns workers
                            # These are NOT orphans:
                            # - worker-train_es (training workers)
                            # - Children of worker-train_es (including training TASK processes)
                            # - watch-queue (legacy queue watcher)
                            # - uvicorn (string server HTTP workers, /sphere/app API workers)
                            # - string-server (string server directory)
                            # - celery_tasks (string server celery workers)
                            # - celery (any celery worker process)
                            # CRITICAL: Must check ppid in worker_children too!
                            # Celery spawns task processes as children, and DataLoaders are
                            # children of the task process, not the celery worker itself.
                            is_legitimate_parent = (
                                ppid in worker_pids or
                                ppid in worker_children or  # Parent is a child of celery worker (e.g., training task)
                                'watch-queue' in parent_cmdline_lower or
                                'uvicorn' in parent_cmdline_lower or
                                'string-server' in parent_cmdline_lower or
                                '/string-server' in parent_cmdline or
                                'celery_tasks' in parent_cmdline_lower or
                                'celery' in parent_cmdline_lower
                            )
                            
                            # If parent is not a legitimate worker/server, it's orphaned
                            if not is_legitimate_parent:
                                process_type = "multiprocessing spawn" if is_multiprocessing_spawn else ("multiprocessing tracker" if is_multiprocessing_tracker else "pt_data_worker")
                                orphaned.append((pid, ppid, f"Orphaned {process_type} - parent {ppid} is not worker-train_es"))
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            # Parent is gone - definitely orphaned
                            process_type = "multiprocessing spawn" if is_multiprocessing_spawn else ("multiprocessing tracker" if is_multiprocessing_tracker else "pt_data_worker")
                            orphaned.append((pid, ppid, f"Orphaned {process_type} - parent process no longer exists"))
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except ImportError:
            logger.warning("psutil not available - cannot find orphaned workers")
        except Exception as e:
            # Don't log pgid-related errors as errors - they're expected on some platforms
            error_msg = str(e).lower()
            if 'pgid' in error_msg and ('invalid attr' in error_msg or 'invalid attribute' in error_msg):
                logger.debug(f"pgid not available on this platform: {e}")
            else:
                logger.error(f"Error finding orphaned workers: {e}")
        
        return orphaned

    def kill_orphaned_workers(self, orphaned: list) -> int:
        """Kill orphaned multiprocess workers."""
        killed_count = 0
        skipped_count = 0
        for pid, ppid, reason in orphaned:
            try:
                import psutil
                proc = psutil.Process(pid)
                
                # CRITICAL: Check Redis heartbeat FIRST - active DataLoader workers post heartbeats
                # This prevents killing legitimate workers that are actively being used by training
                heartbeat = check_worker_heartbeat(pid)
                if heartbeat:
                    job_id = heartbeat.get('job_id', 'unknown')
                    job_type = heartbeat.get('job_type', 'unknown')
                    worker_id = heartbeat.get('worker_id', '?')
                    logger.info(
                        f"✅ PID {pid} has active heartbeat - DataLoader worker {worker_id} for job {job_id[:12] if len(job_id) > 12 else job_id}... "
                        f"({job_type}). NOT killing despite being flagged as orphaned."
                    )
                    skipped_count += 1
                    continue  # Skip killing - this is an active worker
                
                # DISABLED: Log what we WOULD kill, but don't actually kill
                # TODO: Re-enable once orphan detection is verified to be correct
                logger.warning(f"🔪 [DRY RUN] WOULD kill orphaned process PID {pid} ({reason}) - but killing is DISABLED")
                # proc.kill()  # DISABLED
                killed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Already gone or can't access
                pass
            except Exception as e:
                logger.debug(f"Error checking PID {pid}: {e}")
        
        if skipped_count > 0:
            logger.info(f"✅ Skipped {skipped_count} process(es) with active heartbeats")
        
        return killed_count

    def send_slack_notification(self, issue_type: str, message: str) -> bool:
        """
        Send Slack notification with rate limiting (max once per 15 minutes per issue type).
        
        Args:
            issue_type: Type of issue (e.g., "orphaned_workers", "gpu_ram_full", "worker_restart")
            message: Message to send to Slack
            
        Returns:
            bool: True if message was sent, False if throttled
        """
        current_time = time.time()
        
        # Check if we've sent this type of notification recently
        if issue_type in self.last_slack_notification:
            time_since_last = current_time - self.last_slack_notification[issue_type]
            if time_since_last < self.slack_notification_interval:
                logger.debug(f"⏸️  Slack notification throttled for {issue_type} (last sent {int(time_since_last)}s ago)")
                return False
        
        # Send notification
        try:
            slack_msg = f"🐕 Watchdog Alert ({self.node_name}): {message}"
            # pylint: disable=unexpected-keyword-arg,assignment-from-no-return
            success = send_slack_message(slack_msg, throttle=True, skip_hostname_prefix=True)
            if success:
                self.last_slack_notification[issue_type] = current_time
                logger.info(f"📢 Sent Slack notification for {issue_type}")
                return True
            else:
                logger.debug(f"⚠️  Failed to send Slack notification for {issue_type}")
                return False
        except Exception as e:
            logger.warning(f"⚠️  Error sending Slack notification: {e}")
            return False

    def restart_worker_train_es(self, reason_key: str, reason: str) -> bool:
        """Restart worker-train_es via supervisorctl."""
        return self.restart_training_workers(reason_key, reason, workers=['worker-train_es'])
    
    def restart_training_workers(self, reason_key: str, reason: str, workers: list = None) -> bool:
        """Restart training workers via supervisorctl. Defaults to both train_es and train_single_predictor."""
        if workers is None:
            workers = ['worker-train_es', 'worker-train_single_predictor']
        
        current_time = time.time()
        
        # Prevent restart spam - only restart once per 5 minutes
        if reason_key in self.last_restart_time:
            time_since_restart = current_time - self.last_restart_time[reason_key]
            if time_since_restart < 300:  # 5 minutes
                logger.warning(f"⏸️  Skipping restart - last restart was {int(time_since_restart)}s ago")
                return False
        
        all_succeeded = True
        for worker in workers:
            try:
                logger.warning(f"🔄 Restarting {worker}")
                logger.warning(f"   Reason: {reason}")
                
                result = subprocess.run(
                    ['supervisorctl', 'restart', worker],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ Successfully restarted {worker}")
                else:
                    logger.error(f"❌ Failed to restart {worker}: {result.stderr}")
                    all_succeeded = False
            except Exception as e:
                logger.error(f"❌ Error restarting {worker}: {e}")
                all_succeeded = False
        
        if all_succeeded:
            self.last_restart_time[reason_key] = current_time
            
            # Send Slack notification about worker restart
            workers_str = ', '.join(workers)
            self.send_slack_notification(
                "worker_restart",
                f"Restarted {workers_str}. Reason: {reason}"
            )
            
            return True
        else:
            # Send Slack notification about failed restart
            workers_str = ', '.join(workers)
            self.send_slack_notification(
                "worker_restart_failed",
                f"Failed to restart some workers ({workers_str}). Reason: {reason}"
            )
            return False

    def cleanup_orphaned_ready_jobs(self, min_age_hours: int = 1, max_age_days: int = 7) -> int:
        """
        Clean up orphaned READY jobs from Redis.
        
        Orphaned jobs are created when:
        - Workers restart and don't pick up previously queued jobs
        - Jobs are created but never dispatched
        - Celery queue gets corrupted
        
        Args:
            min_age_hours: Minimum age before deleting (default: 1 hour)
            max_age_days: Delete all READY jobs older than this (default: 7 days)
        
        Returns:
            Number of jobs deleted
        """
        try:
            from lib.job_manager import get_redis_client
            import json
            
            redis_client = get_redis_client()
            job_keys = redis_client.keys("job:*")
            
            now = datetime.now()
            deleted = 0
            
            for key in job_keys:
                job_data_json = redis_client.get(key)
                if not job_data_json:
                    continue
                
                try:
                    job = json.loads(job_data_json)
                    status = job.get('status', '')
                    
                    if status == 'ready':
                        created = job.get('created_at', '')
                        if created:
                            try:
                                created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                                age = now - created_dt.replace(tzinfo=None)
                                
                                # Delete if older than min_age_hours
                                if age > timedelta(hours=min_age_hours):
                                    job_type = job.get('job_type', job.get('type', 'unknown'))
                                    job_id = job.get('job_id', key.split(':')[1])[:8]
                                    
                                    if deleted < 5:  # Only log first 5 to avoid spam
                                        logger.info(f"   🗑️  Deleting orphaned {job_type} {job_id} ({age.days}d {age.seconds//3600}h old)")
                                    elif deleted == 5:
                                        logger.info(f"   ... (suppressing further delete logs)")
                                    
                                    redis_client.delete(key)
                                    deleted += 1
                            except:
                                pass
                except:
                    pass
            
            return deleted
        
        except Exception as e:
            logger.error(f"Error cleaning orphaned READY jobs: {e}")
            return 0
    
    def cleanup_old_orphaned_processes(self, max_age_seconds: int = 3600) -> int:
        """
        Proactively find and kill very old orphaned multiprocessing processes.
        This runs regardless of GPU RAM usage to prevent accumulation of orphaned processes.
        
        Args:
            max_age_seconds: Maximum age in seconds before considering a process old (default: 1 hour)
            
        Returns:
            Number of processes killed
        """
        try:
            import psutil
            orphaned = self.find_orphaned_multiprocess_workers()
            
            if not orphaned:
                return 0
            
            # Filter to only very old processes
            old_orphaned = []
            current_time = time.time()
            
            for pid, ppid, reason in orphaned:
                try:
                    proc = psutil.Process(pid)
                    # Get process creation time
                    create_time = proc.create_time()
                    age_seconds = current_time - create_time
                    
                    if age_seconds > max_age_seconds:
                        old_orphaned.append((pid, ppid, reason, age_seconds))
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if old_orphaned:
                logger.warning(f"🔍 Found {len(old_orphaned)} very old orphaned process(es) (> {max_age_seconds}s old)")
                killed_count = 0
                for pid, ppid, reason, age_seconds in old_orphaned:
                    try:
                        proc = psutil.Process(pid)
                        age_hours = age_seconds / 3600
                        
                        # CRITICAL: Check Redis heartbeat FIRST - active DataLoader workers post heartbeats
                        heartbeat = check_worker_heartbeat(pid)
                        if heartbeat:
                            job_id = heartbeat.get('job_id', 'unknown')
                            job_type = heartbeat.get('job_type', 'unknown')
                            worker_id = heartbeat.get('worker_id', '?')
                            logger.info(
                                f"✅ PID {pid} has active heartbeat - DataLoader worker {worker_id} for job {job_id[:12]}... "
                                f"({job_type}). NOT killing despite being flagged as orphaned."
                            )
                            continue  # Skip killing - this is an active worker
                        
                        # CRITICAL: Check for worker markers before killing
                        from pathlib import Path
                        traceback_file = Path(f"/tmp/traceback-{pid}")
                        finished_file = Path(f"/tmp/finished-worker-{pid}")
                        
                        # If worker finished cleanly, it should have been cleaned up by parent
                        # But if it's still running with a finished marker, something is wrong
                        if finished_file.exists():
                            logger.warning(
                                f"⚠️  PID {pid} has finished marker but still running - "
                                f"parent should have cleaned it up. Killing stale process."
                            )
                            # Safe to kill - it finished but wasn't cleaned up
                        elif traceback_file.exists():
                            # Worker crashed - safe to kill
                            try:
                                tb_content = traceback_file.read_text()[:500]  # First 500 chars
                                logger.warning(
                                    f"💥 PID {pid} has traceback marker (crashed) - safe to kill. "
                                    f"Error: {tb_content[:200]}..."
                                )
                            except Exception:
                                logger.warning(f"💥 PID {pid} has traceback marker (crashed) - safe to kill")
                        else:
                            # No markers - check if it's actually doing work
                            # CRITICAL: Verify process is not doing work before killing
                            # Check CPU usage over last few seconds to ensure it's idle
                            try:
                                # Get CPU percent (non-blocking, uses interval=0.1 for quick check)
                                cpu_percent = proc.cpu_percent(interval=0.1)
                                # Get memory info
                                memory_info = proc.memory_info()
                                memory_mb = memory_info.rss / (1024 * 1024)
                                
                                # If process is using significant CPU (>5%), it might be doing work
                                # But for orphaned multiprocessing workers, even 1% CPU over 1 hour suggests stuck/idle
                                # Real work would show higher CPU spikes
                                if cpu_percent > 5.0:
                                    logger.warning(
                                        f"⚠️  Skipping PID {pid} - still using {cpu_percent:.1f}% CPU "
                                        f"(may be doing work despite being orphaned, no markers found)"
                                    )
                                    continue
                                
                                # Log what we're about to kill
                                logger.warning(
                                    f"🔪 Killing very old orphaned process PID {pid} "
                                    f"(age: {age_hours:.1f} hours, CPU: {cpu_percent:.1f}%, "
                                    f"RAM: {memory_mb:.1f}MB, no markers, {reason})"
                                )
                            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                # Process already dead or inaccessible - skip
                                continue
                            except Exception as check_err:
                                # If we can't check CPU, log but still kill (better safe than sorry for orphans)
                                logger.debug(f"Could not check CPU for PID {pid}: {check_err}, killing anyway")
                        
                        proc.kill()
                        killed_count += 1
                        
                        # Clean up markers after killing
                        try:
                            if traceback_file.exists():
                                traceback_file.unlink()
                            if finished_file.exists():
                                finished_file.unlink()
                        except Exception:
                            pass
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                    except Exception as e:
                        logger.debug(f"Error killing old orphaned PID {pid}: {e}")
                
                if killed_count > 0:
                    logger.info(f"✅ Killed {killed_count} very old orphaned process(es)")
                    # Send Slack notification if we killed a significant number
                    if killed_count >= 5:
                        self.send_slack_notification(
                            "orphaned_workers_cleanup",
                            f"Cleaned up {killed_count} very old orphaned multiprocessing processes (> {max_age_seconds}s old)"
                        )
                
                return killed_count
            
            return 0
        except Exception as e:
            logger.debug(f"Error in cleanup_old_orphaned_processes: {e}")
            return 0

    def check_and_restart_if_needed(self):
        """Main check loop - monitors GPU RAM and kills orphaned multiprocess workers."""
        # First, proactively clean up very old orphaned processes (regardless of GPU RAM)
        self.cleanup_old_orphaned_processes(max_age_seconds=3600)  # 1 hour
        
        # Get GPU stats
        gpu_stats = self.get_gpu_stats()
        
        if not gpu_stats:
            logger.debug("GPU stats not available - skipping GPU check")
            return
        
        gpu_ram_percent = gpu_stats.get('memory_percent', 0)
        gpu_util = gpu_stats.get('gpu_utilization', 0)
        
        logger.debug(f"GPU RAM: {gpu_ram_percent:.1f}%, GPU Util: {gpu_util:.1f}%")
        
        # Check if GPU RAM is full (>95%)
        if gpu_ram_percent > 95.0:
            logger.warning(f"⚠️  GPU RAM is {gpu_ram_percent:.1f}% full - checking for orphaned workers...")
            
            # Find orphaned multiprocess workers
            orphaned = self.find_orphaned_multiprocess_workers()
            
            if orphaned:
                logger.warning(f"🔍 Found {len(orphaned)} orphaned multiprocessing process(es)")
                
                # Send Slack notification about orphaned workers
                self.send_slack_notification(
                    "orphaned_workers",
                    f"Found {len(orphaned)} orphaned multiprocessing process(es). GPU RAM: {gpu_ram_percent:.1f}%"
                )
                
                # DISABLED: The orphan detection logic is broken - it was killing legitimate
                # DataLoader workers from active training jobs. Need to fix the detection first.
                # See: https://github.com/featrix/taco-fixes - 2026-01-05 investigation
                # killed_count = self.kill_orphaned_workers(orphaned)
                killed_count = 0
                logger.warning("⚠️  Orphan killing DISABLED - detection logic needs fixing")
                
                if killed_count > 0:
                    logger.info(f"✅ Killed {killed_count} orphaned worker(s)")
                    
                    # Wait a moment and check GPU RAM again
                    time.sleep(5)
                    gpu_stats_after = self.get_gpu_stats()
                    if gpu_stats_after:
                        new_ram_percent = gpu_stats_after.get('memory_percent', 0)
                        logger.info(f"📊 GPU RAM after cleanup: {new_ram_percent:.1f}% (was {gpu_ram_percent:.1f}%)")
                        
                        # If still >95% and GPU utilization is low, restart all training workers
                        if new_ram_percent > 95.0 and gpu_util < 10.0:
                            logger.warning(f"🔄 GPU RAM still {new_ram_percent:.1f}% full with low utilization - restarting training workers")
                            self.restart_training_workers("gpu_ram_full", f"GPU RAM {new_ram_percent:.1f}% full, GPU util {gpu_util:.1f}%")
                else:
                    logger.warning("⚠️  No orphaned workers killed - GPU RAM may be held by active processes")
            else:
                logger.debug("✅ No orphaned workers found")
                
                # If GPU RAM is full and utilization is low, restart all training workers
                if gpu_util < 10.0:
                    logger.warning(f"🔄 GPU RAM {gpu_ram_percent:.1f}% full with low utilization ({gpu_util:.1f}%) - restarting training workers")
                    
                    # Send Slack notification about GPU RAM issue
                    self.send_slack_notification(
                        "gpu_ram_full",
                        f"GPU RAM {gpu_ram_percent:.1f}% full with low utilization ({gpu_util:.1f}%) - restarting training workers"
                    )
                    
                    self.restart_training_workers("gpu_ram_full_low_util", f"GPU RAM {gpu_ram_percent:.1f}% full, GPU util {gpu_util:.1f}%")
        else:
            logger.debug(f"GPU RAM at {gpu_ram_percent:.1f}% - no action needed")

    def get_current_training_job_info(self) -> Optional[Dict]:
        """Get info about the current training job (if any) by checking worker output directories."""
        try:
            # Find most recent train_es job output directory
            output_base = Path(config.output_dir)
            train_es_dir = output_base / "train_es"
            
            if not train_es_dir.exists():
                return None
            
            # Find most recently modified job directory
            job_dirs = sorted(
                [d for d in train_es_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            if not job_dirs:
                return None
            
            job_output_dir = job_dirs[0]
            job_id = job_output_dir.name
            
            # Get latest epoch
            latest_epoch = self.get_latest_epoch(job_output_dir)
            if latest_epoch is None:
                latest_epoch = 0
            
            # Calculate runtime from directory creation time
            runtime_seconds = int(time.time() - job_output_dir.stat().st_ctime)
            
            # Extract job name, rows, cols, and validation losses
            job_name = None
            num_rows = None
            num_columns = None
            initial_val_loss = None
            current_val_loss = None
            
            # Try to get session_id from job_id (format: {session_id}/{job_type}/{job_id}/)
            session_id = None
            if '/' in job_id:
                parts = job_id.split('/')
                if len(parts) >= 1:
                    session_id = parts[0]
            
            # Try to load session metadata
            if session_id:
                try:
                    session_file = Path("/sphere/app/featrix_sessions") / f"{session_id}.session"
                    if session_file.exists():
                        with open(session_file, 'r') as f:
                            session_data = json.load(f)
                            job_name = session_data.get('name')
                            if 'column_spec' in session_data:
                                num_columns = len(session_data['column_spec'])
                except Exception as e:
                    logger.debug(f"Error loading session metadata: {e}")
            
            # Try to get data info from structured data output
            if session_id:
                try:
                    session_dir = output_base.parent / "featrix_sessions" / session_id
                    create_sd_dir = session_dir / "create_structured_data"
                    if create_sd_dir.exists():
                        sd_jobs = sorted(create_sd_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
                        for sd_job in sd_jobs[:1]:
                            schema_file = sd_job / "schema_metadata.json"
                            if schema_file.exists():
                                with open(schema_file, 'r') as f:
                                    schema = json.load(f)
                                    if num_rows is None:
                                        num_rows = schema.get('total_rows')
                                    if num_columns is None:
                                        num_columns = schema.get('total_columns')
                except Exception as e:
                    logger.debug(f"Error loading schema metadata: {e}")
            
            # Try to get ES name from embedded_space.json
            es_file = job_output_dir / "embedded_space.json"
            if es_file.exists() and job_name is None:
                try:
                    with open(es_file, 'r') as f:
                        es_data = json.load(f)
                        job_name = es_data.get('name')
                except Exception as e:
                    logger.debug(f"Error loading embedded_space.json: {e}")
            
            # Extract validation losses from log file
            log_file = job_output_dir / "logs" / "stdout.log"
            if log_file.exists():
                try:
                    # Patterns to match validation loss
                    epoch_val_pattern = re.compile(r'\[epoch=(\d+)\].*?VAL LOSS:\s+([\d.]+)')
                    train_epoch_pattern = re.compile(r'Epoch (\d+)/\d+.*?validation_loss=([\d.]+)')
                    
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            # Try epoch pattern first
                            match = epoch_val_pattern.search(line)
                            if not match:
                                match = train_epoch_pattern.search(line)
                            
                            if match:
                                epoch = int(match.group(1))
                                val_loss = float(match.group(2))
                                if initial_val_loss is None:
                                    initial_val_loss = val_loss
                                if epoch >= latest_epoch:
                                    current_val_loss = val_loss
                except Exception as e:
                    logger.debug(f"Error extracting losses from log: {e}")
            
            result = {
                "job_id": job_id,
                "epochs": latest_epoch,
                "runtime_seconds": runtime_seconds
            }
            
            # Add optional fields if available
            if job_name:
                result["job_name"] = job_name
            if num_rows is not None:
                result["num_rows"] = num_rows
            if num_columns is not None:
                result["num_columns"] = num_columns
            if initial_val_loss is not None:
                result["initial_val_loss"] = initial_val_loss
            if current_val_loss is not None:
                result["current_val_loss"] = current_val_loss
            
            return result
        except Exception as e:
            logger.debug(f"Error getting training job info: {e}")
            return None

    def ping_sphere_api(self, training_info: Optional[Dict] = None):
        """Ping sphere-api /compute-nodes/announce endpoint with training info."""
        if not HAS_REQUESTS:
            return
        
        current_time = time.time()
        if current_time - self.last_announce_time < self.announce_interval:
            return  # Don't ping too frequently
        
        try:
            # Get version info if available
            version = "unknown"
            version_hash = "unknown"
            try:
                # Try importing from src/version module
                import sys
                from pathlib import Path
                src_path = Path(__file__).parent
                if str(src_path.resolve()) not in sys.path:
                    sys.path.insert(0, str(src_path.resolve()))
                
                from version import get_version
                version_info = get_version()
                version = version_info.semantic_version
                version_hash = version_info.git_hash[:8] if version_info.git_hash else "unknown"
            except (ImportError, AttributeError, Exception) as e:
                logger.debug(f"Could not get version info: {e}")
                # Fallback: try reading from files
                try:
                    version_file = Path("/sphere/VERSION")
                    if version_file.exists():
                        version = version_file.read_text().strip()
                    
                    # Try multiple locations for hash file (in order of preference)
                    hash_file = None
                    for hash_path in [
                        Path("/tmp/SPHERE_GIT_HASH"),
                        Path("/sphere/VERSION_HASH"),
                        Path("/sphere/app/VERSION_HASH"),
                    ]:
                        if hash_path.exists():
                            hash_file = hash_path
                            break
                    
                    if hash_file:
                        version_hash = hash_file.read_text().strip()[:8]
                except Exception:
                    pass
            
            # Map node name to port (fixed mapping for production nodes)
            # CRITICAL: Must match the actual ports nodes are running on
            node_port_mapping = {
                'taco': 8003,
                'churro': 8002,
                'burrito': 8004,
            }
            node_port = node_port_mapping.get(self.node_name, 8000)  # Default 8000 for unknown nodes
            
            # Get ALL network IPs and find the 192.168.x.x one (local ethernet IP)
            # CRITICAL: These nodes are on 192.168.10.x internal network
            main_local_ip_address = None
            try:
                import socket
                # Get hostname
                hostname = socket.gethostname()
                
                # Get ALL IP addresses for this hostname
                try:
                    # getaddrinfo returns all addresses
                    addr_info = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
                    all_ips = [addr[4][0] for addr in addr_info]
                    
                    # Look for 192.168.x.x address first (internal network)
                    for ip in all_ips:
                        if ip.startswith('192.168.'):
                            main_local_ip_address = ip
                            logger.debug(f"Found 192.168.x.x IP: {ip}")
                            break
                    
                    # If no 192.168.x.x, try 10.x.x.x (private network)
                    if not main_local_ip_address:
                        for ip in all_ips:
                            if ip.startswith('10.'):
                                main_local_ip_address = ip
                                logger.debug(f"Found 10.x.x.x IP: {ip}")
                                break
                    
                    # If no private IP, use first non-localhost
                    if not main_local_ip_address:
                        for ip in all_ips:
                            if not ip.startswith('127.'):
                                main_local_ip_address = ip
                                logger.debug(f"Found non-localhost IP: {ip}")
                                break
                    
                    logger.debug(f"All IPs found: {all_ips}, selected: {main_local_ip_address}")
                except Exception as e:
                    logger.debug(f"getaddrinfo failed: {e}, trying gethostbyname")
                    # Fallback to simple hostname resolution
                    main_local_ip_address = socket.gethostbyname(hostname)
            except Exception as e:
                logger.debug(f"Could not detect network IP: {e}")
            
            payload = {
                "node_name": self.node_name,
                "port": node_port,  # CRITICAL: Include port so sphere-api routes correctly
                "main_local_ip_address": main_local_ip_address,  # Local ethernet IP (192.168.x.x)
                "status": "available",
                "node_timestamp_now": datetime.now().isoformat(),
                "version": version,
                "version_hash": version_hash
            }
            
            # Add training info if available
            if training_info:
                payload["training_job"] = training_info
            
            # Ping sphere-api
            try:
                # Create custom User-Agent with version and hostname
                user_agent = f"Featrix Firmware v{version} ({self.node_name})"
                response = requests.post(
                    "https://sphere-api.featrix.com/compute-nodes/announce",
                    json=payload,
                    timeout=5,
                    headers={'User-Agent': user_agent}
                )
                if response.status_code == 200:
                    self.last_announce_time = current_time
                    logger.info(f"✅ Pinged sphere-api successfully (node: {self.node_name}, status: {payload.get('status')})")
                else:
                    logger.warning(f"⚠️  sphere-api ping returned {response.status_code}: {response.text[:200]}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to ping sphere-api: {e}", exc_info=True)
                
                # Log for retry
                try:
                    from lib.api_event_retry import get_retry_manager, EventType
                    retry_manager = get_retry_manager()
                    retry_manager.log_failed_event(
                        event_type=EventType.COMPUTE_NODE_ANNOUNCE,
                        url="https://sphere-api.featrix.com/compute-nodes/announce",
                        method="POST",
                        payload=payload,
                        timeout=5,
                        error=str(e),
                        metadata={"node_name": self.node_name}
                    )
                except Exception as retry_err:
                    logger.debug(f"Failed to log compute node announce for retry: {retry_err}")
        except Exception as e:
            logger.debug(f"Error pinging sphere-api: {e}")

    def check_redis_health(self) -> bool:
        """
        Check if Redis is running and responding.
        On production servers, Redis is CRITICAL - log errors if not available.
        
        Returns:
            True if Redis is healthy, False otherwise
        """
        try:
            import redis
            redis_client = redis.Redis(host='localhost', port=6379, db=1, socket_timeout=2, socket_connect_timeout=2)
            redis_client.ping()
            return True
        except ImportError:
            logger.error("❌ CRITICAL: Redis Python module not installed")
            logger.error("   Install with: pip install redis")
            return False
        except redis.ConnectionError as e:
            logger.error(f"❌ CRITICAL: Redis is not responding on localhost:6379")
            logger.error(f"   Error: {e}")
            logger.error(f"   Fix: systemctl start redis-server")
            logger.error(f"   Redis is REQUIRED for job tracking, Celery tasks, and movie generation")
            return False
        except Exception as e:
            logger.error(f"❌ CRITICAL: Unexpected Redis error: {e}")
            return False

    def check_api_server_health(self) -> bool:
        """
        Check if the FastAPI server is responding to /health endpoint.
        Uses user-agent "local watchdog" to identify health check requests.
        
        Returns:
            True if API server is healthy, False otherwise
        """
        if not HAS_REQUESTS:
            logger.debug("requests not available - cannot check API health")
            return True  # Don't fail if requests not available
        
        current_time = time.time()
        
        # Don't check too frequently
        if current_time - self.last_api_health_check < self.api_health_check_interval:
            return True  # Assume healthy if we checked recently
        
        self.last_api_health_check = current_time
        
        try:
            # Check localhost:8000/health with user-agent "local watchdog"
            health_url = "http://localhost:8000/health"
            response = requests.get(
                health_url,
                timeout=5,
                headers={'User-Agent': 'local watchdog'}
            )
            
            if response.status_code == 200:
                try:
                    health_data = response.json()
                    status = health_data.get('status', 'unknown')
                    if status == 'healthy':
                        logger.debug("✅ API server health check passed")
                        return True
                    else:
                        logger.warning(f"⚠️  API server health check returned status: {status}")
                        return False
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"⚠️  API server health check returned invalid JSON: {e}")
                    return False
            else:
                logger.warning(f"⚠️  API server health check returned status code: {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.warning("⚠️  API server health check timed out (server may be wedged)")
            return False
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  API server health check connection error (server may be down)")
            return False
        except Exception as e:
            logger.warning(f"⚠️  API server health check failed: {e}")
            return False
    
    def restart_api_server(self) -> bool:
        """
        Restart the API server via supervisorctl.
        Prevents restart spam - only restarts once per 5 minutes.
        
        Returns:
            True if restart was successful or skipped (rate limited), False if failed
        """
        current_time = time.time()
        
        # Prevent restart spam - only restart once per 5 minutes
        if self.last_api_restart_time > 0:
            time_since_restart = current_time - self.last_api_restart_time
            if time_since_restart < 300:  # 5 minutes
                logger.warning(f"⏸️  Skipping API server restart - last restart was {int(time_since_restart)}s ago")
                return True
        
        try:
            logger.warning("🔄 Restarting API server (api supervisor task)")
            
            # Try both possible supervisor program names
            # The config shows [program:api] but it might be in a group
            restart_result = subprocess.run(
                ['supervisorctl', 'restart', 'api'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if restart_result.returncode == 0:
                logger.info("✅ Successfully restarted API server")
                self.last_api_restart_time = current_time
                
                # Send Slack notification
                self.send_slack_notification(
                    "api_server_restart",
                    f"API server was wedged/unhealthy and was auto-restarted by watchdog"
                )
                return True
            else:
                # Try with group prefix
                logger.debug("Trying with group prefix...")
                restart_result = subprocess.run(
                    ['supervisorctl', 'restart', 'featrix-firmware:api'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if restart_result.returncode == 0:
                    logger.info("✅ Successfully restarted API server (with group prefix)")
                    self.last_api_restart_time = current_time
                    
                    # Send Slack notification
                    self.send_slack_notification(
                        "api_server_restart",
                        f"API server was wedged/unhealthy and was auto-restarted by watchdog"
                    )
                    return True
                else:
                    logger.error(f"❌ Failed to restart API server: {restart_result.stderr}")
                    self.send_slack_notification(
                        "api_server_restart_failed",
                        f"API server health check failed but restart attempt failed: {restart_result.stderr}"
                    )
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Error restarting API server: {e}")
            self.send_slack_notification(
                "api_server_restart_failed",
                f"API server health check failed but restart attempt failed: {e}"
            )
            return False

    def check_celery_workers(self) -> bool:
        """Check if Celery workers are running, restart if down (unless /DISABLE exists or upgrade in progress)."""
        # Check for /DISABLE flag - skip worker monitoring if it exists
        disable_flag = Path("/sphere/DISABLE")
        if disable_flag.exists():
            logger.debug("✅ /DISABLE flag exists - skipping Celery worker check")
            return True
        
        # Check if upgrade is in progress - don't restart workers during upgrade
        upgrade_lock = Path("/tmp/auto-upgrade.lock")
        upgrade_flag = Path("/tmp/UPGRADE_SPHERE")
        if upgrade_lock.exists() or upgrade_flag.exists():
            logger.info("⚠️  Upgrade in progress - skipping Celery worker auto-restart")
            if upgrade_lock.exists():
                logger.info(f"   Upgrade lock file exists: {upgrade_lock}")
            if upgrade_flag.exists():
                logger.info(f"   Upgrade flag file exists: {upgrade_flag}")
            return True
        
        try:
            import subprocess
            # Check supervisor status for Celery workers
            # Note: supervisor program names are 'featrix-firmware:cpu', 'featrix-firmware:gpu', and 'featrix-firmware:movie'
            result = subprocess.run(
                ['supervisorctl', 'status', 'featrix-firmware:cpu', 'featrix-firmware:gpu', 'featrix-firmware:movie'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # Check if this is "no such process" error (workers not registered in supervisor yet)
                output_text = (result.stdout or "") + (result.stderr or "")
                if "no such process" in output_text.lower():
                    # Workers aren't registered in supervisor yet - this is OK, supervisor just needs reload
                    # Check celery workers directly via celery inspect instead
                    logger.debug(f"⚠️  Workers not registered in supervisor yet (supervisor needs reload)")
                    logger.debug(f"   Checking celery workers directly via celery inspect...")
                    
                    # Fall back to celery inspect to check if workers are actually running
                    try:
                        from celery_app import app
                        inspect = app.control.inspect(timeout=2)
                        active_queues = inspect.active_queues() or {}
                        
                        # Check if we have workers for the queues we care about
                        cpu_worker_running = False
                        gpu_worker_running = False
                        movie_worker_running = False
                        
                        for worker_name, queues in active_queues.items():
                            for queue_info in queues:
                                queue_name = queue_info.get('name', '')
                                if 'cpu_worker' in queue_name or 'cpu' in worker_name.lower():
                                    cpu_worker_running = True
                                if 'gpu_training' in queue_name or 'gpu' in worker_name.lower():
                                    gpu_worker_running = True
                                if 'movie_generation' in queue_name or 'movie' in worker_name.lower():
                                    movie_worker_running = True
                        
                        # If workers are running via celery, that's fine - supervisor just needs reload
                        if cpu_worker_running and gpu_worker_running:
                            logger.debug(f"✅ Celery workers are running (supervisor just needs reload)")
                            return True  # Workers are OK, just not registered in supervisor
                        else:
                            logger.warning(f"⚠️  Some celery workers not running (cpu={cpu_worker_running}, gpu={gpu_worker_running}, movie={movie_worker_running})")
                            # Continue to check supervisor status below
                    except Exception as celery_err:
                        logger.debug(f"   Could not check celery workers: {celery_err}")
                    
                    # If celery check failed or workers aren't running, treat as supervisor error
                    output = ""  # Empty output means we couldn't check
                else:
                    # Real error - log and return True (assume workers are OK to avoid false alarms)
                    logger.warning(f"⚠️  Could not check worker status (rc={result.returncode})")
                    if result.stderr:
                        logger.warning(f"   stderr: {result.stderr}")
                    if result.stdout:
                        logger.warning(f"   stdout: {result.stdout}")
                    return True
            else:
                output = result.stdout
            
            output = result.stdout
            # Parse supervisorctl status output line by line
            # Format: "cpu                              RUNNING   pid 12345, uptime 0:05:00"
            cpu_worker_down = True  # Default to down unless we find it running
            gpu_worker_down = True  # Default to down unless we find it running
            movie_worker_down = True  # Default to down unless we find it running
            
            for line in output.split('\n'):
                line = line.strip()
                if 'featrix-firmware:cpu' in line or line.startswith('cpu'):
                    cpu_worker_down = 'RUNNING' not in line
                elif 'featrix-firmware:gpu' in line or line.startswith('gpu'):
                    gpu_worker_down = 'RUNNING' not in line
                elif 'featrix-firmware:movie' in line or line.startswith('movie'):
                    movie_worker_down = 'RUNNING' not in line
            
            if cpu_worker_down or gpu_worker_down or movie_worker_down:
                workers_down = []
                if cpu_worker_down:
                    workers_down.append('cpu')
                if gpu_worker_down:
                    workers_down.append('gpu')
                if movie_worker_down:
                    workers_down.append('movie')
                
                logger.error(f"❌ CRITICAL: Celery workers are DOWN: {workers_down}")
                logger.error(f"   Auto-restarting workers (create /sphere/DISABLE to prevent this)...")
                
                # Restart the down workers
                for worker in workers_down:
                    try:
                        # Use full supervisor program name format
                        supervisor_program = f'featrix-firmware:{worker}'
                        restart_result = subprocess.run(
                            ['supervisorctl', 'start', supervisor_program],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if restart_result.returncode == 0:
                            logger.info(f"✅ Auto-restarted {worker}")
                        else:
                            logger.error(f"❌ Failed to auto-restart {worker}: {restart_result.stderr}")
                    except Exception as e:
                        logger.error(f"❌ Error auto-restarting {worker}: {e}")
                
                # Send Slack notification
                self.send_slack_notification(
                    "celery_workers_auto_restart",
                    f"Celery workers were DOWN and auto-restarted by watchdog: {', '.join(workers_down)}"
                )
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Could not check Celery worker status: {e}")
            return True  # Non-critical, continue
    
    def _get_running_jobs_from_celery(self) -> list:
        """Get all jobs marked as RUNNING in Celery/Redis."""
        try:
            from lib.session_manager import iterate_over_sessions
            running_jobs = []
            
            # Iterate over all sessions
            for session in iterate_over_sessions():
                try:
                    session_id = session.get('session_id')
                    if not session_id:
                        continue
                    
                    jobs = session.get('jobs', [])
                    for job in jobs:
                        if job.get('status') == 'RUNNING':
                            running_jobs.append({
                                'job_id': job.get('job_id'),
                                'job_type': job.get('job_type'),
                                'session_id': session_id,
                                'started_at': job.get('started_at'),
                                'job': job
                            })
                except Exception as e:
                    logger.debug(f"Error processing session: {e}")
                    continue
            
            return running_jobs
        except Exception as e:
            logger.error(f"Failed to get running jobs: {e}")
            return []
    
    def _find_job_directory(self, job_id: str) -> Optional[Path]:
        """Find the output directory for a job."""
        # Common output locations
        search_paths = [
            Path("/sphere/app/featrix_output"),
            Path("/featrix-output"),
            Path("/sphere/featrix_data"),
        ]
        
        for base_path in search_paths:
            if not base_path.exists():
                continue
            
            # Search recursively for job directory
            try:
                result = subprocess.run(
                    ['find', str(base_path), '-type', 'd', '-name', f'*{job_id[:8]}*'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    paths = result.stdout.strip().split('\n')
                    for path in paths:
                        if job_id in path:
                            return Path(path)
            except Exception as e:
                logger.debug(f"Error searching {base_path}: {e}")
                continue
        
        return None
    
    def _get_latest_mtime(self, directory: Path) -> float:
        """Get the most recent modification time in a directory tree."""
        try:
            result = subprocess.run(
                ['find', str(directory), '-type', 'f', '-printf', '%T@\n'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                mtimes = [float(t) for t in result.stdout.strip().split('\n') if t]
                return max(mtimes) if mtimes else 0.0
        except Exception:
            pass
        
        # Fallback: check directory mtime
        try:
            return directory.stat().st_mtime
        except:
            return 0.0
    
    def _diagnose_zombie_cause(self, job_id: str, job_dir: Optional[Path] = None) -> list:
        """Check system logs and job logs to find why job died."""
        reasons = []
        
        # Check for GPU errors in dmesg
        try:
            result = subprocess.run(
                ['dmesg', '-T'],
                capture_output=True,
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            if result.returncode == 0:
                dmesg = result.stdout
                
                # Check for GPU Xid errors
                if 'NVRM: Xid' in dmesg:
                    xid_lines = [line for line in dmesg.split('\n') if 'NVRM: Xid' in line and 'python' in line.lower()]
                    if xid_lines:
                        # Check for Xid 43 (GPU fell off bus)
                        if any(': 43,' in line for line in xid_lines):
                            reasons.append('GPU_HARDWARE_FAILURE_XID_43')
                        else:
                            reasons.append('GPU_ERROR')
                
                # Check for OOM killer
                if job_id[:8] in dmesg or 'Out of memory' in dmesg:
                    oom_lines = [line for line in dmesg.split('\n') if 'Out of memory' in line or 'oom-killer' in line.lower()]
                    if oom_lines:
                        reasons.append('OOM_KILLED')
        except Exception as e:
            logger.debug(f"Could not check dmesg: {e}")
        
        # Check job logs for crashes
        if job_dir and job_dir.exists():
            log_file = job_dir / 'logs' / 'stdout.log'
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        # Read last 50 lines
                        f.seek(0, 2)  # Go to end
                        file_size = f.tell()
                        f.seek(max(0, file_size - 10000))  # Read last ~10KB
                        last_content = f.read()
                    
                    if 'CUDA' in last_content or 'GPU' in last_content:
                        if 'out of memory' in last_content.lower():
                            reasons.append('CUDA_OOM')
                        else:
                            reasons.append('CUDA_ERROR')
                    if 'Killed' in last_content:
                        reasons.append('PROCESS_KILLED')
                    if 'Segmentation fault' in last_content or 'segfault' in last_content.lower():
                        reasons.append('SEGFAULT')
                    if 'Exception' in last_content and 'Traceback' in last_content:
                        reasons.append('PYTHON_EXCEPTION')
                except Exception as e:
                    logger.debug(f"Could not read log file {log_file}: {e}")
        
        return reasons if reasons else ['UNKNOWN']
    
    def detect_zombie_jobs(self) -> list:
        """
        Detect jobs marked RUNNING but with no actual process.
        
        A zombie job is:
        1. Status = RUNNING in database/Redis
        2. No matching Python process (ps aux)
        3. No log updates for > stuck_threshold seconds
        
        Returns:
            List of zombie job info dicts
        """
        try:
            # Get all RUNNING jobs
            running_jobs = self._get_running_jobs_from_celery()
            if not running_jobs:
                return []
            
            # Get all actual Python/training processes
            try:
                ps_result = subprocess.run(
                    ['ps', 'aux'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                ps_output = ps_result.stdout if ps_result.returncode == 0 else ""
            except Exception as e:
                logger.error(f"Failed to get process list: {e}")
                return []
            
            zombies = []
            
            for job_info in running_jobs:
                job_id = job_info['job_id']
                
                # Check 1: Is there a process for this job?
                # Look for job_id in process list (either full ID or first 8 chars)
                has_process = (job_id in ps_output) or (job_id[:8] in ps_output)
                
                # Check 2: Find job directory and check last activity
                job_dir = self._find_job_directory(job_id)
                
                last_activity_time = 0.0
                dir_modified_recently = False
                
                if job_dir and job_dir.exists():
                    latest_mtime = self._get_latest_mtime(job_dir)
                    last_activity_time = latest_mtime
                    dir_modified_recently = (time.time() - latest_mtime) < 300  # 5 min
                
                time_since_activity = time.time() - last_activity_time if last_activity_time > 0 else float('inf')
                
                # ZOMBIE DETECTION
                # Job is zombie if:
                # 1. No process exists for it
                # 2. No file activity for > stuck_threshold
                # 3. Has been "running" for at least 60 seconds (not just started)
                started_at_str = job_info.get('started_at', '')
                job_age = 0
                try:
                    if started_at_str:
                        from dateutil import parser
                        started_at = parser.parse(started_at_str)
                        job_age = (datetime.now(started_at.tzinfo) - started_at).total_seconds()
                except Exception:
                    job_age = 0
                
                is_zombie = (
                    not has_process and
                    time_since_activity > self.stuck_threshold and
                    job_age > 60  # Must be at least 1 minute old
                )
                
                if is_zombie:
                    # Diagnose why it died
                    reasons = self._diagnose_zombie_cause(job_id, job_dir)
                    
                    zombie_info = {
                        'job_id': job_id,
                        'job_type': job_info['job_type'],
                        'session_id': job_info['session_id'],
                        'started_at': started_at_str,
                        'last_activity': last_activity_time,
                        'time_stuck': time_since_activity,
                        'job_age': job_age,
                        'has_process': has_process,
                        'dir_active': dir_modified_recently,
                        'job_dir': str(job_dir) if job_dir else None,
                        'reason': reasons
                    }
                    zombies.append(zombie_info)
            
            return zombies
            
        except Exception as e:
            logger.error(f"Error in zombie job detection: {e}", exc_info=True)
            return []
    
    def auto_fail_zombie_jobs(self, zombies: list, dry_run: bool = False) -> int:
        """Automatically fail zombie jobs and clean up."""
        if not zombies:
            return 0
        
        failed_count = 0
        
        for zombie in zombies:
            job_id = zombie['job_id']
            reasons = zombie['reason']
            
            logger.warning(f"🧟 ZOMBIE JOB DETECTED: {job_id[:12]}...")
            logger.warning(f"   Type: {zombie['job_type']}")
            logger.warning(f"   Session: {zombie['session_id']}")
            logger.warning(f"   Stuck for: {zombie['time_stuck']:.0f}s ({zombie['time_stuck']/60:.1f} min)")
            logger.warning(f"   Cause: {', '.join(reasons)}")
            logger.warning(f"   Job directory: {zombie['job_dir']}")
            
            if dry_run:
                logger.info(f"   [DRY RUN] Would auto-fail this job")
                continue
            
            # Auto-fail the job
            try:
                from lib.job_manager import update_job_status, JobStatus
                
                error_msg = f"Auto-failed by watchdog: Process died without logging error. Diagnostic: {', '.join(reasons)}. Job was stuck for {zombie['time_stuck']:.0f}s with no process activity."
                
                update_job_status(
                    job_id=job_id,
                    status=JobStatus.FAILED,
                    metadata={'error': error_msg}
                )
                
                logger.info(f"   ✅ Auto-failed zombie job {job_id[:12]}...")
                failed_count += 1
                
                # Send Slack notification
                self.send_slack_notification(
                    "zombie_job_auto_failed",
                    f"Zombie job auto-failed: {zombie['job_type']} ({job_id[:12]}...) - Cause: {', '.join(reasons)}"
                )
                
                # Alert if GPU hardware failure
                if 'GPU_HARDWARE_FAILURE' in reasons or 'GPU_HARDWARE_FAILURE_XID_43' in reasons:
                    self._alert_gpu_hardware_failure(zombie)
                    
            except Exception as e:
                logger.error(f"   ❌ Failed to auto-fail zombie {job_id[:12]}...: {e}")
        
        return failed_count
    
    def _alert_gpu_hardware_failure(self, zombie_info: dict):
        """Alert admins when GPU hardware failure is detected."""
        logger.error("=" * 80)
        logger.error("🚨 GPU HARDWARE FAILURE DETECTED")
        logger.error("=" * 80)
        logger.error(f"Job {zombie_info['job_id'][:12]}... died due to GPU hardware failure")
        logger.error("This indicates the GPU may be failing and needs attention")
        logger.error("Recommendation: Check GPU health, consider disabling GPU training")
        logger.error("=" * 80)
        
        # Write alert file for dashboard/monitoring
        try:
            alert_file = Path('/tmp/FEATRIX_GPU_FAILURE_ALERT')
            alert_data = {
                'timestamp': time.time(),
                'zombie_job': zombie_info,
                'recommendation': 'GPU hardware failure detected - check nvidia-smi, check dmesg for Xid errors',
                'action_required': 'May need to reboot server or replace GPU'
            }
            with open(alert_file, 'w') as f:
                json.dump(alert_data, f, indent=2)
            logger.error(f"Alert written to {alert_file}")
        except Exception as e:
            logger.error(f"Failed to write GPU alert file: {e}")
        
        # Send urgent Slack notification
        self.send_slack_notification(
            "gpu_hardware_failure",
            f"🚨 GPU HARDWARE FAILURE on {self.node_name}: Job {zombie_info['job_id'][:12]}... killed by GPU Xid 43 error. GPU may be dying. Action required!"
        )



    def check_for_stuck_jobs(self) -> list:
        """
        Check for jobs that are still processing but making no progress.
        
        A stuck job is:
        1. Status = RUNNING
        2. Has an active process
        3. But no epoch/file progress for > stuck_threshold
        
        Returns:
            List of stuck job info dicts
        """
        try:
            running_jobs = self._get_running_jobs_from_celery()
            if not running_jobs:
                return []
            
            stuck_jobs = []
            
            for job_info in running_jobs:
                job_id = job_info['job_id']
                job_type = job_info['job_type']
                
                # Find job directory
                job_dir = self._find_job_directory(job_id)
                if not job_dir or not job_dir.exists():
                    continue
                
                # Check for training status file
                status_file = None
                for possible_name in ['training_status.json', 'single_predictor_training_status.json', 'es_training_status.json']:
                    potential_file = job_dir / possible_name
                    if potential_file.exists():
                        status_file = potential_file
                        break
                
                if not status_file:
                    continue
                
                try:
                    with open(status_file, 'r') as f:
                        status_data = json.load(f)
                    
                    current_epoch = status_data.get('epoch', 0)
                    last_update = status_file.stat().st_mtime
                    time_since_update = time.time() - last_update
                    
                    # Check if we've seen this job before
                    last_check = self.last_epoch_check.get(job_id)
                    
                    if last_check:
                        last_epoch, last_time = last_check
                        
                        # If epoch hasn't changed and enough time has passed, it's stuck
                        if current_epoch == last_epoch and time_since_update > self.stuck_threshold:
                            stuck_jobs.append({
                                'job_id': job_id,
                                'job_type': job_type,
                                'session_id': job_info['session_id'],
                                'current_epoch': current_epoch,
                                'time_stuck': time_since_update,
                                'job_dir': str(job_dir)
                            })
                    
                    # Update tracking
                    self.last_epoch_check[job_id] = (current_epoch, time.time())
                    
                except Exception as e:
                    logger.debug(f"Error checking job {job_id}: {e}")
                    continue
            
            return stuck_jobs
            
        except Exception as e:
            logger.error(f"Error in stuck job detection: {e}", exc_info=True)
            return []
    
    def alert_stuck_jobs(self, stuck_jobs: list) -> int:
        """Send alerts for stuck jobs without failing them."""
        if not stuck_jobs:
            return 0
        
        alerted_count = 0
        
        for stuck in stuck_jobs:
            job_id = stuck['job_id']
            
            logger.warning(f"🐌 STUCK JOB DETECTED: {job_id[:12]}...")
            logger.warning(f"   Type: {stuck['job_type']}")
            logger.warning(f"   Epoch: {stuck['current_epoch']}")
            logger.warning(f"   Stuck for: {stuck['time_stuck']:.0f}s ({stuck['time_stuck']/60:.1f} min)")
            logger.warning(f"   Job directory: {stuck['job_dir']}")
            logger.warning(f"   Note: Job has active process but is making no progress")
            
            # Send Slack notification (rate-limited)
            self.send_slack_notification(
                "stuck_job_detected",
                f"🐌 Stuck job: {stuck['job_type']} ({job_id[:12]}...) - Epoch {stuck['current_epoch']} for {stuck['time_stuck']/60:.1f} min. May need manual intervention."
            )
            alerted_count += 1
        
        return alerted_count
    

    def run(self):
        """Main watchdog loop - monitors training jobs, GPU, orphaned workers, Redis health, AND Celery worker availability."""
        logger.info("🐕 Featrix Training Watchdog started")
        logger.info("   Monitoring:")
        logger.info("     - Redis health (CRITICAL)")
        logger.info("     - API server health (/health endpoint)")
        logger.info("     - Celery worker availability")
        logger.info("     - Zombie jobs (RUNNING but no process)")
        logger.info("     - Stuck jobs (has process but no progress)")
        logger.info("     - Orphaned READY jobs (stuck in queue)")
        logger.info("     - GPU RAM and orphaned workers")
        logger.info(f"   Check interval: {self.check_interval}s")
        logger.info(f"   Stuck threshold: {self.stuck_threshold}s")
        logger.info(f"   API health check: every {self.api_health_check_interval}s")
        logger.info(f"   Worker auto-restart: enabled (create /sphere/DISABLE to disable)")
        logger.info("")
        
        try:
            while True:
                try:
                    # Check Redis health FIRST - it's critical for everything else
                    redis_healthy = self.check_redis_health()
                    if not redis_healthy:
                        logger.error("⚠️  Redis health check FAILED - system may be degraded")
                    
                    # Check API server health and restart if wedged
                    api_healthy = self.check_api_server_health()
                    if not api_healthy:
                        logger.error("❌ API server health check FAILED - server may be wedged")
                        self.restart_api_server()
                    
                    # Check if Celery workers are running, restart if down
                    self.check_celery_workers()
                    
                    # Clean up orphaned READY jobs (stuck in queue after worker restart)
                    orphaned_count = self.cleanup_orphaned_ready_jobs()
                    if orphaned_count > 0:
                        logger.info(f"🗑️  Cleaned {orphaned_count} orphaned READY job(s) from Redis")
                    
                    # Check for zombie jobs (RUNNING status but no process)
                    zombie_jobs = self.detect_zombie_jobs()
                    if zombie_jobs:
                        logger.warning(f"🧟 Found {len(zombie_jobs)} zombie job(s)")
                        failed_count = self.auto_fail_zombie_jobs(zombie_jobs, dry_run=False)
                        logger.info(f"✅ Auto-failed {failed_count} zombie job(s)")
                    
                    # Check for stuck jobs (has process but no progress) 
                    stuck_jobs = self.check_for_stuck_jobs()
                    if stuck_jobs:
                        logger.warning(f"🐌 Found {len(stuck_jobs)} stuck job(s)")
                        alerted_count = self.alert_stuck_jobs(stuck_jobs)
                        logger.info(f"📢 Sent {alerted_count} stuck job alert(s)")
                    
                    # Check for stuck training jobs and GPU issues
                    self.check_and_restart_if_needed()
                    
                    # Get current training job info and ping sphere-api
                    training_info = self.get_current_training_job_info()
                    self.ping_sphere_api(training_info)
                except Exception as e:
                    logger.error(f"Error in watchdog check: {e}", exc_info=True)
                
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("Watchdog stopped by user")
        except Exception as e:
            logger.error(f"Fatal error in watchdog: {e}", exc_info=True)
            sys.exit(1)


def main():
    import socket
    hostname = socket.gethostname()
    logger.info("=" * 80)
    logger.info(f"🚀 FEATRIX WATCHDOG STARTING - {datetime.now().isoformat()}")
    logger.info("=" * 80)
    logger.info(f"Hostname: {hostname}")
    
    # Install Featrix exception hook for better error tracking
    try:
        from lib.featrix_debug import install_featrix_excepthook
        install_featrix_excepthook()
    except Exception:
        pass  # Don't fail if debug module not available
    
    parser = argparse.ArgumentParser(description='Featrix Training Watchdog')
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--stuck-threshold',
        type=int,
        default=300,
        help='Seconds without epoch progress before considering stuck (default: 300)'
    )
    
    args = parser.parse_args()
    
    logger.info(f"Check interval: {args.interval} seconds")
    logger.info(f"Stuck threshold: {args.stuck_threshold} seconds")
    logger.info("=" * 80)
    
    watchdog = TrainingWatchdog(
        check_interval=args.interval,
        stuck_threshold=args.stuck_threshold
    )
    watchdog.run()


if __name__ == '__main__':
    main()

