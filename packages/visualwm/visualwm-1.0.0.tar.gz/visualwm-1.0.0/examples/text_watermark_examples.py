#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisualWM 示例代码 - 文本水印
"""

from visualwm import TextWatermark, WatermarkInfo, RiskLevel
from visualwm.text.watermark import (
    TextWatermarkStyle,
    TextWatermarkFormat,
    HTMLWatermark,
    MarkdownWatermark
)


def example_basic_text_watermark():
    """基本文本水印示例"""
    print("=" * 60)
    print("示例1: 基本文本水印（头尾模式）")
    print("=" * 60)
    
    # 创建水印信息
    info = WatermarkInfo(
        username="张三",
        employee_id="EMP001",
        device_id="DEV-2024-001",
        department="研发部",
        auto_fill=True
    )
    
    # 原始文本
    content = """这是一份重要的技术文档。

本文档包含公司核心技术资料，请妥善保管。

第一章：概述
本系统采用微服务架构设计...

第二章：技术细节
系统使用Python语言开发..."""
    
    # 创建文本水印处理器
    wm = TextWatermark()
    
    # 添加水印
    watermarked = wm.embed(content, info)
    
    print("添加水印后的文本:")
    print("-" * 40)
    print(watermarked[:500] + "..." if len(watermarked) > 500 else watermarked)
    print("-" * 40)
    print("✓ 基本文本水印完成")


def example_header_watermark():
    """头部水印示例"""
    print("\n" + "=" * 60)
    print("示例2: 头部水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="李四",
        employee_id="EMP002",
        auto_fill=True
    )
    
    style = TextWatermarkStyle(
        format=TextWatermarkFormat.HEADER,
        include_border=True,
        border_char="*"
    )
    
    content = "这是文档内容..."
    
    wm = TextWatermark()
    watermarked = wm.embed(content, info, style)
    
    print("头部水印:")
    print(watermarked)
    print("✓ 头部水印完成")


def example_footer_watermark():
    """尾部水印示例"""
    print("\n" + "=" * 60)
    print("示例3: 尾部水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="王五",
        employee_id="EMP003",
        auto_fill=True
    )
    
    style = TextWatermarkStyle(
        format=TextWatermarkFormat.FOOTER
    )
    
    content = "这是文档内容..."
    
    wm = TextWatermark()
    watermarked = wm.embed(content, info, style)
    
    print("尾部水印:")
    print(watermarked)
    print("✓ 尾部水印完成")


def example_inline_watermark():
    """行内水印示例"""
    print("\n" + "=" * 60)
    print("示例4: 行内水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="赵六",
        employee_id="EMP004",
        auto_fill=True
    )
    
    style = TextWatermarkStyle(
        format=TextWatermarkFormat.INLINE,
        repeat_interval=3,  # 每3行添加一次水印
        bracket_left="《",
        bracket_right="》"
    )
    
    content = """第一行内容
第二行内容
第三行内容
第四行内容
第五行内容
第六行内容
第七行内容
第八行内容
第九行内容"""
    
    wm = TextWatermark()
    watermarked = wm.embed(content, info, style)
    
    print("行内水印（每3行一次）:")
    print(watermarked)
    print("✓ 行内水印完成")


def example_margin_watermark():
    """边距水印示例"""
    print("\n" + "=" * 60)
    print("示例5: 边距水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="孙七",
        employee_id="EMP005",
        auto_fill=True
    )
    
    style = TextWatermarkStyle(
        format=TextWatermarkFormat.MARGIN,
        line_prefix="| "
    )
    
    content = """这是第一行
