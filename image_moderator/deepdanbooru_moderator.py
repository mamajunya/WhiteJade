#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepDanbooru 图片审核器 - 专门针对动漫图片
使用 DeepDanbooru 模型进行精确的动漫图片内容识别
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List, Tuple, Dict
import argparse

try:
    import deepdanbooru as dd
    import tensorflow as tf
    from PIL import Image
    import numpy as np
except ImportError as e:
    print(f"导入错误: {e}")
    print("正在安装必要的依赖...")
    print("请运行: pip install deepdanbooru tensorflow pillow numpy")
    raise ImportError("缺少必要的依赖库，请安装 deepdanbooru tensorflow pillow numpy")


class DeepDanbooruModerator:
    """DeepDanbooru 图片审核器 - 专门针对动漫图片"""
    
    def __init__(self, threshold: float = 0.5, model_path: str = None, filter_tags: List[str] = None, ugoira_threshold_offset: float = -0.1):
        """
        初始化审核器
        
        Args:
            threshold: 检测阈值 (0-1)，标签置信度超过此值才会被识别
            model_path: 模型路径（如果为 None 则使用默认路径）
            filter_tags: 自定义过滤标签列表（如果为 None 则使用默认标签）
            ugoira_threshold_offset: 动图阈值偏移量，动图审核时会在原阈值基础上增加此值（默认-0.1，更严格）
        """
        print("正在加载 DeepDanbooru 模型...")
        print("（首次运行会自动下载模型，约 600MB，请耐心等待）")
        
        # 设置 TensorFlow 日志级别
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
        
        print("步骤 1: 设置 TensorFlow...")
        try:
            tf.get_logger().setLevel('ERROR')
        except Exception as e:
            print(f"TensorFlow 日志设置失败（可忽略）: {e}")
        
        print("步骤 2: 确定模型路径...")
        # 加载模型
        if model_path is None:
            # 检测是否为打包后的环境
            if getattr(sys, 'frozen', False):
                # 打包后的环境，模型在 _internal/model
                base_path = sys._MEIPASS
                project_model_path = os.path.join(base_path, 'model')
            else:
                # 开发环境，模型在项目根目录的 model 文件夹
                project_model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'model')
            
            if os.path.exists(os.path.join(project_model_path, 'model-resnet_custom_v3.h5')):
                model_path = project_model_path
                print(f"✓ 找到本地模型: {model_path}")
            else:
                print(f"✗ 本地模型不存在: {project_model_path}")
                # 使用默认模型路径
                model_path = os.path.join(os.path.expanduser('~'), '.deepdanbooru')
                
                # 如果模型不存在，下载它
                if not os.path.exists(os.path.join(model_path, 'model-resnet_custom_v3.h5')):
                    print("正在下载模型...")
                    os.makedirs(model_path, exist_ok=True)
                    # 使用 deepdanbooru 的下载命令
                    import subprocess
                    try:
                        subprocess.run(['deepdanbooru', 'download-model', model_path], check=True)
                    except Exception as e:
                        print(f"自动下载失败: {e}")
                        print("\n请手动下载模型：")
                        print("1. 访问: https://github.com/KichangKim/DeepDanbooru/releases")
                        print("2. 下载 deepdanbooru-v3-20211112-sgd-e28.zip")
                        print(f"3. 解压到: {model_path}")
                        print(f"\n或者将模型文件放到项目根目录的 model/ 文件夹中")
                        sys.exit(1)
        
        print("步骤 3: 加载模型文件...")
        try:
            self.model = dd.project.load_model_from_project(
                project_path=model_path,
                compile_model=False
            )
            print("✓ 模型加载成功")
            
            print("步骤 4: 加载标签文件...")
            self.tags = dd.project.load_tags_from_project(project_path=model_path)
            print(f"✓ 标签加载成功 (共 {len(self.tags)} 个标签)")
        except Exception as e:
            print(f"✗ 模型加载失败: {e}")
            print("\n请确保模型文件存在：")
            print(f"  {model_path}/model-resnet_custom_v3.h5")
            print(f"  {model_path}/tags.txt")
            print("\n请运行以下命令下载模型：")
            print(f"  python download_deepdanbooru_model.py")
            raise e
        
        self.threshold = threshold
        self.ugoira_threshold_offset = ugoira_threshold_offset
        
        # 需要过滤的标签
        if filter_tags is not None:
            # 使用用户自定义的标签
            self.filter_tags = set(filter_tags)
        else:
            # 使用默认标签（只过滤男性生殖器和性交）
            self.filter_tags = {
                'penis',           # 男性生殖器
                'sex',             # 性交
                'vaginal',         # 阴道性交
                'anal',            # 肛交
            }
        
        # 可选的严格标签（可以根据需要添加）
        self.optional_strict_tags = {
            'fellatio',        # 口交-男
            'cunnilingus',     # 口交-女
            'oral',            # 口交
            'pussy',           # 女性生殖器
            'anus',            # 肛门
        }
        
        print("模型加载完成！")
        print(f"当前过滤标签: {', '.join(self.filter_tags)}")
        print(f"标签总数: {len(self.tags)}")
    
    def check_ugoira(self, ugoira_dir: str, verbose: bool = True) -> Tuple[bool, dict]:
        """
        审核动图（Ugoira）
        根据阈值动态调整审核帧数比例：
        - 0.4 (非常严格): 100% 帧数
        - 0.5 (严格): 90% 帧数
        - 0.6 (默认): 80% 帧数
        - 0.7 (宽松): 60% 帧数
        - 0.8 (非常宽松): 40% 帧数
        
        注意：由于Pixiv动图画质较低可能导致误判通过，审核时会在原阈值基础上减少ugoira_threshold_offset（默认-0.1）使审核更严格
        
        Args:
            ugoira_dir: 动图目录路径（包含zip文件）
            verbose: 是否显示详细信息
            
        Returns:
            (should_keep, result): 是否保留和详细结果
        """
        import zipfile
        import random
        import tempfile
        
        ugoira_path = Path(ugoira_dir)
        
        # 查找zip文件
        zip_files = list(ugoira_path.glob('*_ugoira.zip'))
        if not zip_files:
            return True, {'error': '未找到动图zip文件'}
        
        zip_file = zip_files[0]
        
        # 保存原始阈值
        original_threshold = self.threshold
        
        # 动图使用更严格的阈值（因为画质较低可能导致误判通过）
        ugoira_threshold = max(0.0, self.threshold + self.ugoira_threshold_offset)
        self.threshold = ugoira_threshold
        
        try:
            # 解压zip文件获取帧列表
            with zipfile.ZipFile(zip_file, 'r') as zf:
                frame_files = sorted([f for f in zf.namelist() if f.lower().endswith(('.jpg', '.png'))])
                
                if not frame_files:
                    return True, {'error': '动图中没有找到图片帧'}
                
                total_frames = len(frame_files)
                
                # 根据原始阈值确定审核帧数比例
                if original_threshold <= 0.4:
                    # 非常严格：100% 帧数
                    check_ratio = 1.0
                elif original_threshold <= 0.5:
                    # 严格：90% 帧数
                    check_ratio = 0.9
                elif original_threshold <= 0.6:
                    # 默认：80% 帧数
                    check_ratio = 0.8
                elif original_threshold <= 0.7:
                    # 宽松：60% 帧数
                    check_ratio = 0.6
                else:
                    # 非常宽松：40% 帧数
                    check_ratio = 0.4
                
                # 计算需要审核的帧数（至少2帧）
                frames_to_check_count = max(2, int(total_frames * check_ratio))
                
                # 均匀分布选择帧
                if frames_to_check_count >= total_frames:
                    # 审核所有帧
                    selected_indices = list(range(total_frames))
                else:
                    # 均匀分布选择帧
                    step = total_frames / frames_to_check_count
                    selected_indices = [int(i * step) for i in range(frames_to_check_count)]
                
                selected_frames = [frame_files[i] for i in selected_indices]
                
                if verbose:
                    print(f"  动图共 {total_frames} 帧")
                    print(f"  审核比例: {check_ratio*100:.0f}% ({frames_to_check_count} 帧)")
                    print(f"  动图阈值: {ugoira_threshold:.2f} (原始: {original_threshold:.2f}, 偏移: {self.ugoira_threshold_offset:+.2f})")
                    print(f"  抽取帧: {', '.join([f'#{i}' for i in selected_indices[:5]])}{'...' if len(selected_indices) > 5 else ''}")
                
                # 创建临时目录
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    
                    # 提取并审核选中的帧
                    all_results = []
                    failed_frames = []
                    
                    for frame_name in selected_frames:
                        # 提取帧到临时目录
                        frame_data = zf.read(frame_name)
                        temp_frame = temp_path / frame_name
                        temp_frame.write_bytes(frame_data)
                        
                        # 审核这一帧
                        should_keep, result = self.check_image(str(temp_frame), verbose=False)
                        all_results.append((should_keep, result, frame_name))
                        
                        if not should_keep:
                            failed_frames.append(frame_name)
                            if verbose:
                                print(f"    {frame_name}: ✗ 不通过 - {result['reason']}")
                        elif verbose:
                            print(f"    {frame_name}: ✓ 通过")
                        
                        # 如果有一帧不通过，整个动图不通过
                        if not should_keep:
                            # 恢复原始阈值
                            self.threshold = original_threshold
                            return False, {
                                'frame': frame_name,
                                'reason': f"动图帧 {frame_name} 未通过审核: {result['reason']}",
                                'filtered_tags': result.get('filtered_tags', {}),
                                'all_tags': result.get('all_tags', {}),
                                'frames_checked': len(all_results),
                                'total_frames': total_frames,
                                'check_ratio': check_ratio,
                                'ugoira_threshold': ugoira_threshold,
                                'original_threshold': original_threshold
                            }
                    
                    # 恢复原始阈值
                    self.threshold = original_threshold
                    
                    # 所有帧都通过
                    return True, {
                        'reason': '动图审核通过',
                        'frames_checked': frames_to_check_count,
                        'total_frames': total_frames,
                        'check_ratio': check_ratio,
                        'ugoira_threshold': ugoira_threshold,
                        'original_threshold': original_threshold
                    }
                    
        except Exception as e:
            # 恢复原始阈值
            self.threshold = original_threshold
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"审核动图时出错: {error_msg}")
            return True, {'error': error_msg}
    
    def check_image(self, image_path: str, verbose: bool = False) -> Tuple[bool, dict]:
        """
        检查单张图片
        
        Args:
            image_path: 图片路径
            verbose: 是否显示详细信息
            
        Returns:
            (是否应该保留, 检测详情)
        """
        try:
            # 加载图片
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 调整图片大小（DeepDanbooru 需要固定尺寸）
            width = self.model.input_shape[2]
            height = self.model.input_shape[1]
            image = image.resize((width, height), Image.LANCZOS)
            
            # 转换为数组并归一化
            image_array = np.array(image, dtype=np.float32) / 255.0
            image_array = np.expand_dims(image_array, axis=0)
            
            # 预测
            predictions = self.model.predict(image_array, verbose=0)[0]
            
            # 获取所有标签及其置信度
            detected_tags = {}
            filtered_tags = {}
            
            for i, tag in enumerate(self.tags):
                score = float(predictions[i])
                if score >= self.threshold:
                    detected_tags[tag] = score
                    
                    # 检查是否需要过滤
                    if tag in self.filter_tags:
                        filtered_tags[tag] = score
            
            # 判断是否应该保留
            should_keep = len(filtered_tags) == 0
            
            # 生成原因
            if filtered_tags:
                reasons = [f"{tag} ({score:.2%})" for tag, score in filtered_tags.items()]
                reason = f"检测到敏感内容: {', '.join(reasons)}"
            else:
                reason = "通过审核"
            
            # 检查是否有打码
            censored_tags = {}
            for tag in ['censored', 'mosaic_censoring', 'bar_censor']:
                if tag in detected_tags:
                    censored_tags[tag] = detected_tags[tag]
            
            result = {
                'all_tags': detected_tags,
                'filtered_tags': filtered_tags,
                'censored_tags': censored_tags,
                'should_keep': should_keep,
                'reason': reason
            }
            
            if verbose:
                print(f"\n检测到 {len(detected_tags)} 个标签（置信度 ≥ {self.threshold}）")
                if censored_tags:
                    print(f"打码标签: {', '.join(censored_tags.keys())}")
                if filtered_tags:
                    print(f"过滤标签: {', '.join(filtered_tags.keys())}")
            
            return should_keep, result
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            print(f"处理图片时出错 {image_path}: {error_msg}")
            return True, {'error': error_msg}
    
    def process_directory(
        self, 
        input_dir: str, 
        output_dir: str = None,
        ban_dir: str = None,
        delete_filtered: bool = False,
        verbose: bool = True
    ) -> dict:
        """
        批量处理目录中的图片
        
        Args:
            input_dir: 输入目录（picture 目录）
            output_dir: 输出目录（保留的图片，如果为None则保持在原位置）
            ban_dir: 被过滤图片的目录（如果为None则自动使用 ../ban）
            delete_filtered: 是否删除被过滤的图片
            verbose: 是否显示详细信息
            
        Returns:
            处理统计信息
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            raise ValueError(f"输入目录不存在: {input_dir}")
        
        # 如果没有指定 ban_dir，自动使用 ../ban
        if ban_dir is None:
            ban_dir = input_path.parent / 'ban'
        ban_path = Path(ban_dir)
        ban_path.mkdir(parents=True, exist_ok=True)
        
        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        
        # 获取所有图片文件和动图目录
        image_files = []
        ugoira_dirs = []
        
        for item in input_path.iterdir():
            if item.is_file() and item.suffix.lower() in image_extensions:
                image_files.append(item)
            elif item.is_dir() and item.name.endswith('_ugoira'):
                # 动图目录
                ugoira_dirs.append(item)
            elif item.is_dir():
                # 检查子目录中的图片（漫画目录）
                for subitem in item.rglob('*'):
                    if subitem.is_file() and subitem.suffix.lower() in image_extensions:
                        image_files.append(subitem)
        
        total_items = len(image_files) + len(ugoira_dirs)
        
        if total_items == 0:
            print(f"在 {input_dir} 中没有找到图片文件或动图")
            return {}
        
        print(f"\n找到 {len(image_files)} 张图片和 {len(ugoira_dirs)} 个动图，开始审核...\n")
        
        stats = {
            'total': total_items,
            'kept': 0,
            'filtered': 0,
            'errors': 0
        }
        
        filtered_list = []
        current_idx = 0
        
        # 处理图片文件
        for image_file in image_files:
            current_idx += 1
            if verbose:
                print(f"[{current_idx}/{total_items}] 处理图片: {image_file.name}")
            
            should_keep, result = self.check_image(str(image_file), verbose=False)
            
            if 'error' in result:
                stats['errors'] += 1
                if verbose:
                    print(f"  ✗ 错误: {result['error'][:50]}...")
                continue
            
            if should_keep:
                stats['kept'] += 1
                if verbose:
                    print(f"  ✓ 保留 - {result['reason']}")
                    if result.get('censored_tags'):
                        print(f"    （检测到打码: {', '.join(result['censored_tags'].keys())}）")
                
                # 如果指定了输出目录，复制文件
                if output_dir:
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    # 保持相对路径结构
                    relative_path = image_file.relative_to(input_path)
                    dest_file = output_path / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.copy2(image_file, dest_file)
            else:
                stats['filtered'] += 1
                filtered_list.append(str(image_file))
                if verbose:
                    print(f"  ✗ 过滤 - {result['reason']}")
                    if result.get('censored_tags'):
                        print(f"    （检测到打码: {', '.join(result['censored_tags'].keys())}）")
                
                # 移动到 ban 目录
                try:
                    # 保持相对路径结构
                    relative_path = image_file.relative_to(input_path)
                    ban_file = ban_path / relative_path
                    ban_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    if delete_filtered:
                        # 移动文件
                        shutil.move(str(image_file), str(ban_file))
                        if verbose:
                            print(f"    已移动到 ban 目录")
                    else:
                        # 复制文件
                        shutil.copy2(image_file, ban_file)
                        if verbose:
                            print(f"    已复制到 ban 目录")
                except Exception as e:
                    print(f"    移动/复制到 ban 目录失败: {e}")
        
        # 处理动图目录
        for ugoira_dir in ugoira_dirs:
            current_idx += 1
            if verbose:
                print(f"[{current_idx}/{total_items}] 处理动图: {ugoira_dir.name}")
            
            should_keep, result = self.check_ugoira(str(ugoira_dir), verbose=verbose)
            
            if 'error' in result:
                stats['errors'] += 1
                if verbose:
                    print(f"  ✗ 错误: {result['error'][:50]}...")
                continue
            
            if should_keep:
                stats['kept'] += 1
                if verbose:
                    print(f"  ✓ 保留 - {result['reason']}")
                
                # 如果指定了输出目录，复制整个目录
                if output_dir:
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    relative_path = ugoira_dir.relative_to(input_path)
                    dest_dir = output_path / relative_path
                    
                    shutil.copytree(ugoira_dir, dest_dir, dirs_exist_ok=True)
            else:
                stats['filtered'] += 1
                filtered_list.append(str(ugoira_dir))
                if verbose:
                    print(f"  ✗ 过滤 - {result['reason']}")
                
                # 移动到 ban 目录
                try:
                    relative_path = ugoira_dir.relative_to(input_path)
                    ban_dir_path = ban_path / relative_path
                    
                    if delete_filtered:
                        # 移动整个目录
                        shutil.move(str(ugoira_dir), str(ban_dir_path))
                        if verbose:
                            print(f"    已移动到 ban 目录")
                    else:
                        # 复制整个目录
                        shutil.copytree(ugoira_dir, ban_dir_path, dirs_exist_ok=True)
                        if verbose:
                            print(f"    已复制到 ban 目录")
                except Exception as e:
                    print(f"    移动/复制到 ban 目录失败: {e}")
        
        # 打印统计信息
        print("\n" + "="*50)
        print("审核完成！统计信息：")
        print(f"  总计: {stats['total']} 张")
        print(f"  保留: {stats['kept']} 张 ({stats['kept']/stats['total']*100:.1f}%)")
        print(f"  过滤: {stats['filtered']} 张 ({stats['filtered']/stats['total']*100:.1f}%)")
        if stats['errors'] > 0:
            print(f"  错误: {stats['errors']} 张")
        print("="*50)
        
        # 保存过滤列表到 history 目录
        if filtered_list:
            # 尝试找到 history 目录
            history_dir = input_path.parent / 'history'
            if not history_dir.exists():
                history_dir = input_path.parent
            
            log_file = history_dir / 'filtered_images_deepdanbooru.log'
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(filtered_list))
            print(f"\n被过滤的图片列表已保存到: {log_file}")
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description='DeepDanbooru 图片审核工具 - 专门针对动漫图片',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 审核目录中的图片（不删除）
  python deepdanbooru_moderator.py -i ./downloads/纳西妲/picture
  
  # 审核并将通过的图片复制到新目录
  python deepdanbooru_moderator.py -i ./images -o ./approved
  
  # 审核并删除被过滤的图片
  python deepdanbooru_moderator.py -i ./images --delete
  
  # 调整检测阈值（更严格）
  python deepdanbooru_moderator.py -i ./images -t 0.3
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='输入目录路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出目录路径（保留通过审核的图片）'
    )
    
    parser.add_argument(
        '-t', '--threshold',
        type=float,
        default=0.5,
        help='检测阈值 (0-1)，默认0.5'
    )
    
    parser.add_argument(
        '--delete',
        action='store_true',
        help='删除被过滤的图片（危险操作，请谨慎使用）'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='静默模式，只显示统计信息'
    )
    
    args = parser.parse_args()
    
    # 安全确认
    if args.delete:
        print("\n⚠️  警告：您选择了删除模式，被过滤的图片将被永久删除！")
        confirm = input("确认继续？(输入 YES 继续): ")
        if confirm != "YES":
            print("操作已取消")
            return
    
    # 创建审核器
    moderator = DeepDanbooruModerator(threshold=args.threshold)
    
    # 处理图片
    moderator.process_directory(
        input_dir=args.input,
        output_dir=args.output,
        delete_filtered=args.delete,
        verbose=not args.quiet
    )


if __name__ == '__main__':
    main()
