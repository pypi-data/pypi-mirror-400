import socket
import psutil
import json
import requests
from typing import Dict, Any, List, Optional

def get_network_info() -> Dict[str, Any]:
    """
    Coleta informações de rede (versão síncrona sem aiohttp)
    """
    # IPs locais
    local_ips = []
    
    # Obter todos os IPs das interfaces de rede
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if address.family == socket.AF_INET:  # IPv4
                if not address.address.startswith('127.'):  # Ignorar localhost
                    local_ips.append({
                        "interface": interface_name,
                        "address": address.address,
                        "netmask": address.netmask,
                        "broadcast": address.broadcast if hasattr(address, 'broadcast') else None
                    })
    
    # IP público e localização
    geo_info = _get_public_ip_and_geo()
    
    return {
        "local_ips": local_ips,
        "public_ip": geo_info.get("ip") if geo_info else None,
        "location": {
            "city": geo_info.get("city") if geo_info else None,
            "region": geo_info.get("region") if geo_info else None,
            "country": geo_info.get("country") if geo_info else None,
            "org": geo_info.get("org") if geo_info else None,
            "timezone": geo_info.get("timezone") if geo_info else None,
            "postal": geo_info.get("postal") if geo_info else None,
            "loc": geo_info.get("loc") if geo_info else None,
        } if geo_info else None
    }

def _get_public_ip_and_geo() -> Optional[Dict[str, Any]]:
    """
    Obtém IP público e informações de geolocalização (versão síncrona)
    """
    services = [
        "https://ipinfo.io/json",
        "https://api.ipify.org?format=json",
        "https://api.my-ip.io/ip.json",
    ]
    
    for service_url in services:
        try:
            response = requests.get(service_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Padronizar a resposta
                if "ip" in data:
                    return {
                        "ip": data.get("ip"),
                        "city": data.get("city"),
                        "region": data.get("region"),
                        "country": data.get("country"),
                        "org": data.get("org"),
                        "timezone": data.get("timezone"),
                        "postal": data.get("postal"),
                        "loc": data.get("loc"),
                    }
        except Exception:
            continue
    
    return None

def get_local_ips_sync() -> List[str]:
    """
    Versão síncrona para obter apenas IPs locais
    """
    local_ips = []
    
    for interface_name, interface_addresses in psutil.net_if_addrs().items():
        for address in interface_addresses:
            if address.family == socket.AF_INET:  # IPv4
                if not address.address.startswith('127.'):  # Ignorar localhost
                    local_ips.append(address.address)
    
    return local_ips