#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisualWM 综合示例 - 完整功能演示
"""

from visualwm import (
    WatermarkInfo,
    WatermarkStyle,
    RiskLevel,
    ChecksumGenerator,
    ImageWatermark,
    VideoWatermark,
    TextWatermark,
)
from visualwm.core.device import DeviceInfoCollector
from visualwm.core.checksum import TamperDetector


def demo_device_info():
    """设备信息收集演示"""
    print("=" * 60)
    print("设备信息收集演示")
    print("=" * 60)
    
    collector = DeviceInfoCollector()
    
    print(f"IP地址: {collector.get_ip_address()}")
    print(f"MAC地址: {collector.get_mac_address()}")
    print(f"主机名: {collector.get_hostname()}")
    print(f"时间戳: {collector.get_timestamp()}")
    
    platform_info = collector.get_platform_info()
    print(f"操作系统: {platform_info['system']} {platform_info['release']}")
    print(f"机器类型: {platform_info['machine']}")
    
    print()


def demo_watermark_info():
    """水印信息演示"""
    print("=" * 60)
    print("水印信息演示")
    print("=" * 60)
    
    # 创建完整的水印信息
    info = WatermarkInfo(
        username="张三",
        employee_id="EMP20240001",
        device_id="DEV-LAPTOP-001",
        department="信息安全部",
        auto_fill=True,  # 自动填充IP、MAC、时间戳
        include_checksum=True,  # 包含校验码
        custom_data={
            "项目": "机密项目Alpha",
            "密级": "秘密"
        }
    )
    
    print("水印信息对象:")
    print(f"  用户名: {info.username}")
    print(f"  工号: {info.employee_id}")
    print(f"  设备ID: {info.device_id}")
    print(f"  部门: {info.department}")
    print(f"  IP地址: {info.ip_address}")
    print(f"  MAC地址: {info.mac_address}")
    print(f"  时间戳: {info.timestamp}")
    print(f"  校验码: {info.checksum[:16]}...")
    
    print("\n水印字符串格式:")
    print(f"  单行: {info.to_string()}")
    print(f"  紧凑: {info.to_string(compact=True)}")
    
    print("\n多行格式:")
    for line in info.to_multiline_string().split('\n'):
        print(f"  {line}")
    
    print()


def demo_watermark_styles():
    """水印样式演示"""
    print("=" * 60)
    print("水印样式演示")
    print("=" * 60)
    
    # 各种预设样式
    styles = {
        "默认样式": WatermarkStyle.default(),
        "低风险": WatermarkStyle.low_risk_preset(),
        "中风险": WatermarkStyle.medium_risk_preset(),
        "高风险": WatermarkStyle.high_risk_preset(),
        "极高风险": WatermarkStyle.critical_risk_preset(),
        "角落水印": WatermarkStyle.corner_preset(),
        "居中水印": WatermarkStyle.center_preset(),
    }
    
    for name, style in styles.items():
        print(f"\n{name}:")
        print(f"  字体大小: {style.font_size}")
        print(f"  颜色: {style.hex_color}")
        print(f"  透明度: {style.opacity}")
        print(f"  位置: {style.position}")
        print(f"  前缀: {style.prefix or '无'}")
    
    print()


def demo_checksum():
    """校验码演示"""
    print("=" * 60)
    print("校验码与防篡改演示")
    print("=" * 60)
    
    content = "用户:张三 | 工号:EMP001 | 时间:2024-01-01 12:00:00"
    
    # 生成校验码
    checksum = ChecksumGenerator.generate(content)
    short_checksum = ChecksumGenerator.generate_short(content, length=8)
    
    print(f"原始内容: {content}")
    print(f"完整校验码: {checksum}")
    print(f"短校验码: {short_checksum}")
    
    # 验证校验码
    is_valid = ChecksumGenerator.verify(content, checksum)
    print(f"校验结果: {'✓ 通过' if is_valid else '✗ 失败'}")
    
    # 模拟篡改
    tampered_content = content.replace("张三", "李四")
    is_valid_tampered = ChecksumGenerator.verify(tampered_content, checksum)
    print(f"\n篡改后内容: {tampered_content}")
    print(f"校验结果: {'✓ 通过' if is_valid_tampered else '✗ 失败（检测到篡改）'}")
    
    # 使用篡改检测器
    print("\n使用篡改检测器:")
    detector = TamperDetector()
    result = detector.check(content, tampered_content, short_checksum)
    
    print(f"  是否被篡改: {'是' if result['is_tampered'] else '否'}")
    print(f"  内容已修改: {'是' if result['content_modified'] else '否'}")
    print(f"  校验码有效: {'是' if result['checksum_valid'] else '否'}")
    if result['details']:
        print(f"  详情: {', '.join(result['details'])}")
    
    print()


def demo_complete_workflow():
    """完整工作流演示"""
    print("=" * 60)
    print("完整工作流演示")
    print("=" * 60)
    
    # 1. 创建水印信息
    print("\n步骤1: 创建水印信息")
    info = WatermarkInfo(
        username="安全审计员",
        employee_id="SEC001",
        department="安全合规部",
        auto_fill=True
    )
    print(f"  水印信息已创建: {info.username} ({info.employee_id})")
    
    # 2. 选择样式
    print("\n步骤2: 选择水印样式")
    style = WatermarkStyle.high_risk_preset()
    print(f"  使用高风险预设样式")
    print(f"  前缀: {style.prefix}")
    print(f"  颜色: {style.hex_color}")
    
    # 3. 初始化处理器
    print("\n步骤3: 初始化水印处理器")
    image_wm = ImageWatermark(default_style=style)
    video_wm = VideoWatermark(default_style=style)
    text_wm = TextWatermark()
    print("  ✓ 图片水印处理器")
    print("  ✓ 视频水印处理器")
    print("  ✓ 文本水印处理器")
    
    # 4. 添加水印
    print("\n步骤4: 添加水印")
    print("  图片: image_wm.embed('input.jpg', 'output.jpg', info)")
    print("  视频: video_wm.embed('input.mp4', 'output.mp4', info)")
    print("  文本: text_wm.embed('文本内容', info)")
    
    # 5. 提取和验证
    print("\n步骤5: 提取和验证水印")
    print("  图片: extracted = image_wm.extract('output.jpg', use_ocr=True)")
    print("  视频: extracted = video_wm.extract('output.mp4', use_ocr=True)")
    print("  文本: extracted = text_wm.extract(watermarked_text)")
    
    # 6. 演示文本水印完整流程
    print("\n步骤6: 文本水印完整流程演示")
    sample_text = "这是一份机密文档的内容示例。"
    watermarked = text_wm.embed(sample_text, info)
    extracted = text_wm.extract(watermarked)
    
    if extracted:
        print(f"  提取的用户: {extracted.username}")
        print(f"  提取的工号: {extracted.employee_id}")
        print("  ✓ 水印提取成功")
    
    print()


def demo_risk_levels():
    """风险等级演示"""
    print("=" * 60)
    print("风险等级水印演示")
    print("=" * 60)
    
    risk_descriptions = {
        RiskLevel.LOW: "普通文档 - 浅灰色半透明水印",
        RiskLevel.MEDIUM: "内部文档 - 带【内部】前缀",
        RiskLevel.HIGH: "机密文档 - 红色加粗，带【机密】前缀",
        RiskLevel.CRITICAL: "绝密文档 - 深红色加粗带阴影，【绝密】前缀",
    }
    
    for level, desc in risk_descriptions.items():
        style = WatermarkStyle.get_preset_by_risk_level(level)
        print(f"\n{level.value.upper()}: {desc}")
        print(f"  颜色: {style.hex_color}")
        print(f"  透明度: {style.opacity}")
        print(f"  字体大小: {style.font_size}")
        print(f"  加粗: {'是' if style.bold else '否'}")
        print(f"  前缀: {style.prefix or '无'}")
    
    print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("VisualWM - 泄密警示明水印SDK 综合演示")
    print("=" * 60 + "\n")
    
    demo_device_info()
    demo_watermark_info()
    demo_watermark_styles()
    demo_checksum()
    demo_risk_levels()
    demo_complete_workflow()
    
    print("=" * 60)
    print("演示完成!")
    print("=" * 60)
    print("\n使用方法:")
    print("  pip install -e .")
    print("  python -c 'from visualwm import ImageWatermark; print(\"OK\")'")
    print("\n命令行工具:")
    print("  visualwm embed input.jpg output.jpg -u 张三 -e EMP001")
    print("  visualwm extract output.jpg --ocr")
    print("  visualwm batch ./input_dir ./output_dir -u 张三 -t image")
    print()


if __name__ == "__main__":
    main()
