"""
System Telemetry and Native Dialog Subsystem Service
Collects live hardware performance metrics via psutil:
CPU utilization percentage, RAM consumption, storage volume partitions,
and operating system kernel metrics.
"""

import os
import time
import platform
import psutil
from typing import Dict, Any


class SystemService:
    START_TIME = time.time()

    def get_hardware_telemetry(self) -> Dict[str, Any]:
        """Collect real-time hardware telemetry."""
        cpu_pct = psutil.cpu_percent(interval=None)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()
        cpu_mhz = round(cpu_freq.current, 0) if cpu_freq else 0

        mem = psutil.virtual_memory()
        ram_total_gb = round(mem.total / (1024 ** 3), 2)
        ram_used_gb = round(mem.used / (1024 ** 3), 2)
        ram_pct = mem.percent

        disk = psutil.disk_usage('/')
        disk_total_gb = round(disk.total / (1024 ** 3), 1)
        disk_used_gb = round(disk.used / (1024 ** 3), 1)
        disk_pct = disk.percent

        uptime_seconds = int(time.time() - self.START_TIME)
        hrs = uptime_seconds // 3600
        mins = (uptime_seconds % 3600) // 60
        secs = uptime_seconds % 60
        uptime_formatted = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        return {
            "cpu_percent": cpu_pct,
            "cpu_cores": cpu_count,
            "cpu_freq_mhz": cpu_mhz,
            "ram_percent": ram_pct,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
            "disk_percent": disk_pct,
            "disk_used_gb": disk_used_gb,
            "disk_total_gb": disk_total_gb,
            "os_name": platform.system(),
            "os_release": platform.release(),
            "os_arch": platform.machine(),
            "uptime": uptime_formatted,
            "python_version": platform.python_version()
        }


system_service = SystemService()
