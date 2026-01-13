"""
Training Banner - Cool epoch announcements for screenshotable logs
"""
import logging
import os
import re
import resource
import socket
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


def visual_len(text: str) -> int:
    """
    Calculate visual width of text accounting for wide characters (emojis).
    Emojis display as 2 columns in terminals.
    """
    # Known emojis we use in banners (hardcode for reliability)
    double_width_chars = {
        '🚀', '🎯', '🎮', '💾', '🖥️', '⏰', '⏱️', '📊', '📦', '🔧',
        '🔄', '✅', '❌', '⚠️', '🧟', '🐌', '🚨', '📈', '📉', '➡️',
        '📁', '📝', '🔍', '💡', '🔥', '⚡', '🎬', '🐕', '👁️', '🏃',
        '📋', '🏆', '🔀', '🔓', '🔒', '🏗️', '🧪', '🧹', '📤', '🗑️'
    }
    
    width = 0
    for char in text:
        if char in double_width_chars:
            width += 2
        elif ord(char) > 0x1F300:  # Emoji range starts here
            width += 2
        else:
            width += 1
    return width


def pad_to_width(text: str, width: int, align: str = 'left') -> str:
    """
    Pad text to visual width, accounting for wide characters.
    
    Args:
        text: Text to pad
        width: Target visual width
        align: 'left', 'center', or 'right'
    """
    visual_width = visual_len(text)
    padding_needed = max(0, width - visual_width)
    
    if align == 'center':
        left_pad = padding_needed // 2
        right_pad = padding_needed - left_pad
        return ' ' * left_pad + text + ' ' * right_pad
    elif align == 'right':
        return ' ' * padding_needed + text
    else:  # left
        return text + ' ' * padding_needed


def get_version_info():
    """Get Featrix firmware version."""
    try:
        version_file = Path("/sphere/app/VERSION")
        if version_file.exists():
            return version_file.read_text().strip()
        
        # Fallback to local VERSION
        version_file = Path(__file__).parent.parent.parent.parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
    except Exception:
        pass
    
    return "unknown"


