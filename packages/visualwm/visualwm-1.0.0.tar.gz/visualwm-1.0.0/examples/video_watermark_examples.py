#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VisualWM 示例代码 - 视频水印
"""

from visualwm import VideoWatermark, WatermarkInfo, WatermarkStyle, RiskLevel


def example_basic_video_watermark():
    """基本视频水印示例"""
    print("=" * 60)
    print("示例1: 基本视频水印")
    print("=" * 60)
    
    # 创建水印信息
    info = WatermarkInfo(
        username="张三",
        employee_id="EMP001",
        device_id="DEV-2024-001",
        auto_fill=True
    )
    
    print(f"水印信息: {info}")
    
    # 创建视频水印处理器
    wm = VideoWatermark()
    
    # 定义进度回调
    def progress_callback(current, total):
        percent = (current / total) * 100
        print(f"\r处理进度: {current}/{total} ({percent:.1f}%)", end="")
    
    # 添加水印
    # wm.embed(
    #     "input.mp4",
    #     "output.mp4",
    #     info,
    #     progress_callback=progress_callback
    # )
    
    print("\n✓ 基本视频水印配置完成")


def example_dynamic_timestamp_watermark():
    """动态时间戳水印示例"""
    print("\n" + "=" * 60)
    print("示例2: 动态时间戳水印（每帧更新）")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="李四",
        employee_id="EMP002",
        auto_fill=True
    )
    
    style = WatermarkStyle(
        font_size=18,
        opacity=0.4,
        position="bottom_right",
        margin=20
    )
    
    # wm = VideoWatermark()
    # wm.embed(
    #     "input.mp4",
    #     "output_dynamic.mp4",
    #     info,
    #     style,
    #     dynamic_timestamp=True  # 每帧更新时间戳
    # )
    
    print("动态时间戳功能: 每帧显示实时时间")
    print("✓ 动态时间戳配置完成")


def example_tiled_video_watermark():
    """平铺视频水印示例"""
    print("\n" + "=" * 60)
    print("示例3: 平铺视频水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="王五",
        employee_id="EMP003",
        department="研发部",
        auto_fill=True
    )
    
    # 平铺样式
    style = WatermarkStyle(
        font_size=20,
        color=(150, 150, 150),
        opacity=0.3,
        rotation=-30,
        position="tile",
        line_spacing=100,
        column_spacing=200
    )
    
    print(f"水印样式: 平铺模式")
    print(f"旋转角度: {style.rotation}°")
    print(f"行间距: {style.line_spacing}px")
    print(f"列间距: {style.column_spacing}px")
    
    # wm = VideoWatermark()
    # wm.embed("input.mp4", "output_tiled.mp4", info, style)
    
    print("✓ 平铺水印配置完成")


def example_high_risk_video_watermark():
    """高风险视频水印示例"""
    print("\n" + "=" * 60)
    print("示例4: 高风险（机密）视频水印")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="赵六",
        employee_id="EMP004",
        department="安全部",
        auto_fill=True
    )
    
    # 使用高风险预设
    style = WatermarkStyle.critical_risk_preset()
    
    print(f"风险等级: {style.risk_level}")
    print(f"前缀: {style.prefix}")
    print(f"颜色: {style.hex_color} (红色)")
    print(f"透明度: {style.opacity}")
    
    # wm = VideoWatermark()
    # wm.embed("secret_video.mp4", "output_secret.mp4", info, style)
    
    print("✓ 高风险视频水印配置完成")


def example_get_video_info():
    """获取视频信息示例"""
    print("\n" + "=" * 60)
    print("示例5: 获取视频信息")
    print("=" * 60)
    
    wm = VideoWatermark()
    
    # video_info = wm.get_video_info("input.mp4")
    # print(f"分辨率: {video_info['width']}x{video_info['height']}")
    # print(f"帧率: {video_info['fps']} FPS")
    # print(f"总帧数: {video_info['total_frames']}")
    # print(f"时长: {video_info['duration']:.2f} 秒")
    
    print("视频信息获取功能演示")
    print("✓ 获取视频信息完成")


def example_extract_video_frame():
    """提取视频帧示例"""
    print("\n" + "=" * 60)
    print("示例6: 提取视频帧")
    print("=" * 60)
    
    wm = VideoWatermark()
    
    # 提取第100帧
    # frame = wm.extract_frame("watermarked_video.mp4", frame_number=100)
    # frame.save("extracted_frame.png")
    
    # 从帧中提取水印
    # info = wm.extract("watermarked_video.mp4", frame_number=100, use_ocr=True)
    
    print("可提取任意帧进行分析")
    print("✓ 提取视频帧完成")


def example_batch_video_processing():
    """批量视频处理示例"""
    print("\n" + "=" * 60)
    print("示例7: 批量视频处理")
    print("=" * 60)
    
    info = WatermarkInfo(
        username="批量处理用户",
        employee_id="BATCH001",
        auto_fill=True
    )
    
    def batch_progress(filename, current, total):
        print(f"处理中 ({current}/{total}): {filename}")
    
    # wm = VideoWatermark()
    # processed = wm.batch_embed(
    #     input_dir="./input_videos/",
    #     output_dir="./output_videos/",
    #     info=info,
    #     recursive=True,
    #     progress_callback=batch_progress
    # )
    # print(f"已处理 {len(processed)} 个视频文件")
    
    print("✓ 批量视频处理配置完成")


if __name__ == "__main__":
    print("VisualWM 视频水印示例")
    print("=" * 60)
    
    example_basic_video_watermark()
    example_dynamic_timestamp_watermark()
    example_tiled_video_watermark()
    example_high_risk_video_watermark()
    example_get_video_info()
    example_extract_video_frame()
    example_batch_video_processing()
    
    print("\n" + "=" * 60)
    print("所有视频水印示例演示完成!")
    print("=" * 60)
