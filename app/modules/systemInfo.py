import platform
import os
import sys
import psutil
import socket
import uuid
import re
import datetime
from typing import Dict, Any

class SystemInfo:
    """
    A class to gather comprehensive system information.
    Requires psutil package: pip install psutil
    """
    
    def __init__(self):
        """Initialize the SystemInfo class"""
        self.info = {}
        
    def gather_all_info(self) -> Dict[str, Any]:
        """
        Gather all available system information
        Returns a dictionary with all system information
        """
        self.info = {
            "system": self.get_system_info(),
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network": self.get_network_info(),
            "users": self.get_users_info(),
            "boot_time": self.get_boot_time(),
            "python": self.get_python_info(),
            "environment": self.get_environment_vars(),
            "processes": self.get_processes_info()
        }
        return self.info
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        system_info = {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "mac_address": ':'.join(re.findall('..', '%012x' % uuid.getnode())),
            "fqdn": socket.getfqdn()
        }
        
        # Additional platform-specific info
        if platform.system() == "Windows":
            system_info["windows_edition"] = platform.win32_edition()
            system_info["windows_version"] = platform.win32_ver()
        elif platform.system() == "Linux":
            system_info["linux_distribution"] = platform.linux_distribution()
            
        return system_info
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        cpu_info = {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "max_frequency": f"{psutil.cpu_freq().max:.2f}Mhz",
            "min_frequency": f"{psutil.cpu_freq().min:.2f}Mhz",
            "current_frequency": f"{psutil.cpu_freq().current:.2f}Mhz",
            "cpu_usage_percent": f"{psutil.cpu_percent()}%",
            "cpu_usage_per_core": [f"{percent}%" for percent in psutil.cpu_percent(percpu=True)],
            "cpu_times": psutil.cpu_times()._asdict(),
            "cpu_stats": psutil.cpu_stats()._asdict()
        }
        
        # Additional platform-specific CPU info
        if platform.system() == "Linux":
            with open('/proc/cpuinfo') as f:
                cpuinfo = f.readlines()
            model = [line.split(':')[1].strip() for line in cpuinfo if "model name" in line]
            if model:
                cpu_info["model"] = model[0]
                
        return cpu_info
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        virtual_mem = psutil.virtual_memory()
        swap_mem = psutil.swap_memory()
        
        memory_info = {
            "total_ram": f"{virtual_mem.total / (1024**3):.2f} GB",
            "available_ram": f"{virtual_mem.available / (1024**3):.2f} GB",
            "used_ram": f"{virtual_mem.used / (1024**3):.2f} GB",
            "ram_usage_percent": f"{virtual_mem.percent}%",
            "total_swap": f"{swap_mem.total / (1024**3):.2f} GB",
            "used_swap": f"{swap_mem.used / (1024**3):.2f} GB",
            "swap_usage_percent": f"{swap_mem.percent}%"
        }
        return memory_info
    
    def get_disk_info(self) -> Dict[str, Any]:
        """Get disk information"""
        disk_info = {}
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total_size": f"{usage.total / (1024**3):.2f} GB",
                    "used": f"{usage.used / (1024**3):.2f} GB",
                    "free": f"{usage.free / (1024**3):.2f} GB",
                    "usage_percent": f"{usage.percent}%"
                }
            except PermissionError:
                continue
                
        disk_io = psutil.disk_io_counters()
        disk_info["io_counters"] = {
            "read_count": disk_io.read_count,
            "write_count": disk_io.write_count,
            "read_bytes": f"{disk_io.read_bytes / (1024**2):.2f} MB",
            "write_bytes": f"{disk_io.write_bytes / (1024**2):.2f} MB"
        }
        
        return disk_info
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        network_info = {}
        net_io = psutil.net_io_counters()
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        network_info["io_counters"] = {
            "bytes_sent": f"{net_io.bytes_sent / (1024**2):.2f} MB",
            "bytes_recv": f"{net_io.bytes_recv / (1024**2):.2f} MB",
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
        
        for interface, addrs in net_if_addrs.items():
            network_info[interface] = {
                "addresses": [addr._asdict() for addr in addrs],
                "stats": net_if_stats[interface]._asdict() if interface in net_if_stats else None
            }
            
        return network_info
    
    def get_users_info(self) -> Dict[str, Any]:
        """Get logged in users information"""
        users = []
        for user in psutil.users():
            users.append({
                "name": user.name,
                "terminal": user.terminal,
                "host": user.host,
                "started": datetime.datetime.fromtimestamp(user.started).strftime('%Y-%m-%d %H:%M:%S')
            })
        return {"users": users}
    
    def get_boot_time(self) -> Dict[str, Any]:
        """Get system boot time"""
        boot_time = psutil.boot_time()
        return {
            "boot_time": datetime.datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S'),
            "up_since": str(datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time))
        }
    
    def get_python_info(self) -> Dict[str, Any]:
        """Get Python interpreter information"""
        return {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "compiler": platform.python_compiler(),
            "build": platform.python_build(),
            "executable": sys.executable,
            "path": sys.path
        }
    
    def get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables"""
        return dict(os.environ)
    
    def get_processes_info(self) -> Dict[str, Any]:
        """Get running processes information"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info']):
            try:
                processes.append({
                    "pid": proc.info['pid'],
                    "name": proc.info['name'],
                    "user": proc.info['username'],
                    "cpu_percent": proc.info['cpu_percent'],
                    "memory_rss": f"{proc.info['memory_info'].rss / (1024**2):.2f} MB"
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
                
        # Sort by CPU usage
        processes = sorted(processes, key=lambda p: p['cpu_percent'], reverse=True)
        return {"processes": processes, "count": len(processes)}


# Example usage
if __name__ == "__main__":
    sys_info = SystemInfo()
    all_info = sys_info.gather_all_info()
    
    # Print basic system info
    print("=== System Information ===")
    for key, value in all_info["system"].items():
        print(f"{key:>20}: {value}")
    
    # Print CPU info
    print("\n=== CPU Information ===")
    for key, value in all_info["cpu"].items():
        if key not in ["cpu_times", "cpu_stats"]:
            print(f"{key:>20}: {value}")
    
    # Print memory info
    print("\n=== Memory Information ===")
    for key, value in all_info["memory"].items():
        print(f"{key:>20}: {value}")