"""
视频水印处理器 - 支持视频添加明水印和提取

支持多核并行处理加速，保留原始音频
"""

import os
import shutil
import subprocess
import tempfile
import multiprocessing as mp
from multiprocessing import shared_memory
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, Union, List, Callable, Tuple
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import warnings

try:
    # imageio-ffmpeg provides prebuilt ffmpeg/ffprobe binaries via pip
    import imageio_ffmpeg as _imageio_ffmpeg
except Exception:
    _imageio_ffmpeg = None

from visualwm.core.info import WatermarkInfo
from visualwm.core.style import WatermarkStyle
from visualwm.image.watermark import ImageWatermark


# 全局变量用于进程间共享水印叠加层
_global_watermark_overlay = None
_global_style_opacity = None
_global_frame_shape = None


def _init_worker(watermark_overlay: np.ndarray, opacity: float):
    """初始化worker进程的全局变量"""
    global _global_watermark_overlay, _global_style_opacity, _global_frame_shape
    _global_watermark_overlay = watermark_overlay
    _global_style_opacity = opacity
    _global_frame_shape = watermark_overlay.shape[:2]


def _process_single_frame(frame: np.ndarray) -> np.ndarray:
    """处理单帧（在子进程中运行）"""
    global _global_watermark_overlay, _global_style_opacity
    
    # 转换帧为RGBA
    frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    
    # 获取水印的alpha通道
    alpha = _global_watermark_overlay[:, :, 3:4] / 255.0
    
    # 混合
    blended = frame_rgba.astype(np.float32)
    watermark_rgb = _global_watermark_overlay[:, :, :3].astype(np.float32)
    
    # 只在有水印的地方混合
    mask = alpha > 0
    blended[:, :, :3] = np.where(
        np.broadcast_to(mask, blended[:, :, :3].shape),
        frame_rgba[:, :, :3] * (1 - alpha) + watermark_rgb * alpha,
        frame_rgba[:, :, :3]
    )
    
    # 转回BGR
    result = cv2.cvtColor(blended.astype(np.uint8), cv2.COLOR_RGBA2BGR)
    return result


def _process_frame_batch(args: Tuple[int, List[np.ndarray]]) -> Tuple[int, List[np.ndarray]]:
    """
    处理一批视频帧（在子进程中运行）
    
    Args:
        args: (batch_index, frames) 批次索引和帧列表
        
    Returns:
        (batch_index, processed_frames) 批次索引和处理后的帧列表
    """
    batch_idx, frames = args
    processed = [_process_single_frame(frame) for frame in frames]
    return batch_idx, processed


