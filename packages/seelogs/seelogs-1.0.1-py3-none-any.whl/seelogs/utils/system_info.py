import os
import psutil
import platform
import time
from datetime import datetime, timezone
from typing import Dict, Any
from .network_info import get_network_info

def get_system_info() -> Dict[str, Any]:
    """
    Coleta informações do sistema
    """
    # Informações de memória do sistema
    mem = psutil.virtual_memory()
    
    # Informações de CPU
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count()
    
    # Informações do processo atual
    process = psutil.Process()
    process_mem = process.memory_info()
    process_cpu_times = process.cpu_times()
    
    # Informações de carga do sistema
    load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
    
    return {
        # CPU e memória reais
        "cpu_usage_percent": round(cpu_percent, 2),
        "cpus_total": cpu_count,
        "memory_total_mb": round(mem.total / 1024 / 1024),
        "memory_used_mb": round(mem.used / 1024 / 1024),
        "memory_used_percent": round(mem.percent, 2),
        
        # Dados técnicos adicionais do processo
        "memory_process_mb": {
            "rss": round(process_mem.rss / 1024 / 1024, 2),
            "vms": round(process_mem.vms / 1024 / 1024, 2),
            "shared": round(getattr(process_mem, 'shared', 0) / 1024 / 1024, 2) if hasattr(process_mem, 'shared') else 0,
            "text": round(getattr(process_mem, 'text', 0) / 1024 / 1024, 2) if hasattr(process_mem, 'text') else 0,
            "lib": round(getattr(process_mem, 'lib', 0) / 1024 / 1024, 2) if hasattr(process_mem, 'lib') else 0,
            "data": round(getattr(process_mem, 'data', 0) / 1024 / 1024, 2) if hasattr(process_mem, 'data') else 0,
            "dirty": round(getattr(process_mem, 'dirty', 0) / 1024 / 1024, 2) if hasattr(process_mem, 'dirty') else 0,
        },
        
        "cpu_process_time": {
            "user": round(process_cpu_times.user, 2),
            "system": round(process_cpu_times.system, 2),
            "children_user": round(process_cpu_times.children_user, 2),
            "children_system": round(process_cpu_times.children_system, 2),
        },
        
        # Ambiente
        "load_average": [round(load, 2) for load in load_avg] if load_avg[0] != 0 else [0, 0, 0],
        "uptime_seconds": int(time.time() - psutil.boot_time()),
        "hostname": platform.node(),
        "platform": platform.system(),
        "arch": platform.machine(),
        "python_version": platform.python_version(),
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

def get_full_system_info() -> Dict[str, Any]:
    """
    Coleta informações completas do sistema incluindo rede (síncrona)
    """
    system = get_system_info()
    network = get_network_info()
    
    try:
        network = get_network_info()
    except Exception as error:
        network = {
            "error": "Falha ao obter informações de rede",
            "details": str(error)
        }
    
    return {**system, "network": network}