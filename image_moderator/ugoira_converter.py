#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ugoira 转换器 - 将 Pixiv 动图转换为 GIF 或 MP4
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from typing import Tuple, Optional

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("警告: PIL/Pillow 未安装，无法转换为 GIF")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("警告: OpenCV 未安装，无法转换为 MP4")


class UgoiraConverter:
    """Ugoira 动图转换器"""
    
    def __init__(self, output_format: str = "gif"):
        """
        初始化转换器
        
        Args:
            output_format: 输出格式 ("gif" 或 "mp4")
        """
        self.output_format = output_format.lower()
        
        if self.output_format == "gif" and not PIL_AVAILABLE:
            raise ImportError("需要安装 Pillow 才能转换为 GIF: pip install Pillow")
        
        if self.output_format == "mp4" and not CV2_AVAILABLE:
            raise ImportError("需要安装 OpenCV 才能转换为 MP4: pip install opencv-python")
    
    def convert_ugoira(self, ugoira_dir: str, delete_source: bool = True) -> Tuple[bool, str]:
        """
        转换 ugoira 目录为 GIF 或 MP4
        
        Args:
            ugoira_dir: ugoira 目录路径
            delete_source: 是否删除源文件（zip和解压的帧）
            
        Returns:
            Tuple[bool, str]: (是否成功, 输出文件路径或错误信息)
        """
        ugoira_path = Path(ugoira_dir)
        
        if not ugoira_path.exists() or not ugoira_path.is_dir():
            return False, f"目录不存在: {ugoira_dir}"
        
        # 查找 zip 文件和 frames.json
        zip_files = list(ugoira_path.glob("*.zip"))
        frames_file = ugoira_path / "frames.json"
        
        if not zip_files:
            return False, "未找到 zip 文件"
        
        if not frames_file.exists():
            return False, "未找到 frames.json"
        
        zip_file = zip_files[0]
        
        try:
            # 读取帧信息
            with open(frames_file, 'r', encoding='utf-8') as f:
                frames_info = json.load(f)
            
            # 解压 zip 文件
            extract_dir = ugoira_path / "frames"
            extract_dir.mkdir(exist_ok=True)
            
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # 获取所有帧文件（按顺序）
            frame_files = []
            for frame_info in frames_info:
                frame_file = extract_dir / frame_info['file']
                if frame_file.exists():
                    frame_files.append((str(frame_file), frame_info['delay']))
            
            if not frame_files:
                return False, "未找到帧文件"
            
            # 根据格式转换
            if self.output_format == "gif":
                output_file = self._convert_to_gif(frame_files, ugoira_path)
            else:  # mp4
                output_file = self._convert_to_mp4(frame_files, ugoira_path)
            
            # 清理临时文件
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            
            # 删除源文件
            if delete_source and output_file:
                if zip_file.exists():
                    zip_file.unlink()
                if frames_file.exists():
                    frames_file.unlink()
            
            return True, str(output_file)
            
        except Exception as e:
            return False, f"转换失败: {str(e)}"
    
    def _convert_to_gif(self, frame_files: list, output_dir: Path) -> Optional[Path]:
        """
        转换为 GIF
        
        Args:
            frame_files: [(帧文件路径, 延迟ms), ...]
            output_dir: 输出目录
            
        Returns:
            输出文件路径
        """
        if not PIL_AVAILABLE:
            raise ImportError("需要安装 Pillow")
        
        # 加载所有帧
        frames = []
        durations = []
        
        for frame_path, delay in frame_files:
            img = Image.open(frame_path)
            frames.append(img.copy())
            durations.append(delay)  # PIL 使用毫秒
        
        # 生成输出文件名
        output_file = output_dir / f"{output_dir.name.replace('_ugoira', '')}.gif"
        
        # 保存为 GIF
        frames[0].save(
            output_file,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,  # 无限循环
            optimize=False  # 不优化以保持质量
        )
        
        return output_file
    
    def _convert_to_mp4(self, frame_files: list, output_dir: Path) -> Optional[Path]:
        """
        转换为 MP4
        
        Args:
            frame_files: [(帧文件路径, 延迟ms), ...]
            output_dir: 输出目录
            
        Returns:
            输出文件路径
        """
        if not CV2_AVAILABLE:
            raise ImportError("需要安装 OpenCV")
        
        # 读取第一帧以获取尺寸
        first_frame = cv2.imread(frame_files[0][0])
        height, width = first_frame.shape[:2]
        
        # 生成输出文件名
        output_file = output_dir / f"{output_dir.name.replace('_ugoira', '')}.mp4"
        
        # 计算平均帧率
        total_duration = sum(delay for _, delay in frame_files)
        fps = len(frame_files) / (total_duration / 1000.0)
        fps = max(1, min(fps, 60))  # 限制在 1-60 fps
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_file), fourcc, fps, (width, height))
        
        # 写入所有帧
        for frame_path, delay in frame_files:
            frame = cv2.imread(frame_path)
            # 根据延迟重复帧
            repeat_count = max(1, int(delay * fps / 1000))
            for _ in range(repeat_count):
                out.write(frame)
        
        out.release()
        
        return output_file
    
    def convert_directory(self, input_dir: str, delete_source: bool = True, verbose: bool = True) -> dict:
        """
        批量转换目录中的所有 ugoira
        
        Args:
            input_dir: 输入目录
            delete_source: 是否删除源文件
            verbose: 是否显示详细信息
            
        Returns:
            统计信息字典
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            return {'error': '目录不存在'}
        
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }
        
        # 查找所有 ugoira 目录
        ugoira_dirs = [d for d in input_path.iterdir() if d.is_dir() and d.name.endswith('_ugoira')]
        
        stats['total'] = len(ugoira_dirs)
        
        for ugoira_dir in ugoira_dirs:
            if verbose:
                print(f"转换: {ugoira_dir.name}")
            
            success, message = self.convert_ugoira(str(ugoira_dir), delete_source=delete_source)
            
            if success:
                stats['success'] += 1
                if verbose:
                    print(f"  ✓ 成功: {message}")
            else:
                stats['failed'] += 1
                if verbose:
                    print(f"  ✗ 失败: {message}")
        
        return stats
