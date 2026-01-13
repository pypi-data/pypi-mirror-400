"""
文本水印处理器 - 支持文本内容添加明水印和提取
"""

import re
import json
from pathlib import Path
from typing import Optional, Union, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from visualwm.core.info import WatermarkInfo
from visualwm.core.style import WatermarkStyle, RiskLevel


class TextWatermarkFormat(Enum):
    """文本水印格式"""
    HEADER = "header"           # 头部水印
    FOOTER = "footer"           # 尾部水印
    HEADER_FOOTER = "header_footer"  # 头尾水印
    INLINE = "inline"           # 行内水印
    MARGIN = "margin"           # 边距水印
    BRACKET = "bracket"         # 括号包围


@dataclass
class TextWatermarkStyle:
    """
    文本水印样式
    
    Attributes:
        format: 水印格式
        separator: 分隔符
        line_prefix: 行前缀（边距水印）
        bracket_left: 左括号
        bracket_right: 右括号
        repeat_interval: 重复间隔（行内水印）
        include_border: 是否包含边框
        border_char: 边框字符
        risk_level: 风险等级
    """
    format: TextWatermarkFormat = TextWatermarkFormat.HEADER_FOOTER
    separator: str = "\n"
    line_prefix: str = "| "
    bracket_left: str = "【"
    bracket_right: str = "】"
    repeat_interval: int = 10
    include_border: bool = True
    border_char: str = "="
    border_length: int = 60
    risk_level: RiskLevel = RiskLevel.LOW
    prefix: str = ""
    
    @classmethod
    def header_preset(cls) -> "TextWatermarkStyle":
        """头部水印预设"""
        return cls(format=TextWatermarkFormat.HEADER)
    
    @classmethod
    def footer_preset(cls) -> "TextWatermarkStyle":
        """尾部水印预设"""
        return cls(format=TextWatermarkFormat.FOOTER)
    
    @classmethod
    def high_risk_preset(cls) -> "TextWatermarkStyle":
        """高风险预设"""
        return cls(
            format=TextWatermarkFormat.HEADER_FOOTER,
            include_border=True,
            border_char="*",
            risk_level=RiskLevel.HIGH,
            prefix="【机密】"
        )