class VideoWatermark:
    """
    视频水印处理器
    
    支持在视频上添加明水印，并从视频中提取水印信息。
    
    Features:
        - 支持多种视频格式（MP4、AVI、MOV等）
        - 逐帧添加水印
        - 动态水印（时间戳实时更新）
        - 批量处理
        - 进度回调
    """
    
    # 支持的视频格式
    SUPPORTED_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
    
    # 常用视频编解码器
    CODECS = {
        '.mp4': 'mp4v',
        '.avi': 'XVID',
        '.mov': 'mp4v',
        '.mkv': 'XVID',
        '.wmv': 'WMV2',
        '.webm': 'VP80',
    }
    
    def __init__(self, default_style: Optional[WatermarkStyle] = None):
        """
        初始化视频水印处理器
        
        Args:
            default_style: 默认水印样式
        """
        self.default_style = default_style or WatermarkStyle.default()
        self._image_watermark = ImageWatermark(default_style)
        # 默认使用CPU核心数的一半（避免过度并行）
        self._num_workers = max(1, mp.cpu_count() // 2)
        # ffmpeg 可执行路径（优先使用 imageio-ffmpeg 提供的二进制）
        self._ffmpeg_exe = None
        # 检测ffmpeg是否可用
        self._ffmpeg_available = self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """检查ffmpeg是否可用"""
        # Try imageio-ffmpeg first (bundled via pip)
        if _imageio_ffmpeg is not None:
            try:
                ffmpeg_exe = _imageio_ffmpeg.get_ffmpeg_exe()
                if ffmpeg_exe and Path(ffmpeg_exe).exists():
                    self._ffmpeg_exe = ffmpeg_exe
                    return True
            except Exception:
                pass

        # Fallback to system ffmpeg
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self._ffmpeg_exe = 'ffmpeg'
                return True
            return False
        except FileNotFoundError:
            return False
    
    def _has_audio(self, video_path: Union[str, Path]) -> bool:
        """检查视频是否包含音频轨道"""
        if not self._ffmpeg_available:
            return False

        # Try to locate ffprobe provided by imageio-ffmpeg
        ffprobe_exe = None
        if _imageio_ffmpeg is not None:
            try:
                ffprobe_exe = _imageio_ffmpeg.get_ffprobe_exe()
            except Exception:
                ffprobe_exe = None

        probe_cmd = [ffprobe_exe or 'ffprobe', '-v', 'error', '-select_streams', 'a',
                     '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', str(video_path)]
        try:
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            return 'audio' in result.stdout
        except Exception:
            return False
    
    def _extract_audio(self, video_path: Union[str, Path], audio_path: Union[str, Path]) -> bool:
        """从视频中提取音频"""
        if not self._ffmpeg_available:
            return False
        ffmpeg_cmd = getattr(self, '_ffmpeg_exe', 'ffmpeg')
        try:
            result = subprocess.run(
                [ffmpeg_cmd, '-y', '-i', str(video_path), '-vn', '-acodec', 'copy', str(audio_path)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and Path(audio_path).exists()
        except Exception:
            return False
    
    def _merge_audio_video(
        self, 
        video_path: Union[str, Path], 
        audio_path: Union[str, Path], 
        output_path: Union[str, Path]
    ) -> bool:
        """合并音频和视频"""
        if not self._ffmpeg_available:
            return False
        ffmpeg_cmd = getattr(self, '_ffmpeg_exe', 'ffmpeg')
        try:
            result = subprocess.run(
                [ffmpeg_cmd, '-y', '-i', str(video_path), '-i', str(audio_path),
                 '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental',
                 str(output_path)],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def set_workers(self, num_workers: int):
        """
        设置并行处理的worker数量
        
        Args:
            num_workers: worker数量，默认为CPU核心数的一半
        """
        self._num_workers = max(1, num_workers)
    
    def embed(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        info: WatermarkInfo,
        style: Optional[WatermarkStyle] = None,
        dynamic_timestamp: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        parallel: bool = True,
        num_workers: Optional[int] = None,
        batch_size: int = 50,
        mode: str = "thread",
    ) -> str:
        """
        在视频中嵌入水印
        
        Args:
            input_path: 输入视频路径
            output_path: 输出视频路径
            info: 水印信息
            style: 水印样式
            dynamic_timestamp: 是否使用动态时间戳（每帧更新）
            progress_callback: 进度回调函数 (current_frame, total_frames)
            parallel: 是否启用多核并行处理（默认True）
            num_workers: 并行worker数量（默认为CPU核心数的一半）
            batch_size: 每批处理的帧数（仅用于process模式，默认50帧）
            mode: 并行模式 "thread"（多线程，默认，推荐）或 "process"（多进程）
            
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
            raise ValueError(f"不支持的视频格式: {input_path.suffix}")
        
        # 动态时间戳模式不支持并行（因为每帧时间戳不同）
        if dynamic_timestamp:
            parallel = False
        
        # 检查是否有音频需要保留
        has_audio = self._has_audio(input_path)
        if has_audio and not self._ffmpeg_available:
            warnings.warn("ffmpeg未安装，视频音频轨道将不会被保留，仅处理画面。", RuntimeWarning)
            has_audio = False
        
        # 如果有音频，先提取
        audio_temp = None
        if has_audio:
            audio_temp = tempfile.NamedTemporaryFile(suffix='.aac', delete=False)
            audio_temp.close()
            if not self._extract_audio(input_path, audio_temp.name):
                has_audio = False
                os.unlink(audio_temp.name)
                audio_temp = None
        
        # 处理视频（不带音频）
        if has_audio:
            # 先输出到临时文件
            video_temp = tempfile.NamedTemporaryFile(suffix=output_path.suffix, delete=False)
            video_temp.close()
            temp_output = Path(video_temp.name)
        else:
            temp_output = output_path
        
        try:
            if parallel:
                if mode == "thread":
                    self._embed_parallel_thread(
                        input_path, temp_output, info, style,
                        progress_callback, num_workers
                    )
                else:
                    self._embed_parallel(
                        input_path, temp_output, info, style,
                        progress_callback, num_workers, batch_size
                    )
            else:
                self._embed_sequential(
                    input_path, temp_output, info, style,
                    dynamic_timestamp, progress_callback
                )
            
            # 如果有音频，合并音频和视频
            if has_audio and audio_temp:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if self._merge_audio_video(temp_output, audio_temp.name, output_path):
                    # 合并成功，删除临时文件
                    os.unlink(temp_output)
                else:
                    # 合并失败，使用无音频版本
                    shutil.move(str(temp_output), str(output_path))
        finally:
            # 清理音频临时文件
            if audio_temp and os.path.exists(audio_temp.name):
                os.unlink(audio_temp.name)
        
        return str(output_path)
    
    def _embed_parallel_thread(
        self,
        input_path: Path,
        output_path: Path,
        info: WatermarkInfo,
        style: WatermarkStyle,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        num_workers: Optional[int] = None,
    ) -> str:
        """
        多线程并行处理视频水印（流式处理，内存友好）
        
        使用线程池进行并行处理，避免进程间数据拷贝开销
        """
        num_workers = num_workers or self._num_workers
        
        # 打开视频
        cap = cv2.VideoCapture(str(input_path))
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {input_path}")
        
        # 获取视频属性
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 创建输出目录
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 获取编解码器
        codec = self.CODECS.get(output_path.suffix.lower(), 'mp4v')
        fourcc = cv2.VideoWriter_fourcc(*codec)
        
        # 预生成水印叠加层
        watermark_overlay = self._create_watermark_overlay(width, height, info, style)
        
        # 预计算alpha通道
        alpha = watermark_overlay[:, :, 3:4].astype(np.float32) / 255.0
        watermark_rgb = watermark_overlay[:, :, :3].astype(np.float32)
        mask = alpha > 0
        
        def process_frame(frame):
            """处理单帧"""
            frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            blended = frame_rgba.astype(np.float32)
            blended[:, :, :3] = np.where(
                np.broadcast_to(mask, blended[:, :, :3].shape),
                frame_rgba[:, :, :3] * (1 - alpha) + watermark_rgb * alpha,
                frame_rgba[:, :, :3]
            )
            return cv2.cvtColor(blended.astype(np.uint8), cv2.COLOR_RGBA2BGR)
        
        # 创建视频写入器
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        try:
            frame_count = 0
            pending_results = {}
            next_write_idx = 0
            
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = {}
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    
                    # 提交帧处理任务
                    future = executor.submit(process_frame, frame.copy())
                    futures[future] = frame_count
                    frame_count += 1
                    
                    # 检查完成的任务并按顺序写入
                    done_futures = [f for f in futures if f.done()]
                    for future in done_futures:
                        idx = futures.pop(future)
                        pending_results[idx] = future.result()
                    
                    # 按顺序写入已完成的帧
                    while next_write_idx in pending_results:
                        out.write(pending_results.pop(next_write_idx))
                        next_write_idx += 1
                        if progress_callback:
                            progress_callback(next_write_idx, total_frames)
                
                # 等待剩余任务完成
                for future in as_completed(futures):
                    idx = futures[future]
                    pending_results[idx] = future.result()
                
                # 写入剩余帧
                while next_write_idx in pending_results:
                    out.write(pending_results.pop(next_write_idx))
                    next_write_idx += 1
                    if progress_callback:
                        progress_callback(next_write_idx, total_frames)
        
        finally:
            cap.release()
            out.release()
        
        return str(output_path)
    
    def _embed_parallel(
        self,
        input_path: Path,
        output_path: Path,
        info: WatermarkInfo,
        style: WatermarkStyle,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        num_workers: Optional[int] = None,
        batch_size: int = 30,
    ) -> str:
        """
        多核并行处理视频水印
        
        使用多进程并行处理视频帧，显著提升处理速度
        """
        num_workers = num_workers or self._num_workers
        
        # 打开视频
        cap = cv2.VideoCapture(str(input_path))
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {input_path}")
        
        # 获取视频属性
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 创建输出目录
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 获取编解码器
        codec = self.CODECS.get(output_path.suffix.lower(), 'mp4v')
        fourcc = cv2.VideoWriter_fourcc(*codec)
        
        # 预生成水印叠加层
        watermark_overlay = self._create_watermark_overlay(width, height, info, style)
        
        # 读取所有帧
        all_frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            all_frames.append(frame)
        cap.release()
        
        actual_total = len(all_frames)
        
        # 将帧分批
        batches = []
        for i in range(0, actual_total, batch_size):
            batch_frames = all_frames[i:i + batch_size]
            batches.append((len(batches), batch_frames))
        
        # 创建视频写入器
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        try:
            # 多进程并行处理
            processed_batches = {}
            completed = 0
            
            with ProcessPoolExecutor(
                max_workers=num_workers,
                initializer=_init_worker,
                initargs=(watermark_overlay, style.opacity)
            ) as executor:
                # 提交所有批次
                futures = {
                    executor.submit(_process_frame_batch, batch): batch[0]
                    for batch in batches
                }
                
                # 收集结果
                for future in as_completed(futures):
                    batch_idx, processed_frames = future.result()
                    processed_batches[batch_idx] = processed_frames
                    completed += len(processed_frames)
                    
                    if progress_callback:
                        progress_callback(completed, actual_total)
            
            # 按顺序写入帧
            for batch_idx in range(len(batches)):
                for frame in processed_batches[batch_idx]:
                    out.write(frame)
        
        finally:
            out.release()
        
        return str(output_path)
    
    def _embed_sequential(
        self,
        input_path: Path,
        output_path: Path,
        info: WatermarkInfo,
        style: WatermarkStyle,
        dynamic_timestamp: bool = False,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> str:
        """
        顺序处理视频水印（原始方法）
        """
        
        # 打开视频
        cap = cv2.VideoCapture(str(input_path))
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {input_path}")
        
        # 获取视频属性
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # 创建输出目录
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 获取编解码器
        codec = self.CODECS.get(output_path.suffix.lower(), 'mp4v')
        fourcc = cv2.VideoWriter_fourcc(*codec)
        
        # 创建视频写入器
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
        
        try:
            # 预生成水印层（如果不是动态的）
            if not dynamic_timestamp:
                watermark_overlay = self._create_watermark_overlay(
                    width, height, info, style
                )
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # 动态时间戳模式：每帧更新时间
                if dynamic_timestamp:
                    info.refresh_dynamic_info()
                    watermark_overlay = self._create_watermark_overlay(
                        width, height, info, style
                    )
                
                # 应用水印
                watermarked_frame = self._apply_watermark_to_frame(
                    frame, watermark_overlay, style.opacity
                )
                
                # 写入帧
                out.write(watermarked_frame)
                
                frame_count += 1
                
                # 进度回调
                if progress_callback:
                    progress_callback(frame_count, total_frames)
        
        finally:
            cap.release()
            out.release()
        
        return str(output_path)
    
    def _create_watermark_overlay(
        self,
        width: int,
        height: int,
        info: WatermarkInfo,
        style: WatermarkStyle
    ) -> np.ndarray:
        """
        创建水印叠加层
        
        Args:
            width: 视频宽度
            height: 视频高度
            info: 水印信息
            style: 水印样式
            
        Returns:
            RGBA格式的numpy数组
        """
        # 创建透明图层
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        
        # 使用图片水印处理器的方法添加水印
        watermark_text = self._format_watermark_text(info, style)
        
        position = style.position.lower()
        
        if position == "tile":
            overlay = self._add_tiled_watermark_pil(overlay, watermark_text, style)
        elif position == "center":
            overlay = self._add_centered_watermark_pil(overlay, watermark_text, style)
        else:
            overlay = self._add_positioned_watermark_pil(overlay, watermark_text, style, position)
        
        # 转换为numpy数组
        return np.array(overlay)
    
    def _format_watermark_text(self, info: WatermarkInfo, style: WatermarkStyle) -> str:
        """格式化水印文本"""
        text = info.to_string(separator=" | ", compact=True)
        
        if style.prefix:
            text = f"{style.prefix} {text}"
        if style.suffix:
            text = f"{text} {style.suffix}"
        
        return text
    
    def _get_font(self, style: WatermarkStyle) -> ImageFont.FreeTypeFont:
        """获取字体"""
        return self._image_watermark._get_font(style)
    
    def _add_tiled_watermark_pil(
        self,
        image: Image.Image,
        text: str,
        style: WatermarkStyle
    ) -> Image.Image:
        """添加平铺水印（PIL版本）"""
        import math
        
        width, height = image.size
        font = self._get_font(style)
        draw = ImageDraw.Draw(image)
        
        # 获取文本尺寸
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 创建单个水印
        diagonal = int(math.sqrt(text_width**2 + text_height**2)) + 20
        single_watermark = Image.new('RGBA', (diagonal, diagonal), (0, 0, 0, 0))
        single_draw = ImageDraw.Draw(single_watermark)
        
        x = (diagonal - text_width) // 2
        y = (diagonal - text_height) // 2
        
        # 绘制阴影
        if style.shadow:
            shadow_color = (*style.shadow_color, int(style.opacity * 128))
            single_draw.text(
                (x + style.shadow_offset[0], y + style.shadow_offset[1]),
                text, font=font, fill=shadow_color
            )
        
        # 绘制文本
        single_draw.text((x, y), text, font=font, fill=style.rgba_color)
        
        # 旋转
        single_watermark = single_watermark.rotate(
            style.rotation, expand=False, resample=Image.BICUBIC
        )
        
        # 平铺
        spacing_x = text_width + style.column_spacing
        spacing_y = text_height + style.line_spacing
        
        for y_pos in range(-diagonal, height + diagonal, spacing_y):
            offset = spacing_x // 2 if (y_pos // spacing_y) % 2 else 0
            for x_pos in range(-diagonal + offset, width + diagonal, spacing_x):
                image.paste(single_watermark, (x_pos, y_pos), single_watermark)
        
        return image
    
    def _add_centered_watermark_pil(
        self,
        image: Image.Image,
        text: str,
        style: WatermarkStyle
    ) -> Image.Image:
        """添加居中水印"""
        width, height = image.size
        font = self._get_font(style)
        draw = ImageDraw.Draw(image)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        if style.shadow:
            shadow_color = (*style.shadow_color, int(style.opacity * 128))
            draw.text(
                (x + style.shadow_offset[0], y + style.shadow_offset[1]),
                text, font=font, fill=shadow_color
            )
        
        draw.text((x, y), text, font=font, fill=style.rgba_color)
        
        return image
    
    def _add_positioned_watermark_pil(
        self,
        image: Image.Image,
        text: str,
        style: WatermarkStyle,
        position: str
    ) -> Image.Image:
        """添加定位水印"""
        width, height = image.size
        font = self._get_font(style)
        draw = ImageDraw.Draw(image)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
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
        
        return image
    
    def _apply_watermark_to_frame(
        self,
        frame: np.ndarray,
        watermark_overlay: np.ndarray,
        opacity: float
    ) -> np.ndarray:
        """
        将水印应用到视频帧
        
        Args:
            frame: BGR格式的视频帧
            watermark_overlay: RGBA格式的水印层
            opacity: 透明度
            
        Returns:
            添加水印后的帧
        """
        # 转换帧为RGBA
        frame_rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        
        # 获取水印的alpha通道
        alpha = watermark_overlay[:, :, 3:4] / 255.0
        
        # 混合
        blended = frame_rgba.astype(float)
        watermark_rgb = watermark_overlay[:, :, :3]
        
        # 只在有水印的地方混合
        mask = alpha > 0
        blended[:, :, :3] = np.where(
            np.broadcast_to(mask, blended[:, :, :3].shape),
            frame_rgba[:, :, :3] * (1 - alpha) + watermark_rgb * alpha,
            frame_rgba[:, :, :3]
        )
        
        # 转回BGR
        result = cv2.cvtColor(blended.astype(np.uint8), cv2.COLOR_RGBA2BGR)
        
        return result
    
    def extract_frame(
        self,
        video_path: Union[str, Path],
        frame_number: int = 0
    ) -> Image.Image:
        """
        提取视频帧
        
        Args:
            video_path: 视频路径
            frame_number: 帧号
            
        Returns:
            PIL Image对象
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise ValueError(f"无法读取帧 {frame_number}")
        
        # 转换为RGB并创建PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame_rgb)
    
    def extract(
        self,
        video_path: Union[str, Path],
        frame_number: int = 0,
        use_ocr: bool = False
    ) -> Optional[WatermarkInfo]:
        """
        从视频中提取水印信息
        
        Args:
            video_path: 视频路径
            frame_number: 要分析的帧号
            use_ocr: 是否使用OCR
            
        Returns:
            提取的水印信息
        """
        # 提取帧
        frame = self.extract_frame(video_path, frame_number)
        
        # 保存临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            frame.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            # 使用图片水印处理器提取
            return self._image_watermark.extract(tmp_path, use_ocr)
        finally:
            os.unlink(tmp_path)
    
    def get_video_info(self, video_path: Union[str, Path]) -> dict:
        """
        获取视频信息
        
        Args:
            video_path: 视频路径
            
        Returns:
            视频信息字典
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"无法打开视频文件: {video_path}")
        
        info = {
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS),
            "codec": int(cap.get(cv2.CAP_PROP_FOURCC)),
        }
        
        cap.release()
        return info
    
    def batch_embed(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        info: WatermarkInfo,
        style: Optional[WatermarkStyle] = None,
        recursive: bool = False,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> List[str]:
        """
        批量添加水印
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            info: 水印信息
            style: 水印样式
            recursive: 是否递归处理
            progress_callback: 进度回调 (filename, current, total)
            
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
            files = list(input_dir.rglob("*"))
        else:
            files = list(input_dir.glob("*"))
        
        video_files = [f for f in files if f.suffix.lower() in self.SUPPORTED_FORMATS]
        total = len(video_files)
        
        for i, input_file in enumerate(video_files):
            relative_path = input_file.relative_to(input_dir)
            output_file = output_dir / relative_path
            
            try:
                if progress_callback:
                    progress_callback(str(input_file.name), i + 1, total)
                
                self.embed(input_file, output_file, info, style)
                processed.append(str(output_file))
            except Exception as e:
                print(f"处理失败 {input_file}: {e}")
        
        return processed