def get_uptime():
    """Get system uptime."""
    try:
        # Linux: read /proc/uptime
        with open('/proc/uptime') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_td = timedelta(seconds=uptime_seconds)
            days = uptime_td.days
            hours, remainder = divmod(uptime_td.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m {seconds}s"
    except FileNotFoundError:
        # macOS: use sysctl to get boot time
        try:
            result = subprocess.run(
                ['sysctl', '-n', 'kern.boottime'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # Output format: { sec = 1234567890, usec = 0 } Thu Dec 13 10:00:00 2025
                match = re.search(r'sec = (\d+)', result.stdout)
                if match:
                    boot_time = int(match.group(1))
                    uptime_seconds = datetime.now().timestamp() - boot_time
                    uptime_td = timedelta(seconds=uptime_seconds)
                    days = uptime_td.days
                    hours, remainder = divmod(uptime_td.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    if days > 0:
                        return f"{days}d {hours}h {minutes}m"
                    elif hours > 0:
                        return f"{hours}h {minutes}m"
                    else:
                        return f"{minutes}m {seconds}s"
        except Exception:
            pass
        return "unknown"
    except Exception:
        return "unknown"


def get_gpu_info():
    """Get GPU model and memory stats."""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu',
             '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            parts = [p.strip() for p in result.stdout.strip().split(',')]
            if len(parts) >= 5:
                gpu_name = parts[0]
                mem_used = float(parts[1])
                mem_total = float(parts[2])
                gpu_util = parts[3]
                temp = parts[4]
                
                mem_pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
                
                return {
                    'name': gpu_name,
                    'mem_used_gb': mem_used / 1024,
                    'mem_total_gb': mem_total / 1024,
                    'mem_pct': mem_pct,
                    'util': gpu_util,
                    'temp': temp,
                    'available': True
                }
    except Exception:
        pass
    
    return {'available': False}


def get_ram_info():
    """Get system RAM stats."""
    try:
        # Linux: read /proc/meminfo
        with open('/proc/meminfo') as f:
            lines = f.readlines()
            mem_total = 0
            mem_available = 0
            
            for line in lines:
                if line.startswith('MemTotal:'):
                    mem_total = int(line.split()[1]) / (1024 * 1024)  # GB
                elif line.startswith('MemAvailable:'):
                    mem_available = int(line.split()[1]) / (1024 * 1024)  # GB
            
            mem_used = mem_total - mem_available
            mem_pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
            
            return {
                'total_gb': mem_total,
                'used_gb': mem_used,
                'available_gb': mem_available,
                'used_pct': mem_pct
            }
    except FileNotFoundError:
        # macOS: use sysctl and vm_stat
        try:
            # Get total physical memory
            result = subprocess.run(
                ['sysctl', '-n', 'hw.memsize'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                mem_total = int(result.stdout.strip()) / (1024 ** 3)  # GB
                
                # Get page size
                result_pagesize = subprocess.run(
                    ['sysctl', '-n', 'hw.pagesize'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                page_size = int(result_pagesize.stdout.strip()) if result_pagesize.returncode == 0 else 4096
                
                # Get memory statistics from vm_stat
                result_vm = subprocess.run(
                    ['vm_stat'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result_vm.returncode == 0:
                    # Parse vm_stat output
                    free_pages = 0
                    inactive_pages = 0
                    for line in result_vm.stdout.splitlines():
                        if 'Pages free:' in line:
                            free_pages = int(line.split(':')[1].strip().rstrip('.'))
                        elif 'Pages inactive:' in line:
                            inactive_pages = int(line.split(':')[1].strip().rstrip('.'))
                    
                    mem_available = (free_pages + inactive_pages) * page_size / (1024 ** 3)  # GB
                    mem_used = mem_total - mem_available
                    mem_pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
                    
                    return {
                        'total_gb': mem_total,
                        'used_gb': mem_used,
                        'available_gb': mem_available,
                        'used_pct': mem_pct
                    }
        except Exception:
            pass
        return None
    except Exception:
        return None


def get_open_files_info():
    """Get ulimit and current open file descriptor count."""
    try:
        # Get soft and hard limits for open files
        soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
        
        # Get current number of open file descriptors for this process
        current_open = None
        try:
            # Linux: count entries in /proc/self/fd
            fd_dir = '/proc/self/fd'
            if os.path.exists(fd_dir):
                current_open = len(os.listdir(fd_dir))
        except Exception:
            pass
        
        return {
            'soft_limit': soft_limit,
            'hard_limit': hard_limit,
            'current_open': current_open,
        }
    except Exception:
        return None


def log_epoch_banner(epoch: int, total_epochs: int, training_type: str = "ES"):
    """
    Log a cool banner at the start of each epoch.
    
    Args:
        epoch: Current epoch number (1-indexed)
        total_epochs: Total number of epochs
        training_type: "ES" for embedding space, "SP" for single predictor
    """
    version = get_version_info()
    hostname = socket.gethostname()
    uptime = get_uptime()
    gpu_info = get_gpu_info()
    ram_info = get_ram_info()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Progress percentage
    progress_pct = (epoch / total_epochs * 100) if total_epochs > 0 else 0
    
    # Build simple, useful banner
    lines = [
        "\n",
        "╔" + "═" * 78 + "╗",
        f"║ {pad_to_width(f'EPOCH {epoch} / {total_epochs} ({progress_pct:.0f}%)', 76, 'center')} ║",
        "╚" + "═" * 78 + "╝",
    ]
    
    # Log each line separately
    for line in lines:
        logger.info(line)


def log_training_start_banner(total_epochs: int, batch_size: int, training_type: str = "ES", **kwargs):
    """
    Log a cool banner at the start of training.
    
    Args:
        total_epochs: Total number of epochs
        batch_size: Batch size
        training_type: "ES" for embedding space, "SP" for single predictor
        **kwargs: Additional training parameters to display
    """
    version = get_version_info()
    hostname = socket.gethostname()
    uptime = get_uptime()
    gpu_info = get_gpu_info()
    ram_info = get_ram_info()
    open_files_info = get_open_files_info()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Build banner with system stats + Featrix config
    lines = [
        "\n",
        "╔" + "═" * 78 + "╗",
        "║" + " " * 78 + "║",
        f"║ {pad_to_width('🚀  FEATRIX v' + version + '  🚀', 76, 'center')} ║",
        "║" + " " * 78 + "║",
        "╠" + "═" * 78 + "╣",
    ]
    
    # Training session info
    training_label = "EMBEDDING SPACE" if training_type == "ES" else "SINGLE PREDICTOR"
    lines.append(f"║ {pad_to_width(training_label + ' TRAINING', 76, 'center')} ║")
    lines.append("╠" + "═" * 78 + "╣")
    
    # Featrix training config
    lines.append(f"║ {pad_to_width(f'Epochs: {total_epochs}  │  Batch: {batch_size}', 76)} ║")
    
    # Show Featrix-specific architecture params (NOT optimizer/scheduler bullshit)
    useful_keys = ['d_model', 'n_columns', 'target_column', 'fine_tune', 'n_transformer_layers', 'n_attention_heads', 'n_hybrid_groups', 'n_hidden_layers']
    for key, value in kwargs.items():
        if value is not None and key in useful_keys:
            label = key.replace('_', ' ').title()
            config_line = f"{label}: {value}"
            lines.append(f"║ {pad_to_width(config_line, 76)} ║")
    
    lines.append("╠" + "═" * 78 + "╣")
    
    # System info (trim hostname if too long to prevent overflow)
    hostname_display = hostname if len(hostname) <= 20 else hostname[:17] + "..."
    host_line = f"Host: {hostname_display}"
    start_line = f"Started: {timestamp}"
    uptime_line = f"Uptime: {uptime}"
    lines.append(f"║ {pad_to_width(host_line, 76)} ║")
    lines.append(f"║ {pad_to_width(start_line, 76)} ║")
    lines.append(f"║ {pad_to_width(uptime_line, 76)} ║")
    
    # GPU info (if available, but skip on Mac for cleaner output)
    if gpu_info['available']:
        gpu_name_short = gpu_info['name'][:55]
        lines.append("╠" + "─" * 78 + "╣")
        
        gpu_line = f"GPU: {gpu_name_short}"
        lines.append(f"║ {pad_to_width(gpu_line, 76)} ║")
        
        vram_line = f"VRAM: {gpu_info['mem_used_gb']:.1f} / {gpu_info['mem_total_gb']:.1f} GB ({gpu_info['mem_pct']:.1f}%)"
        lines.append(f"║ {pad_to_width(vram_line, 76)} ║")
        
        util_temp = f"Util: {gpu_info['util']}% | Temp: {gpu_info['temp']}°C"
        lines.append(f"║ {pad_to_width(util_temp, 76)} ║")
    
    # RAM info
    if ram_info:
        lines.append("╠" + "─" * 78 + "╣")
        ram_line = f"RAM: {ram_info['used_gb']:.1f} / {ram_info['total_gb']:.1f} GB ({ram_info['used_pct']:.1f}% used)"
        lines.append(f"║ {pad_to_width(ram_line, 76)} ║")
        
        avail_line = f"Available: {ram_info['available_gb']:.1f} GB"
        lines.append(f"║ {pad_to_width(avail_line, 76)} ║")
    
    # Open file limits (ulimit)
    if open_files_info:
        lines.append("╠" + "─" * 78 + "╣")
        if open_files_info['current_open'] is not None:
            ulimit_line = f"Open Files: {open_files_info['current_open']} / {open_files_info['soft_limit']} (hard: {open_files_info['hard_limit']})"
        else:
            ulimit_line = f"ulimit -n: {open_files_info['soft_limit']} (hard: {open_files_info['hard_limit']})"
        lines.append(f"║ {pad_to_width(ulimit_line, 76)} ║")
    
    lines.append("╠" + "═" * 78 + "╣")
    lines.append(f"║ {pad_to_width('🎯  TRAINING BEGINS  🎯', 76, 'center')} ║")
    lines.append("╚" + "═" * 78 + "╝")
    
    # Log each line separately
    for line in lines:
        logger.info(line)