class TextWatermark:
    """
    文本水印处理器
    
    支持在纯文本内容中添加明水印，并从文本中提取水印信息。
    
    Features:
        - 多种水印格式：头部、尾部、行内、边距
        - 风险等级标识
        - 水印信息提取
        - 防篡改校验
    """
    
    # 水印标记
    WATERMARK_START_MARKER = "<!-- VISUALWM_START -->"
    WATERMARK_END_MARKER = "<!-- VISUALWM_END -->"
    
    def __init__(self, default_style: Optional[TextWatermarkStyle] = None):
        """
        初始化文本水印处理器
        
        Args:
            default_style: 默认水印样式
        """
        self.default_style = default_style or TextWatermarkStyle()
    
    def embed(
        self,
        content: str,
        info: WatermarkInfo,
        style: Optional[TextWatermarkStyle] = None,
    ) -> str:
        """
        在文本内容中嵌入水印
        
        Args:
            content: 原始文本内容
            info: 水印信息
            style: 水印样式
            
        Returns:
            带水印的文本内容
        """
        style = style or self.default_style
        
        # 生成水印文本
        watermark_text = self._generate_watermark_text(info, style)
        
        # 根据格式添加水印
        format_type = style.format
        
        if format_type == TextWatermarkFormat.HEADER:
            return self._add_header_watermark(content, watermark_text, style)
        
        elif format_type == TextWatermarkFormat.FOOTER:
            return self._add_footer_watermark(content, watermark_text, style)
        
        elif format_type == TextWatermarkFormat.HEADER_FOOTER:
            return self._add_header_footer_watermark(content, watermark_text, style)
        
        elif format_type == TextWatermarkFormat.INLINE:
            return self._add_inline_watermark(content, watermark_text, style)
        
        elif format_type == TextWatermarkFormat.MARGIN:
            return self._add_margin_watermark(content, watermark_text, style)
        
        elif format_type == TextWatermarkFormat.BRACKET:
            return self._add_bracket_watermark(content, watermark_text, style)
        
        else:
            raise ValueError(f"不支持的水印格式: {format_type}")
    
    def _generate_watermark_text(
        self,
        info: WatermarkInfo,
        style: TextWatermarkStyle
    ) -> str:
        """生成水印文本"""
        text = info.to_string(separator=" | ")
        
        if style.prefix:
            text = f"{style.prefix} {text}"
        
        return text
    
    def _create_border(self, style: TextWatermarkStyle) -> str:
        """创建边框"""
        return style.border_char * style.border_length
    
    def _add_header_watermark(
        self,
        content: str,
        watermark_text: str,
        style: TextWatermarkStyle
    ) -> str:
        """添加头部水印"""
        parts = []
        
        if style.include_border:
            parts.append(self._create_border(style))
        
        parts.append(self.WATERMARK_START_MARKER)
        parts.append(watermark_text)
        parts.append(self.WATERMARK_END_MARKER)
        
        if style.include_border:
            parts.append(self._create_border(style))
        
        parts.append("")
        parts.append(content)
        
        return "\n".join(parts)
    
    def _add_footer_watermark(
        self,
        content: str,
        watermark_text: str,
        style: TextWatermarkStyle
    ) -> str:
        """添加尾部水印"""
        parts = [content, ""]
        
        if style.include_border:
            parts.append(self._create_border(style))
        
        parts.append(self.WATERMARK_START_MARKER)
        parts.append(watermark_text)
        parts.append(self.WATERMARK_END_MARKER)
        
        if style.include_border:
            parts.append(self._create_border(style))
        
        return "\n".join(parts)
    
    def _add_header_footer_watermark(
        self,
        content: str,
        watermark_text: str,
        style: TextWatermarkStyle
    ) -> str:
        """添加头尾水印"""
        parts = []
        
        # 头部
        if style.include_border:
            parts.append(self._create_border(style))
        
        parts.append(self.WATERMARK_START_MARKER)
        parts.append(watermark_text)
        parts.append(self.WATERMARK_END_MARKER)
        
        if style.include_border:
            parts.append(self._create_border(style))
        
        parts.append("")
        parts.append(content)
        parts.append("")
        
        # 尾部
        if style.include_border:
            parts.append(self._create_border(style))
        
        parts.append(self.WATERMARK_START_MARKER)
        parts.append(watermark_text)
        parts.append(self.WATERMARK_END_MARKER)
        
        if style.include_border:
            parts.append(self._create_border(style))
        
        return "\n".join(parts)
    
    def _add_inline_watermark(
        self,
        content: str,
        watermark_text: str,
        style: TextWatermarkStyle
    ) -> str:
        """添加行内水印"""
        lines = content.split("\n")
        result = []
        
        inline_marker = f" {style.bracket_left}{watermark_text}{style.bracket_right}"
        
        for i, line in enumerate(lines):
            if i > 0 and i % style.repeat_interval == 0:
                result.append(line + inline_marker)
            else:
                result.append(line)
        
        return "\n".join(result)
    
    def _add_margin_watermark(
        self,
        content: str,
        watermark_text: str,
        style: TextWatermarkStyle
    ) -> str:
        """添加边距水印"""
        lines = content.split("\n")
        
        # 计算最长行
        max_length = max(len(line) for line in lines) if lines else 0
        
        # 添加头部水印
        header = f"{style.line_prefix}{watermark_text}"
        border = style.line_prefix + style.border_char * (max_length + 20)
        
        result = [border, header, border]
        
        for line in lines:
            result.append(f"{style.line_prefix}{line}")
        
        result.append(border)
        result.append(header)
        result.append(border)
        
        return "\n".join(result)
    
    def _add_bracket_watermark(
        self,
        content: str,
        watermark_text: str,
        style: TextWatermarkStyle
    ) -> str:
        """添加括号包围水印"""
        marker = f"{style.bracket_left}{watermark_text}{style.bracket_right}"
        
        return f"{marker}\n\n{content}\n\n{marker}"
    
    def embed_to_file(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        info: WatermarkInfo,
        style: Optional[TextWatermarkStyle] = None,
        encoding: str = "utf-8"
    ) -> str:
        """
        为文本文件添加水印
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径
            info: 水印信息
            style: 水印样式
            encoding: 文件编码
            
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        # 读取文件
        with open(input_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        # 添加水印
        watermarked = self.embed(content, info, style)
        
        # 写入文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding=encoding) as f:
            f.write(watermarked)
        
        return str(output_path)
    
    def extract(self, content: str) -> Optional[WatermarkInfo]:
        """
        从文本中提取水印信息
        
        Args:
            content: 带水印的文本内容
            
        Returns:
            提取的水印信息，如果未找到返回None
        """
        # 尝试使用标记提取
        pattern = f"{re.escape(self.WATERMARK_START_MARKER)}\\s*(.+?)\\s*{re.escape(self.WATERMARK_END_MARKER)}"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            watermark_text = match.group(1).strip()
            return WatermarkInfo.from_string(watermark_text)
        
        # 尝试使用括号提取
        bracket_pattern = r"【(.+?)】"
        matches = re.findall(bracket_pattern, content)
        
        for match in matches:
            if "用户:" in match or "工号:" in match or "IP:" in match:
                return WatermarkInfo.from_string(match)
        
        return None
    
    def extract_from_file(
        self,
        file_path: Union[str, Path],
        encoding: str = "utf-8"
    ) -> Optional[WatermarkInfo]:
        """
        从文本文件中提取水印信息
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
            
        Returns:
            提取的水印信息
        """
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        return self.extract(content)
    
    def remove_watermark(self, content: str) -> str:
        """
        移除文本中的水印
        
        Args:
            content: 带水印的文本
            
        Returns:
            移除水印后的文本
            
        Note:
            此功能主要用于测试，实际应用中不建议使用
        """
        # 移除标记水印
        pattern = f"{re.escape(self.WATERMARK_START_MARKER)}.*?{re.escape(self.WATERMARK_END_MARKER)}"
        content = re.sub(pattern, "", content, flags=re.DOTALL)
        
        # 移除边框
        content = re.sub(r"^[=*\-]{20,}\n", "", content, flags=re.MULTILINE)
        
        # 清理空行
        content = re.sub(r"\n{3,}", "\n\n", content)
        
        return content.strip()
    
    def verify_watermark(
        self,
        content: str,
        expected_info: WatermarkInfo
    ) -> Dict[str, Any]:
        """
        验证水印完整性
        
        Args:
            content: 带水印的文本
            expected_info: 预期的水印信息
            
        Returns:
            验证结果字典
        """
        result = {
            "is_valid": False,
            "watermark_found": False,
            "checksum_valid": False,
            "info_match": False,
            "details": []
        }
        
        # 提取水印
        extracted = self.extract(content)
        
        if extracted is None:
            result["details"].append("未找到水印")
            return result
        
        result["watermark_found"] = True
        
        # 验证校验码
        if extracted.checksum and expected_info.checksum:
            if extracted.checksum[:8] == expected_info.checksum[:8]:
                result["checksum_valid"] = True
            else:
                result["details"].append("校验码不匹配")
        
        # 验证关键信息
        if (extracted.username == expected_info.username and
            extracted.employee_id == expected_info.employee_id):
            result["info_match"] = True
        else:
            result["details"].append("用户信息不匹配")
        
        result["is_valid"] = result["checksum_valid"] and result["info_match"]
        
        return result
    
    def batch_embed(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        info: WatermarkInfo,
        style: Optional[TextWatermarkStyle] = None,
        file_extensions: List[str] = None,
        recursive: bool = False,
        encoding: str = "utf-8"
    ) -> List[str]:
        """
        批量添加水印
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            info: 水印信息
            style: 水印样式
            file_extensions: 文件扩展名列表
            recursive: 是否递归处理
            encoding: 文件编码
            
        Returns:
            处理的文件列表
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if file_extensions is None:
            file_extensions = ['.txt', '.md', '.rst', '.log']
        
        processed = []
        
        # 获取文件列表
        if recursive:
            files = input_dir.rglob("*")
        else:
            files = input_dir.glob("*")
        
        for input_file in files:
            if input_file.suffix.lower() in file_extensions:
                relative_path = input_file.relative_to(input_dir)
                output_file = output_dir / relative_path
                
                try:
                    self.embed_to_file(input_file, output_file, info, style, encoding)
                    processed.append(str(output_file))
                except Exception as e:
                    print(f"处理失败 {input_file}: {e}")
        
        return processed


