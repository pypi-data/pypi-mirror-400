#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisualWM 示例代码 - 文档水印 (Word, PDF, Excel, OFD)
"""

from visualwm import (
    WatermarkInfo,
    WatermarkStyle,
    RiskLevel,
    WordWatermark,
    PDFWatermark,
    ExcelWatermark,
    OFDWatermark,
)


def example_word_watermark():
    """Word文档水印示例"""
    print("=" * 60)
    print("示例1: Word文档水印 (.docx)")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="张三",
        employee_id="EMP001",
        department="研发部",
        auto_fill=True
    )
    
    # 创建Word水印处理器
    wm = WordWatermark()
    
    print("支持的水印类型:")
    print("  - header_footer: 页眉页脚水印")
    print("  - diagonal: 对角线文字水印")
    print("  - background: 背景水印")
    
    print("\n使用方法:")
    print("  wm = WordWatermark()")
    print("  wm.embed('input.docx', 'output.docx', info)")
    print("  wm.embed('input.docx', 'output.docx', info, watermark_type='diagonal')")
    
    # 演示创建新文档
    print("\n创建带水印的新Word文档:")
    print("  wm.embed_new('output.docx', '文档内容...', info)")
    
    print("✓ Word水印配置完成")


def example_pdf_watermark():
    """PDF文档水印示例"""
    print("\n" + "=" * 60)
    print("示例2: PDF文档水印 (.pdf)")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="李四",
        employee_id="EMP002",
        department="安全部",
        auto_fill=True
    )
    
    # 使用高风险样式
    style = WatermarkStyle.high_risk_preset()
    
    print(f"水印样式: 高风险")
    print(f"  前缀: {style.prefix}")
    print(f"  颜色: {style.hex_color}")
    
    # 创建PDF水印处理器
    wm = PDFWatermark()
    
    print("\n支持的水印类型:")
    print("  - tile: 平铺水印（默认）")
    print("  - center: 居中水印")
    print("  - diagonal: 对角线水印")
    print("  - header_footer: 页眉页脚水印")
    
    print("\n使用方法:")
    print("  wm = PDFWatermark()")
    print("  wm.embed('input.pdf', 'output.pdf', info, style)")
    print("  wm.embed('input.pdf', 'output.pdf', info, watermark_type='center')")
    
    # 加密PDF
    print("\n处理加密PDF:")
    print("  wm.embed('encrypted.pdf', 'output.pdf', info, password='密码')")
    
    # 获取PDF信息
    print("\n获取PDF信息:")
    print("  info = wm.get_pdf_info('document.pdf')")
    print("  # 返回: pages, width, height, encrypted, metadata")
    
    print("✓ PDF水印配置完成")


def example_excel_watermark():
    """Excel文档水印示例"""
    print("\n" + "=" * 60)
    print("示例3: Excel文档水印 (.xlsx)")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="王五",
        employee_id="EMP003",
        department="财务部",
        auto_fill=True
    )
    
    # 创建Excel水印处理器
    wm = ExcelWatermark()
    
    print("支持的水印类型:")
    print("  - header_footer: 页眉页脚水印（打印时显示）")
    print("  - first_row: 首行水印")
    print("  - comment: 批注水印")
    print("  - background: 背景列水印")
    
    print("\n使用方法:")
    print("  wm = ExcelWatermark()")
    print("  wm.embed('input.xlsx', 'output.xlsx', info)")
    print("  wm.embed('input.xlsx', 'output.xlsx', info, watermark_type='first_row')")
    
    # 指定工作表
    print("\n指定工作表:")
    print("  wm.embed('input.xlsx', 'output.xlsx', info, sheets=['Sheet1', 'Sheet2'])")
    
    # 创建新Excel
    print("\n创建带水印的新Excel文档:")
    print("  data = [['姓名', '工号'], ['张三', '001'], ['李四', '002']]")
    print("  wm.embed_new('output.xlsx', data, info)")
    
    # 获取工作簿信息
    print("\n获取工作簿信息:")
    print("  info = wm.get_workbook_info('document.xlsx')")
    print("  # 返回: sheet_names, sheet_count, sheets详情")
    
    print("✓ Excel水印配置完成")


def example_ofd_watermark():
    """OFD文档水印示例"""
    print("\n" + "=" * 60)
    print("示例4: OFD文档水印 (.ofd)")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="赵六",
        employee_id="EMP004",
        department="法务部",
        auto_fill=True
    )
    
    print("OFD (Open Fixed-layout Document):")
    print("  - 中国电子公文版式文档格式标准")
    print("  - 结构类似于ZIP压缩包")
    print("  - 包含XML描述和资源文件")
    
    # 创建OFD水印处理器
    wm = OFDWatermark()
    
    print("\n支持的水印类型:")
    print("  - annotation: 注释水印（默认）")
    print("  - layer: 图层水印")
    print("  - metadata: 元数据水印")
    
    print("\n使用方法:")
    print("  wm = OFDWatermark()")
    print("  wm.embed('input.ofd', 'output.ofd', info)")
    print("  wm.embed('input.ofd', 'output.ofd', info, watermark_type='metadata')")
    
    # 验证OFD文件
    print("\n验证OFD文件:")
    print("  is_valid = wm.is_valid_ofd('document.ofd')")
    
    # 获取OFD信息
    print("\n获取OFD信息:")
    print("  info = wm.get_ofd_info('document.ofd')")
    print("  # 返回: file_size, documents, pages")
    
    print("✓ OFD水印配置完成")


def example_batch_processing():
    """批量处理示例"""
    print("\n" + "=" * 60)
    print("示例5: 批量文档处理")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="批量处理",
        employee_id="BATCH001",
        auto_fill=True
    )
    
    print("批量处理Word文档:")
    print("  wm = WordWatermark()")
    print("  processed = wm.batch_embed('./input/', './output/', info, recursive=True)")
    
    print("\n批量处理PDF文档:")
    print("  wm = PDFWatermark()")
    print("  processed = wm.batch_embed('./input/', './output/', info)")
    
    print("\n批量处理Excel文档:")
    print("  wm = ExcelWatermark()")
    print("  processed = wm.batch_embed('./input/', './output/', info)")
    
    print("\n批量处理OFD文档:")
    print("  wm = OFDWatermark()")
    print("  processed = wm.batch_embed('./input/', './output/', info)")
    
    print("✓ 批量处理配置完成")


def example_extract_watermark():
    """提取水印示例"""
    print("\n" + "=" * 60)
    print("示例6: 提取文档水印")
    print("=" * 60)
    
    print("从Word文档提取:")
    print("  wm = WordWatermark()")
    print("  info = wm.extract('document.docx')")
    print("  if info:")
    print("      print(f'用户: {info.username}')")
    
    print("\n从PDF文档提取:")
    print("  wm = PDFWatermark()")
    print("  info = wm.extract('document.pdf')")
    
    print("\n从Excel文档提取:")
    print("  wm = ExcelWatermark()")
    print("  info = wm.extract('document.xlsx')")
    
    print("\n从OFD文档提取:")
    print("  wm = OFDWatermark()")
    print("  info = wm.extract('document.ofd')")
    
    print("✓ 水印提取配置完成")


def example_complete_workflow():
    """完整工作流示例"""
    print("\n" + "=" * 60)
    print("示例7: 完整文档水印工作流")
    print("=" * 60)
    
    # 创建水印信息
    info = WatermarkInfo(
        username="安全管理员",
        employee_id="SEC001",
        department="信息安全部",
        device_id="WORKSTATION-001",
        auto_fill=True,
        custom_data={
            "密级": "机密",
            "有效期": "2026-12-31"
        }
    )
    
    # 使用高风险样式
    style = WatermarkStyle.high_risk_preset()
    
    print("1. 创建水印信息:")
    print(f"   用户: {info.username}")
    print(f"   工号: {info.employee_id}")
    print(f"   校验码: {info.checksum[:8]}")
    
    print("\n2. 选择高风险样式:")
    print(f"   前缀: {style.prefix}")
    print(f"   颜色: {style.hex_color}")
    
    print("\n3. 初始化处理器:")
    word_wm = WordWatermark(default_style=style)
    pdf_wm = PDFWatermark(default_style=style)
    excel_wm = ExcelWatermark(default_style=style)
    ofd_wm = OFDWatermark(default_style=style)
    print("   ✓ Word处理器")
    print("   ✓ PDF处理器")
    print("   ✓ Excel处理器")
    print("   ✓ OFD处理器")
    
    print("\n4. 添加水印:")
    print("   word_wm.embed('report.docx', 'report_wm.docx', info)")
    print("   pdf_wm.embed('contract.pdf', 'contract_wm.pdf', info)")
    print("   excel_wm.embed('data.xlsx', 'data_wm.xlsx', info)")
    print("   ofd_wm.embed('official.ofd', 'official_wm.ofd', info)")
    
    print("\n5. 验证水印:")
    print("   extracted = word_wm.extract('report_wm.docx')")
    print("   if extracted.username == info.username:")
    print("       print('水印验证通过')")
    
    print("\n✓ 完整工作流演示完成")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("VisualWM 文档水印示例")
    print("支持格式: Word(.docx), PDF(.pdf), Excel(.xlsx), OFD(.ofd)")
    print("=" * 60 + "\n")
    
    example_word_watermark()
    example_pdf_watermark()
    example_excel_watermark()
    example_ofd_watermark()
    example_batch_processing()
    example_extract_watermark()
    example_complete_workflow()
    
    print("\n" + "=" * 60)
    print("所有文档水印示例演示完成!")
    print("=" * 60)
    
    print("\n快速使用:")
    print("  from visualwm import WordWatermark, PDFWatermark, ExcelWatermark, OFDWatermark")
    print("  from visualwm import WatermarkInfo, WatermarkStyle")
    print()
    print("  info = WatermarkInfo(username='张三', employee_id='001', auto_fill=True)")
    print("  style = WatermarkStyle.high_risk_preset()  # 可选")
    print()
    print("  # Word")
    print("  WordWatermark().embed('in.docx', 'out.docx', info)")
    print("  # PDF")
    print("  PDFWatermark().embed('in.pdf', 'out.pdf', info)")
    print("  # Excel")
    print("  ExcelWatermark().embed('in.xlsx', 'out.xlsx', info)")
    print("  # OFD")
    print("  OFDWatermark().embed('in.ofd', 'out.ofd', info)")
    print()


if __name__ == "__main__":
    main()
