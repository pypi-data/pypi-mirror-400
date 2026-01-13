"""
图片水印处理器 - 支持图片添加明水印和提取
"""

import os
import math
from pathlib import Path
from typing import Optional, Tuple, Union, List
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np

from visualwm.core.info import WatermarkInfo
from visualwm.core.style import WatermarkStyle, WatermarkPosition


class ImageWatermark:
    """
    图片水印处理器
    
    支持在图片上添加明水印，并从图片中提取水印信息。
    
    Features:
        - 多种位置模式：平铺、居中、角落
        - 自定义样式：字体、颜色、透明度、旋转
        - 支持多种图片格式
        - 水印信息提取（OCR）
    """
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
    
    # 默认字体搜索路径
    FONT_PATHS = [
        os.path.join(os.path.dirname(__file__), "..", "font"),  # SDK内置字体目录
        "/usr/share/fonts/opentype/noto/",
        "/usr/share/fonts/truetype/wqy/",
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/truetype/",
        "/usr/share/fonts/opentype/",
        "/usr/share/fonts/",
        "/System/Library/Fonts/",
        "/Library/Fonts/",
        "C:/Windows/Fonts/",
        "./fonts/",
    ]
    
    # 中文字体文件名映射
    CJK_FONT_FILES = [
        "NotoSerifSC-VariableFont_wght.ttf",  # SDK内置字体
        "NotoSansCJK-Regular.ttc",
        "NotoSansCJKsc-Regular.otf", 
        "wqy-zenhei.ttc",
        "wqy-microhei.ttc",
        "DejaVuSans.ttf",
    ]
    
    def __init__(self, default_style: Optional[WatermarkStyle] = None):
        """
        初始化图片水印处理器
        
        Args:
            default_style: 默认水印样式
        """
        self.default_style = default_style or WatermarkStyle.default()
        self._font_cache = {}
    
    def embed(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        info: WatermarkInfo,
        style: Optional[WatermarkStyle] = None,
    ) -> str:
        """
        在图片中嵌入水印
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            info: 水印信息
            style: 水印样式（可选，使用默认样式）
            
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        style = style or self.default_style
        
        # 验证输入文件
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        if input_path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的图片格式: {input_path.suffix}")
        
        # 打开图片
        image = Image.open(input_path)
        
        # 确保是RGBA模式以支持透明度
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 添加水印
        watermarked = self._add_watermark(image, info, style)
        
        # 保存图片
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 根据输出格式处理
        if output_path.suffix.lower() in {'.jpg', '.jpeg'}:
            # JPEG不支持透明度，转换为RGB
            watermarked = watermarked.convert('RGB')
        
        watermarked.save(output_path, quality=95)
        
        return str(output_path)
    
    def embed_to_bytes(
        self,
        image_bytes: bytes,
        info: WatermarkInfo,
        style: Optional[WatermarkStyle] = None,
        format: str = "PNG"
    ) -> bytes:
        """
        在内存中处理图片并返回字节
        
        Args:
            image_bytes: 输入图片字节
            info: 水印信息
            style: 水印样式
            format: 输出格式
            
        Returns:
            带水印的图片字节
        """
        from io import BytesIO
        
        style = style or self.default_style
        
        # 从字节加载图片
        image = Image.open(BytesIO(image_bytes))
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # 添加水印
        watermarked = self._add_watermark(image, info, style)
        
        # 输出到字节
        output = BytesIO()
        if format.upper() in {'JPG', 'JPEG'}:
            watermarked = watermarked.convert('RGB')
        watermarked.save(output, format=format, quality=95)
        
        return output.getvalue()
    
    def _add_watermark(
        self,
        image: Image.Image,
        info: WatermarkInfo,
        style: WatermarkStyle
    ) -> Image.Image:
        """
        添加水印到图片
        
        Args:
            image: PIL图片对象
            info: 水印信息
            style: 水印样式
            
        Returns:
            带水印的图片
        """
        # 获取水印文本
        watermark_text = self._format_watermark_text(info, style)
        
        # 根据位置模式添加水印
        position = style.position.lower()
        
        if position == "tile":
            return self._add_tiled_watermark(image, watermark_text, style)
        elif position == "center":
            return self._add_centered_watermark(image, watermark_text, style)
        else:
            return self._add_positioned_watermark(image, watermark_text, style, position)
    
    def _format_watermark_text(self, info: WatermarkInfo, style: WatermarkStyle) -> str:
        """格式化水印文本"""
        text = info.to_string(separator=" | ", compact=True)
        
        if style.prefix:
            text = f"{style.prefix} {text}"
        if style.suffix:
            text = f"{text} {style.suffix}"
        
        return text
    
    def _get_font(self, style: WatermarkStyle) -> ImageFont.FreeTypeFont:
        """获取字体对象"""
        cache_key = (style.font_name, style.font_size, style.bold, style.italic)
        
        if cache_key in self._font_cache:
            return self._font_cache[cache_key]
        
        font = None
        
        # 首先尝试直接加载CJK字体文件（优先级最高）
        for font_file in self.CJK_FONT_FILES:
            for font_path in self.FONT_PATHS:
                full_path = os.path.join(font_path, font_file)
                if os.path.exists(full_path):
                    try:
                        font = ImageFont.truetype(full_path, style.font_size)
                        self._font_cache[cache_key] = font
                        return font
                    except (IOError, OSError):
                        continue
        
        # 尝试加载指定字体
        font_names = [style.font_name]
        
        # 添加备选字体
        if style.bold:
            font_names.append(f"{style.font_name}-Bold")
            font_names.append(f"{style.font_name}Bold")
        
        # 添加中文字体备选
        font_names.extend([
            "SimHei", "Microsoft YaHei", "STHeiti", "Noto Sans CJK SC",
            "WenQuanYi Micro Hei", "DejaVuSans", "Arial Unicode MS"
        ])
        
        for font_name in font_names:
            # 尝试直接加载
            try:
                font = ImageFont.truetype(font_name, style.font_size)
                break
            except (IOError, OSError):
                pass
            
            # 在字体目录中搜索
            for font_path in self.FONT_PATHS:
                for ext in ['.ttf', '.ttc', '.otf']:
                    try:
                        full_path = os.path.join(font_path, f"{font_name}{ext}")
                        if os.path.exists(full_path):
                            font = ImageFont.truetype(full_path, style.font_size)
                            break
                    except (IOError, OSError):
                        continue
                if font:
                    break
            
            if font:
                break
        
        # 如果所有字体都失败，使用默认字体
        if font is None:
            font = ImageFont.load_default()
        
        self._font_cache[cache_key] = font
        return font
    
    def _add_tiled_watermark(
        self,
        image: Image.Image,
        text: str,
        style: WatermarkStyle
    ) -> Image.Image:
        """添加平铺水印"""
        width, height = image.size
        font = self._get_font(style)
        
        # 创建水印层
        watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 创建单个水印图像（带旋转）
        diagonal = int(math.sqrt(text_width**2 + text_height**2)) + 20
        single_watermark = Image.new('RGBA', (diagonal, diagonal), (0, 0, 0, 0))
        single_draw = ImageDraw.Draw(single_watermark)
        
        # 计算居中位置
        x = (diagonal - text_width) // 2
        y = (diagonal - text_height) // 2
        
        # 绘制阴影
        if style.shadow:
            shadow_x = x + style.shadow_offset[0]
            shadow_y = y + style.shadow_offset[1]
            shadow_color = (*style.shadow_color, int(style.opacity * 128))
            single_draw.text((shadow_x, shadow_y), text, font=font, fill=shadow_color)
        
        # 绘制文本
        single_draw.text((x, y), text, font=font, fill=style.rgba_color)
        
        # 旋转水印
        single_watermark = single_watermark.rotate(
            style.rotation, 
            expand=False, 
            resample=Image.BICUBIC
        )
        
        # 平铺水印
        spacing_x = text_width + style.column_spacing
        spacing_y = text_height + style.line_spacing
        
        for y_pos in range(-diagonal, height + diagonal, spacing_y):
            # 奇偶行错开
            offset = spacing_x // 2 if (y_pos // spacing_y) % 2 else 0
            for x_pos in range(-diagonal + offset, width + diagonal, spacing_x):
                watermark_layer.paste(single_watermark, (x_pos, y_pos), single_watermark)
        
        # 合并图层
        return Image.alpha_composite(image, watermark_layer)
    
    def _add_centered_watermark(
        self,
        image: Image.Image,
        text: str,
        style: WatermarkStyle
    ) -> Image.Image:
        """添加居中水印"""
        width, height = image.size
        font = self._get_font(style)
        
        # 创建水印层
        watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 创建单个水印图像
        padding = 40
        single_watermark = Image.new(
            'RGBA', 
            (text_width + padding * 2, text_height + padding * 2), 
            (0, 0, 0, 0)
        )
        single_draw = ImageDraw.Draw(single_watermark)
        
        # 绘制背景
        if style.background_color:
            single_draw.rectangle(
                [0, 0, text_width + padding * 2, text_height + padding * 2],
                fill=style.background_color
            )
        
        # 绘制边框
        if style.border:
            single_draw.rectangle(
                [0, 0, text_width + padding * 2 - 1, text_height + padding * 2 - 1],
                outline=(*style.border_color, int(style.opacity * 255)),
                width=style.border_width
            )
        
        # 绘制阴影
        if style.shadow:
            shadow_color = (*style.shadow_color, int(style.opacity * 128))
            single_draw.text(
                (padding + style.shadow_offset[0], padding + style.shadow_offset[1]),
                text, font=font, fill=shadow_color
            )
        
        # 绘制文本
        single_draw.text((padding, padding), text, font=font, fill=style.rgba_color)
        
        # 旋转水印
        single_watermark = single_watermark.rotate(
            style.rotation,
            expand=True,
            resample=Image.BICUBIC
        )
        
        # 计算居中位置
        wm_width, wm_height = single_watermark.size
        x = (width - wm_width) // 2
        y = (height - wm_height) // 2
        
        # 粘贴水印
        watermark_layer.paste(single_watermark, (x, y), single_watermark)
        
        return Image.alpha_composite(image, watermark_layer)
    
    def _add_positioned_watermark(
        self,
        image: Image.Image,
        text: str,
        style: WatermarkStyle,
        position: str
    ) -> Image.Image:
        """添加定位水印（角落等）"""
        width, height = image.size
        font = self._get_font(style)
        
        # 创建水印层
        watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算位置
        margin = style.margin
        
        position_map = {
            "top_left": (margin, margin),
            "top_right": (width - text_width - margin, margin),
            "bottom_left": (margin, height - text_height - margin),
            "bottom_right": (width - text_width - margin, height - text_height - margin),
            "top_center": ((width - text_width) // 2, margin),
            "bottom_center": ((width - text_width) // 2, height - text_height - margin),
        }
        
        x, y = position_map.get(position, (margin, margin))
        
        # 绘制背景
        if style.background_color:
            padding = 5
            draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                fill=style.background_color
            )
        
        # 绘制边框
        if style.border:
            padding = 5
            draw.rectangle(
                [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
                outline=(*style.border_color, int(style.opacity * 255)),
                width=style.border_width
            )
        
        # 绘制阴影
        if style.shadow:
            shadow_color = (*style.shadow_color, int(style.opacity * 128))
            draw.text(
                (x + style.shadow_offset[0], y + style.shadow_offset[1]),
                text, font=font, fill=shadow_color
            )
        
        # 绘制文本
        draw.text((x, y), text, font=font, fill=style.rgba_color)
        
        return Image.alpha_composite(image, watermark_layer)
    
    def extract(
        self,
        image_path: Union[str, Path],
        use_ocr: bool = False
    ) -> Optional[WatermarkInfo]:
        """
        从图片中提取水印信息
        
        Args:
            image_path: 图片路径
            use_ocr: 是否使用OCR（需要额外依赖）
            
        Returns:
            提取的水印信息，如果无法提取返回None
            
        Note:
            明水印的提取依赖OCR技术，需要安装pytesseract等OCR库
        """
        if use_ocr:
            return self._extract_with_ocr(image_path)
        else:
            # 不使用OCR时，返回提示信息
            print("警告：明水印提取需要启用OCR功能，请设置 use_ocr=True")
            print("需要安装：pip install pytesseract")
            return None
    
    def _extract_with_ocr(self, image_path: Union[str, Path]) -> Optional[WatermarkInfo]:
        """使用OCR提取水印"""
        try:
            import pytesseract
        except ImportError:
            raise ImportError(
                "OCR功能需要安装pytesseract: pip install pytesseract\n"
                "同时需要安装Tesseract OCR引擎"
            )
        
        image = Image.open(image_path)
        
        # 图像预处理以提高OCR准确率
        # 转换为灰度
        gray = image.convert('L')
        
        # 增强对比度
        enhancer = ImageEnhance.Contrast(gray)
        enhanced = enhancer.enhance(2.0)
        
        # OCR识别
        text = pytesseract.image_to_string(enhanced, lang='chi_sim+eng')
        
        # 尝试解析水印信息
        if text.strip():
            try:
                return WatermarkInfo.from_string(text.strip())
            except Exception:
                # 解析失败，返回原始文本
                return WatermarkInfo(custom_data={"raw_text": text.strip()})
        
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
            recursive: 是否递归处理子目录
            
        Returns:
            处理的文件列表
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not input_dir.is_dir():
            raise ValueError(f"输入路径不是目录: {input_dir}")
        
        processed = []
        
        # 获取文件列表
        if recursive:
            files = input_dir.rglob("*")
        else:
            files = input_dir.glob("*")
        
        for input_file in files:
            if input_file.suffix.lower() in self.SUPPORTED_FORMATS:
                # 计算输出路径
                relative_path = input_file.relative_to(input_dir)
                output_file = output_dir / relative_path
                
                try:
                    self.embed(input_file, output_file, info, style)
                    processed.append(str(output_file))
                except Exception as e:
                    print(f"处理失败 {input_file}: {e}")
        
        return processed
    
    def add_multiline_watermark(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        info: WatermarkInfo,
        style: Optional[WatermarkStyle] = None,
    ) -> str:
        """
        添加多行水印
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            info: 水印信息
            style: 水印样式
            
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        style = style or self.default_style
        
        image = Image.open(input_path)
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        width, height = image.size
        font = self._get_font(style)
        
        # 创建水印层
        watermark_layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)
        
        # 获取多行文本
        lines = info.to_multiline_string().split('\n')
        
        # 计算总高度
        line_heights = []
        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            h = bbox[3] - bbox[1]
            line_heights.append(h)
            total_height += h + 5  # 5px行间距
        
        # 计算起始位置（居中）
        start_y = (height - total_height) // 2
        
        # 绘制每行
        y = start_y
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            draw.text((x, y), line, font=font, fill=style.rgba_color)
            y += line_heights[i] + 5
        
        # 合并图层
        result = Image.alpha_composite(image, watermark_layer)
        
        # 保存
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.suffix.lower() in {'.jpg', '.jpeg'}:
            result = result.convert('RGB')
        result.save(output_path, quality=95)
        
        return str(output_path)