class HTMLWatermark(TextWatermark):
    """
    HTML水印处理器
    
    专门用于处理HTML内容的水印。
    """
    
    def embed(
        self,
        content: str,
        info: WatermarkInfo,
        style: Optional[TextWatermarkStyle] = None,
    ) -> str:
        """在HTML内容中嵌入水印"""
        style = style or self.default_style
        watermark_text = self._generate_watermark_text(info, style)
        
        # 创建HTML水印元素
        watermark_html = self._create_html_watermark(watermark_text, style)
        
        # 插入到body后面
        if "</body>" in content.lower():
            content = re.sub(
                r"(</body>)",
                f"{watermark_html}\\1",
                content,
                flags=re.IGNORECASE
            )
        else:
            content = f"{content}\n{watermark_html}"
        
        return content
    
    def _create_html_watermark(
        self,
        watermark_text: str,
        style: TextWatermarkStyle
    ) -> str:
        """创建HTML水印元素"""
        color = "red" if style.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else "gray"
        opacity = "0.7" if style.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else "0.5"
        
        return f'''
<!-- VISUALWM_START -->
<div class="visualwm-watermark" style="
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 999999;
    background: repeating-linear-gradient(
        -45deg,
        transparent,
        transparent 100px,
        rgba(0,0,0,0.02) 100px,
        rgba(0,0,0,0.02) 200px
    );
">
    <div style="
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%) rotate(-30deg);
        font-size: 24px;
        color: {color};
        opacity: {opacity};
        white-space: nowrap;
        font-family: Arial, sans-serif;
    ">
        {watermark_text}
    </div>
</div>
<!-- VISUALWM_END -->
'''


class MarkdownWatermark(TextWatermark):
    """
    Markdown水印处理器
    
    专门用于处理Markdown内容的水印。
    """
    
    def embed(
        self,
        content: str,
        info: WatermarkInfo,
        style: Optional[TextWatermarkStyle] = None,
    ) -> str:
        """在Markdown内容中嵌入水印"""
        style = style or self.default_style
        watermark_text = self._generate_watermark_text(info, style)
        
        # 创建Markdown水印
        warning = ""
        if style.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            warning = "⚠️ **机密文档** ⚠️\n\n"
        
        header = f"""
---

{warning}> **文档水印信息**
> {watermark_text}

---

"""
        
        footer = f"""

---

> **文档水印信息**
> {watermark_text}

---
"""
        
        return f"{header}{content}{footer}"
