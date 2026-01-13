"""
VisualWM - 泄密警示明水印SDK

支持图片、视频、文本、文档多模态水印嵌入与提取
"""

from visualwm.core.info import WatermarkInfo
from visualwm.core.style import WatermarkStyle, RiskLevel
from visualwm.core.checksum import ChecksumGenerator
from visualwm.image.watermark import ImageWatermark
from visualwm.video.watermark import VideoWatermark
from visualwm.text.watermark import TextWatermark
from visualwm.document.word import WordWatermark
from visualwm.document.pdf import PDFWatermark
from visualwm.document.excel import ExcelWatermark
from visualwm.document.ofd import OFDWatermark

__version__ = "1.1.0"
__author__ = "VisualWM Team"

__all__ = [
    # 核心模块
    "WatermarkInfo",
    "WatermarkStyle",
    "RiskLevel",
    "ChecksumGenerator",
    # 媒体水印
    "ImageWatermark",
    "VideoWatermark",
    "TextWatermark",
    # 文档水印
    "WordWatermark",
    "PDFWatermark",
    "ExcelWatermark",
    "OFDWatermark",
]