这是第二行
这是第三行"""
    
    wm = TextWatermark()
    watermarked = wm.embed(content, info, style)
    
    print("边距水印:")
    print(watermarked)
    print("✓ 边距水印完成")


def example_high_risk_text_watermark():
    """高风险文本水印示例"""
    print("\n" + "=" * 60)
    print("示例6: 高风险文本水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="周八",
        employee_id="EMP006",
        department="安全部",
        auto_fill=True
    )
    
    # 使用高风险预设
    style = TextWatermarkStyle.high_risk_preset()
    
    content = "这是一份机密文档..."
    
    wm = TextWatermark()
    watermarked = wm.embed(content, info, style)
    
    print("高风险文本水印:")
    print(watermarked)
    print("✓ 高风险水印完成")


def example_html_watermark():
    """HTML水印示例"""
    print("\n" + "=" * 60)
    print("示例7: HTML水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="吴九",
        employee_id="EMP007",
        auto_fill=True
    )
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>测试文档</title>
</head>
<body>
    <h1>标题</h1>
    <p>这是HTML文档内容</p>
</body>
</html>"""
    
    wm = HTMLWatermark()
    watermarked = wm.embed(html_content, info)
    
    print("HTML水印（固定定位覆盖层）:")
    print(watermarked[:600] + "..." if len(watermarked) > 600 else watermarked)
    print("✓ HTML水印完成")


def example_markdown_watermark():
    """Markdown水印示例"""
    print("\n" + "=" * 60)
    print("示例8: Markdown水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="郑十",
        employee_id="EMP008",
        auto_fill=True
    )
    
    md_content = """# 项目文档

## 概述
这是项目概述部分。

## 功能列表
- 功能1
- 功能2
- 功能3"""
    
    wm = MarkdownWatermark()
    watermarked = wm.embed(md_content, info)
    
    print("Markdown水印:")
    print(watermarked)
    print("✓ Markdown水印完成")


def example_extract_watermark():
    """提取水印示例"""
    print("\n" + "=" * 60)
    print("示例9: 提取水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="测试用户",
        employee_id="TEST001",
        auto_fill=True
    )
    
    content = "这是测试文本内容"
    
    wm = TextWatermark()
    
    # 添加水印
    watermarked = wm.embed(content, info)
    
    # 提取水印
    extracted = wm.extract(watermarked)
    
    if extracted:
        print("提取的水印信息:")
        print(f"  用户名: {extracted.username}")
        print(f"  工号: {extracted.employee_id}")
        print(f"  时间戳: {extracted.timestamp}")
    else:
        print("未能提取水印")
    
    print("✓ 提取水印完成")


def example_verify_watermark():
    """验证水印示例"""
    print("\n" + "=" * 60)
    print("示例10: 验证水印完整性")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="验证测试",
        employee_id="VERIFY001",
        auto_fill=True
    )
    
    content = "这是需要验证的文本"
    
    wm = TextWatermark()
    watermarked = wm.embed(content, info)
    
    # 验证水印
    result = wm.verify_watermark(watermarked, info)
    
    print("验证结果:")
    print(f"  有效性: {'✓ 有效' if result['is_valid'] else '✗ 无效'}")
    print(f"  找到水印: {'✓ 是' if result['watermark_found'] else '✗ 否'}")
    print(f"  校验码有效: {'✓ 是' if result['checksum_valid'] else '✗ 否'}")
    print(f"  信息匹配: {'✓ 是' if result['info_match'] else '✗ 否'}")
    
    if result['details']:
        print(f"  详情: {', '.join(result['details'])}")
    
    print("✓ 验证水印完成")


def example_file_watermark():
    """文件水印示例"""
    print("\n" + "=" * 60)
    print("示例11: 文件水印操作")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="文件测试",
        employee_id="FILE001",
        auto_fill=True
    )
    
    wm = TextWatermark()
    
    # 添加水印到文件
    # wm.embed_to_file("input.txt", "output.txt", info)
    
    # 从文件提取水印
    # extracted = wm.extract_from_file("output.txt")
    
    print("文件操作方法:")
    print("  - embed_to_file(input, output, info, style)")
    print("  - extract_from_file(file_path)")
    print("  - batch_embed(input_dir, output_dir, info)")
    print("✓ 文件水印演示完成")


if __name__ == "__main__":
    print("VisualWM 文本水印示例")
    print("=" * 60)
    
    example_basic_text_watermark()
    example_header_watermark()
    example_footer_watermark()
    example_inline_watermark()
    example_margin_watermark()
    example_high_risk_text_watermark()
    example_html_watermark()
    example_markdown_watermark()
    example_extract_watermark()
    example_verify_watermark()
    example_file_watermark()
    
    print("\n" + "=" * 60)
    print("所有文本水印示例演示完成!")
    print("=" * 60)
