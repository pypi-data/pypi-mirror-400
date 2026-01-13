"""
PDF文档水印处理器 - 支持.pdf格式添加明水印
"""

import io
import os
from pathlib import Path
from typing import Optional, Union, List, Tuple
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from visualwm.core.info import WatermarkInfo
from visualwm.core.style import WatermarkStyle, RiskLevel


class PDFWatermark:
    """
    PDF文档水印处理器
    
    支持在PDF文档中添加明水印，包括：
    - 平铺水印
    - 居中水印
    - 页眉/页脚水印
    - 对角线水印
    
    Features:
        - 支持.pdf格式
        - 保持原PDF结构
        - 支持加密PDF（需要密码）
        - 多种水印模式
        - 批量处理
    """
    
    SUPPORTED_EXTENSIONS = {'.pdf'}
    
    # 字体搜索路径
    FONT_PATHS = [
        os.path.join(os.path.dirname(__file__), "..", "font"),  # SDK内置字体目录
        "/usr/share/fonts/opentype/noto/",
        "/usr/share/fonts/truetype/wqy/",
        "/usr/share/fonts/truetype/",
        "/usr/share/fonts/",
        "/System/Library/Fonts/",
        "C:/Windows/Fonts/",
        "./fonts/",
    ]
    
    # 中文字体文件优先级列表
    CJK_FONT_FILES = [
        "NotoSerifSC-VariableFont_wght.ttf",  # SDK内置字体
        "NotoSansCJK-Regular.ttc",
        "NotoSansSC-Regular.otf",
        "wqy-zenhei.ttc",
        "wqy-microhei.ttc",
        "simhei.ttf",
        "SimHei.ttf",
    ]
    
    def __init__(self, default_style: Optional[WatermarkStyle] = None):
        """
        初始化PDF水印处理器
        
        Args:
            default_style: 默认水印样式
        """
        self.default_style = default_style or WatermarkStyle.default()
        self._font_registered = False
    
    def _register_font(self, font_name: str = "SimHei"):
        """注册中文字体"""
        if self._font_registered:
            return "ChineseFont"
        
        # 优先使用CJK字体文件列表
        for font_file in self.CJK_FONT_FILES:
            for font_path in self.FONT_PATHS:
                full_path = os.path.join(font_path, font_file)
                if os.path.exists(full_path):
                    try:
                        pdfmetrics.registerFont(TTFont("ChineseFont", full_path))
                        self._font_registered = True
                        return "ChineseFont"
                    except Exception as e:
                        continue
        
        # 备用字体列表
        font_files = [
            ("SimHei", ["simhei.ttf", "SimHei.ttf"]),
            ("SimSun", ["simsun.ttc", "SimSun.ttc"]),
            ("STHeiti", ["STHeiti.ttf"]),
            ("WenQuanYi", ["wqy-microhei.ttc", "wenquanyi-microhei.ttc"]),
            ("Noto", ["NotoSansCJK-Regular.ttc", "NotoSansSC-Regular.otf"]),
        ]
        
        for name, files in font_files:
            for font_file in files:
                for font_path in self.FONT_PATHS:
                    full_path = os.path.join(font_path, font_file)
                    if os.path.exists(full_path):
                        try:
                            pdfmetrics.registerFont(TTFont(name, full_path))
                            self._font_registered = True
                            return name
                        except Exception:
                            continue
        
        # 使用默认字体
        return "Helvetica"
    
    def embed(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        info: WatermarkInfo,
        style: Optional[WatermarkStyle] = None,
        watermark_type: str = "tile",
        password: Optional[str] = None
    ) -> str:
        """
        在PDF文档中嵌入水印
        
        Args:
            input_path: 输入PDF路径
            output_path: 输出PDF路径
            info: 水印信息
            style: 水印样式
            watermark_type: 水印类型 ("tile", "center", "diagonal", "header_footer")
            password: PDF密码（如果加密）
            
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        style = style or self.default_style
        
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 读取原PDF
        reader = PdfReader(input_path)
        
        if reader.is_encrypted:
            if password:
                reader.decrypt(password)
            else:
                raise ValueError("PDF已加密，请提供密码")
        
        writer = PdfWriter()
        
        # 为每一页添加水印
        for page_num, page in enumerate(reader.pages):
            # 获取页面尺寸
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # 创建水印PDF
            watermark_pdf = self._create_watermark_page(
                info, style, watermark_type,
                (page_width, page_height)
            )
            
            # 合并水印
            watermark_reader = PdfReader(watermark_pdf)
            watermark_page = watermark_reader.pages[0]
            
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        # 保存
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        return str(output_path)
    
    def _create_watermark_page(
        self,
        info: WatermarkInfo,
        style: WatermarkStyle,
        watermark_type: str,
        page_size: Tuple[float, float]
    ) -> io.BytesIO:
        """
        创建水印页面
        
        Args:
            info: 水印信息
            style: 水印样式
            watermark_type: 水印类型
            page_size: 页面尺寸
            
        Returns:
            水印PDF的BytesIO对象
        """
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=page_size)
        
        # 注册字体
        font_name = self._register_font(style.font_name)
        
        # 获取水印文本
        watermark_text = self._format_watermark_text(info, style)
        
        # 设置透明度
        c.setFillColor(Color(
            style.color[0] / 255,
            style.color[1] / 255,
            style.color[2] / 255,
            alpha=style.opacity
        ))
        
        # 根据类型绘制水印
        if watermark_type == "tile":
            self._draw_tiled_watermark(c, watermark_text, style, page_size, font_name)
        elif watermark_type == "center":
            self._draw_centered_watermark(c, watermark_text, style, page_size, font_name)
        elif watermark_type == "diagonal":
            self._draw_diagonal_watermark(c, watermark_text, style, page_size, font_name)
        elif watermark_type == "header_footer":
            self._draw_header_footer_watermark(c, watermark_text, style, page_size, font_name)
        
        c.save()
        packet.seek(0)
        
        return packet
    
    def _draw_tiled_watermark(
        self,
        c: canvas.Canvas,
        text: str,
        style: WatermarkStyle,
        page_size: Tuple[float, float],
        font_name: str
    ):
        """绘制平铺水印"""
        width, height = page_size
        
        c.setFont(font_name, style.font_size)
        
        # 计算文本宽度
        text_width = c.stringWidth(text, font_name, style.font_size)
        text_height = style.font_size
        
        # 计算间距
        spacing_x = text_width + style.column_spacing
        spacing_y = text_height + style.line_spacing
        
        # 绘制平铺水印
        y = -spacing_y
        row = 0
        while y < height + spacing_y:
            x = -text_width + (spacing_x // 2 if row % 2 else 0)
            while x < width + text_width:
                c.saveState()
                c.translate(x + text_width / 2, y + text_height / 2)
                c.rotate(style.rotation)
                c.drawString(-text_width / 2, -text_height / 2, text)
                c.restoreState()
                x += spacing_x
            y += spacing_y
            row += 1
    
    def _draw_centered_watermark(
        self,
        c: canvas.Canvas,
        text: str,
        style: WatermarkStyle,
        page_size: Tuple[float, float],
        font_name: str
    ):
        """绘制居中水印"""
        width, height = page_size
        
        c.setFont(font_name, style.font_size * 1.5)  # 居中水印稍大
        
        text_width = c.stringWidth(text, font_name, style.font_size * 1.5)
        
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(style.rotation)
        c.drawString(-text_width / 2, 0, text)
        c.restoreState()
    
    def _draw_diagonal_watermark(
        self,
        c: canvas.Canvas,
        text: str,
        style: WatermarkStyle,
        page_size: Tuple[float, float],
        font_name: str
    ):
        """绘制对角线水印"""
        width, height = page_size
        
        # 使用较大字体
        font_size = style.font_size * 2
        c.setFont(font_name, font_size)
        
        text_width = c.stringWidth(text, font_name, font_size)
        
        # 从左下到右上绘制
        c.saveState()
        c.translate(width / 2, height / 2)
        c.rotate(-45)  # 对角线角度
        c.drawString(-text_width / 2, 0, text)
        c.restoreState()
    
    def _draw_header_footer_watermark(
        self,
        c: canvas.Canvas,
        text: str,
        style: WatermarkStyle,
        page_size: Tuple[float, float],
        font_name: str
    ):
        """绘制页眉页脚水印"""
        width, height = page_size
        
        font_size = style.font_size * 0.6
        c.setFont(font_name, font_size)
        
        text_width = c.stringWidth(text, font_name, font_size)
        
        # 页眉
        c.drawString((width - text_width) / 2, height - style.margin - font_size, text)
        
        # 页脚
        c.drawString((width - text_width) / 2, style.margin, text)
    
    def _format_watermark_text(self, info: WatermarkInfo, style: WatermarkStyle) -> str:
        """格式化水印文本"""
        text = info.to_string(separator=" | ", compact=True)
        
        if style.prefix:
            text = f"{style.prefix} {text}"
        if style.suffix:
            text = f"{text} {style.suffix}"
        
        return text
    
    def create_watermarked_pdf(
        self,
        output_path: Union[str, Path],
        content: str,
        info: WatermarkInfo,
        style: Optional[WatermarkStyle] = None,
        page_size: Tuple[float, float] = A4
    ) -> str:
        """
        创建带水印的新PDF文档
        
        Args:
            output_path: 输出路径
            content: 文档内容
            info: 水印信息
            style: 水印样式
            page_size: 页面尺寸
            
        Returns:
            输出文件路径
        """
        output_path = Path(output_path)
        style = style or self.default_style
        
        # 注册字体
        font_name = self._register_font(style.font_name)
        
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=page_size)
        
        width, height = page_size
        
        # 设置字体
        c.setFont(font_name, 12)
        
        # 绘制内容
        y = height - 50
        for line in content.split('\n'):
            if y < 50:
                c.showPage()
                c.setFont(font_name, 12)
                y = height - 50
            c.drawString(50, y, line)
            y -= 15
        
        c.save()
        packet.seek(0)
        
        # 保存临时PDF
        temp_path = output_path.with_suffix('.temp.pdf')
        with open(temp_path, 'wb') as f:
            f.write(packet.getvalue())
        
        # 添加水印
        self.embed(temp_path, output_path, info, style)
        
        # 删除临时文件
        os.unlink(temp_path)
        
        return str(output_path)
    
    def extract(
        self,
        pdf_path: Union[str, Path]
    ) -> Optional[WatermarkInfo]:
        """
        从PDF中提取水印信息
        
        Args:
            pdf_path: PDF路径
            
        Returns:
            提取的水印信息
            
        Note:
            PDF水印提取较为复杂，可能需要OCR支持
        """
        reader = PdfReader(pdf_path)
        
        # 尝试从第一页提取文本
        for page in reader.pages:
            text = page.extract_text()
            if text:
                # 查找水印特征
                lines = text.split('\n')
                for line in lines:
                    if "用户:" in line or "工号:" in line:
                        return WatermarkInfo.from_string(line.strip())
        
        return None
    
    def batch_embed(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        info: WatermarkInfo,
        style: Optional[WatermarkStyle] = None,
        recursive: bool = False
    ) -> List[str]:
        """
        批量添加水印
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            info: 水印信息
            style: 水印样式
            recursive: 是否递归处理
            
        Returns:
            处理的文件列表
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        processed = []
        
        pattern = "**/*.pdf" if recursive else "*.pdf"
        
        for input_file in input_dir.glob(pattern):
            relative_path = input_file.relative_to(input_dir)
            output_file = output_dir / relative_path
            
            try:
                self.embed(input_file, output_file, info, style)
                processed.append(str(output_file))
            except Exception as e:
                print(f"处理失败 {input_file}: {e}")
        
        return processed
    
    def get_pdf_info(self, pdf_path: Union[str, Path]) -> dict:
        """
        获取PDF信息
        
        Args:
            pdf_path: PDF路径
            
        Returns:
            PDF信息字典
        """
        reader = PdfReader(pdf_path)
        
        info = {
            "pages": len(reader.pages),
            "encrypted": reader.is_encrypted,
            "metadata": {},
        }
        
        if reader.metadata:
            info["metadata"] = {
                "title": reader.metadata.get("/Title", ""),
                "author": reader.metadata.get("/Author", ""),
                "creator": reader.metadata.get("/Creator", ""),
                "producer": reader.metadata.get("/Producer", ""),
            }
        
        # 获取第一页尺寸
        if reader.pages:
            page = reader.pages[0]
            info["width"] = float(page.mediabox.width)
            info["height"] = float(page.mediabox.height)
        
        return info
