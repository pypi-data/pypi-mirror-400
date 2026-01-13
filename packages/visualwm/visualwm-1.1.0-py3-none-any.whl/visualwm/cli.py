"""
命令行接口
"""

import argparse
import sys
from pathlib import Path

from visualwm import (
    WatermarkInfo,
    WatermarkStyle,
    RiskLevel,
    ImageWatermark,
    VideoWatermark,
    TextWatermark,
)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        prog="visualwm",
        description="泄密警示明水印SDK - 支持图片、视频、文本多模态水印嵌入与提取"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 添加水印命令
    embed_parser = subparsers.add_parser("embed", help="添加水印")
    embed_parser.add_argument("input", help="输入文件路径")
    embed_parser.add_argument("output", help="输出文件路径")
    embed_parser.add_argument("-u", "--username", required=True, help="用户姓名")
    embed_parser.add_argument("-e", "--employee-id", default="", help="工号")
    embed_parser.add_argument("-d", "--device-id", default="", help="设备编号")
    embed_parser.add_argument("-t", "--type", choices=["image", "video", "text"], help="文件类型（自动检测）")
    embed_parser.add_argument("--risk-level", choices=["low", "medium", "high", "critical"], default="low", help="风险等级")
    embed_parser.add_argument("--position", choices=["tile", "center", "top_left", "top_right", "bottom_left", "bottom_right"], default="tile", help="水印位置")
    embed_parser.add_argument("--opacity", type=float, default=0.5, help="透明度")
    embed_parser.add_argument("--font-size", type=int, default=24, help="字体大小")
    
    # 提取水印命令
    extract_parser = subparsers.add_parser("extract", help="提取水印")
    extract_parser.add_argument("input", help="输入文件路径")
    extract_parser.add_argument("-t", "--type", choices=["image", "video", "text"], help="文件类型")
    extract_parser.add_argument("--ocr", action="store_true", help="使用OCR提取")
    
    # 批量处理命令
    batch_parser = subparsers.add_parser("batch", help="批量添加水印")
    batch_parser.add_argument("input_dir", help="输入目录")
    batch_parser.add_argument("output_dir", help="输出目录")
    batch_parser.add_argument("-u", "--username", required=True, help="用户姓名")
    batch_parser.add_argument("-e", "--employee-id", default="", help="工号")
    batch_parser.add_argument("-t", "--type", choices=["image", "video", "text"], required=True, help="文件类型")
    batch_parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子目录")
    
    # 版本命令
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    if args.command == "embed":
        embed_watermark(args)
    elif args.command == "extract":
        extract_watermark(args)
    elif args.command == "batch":
        batch_process(args)
    else:
        parser.print_help()


def detect_file_type(file_path: str) -> str:
    """检测文件类型"""
    suffix = Path(file_path).suffix.lower()
    
    image_formats = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
    video_formats = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    text_formats = {'.txt', '.md', '.rst', '.log', '.html', '.htm'}
    
    if suffix in image_formats:
        return "image"
    elif suffix in video_formats:
        return "video"
    elif suffix in text_formats:
        return "text"
    else:
        raise ValueError(f"无法识别的文件类型: {suffix}")


def embed_watermark(args):
    """添加水印"""
    file_type = args.type or detect_file_type(args.input)
    
    # 创建水印信息
    info = WatermarkInfo(
        username=args.username,
        employee_id=args.employee_id,
        device_id=args.device_id,
        auto_fill=True
    )
    
    # 创建水印样式
    risk_level = RiskLevel(args.risk_level)
    
    if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        style = WatermarkStyle.get_preset_by_risk_level(risk_level)
    else:
        style = WatermarkStyle(
            font_size=args.font_size,
            opacity=args.opacity,
            position=args.position,
            risk_level=risk_level
        )
    
    # 添加水印
    if file_type == "image":
        wm = ImageWatermark()
        output = wm.embed(args.input, args.output, info, style)
    elif file_type == "video":
        wm = VideoWatermark()
        output = wm.embed(args.input, args.output, info, style, 
                         progress_callback=lambda c, t: print(f"\r处理进度: {c}/{t}", end=""))
        print()
    elif file_type == "text":
        wm = TextWatermark()
        output = wm.embed_to_file(args.input, args.output, info)
    
    print(f"水印添加成功: {output}")


def extract_watermark(args):
    """提取水印"""
    file_type = args.type or detect_file_type(args.input)
    
    if file_type == "image":
        wm = ImageWatermark()
        info = wm.extract(args.input, use_ocr=args.ocr)
    elif file_type == "video":
        wm = VideoWatermark()
        info = wm.extract(args.input, use_ocr=args.ocr)
    elif file_type == "text":
        wm = TextWatermark()
        info = wm.extract_from_file(args.input)
    
    if info:
        print("提取的水印信息:")
        print(info.to_string(separator="\n"))
    else:
        print("未找到水印信息")


def batch_process(args):
    """批量处理"""
    info = WatermarkInfo(
        username=args.username,
        employee_id=args.employee_id,
        auto_fill=True
    )
    
    if args.type == "image":
        wm = ImageWatermark()
        processed = wm.batch_embed(args.input_dir, args.output_dir, info, recursive=args.recursive)
    elif args.type == "video":
        wm = VideoWatermark()
        processed = wm.batch_embed(args.input_dir, args.output_dir, info, recursive=args.recursive)
    elif args.type == "text":
        wm = TextWatermark()
        processed = wm.batch_embed(args.input_dir, args.output_dir, info, recursive=args.recursive)
    
    print(f"批量处理完成，共处理 {len(processed)} 个文件")


if __name__ == "__main__":
    main()
