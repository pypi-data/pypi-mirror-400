"""
水印样式配置 - 定义水印的视觉属性
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple, Optional, Dict, Any


class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"           # 低风险 - 普通文档
    MEDIUM = "medium"     # 中风险 - 内部文档
    HIGH = "high"         # 高风险 - 机密文档
    CRITICAL = "critical" # 极高风险 - 绝密文档


class WatermarkPosition(Enum):
    """水印位置"""
    TILE = "tile"               # 平铺
    CENTER = "center"           # 居中
    TOP_LEFT = "top_left"       # 左上角
    TOP_RIGHT = "top_right"     # 右上角
    BOTTOM_LEFT = "bottom_left" # 左下角
    BOTTOM_RIGHT = "bottom_right" # 右下角
    TOP_CENTER = "top_center"   # 顶部居中
    BOTTOM_CENTER = "bottom_center" # 底部居中


@dataclass
class WatermarkStyle:
    """
    水印样式类
    
    用于配置水印的视觉属性，包括字体、颜色、透明度、位置等。
    
    Attributes:
        font_name: 字体名称
        font_size: 字体大小
        color: RGB颜色元组
        opacity: 透明度(0-1)
        rotation: 旋转角度
        position: 位置模式
        bold: 是否加粗
        italic: 是否斜体
        prefix: 前缀文字
        suffix: 后缀文字
        line_spacing: 行间距（平铺模式）
        column_spacing: 列间距（平铺模式）
        margin: 边距
        risk_level: 风险等级
        border: 是否添加边框
        background_color: 背景颜色
    """
    
    font_name: str = "SimHei"
    font_size: int = 24
    color: Tuple[int, int, int] = (128, 128, 128)
    opacity: float = 0.5
    rotation: int = -30
    position: str = "tile"
    bold: bool = False
    italic: bool = False
    prefix: str = ""
    suffix: str = ""
    line_spacing: int = 100
    column_spacing: int = 200
    margin: int = 20
    risk_level: RiskLevel = RiskLevel.LOW
    border: bool = False
    border_color: Tuple[int, int, int] = (200, 200, 200)
    border_width: int = 1
    background_color: Optional[Tuple[int, int, int, int]] = None
    shadow: bool = False
    shadow_color: Tuple[int, int, int] = (50, 50, 50)
    shadow_offset: Tuple[int, int] = (2, 2)
    
    def __post_init__(self):
        """初始化后验证"""
        self._validate()
    
    def _validate(self):
        """验证参数"""
        if not 0 <= self.opacity <= 1:
            raise ValueError("透明度必须在0-1之间")
        
        if self.font_size <= 0:
            raise ValueError("字体大小必须大于0")
        
        if not all(0 <= c <= 255 for c in self.color):
            raise ValueError("颜色值必须在0-255之间")
    
    @property
    def rgba_color(self) -> Tuple[int, int, int, int]:
        """获取RGBA颜色（带透明度）"""
        alpha = int(self.opacity * 255)
        return (*self.color, alpha)
    
    @property
    def hex_color(self) -> str:
        """获取十六进制颜色"""
        return "#{:02x}{:02x}{:02x}".format(*self.color)
    
    def get_font_style(self) -> str:
        """获取字体样式描述"""
        styles = []
        if self.bold:
            styles.append("bold")
        if self.italic:
            styles.append("italic")
        return " ".join(styles) if styles else "normal"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "font_name": self.font_name,
            "font_size": self.font_size,
            "color": self.color,
            "opacity": self.opacity,
            "rotation": self.rotation,
            "position": self.position,
            "bold": self.bold,
            "italic": self.italic,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "line_spacing": self.line_spacing,
            "column_spacing": self.column_spacing,
            "margin": self.margin,
            "risk_level": self.risk_level.value,
            "border": self.border,
            "border_color": self.border_color,
            "shadow": self.shadow,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WatermarkStyle":
        """从字典创建实例"""
        if "risk_level" in data and isinstance(data["risk_level"], str):
            data["risk_level"] = RiskLevel(data["risk_level"])
        return cls(**data)
    
    @classmethod
    def default(cls) -> "WatermarkStyle":
        """默认样式"""
        return cls()
    
    @classmethod
    def low_risk_preset(cls) -> "WatermarkStyle":
        """低风险预设样式"""
        return cls(
            font_size=20,
            color=(180, 180, 180),
            opacity=0.3,
            rotation=-30,
            position="tile",
            line_spacing=150,
            column_spacing=250,
            risk_level=RiskLevel.LOW,
        )
    
    @classmethod
    def medium_risk_preset(cls) -> "WatermarkStyle":
        """中风险预设样式"""
        return cls(
            font_size=24,
            color=(128, 128, 128),
            opacity=0.4,
            rotation=-30,
            position="tile",
            line_spacing=120,
            column_spacing=200,
            prefix="【内部】",
            risk_level=RiskLevel.MEDIUM,
        )
    
    @classmethod
    def high_risk_preset(cls) -> "WatermarkStyle":
        """高风险预设样式（涉密文档）"""
        return cls(
            font_size=28,
            color=(255, 0, 0),
            opacity=0.6,
            rotation=-30,
            position="tile",
            bold=True,
            line_spacing=100,
            column_spacing=180,
            prefix="【机密】",
            border=True,
            border_color=(255, 0, 0),
            risk_level=RiskLevel.HIGH,
        )
    
    @classmethod
    def critical_risk_preset(cls) -> "WatermarkStyle":
        """极高风险预设样式（绝密文档）"""
        return cls(
            font_size=32,
            color=(200, 0, 0),
            opacity=0.7,
            rotation=-30,
            position="tile",
            bold=True,
            line_spacing=80,
            column_spacing=150,
            prefix="【绝密】",
            border=True,
            border_color=(200, 0, 0),
            border_width=2,
            shadow=True,
            shadow_color=(100, 0, 0),
            risk_level=RiskLevel.CRITICAL,
        )
    
    @classmethod
    def get_preset_by_risk_level(cls, level: RiskLevel) -> "WatermarkStyle":
        """根据风险等级获取预设样式"""
        presets = {
            RiskLevel.LOW: cls.low_risk_preset,
            RiskLevel.MEDIUM: cls.medium_risk_preset,
            RiskLevel.HIGH: cls.high_risk_preset,
            RiskLevel.CRITICAL: cls.critical_risk_preset,
        }
        return presets[level]()
    
    @classmethod
    def corner_preset(cls, position: str = "bottom_right") -> "WatermarkStyle":
        """角落水印预设"""
        return cls(
            font_size=16,
            color=(100, 100, 100),
            opacity=0.6,
            rotation=0,
            position=position,
            margin=15,
        )
    
    @classmethod
    def center_preset(cls) -> "WatermarkStyle":
        """居中水印预设"""
        return cls(
            font_size=48,
            color=(150, 150, 150),
            opacity=0.3,
            rotation=-30,
            position="center",
        )
    
    def copy(self, **kwargs) -> "WatermarkStyle":
        """
        复制并修改样式
        
        Args:
            **kwargs: 要修改的属性
            
        Returns:
            新的WatermarkStyle实例
        """
        data = self.to_dict()
        data.update(kwargs)
        return self.from_dict(data)
