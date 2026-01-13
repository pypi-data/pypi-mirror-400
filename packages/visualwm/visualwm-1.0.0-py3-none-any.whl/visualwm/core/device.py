"""
设备信息收集器 - 自动获取IP、MAC地址等设备信息
"""

import socket
import uuid
import platform
from datetime import datetime
from typing import Dict, Optional


class DeviceInfoCollector:
    """设备信息收集器"""
    
    @staticmethod
    def get_ip_address() -> str:
        """获取本机IP地址"""
        try:
            # 创建一个UDP socket来获取本机IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            try:
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return "127.0.0.1"
    
    @staticmethod
    def get_mac_address() -> str:
        """获取本机MAC地址"""
        try:
            mac = uuid.getnode()
            mac_str = ':'.join(('%012X' % mac)[i:i+2] for i in range(0, 12, 2))
            return mac_str
        except Exception:
            return "00:00:00:00:00:00"
    
    @staticmethod
    def get_hostname() -> str:
        """获取主机名"""
        try:
            return socket.gethostname()
        except Exception:
            return "unknown"
    
    @staticmethod
    def get_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """获取当前时间戳"""
        return datetime.now().strftime(format_str)
    
    @staticmethod
    def get_platform_info() -> Dict[str, str]:
        """获取平台信息"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
    
    @classmethod
    def collect_all(cls) -> Dict[str, str]:
        """收集所有设备信息"""
        platform_info = cls.get_platform_info()
        return {
            "ip_address": cls.get_ip_address(),
            "mac_address": cls.get_mac_address(),
            "hostname": cls.get_hostname(),
            "timestamp": cls.get_timestamp(),
            "system": platform_info["system"],
            "machine": platform_info["machine"],
        }
