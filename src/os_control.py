"""
Jarvis OS Control Module
Full Windows system control capabilities
"""

import os
import sys
import psutil
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger('JarvisOS')

# Windows-specific imports
if sys.platform == 'win32':
    try:
        import win32api
        import win32con
        import win32security
        import win32ts
        import wmi
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
else:
    WINDOWS_AVAILABLE = False


class SystemMonitor:
    """Monitor system resources and performance"""
    
    def __init__(self):
        self.wmi_conn = None
        if WINDOWS_AVAILABLE:
            try:
                self.wmi_conn = wmi.WMI()
            except Exception as e:
                logger.warning(f"WMI not available: {e}")
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        mem = psutil.virtual_memory()
        return {
            'total': self.format_bytes(mem.total),
            'available': self.format_bytes(mem.available),
            'used': self.format_bytes(mem.used),
            'percent': mem.percent
        }
    
    def get_disk_usage(self) -> List[Dict[str, Any]]:
        """Get disk usage for all partitions"""
        partitions = psutil.disk_partitions()
        result = []
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                result.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total': self.format_bytes(usage.total),
                    'used': self.format_bytes(usage.used),
                    'free': self.format_bytes(usage.free),
                    'percent': usage.percent
                })
            except PermissionError:
                continue
        return result
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': self.format_bytes(net.bytes_sent),
            'bytes_recv': self.format_bytes(net.bytes_recv),
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv,
            'errin': net.errin,
            'errout': net.errout
        }
    
    def get_processes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get running processes sorted by CPU usage"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                processes.append({
                    'pid': info['pid'],
                    'name': info['name'],
                    'cpu': info['cpu_percent'],
                    'memory': info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        processes.sort(key=lambda x: x['cpu'] if x['cpu'] else 0, reverse=True)
        return processes[:limit]
    
    def get_battery_status(self) -> Optional[Dict[str, Any]]:
        """Get battery status if available"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'plugged_in': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
        except Exception:
            pass
        return None
    
    @staticmethod
    def format_bytes(bytes_val: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f} PB"


class ProcessManager:
    """Manage system processes"""
    
    def list_processes(self) -> List[Dict[str, Any]]:
        """List all running processes"""
        result = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
            try:
                result.append({
                    'pid': proc.pid,
                    'name': proc.name(),
                    'username': proc.username(),
                    'status': proc.status()
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return result
    
    def kill_process(self, pid: int) -> bool:
        """Terminate a process by PID"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait(timeout=5)
            logger.info(f"Process {pid} terminated successfully")
            return True
        except psutil.NoSuchProcess:
            logger.warning(f"Process {pid} not found")
            return False
        except psutil.AccessDenied:
            logger.error(f"Access denied to terminate process {pid}")
            return False
        except Exception as e:
            logger.error(f"Error terminating process {pid}: {e}")
            return False
    
    def start_process(self, command: str) -> Optional[int]:
        """Start a new process"""
        try:
            import subprocess
            proc = subprocess.Popen(command, shell=True)
            logger.info(f"Started process with PID {proc.pid}")
            return proc.pid
        except Exception as e:
            logger.error(f"Error starting process: {e}")
            return None
    
    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a process"""
        try:
            proc = psutil.Process(pid)
            return {
                'pid': proc.pid,
                'name': proc.name(),
                'status': proc.status(),
                'username': proc.username(),
                'create_time': proc.create_time(),
                'cpu_percent': proc.cpu_percent(),
                'memory_percent': proc.memory_percent(),
                'num_threads': proc.num_threads(),
                'cmdline': ' '.join(proc.cmdline())
            }
        except psutil.NoSuchProcess:
            return None


class FileManager:
    """File system operations"""
    
    def __init__(self):
        self.current_dir = os.getcwd()
    
    def list_directory(self, path: str = None) -> List[Dict[str, Any]]:
        """List files and directories"""
        target = path or self.current_dir
        result = []
        try:
            for entry in os.listdir(target):
                full_path = os.path.join(target, entry)
                stat = os.stat(full_path)
                result.append({
                    'name': entry,
                    'path': full_path,
                    'is_dir': os.path.isdir(full_path),
                    'size': SystemMonitor.format_bytes(stat.st_size),
                    'modified': stat.st_mtime,
                    'created': stat.st_ctime
                })
        except PermissionError:
            logger.error(f"Access denied to {target}")
        except Exception as e:
            logger.error(f"Error listing directory: {e}")
        return result
    
    def create_directory(self, path: str) -> bool:
        """Create a new directory"""
        try:
            os.makedirs(path, exist_ok=True)
            logger.info(f"Directory created: {path}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory: {e}")
            return False
    
    def delete_file(self, path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
            logger.info(f"File deleted: {path}")
            return True
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def copy_file(self, source: str, dest: str) -> bool:
        """Copy a file"""
        try:
            import shutil
            shutil.copy2(source, dest)
            logger.info(f"File copied: {source} -> {dest}")
            return True
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            return False


class OSControl:
    """Main OS Control class combining all system operations"""
    
    def __init__(self):
        self.monitor = SystemMonitor()
        self.process_manager = ProcessManager()
        self.file_manager = FileManager()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get complete system information"""
        return {
            'platform': sys.platform,
            'os': os.name,
            'cpu_count': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'total_memory': SystemMonitor.format_bytes(psutil.virtual_memory().total),
            'hostname': os.environ.get('COMPUTERNAME', os.uname().nodename),
            'username': os.environ.get('USERNAME', os.getenv('USER', 'Unknown')),
            'boot_time': psutil.boot_time()
        }
    
    def execute_command(self, command: str) -> Dict[str, Any]:
        """Execute a system command"""
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Export all classes
__all__ = ['SystemMonitor', 'ProcessManager', 'FileManager', 'OSControl']