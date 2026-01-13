#!/usr/bin/env python3
"""
System health monitoring for memory pressure, disk errors, and kernel OOM events.

This module provides real-time monitoring of:
- System RAM usage and memory pressure
- GPU VRAM usage and per-process GPU utilization
- Kernel OOM events from dmesg
- Disk errors from dmesg
- Process-level memory consumption
- DataLoader worker process memory (logged every 30 seconds during training)
"""
import logging
import os
import psutil
import subprocess
import re
import torch
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# Module-level tracking for worker memory logging (shared across all instances)
_last_worker_memory_log_time = 0
_worker_memory_log_interval = 30  # Log every 30 seconds


class SystemHealthMonitor:
    """
    Monitor system health metrics including memory pressure, OOM events, and disk errors.
    """
    
    def __init__(self, job_id: str = None):
        self.job_id = job_id
        self.last_dmesg_check = None
        self.oom_events_seen = set()  # Track which OOM events we've already logged
        self.disk_errors_seen = set()
        
    def check_memory_pressure(self) -> Dict:
        """
        Check system memory pressure and return detailed stats.
        
        Returns:
            dict with keys:
                - total_ram_gb: Total system RAM
                - available_ram_gb: Available RAM (accounts for cache/buffers)
                - used_ram_gb: Used RAM
                - percent_used: Percentage of RAM used
                - swap_total_gb: Total swap space
                - swap_used_gb: Used swap
                - swap_percent: Percentage of swap used
                - pressure_level: 'low', 'medium', 'high', 'critical'
                - warning: Human-readable warning message if pressure is high
        """
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            total_ram = mem.total / (1024**3)
            available_ram = mem.available / (1024**3)
            used_ram = mem.used / (1024**3)
            percent_used = mem.percent
            
            swap_total = swap.total / (1024**3)
            swap_used = swap.used / (1024**3)
            swap_percent = swap.percent
            
            # Determine pressure level
            if percent_used < 70:
                pressure = 'low'
                warning = None
            elif percent_used < 85:
                pressure = 'medium'
                warning = f"Memory pressure moderate: {percent_used:.1f}% RAM used, {available_ram:.1f}GB available"
            elif percent_used < 95:
                pressure = 'high'
                warning = f"⚠️  HIGH memory pressure: {percent_used:.1f}% RAM used, only {available_ram:.1f}GB available"
            else:
                pressure = 'critical'
                warning = f"🚨 CRITICAL memory pressure: {percent_used:.1f}% RAM used, only {available_ram:.1f}GB available - OOM imminent!"
            
            # Check swap usage
            if swap_percent > 50 and swap_total > 0:
                if warning:
                    warning += f" | Swap: {swap_percent:.1f}% used ({swap_used:.1f}/{swap_total:.1f}GB)"
                else:
                    warning = f"⚠️  Swap usage high: {swap_percent:.1f}% ({swap_used:.1f}/{swap_total:.1f}GB)"
            
            return {
                'total_ram_gb': total_ram,
                'available_ram_gb': available_ram,
                'used_ram_gb': used_ram,
                'percent_used': percent_used,
                'swap_total_gb': swap_total,
                'swap_used_gb': swap_used,
                'swap_percent': swap_percent,
                'pressure_level': pressure,
                'warning': warning,
            }
        except Exception as e:
            logger.error(f"Failed to check memory pressure: {e}")
            return None
    
    def check_process_memory(self, pid: int = None) -> Dict:
        """
        Check memory usage for current process or specified PID.
        
        Args:
            pid: Process ID to check (None = current process)
            
        Returns:
            dict with keys:
                - pid: Process ID
                - rss_gb: Resident Set Size (actual RAM used)
                - vms_gb: Virtual Memory Size
                - percent: Percent of system RAM
                - num_threads: Number of threads
                - num_fds: Number of open file descriptors
        """
        try:
            if pid is None:
                pid = os.getpid()
            
            process = psutil.Process(pid)
            mem_info = process.memory_info()
            
            rss_gb = mem_info.rss / (1024**3)  # Resident Set Size (actual RAM)
            vms_gb = mem_info.vms / (1024**3)  # Virtual Memory Size
            percent = process.memory_percent()
            
            num_threads = process.num_threads()
            
            # Count file descriptors
            try:
                num_fds = process.num_fds()
            except:
                num_fds = None  # Not available on all platforms
            
            return {
                'pid': pid,
                'rss_gb': rss_gb,
                'vms_gb': vms_gb,
                'percent': percent,
                'num_threads': num_threads,
                'num_fds': num_fds,
            }
        except Exception as e:
            logger.error(f"Failed to check process memory for PID {pid}: {e}")
            return None
    
    def check_dmesg_for_oom(self) -> List[Dict]:
        """
        Check dmesg for recent OOM killer events.
        
        Returns:
            List of OOM events, each with:
                - timestamp: When the OOM occurred
                - victim_process: Process name that was killed
                - victim_pid: PID that was killed
                - message: Full dmesg message
        """
        try:
            # Run dmesg to get kernel messages
            # Use -T for human-readable timestamps
            result = subprocess.run(
                ['dmesg', '-T'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                # Try without -T (some systems don't support it)
                result = subprocess.run(
                    ['dmesg'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            
            if result.returncode != 0:
                logger.debug(f"dmesg failed with return code {result.returncode}")
                return []
            
            dmesg_output = result.stdout
            
            # Parse for OOM killer messages
            # Pattern: "Out of memory: Killed process <pid> (<name>)"
            oom_events = []
            oom_pattern = re.compile(
                r'(.*?)\s+.*?Out of memory.*?Killed process (\d+) \(([^)]+)\)',
                re.IGNORECASE
            )
            
            for line in dmesg_output.split('\n'):
                match = oom_pattern.search(line)
                if match:
                    timestamp_str = match.group(1)
                    pid = match.group(2)
                    process_name = match.group(3)
                    
                    # Create unique ID for this event (to avoid duplicate logging)
                    event_id = f"{timestamp_str}_{pid}_{process_name}"
                    
                    if event_id not in self.oom_events_seen:
                        self.oom_events_seen.add(event_id)
                        oom_events.append({
                            'timestamp': timestamp_str,
                            'victim_pid': pid,
                            'victim_process': process_name,
                            'message': line.strip(),
                            'event_id': event_id,
                        })
            
            return oom_events
            
        except subprocess.TimeoutExpired:
            logger.warning("dmesg check timed out")
            return []
        except PermissionError:
            logger.debug("Permission denied for dmesg (requires root/sudo)")
            return []
        except FileNotFoundError:
            logger.debug("dmesg command not found")
            return []
        except Exception as e:
            logger.debug(f"Failed to check dmesg for OOM events: {e}")
            return []
    
    def find_dataloader_workers(self, parent_pid: int = None) -> List[Dict]:
        """
        Find DataLoader worker processes by checking child processes of the parent.
        
        DataLoader workers are spawned as child processes and typically have:
        - Parent PID matching the training process
        - Python processes (cmdline contains python)
        - Lower memory usage than the main training process
        
        Args:
            parent_pid: Parent process ID (None = current process)
            
        Returns:
            List of dicts with worker process info:
            {
                'pid': int,
                'ppid': int,
                'rss_gb': float,
                'vms_gb': float,
                'percent': float,
                'num_threads': int,
                'cmdline': str
            }
        """
        workers = []
        try:
            if parent_pid is None:
                parent_pid = os.getpid()
            
            parent_process = psutil.Process(parent_pid)
            children = parent_process.children(recursive=True)
            
            for child in children:
                try:
                    # Check if this looks like a DataLoader worker
                    # Workers are typically Python processes spawned by the parent
                    cmdline = ' '.join(child.cmdline()[:3]) if child.cmdline() else ''
                    
                    # DataLoader workers are typically Python processes
                    # They might have 'python' or 'torch' in their cmdline
                    # or be child processes that aren't the main training script
                    is_likely_worker = (
                        'python' in cmdline.lower() or 
                        'torch' in cmdline.lower() or
                        child.pid != parent_pid
                    )
                    
                    if is_likely_worker:
                        mem_info = child.memory_info()
                        rss_gb = mem_info.rss / (1024**3)
                        vms_gb = mem_info.vms / (1024**3)
                        percent = child.memory_percent()
                        num_threads = child.num_threads()
                        
                        workers.append({
                            'pid': child.pid,
                            'ppid': child.ppid(),
                            'rss_gb': round(rss_gb, 3),
                            'vms_gb': round(vms_gb, 3),
                            'percent': round(percent, 2),
                            'num_threads': num_threads,
                            'cmdline': cmdline[:100] if cmdline else 'N/A'  # Truncate long cmdlines
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Process may have terminated or we don't have access
                    continue
                except Exception as e:
                    logger.debug(f"Error checking child process {child.pid}: {e}")
                    continue
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug(f"Could not access parent process {parent_pid}: {e}")
        except Exception as e:
            logger.debug(f"Error finding DataLoader workers: {e}")
        
        return workers
    
    def check_dataloader_worker_memory(self, parent_pid: int = None) -> Dict:
        """
        Check memory usage of all DataLoader worker processes.
        
        Args:
            parent_pid: Parent process ID (None = current process)
            
        Returns:
            dict with:
            {
                'worker_count': int,
                'total_rss_gb': float,
                'total_vms_gb': float,
                'total_percent': float,
                'workers': List[Dict]  # Individual worker details
            }
        """
        workers = self.find_dataloader_workers(parent_pid=parent_pid)
        
        if not workers:
            return {
                'worker_count': 0,
                'total_rss_gb': 0.0,
                'total_vms_gb': 0.0,
                'total_percent': 0.0,
                'workers': []
            }
        
        total_rss = sum(w['rss_gb'] for w in workers)
        total_vms = sum(w['vms_gb'] for w in workers)
        total_percent = sum(w['percent'] for w in workers)
        
        return {
            'worker_count': len(workers),
            'total_rss_gb': round(total_rss, 3),
            'total_vms_gb': round(total_vms, 3),
            'total_percent': round(total_percent, 2),
            'workers': workers
        }
    
    def log_dataloader_worker_memory(self, context: str = "", parent_pid: int = None):
        """
        Log DataLoader worker memory usage (called every 30 seconds during training).
        
        Uses module-level throttling so it works even when new monitor instances are created.
        
        Args:
            context: Context string for logging
            parent_pid: Parent process ID (None = current process)
        """
        global _last_worker_memory_log_time
        
        current_time = time.time()
        
        # Only log every 30 seconds to avoid spam (module-level throttling)
        if current_time - _last_worker_memory_log_time < _worker_memory_log_interval:
            return
        
        _last_worker_memory_log_time = current_time
        
        try:
            worker_info = self.check_dataloader_worker_memory(parent_pid=parent_pid)
            
            context_str = f" [{context}]" if context else ""
            
            if worker_info['worker_count'] > 0:
                logger.info(
                    f"🔧 DATALOADER WORKERS{context_str}: {worker_info['worker_count']} workers, "
                    f"total RSS={worker_info['total_rss_gb']:.2f}GB "
                    f"({worker_info['total_percent']:.1f}% of system RAM)"
                )
                
                # Log individual worker details at debug level
                for i, worker in enumerate(worker_info['workers']):
                    logger.debug(
                        f"   Worker {i+1}: PID={worker['pid']}, RSS={worker['rss_gb']:.2f}GB, "
                        f"VMS={worker['vms_gb']:.2f}GB, {worker['percent']:.1f}% RAM, "
                        f"{worker['num_threads']} threads"
                    )
            else:
                logger.debug(f"🔧 DATALOADER WORKERS{context_str}: No workers detected (num_workers=0 or workers not yet spawned)")
                
        except Exception as e:
            logger.debug(f"Failed to log DataLoader worker memory: {e}")
    
    def check_dmesg_for_disk_errors(self) -> List[Dict]:
        """
        Check dmesg for recent disk I/O errors.
        
        Returns:
            List of disk errors, each with:
                - timestamp: When the error occurred
                - device: Affected device (e.g., sda, nvme0n1)
                - error_type: Type of error (I/O error, timeout, etc.)
                - message: Full dmesg message
        """
        try:
            result = subprocess.run(
                ['dmesg', '-T'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                result = subprocess.run(['dmesg'], capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return []
            
            dmesg_output = result.stdout
            
            # Parse for disk errors
            disk_errors = []
            error_patterns = [
                (r'(.*?)\s+.*?(sd[a-z]+|nvme\d+n\d+).*?(I/O error|timeout|failed command)', 'I/O error'),
                (r'(.*?)\s+.*?EXT4-fs.*?error', 'filesystem error'),
                (r'(.*?)\s+.*?Buffer I/O error', 'buffer I/O error'),
            ]
            
            for line in dmesg_output.split('\n'):
                for pattern, error_type in error_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        timestamp_str = match.group(1) if match.lastindex >= 1 else 'unknown'
                        device = match.group(2) if match.lastindex >= 2 else 'unknown'
                        
                        event_id = f"{timestamp_str}_{device}_{error_type}"
                        
                        if event_id not in self.disk_errors_seen:
                            self.disk_errors_seen.add(event_id)
                            disk_errors.append({
                                'timestamp': timestamp_str,
                                'device': device,
                                'error_type': error_type,
                                'message': line.strip(),
                                'event_id': event_id,
                            })
            
            return disk_errors
            
        except Exception as e:
            logger.debug(f"Failed to check dmesg for disk errors: {e}")
            return []
    
    def get_comprehensive_status(self) -> Dict:
        """
        Get comprehensive system health status including memory, OOM, and disk.
        
        Returns:
            dict with all health metrics
        """
        status = {
            'timestamp': datetime.now().isoformat(),
            'job_id': self.job_id,
        }
        
        # Memory pressure
        mem_pressure = self.check_memory_pressure()
        if mem_pressure:
            status['memory'] = mem_pressure
        
        # Process memory
        proc_mem = self.check_process_memory()
        if proc_mem:
            status['process'] = proc_mem
        
        # DataLoader worker memory (check every 30 seconds)
        worker_mem = self.check_dataloader_worker_memory()
        if worker_mem['worker_count'] > 0:
            status['dataloader_workers'] = worker_mem
        
        # OOM events
        oom_events = self.check_dmesg_for_oom()
        if oom_events:
            status['oom_events'] = oom_events
        
        # Disk errors
        disk_errors = self.check_dmesg_for_disk_errors()
        if disk_errors:
            status['disk_errors'] = disk_errors
        
        return status
    
    def log_health_status(self, context: str = "", log_level: int = logging.INFO):
        """
        Log comprehensive health status with warnings for issues.
        
        Args:
            context: Context string to include in log (e.g., "EPOCH_START", "BEFORE_VALIDATION")
            log_level: Logging level to use for normal status
        """
        status = self.get_comprehensive_status()
        
        context_str = f" [{context}]" if context else ""
        
        # Log memory status
        if 'memory' in status:
            mem = status['memory']
            logger.log(
                log_level,
                f"💾 SYSTEM RAM{context_str}: {mem['used_ram_gb']:.1f}/{mem['total_ram_gb']:.1f}GB used "
                f"({mem['percent_used']:.1f}%), {mem['available_ram_gb']:.1f}GB available"
            )
            
            if mem['swap_percent'] > 10:
                logger.warning(
                    f"⚠️  SWAP{context_str}: {mem['swap_used_gb']:.1f}/{mem['swap_total_gb']:.1f}GB used "
                    f"({mem['swap_percent']:.1f}%)"
                )
            
            # Log warning if pressure is high
            if mem['warning']:
                logger.warning(mem['warning'])
        
        # Log process memory
        if 'process' in status:
            proc = status['process']
            logger.log(
                log_level,
                f"📊 PROCESS RAM{context_str}: PID={proc['pid']} RSS={proc['rss_gb']:.2f}GB "
                f"({proc['percent']:.1f}% of system), VMS={proc['vms_gb']:.2f}GB, threads={proc['num_threads']}"
            )
            
            if proc['num_fds']:
                logger.debug(f"   File descriptors: {proc['num_fds']}")
        
        # Log DataLoader worker memory (automatically throttled to every 30 seconds)
        self.log_dataloader_worker_memory(context=context)
        
        # Log OOM events
        if 'oom_events' in status and status['oom_events']:
            for event in status['oom_events']:
                logger.error(
                    f"🚨 KERNEL OOM EVENT{context_str}: Killed PID {event['victim_pid']} "
                    f"({event['victim_process']}) at {event['timestamp']}"
                )
                logger.error(f"   Message: {event['message']}")
        
        # Log disk errors
        if 'disk_errors' in status and status['disk_errors']:
            for error in status['disk_errors']:
                logger.error(
                    f"💥 DISK ERROR{context_str}: {error['error_type']} on {error['device']} "
                    f"at {error['timestamp']}"
                )
                logger.error(f"   Message: {error['message']}")
        
        return status


def check_system_health(context: str = "", job_id: str = None) -> Dict:
    """
    Convenience function to check and log system health.
    
    Args:
        context: Context string for logging
        job_id: Job ID for tracking
        
    Returns:
        System health status dict
    """
    monitor = SystemHealthMonitor(job_id=job_id)
    return monitor.log_health_status(context=context)


def check_memory_available_for_workers(safety_margin_gb: float = 10.0, num_columns: int = None) -> int:
    """
    Calculate how many DataLoader workers can be safely created based on available system RAM.
    
    Args:
        safety_margin_gb: GB of RAM to reserve for safety (default: 10GB for more conservative calculation)
        num_columns: Number of columns in the dataset (affects worker memory usage)
        
    Returns:
        Maximum number of workers that can be created safely
    """
    try:
        mem = psutil.virtual_memory()
        available_ram_gb = mem.available / (1024**3)
        
        # Reserve safety margin
        available_for_workers = max(0, available_ram_gb - safety_margin_gb)
        
        # Base worker memory: 2.5GB per worker
        # Additional memory for wide datasets: ~0.01GB per column
        # This accounts for:
        # - Larger batches with more columns
        # - More string cache lookups
        # - More encoding operations per batch
        # - Larger tensors in memory
        base_worker_ram_gb = 2.5
        column_overhead_gb = 0.0
        if num_columns:
            # For very wide datasets (100+ columns), workers need significantly more memory
            if num_columns >= 100:
                # Wide dataset: add 0.015GB per column over 100
                column_overhead_gb = 0.01 * num_columns
            elif num_columns >= 50:
                # Medium-wide: add 0.01GB per column
                column_overhead_gb = 0.008 * num_columns
            else:
                # Narrow dataset: minimal overhead
                column_overhead_gb = 0.005 * num_columns
        
        worker_ram_gb = base_worker_ram_gb + column_overhead_gb
        max_workers = int(available_for_workers / worker_ram_gb)
        
        if num_columns:
            logger.info(
                f"RAM worker calculation: {available_ram_gb:.1f}GB available, "
                f"{safety_margin_gb:.1f}GB safety margin, {worker_ram_gb:.2f}GB per worker "
                f"(base={base_worker_ram_gb:.1f}GB + {num_columns} cols×{column_overhead_gb/num_columns:.3f}GB) → max {max_workers} workers"
            )
        else:
            logger.info(
                f"RAM worker calculation: {available_ram_gb:.1f}GB available, "
                f"{safety_margin_gb:.1f}GB safety margin, {worker_ram_gb:.1f}GB per worker → max {max_workers} workers"
            )
        
        return max(0, max_workers)
    except Exception as e:
        logger.warning(f"Failed to calculate workers by RAM: {e}")
        return 4  # More conservative safe default (was 8)


def check_for_recent_oom_events(minutes: int = 10) -> List[Dict]:
    """
    Check for OOM events in the last N minutes.
    
    Args:
        minutes: How many minutes back to check
        
    Returns:
        List of recent OOM events
    """
    monitor = SystemHealthMonitor()
    all_events = monitor.check_dmesg_for_oom()
    
    # Filter for recent events (dmesg timestamp parsing is tricky, so return all for now)
    # In practice, we track seen events to avoid duplicate logging
    return all_events


def check_training_memory_requirements(
    num_workers: int,
    batch_size: int,
    dataset_size: int,
    gpu_available: bool = False,
    print_warnings: bool = True
) -> Dict:
    """
    Check if system has enough memory for training with given parameters.
    
    Args:
        num_workers: Number of DataLoader workers
        batch_size: Training batch size
        dataset_size: Number of rows in dataset
        gpu_available: Whether GPU is available
        print_warnings: Whether to print warnings to logger
        
    Returns:
        dict with keys:
            - sufficient_memory: bool - whether memory is sufficient
            - available_ram_gb: float - available system RAM
            - required_ram_gb: float - estimated RAM requirement
            - available_vram_gb: float - available GPU VRAM (if GPU)
            - required_vram_gb: float - estimated VRAM requirement (if GPU)
            - warnings: list of warning messages
            - recommendations: list of actionable recommendations
    """
    try:
        mem = psutil.virtual_memory()
        available_ram_gb = mem.available / (1024**3)
        total_ram_gb = mem.total / (1024**3)
        used_ram_gb = mem.used / (1024**3)
        
        # Estimate RAM requirements
        worker_ram_gb = 2.5  # Each worker uses ~2.5GB (conservative estimate for batch loading, encoding, cache lookups)
        training_process_ram_gb = 3.0  # Base training process overhead
        data_ram_gb = max(0.5, dataset_size / 1000)  # Rough estimate: 0.5-1GB per 1K rows
        required_ram_gb = training_process_ram_gb + data_ram_gb + (num_workers * worker_ram_gb)
        
        warnings = []
        recommendations = []
        sufficient_memory = True
        
        # Check RAM sufficiency with 20% safety margin
        safety_margin = 1.2
        if available_ram_gb < required_ram_gb * safety_margin:
            sufficient_memory = False
            warnings.append(
                f"⚠️  LOW SYSTEM RAM: {available_ram_gb:.1f}GB available, "
                f"{required_ram_gb:.1f}GB required ({required_ram_gb * safety_margin:.1f}GB with safety margin)"
            )
            warnings.append(
                f"   RAM breakdown: {training_process_ram_gb:.1f}GB training + "
                f"{data_ram_gb:.1f}GB data + {num_workers}×{worker_ram_gb:.1f}GB workers = {required_ram_gb:.1f}GB"
            )
            
            if num_workers > 0:
                recommendations.append(
                    f"   💡 Disable DataLoader workers: export PYTORCH_NUM_WORKERS=0 (saves {num_workers * worker_ram_gb:.1f}GB RAM)"
                )
            if batch_size > 32:
                recommendations.append(
                    f"   💡 Reduce batch size: --batch-size 32 or --batch-size 16"
                )
            recommendations.append(
                f"   💡 Check other processes: free -h && ps aux --sort=-%mem | head -15"
            )
        
        result = {
            'sufficient_memory': sufficient_memory,
            'available_ram_gb': available_ram_gb,
            'total_ram_gb': total_ram_gb,
            'used_ram_gb': used_ram_gb,
            'required_ram_gb': required_ram_gb,
            'warnings': warnings,
            'recommendations': recommendations,
        }
        
        # Check GPU VRAM if available
        if gpu_available:
            try:
                if torch.cuda.is_available():
                    allocated_gb = torch.cuda.memory_allocated() / (1024**3)
                    reserved_gb = torch.cuda.memory_reserved() / (1024**3)
                    total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    available_vram_gb = total_vram_gb - reserved_gb
                    
                    # Estimate VRAM requirements
                    worker_vram_gb = 0.6  # Each worker uses ~600MB for CUDA context
                    model_vram_gb = 5.0  # Rough estimate for model + gradients
                    required_vram_gb = model_vram_gb + (num_workers * worker_vram_gb)
                    
                    result['available_vram_gb'] = available_vram_gb
                    result['total_vram_gb'] = total_vram_gb
                    result['reserved_vram_gb'] = reserved_gb
                    result['required_vram_gb'] = required_vram_gb
                    
                    # Check VRAM sufficiency with 20% safety margin
                    if available_vram_gb < required_vram_gb * safety_margin:
                        sufficient_memory = False
                        result['sufficient_memory'] = False
                        warnings.append(
                            f"⚠️  LOW GPU VRAM: {available_vram_gb:.1f}GB available, "
                            f"{required_vram_gb:.1f}GB required ({required_vram_gb * safety_margin:.1f}GB with safety margin)"
                        )
                        warnings.append(
                            f"   VRAM breakdown: {model_vram_gb:.1f}GB model + "
                            f"{num_workers}×{worker_vram_gb:.1f}GB workers = {required_vram_gb:.1f}GB"
                        )
                        
                        if num_workers > 0 and not any("PYTORCH_NUM_WORKERS" in r for r in recommendations):
                            recommendations.append(
                                f"   💡 Disable DataLoader workers: export PYTORCH_NUM_WORKERS=0 (saves {num_workers * worker_vram_gb:.1f}GB VRAM)"
                            )
            except Exception as e:
                logger.debug(f"Could not check GPU VRAM: {e}")
        
        # Print warnings if requested
        if print_warnings and warnings:
            logger.warning("=" * 80)
            logger.warning("🚨 MEMORY PRESSURE DETECTED - OOM RISK HIGH")
            logger.warning("=" * 80)
            for warning in warnings:
                logger.warning(warning)
            if recommendations:
                logger.warning("")
                logger.warning("Recommended actions to prevent OOM:")
                for rec in recommendations:
                    logger.warning(rec)
            logger.warning("=" * 80)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to check training memory requirements: {e}")
        return {
            'sufficient_memory': True,  # Fail open to avoid blocking training
            'available_ram_gb': 0,
            'required_ram_gb': 0,
            'warnings': [],
            'recommendations': [],
        }


def print_oom_recovery_help(error: Exception, num_workers: int = None, batch_size: int = None):
    """
    Print helpful recovery instructions after OOM error.
    
    Args:
        error: The OOM exception that was caught
        num_workers: Number of DataLoader workers that were used
        batch_size: Batch size that was used
    """
    logger.error("=" * 80)
    logger.error("💥 OUT OF MEMORY (OOM) ERROR DETECTED")
    logger.error("=" * 80)
    logger.error(f"Error: {error}")
    logger.error("")
    
    # Check current memory state
    try:
        mem = psutil.virtual_memory()
        available_ram_gb = mem.available / (1024**3)
        total_ram_gb = mem.total / (1024**3)
        percent_used = mem.percent
        
        logger.error(f"Current memory state:")
        logger.error(f"   Total RAM: {total_ram_gb:.1f}GB")
        logger.error(f"   Used RAM: {percent_used:.1f}%")
        logger.error(f"   Available: {available_ram_gb:.1f}GB")
        logger.error("")
    except Exception as e:
        logger.debug(f"Could not check memory state: {e}")
    
    logger.error("The DataLoader worker was killed by the Linux OOM (Out-of-Memory) killer.")
    logger.error("This happens when the system runs out of RAM during training.")
    logger.error("")
    logger.error("🔧 RECOMMENDED FIXES (try in order):")
    logger.error("")
    logger.error("1. Disable DataLoader multiprocessing (saves ~2.5GB RAM per worker):")
    logger.error("   export PYTORCH_NUM_WORKERS=0")
    logger.error("   # Then re-run your training command")
    logger.error("")
    
    if batch_size and batch_size > 32:
        logger.error("2. Reduce batch size:")
        logger.error(f"   --batch-size 32  # Current: {batch_size}")
        logger.error("")
    
    logger.error("3. Check what's using memory on this machine:")
    logger.error("   free -h")
    logger.error("   ps aux --sort=-%mem | head -15")
    logger.error("")
    logger.error("4. If multiple jobs are running, stop some to free up RAM:")
    logger.error("   ps aux | grep python")
    logger.error("")
    
    if num_workers and num_workers > 0:
        worker_ram = num_workers * 2.0
        logger.error(f"Note: You were using {num_workers} DataLoader workers")
        logger.error(f"      Each worker uses ~2GB RAM = {worker_ram:.1f}GB total worker overhead")
        logger.error(f"      Setting PYTORCH_NUM_WORKERS=0 will save this RAM")
        logger.error("")
    
    logger.error("=" * 80)


def get_gpu_processes() -> List[Dict]:
    """
    Get list of processes using GPU with FULL hierarchical details.
    Returns primary training processes with their multiprocessing workers grouped.
    
    Returns:
        List of dicts with primary process info and nested workers:
        {
            'pid': int,
            'type': 'primary',
            'process_type': 'es_training' | 'nf_training' | 'other',
            'script': '/full/path/to/script.py',
            'job_id': 'uuid' or None,
            'gpu_memory_mb': float,
            'cpu_percent': float,
            'memory_rss_gb': float,
            'cmdline': 'full command',
            'workers': [
                {
                    'pid': int,
                    'type': 'worker',
                    'gpu_memory_mb': float,
                    'cpu_percent': float,
                    'memory_rss_gb': float
                }
            ],
            'worker_count': int,
            'total_gpu_memory_mb': float (primary + all workers)
        }
    """
    try:
        # Use nvidia-smi to get GPU process information
        cmd = [
            'nvidia-smi',
            '--query-compute-apps=pid,process_name,used_memory',
            '--format=csv,noheader,nounits'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return []
        
        # Get all PIDs and their GPU memory
        gpu_pids = []
        gpu_mem = {}
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3:
                try:
                    pid = parts[0]
                    gpu_pids.append(pid)
                    gpu_mem[pid] = float(parts[2])
                except (ValueError, IndexError):
                    continue
        
        if not gpu_pids:
            return []
        
        # Get full process details with ps -f
        ps_result = subprocess.run(['ps', '-f', '-p', ','.join(gpu_pids)],
                                  capture_output=True, text=True, timeout=5)
        if ps_result.returncode != 0:
            # Fallback to simple list if ps fails
            return _get_simple_gpu_processes_fallback(gpu_pids, gpu_mem)
        
        lines = ps_result.stdout.strip().split('\n')
        if len(lines) <= 1:  # No data lines
            return []
        
        # Parse process info
        processes = {}
        for line in lines[1:]:  # Skip header
            parts = line.split(None, 7)  # Split into max 8 parts
            if len(parts) >= 8:
                pid = parts[1]
                ppid = parts[2]
                cmd = parts[7]
                processes[pid] = {
                    'ppid': ppid,
                    'cmd': cmd,
                    'gpu_memory_mb': gpu_mem.get(pid, 0)
                }
        
        # Find primary processes (PPID not in GPU process list)
        primary_pids = [pid for pid, info in processes.items() 
                       if info['ppid'] not in processes]
        
        # Build result with primary processes and their workers
        result_list = []
        for pid in primary_pids:
            info = processes[pid]
            cmd = info['cmd']
            
            # Get psutil details for primary
            try:
                proc = psutil.Process(int(pid))
                cpu_percent = proc.cpu_percent(interval=0.1)
                mem_info = proc.memory_info()
                rss_gb = mem_info.rss / (1024 * 1024 * 1024)
            except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
                cpu_percent = 0
                rss_gb = 0
            
            # Extract script path and job ID
            script = None
            job_id = None
            process_type = 'other'
            
            if 'es_training_wrapper.py' in cmd:
                process_type = 'es_training'
                # Extract script path
                if '/sphere/' in cmd or '/shared1/' in cmd:
                    parts = cmd.split()
                    for i, part in enumerate(parts):
                        if 'es_training_wrapper.py' in part:
                            script = part
                            break
                # Extract job ID
                if '--job-id' in cmd:
                    job_parts = cmd.split('--job-id')
                    if len(job_parts) > 1:
                        job_id = job_parts[1].strip().split()[0]
            elif 'nf_training_wrapper.py' in cmd:
                process_type = 'nf_training'
                if '/sphere/' in cmd or '/shared1/' in cmd:
                    parts = cmd.split()
                    for i, part in enumerate(parts):
                        if 'nf_training_wrapper.py' in part:
                            script = part
                            break
                if '--job-id' in cmd:
                    job_parts = cmd.split('--job-id')
                    if len(job_parts) > 1:
                        job_id = job_parts[1].strip().split()[0]
            
            # Find all workers for this primary process
            workers = []
            total_gpu_mem = info['gpu_memory_mb']
            
            for wpid, winfo in processes.items():
                if winfo['ppid'] == pid:
                    # Get psutil details for worker
                    try:
                        wproc = psutil.Process(int(wpid))
                        wcpu = wproc.cpu_percent(interval=0.1)
                        wmem = wproc.memory_info()
                        wrss_gb = wmem.rss / (1024 * 1024 * 1024)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
                        wcpu = 0
                        wrss_gb = 0
                    
                    worker_gpu_mem = winfo['gpu_memory_mb']
                    total_gpu_mem += worker_gpu_mem
                    
                    workers.append({
                        'pid': int(wpid),
                        'type': 'worker',
                        'gpu_memory_mb': worker_gpu_mem,
                        'cpu_percent': wcpu,
                        'memory_rss_gb': round(wrss_gb, 2)
                    })
            
            # Add primary process with workers
            result_list.append({
                'pid': int(pid),
                'type': 'primary',
                'process_type': process_type,
                'script': script,
                'job_id': job_id,
                'gpu_memory_mb': info['gpu_memory_mb'],
                'cpu_percent': cpu_percent,
                'memory_rss_gb': round(rss_gb, 2),
                'cmdline': cmd,
                'workers': workers,
                'worker_count': len(workers),
                'total_gpu_memory_mb': round(total_gpu_mem, 0)
            })
        
        return result_list
        
    except subprocess.TimeoutExpired:
        logger.warning("GPU process query timed out")
        return []
    except FileNotFoundError:
        # nvidia-smi or ps not available
        return []
    except Exception as e:
        logger.error(f"Error getting GPU processes: {e}")
        return []


def _get_simple_gpu_processes_fallback(gpu_pids: List[str], gpu_mem: Dict[str, float]) -> List[Dict]:
    """Fallback to simple process list if ps command fails."""
    result = []
    for pid in gpu_pids:
        try:
            proc = psutil.Process(int(pid))
            result.append({
                'pid': int(pid),
                'type': 'unknown',
                'process_type': 'other',
                'script': None,
                'job_id': None,
                'gpu_memory_mb': gpu_mem.get(pid, 0),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_rss_gb': round(proc.memory_info().rss / (1024 * 1024 * 1024), 2),
                'cmdline': ' '.join(proc.cmdline()[:3]),
                'workers': [],
                'worker_count': 0,
                'total_gpu_memory_mb': gpu_mem.get(pid, 0)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
            continue
    return result


if __name__ == '__main__':
    # Test the monitoring
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 80)
    print("SYSTEM HEALTH CHECK")
    print("=" * 80 + "\n")
    
    monitor = SystemHealthMonitor(job_id="test-job")
    status = monitor.log_health_status(context="TEST", log_level=logging.INFO)
    
    print("\n" + "=" * 80)
    print("RAW STATUS DICT")
    print("=" * 80)
    print(json.dumps(status, indent=2, default=str))

