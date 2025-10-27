#!/usr/bin/env python3
# Question: Why is this a seperate sctipy?
# We have system_monitor_script.py, container_monitor.py, container_monitor_script.py
# Do we need more than 1? This is messy.

"""
System Monitor Script
Collects system and GPU stats and publishes to MQTT
"""

import json
import time
import psutil
import os
try:
    import gputil as GPUtil
except ImportError:
    GPUtil = None
import paho.mqtt.publish as publish
import sys
from typing import Dict, Any

def get_system_stats() -> Dict[str, Any]:
    """Collect comprehensive system statistics"""
    stats = {
        "timestamp": int(time.time()),
        "cpu": {},
        "memory": {},
        "disk": {},
        "network": {}
    }

    # CPU stats
    stats["cpu"] = {
        "percent": psutil.cpu_percent(interval=1),
        "count_logical": psutil.cpu_count(logical=True),
        "count_physical": psutil.cpu_count(logical=False),
        "freq_current": psutil.cpu_freq().current if psutil.cpu_freq() else None,
        "freq_max": psutil.cpu_freq().max if psutil.cpu_freq() else None,
        "load_avg": dict(zip(["1min", "5min", "15min"], psutil.getloadavg())) if hasattr(psutil, 'getloadavg') else None
    }

    # Memory stats
    mem = psutil.virtual_memory()
    stats["memory"] = {
        "total_gb": round(mem.total / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "used_gb": round(mem.used / (1024**3), 2),
        "percent": mem.percent,
        "free_gb": round(mem.free / (1024**3), 2)
    }

    # Disk stats
    disk = psutil.disk_usage('/')
    stats["disk"] = {
        "total_gb": round(disk.total / (1024**3), 2),
        "used_gb": round(disk.used / (1024**3), 2),
        "free_gb": round(disk.free / (1024**3), 2),
        "percent": disk.percent
    }

    # Network stats
    net = psutil.net_io_counters()
    stats["network"] = {
        "bytes_sent_mb": round(net.bytes_sent / (1024**2), 2),
        "bytes_recv_mb": round(net.bytes_recv / (1024**2), 2),
        "packets_sent": net.packets_sent,
        "packets_recv": net.packets_recv
    }

    return stats

def get_gpu_stats() -> Dict[str, Any]:
    """Collect GPU statistics using GPUtil if available"""
    try:
        import gputil as GPUtil
    except ImportError:
        try:
            import GPUtil
        except ImportError:
            return {"error": "GPUtil not installed"}

    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            return {"error": "No GPUs detected"}

        gpu_stats = {}
        for i, gpu in enumerate(gpus):
            gpu_stats[f"gpu_{i}"] = {
                "name": gpu.name,
                "id": gpu.id,
                "uuid": gpu.uuid,
                "load": gpu.load * 100,  # Convert to percentage
                "memory_used_mb": gpu.memoryUsed,
                "memory_total_mb": gpu.memoryTotal,
                "memory_free_mb": gpu.memoryFree,
                "memory_util_percent": gpu.memoryUtil * 100,  # Convert to percentage
                "temperature": gpu.temperature
            }

        return gpu_stats
    except Exception as e:
        return {"error": f"Failed to get GPU stats: {str(e)}"}

def publish_system_data():
    """Collect and publish system and GPU data to MQTT"""
    try:
        # Get system stats
        system_stats = get_system_stats()

        # Get GPU stats
        gpu_stats = get_gpu_stats()

        # Combine all stats
        all_stats = {
            "system": system_stats,
            "gpu": gpu_stats
        }

        # Optionally write JSON to disk for file-based consumers (atomic replace)
        stats_file = os.getenv('SYSTEM_STATS_FILE', '/app/last_system_stats.json')
        try:
            tmp_path = stats_file + '.tmp'
            os.makedirs(os.path.dirname(stats_file), exist_ok=True)
            with open(tmp_path, 'w', encoding='utf-8') as f:
                json.dump(all_stats, f)
            # atomic replace
            os.replace(tmp_path, stats_file)
            print(f'Wrote system stats JSON to {stats_file}')
        except Exception as e:
            print(f'Failed to write stats file: {e}')

        # Publish to MQTT
        topic = "/chainloot/system/stats"
        payload = json.dumps(all_stats)

        publish.single(
            topic=topic,
            payload=payload,
            hostname="192.168.1.98",
            port=1883,
            retain=True,
            qos=1
        )

        # Publish per-key system stats
        for section, data in system_stats.items():
            if section == "timestamp":
                # Publish timestamp separately
                ts_topic = "/chainloot/system/timestamp"
                ts_payload = json.dumps(data)
                publish.single(
                    topic=ts_topic,
                    payload=ts_payload,
                    hostname="192.168.1.98",
                    port=1883,
                    retain=True,
                    qos=1
                )
                continue
            if isinstance(data, dict):
                for key, value in data.items():
                    key_topic = f"/chainloot/system/{section}/{key}"
                    key_payload = json.dumps(value)
                    publish.single(
                        topic=key_topic,
                        payload=key_payload,
                        hostname="192.168.1.98",
                        port=1883,
                        retain=True,
                        qos=1
                    )

        # Publish per-key GPU stats
        if isinstance(gpu_stats, dict) and "error" not in gpu_stats:
            for gpu_id, gpu_data in gpu_stats.items():
                if isinstance(gpu_data, dict):
                    for key, value in gpu_data.items():
                        gpu_topic = f"/chainloot/system/gpu/{gpu_id}/{key}"
                        gpu_payload = json.dumps(value)
                        publish.single(
                            topic=gpu_topic,
                            payload=gpu_payload,
                            hostname="192.168.1.98",
                            port=1883,
                            retain=True,
                            qos=1
                        )

        print(f"Published system stats: CPU {system_stats['cpu']['percent']}%, Memory {system_stats['memory']['percent']}%, GPU count: {len(gpu_stats) if isinstance(gpu_stats, dict) and 'error' not in gpu_stats else 0}")

    except Exception as e:
        print(f"Failed to publish system data: {e}")

def main():
    """Main monitoring function"""
    print("Starting system monitoring...")

    try:
        publish_system_data()
        print("System monitoring complete.")
    except Exception as e:
        print(f"System monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()