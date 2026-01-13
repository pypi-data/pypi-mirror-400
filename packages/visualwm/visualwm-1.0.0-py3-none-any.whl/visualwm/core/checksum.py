"""
校验码生成器 - 用于防篡改机制
"""

import hashlib
import hmac
from typing import Optional


class ChecksumGenerator:
    """
    校验码生成器
    
    提供校验码的生成与验证功能，用于检测水印是否被篡改。
    """
    
    # 默认密钥（生产环境应使用环境变量或配置文件）
    DEFAULT_SECRET_KEY = "visualwm_secret_2024"
    
    @classmethod
    def generate(
        cls, 
        content: str, 
        secret_key: Optional[str] = None,
        algorithm: str = "sha256"
    ) -> str:
        """
        生成校验码
        
        Args:
            content: 需要校验的内容
            secret_key: 密钥（可选）
            algorithm: 哈希算法
            
        Returns:
            校验码字符串
        """
        key = (secret_key or cls.DEFAULT_SECRET_KEY).encode('utf-8')
        content_bytes = content.encode('utf-8')
        
        if algorithm == "sha256":
            h = hmac.new(key, content_bytes, hashlib.sha256)
        elif algorithm == "sha512":
            h = hmac.new(key, content_bytes, hashlib.sha512)
        elif algorithm == "md5":
            h = hmac.new(key, content_bytes, hashlib.md5)
        else:
            raise ValueError(f"不支持的算法: {algorithm}")
        
        return h.hexdigest()
    
    @classmethod
    def generate_short(
        cls, 
        content: str, 
        length: int = 8,
        secret_key: Optional[str] = None
    ) -> str:
        """
        生成短校验码
        
        Args:
            content: 需要校验的内容
            length: 校验码长度
            secret_key: 密钥（可选）
            
        Returns:
            短校验码字符串
        """
        full_checksum = cls.generate(content, secret_key)
        return full_checksum[:length]
    
    @classmethod
    def verify(
        cls, 
        content: str, 
        checksum: str,
        secret_key: Optional[str] = None,
        algorithm: str = "sha256"
    ) -> bool:
        """
        验证校验码
        
        Args:
            content: 需要校验的内容
            checksum: 待验证的校验码
            secret_key: 密钥（可选）
            algorithm: 哈希算法
            
        Returns:
            校验是否通过
        """
        expected = cls.generate(content, secret_key, algorithm)
        
        # 支持短校验码验证
        if len(checksum) < len(expected):
            expected = expected[:len(checksum)]
        
        return hmac.compare_digest(expected, checksum)
    
    @classmethod
    def generate_with_timestamp(
        cls, 
        content: str, 
        timestamp: str,
        secret_key: Optional[str] = None
    ) -> str:
        """
        生成带时间戳的校验码
        
        Args:
            content: 需要校验的内容
            timestamp: 时间戳
            secret_key: 密钥（可选）
            
        Returns:
            校验码字符串
        """
        combined = f"{content}|{timestamp}"
        return cls.generate(combined, secret_key)


class TamperDetector:
    """
    篡改检测器
    
    用于检测水印是否被篡改，并记录篡改行为。
    """
    
    def __init__(self):
        self.tamper_log = []
    
    def check(
        self, 
        original_info: str, 
        current_info: str,
        original_checksum: str,
        current_checksum: Optional[str] = None
    ) -> dict:
        """
        检测篡改
        
        Args:
            original_info: 原始信息
            current_info: 当前信息
            original_checksum: 原始校验码
            current_checksum: 当前校验码（可选）
            
        Returns:
            检测结果字典
        """
        result = {
            "is_tampered": False,
            "content_modified": False,
            "checksum_valid": True,
            "details": []
        }
        
        # 检查内容是否被修改
        if original_info != current_info:
            result["content_modified"] = True
            result["is_tampered"] = True
            result["details"].append("内容已被修改")
        
        # 验证校验码
        if not ChecksumGenerator.verify(current_info, original_checksum):
            result["checksum_valid"] = False
            result["is_tampered"] = True
            result["details"].append("校验码验证失败")
        
        # 记录篡改行为
        if result["is_tampered"]:
            self._log_tamper(original_info, current_info, result)
        
        return result
    
    def _log_tamper(self, original: str, current: str, result: dict):
        """记录篡改行为"""
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_content": original[:100],  # 只记录前100字符
            "current_content": current[:100],
            "detection_result": result
        }
        self.tamper_log.append(log_entry)
    
    def get_tamper_log(self) -> list:
        """获取篡改日志"""
        return self.tamper_log.copy()
    
    def clear_log(self):
        """清空篡改日志"""
        self.tamper_log.clear()
