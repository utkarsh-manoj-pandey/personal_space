"""
System Telemetry and Native Dialog Subsystem Service
Deep system diagnostic and hardware performance monitoring engine:
- Real-time CPU Utilization (Total & Per-Core breakdown), frequencies, and architectural topologies.
- Memory & Virtual Swap Partition Profiling (RAM, Buffers, Cached, Swap metrics).
- Storage Volume Partitions and Disk I/O Throughput Counters.
- Network Interface Packet Counters and Throughput Telemetry.
- Top Process Resource Inspector (CPU and RAM consumption).
- Sovereign System Health & Resource Saturation Composite Score.
"""

import os
import time
import platform
import psutil
from typing import Dict, Any, List


class SystemHealthEvaluator:
    """
    Computes weighted system operational health and resource saturation scores.
    """

    @staticmethod
    def calculate_health_score(cpu_pct: float, ram_pct: float, disk_pct: float) -> Dict[str, Any]:
        """
        Synthesizes composite health score in [0, 100].
        100 = optimal headroom; <50 = heavy resource saturation.
        """
        # Weighted penalty: CPU (40%), RAM (40%), Disk (20%)
        penalty = (cpu_pct * 0.4) + (ram_pct * 0.4) + (disk_pct * 0.2)
        score = max(0, min(100, int(100.0 - penalty)))

        if score >= 80:
            status = "Optimal Headroom"
            color = "#10b981"
        elif score >= 60:
            status = "Nominal Load"
            color = "#06b6d4"
        elif score >= 40:
            status = "Moderate Saturation"
            color = "#f59e0b"
        else:
            status = "Critical Pressure"
            color = "#ef4444"

        return {
            "score": score,
            "status": status,
            "color": color
        }


class SystemService:
    START_TIME = time.time()

    def get_hardware_telemetry(self) -> Dict[str, Any]:
        """Collect complete real-time hardware telemetry and diagnostics."""
        # CPU
        cpu_pct = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(percpu=True, interval=None)
        cpu_count_logical = psutil.cpu_count(logical=True) or 1
        cpu_count_physical = psutil.cpu_count(logical=False) or 1
        cpu_freq = psutil.cpu_freq()
        cpu_mhz = round(cpu_freq.current, 0) if cpu_freq else 0

        # Memory (RAM)
        mem = psutil.virtual_memory()
        ram_total_gb = round(mem.total / (1024 ** 3), 2)
        ram_used_gb = round(mem.used / (1024 ** 3), 2)
        ram_avail_gb = round(mem.available / (1024 ** 3), 2)
        ram_pct = mem.percent

        # Swap Memory
        swap = psutil.swap_memory()
        swap_total_gb = round(swap.total / (1024 ** 3), 2)
        swap_used_gb = round(swap.used / (1024 ** 3), 2)
        swap_pct = swap.percent

        # Primary Storage Partition
        disk = psutil.disk_usage('/')
        disk_total_gb = round(disk.total / (1024 ** 3), 1)
        disk_used_gb = round(disk.used / (1024 ** 3), 1)
        disk_free_gb = round(disk.free / (1024 ** 3), 1)
        disk_pct = disk.percent

        # Disk I/O Counters
        try:
            dio = psutil.disk_io_counters()
            disk_read_mb = round(dio.read_bytes / (1024 ** 2), 1) if dio else 0.0
            disk_write_mb = round(dio.write_bytes / (1024 ** 2), 1) if dio else 0.0
        except Exception:
            disk_read_mb = 0.0
            disk_write_mb = 0.0

        # Network I/O Counters
        try:
            net = psutil.net_io_counters()
            net_sent_mb = round(net.bytes_sent / (1024 ** 2), 1) if net else 0.0
            net_recv_mb = round(net.bytes_recv / (1024 ** 2), 1) if net else 0.0
        except Exception:
            net_sent_mb = 0.0
            net_recv_mb = 0.0

        # Uptime
        uptime_seconds = int(time.time() - self.START_TIME)
        hrs = uptime_seconds // 3600
        mins = (uptime_seconds % 3600) // 60
        secs = uptime_seconds % 60
        uptime_formatted = f"{hrs:02d}:{mins:02d}:{secs:02d}"

        # Top processes by RAM / CPU
        top_procs = self.get_top_processes(limit=5)

        # Health score
        health = SystemHealthEvaluator.calculate_health_score(cpu_pct, ram_pct, disk_pct)

        return {
            "cpu_percent": cpu_pct,
            "cpu_cores": cpu_count_logical,
            "cpu_physical_cores": cpu_count_physical,
            "per_core_percent": per_core,
            "cpu_freq_mhz": cpu_mhz,
            "ram_percent": ram_pct,
            "ram_used_gb": ram_used_gb,
            "ram_total_gb": ram_total_gb,
            "ram_available_gb": ram_avail_gb,
            "swap_percent": swap_pct,
            "swap_used_gb": swap_used_gb,
            "swap_total_gb": swap_total_gb,
            "disk_percent": disk_pct,
            "disk_used_gb": disk_used_gb,
            "disk_total_gb": disk_total_gb,
            "disk_free_gb": disk_free_gb,
            "disk_read_mb": disk_read_mb,
            "disk_write_mb": disk_write_mb,
            "net_sent_mb": net_sent_mb,
            "net_recv_mb": net_recv_mb,
            "os_name": platform.system(),
            "os_release": platform.release(),
            "os_arch": platform.machine(),
            "uptime": uptime_formatted,
            "uptime_seconds": uptime_seconds,
            "python_version": platform.python_version(),
            "health_score": health["score"],
            "health_status": health["status"],
            "health_color": health["color"],
            "top_processes": top_procs
        }

    def get_top_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Enumerates active processes sorted by memory consumption."""
        procs = []
        try:
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = p.info
                    procs.append({
                        "pid": info.get("pid"),
                        "name": info.get("name", "Unknown"),
                        "cpu_percent": round(info.get("cpu_percent") or 0.0, 1),
                        "memory_percent": round(info.get("memory_percent") or 0.0, 1)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            procs.sort(key=lambda x: x["memory_percent"], reverse=True)
            return procs[:limit]
        except Exception:
            return []


system_service = SystemService()
