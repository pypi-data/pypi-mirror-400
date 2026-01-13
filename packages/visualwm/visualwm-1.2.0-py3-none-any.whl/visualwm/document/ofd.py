"""
OFD文档水印处理器 - 支持.ofd格式添加明水印

OFD (Open Fixed-layout Document) 是中国电子公文交换的版式文档格式标准。
OFD文件本质上是一个ZIP压缩包，包含XML描述文件和资源文件。
"""

import os
import io
import zipfile
import tempfile
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, Union, List, Dict, Any
from datetime import datetime

from visualwm.core.info import WatermarkInfo
from visualwm.core.style import WatermarkStyle, RiskLevel


class OFDWatermark:
    """
    OFD文档水印处理器
    
    支持在OFD文档中添加明水印。
    
    OFD文件结构：
    - OFD.xml: 入口文件
    - Doc_0/Document.xml: 文档描述
    - Doc_0/Pages/Page_0/Content.xml: 页面内容
    - Doc_0/Res/: 资源文件
    
    Features:
        - 支持.ofd格式
        - 文本水印层
        - 注释水印
        - 批量处理
        
    Note:
        OFD格式相对复杂，此实现提供基本的水印功能。
        对于更复杂的需求，建议使用专业的OFD处理库。
    """
    
    SUPPORTED_EXTENSIONS = {'.ofd'}
    
    # OFD命名空间
    OFD_NAMESPACE = "http://www.ofdspec.org/2016"
    
    def __init__(self, default_style: Optional[WatermarkStyle] = None):
        """
        初始化OFD水印处理器
        
        Args:
            default_style: 默认水印样式
        """
        self.default_style = default_style or WatermarkStyle.default()
        
        # 注册命名空间
        ET.register_namespace('ofd', self.OFD_NAMESPACE)
    
    def embed(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        info: WatermarkInfo,
        style: Optional[WatermarkStyle] = None,
        watermark_type: str = "annotation"
    ) -> str:
        """
        在OFD文档中嵌入水印
        
        Args:
            input_path: 输入OFD路径
            output_path: 输出OFD路径
            info: 水印信息
            style: 水印样式
            watermark_type: 水印类型 ("annotation", "layer", "metadata")
            
        Returns:
            输出文件路径
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        style = style or self.default_style
        
        if not input_path.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_path}")
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 解压OFD文件
            self._extract_ofd(input_path, temp_path)
            
            # 添加水印
            if watermark_type == "annotation":
                self._add_annotation_watermark(temp_path, info, style)
            elif watermark_type == "layer":
                self._add_layer_watermark(temp_path, info, style)
            elif watermark_type == "metadata":
                self._add_metadata_watermark(temp_path, info, style)
            else:
                raise ValueError(f"不支持的水印类型: {watermark_type}")
            
            # 重新打包OFD
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self._pack_ofd(temp_path, output_path)
        
        return str(output_path)
    
    def _extract_ofd(self, ofd_path: Path, extract_path: Path):
        """解压OFD文件"""
        with zipfile.ZipFile(ofd_path, 'r') as zf:
            zf.extractall(extract_path)
    
    def _pack_ofd(self, source_path: Path, ofd_path: Path):
        """打包OFD文件"""
        with zipfile.ZipFile(ofd_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_path)
                    zf.write(file_path, arcname)
    
    def _add_annotation_watermark(
        self,
        ofd_path: Path,
        info: WatermarkInfo,
        style: WatermarkStyle
    ):
        """添加注释水印"""
        watermark_text = self._format_watermark_text(info, style)
        
        # 查找文档目录
        doc_dirs = list(ofd_path.glob("Doc_*"))
        
        for doc_dir in doc_dirs:
            # 创建或更新Annotations.xml
            annot_path = doc_dir / "Annots" / "Annotations.xml"
            annot_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建注释XML
            root = ET.Element('{%s}Annotations' % self.OFD_NAMESPACE)
            
            # 添加水印注释
            annot = ET.SubElement(root, '{%s}Annotation' % self.OFD_NAMESPACE)
            annot.set('ID', 'watermark_annot')
            annot.set('Type', 'Watermark')
            annot.set('Creator', 'VisualWM')
            annot.set('LastModDate', datetime.now().strftime('%Y-%m-%d'))
            
            # 注释内容
            content = ET.SubElement(annot, '{%s}Content' % self.OFD_NAMESPACE)
            content.text = watermark_text
            
            # 保存
            tree = ET.ElementTree(root)
            tree.write(annot_path, encoding='utf-8', xml_declaration=True)
            
            # 更新Document.xml引用
            self._update_document_reference(doc_dir, "Annots/Annotations.xml")
    
    def _add_layer_watermark(
        self,
        ofd_path: Path,
        info: WatermarkInfo,
        style: WatermarkStyle
    ):
        """添加图层水印"""
        watermark_text = self._format_watermark_text(info, style)
        
        # 查找所有页面Content.xml
        for content_path in ofd_path.rglob("Content.xml"):
            try:
                tree = ET.parse(content_path)
                root = tree.getroot()
                
                # 添加水印文本对象
                # 注：实际OFD结构更复杂，这里是简化实现
                watermark_elem = ET.SubElement(root, '{%s}TextObject' % self.OFD_NAMESPACE)
                watermark_elem.set('ID', 'watermark_text')
                watermark_elem.set('Boundary', '10 10 200 20')
                
                text_code = ET.SubElement(watermark_elem, '{%s}TextCode' % self.OFD_NAMESPACE)
                text_code.text = watermark_text
                
                tree.write(content_path, encoding='utf-8', xml_declaration=True)
                
            except ET.ParseError:
                continue
    
    def _add_metadata_watermark(
        self,
        ofd_path: Path,
        info: WatermarkInfo,
        style: WatermarkStyle
    ):
        """添加元数据水印"""
        watermark_text = self._format_watermark_text(info, style)
        
        # 查找OFD.xml
        ofd_xml_path = ofd_path / "OFD.xml"
        
        if ofd_xml_path.exists():
            try:
                tree = ET.parse(ofd_xml_path)
                root = tree.getroot()
                
                # 添加自定义元数据
                custom_data = ET.SubElement(root, '{%s}CustomDatas' % self.OFD_NAMESPACE)
                
                watermark_data = ET.SubElement(custom_data, '{%s}CustomData' % self.OFD_NAMESPACE)
                watermark_data.set('Name', 'Watermark')
                watermark_data.text = watermark_text
                
                creator_data = ET.SubElement(custom_data, '{%s}CustomData' % self.OFD_NAMESPACE)
                creator_data.set('Name', 'WatermarkCreator')
                creator_data.text = 'VisualWM'
                
                timestamp_data = ET.SubElement(custom_data, '{%s}CustomData' % self.OFD_NAMESPACE)
                timestamp_data.set('Name', 'WatermarkTime')
                timestamp_data.text = datetime.now().isoformat()
                
                tree.write(ofd_xml_path, encoding='utf-8', xml_declaration=True)
                
            except ET.ParseError:
                pass
        
        # 同时添加注释水印作为可见标记
        self._add_annotation_watermark(ofd_path, info, style)
    
    def _update_document_reference(self, doc_dir: Path, ref_path: str):
        """更新文档引用"""
        doc_xml_path = doc_dir / "Document.xml"
        
        if doc_xml_path.exists():
            try:
                tree = ET.parse(doc_xml_path)
                root = tree.getroot()
                
                # 添加注释引用
                annots_ref = ET.SubElement(root, '{%s}Annotations' % self.OFD_NAMESPACE)
                annots_ref.text = ref_path
                
                tree.write(doc_xml_path, encoding='utf-8', xml_declaration=True)
                
            except ET.ParseError:
                pass
    
    def _format_watermark_text(self, info: WatermarkInfo, style: WatermarkStyle) -> str:
        """格式化水印文本"""
        text = info.to_string(separator=" | ", compact=True)
        
        if style.prefix:
            text = f"{style.prefix} {text}"
        if style.suffix:
            text = f"{text} {style.suffix}"
        
        return text
    
    def extract(
        self,
        ofd_path: Union[str, Path]
    ) -> Optional[WatermarkInfo]:
        """
        从OFD文档中提取水印信息
        
        Args:
            ofd_path: OFD文件路径
            
        Returns:
            提取的水印信息
        """
        ofd_path = Path(ofd_path)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._extract_ofd(ofd_path, temp_path)
            
            # 从注释中提取
            for annot_path in temp_path.rglob("Annotations.xml"):
                try:
                    tree = ET.parse(annot_path)
                    root = tree.getroot()
                    
                    for content in root.iter('{%s}Content' % self.OFD_NAMESPACE):
                        text = content.text
                        if text and ("用户:" in text or "工号:" in text):
                            return WatermarkInfo.from_string(text)
                except ET.ParseError:
                    continue
            
            # 从元数据中提取
            ofd_xml_path = temp_path / "OFD.xml"
            if ofd_xml_path.exists():
                try:
                    tree = ET.parse(ofd_xml_path)
                    root = tree.getroot()
                    
                    for custom_data in root.iter('{%s}CustomData' % self.OFD_NAMESPACE):
                        if custom_data.get('Name') == 'Watermark':
                            text = custom_data.text
                            if text:
                                return WatermarkInfo.from_string(text)
                except ET.ParseError:
                    pass
        
        return None
    
    def get_ofd_info(self, ofd_path: Union[str, Path]) -> Dict[str, Any]:
        """
        获取OFD文档信息
        
        Args:
            ofd_path: OFD文件路径
            
        Returns:
            文档信息字典
        """
        ofd_path = Path(ofd_path)
        
        info = {
            "file_size": ofd_path.stat().st_size,
            "documents": [],
            "pages": 0,
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._extract_ofd(ofd_path, temp_path)
            
            # 解析OFD.xml
            ofd_xml_path = temp_path / "OFD.xml"
            if ofd_xml_path.exists():
                try:
                    tree = ET.parse(ofd_xml_path)
                    root = tree.getroot()
                    
                    # 获取文档引用
                    for doc_ref in root.iter('{%s}DocRoot' % self.OFD_NAMESPACE):
                        info["documents"].append(doc_ref.text)
                except ET.ParseError:
                    pass
            
            # 统计页面数
            info["pages"] = len(list(temp_path.rglob("Page_*/Content.xml")))
        
        return info
    
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
        
        pattern = "**/*.ofd" if recursive else "*.ofd"
        
        for input_file in input_dir.glob(pattern):
            relative_path = input_file.relative_to(input_dir)
            output_file = output_dir / relative_path
            
            try:
                self.embed(input_file, output_file, info, style)
                processed.append(str(output_file))
            except Exception as e:
                print(f"处理失败 {input_file}: {e}")
        
        return processed
    
    def is_valid_ofd(self, ofd_path: Union[str, Path]) -> bool:
        """
        检查是否为有效的OFD文件
        
        Args:
            ofd_path: OFD文件路径
            
        Returns:
            是否有效
        """
        try:
            with zipfile.ZipFile(ofd_path, 'r') as zf:
                # 检查是否包含OFD.xml
                namelist = zf.namelist()
                return 'OFD.xml' in namelist
        except (zipfile.BadZipFile, FileNotFoundError):
            return False
