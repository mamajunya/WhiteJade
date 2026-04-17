#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pixiv图片下载器 - 增强版
支持通过角色名、标签、作者ID等多种方式自动拉取图片
"""

import os
import sys
import json
import time
import argparse
from typing import List, Dict, Optional, Set
from datetime import datetime
from pathlib import Path

try:
    from pixivpy3 import AppPixivAPI
except ImportError:
    print("错误: 未安装 pixivpy3")
    print("请运行: pip install pixivpy3")
    sys.exit(1)

class PixivDownloader:
    """Pixiv图片下载器主类 - 增强版"""
    
    def __init__(self, refresh_token: str = None, download_dir: str = "downloads"):
        """
        初始化Pixiv下载器
        
        Args:
            refresh_token: Pixiv刷新令牌，用于认证
            download_dir: 下载根目录
        """
        self.api = AppPixivAPI()
        self.refresh_token = refresh_token
        self.is_logged_in = False
        
        # 下载根目录
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        
        # 下载历史记录（避免重复下载）
        self.downloaded_ids: Set[int] = set()
        
        # 统计信息
        self.stats = {
            'total_searched': 0,
            'total_downloaded': 0,
            'total_skipped': 0,
            'total_failed': 0
        }
    
    def _get_project_dirs(self, project_name: str) -> dict:
        """
        获取项目目录结构
        
        Args:
            project_name: 项目名称（如关键词、用户ID等）
            
        Returns:
            包含各个子目录路径的字典
        """
        # 清理项目名称中的非法字符
        safe_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_', '。', '！', '？')).strip()
        if len(safe_name) > 50:
            safe_name = safe_name[:50]
        
        project_root = os.path.join(self.download_dir, safe_name)
        
        dirs = {
            'root': project_root,
            'history': os.path.join(project_root, 'history'),
            'ban': os.path.join(project_root, 'ban'),
            'picture': os.path.join(project_root, 'picture')
        }
        
        # 创建所有目录
        for dir_path in dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        return dirs
    
    def _load_history(self, project_name: str):
        """
        加载指定项目的下载历史
        
        Args:
            project_name: 项目名称
        """
        dirs = self._get_project_dirs(project_name)
        history_file = os.path.join(dirs['history'], 'download_history.json')
        
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    self.downloaded_ids = set(history.get('downloaded_ids', []))
                    print(f"已加载下载历史: {len(self.downloaded_ids)} 个作品")
            except Exception as e:
                print(f"加载历史记录失败: {e}")
    
    def _save_history(self, project_name: str):
        """
        保存指定项目的下载历史
        
        Args:
            project_name: 项目名称
        """
        dirs = self._get_project_dirs(project_name)
        history_file = os.path.join(dirs['history'], 'download_history.json')
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'project_name': project_name,
                    'downloaded_ids': list(self.downloaded_ids),
                    'last_update': datetime.now().isoformat(),
                    'total_downloaded': len(self.downloaded_ids)
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
        
    def login(self, refresh_token: str = None) -> bool:
        """
        登录Pixiv
        
        Args:
            refresh_token: 刷新令牌，如果为None则使用初始化时提供的
            
        Returns:
            bool: 登录是否成功
        """
        token = refresh_token or self.refresh_token
        
        if not token:
            print("错误: 需要提供refresh_token才能登录Pixiv")
            print("请按照以下步骤获取refresh_token:")
            print("1. 访问 https://app-api.pixiv.net/web/v1/login")
            print("2. 登录你的Pixiv账号")
            print("3. 从浏览器开发者工具中获取refresh_token")
            return False
        
        try:
            self.api.auth(refresh_token=token)
            self.is_logged_in = True
            print("登录Pixiv成功!")
            return True
        except Exception as e:
            print(f"登录失败: {e}")
            return False
    
    def search_illustrations(self, query: str, page: int = 1, per_page: int = 30, 
                           sort: str = 'date_desc', search_target: str = 'partial_match_for_tags') -> List[Dict]:
        """
        搜索插画
        
        Args:
            query: 搜索关键词（角色名+标签）
            page: 页码
            per_page: 每页数量
            sort: 排序方式 (date_desc, date_asc, popular_desc)
            search_target: 搜索目标 (partial_match_for_tags, exact_match_for_tags, title_and_caption)
            
        Returns:
            List[Dict]: 插画列表
        """
        if not self.is_logged_in:
            print("错误: 请先登录Pixiv")
            return []
        
        try:
            print(f"正在搜索: {query} (第{page}页, 排序: {sort})...")
            json_result = self.api.search_illust(
                query, 
                search_target=search_target, 
                sort=sort, 
                duration=None, 
                offset=(page-1)*per_page
            )
            
            if not json_result or 'illusts' not in json_result:
                print("未找到相关作品")
                return []
            
            illusts = json_result['illusts']
            self.stats['total_searched'] += len(illusts)
            print(f"找到 {len(illusts)} 个作品")
            return illusts
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_user_illustrations(self, user_id: int, illust_type: str = 'illust', offset: int = 0) -> List[Dict]:
        """
        获取指定用户的作品
        
        Args:
            user_id: 用户ID
            illust_type: 作品类型 (illust, manga)
            offset: 偏移量
            
        Returns:
            List[Dict]: 作品列表
        """
        if not self.is_logged_in:
            print("错误: 请先登录Pixiv")
            return []
        
        try:
            print(f"正在获取用户 {user_id} 的作品...")
            json_result = self.api.user_illusts(user_id, type=illust_type, offset=offset)
            
            if not json_result or 'illusts' not in json_result:
                print("未找到作品")
                return []
            
            illusts = json_result['illusts']
            self.stats['total_searched'] += len(illusts)
            print(f"找到 {len(illusts)} 个作品")
            return illusts
            
        except Exception as e:
            print(f"获取用户作品失败: {e}")
            return []
    
    def get_recommended_illustrations(self, offset: int = 0) -> List[Dict]:
        """
        获取推荐作品
        
        Args:
            offset: 偏移量
            
        Returns:
            List[Dict]: 作品列表
        """
        if not self.is_logged_in:
            print("错误: 请先登录Pixiv")
            return []
        
        try:
            print("正在获取推荐作品...")
            json_result = self.api.illust_recommended(offset=offset)
            
            if not json_result or 'illusts' not in json_result:
                print("未找到推荐作品")
                return []
            
            illusts = json_result['illusts']
            self.stats['total_searched'] += len(illusts)
            print(f"找到 {len(illusts)} 个推荐作品")
            return illusts
            
        except Exception as e:
            print(f"获取推荐作品失败: {e}")
            return []
    
    def get_ranking_illustrations(self, mode: str = 'day', date: str = None, offset: int = 0) -> List[Dict]:
        """
        获取排行榜作品
        
        Args:
            mode: 排行榜类型 (day, week, month, day_male, day_female, week_original, week_rookie, day_r18, etc.)
            date: 日期 (格式: YYYY-MM-DD)
            offset: 偏移量
            
        Returns:
            List[Dict]: 作品列表
        """
        if not self.is_logged_in:
            print("错误: 请先登录Pixiv")
            return []
        
        try:
            print(f"正在获取排行榜作品 (模式: {mode})...")
            json_result = self.api.illust_ranking(mode=mode, date=date, offset=offset)
            
            if not json_result or 'illusts' not in json_result:
                print("未找到排行榜作品")
                return []
            
            illusts = json_result['illusts']
            self.stats['total_searched'] += len(illusts)
            print(f"找到 {len(illusts)} 个排行榜作品")
            return illusts
            
        except Exception as e:
            print(f"获取排行榜失败: {e}")
            return []
    
    def get_illustration_details(self, illust_id: int) -> Optional[Dict]:
        """
        获取插画详细信息
        
        Args:
            illust_id: 插画ID
            
        Returns:
            Dict: 插画详细信息
        """
        if not self.is_logged_in:
            print("错误: 请先登录Pixiv")
            return None
        
        try:
            json_result = self.api.illust_detail(illust_id)
            if json_result and 'illust' in json_result:
                return json_result['illust']
            return None
        except Exception as e:
            print(f"获取作品详情失败: {e}")
            return None
    
    def download_illustration(self, illust: Dict, project_name: str, skip_existing: bool = True) -> bool:
        """
        下载插画到新的目录结构
        
        Args:
            illust: 插画信息
            project_name: 项目名称（用于创建目录）
            skip_existing: 是否跳过已下载的作品
            
        Returns:
            bool: 下载是否成功
        """
        if not illust:
            return False
        
        try:
            illust_id = illust['id']
            
            # 检查是否已下载
            if skip_existing and illust_id in self.downloaded_ids:
                print(f"已下载过: {illust['title']} (ID: {illust_id})")
                self.stats['total_skipped'] += 1
                return False
            
            title = illust['title']
            user_name = illust['user']['name']
            
            # 清理文件名中的非法字符
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_', '。', '！', '？')).strip()
            
            # 限制文件名长度
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
            
            # 获取项目目录结构
            dirs = self._get_project_dirs(project_name)
            target_dir = dirs['picture']  # 图片保存到 picture 目录
            
            # 检查作品类型
            if illust['type'] == 'illust':
                # 单张图片 - 优先下载原图
                if illust.get('meta_single_page') and illust['meta_single_page'].get('original_image_url'):
                    image_url = illust['meta_single_page']['original_image_url']
                else:
                    image_url = illust['image_urls'].get('large') or illust['image_urls'].get('medium')
                
                # 从URL获取文件扩展名
                ext = os.path.splitext(image_url)[1] or '.jpg'
                filename = f"{illust_id}_{safe_title}{ext}"
                filepath = os.path.join(target_dir, filename)
                
                if not os.path.exists(filepath):
                    print(f"下载中: {title} (ID: {illust_id})")
                    self.api.download(image_url, path=target_dir, name=filename)
                    print(f"✓ 已保存: {filename}")
                else:
                    print(f"已存在: {filename}")
                    
            elif illust['type'] == 'manga' or illust.get('page_count', 1) > 1:
                # 漫画（多张图片）
                print(f"下载漫画: {title} (ID: {illust_id}, {illust.get('page_count', 0)} 页)")
                manga_dir = os.path.join(target_dir, f"{illust_id}_{safe_title}")
                os.makedirs(manga_dir, exist_ok=True)
                
                # 获取漫画所有页面
                manga_pages = illust.get('meta_pages', [])
                if not manga_pages:
                    print("  无法获取漫画页面")
                    return False
                
                for i, page in enumerate(manga_pages):
                    # 优先下载原图
                    image_url = page['image_urls'].get('original') or page['image_urls'].get('large')
                    ext = os.path.splitext(image_url)[1] or '.jpg'
                    filename = f"{illust_id}_p{i}{ext}"
                    filepath = os.path.join(manga_dir, filename)
                    
                    if not os.path.exists(filepath):
                        self.api.download(image_url, path=manga_dir, name=filename)
                        print(f"  ✓ 页面 {i+1}/{len(manga_pages)}")
                    else:
                        print(f"  已存在 {i+1}/{len(manga_pages)}")
                    
                    time.sleep(0.5)  # 避免请求过快
                        
            elif illust['type'] == 'ugoira':
                # 动图
                print(f"动图作品: {title} (ID: {illust_id}) - 暂不支持下载动图")
                self.stats['total_skipped'] += 1
                return False
            else:
                print(f"未知作品类型: {illust['type']}")
                self.stats['total_skipped'] += 1
                return False
            
            # 保存作品信息到 history 目录
            info_file = os.path.join(dirs['history'], f"{illust_id}_info.json")
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'id': illust_id,
                    'title': title,
                    'user_id': illust['user']['id'],
                    'user_name': user_name,
                    'tags': [tag['name'] for tag in illust['tags']],
                    'create_date': illust['create_date'],
                    'page_count': illust.get('page_count', 1),
                    'type': illust['type'],
                    'total_view': illust.get('total_view', 0),
                    'total_bookmarks': illust.get('total_bookmarks', 0),
                    'width': illust.get('width', 0),
                    'height': illust.get('height', 0),
                    'x_restrict': illust.get('x_restrict', 0),
                    'download_date': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
            
            # 记录到下载历史
            self.downloaded_ids.add(illust_id)
            self._save_history(project_name)
            self.stats['total_downloaded'] += 1
            
            return True
            
        except Exception as e:
            print(f"✗ 下载失败 (ID: {illust.get('id', 'unknown')}): {e}")
            self.stats['total_failed'] += 1
            return False
    
    def download_by_query(self, query: str, max_count: int = 50, 
                         start_page: int = 1, max_pages: int = 5,
                         skip_r18: bool = False, skip_ai: bool = False, min_bookmarks: int = 0,
                         sort: str = 'date_desc') -> int:
        """
        根据查询词下载图片
        
        Args:
            query: 搜索关键词
            max_count: 最大下载数量
            start_page: 起始页码
            max_pages: 最大搜索页数
            skip_r18: 是否跳过R-18作品
            skip_ai: 是否跳过AI作品
            min_bookmarks: 最小收藏数过滤
            sort: 排序方式
            
        Returns:
            int: 成功下载的数量
        """
        if not self.is_logged_in:
            print("错误: 请先登录Pixiv")
            return 0
        
        # 加载该项目的下载历史
        self._load_history(query)
        
        downloaded_count = 0
        page = start_page
        
        print(f"\n开始下载任务:")
        print(f"  关键词: {query}")
        print(f"  目标数量: {max_count}")
        print(f"  最小收藏数: {min_bookmarks}")
        print(f"  跳过R-18: {'是' if skip_r18 else '否'}")
        print(f"  跳过AI作品: {'是' if skip_ai else '否'}")
        print(f"  排序方式: {sort}\n")
        
        while downloaded_count < max_count and page <= start_page + max_pages - 1:
            illusts = self.search_illustrations(query, page=page, sort=sort)
            
            if not illusts:
                print("没有更多作品了")
                break
            
            for illust in illusts:
                if downloaded_count >= max_count:
                    break
                
                # 跳过R-18作品（可选）
                if skip_r18 and illust.get('x_restrict', 0) > 0:
                    print(f"跳过R-18: {illust['title']} (ID: {illust['id']})")
                    self.stats['total_skipped'] += 1
                    continue
                
                # 跳过AI作品（可选）
                # illust_ai_type: 0=未知, 1=非AI, 2=AI生成
                if skip_ai and illust.get('illust_ai_type', 0) == 2:
                    print(f"跳过AI作品: {illust['title']} (ID: {illust['id']})")
                    self.stats['total_skipped'] += 1
                    continue
                
                # 收藏数过滤
                if illust.get('total_bookmarks', 0) < min_bookmarks:
                    print(f"收藏数不足: {illust['title']} ({illust.get('total_bookmarks', 0)} < {min_bookmarks})")
                    self.stats['total_skipped'] += 1
                    continue
                
                # 获取完整作品信息
                full_illust = self.get_illustration_details(illust['id'])
                if full_illust:
                    if self.download_illustration(full_illust, project_name=query):
                        downloaded_count += 1
                        print(f"进度: {downloaded_count}/{max_count}")
                
                # 避免请求过快
                time.sleep(1.5)
            
            page += 1
            time.sleep(2)  # 页间延迟
        
        self._print_stats()
        return downloaded_count
    
    def download_by_user(self, user_id: int, max_count: int = 50, 
                        illust_type: str = 'illust') -> int:
        """
        下载指定用户的作品
        
        Args:
            user_id: 用户ID
            max_count: 最大下载数量
            illust_type: 作品类型
            
        Returns:
            int: 成功下载的数量
        """
        if not self.is_logged_in:
            print("错误: 请先登录Pixiv")
            return 0
        
        project_name = f"user_{user_id}"
        self._load_history(project_name)
        
        downloaded_count = 0
        offset = 0
        
        print(f"\n开始下载用户 {user_id} 的作品...")
        
        while downloaded_count < max_count:
            illusts = self.get_user_illustrations(user_id, illust_type=illust_type, offset=offset)
            
            if not illusts:
                break
            
            for illust in illusts:
                if downloaded_count >= max_count:
                    break
                
                if self.download_illustration(illust, project_name=project_name):
                    downloaded_count += 1
                    print(f"进度: {downloaded_count}/{max_count}")
                
                time.sleep(1.5)
            
            offset += len(illusts)
            time.sleep(2)
        
        self._print_stats()
        return downloaded_count
    
    def download_ranking(self, mode: str = 'day', max_count: int = 50, 
                        date: str = None) -> int:
        """
        下载排行榜作品
        
        Args:
            mode: 排行榜类型
            max_count: 最大下载数量
            date: 日期
            
        Returns:
            int: 成功下载的数量
        """
        if not self.is_logged_in:
            print("错误: 请先登录Pixiv")
            return 0
        
        project_name = f"ranking_{mode}"
        self._load_history(project_name)
        
        downloaded_count = 0
        offset = 0
        
        print(f"\n开始下载排行榜作品 (模式: {mode})...")
        
        while downloaded_count < max_count:
            illusts = self.get_ranking_illustrations(mode=mode, date=date, offset=offset)
            
            if not illusts:
                break
            
            for illust in illusts:
                if downloaded_count >= max_count:
                    break
                
                if self.download_illustration(illust, project_name=project_name):
                    downloaded_count += 1
                    print(f"进度: {downloaded_count}/{max_count}")
                
                time.sleep(1.5)
            
            offset += len(illusts)
            time.sleep(2)
        
        self._print_stats()
        return downloaded_count
    
    def _print_stats(self):
        """打印统计信息"""
        print("\n" + "="*60)
        print("下载统计:")
        print(f"  搜索到: {self.stats['total_searched']} 个作品")
        print(f"  已下载: {self.stats['total_downloaded']} 个作品")
        print(f"  已跳过: {self.stats['total_skipped']} 个作品")
        if self.stats['total_failed'] > 0:
            print(f"  失败: {self.stats['total_failed']} 个作品")
        print("="*60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Pixiv图片下载器 - 增强版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 按关键词搜索下载
  python pixiv_downloader.py "小萝莉" -n 30
  
  # 过滤低收藏作品
  python pixiv_downloader.py "原神 纳西妲" -n 50 --min-bookmarks 1000
  
  # 下载指定用户的作品
  python pixiv_downloader.py --user 12345678 -n 50
  
  # 下载排行榜
  python pixiv_downloader.py --ranking day -n 50
  
  # 跳过R-18内容
  python pixiv_downloader.py "二次元" -n 20 --skip-r18
        """
    )
    
    # 基础参数
    parser.add_argument('query', nargs='?', help='搜索关键词（角色名+标签）')
    parser.add_argument('-t', '--refresh-token', help='Pixiv刷新令牌')
    parser.add_argument('-n', '--max-count', type=int, default=20, help='最大下载数量（默认: 20）')
    parser.add_argument('-p', '--max-pages', type=int, default=3, help='最大搜索页数（默认: 3）')
    parser.add_argument('-s', '--start-page', type=int, default=1, help='起始页码（默认: 1）')
    
    # 获取脚本所在目录，用于定位配置文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(script_dir, 'config.json')
    
    parser.add_argument('-c', '--config', default=default_config, help='配置文件路径（默认: config.json）')
    parser.add_argument('-o', '--output', help='输出目录（默认: downloads）')
    
    # 高级参数
    parser.add_argument('--user', type=int, help='下载指定用户ID的作品')
    parser.add_argument('--type', choices=['illust', 'manga'], default='illust', help='作品类型（默认: illust）')
    parser.add_argument('--ranking', choices=['day', 'week', 'month', 'day_male', 'day_female', 
                                             'week_original', 'week_rookie', 'day_r18'],
                       help='下载排行榜作品')
    parser.add_argument('--date', help='排行榜日期（格式: YYYY-MM-DD）')
    parser.add_argument('--skip-r18', action='store_true', help='跳过R-18内容')
    parser.add_argument('--skip-ai', action='store_true', help='跳过AI生成作品')
    parser.add_argument('--min-bookmarks', type=int, default=0, help='最小收藏数过滤（默认: 0）')
    parser.add_argument('--sort', choices=['date_desc', 'date_asc', 'popular_desc'], 
                       default='date_desc', help='排序方式（默认: date_desc）')
    
    args = parser.parse_args()
    
    # 从配置文件读取设置
    refresh_token = args.refresh_token
    download_dir = args.output or "downloads"
    
    if os.path.exists(args.config):
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if not refresh_token and 'refresh_token' in config:
                    refresh_token = config['refresh_token']
                if not args.output and 'download_dir' in config:
                    download_dir = config['download_dir']
                if args.max_count == 20 and 'default_max_count' in config:
                    args.max_count = config['default_max_count']
                if args.max_pages == 3 and 'default_max_pages' in config:
                    args.max_pages = config['default_max_pages']
                if not args.skip_r18 and config.get('skip_r18'):
                    args.skip_r18 = True
                if not args.skip_ai and config.get('skip_ai'):
                    args.skip_ai = True
                if args.min_bookmarks == 0 and 'min_bookmarks' in config:
                    args.min_bookmarks = config['min_bookmarks']
        except Exception as e:
            print(f"读取配置文件失败: {e}")
    
    # 创建下载器
    downloader = PixivDownloader(refresh_token, download_dir=download_dir)
    
    # 登录
    if not downloader.login():
        return
    
    # 根据参数执行不同的下载任务
    if args.user:
        # 下载指定用户的作品
        print(f"下载用户 {args.user} 的作品...")
        count = downloader.download_by_user(
            user_id=args.user,
            max_count=args.max_count,
            illust_type=args.type
        )
        print(f"\n✓ 下载完成! 共下载 {count} 个作品")
        return
    
    if args.ranking:
        # 下载排行榜
        print(f"下载排行榜: {args.ranking}")
        count = downloader.download_ranking(
            mode=args.ranking,
            max_count=args.max_count,
            date=args.date
        )
        print(f"\n✓ 下载完成! 共下载 {count} 个作品")
        return
    
    if args.query:
        # 按关键词搜索下载
        print(f"搜索并下载: {args.query}")
        count = downloader.download_by_query(
            query=args.query,
            max_count=args.max_count,
            start_page=args.start_page,
            max_pages=args.max_pages,
            skip_r18=args.skip_r18,
            skip_ai=args.skip_ai,
            min_bookmarks=args.min_bookmarks,
            sort=args.sort
        )
        print(f"\n✓ 下载完成! 共下载 {count} 个作品")
        return
    
    # 交互模式
    print("\n" + "="*60)
    print("  Pixiv 图片下载器 - 增强版")
    print("="*60)
    print("\n命令:")
    print("  search <关键词>  - 搜索并下载")
    print("  user <用户ID>    - 下载用户作品")
    print("  ranking <类型>   - 下载排行榜 (day/week/month)")
    print("  help            - 显示帮助")
    print("  quit            - 退出程序")
    print()
    
    while True:
        try:
            user_input = input(">>> ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            
            if command in ('quit', 'exit', 'q'):
                print("再见!")
                break
            
            elif command in ('help', 'h'):
                print("\n使用说明:")
                print("  search <关键词>")
                print("    示例: search 小萝莉 VOCALOID")
                print("    示例: search 原神 纳西妲")
                print()
                print("  user <用户ID>")
                print("    示例: user 12345678")
                print()
                print("  ranking <类型>")
                print("    示例: ranking day")
                print("    示例: ranking week")
                print()
                continue
            
            elif command == 'search':
                if len(parts) < 2:
                    print("请输入搜索关键词")
                    continue
                
                query = parts[1]
                
                # 询问下载数量
                try:
                    max_count = input(f"下载数量 (默认 {args.max_count}): ").strip()
                    max_count = int(max_count) if max_count else args.max_count
                except ValueError:
                    max_count = args.max_count
                
                count = downloader.download_by_query(
                    query=query,
                    max_count=max_count,
                    start_page=args.start_page,
                    max_pages=args.max_pages,
                    skip_r18=args.skip_r18,
                    skip_ai=args.skip_ai,
                    min_bookmarks=args.min_bookmarks,
                    sort=args.sort
                )
                print(f"\n✓ 下载完成! 共下载 {count} 个作品\n")
            
            elif command == 'user':
                if len(parts) < 2:
                    print("请输入用户ID")
                    continue
                
                try:
                    user_id = int(parts[1])
                except ValueError:
                    print("用户ID必须是数字")
                    continue
                
                # 询问下载数量
                try:
                    max_count = input(f"下载数量 (默认 {args.max_count}): ").strip()
                    max_count = int(max_count) if max_count else args.max_count
                except ValueError:
                    max_count = args.max_count
                
                count = downloader.download_by_user(
                    user_id=user_id,
                    max_count=max_count,
                    illust_type=args.type
                )
                print(f"\n✓ 下载完成! 共下载 {count} 个作品\n")
            
            elif command == 'ranking':
                mode = parts[1] if len(parts) > 1 else 'day'
                
                if mode not in ['day', 'week', 'month', 'day_male', 'day_female', 
                               'week_original', 'week_rookie', 'day_r18']:
                    print(f"不支持的排行榜类型: {mode}")
                    print("支持的类型: day, week, month, day_male, day_female, week_original, week_rookie")
                    continue
                
                # 询问下载数量
                try:
                    max_count = input(f"下载数量 (默认 {args.max_count}): ").strip()
                    max_count = int(max_count) if max_count else args.max_count
                except ValueError:
                    max_count = args.max_count
                
                count = downloader.download_ranking(
                    mode=mode,
                    max_count=max_count
                )
                print(f"\n✓ 下载完成! 共下载 {count} 个作品\n")
            
            else:
                print(f"未知命令: {command}")
                print("输入 'help' 查看帮助")
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
