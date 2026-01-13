"""
文档水印模块 - 支持Word、PDF、Excel、OFD等格式
"""

from visualwm.document.word import WordWatermark
from visualwm.document.pdf import PDFWatermark
from visualwm.document.excel import ExcelWatermark
from visualwm.document.ofd import OFDWatermark

__all__ = [
    "WordWatermark",
    "PDFWatermark",
    "ExcelWatermark",
    "OFDWatermark",
]
