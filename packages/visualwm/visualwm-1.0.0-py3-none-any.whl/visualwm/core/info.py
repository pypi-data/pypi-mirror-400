"""
水印信息模型 - 存储溯源信息
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, Any
from datetime import datetime

from visualwm.core.device import DeviceInfoCollector
from visualwm.core.checksum import ChecksumGenerator


@dataclass
class WatermarkInfo:
    """
    水印信息类
    
    用于存储和管理水印中嵌入的溯源信息，包括用户信息、设备信息、时间戳等。
    
    Attributes:
        username: 用户姓名
        employee_id: 工号
        device_id: 设备编号
        ip_address: IP地址
        mac_address: MAC地址
        timestamp: 时间戳
        custom_data: 自定义扩展数据
        auto_fill: 是否自动填充动态信息
        include_checksum: 是否包含校验码
    """
    
    username: str = ""
    employee_id: str = ""
    device_id: str = ""
    ip_address: str = ""
    mac_address: str = ""
    timestamp: str = ""
    department: str = ""
    custom_data: Dict[str, Any] = field(default_factory=dict)
    auto_fill: bool = True
    include_checksum: bool = True
    _checksum: str = field(default="", init=False)
    
    def __post_init__(self):
        """初始化后处理，自动填充设备信息"""
        if self.auto_fill:
            self._fill_device_info()
        if self.include_checksum:
            self._generate_checksum()
    
    def _fill_device_info(self):
        """自动填充设备信息"""
        collector = DeviceInfoCollector()
        
        if not self.ip_address:
            self.ip_address = collector.get_ip_address()
        
        if not self.mac_address:
            self.mac_address = collector.get_mac_address()
        
        if not self.timestamp:
            self.timestamp = collector.get_timestamp()
    
    def _generate_checksum(self):
        """生成校验码"""
        content = self.to_string(include_checksum=False)
        self._checksum = ChecksumGenerator.generate(content)
    
    @property
    def checksum(self) -> str:
        """获取校验码"""
        return self._checksum
    
    def verify_checksum(self, checksum: str) -> bool:
        """
        验证校验码
        
        Args:
            checksum: 待验证的校验码
            
        Returns:
            校验是否通过
        """
        content = self.to_string(include_checksum=False)
        return ChecksumGenerator.verify(content, checksum)
    
    def refresh_dynamic_info(self):
        """刷新动态信息（时间戳、设备状态等）"""
        collector = DeviceInfoCollector()
        self.timestamp = collector.get_timestamp()
        self.ip_address = collector.get_ip_address()
        if self.include_checksum:
            self._generate_checksum()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典
        
        Returns:
            包含所有信息的字典
        """
        data = {
            "username": self.username,
            "employee_id": self.employee_id,
            "device_id": self.device_id,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "timestamp": self.timestamp,
            "department": self.department,
        }
        
        if self.custom_data:
            data["custom_data"] = self.custom_data
        
        if self.include_checksum and self._checksum:
            data["checksum"] = self._checksum
        
        return data
    
    def to_string(
        self, 
        separator: str = " | ", 
        include_checksum: bool = True,
        compact: bool = False
    ) -> str:
        """
        转换为字符串（用于水印显示）
        
        Args:
            separator: 字段分隔符
            include_checksum: 是否包含校验码
            compact: 是否使用紧凑格式
            
        Returns:
            格式化的水印字符串
        """
        parts = []
        
        if self.username:
            parts.append(f"用户:{self.username}" if not compact else self.username)
        
        if self.employee_id:
            parts.append(f"工号:{self.employee_id}" if not compact else self.employee_id)
        
        if self.department:
            parts.append(f"部门:{self.department}" if not compact else self.department)
        
        if self.device_id:
            parts.append(f"设备:{self.device_id}" if not compact else self.device_id)
        
        if self.ip_address:
            parts.append(f"IP:{self.ip_address}" if not compact else self.ip_address)
        
        if self.mac_address:
            parts.append(f"MAC:{self.mac_address}" if not compact else self.mac_address)
        
        if self.timestamp:
            parts.append(f"时间:{self.timestamp}" if not compact else self.timestamp)
        
        # 添加自定义数据
        for key, value in self.custom_data.items():
            parts.append(f"{key}:{value}")
        
        # 添加校验码
        if include_checksum and self._checksum:
            parts.append(f"校验:{self._checksum[:8]}" if not compact else self._checksum[:8])
        
        return separator.join(parts)
    
    def to_multiline_string(self) -> str:
        """
        转换为多行字符串
        
        Returns:
            多行格式的水印字符串
        """
        return self.to_string(separator="\n")
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WatermarkInfo":
        """
        从字典创建实例
        
        Args:
            data: 包含水印信息的字典
            
        Returns:
            WatermarkInfo实例
        """
        return cls(
            username=data.get("username", ""),
            employee_id=data.get("employee_id", ""),
            device_id=data.get("device_id", ""),
            ip_address=data.get("ip_address", ""),
            mac_address=data.get("mac_address", ""),
            timestamp=data.get("timestamp", ""),
            department=data.get("department", ""),
            custom_data=data.get("custom_data", {}),
            auto_fill=False,  # 从字典创建时不自动填充
            include_checksum=data.get("include_checksum", True),
        )
    
    @classmethod
    def from_string(cls, text: str, separator: str = " | ") -> "WatermarkInfo":
        """
        从字符串解析水印信息
        
        Args:
            text: 水印字符串
            separator: 字段分隔符
            
        Returns:
            WatermarkInfo实例
        """
        data = {}
        parts = text.split(separator)
        
        field_mapping = {
            "用户": "username",
            "工号": "employee_id",
            "部门": "department",
            "设备": "device_id",
            "IP": "ip_address",
            "MAC": "mac_address",
            "时间": "timestamp",
            "校验": "checksum",
        }
        
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip()
                value = value.strip()
                
                if key in field_mapping:
                    data[field_mapping[key]] = value
        
        return cls.from_dict(data)
    
    def __str__(self) -> str:
        return self.to_string()
    
    def __repr__(self) -> str:
        return f"WatermarkInfo(username='{self.username}', employee_id='{self.employee_id}')"
