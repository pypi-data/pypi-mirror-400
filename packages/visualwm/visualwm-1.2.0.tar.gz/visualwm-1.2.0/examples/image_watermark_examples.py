#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisualWM 示例代码 - 图片水印
"""

from visualwm import ImageWatermark, WatermarkInfo, WatermarkStyle, RiskLevel


def example_basic_image_watermark():
    """基本图片水印示例"""
    print("=" * 60)
    print("示例1: 基本图片水印")
    print("=" * 60)
    
    # 创建水印信息（自动获取IP、MAC、时间戳）
    info = WatermarkInfo(
        username="张三",
        employee_id="EMP001",
        device_id="DEV-2024-001",
        department="研发部",
        auto_fill=True
    )
    
    print(f"水印信息: {info}")
    print(f"校验码: {info.checksum[:8]}")
    
    # 创建水印处理器
    wm = ImageWatermark()
    
    # 使用默认样式添加水印
    # wm.embed("input.jpg", "output.jpg", info)
    
    print("✓ 基本水印配置完成")


def example_custom_style_watermark():
    """自定义样式水印示例"""
    print("\n" + "=" * 60)
    print("示例2: 自定义样式水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="李四",
        employee_id="EMP002",
        auto_fill=True
    )
    
    # 自定义样式
    style = WatermarkStyle(
        font_size=28,
        color=(100, 100, 100),
        opacity=0.4,
        rotation=-45,
        position="tile",
        line_spacing=120,
        column_spacing=250,
    )
    
    print(f"字体大小: {style.font_size}")
    print(f"颜色: {style.hex_color}")
    print(f"透明度: {style.opacity}")
    print(f"旋转角度: {style.rotation}°")
    
    # wm = ImageWatermark()
    # wm.embed("input.jpg", "output_custom.jpg", info, style)
    
    print("✓ 自定义样式配置完成")


def example_high_risk_watermark():
    """高风险文档水印示例"""
    print("\n" + "=" * 60)
    print("示例3: 高风险（机密）文档水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="王五",
        employee_id="EMP003",
        department="安全部",
        auto_fill=True
    )
    
    # 使用高风险预设样式
    style = WatermarkStyle.high_risk_preset()
    
    print(f"前缀: {style.prefix}")
    print(f"颜色: {style.hex_color} (红色)")
    print(f"透明度: {style.opacity}")
    print(f"加粗: {style.bold}")
    print(f"边框: {style.border}")
    
    # wm = ImageWatermark()
    # wm.embed("secret_doc.png", "output_secret.png", info, style)
    
    print("✓ 高风险水印配置完成")


def example_corner_watermark():
    """角落水印示例"""
    print("\n" + "=" * 60)
    print("示例4: 角落水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="赵六",
        employee_id="EMP004",
        auto_fill=True
    )
    
    # 右下角水印
    style = WatermarkStyle.corner_preset("bottom_right")
    
    print(f"位置: {style.position}")
    print(f"边距: {style.margin}px")
    
    # wm = ImageWatermark()
    # wm.embed("input.jpg", "output_corner.jpg", info, style)
    
    print("✓ 角落水印配置完成")


def example_multiline_watermark():
    """多行水印示例"""
    print("\n" + "=" * 60)
    print("示例5: 多行水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="孙七",
        employee_id="EMP005",
        device_id="LAPTOP-001",
        auto_fill=True,
        custom_data={
            "项目": "机密项目A",
            "版本": "v1.0"
        }
    )
    
    print("多行水印内容:")
    print(info.to_multiline_string())
    
    # wm = ImageWatermark()
    # wm.add_multiline_watermark("input.jpg", "output_multiline.jpg", info)
    
    print("✓ 多行水印配置完成")


def example_memory_processing():
    """内存处理示例"""
    print("\n" + "=" * 60)
    print("示例6: 内存中处理图片")
    print("=" * 60)
    
    info = WatermarkInfo(username="测试用户", auto_fill=True)
    style = WatermarkStyle.default()
    
    wm = ImageWatermark()
    
    # 读取图片字节
    # with open("input.jpg", "rb") as f:
    #     image_bytes = f.read()
    
    # 在内存中处理
    # watermarked_bytes = wm.embed_to_bytes(image_bytes, info, style, format="PNG")
    
    # 直接使用或保存
    # with open("output_memory.png", "wb") as f:
    #     f.write(watermarked_bytes)
    
    print("✓ 内存处理演示完成")


def example_batch_processing():
    """批量处理示例"""
    print("\n" + "=" * 60)
    print("示例7: 批量处理")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="批量处理用户",
        employee_id="BATCH001",
        auto_fill=True
    )
    
    style = WatermarkStyle.medium_risk_preset()
    
    # wm = ImageWatermark()
    # processed = wm.batch_embed(
    #     input_dir="./input_images/",
    #     output_dir="./output_images/",
    #     info=info,
    #     style=style,
    #     recursive=True
    # )
    # print(f"已处理 {len(processed)} 个文件")
    
    print("✓ 批量处理演示完成")


def example_extract_watermark():
    """提取水印示例"""
    print("\n" + "=" * 60)
    print("示例8: 提取水印（需要OCR）")
    print("=" * 60)
    
    # wm = ImageWatermark()
    
    # 启用OCR提取
    # info = wm.extract("watermarked_image.png", use_ocr=True)
    # if info:
    #     print("提取的水印信息:")
    #     print(info.to_string(separator="\n"))
    # else:
    #     print("未能提取水印信息")
    
    print("注意: OCR提取需要安装 pytesseract 和 Tesseract OCR 引擎")
    print("✓ 提取水印演示完成")


if __name__ == "__main__":
    print("VisualWM 图片水印示例")
    print("=" * 60)
    
    example_basic_image_watermark()
    example_custom_style_watermark()
    example_high_risk_watermark()
    example_corner_watermark()
    example_multiline_watermark()
    example_memory_processing()
    example_batch_processing()
    example_extract_watermark()
    
    print("\n" + "=" * 60)
    print("所有示例演示完成!")
    print("=" * 60)
