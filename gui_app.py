#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pixiv 下载器 + 图片审核工具 - GUI 版本
简洁的淡粉色+白色配色，圆角边框，支持自定义背景
"""

import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QCheckBox, QTextEdit,
    QProgressBar, QFileDialog, QMessageBox, QGroupBox,
    QComboBox, QFrame, QScrollArea, QTabWidget, QRadioButton, QButtonGroup,
    QColorDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QProcess
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPainterPath

# 导入下载和审核模块
sys.path.insert(0, 'pixiv_downloader')
sys.path.insert(0, 'image_moderator')

try:
    from gppt import GetPixivToken
    GPPT_AVAILABLE = True
except ImportError:
    GPPT_AVAILABLE = False
    print("警告: gppt 库未安装，Token 获取功能将不可用")
    print("请运行: pip install gppt")


# 翻译字典
TRANSLATIONS = {
    "zh_CN": {
        "app_title": "WhiteJade",
        "tab_download": "📥 下载与过滤",
        "tab_token": "🔑 Token 获取",
        "tab_settings": "⚙️ 设置",
        "settings": "⚙️ 设置",
        "theme_color": "主题色:",
        "choose_color": "选择颜色",
        "preset_colors": "预设:",
        "language": "语言:",
        "download_dir": "下载目录:",
        "open_folder": "打开下载目录",
        "theme_changed": "主题已切换！",
        "language_changed": "语言已切换！\n\n重启应用后生效。",
        # 下载与过滤
        "download_settings": "📥 下载设置",
        "search_keyword": "搜索关键词:",
        "keyword_placeholder": "例如: 小萝莉",
        "download_count": "下载数量:",
        "min_bookmarks": "最小收藏:",
        "skip_r18": "跳过 R-18 内容",
        "skip_ai": "去除 AI 作品",
        "moderate_settings": "🔍 审核设置",
        "enable_moderate": "启用图片审核（下载完成后自动审核）",
        "detection_threshold": "检测阈值:",
        "move_to_ban": "将不合格图片移动到 ban 目录",
        "run_log": "📝 运行日志",
        "log_placeholder": "日志将显示在这里...",
        "start_execution": "🚀 开始执行",
        "pause_execution": "⏸️ 暂停",
        "resume_execution": "▶️ 继续",
        "stop_execution": "⏹️ 停止",
        "ready": "就绪",
        # Token 获取
        "token_info": "💡 使用 gppt 库获取 Pixiv Token\n\n自动模式：输入邮箱和密码，自动获取 Token（无头浏览器）\n手动模式：打开浏览器，手动登录后自动获取 Token",
        "get_mode": "获取模式",
        "auto_mode": "🤖 自动模式（邮箱 + 密码）",
        "manual_mode": "👆 手动模式（浏览器登录）",
        "login_info": "登录信息",
        "email": "邮箱:",
        "email_placeholder": "your@email.com",
        "password": "密码:",
        "password_placeholder": "密码",
        "current_token": "当前 Token",
        "token_placeholder": "Token 将显示在这里...",
        "copy": "📋 复制",
        "save_to_config": "💾 保存到配置",
        "get_token": "🔑 获取 Token",
        # 设置
        "about": "关于",
        "about_text": "WhiteJade属于cll计划的主分支之一，\n\n 旨在高效的精选内容,\n\n WhiteJade可以自动拉取pixiv上内容筛选，可以最大限度节约时间并防止眼睛遭到重创，\n\n 注:本软件完全开源免费，如果你在网上购买到的此软件，\n\n 请立刻退款并'问候'对方全家",
    },
    "ja_JP": {
        "app_title": "WhiteJade",
        "tab_download": "📥 ダウンロードとフィルター",
        "tab_token": "🔑 Token 取得",
        "tab_settings": "⚙️ 設定",
        "settings": "⚙️ 設定",
        "theme_color": "テーマカラー:",
        "choose_color": "色を選択",
        "preset_colors": "プリセット:",
        "language": "言語:",
        "download_dir": "ダウンロードフォルダ:",
        "open_folder": "フォルダを開く",
        "theme_changed": "テーマが変更されました！",
        "language_changed": "言語が変更されました！\n\nアプリを再起動してください。",
        "download_settings": "📥 ダウンロード設定",
        "search_keyword": "検索キーワード:",
        "keyword_placeholder": "例: 小さなロリ",
        "download_count": "ダウンロード数:",
        "min_bookmarks": "最小ブックマーク:",
        "skip_r18": "R-18 コンテンツをスキップ",
        "skip_ai": "AI 作品を除外",
        "moderate_settings": "🔍 審査設定",
        "enable_moderate": "画像審査を有効にする（ダウンロード後に自動審査）",
        "detection_threshold": "検出しきい値:",
        "move_to_ban": "不適格な画像を ban フォルダに移動",
        "run_log": "📝 実行ログ",
        "log_placeholder": "ログはここに表示されます...",
        "start_execution": "🚀 実行開始",
        "pause_execution": "⏸️ 一時停止",
        "resume_execution": "▶️ 再開",
        "stop_execution": "⏹️ 停止",
        "ready": "準備完了",
        "token_info": "💡 gppt ライブラリを使用して Pixiv Token を取得\n\n自動モード：メールアドレスとパスワードを入力し、自動的に Token を取得（ヘッドレスブラウザ）\n手動モード：ブラウザを開き、手動でログイン後に自動的に Token を取得",
        "get_mode": "取得モード",
        "auto_mode": "🤖 自動モード（メール + パスワード）",
        "manual_mode": "👆 手動モード（ブラウザログイン）",
        "login_info": "ログイン情報",
        "email": "メール:",
        "email_placeholder": "your@email.com",
        "password": "パスワード:",
        "password_placeholder": "パスワード",
        "current_token": "現在の Token",
        "token_placeholder": "Token はここに表示されます...",
        "copy": "📋 コピー",
        "save_to_config": "💾 設定に保存",
        "get_token": "🔑 Token を取得",
        "about": "について",
        "about_text": "WhiteJadeはcll計画の主要ブランチの一つであり、\n効率的にコンテンツを厳選することを目的としています。\nWhiteJadeはpixiv上のコンテンツを自動で取得・フィルタリングし、\n時間を最大限節約し、目へのダメージを防ぎます。\n注：本ソフトは完全にオープンソースで無料です。\nもし本ソフトをネット上で購入した場合は、\nすぐに返金を要求し、相手の家族に「よろしく」伝えてください。\n証拠は必ず保存しておいてください。",
    },
    "ko_KR": {
        "app_title": "WhiteJade",
        "tab_download": "📥 다운로드 및 필터",
        "tab_token": "🔑 Token 가져오기",
        "tab_settings": "⚙️ 설정",
        "settings": "⚙️ 설정",
        "theme_color": "테마 색상:",
        "choose_color": "색상 선택",
        "preset_colors": "프리셋:",
        "language": "언어:",
        "download_dir": "다운로드 폴더:",
        "open_folder": "폴더 열기",
        "theme_changed": "테마가 변경되었습니다！",
        "language_changed": "언어가 변경되었습니다！\n\n앱을 다시 시작하세요。",
        "download_settings": "📥 다운로드 설정",
        "search_keyword": "검색 키워드:",
        "keyword_placeholder": "예: 꼬마 로리",
        "download_count": "다운로드 수:",
        "min_bookmarks": "최소 북마크:",
        "skip_r18": "R-18 콘텐츠 건너뛰기",
        "skip_ai": "AI 작품 제외",
        "moderate_settings": "🔍 심사 설정",
        "enable_moderate": "이미지 심사 활성화（다운로드 후 자동 심사）",
        "detection_threshold": "감지 임계값:",
        "move_to_ban": "부적격 이미지를 ban 폴더로 이동",
        "run_log": "📝 실행 로그",
        "log_placeholder": "로그가 여기에 표시됩니다...",
        "start_execution": "🚀 실행 시작",
        "pause_execution": "⏸️ 일시정지",
        "resume_execution": "▶️ 계속",
        "stop_execution": "⏹️ 중지",
        "ready": "준비",
        "token_info": "💡 gppt 라이브러리를 사용하여 Pixiv Token 가져오기\n\n자동 모드：이메일과 비밀번호를 입력하고 자동으로 Token 가져오기（헤드리스 브라우저）\n수동 모드：브라우저를 열고 수동으로 로그인한 후 자동으로 Token 가져오기",
        "get_mode": "가져오기 모드",
        "auto_mode": "🤖 자동 모드（이메일 + 비밀번호）",
        "manual_mode": "👆 수동 모드（브라우저 로그인）",
        "login_info": "로그인 정보",
        "email": "이메일:",
        "email_placeholder": "your@email.com",
        "password": "비밀번호:",
        "password_placeholder": "비밀번호",
        "current_token": "현재 Token",
        "token_placeholder": "Token이 여기에 표시됩니다...",
        "copy": "📋 복사",
        "save_to_config": "💾 설정에 저장",
        "get_token": "🔑 Token 가져오기",
        "about": "정보",
        "about_text": "WhiteJade는 cll 계획의 주요 브랜치 중 하나로,\n효율적인 콘텐츠 선별을 목표로 합니다.\nWhiteJade는 pixiv의 콘텐츠를 자동으로 가져와 필터링하며,\n시간을 최대한 절약하고 눈에 가해지는 피해를 방지합니다.\n참고: 이 소프트웨어는 완전히 오픈소스이며 무료입니다.\n만약 이 소프트웨어를 인터넷에서 구매하셨다면,\n즉시 환불을 요구하고 상대방의 온 가족에게 '안부'를 전해 주세요.\n증거는 반드시 보관하시기 바랍니다.",
    },
    "en_US": {
        "app_title": "WhiteJade",
        "tab_download": "📥 Download & Filter",
        "tab_token": "🔑 Get Token",
        "tab_settings": "⚙️ Settings",
        "settings": "⚙️ Settings",
        "theme_color": "Theme Color:",
        "choose_color": "Choose Color",
        "preset_colors": "Presets:",
        "language": "Language:",
        "download_dir": "Download Folder:",
        "open_folder": "Open Folder",
        "theme_changed": "Theme changed!",
        "language_changed": "Language changed!\n\nPlease restart the app.",
        "download_settings": "📥 Download Settings",
        "search_keyword": "Search Keyword:",
        "keyword_placeholder": "e.g.: loli",
        "download_count": "Download Count:",
        "min_bookmarks": "Min Bookmarks:",
        "skip_r18": "Skip R-18 Content",
        "skip_ai": "Skip AI Artworks",
        "moderate_settings": "🔍 Moderation Settings",
        "enable_moderate": "Enable Image Moderation (Auto-moderate after download)",
        "detection_threshold": "Detection Threshold:",
        "move_to_ban": "Move unqualified images to ban folder",
        "run_log": "📝 Run Log",
        "log_placeholder": "Logs will be displayed here...",
        "start_execution": "🚀 Start Execution",
        "pause_execution": "⏸️ Pause",
        "resume_execution": "▶️ Resume",
        "stop_execution": "⏹️ Stop",
        "ready": "Ready",
        "token_info": "💡 Use gppt library to get Pixiv Token\n\nAuto Mode: Enter email and password, automatically get Token (headless browser)\nManual Mode: Open browser, manually login and automatically get Token",
        "get_mode": "Get Mode",
        "auto_mode": "🤖 Auto Mode (Email + Password)",
        "manual_mode": "👆 Manual Mode (Browser Login)",
        "login_info": "Login Info",
        "email": "Email:",
        "email_placeholder": "your@email.com",
        "password": "Password:",
        "password_placeholder": "Password",
        "current_token": "Current Token",
        "token_placeholder": "Token will be displayed here...",
        "copy": "📋 Copy",
        "save_to_config": "💾 Save to Config",
        "get_token": "🔑 Get Token",
        "about": "About",
        "about_text": "WhiteJade is one of the main branches of the cll project,\n aiming to efficiently curate content.\n WhiteJade can automatically fetch and filter content from pixiv,\n maximizing time savings and preventing severe eye strain.\n Note: This software is completely open source and free.\n If you have purchased this software online,\n please request a refund immediately and 'send your regards' to the seller's entire family.\n Be sure to keep the evidence.",
    },
    "fr_FR": {
        "app_title": "WhiteJade",
        "tab_download": "📥 Télécharger et filtrer",
        "tab_token": "🔑 Obtenir Token",
        "tab_settings": "⚙️ Paramètres",
        "settings": "⚙️ Paramètres",
        "theme_color": "Couleur du thème:",
        "choose_color": "Choisir la couleur",
        "preset_colors": "Préréglages:",
        "language": "Langue:",
        "download_dir": "Dossier de téléchargement:",
        "open_folder": "Ouvrir le dossier",
        "theme_changed": "Thème changé!",
        "language_changed": "Langue changée!\n\nVeuillez redémarrer l'application.",
        "download_settings": "📥 Paramètres de téléchargement",
        "search_keyword": "Mot-clé de recherche:",
        "keyword_placeholder": "par ex.: loli",
        "download_count": "Nombre de téléchargements:",
        "min_bookmarks": "Signets minimum:",
        "skip_r18": "Ignorer le contenu R-18",
        "skip_ai": "Exclure les œuvres IA",
        "moderate_settings": "🔍 Paramètres de modération",
        "enable_moderate": "Activer la modération d'image (Modération automatique après téléchargement)",
        "detection_threshold": "Seuil de détection:",
        "move_to_ban": "Déplacer les images non qualifiées vers le dossier ban",
        "run_log": "📝 Journal d'exécution",
        "log_placeholder": "Les journaux seront affichés ici...",
        "start_execution": "🚀 Démarrer l'exécution",
        "pause_execution": "⏸️ Pause",
        "resume_execution": "▶️ Reprendre",
        "stop_execution": "⏹️ Arrêter",
        "ready": "Prêt",
        "token_info": "💡 Utilisez la bibliothèque gppt pour obtenir le Token Pixiv\n\nMode automatique: Entrez l'e-mail et le mot de passe, obtenez automatiquement le Token (navigateur sans tête)\nMode manuel: Ouvrez le navigateur, connectez-vous manuellement et obtenez automatiquement le Token",
        "get_mode": "Mode d'obtention",
        "auto_mode": "🤖 Mode automatique (E-mail + Mot de passe)",
        "manual_mode": "👆 Mode manuel (Connexion au navigateur)",
        "login_info": "Informations de connexion",
        "email": "E-mail:",
        "email_placeholder": "your@email.com",
        "password": "Mot de passe:",
        "password_placeholder": "Mot de passe",
        "current_token": "Token actuel",
        "token_placeholder": "Le Token sera affiché ici...",
        "copy": "📋 Copier",
        "save_to_config": "💾 Enregistrer dans la configuration",
        "get_token": "🔑 Obtenir Token",
        "about": "À propos",
        "about_text": "WhiteJade est l'une des principales branches du projet cll,\nvisant à organiser efficacement le contenu.\nWhiteJade peut récupérer et filtrer automatiquement le contenu de pixiv,\nce qui permet de gagner un maximum de temps et d'éviter de graves fatigues oculaires.\nRemarque : Ce logiciel est entièrement open source et gratuit.\nSi vous avez acheté ce logiciel en ligne,\ndemandez immédiatement un remboursement et « transmettez vos salutations » à toute lafamille\n du vendeur.\nPensez à conserver les preuves.",
    },
    "de_DE": {
        "app_title": "WhiteJade",
        "tab_download": "📥 Download & Filter",
        "tab_token": "🔑 Token abrufen",
        "tab_settings": "⚙️ Einstellungen",
        "settings": "⚙️ Einstellungen",
        "theme_color": "Themenfarbe:",
        "choose_color": "Farbe wählen",
        "preset_colors": "Voreinstellungen:",
        "language": "Sprache:",
        "download_dir": "Download-Ordner:",
        "open_folder": "Ordner öffnen",
        "theme_changed": "Thema geändert!",
        "language_changed": "Sprache geändert!\n\nBitte starten Sie die App neu.",
        "download_settings": "📥 Download-Einstellungen",
        "search_keyword": "Suchbegriff:",
        "keyword_placeholder": "z.B.: loli",
        "download_count": "Download-Anzahl:",
        "min_bookmarks": "Min. Lesezeichen:",
        "skip_r18": "R-18-Inhalte überspringen",
        "skip_ai": "KI-Kunstwerke ausschließen",
        "moderate_settings": "🔍 Moderationseinstellungen",
        "enable_moderate": "Bildmoderation aktivieren (Automatische Moderation nach Download)",
        "detection_threshold": "Erkennungsschwelle:",
        "move_to_ban": "Unqualifizierte Bilder in den Ban-Ordner verschieben",
        "run_log": "📝 Ausführungsprotokoll",
        "log_placeholder": "Protokolle werden hier angezeigt...",
        "start_execution": "🚀 Ausführung starten",
        "pause_execution": "⏸️ Pause",
        "resume_execution": "▶️ Fortsetzen",
        "stop_execution": "⏹️ Stoppen",
        "ready": "Bereit",
        "token_info": "💡 Verwenden Sie die gppt-Bibliothek, um Pixiv Token abzurufen\n\nAutomatischer Modus: Geben Sie E-Mail und Passwort ein, Token wird automatisch abgerufen (Headless-Browser)\nManueller Modus: Browser öffnen, manuell anmelden und Token automatisch abrufen",
        "get_mode": "Abrufmodus",
        "auto_mode": "🤖 Automatischer Modus (E-Mail + Passwort)",
        "manual_mode": "👆 Manueller Modus (Browser-Anmeldung)",
        "login_info": "Anmeldeinformationen",
        "email": "E-Mail:",
        "email_placeholder": "your@email.com",
        "password": "Passwort:",
        "password_placeholder": "Passwort",
        "current_token": "Aktueller Token",
        "token_placeholder": "Token wird hier angezeigt...",
        "copy": "📋 Kopieren",
        "save_to_config": "💾 In Konfiguration speichern",
        "get_token": "🔑 Token abrufen",
        "about": "Über",
        "about_text": "WhiteJade ist einer der Hauptzweige des cll-Projekts\nund zielt auf eine effiziente Inhaltskuratierung ab.\nWhiteJade kann automatisch Inhalte von pixiv abrufen und filtern,\nwas maximale Zeitersparnis bringt und schwere Augenbelastungen verhindert.\nHinweis: Diese Software ist vollständig Open Source und kostenlos.\nSollten Sie diese Software online gekauft haben,\nfordern Sie sofort eine Rückerstattung und „übermitteln Sie Ihre Grüße“ an die gesamte Familie \ndes Verkäufers.\nBewahren Sie unbedingt die Nachweise auf.",
    },
}


class WorkThread(QThread):
    """工作线程 - 处理下载和审核"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, query, max_count, min_bookmarks, skip_r18, skip_ai,
                 enable_moderate, threshold, delete_filtered):
        super().__init__()
        self.query = query
        self.max_count = max_count
        self.min_bookmarks = min_bookmarks
        self.skip_r18 = skip_r18
        self.skip_ai = skip_ai
        self.enable_moderate = enable_moderate
        self.threshold = threshold
        self.delete_filtered = delete_filtered
        self._is_paused = False
        self._is_stopped = False
    
    def pause(self):
        """暂停线程"""
        self._is_paused = True
    
    def resume(self):
        """继续线程"""
        self._is_paused = False
    
    def stop(self):
        """停止线程"""
        self._is_stopped = True
        self._is_paused = False
    
    def check_pause(self):
        """检查是否暂停"""
        while self._is_paused and not self._is_stopped:
            self.msleep(100)  # 暂停时每100ms检查一次
        return self._is_stopped
    
    def run(self):
        try:
            # 步骤 1: 下载
            from pixiv_downloader import PixivDownloader
            
            if self.check_pause():
                self.finished.emit(False, "任务已停止")
                return
            
            config_path = "pixiv_downloader/config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            token = config.get('refresh_token')
            
            self.progress.emit("[登录] 正在连接 Pixiv 服务器...")
            downloader = PixivDownloader(refresh_token=token)
            
            if self.check_pause():
                self.finished.emit(False, "任务已停止")
                return
            
            if not downloader.login():
                self.finished.emit(False, "登录失败：无法连接到 Pixiv 服务器")
                return
            
            self.progress.emit("[登录] 登录成功")
            self.progress.emit(f"[下载] 开始搜索关键词: {self.query}")
            self.progress.emit(f"[下载] 目标保留数量: {self.max_count} 张图片")
            self.progress.emit(f"[下载] 最小收藏数: {self.min_bookmarks}")
            self.progress.emit(f"[下载] 跳过 R-18: {'是' if self.skip_r18 else '否'}")
            self.progress.emit(f"[下载] 跳过 AI 作品: {'是' if self.skip_ai else '否'}")
            
            if self.enable_moderate:
                self.progress.emit(f"[下载] 启用审核模式: 将下载更多图片以确保最终保留 {self.max_count} 张")
                # 如果启用审核，下载 1.5 倍数量
                download_count = int(self.max_count * 1.5)
            else:
                download_count = self.max_count
            
            if self.check_pause():
                self.finished.emit(False, "任务已停止")
                return
            
            self.progress.emit(f"[下载] 初始下载数量: {download_count} 个作品")
            
            # 启动一个定时器来监控下载进度
            import threading
            last_downloaded = 0
            monitor_running = True
            
            def monitor_progress():
                nonlocal last_downloaded
                while monitor_running and not self._is_stopped:
                    current = downloader.stats.get('total_downloaded', 0)
                    if current > last_downloaded:
                        self.progress.emit(f"[下载] 进度: {current}/{download_count} 个作品")
                        last_downloaded = current
                    threading.Event().wait(2)  # 每2秒检查一次
            
            monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
            monitor_thread.start()
            
            count = downloader.download_by_query(
                query=self.query,
                max_count=download_count,
                skip_r18=self.skip_r18,
                skip_ai=self.skip_ai,
                min_bookmarks=self.min_bookmarks
            )
            
            monitor_running = False  # 停止监控线程
            
            if self._is_stopped:
                self.finished.emit(False, "任务已停止")
                return
            
            if count == 0:
                self.finished.emit(False, "未下载到任何图片，请尝试更换关键词或降低筛选条件")
                return
            
            self.progress.emit(f"[下载] 下载完成，成功下载 {count} 个作品")
            
            # 步骤 2: 审核（如果启用）
            if self.enable_moderate:
                if self.check_pause():
                    self.finished.emit(False, "任务已停止")
                    return
                
                self.progress.emit("[审核] 开始图片内容审核...")
                
                # 使用 DeepDanbooru 审核器（专门针对动漫图片）
                from image_moderator.deepdanbooru_moderator import DeepDanbooruModerator
                
                # 清理项目名称
                safe_name = "".join(c for c in self.query if c.isalnum() or c in (' ', '-', '_', '。', '！', '？')).strip()
                if len(safe_name) > 50:
                    safe_name = safe_name[:50]
                
                picture_dir = Path("downloads") / safe_name / "picture"
                
                if not picture_dir.exists():
                    self.finished.emit(False, "图片目录不存在")
                    return
                
                if self.check_pause():
                    self.finished.emit(False, "任务已停止")
                    return
                
                self.progress.emit("[审核] 正在加载 DeepDanbooru AI 模型...")
                self.progress.emit("[审核] 提示: 模型加载需要约 10-30 秒，请耐心等待")
                self.progress.emit(f"[审核] 检测阈值: {self.threshold} (阈值越低越严格)")
                
                # 在单独的线程中加载模型，避免阻塞 GUI
                try:
                    self.progress.emit("[审核] 步骤 1/3: 导入 DeepDanbooru 模块...")
                    from image_moderator.deepdanbooru_moderator import DeepDanbooruModerator
                    
                    self.progress.emit("[审核] 步骤 2/3: 初始化模型...")
                    # DeepDanbooru 阈值：GUI 的 0.4-0.8 直接对应模型的 0.4-0.8
                    # 0.4 -> 非常严格（推荐用于打码内容）
                    # 0.5 -> 严格
                    # 0.6 -> 默认（推荐）
                    # 0.7 -> 宽松
                    # 0.8 -> 非常宽松
                    moderator = DeepDanbooruModerator(threshold=self.threshold)
                    
                    self.progress.emit("[审核] 步骤 3/3: 模型加载成功 ✓")
                except Exception as e:
                    import traceback
                    error_detail = traceback.format_exc()
                    self.progress.emit(f"[审核] 错误详情: {error_detail}")
                    self.finished.emit(False, f"模型加载失败: {str(e)}")
                    return
                
                if self.check_pause():
                    self.finished.emit(False, "任务已停止")
                    return
                
                self.progress.emit("[审核] 模型加载完成，开始分析图片内容...")
                self.progress.emit(f"[审核] 目标目录: {picture_dir}")
                
                # 循环：下载 -> 审核 -> 检查是否达到目标
                total_downloaded = count
                iteration = 1
                max_iterations = 5  # 最多尝试5轮
                
                while iteration <= max_iterations:
                    if self._is_stopped:
                        self.finished.emit(False, "任务已停止")
                        return
                    
                    self.progress.emit(f"[审核] 第 {iteration} 轮审核...")
                    
                    stats = moderator.process_directory(
                        input_dir=str(picture_dir),
                        delete_filtered=self.delete_filtered,
                        verbose=False
                    )
                    
                    if self._is_stopped:
                        self.finished.emit(False, "任务已停止")
                        return
                    
                    self.progress.emit(f"[审核] 第 {iteration} 轮完成: 保留 {stats['kept']}/{stats['total']} 张")
                    
                    # 检查是否达到目标
                    if stats['kept'] >= self.max_count:
                        self.progress.emit(f"[审核] 已达到目标数量 {self.max_count} 张，审核完成")
                        break
                    
                    # 如果还不够，计算需要继续下载多少
                    needed = self.max_count - stats['kept']
                    if stats['total'] > 0:
                        filter_rate = stats['filtered'] / stats['total']
                        # 根据过滤率估算需要下载的数量（加20%余量）
                        additional = int(needed / (1 - filter_rate) * 1.2) if filter_rate < 1 else needed * 2
                    else:
                        additional = needed * 2
                    
                    self.progress.emit(f"[下载] 还需 {needed} 张，继续下载 {additional} 个作品...")
                    
                    if self.check_pause():
                        self.finished.emit(False, "任务已停止")
                        return
                    
                    # 继续下载
                    additional_count = downloader.download_by_query(
                        query=self.query,
                        max_count=additional,
                        skip_r18=self.skip_r18,
                        skip_ai=self.skip_ai,
                        min_bookmarks=self.min_bookmarks
                    )
                    
                    if additional_count == 0:
                        self.progress.emit("[下载] 没有更多符合条件的作品了")
                        break
                    
                    total_downloaded += additional_count
                    self.progress.emit(f"[下载] 本轮下载 {additional_count} 个作品，累计 {total_downloaded} 个")
                    iteration += 1
                
                # 最终统计
                self.progress.emit("[审核] 所有审核完成")
                self.progress.emit(f"[审核] 最终保留: {stats['kept']} 张图片")
                self.progress.emit(f"[审核] 总计过滤: {stats['filtered']} 张图片")
                
                if stats['kept'] < self.max_count:
                    result = (f"任务完成（未达到目标）\n\n"
                             f"目标数量: {self.max_count} 张\n"
                             f"实际保留: {stats['kept']} 张\n"
                             f"下载作品: {total_downloaded} 个\n"
                             f"审核图片: {stats['total']} 张\n"
                             f"过滤图片: {stats['filtered']} 张\n"
                             f"过滤率: {stats['filtered']/stats['total']*100:.1f}%\n\n"
                             f"提示: 可尝试降低筛选条件或更换关键词")
                else:
                    result = (f"任务完成\n\n"
                             f"目标数量: {self.max_count} 张\n"
                             f"实际保留: {stats['kept']} 张\n"
                             f"下载作品: {total_downloaded} 个\n"
                             f"审核图片: {stats['total']} 张\n"
                             f"过滤图片: {stats['filtered']} 张\n"
                             f"过滤率: {stats['filtered']/stats['total']*100:.1f}%")
                
                self.finished.emit(True, result)
            else:
                self.progress.emit("[完成] 所有任务已完成")
                result = f"下载完成\n\n成功下载 {count} 个作品"
                self.finished.emit(True, result)
            
        except Exception as e:
            self.finished.emit(False, f"操作失败: {str(e)}")





class BackgroundWidget(QWidget):
    """带背景图片的 Widget"""
    def __init__(self, parent=None, theme_color=(255, 182, 193)):
        super().__init__(parent)
        self.background_image = None
        self.theme_color = theme_color
        self.load_background()
        # 设置圆角
        self.setStyleSheet("""
            QWidget {
                background: transparent;
                border-radius: 15px;
            }
        """)
    
    def set_theme_color(self, color):
        """设置主题色"""
        self.theme_color = color
        self.update()  # 触发重绘
    
    def load_background(self, image_path=None):
        """加载背景图片"""
        if image_path is None:
            image_path = "wallpaper.jpg"
        
        if os.path.exists(image_path):
            self.background_image = QPixmap(image_path)
        else:
            self.background_image = None
    
    def paintEvent(self, event):
        """绘制背景"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.background_image:
            # 缩放背景图片以适应窗口
            scaled_pixmap = self.background_image.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # 居中绘制
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            
            # 创建圆角路径
            from PyQt6.QtGui import QPainterPath
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
            painter.setClipPath(path)
            
            painter.drawPixmap(x, y, scaled_pixmap)
        else:
            # 使用主题色的淡化版本作为背景
            # 将主题色与白色混合，使其更淡（90%白色 + 10%主题色）
            r = int(self.theme_color[0] * 0.1 + 255 * 0.9)
            g = int(self.theme_color[1] * 0.1 + 255 * 0.9)
            b = int(self.theme_color[2] * 0.1 + 255 * 0.9)
            
            from PyQt6.QtGui import QPainterPath
            path = QPainterPath()
            path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
            painter.setClipPath(path)
            painter.fillRect(self.rect(), QColor(r, g, b))


class PixivDownloaderGUI(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        # 加载配置
        self.load_config()
        self.init_ui()
        self.apply_styles()
    
    def load_config(self):
        """从配置文件加载设置"""
        try:
            config_path = "pixiv_downloader/config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 加载主题色
                    if 'theme_color' in config:
                        self.theme_color = tuple(config['theme_color'])
                    else:
                        self.theme_color = (255, 182, 193)  # 默认粉色
                    # 加载语言
                    if 'language' in config:
                        self.current_language = config['language']
                    else:
                        self.current_language = "zh_CN"
            else:
                # 默认值
                self.theme_color = (255, 182, 193)
                self.current_language = "zh_CN"
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.theme_color = (255, 182, 193)
            self.current_language = "zh_CN"
    
    def save_config(self):
        """保存设置到配置文件"""
        try:
            config_path = "pixiv_downloader/config.json"
            
            # 确保目录存在
            os.makedirs("pixiv_downloader", exist_ok=True)
            
            # 读取现有配置
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # 更新设置
            config['theme_color'] = list(self.theme_color)
            config['language'] = self.current_language
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle(self.tr("app_title", "Pixiv 下载器 + 图片审核工具"))
        self.setGeometry(100, 100, 900, 650)
        
        # 设置无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建带背景的中心 widget
        self.background_widget = BackgroundWidget(theme_color=self.theme_color)
        self.setCentralWidget(self.background_widget)
        
        # 用于拖动窗口
        self.drag_position = None
        
        # 主布局
        main_layout = QVBoxLayout(self.background_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏（用于拖动窗口）
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")  # 设置对象名称以便后续查找
        title_bar.setFixedHeight(50)
        colors = self.get_theme_colors()
        title_bar.setStyleSheet(f"""
            QWidget#titleBar {{
                background: {colors['primary']};
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
            }}
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 10, 0)
        
        title_label = QLabel(self.tr("app_title", "Pixiv 下载器 + 图片审核工具"))
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; background: transparent;")
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 最小化按钮
        min_btn = QPushButton("−")
        min_btn.setFixedSize(30, 30)
        min_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.3);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.5);
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_btn)
        
        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 100, 100, 0.7);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 50, 50, 0.9);
            }
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)
        
        main_layout.addWidget(title_bar)
        
        # 内容区域
        content_area = QWidget()
        content_area.setStyleSheet("background: transparent;")
        content_main_layout = QVBoxLayout(content_area)
        content_main_layout.setContentsMargins(20, 10, 20, 20)
        content_main_layout.setSpacing(10)
        
        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid rgba(255, 228, 225, 0.8);
                border-radius: 12px;
                background: transparent;
                top: -2px;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.7);
                color: #666;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 2px solid rgba(255, 228, 225, 0.6);
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: rgba(255, 182, 193, 0.9);
                color: white;
                font-weight: bold;
                border: 2px solid rgba(255, 182, 193, 1);
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background: rgba(255, 192, 203, 0.8);
            }
        """)
        
        # 创建三个标签页
        self.tab_download = self.create_download_tab()
        self.tab_token = self.create_token_tab()
        self.tab_settings = self.create_settings_tab()
        
        self.tabs.addTab(self.tab_download, self.tr("tab_download", "📥 下载与过滤"))
        self.tabs.addTab(self.tab_token, self.tr("tab_token", "🔑 Token 获取"))
        self.tabs.addTab(self.tab_settings, self.tr("tab_settings", "⚙️ 设置"))
        
        content_main_layout.addWidget(self.tabs)
        main_layout.addWidget(content_area)
    
    def create_download_tab(self):
        """创建下载与过滤标签页"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 下载设置组
        download_group = self.create_download_group()
        layout.addWidget(download_group)
        
        # 审核设置组
        moderate_group = self.create_moderate_group()
        layout.addWidget(moderate_group)
        
        layout.addStretch()
        
        # 日志区域（紧凑型）
        log_label = QLabel(self.tr("run_log", "📝 运行日志"))
        log_label.setStyleSheet("color: #666; font-size: 12px; background: transparent;")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setPlaceholderText(self.tr("log_placeholder", "日志将显示在这里..."))
        self.log_text.setMaximumHeight(100)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(255, 228, 225, 0.8);
                border-radius: 8px;
                padding: 8px;
                font-size: 11px;
                color: #333;
                font-family: Consolas, monospace;
            }
        """)
        layout.addWidget(self.log_text)
        
        # 控制按钮行
        buttons_layout = QHBoxLayout()
        
        # 开始按钮
        self.start_btn = QPushButton(self.tr("start_execution", "🚀 开始执行"))
        self.start_btn.setFixedHeight(50)
        self.start_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        # 设置白底黑字样式
        colors = self.get_theme_colors()
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background: white;
                color: #333;
                border: 2px solid {colors['primary']};
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {colors['primary_light']};
                color: #333;
                border: 2px solid {colors['primary']};
            }}
            QPushButton:pressed {{
                background: {colors['primary']};
                color: white;
                border: 2px solid {colors['primary']};
            }}
            QPushButton:disabled {{
                background: #F5F5F5;
                color: #999;
                border: 2px solid #DDD;
            }}
        """)
        self.start_btn.clicked.connect(self.start_work)
        buttons_layout.addWidget(self.start_btn)
        
        # 暂停/继续按钮
        self.pause_btn = QPushButton(self.tr("pause_execution", "⏸️ 暂停"))
        self.pause_btn.setFixedHeight(50)
        self.pause_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.pause_btn.setStyleSheet("color: #333;")  # 黑色文字
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_pause)
        buttons_layout.addWidget(self.pause_btn)
        
        # 停止按钮
        self.stop_btn = QPushButton(self.tr("stop_execution", "⏹️ 停止"))
        self.stop_btn.setFixedHeight(50)
        self.stop_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        self.stop_btn.setStyleSheet("color: #333;")  # 黑色文字
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_work)
        buttons_layout.addWidget(self.stop_btn)
        
        layout.addLayout(buttons_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setFormat(self.tr("ready", "就绪"))
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel(self.tr("ready", "就绪"))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            background: rgba(255, 255, 255, 0.9);
            color: #FFB6C1;
            padding: 8px;
            border-radius: 8px;
            font-size: 12px;
        """)
        layout.addWidget(self.status_label)
        
        return widget
    
    def create_token_tab(self):
        """创建 Token 获取标签页"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 说明
        info_label = QLabel(self.tr("token_info", 
            "💡 使用 gppt 库获取 Pixiv Token\n\n"
            "1. 在下方输入 Pixiv 邮箱和密码\n"
            "2. 点击「获取 Token」按钮\n"
            "3. 等待命令行窗口完成登录\n"
            "4. Token 会自动显示在下方\n"
            "5. 点击「保存到配置」按钮保存"
        ))
        info_label.setWordWrap(True)
        info_label.setStyleSheet("""
            background: rgba(255, 255, 255, 0.85);
            color: #666;
            padding: 15px;
            border-radius: 10px;
            border: 2px solid rgba(255, 228, 225, 0.8);
        """)
        layout.addWidget(info_label)
        
        # 登录信息输入
        login_group = QGroupBox(self.tr("login_info", "登录信息"))
        login_group.setStyleSheet("""
            QGroupBox {
                background: rgba(255, 255, 255, 0.85);
                border: 2px solid rgba(255, 228, 225, 0.8);
                border-radius: 12px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #FFB6C1;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background: transparent;
            }
        """)
        login_layout = QVBoxLayout()
        
        # 邮箱
        email_layout = QHBoxLayout()
        email_label = QLabel(self.tr("email", "邮箱:"))
        email_label.setFixedWidth(80)
        email_label.setStyleSheet("color: #666; background: transparent;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText(self.tr("email_placeholder", "your@email.com"))
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        login_layout.addLayout(email_layout)
        
        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel(self.tr("password", "密码:"))
        password_label.setFixedWidth(80)
        password_label.setStyleSheet("color: #666; background: transparent;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(self.tr("password_placeholder", "密码"))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        login_layout.addLayout(password_layout)
        
        login_group.setLayout(login_layout)
        layout.addWidget(login_group)
        
        # Token 显示
        token_group = QGroupBox(self.tr("current_token", "当前 Token"))
        token_group.setStyleSheet("""
            QGroupBox {
                background: rgba(255, 255, 255, 0.85);
                border: 2px solid rgba(255, 228, 225, 0.8);
                border-radius: 12px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #FFB6C1;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background: transparent;
            }
        """)
        token_layout = QVBoxLayout()
        
        self.token_display = QTextEdit()
        self.token_display.setReadOnly(False)  # 允许编辑，方便手动粘贴
        self.token_display.setMaximumHeight(100)
        self.token_display.setPlaceholderText(self.tr("token_placeholder", "Token 将显示在这里..."))
        
        # 从配置文件加载当前 token
        try:
            config_path = "pixiv_downloader/config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'refresh_token' in config:
                        self.token_display.setText(config['refresh_token'])
        except:
            pass
        
        token_layout.addWidget(self.token_display)
        
        # Token 操作按钮
        token_btn_layout = QHBoxLayout()
        
        copy_btn = QPushButton(self.tr("copy", "📋 复制"))
        copy_btn.clicked.connect(self.copy_token)
        copy_btn.setFixedHeight(40)
        copy_btn.setStyleSheet("color: #333;")  # 黑色文字
        token_btn_layout.addWidget(copy_btn)
        
        save_btn = QPushButton(self.tr("save_to_config", "💾 保存到配置"))
        save_btn.clicked.connect(self.save_token_to_config)
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet("color: #333;")  # 黑色文字
        token_btn_layout.addWidget(save_btn)
        
        token_layout.addLayout(token_btn_layout)
        token_group.setLayout(token_layout)
        layout.addWidget(token_group)
        
        layout.addStretch()
        
        # 获取按钮
        self.get_token_btn = QPushButton(self.tr("get_token", "🔑 获取 Token"))
        self.get_token_btn.setFixedHeight(50)
        self.get_token_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.get_token_btn.setStyleSheet("color: #333;")  # 黑色文字
        self.get_token_btn.clicked.connect(self.get_token)
        layout.addWidget(self.get_token_btn)
        
        # 状态标签
        self.token_status = QLabel(self.tr("ready", "就绪"))
        self.token_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.token_status.setStyleSheet("""
            background: rgba(255, 255, 255, 0.9);
            color: #FFB6C1;
            padding: 8px;
            border-radius: 8px;
            font-size: 12px;
        """)
        layout.addWidget(self.token_status)
        
        return widget
    
    def create_settings_tab(self):
        """创建设置标签页"""
        widget = QWidget()
        widget.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 设置组
        settings_group = self.create_settings_group()
        layout.addWidget(settings_group)
        
        # 关于
        about_group = QGroupBox(self.tr("about", "关于"))
        about_group.setStyleSheet("""
            QGroupBox {
                background: rgba(255, 255, 255, 0.85);
                border: 2px solid rgba(255, 228, 225, 0.8);
                border-radius: 12px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #FFB6C1;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background: transparent;
            }
        """)
        about_layout = QVBoxLayout()
        
        about_text = QLabel(self.tr("about_text",
            "Pixiv 下载器 + 图片审核工具\n\n"
            "版本: 2.0.0\n\n"
            "功能:\n"
            "• 从 Pixiv 批量下载图片\n"
            "• AI 驱动的图片内容审核\n"
            "• 自动分类管理\n"
            "• 使用 gppt 库获取 Token\n\n"
            "目录结构:\n"
            "• picture/ - 合格图片\n"
            "• ban/ - 被过滤图片\n"
            "• history/ - 下载历史\n\n"
            "依赖库:\n"
            "• pixivpy3 - Pixiv API\n"
            "• gppt - Token 获取\n"
            "• nudenet - 图片审核"
        ))
        about_text.setWordWrap(True)
        about_text.setStyleSheet("background: transparent; color: #666;")
        about_layout.addWidget(about_text)
        
        about_group.setLayout(about_layout)
        layout.addWidget(about_group)
        
        layout.addStretch()
        
        return widget
    
    def create_download_group(self):
        """创建下载设置组"""
        group = QGroupBox(self.tr("download_settings", "📥 下载设置"))
        group.setStyleSheet("""
            QGroupBox {
                background: rgba(255, 255, 255, 0.85);
                border: 2px solid rgba(255, 228, 225, 0.8);
                border-radius: 12px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #FFB6C1;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background: transparent;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # 关键词
        keyword_layout = QHBoxLayout()
        keyword_label = QLabel(self.tr("search_keyword", "搜索关键词:"))
        keyword_label.setFixedWidth(100)
        keyword_label.setStyleSheet("color: #666; background: transparent;")
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText(self.tr("keyword_placeholder", "例如: 小萝莉"))
        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.keyword_input)
        layout.addLayout(keyword_layout)
        
        # 下载数量和最小收藏数
        numbers_layout = QHBoxLayout()
        
        count_label = QLabel(self.tr("download_count", "下载数量:"))
        count_label.setFixedWidth(100)
        count_label.setStyleSheet("color: #666; background: transparent;")
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 1000)
        self.count_spin.setValue(20)
        self.count_spin.setFixedWidth(100)
        
        bookmark_label = QLabel(self.tr("min_bookmarks", "最小收藏:"))
        bookmark_label.setStyleSheet("color: #666; background: transparent; margin-left: 20px;")
        self.bookmark_spin = QSpinBox()
        self.bookmark_spin.setRange(0, 100000)
        self.bookmark_spin.setValue(0)
        self.bookmark_spin.setFixedWidth(100)
        
        numbers_layout.addWidget(count_label)
        numbers_layout.addWidget(self.count_spin)
        numbers_layout.addWidget(bookmark_label)
        numbers_layout.addWidget(self.bookmark_spin)
        numbers_layout.addStretch()
        layout.addLayout(numbers_layout)
        
        # 跳过 R-18
        self.skip_r18_check = QCheckBox(self.tr("skip_r18", "跳过 R-18 内容"))
        self.skip_r18_check.setStyleSheet("color: #666; background: transparent;")
        layout.addWidget(self.skip_r18_check)
        
        # 去除 AI 作品
        self.skip_ai_check = QCheckBox(self.tr("skip_ai", "去除 AI 作品"))
        self.skip_ai_check.setStyleSheet("color: #666; background: transparent;")
        layout.addWidget(self.skip_ai_check)
        
        group.setLayout(layout)
        return group
    
    def create_moderate_group(self):
        """创建审核设置组"""
        group = QGroupBox(self.tr("moderate_settings", "🔍 审核设置"))
        group.setStyleSheet("""
            QGroupBox {
                background: rgba(255, 255, 255, 0.85);
                border: 2px solid rgba(255, 228, 225, 0.8);
                border-radius: 12px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #FFB6C1;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background: transparent;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # 启用审核开关
        self.enable_moderate_check = QCheckBox(self.tr("enable_moderate", "启用图片审核（下载完成后自动审核）"))
        self.enable_moderate_check.setChecked(True)
        self.enable_moderate_check.setStyleSheet("color: #666; background: transparent; font-weight: bold;")
        self.enable_moderate_check.toggled.connect(self.toggle_moderate_options)
        layout.addWidget(self.enable_moderate_check)
        
        # 审核选项容器
        self.moderate_options = QWidget()
        moderate_options_layout = QVBoxLayout(self.moderate_options)
        moderate_options_layout.setContentsMargins(20, 10, 0, 0)
        moderate_options_layout.setSpacing(12)
        
        # 阈值
        threshold_layout = QHBoxLayout()
        threshold_label = QLabel(self.tr("detection_threshold", "检测阈值:"))
        threshold_label.setFixedWidth(80)
        threshold_label.setStyleSheet("color: #666; background: transparent;")
        self.threshold_combo = QComboBox()
        self.threshold_combo.addItems([
            "0.4 - 非常严格",
            "0.5 - 严格",
            "0.6 - 默认",
            "0.7 - 宽松",
            "0.8 - 非常宽松"
        ])
        self.threshold_combo.setCurrentIndex(0)  # 默认选择"0.4 - 非常严格"
        threshold_layout.addWidget(threshold_label)
        threshold_layout.addWidget(self.threshold_combo)
        threshold_layout.addStretch()
        moderate_options_layout.addLayout(threshold_layout)
        
        # 删除选项
        self.delete_filtered_check = QCheckBox(self.tr("move_to_ban", "将不合格图片移动到 ban 目录"))
        self.delete_filtered_check.setChecked(True)
        self.delete_filtered_check.setStyleSheet("color: #666; background: transparent;")
        moderate_options_layout.addWidget(self.delete_filtered_check)
        
        layout.addWidget(self.moderate_options)
        
        group.setLayout(layout)
        return group
    
    def create_settings_group(self):
        """创建设置组"""
        group = QGroupBox(self.tr("settings", "⚙️ 设置"))
        group.setStyleSheet("""
            QGroupBox {
                background: rgba(255, 255, 255, 0.85);
                border: 2px solid rgba(255, 228, 225, 0.8);
                border-radius: 12px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #FFB6C1;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background: transparent;
            }
        """)
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 主题色设置
        theme_layout = QHBoxLayout()
        theme_label = QLabel(self.tr("theme_color", "主题色:"))
        theme_label.setFixedWidth(80)
        theme_label.setStyleSheet("color: #666; background: transparent; font-weight: bold;")
        
        # 当前颜色显示
        self.color_preview = QPushButton()
        self.color_preview.setFixedSize(40, 40)
        self.color_preview.setStyleSheet(f"""
            QPushButton {{
                background: {self.get_current_color()};
                border: 2px solid #999;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                border: 3px solid #666;
            }}
        """)
        
        # 选择颜色按钮
        choose_color_btn = QPushButton(self.tr("choose_color", "选择颜色"))
        choose_color_btn.clicked.connect(self.choose_theme_color)
        choose_color_btn.setFixedHeight(40)
        choose_color_btn.setStyleSheet("""
            QPushButton {
                color: #333;
            }
        """)
        
        # 预设颜色按钮
        preset_colors_label = QLabel(self.tr("preset_colors", "预设:"))
        preset_colors_label.setStyleSheet("color: #666; background: transparent; margin-left: 20px;")
        
        pink_preset = QPushButton("🌸")
        pink_preset.setFixedSize(40, 40)
        pink_preset.setStyleSheet("background: rgb(255, 182, 193); color: white; border: 2px solid #999; border-radius: 8px; font-size: 18px;")
        pink_preset.clicked.connect(lambda: self.set_preset_color(255, 182, 193))
        
        blue_preset = QPushButton("💙")
        blue_preset.setFixedSize(40, 40)
        blue_preset.setStyleSheet("background: rgb(135, 206, 250); color: white; border: 2px solid #999; border-radius: 8px; font-size: 18px;")
        blue_preset.clicked.connect(lambda: self.set_preset_color(135, 206, 250))
        
        purple_preset = QPushButton("💜")
        purple_preset.setFixedSize(40, 40)
        purple_preset.setStyleSheet("background: rgb(186, 148, 255); color: white; border: 2px solid #999; border-radius: 8px; font-size: 18px;")
        purple_preset.clicked.connect(lambda: self.set_preset_color(186, 148, 255))
        
        green_preset = QPushButton("💚")
        green_preset.setFixedSize(40, 40)
        green_preset.setStyleSheet("background: rgb(144, 238, 144); color: white; border: 2px solid #999; border-radius: 8px; font-size: 18px;")
        green_preset.clicked.connect(lambda: self.set_preset_color(144, 238, 144))
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.color_preview)
        theme_layout.addWidget(choose_color_btn)
        theme_layout.addWidget(preset_colors_label)
        theme_layout.addWidget(pink_preset)
        theme_layout.addWidget(blue_preset)
        theme_layout.addWidget(purple_preset)
        theme_layout.addWidget(green_preset)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # 语言设置
        lang_layout = QHBoxLayout()
        lang_label = QLabel(self.tr("language", "语言:"))
        lang_label.setFixedWidth(80)
        lang_label.setStyleSheet("color: #666; background: transparent; font-weight: bold;")
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("🇨🇳 中文", "zh_CN")
        self.language_combo.addItem("🇯🇵 日本語", "ja_JP")
        self.language_combo.addItem("🇰🇷 한국어", "ko_KR")
        self.language_combo.addItem("🇺🇸 English", "en_US")
        self.language_combo.addItem("🇫🇷 Français", "fr_FR")
        self.language_combo.addItem("🇩🇪 Deutsch", "de_DE")
        
        # 设置当前语言
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == self.current_language:
                self.language_combo.setCurrentIndex(i)
                break
        
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.language_combo.setFixedHeight(40)
        
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # 目录设置
        folder_layout = QHBoxLayout()
        folder_label = QLabel(self.tr("download_dir", "下载目录:"))
        folder_label.setFixedWidth(80)
        folder_label.setStyleSheet("color: #666; background: transparent;")
        
        open_folder_btn = QPushButton(self.tr("open_folder", "打开下载目录"))
        open_folder_btn.clicked.connect(self.open_download_folder)
        open_folder_btn.setFixedHeight(40)
        open_folder_btn.setStyleSheet("""
            QPushButton {
                color: #333;
            }
        """)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(open_folder_btn)
        folder_layout.addStretch()
        layout.addLayout(folder_layout)
        
        group.setLayout(layout)
        return group
    
    def toggle_moderate_options(self, checked):
        """切换审核选项的可见性"""
        self.moderate_options.setVisible(checked)
    
    def apply_styles(self):
        """应用全局样式 - 支持自定义RGB颜色"""
        colors = self.get_theme_colors()
        
        # 更新标题栏颜色
        title_bar = self.findChild(QWidget, "titleBar")
        if title_bar:
            title_bar.setStyleSheet(f"""
                QWidget#titleBar {{
                    background: {colors['primary']};
                    border-top-left-radius: 15px;
                    border-top-right-radius: 15px;
                }}
            """)
        
        # 更新背景颜色
        if hasattr(self, 'background_widget'):
            self.background_widget.set_theme_color(self.theme_color)
        
        # 更新开始按钮样式（白底黑字，主题色边框）
        if hasattr(self, 'start_btn'):
            self.start_btn.setStyleSheet(f"""
                QPushButton {{
                    background: white;
                    color: #333;
                    border: 2px solid {colors['primary']};
                    border-radius: 10px;
                    padding: 10px 20px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {colors['primary_light']};
                    color: #333;
                    border: 2px solid {colors['primary']};
                }}
                QPushButton:pressed {{
                    background: {colors['primary']};
                    color: white;
                    border: 2px solid {colors['primary']};
                }}
                QPushButton:disabled {{
                    background: #F5F5F5;
                    color: #999;
                    border: 2px solid #DDD;
                }}
            """)
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {colors['background']};
            }}
            QLineEdit, QSpinBox, QComboBox {{
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #333;
            }}
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border: 2px solid {colors['primary']};
                background: rgba(255, 255, 255, 0.95);
            }}
            QPushButton {{
                background: {colors['primary']};
                color: white;
                border: 2px solid {colors['primary_pressed']};
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {colors['primary_hover']};
                color: white;
                border: 2px solid {colors['primary_pressed']};
            }}
            QPushButton:pressed {{
                background: {colors['primary_pressed']};
                color: white;
                border: 2px solid {colors['primary_pressed']};
            }}
            QPushButton:disabled {{
                background: rgba(200, 200, 200, 0.7);
                color: #999;
                border: 2px solid rgba(180, 180, 180, 0.7);
            }}
            QTextEdit {{
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid {colors['border']};
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
                color: #333;
                font-family: Consolas, monospace;
            }}
            QProgressBar {{
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid {colors['border']};
                border-radius: 12px;
                text-align: center;
                color: {colors['primary']};
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {colors['gradient_start']},
                    stop:1 {colors['gradient_end']});
                border-radius: 10px;
            }}
            QCheckBox {{
                color: #666;
                font-size: 13px;
                spacing: 8px;
                background: transparent;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {colors['border']};
                border-radius: 4px;
                background: rgba(255, 255, 255, 0.9);
            }}
            QCheckBox::indicator:checked {{
                background: {colors['primary']};
                border: 2px solid {colors['primary']};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {colors['primary']};
            }}
            QRadioButton {{
                color: #666;
                font-size: 13px;
                spacing: 8px;
                background: transparent;
            }}
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {colors['border']};
                border-radius: 9px;
                background: rgba(255, 255, 255, 0.9);
            }}
            QRadioButton::indicator:checked {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5,
                    stop:0 white,
                    stop:0.5 white,
                    stop:0.51 {colors['primary']},
                    stop:1 {colors['primary']});
                border: 2px solid {colors['primary']};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {colors['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors['primary']};
                margin-right: 5px;
            }}
            QComboBox QAbstractItemView {{
                background: white;
                color: #333;
                font-size: 13px;
                selection-background-color: {colors['primary_light']};
                selection-color: white;
                border: none;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                min-height: 35px;
                border: none;
                background: white;
                color: #333;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: {colors['primary_light']};
                color: white;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background: {colors['primary']};
                color: white;
            }}
            QLabel {{
                color: #666;
                font-size: 13px;
                background: transparent;
            }}
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: #F5F5F5;
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['scrollbar']};
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['primary']};
            }}
            QGroupBox {{
                background: rgba(255, 255, 255, 0.85);
                border: 2px solid {colors['border']};
                border-radius: 12px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: {colors['primary']};
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                background: transparent;
            }}
            QTabWidget::pane {{
                border: 2px solid {colors['border']};
                border-radius: 12px;
                background: transparent;
                top: -2px;
            }}
            QTabBar::tab {{
                background: rgba(255, 255, 255, 0.7);
                color: #666;
                padding: 10px 20px;
                margin-right: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border: 2px solid {colors['border']};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background: {colors['primary']};
                color: white;
                font-weight: bold;
                border: 2px solid {colors['primary']};
                border-bottom: none;
            }}
            QTabBar::tab:hover {{
                background: {colors['primary_light']};
                color: white;
            }}
        """)
        
        # 更新标题栏颜色
        title_bar = self.findChild(QWidget, "titleBar")
        if title_bar:
            title_bar.setStyleSheet(f"""
                QWidget#titleBar {{
                    background: {colors['primary']};
                    border-top-left-radius: 15px;
                    border-top-right-radius: 15px;
                }}
            """)
    
    def start_work(self):
        """开始工作"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索关键词！")
            return
        
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.log_text.clear()
        self.log_text.append("=" * 50)
        self.log_text.append(f"[任务] 开始新任务")
        self.log_text.append(f"[任务] 搜索关键词: {keyword}")
        self.log_text.append(f"[任务] 下载数量: {self.count_spin.value()}")
        self.log_text.append(f"[任务] 最小收藏: {self.bookmark_spin.value()}")
        self.log_text.append("=" * 50)
        self.status_label.setText(f"准备开始: {keyword}")
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        self.progress_bar.setFormat("处理中...")
        
        # 获取阈值
        threshold = 0.4  # 默认使用非常严格模式
        if self.enable_moderate_check.isChecked():
            threshold_text = self.threshold_combo.currentText()
            threshold = float(threshold_text.split()[0])
        
        # 创建工作线程
        self.work_thread = WorkThread(
            query=keyword,
            max_count=self.count_spin.value(),
            min_bookmarks=self.bookmark_spin.value(),
            skip_r18=self.skip_r18_check.isChecked(),
            skip_ai=self.skip_ai_check.isChecked(),
            enable_moderate=self.enable_moderate_check.isChecked(),
            threshold=threshold,
            delete_filtered=self.delete_filtered_check.isChecked()
        )
        self.work_thread.progress.connect(self.on_progress)
        self.work_thread.finished.connect(self.on_finished)
        self.work_thread.start()
    
    def toggle_pause(self):
        """切换暂停/继续状态"""
        if not hasattr(self, 'work_thread') or not self.work_thread.isRunning():
            return
        
        if self.work_thread._is_paused:
            # 当前是暂停状态，点击后继续
            self.work_thread.resume()
            self.pause_btn.setText(self.tr("pause_execution", "⏸️ 暂停"))
            self.log_text.append("[控制] 继续执行任务...")
            self.progress_bar.setFormat("处理中...")
        else:
            # 当前是运行状态，点击后暂停
            self.work_thread.pause()
            self.pause_btn.setText(self.tr("resume_execution", "▶️ 继续"))
            self.log_text.append("[控制] 任务已暂停")
            self.progress_bar.setFormat("已暂停")
    
    def stop_work(self):
        """停止工作"""
        if not hasattr(self, 'work_thread') or not self.work_thread.isRunning():
            return
        
        reply = QMessageBox.question(
            self,
            "确认停止",
            "确定要停止当前任务吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.work_thread.stop()
            self.log_text.append("[控制] 正在停止任务，请稍候...")
            self.progress_bar.setFormat("正在停止...")
    
    def on_progress(self, message):
        """进度更新"""
        self.status_label.setText(message)
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_finished(self, success, message):
        """任务完成"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText(self.tr("pause_execution", "⏸️ 暂停"))
        self.stop_btn.setEnabled(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if success else 0)
        self.progress_bar.setFormat("完成" if success else "失败")
        self.status_label.setText(message.replace('\n', ' '))
        self.log_text.append("=" * 50)
        if success:
            self.log_text.append("[完成] 任务执行成功")
        else:
            self.log_text.append("[失败] 任务执行失败")
        self.log_text.append(message)
        self.log_text.append("=" * 50)
        
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.critical(self, "失败", message)
    
    def change_background(self):
        """更换背景"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择背景图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if file_path:
            self.background_widget.load_background(file_path)
            self.background_widget.update()
            QMessageBox.information(self, "成功", "背景已更换！")
    
    def reset_background(self):
        """恢复默认背景"""
        self.background_widget.load_background()
        self.background_widget.update()
        QMessageBox.information(self, "成功", "已恢复默认背景！")
    
    def open_download_folder(self):
        """打开下载目录"""
        download_dir = Path("downloads")
        if download_dir.exists():
            os.startfile(str(download_dir)) if sys.platform == "win32" else os.system(f'open "{download_dir}"')
        else:
            QMessageBox.information(self, "提示", "下载目录还不存在")
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动窗口"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 只在标题栏区域允许拖动（前50像素）
            if event.position().y() < 50:
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.drag_position = None
    
    def tr(self, key, default=""):
        """翻译方法"""
        return TRANSLATIONS.get(self.current_language, {}).get(key, default)
    
    def get_current_color(self):
        """获取当前主题色的RGB字符串"""
        r, g, b = self.theme_color
        return f"rgb({r}, {g}, {b})"
    
    def get_theme_colors(self):
        """获取主题颜色（基于当前RGB值）"""
        r, g, b = self.theme_color
        
        # 计算不同亮度的颜色变体
        # 主色
        primary = f"rgb({r}, {g}, {b})"
        
        # 悬停色（稍微亮一些）
        r_hover = min(255, int(r * 1.1))
        g_hover = min(255, int(g * 1.1))
        b_hover = min(255, int(b * 1.1))
        primary_hover = f"rgb({r_hover}, {g_hover}, {b_hover})"
        
        # 按下色（稍微暗一些）
        r_pressed = int(r * 0.9)
        g_pressed = int(g * 0.9)
        b_pressed = int(b * 0.9)
        primary_pressed = f"rgb({r_pressed}, {g_pressed}, {b_pressed})"
        
        # 浅色版本（用于选中项背景）
        r_light = min(255, int(r + (255 - r) * 0.3))
        g_light = min(255, int(g + (255 - g) * 0.3))
        b_light = min(255, int(b + (255 - b) * 0.3))
        primary_light = f"rgb({r_light}, {g_light}, {b_light})"
        
        # 边框色（更浅）
        r_border = min(255, int(r + (255 - r) * 0.5))
        g_border = min(255, int(g + (255 - g) * 0.5))
        b_border = min(255, int(b + (255 - b) * 0.5))
        border = f"rgba({r_border}, {g_border}, {b_border}, 0.8)"
        
        # 滚动条色
        r_scroll = min(255, int(r + (255 - r) * 0.4))
        g_scroll = min(255, int(g + (255 - g) * 0.4))
        b_scroll = min(255, int(b + (255 - b) * 0.4))
        scrollbar = f"rgb({r_scroll}, {g_scroll}, {b_scroll})"
        
        # 背景色（非常淡的主题色，90%白色 + 10%主题色）
        r_bg = int(r * 0.1 + 255 * 0.9)
        g_bg = int(g * 0.1 + 255 * 0.9)
        b_bg = int(b * 0.1 + 255 * 0.9)
        background = f"rgb({r_bg}, {g_bg}, {b_bg})"
        
        # 渐变色
        gradient_start = primary
        gradient_end = primary_light
        
        return {
            "primary": primary,
            "primary_hover": primary_hover,
            "primary_pressed": primary_pressed,
            "primary_light": primary_light,
            "border": border,
            "scrollbar": scrollbar,
            "background": background,
            "gradient_start": gradient_start,
            "gradient_end": gradient_end,
        }
    
    def choose_theme_color(self):
        """打开颜色选择器"""
        current_color = QColor(*self.theme_color)
        color = QColorDialog.getColor(current_color, self, "选择主题色")
        
        if color.isValid():
            self.theme_color = (color.red(), color.green(), color.blue())
            self.save_config()  # 保存配置
            self.apply_styles()
            # 更新颜色预览
            self.color_preview.setStyleSheet(f"""
                QPushButton {{
                    background: {self.get_current_color()};
                    border: 2px solid #999;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    border: 3px solid #666;
                }}
            """)
            QMessageBox.information(self, "成功", "主题色已更新！")
    
    def set_preset_color(self, r, g, b):
        """设置预设颜色"""
        self.theme_color = (r, g, b)
        self.save_config()  # 保存配置
        self.apply_styles()
        # 更新颜色预览
        self.color_preview.setStyleSheet(f"""
            QPushButton {{
                background: {self.get_current_color()};
                border: 2px solid #999;
                border-radius: 8px;
            }}
        """)
        QMessageBox.information(self, "成功", "主题色已更新！")
    
    def on_language_changed(self, index):
        """语言改变时触发"""
        new_language = self.language_combo.itemData(index)
        if new_language != self.current_language:
            self.current_language = new_language
            self.save_config()  # 保存配置
            
            # 提示用户即将重启
            reply = QMessageBox.question(
                self,
                "重启应用",
                "语言已更改，需要重启应用才能生效。\n\n是否立即重启？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.restart_application()
            else:
                # 恢复原来的选择
                for i in range(self.language_combo.count()):
                    if self.language_combo.itemData(i) == self.current_language:
                        self.language_combo.blockSignals(True)
                        self.language_combo.setCurrentIndex(i)
                        self.language_combo.blockSignals(False)
                        break
    
    def restart_application(self):
        """重启应用"""
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)
    
    def get_token(self):
        """获取 Token"""
        if not GPPT_AVAILABLE:
            QMessageBox.critical(self, "错误", "gppt 库未安装！\n\n请运行: pip install gppt")
            return
        
        # 获取邮箱和密码
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "提示", "请输入邮箱和密码！")
            return
        
        # 禁用按钮
        self.get_token_btn.setEnabled(False)
        self.token_status.setText("正在启动命令行...")
        
        # 构建命令
        command = f'gppt login -u "{email}" -p "{password}"'
        
        try:
            # 在 Windows 上打开新的 PowerShell 窗口并运行命令
            import subprocess
            
            # 创建一个临时脚本来捕获输出
            script_content = f'''
$output = {command} 2>&1
Write-Host "========================================"
Write-Host "Token Get Complete!"
Write-Host "========================================"
Write-Host ""
Write-Host "Please copy the refresh_token below:"
Write-Host ""
$output | Select-String -Pattern "refresh_token" | ForEach-Object {{
    $line = $_.Line
    if ($line -match 'refresh_token') {{
        $parts = $line -split '[:=]'
        if ($parts.Length -gt 1) {{
            $token = $parts[1].Trim() -replace '[",\\s}}]', ''
            Write-Host $token
            Set-Clipboard -Value $token
            Write-Host ""
            Write-Host "Token has been copied to clipboard!"
        }}
    }}
}}
Write-Host ""
Write-Host "Please return to GUI and paste the Token."
Write-Host ""
Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
'''
            
            # 保存临时脚本（使用 UTF-8 BOM 编码）
            script_path = "temp_get_token.ps1"
            with open(script_path, 'w', encoding='utf-8-sig') as f:
                f.write(script_content)
            
            # 启动 PowerShell 窗口
            subprocess.Popen([
                'powershell.exe',
                '-NoExit',
                '-ExecutionPolicy', 'Bypass',
                '-File', script_path
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # 显示提示
            self.token_status.setText("命令行窗口已打开，请等待...")
            
            QMessageBox.information(
                self,
                "提示",
                "命令行窗口已打开！\n\n"
                "请等待登录完成：\n"
                "1. Token 会自动复制到剪贴板\n"
                "2. 返回此窗口\n"
                "3. 在 Token 显示框中粘贴（Ctrl+V）\n"
                "4. 点击「保存到配置」\n\n"
                "如果自动复制失败，请手动复制命令行中显示的 Token。"
            )
            
            # 重新启用按钮
            self.get_token_btn.setEnabled(True)
            self.token_status.setText("等待粘贴 Token...")
            
        except Exception as e:
            self.get_token_btn.setEnabled(True)
            self.token_status.setText("启动失败")
            QMessageBox.critical(
                self,
                "错误",
                f"无法启动命令行窗口！\n\n"
                f"错误信息：{str(e)}\n\n"
                f"请手动在命令行中运行：\n"
                f'gppt login -u "{email}" -p "{password}"'
            )
    
    def copy_token(self):
        """复制 Token"""
        token = self.token_display.toPlainText().strip()
        if token:
            QApplication.clipboard().setText(token)
            QMessageBox.information(self, "成功", "Token 已复制到剪贴板！")
        else:
            QMessageBox.warning(self, "提示", "没有可复制的 Token！")
    
    def save_token_to_config(self):
        """保存 Token 到配置文件"""
        token = self.token_display.toPlainText().strip()
        if not token:
            QMessageBox.warning(self, "提示", "没有可保存的 Token！")
            return
        
        try:
            config_path = "pixiv_downloader/config.json"
            
            # 确保目录存在
            os.makedirs("pixiv_downloader", exist_ok=True)
            
            # 读取现有配置
            config = {}
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            # 更新 token
            config['refresh_token'] = token
            
            # 保存配置
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", "Token 已保存到配置文件！\n\n现在可以使用下载功能了。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序字体 - 使用更通用的字体
    try:
        font = QFont("Microsoft YaHei", 10)
        if not font.exactMatch():
            font = QFont("Arial", 10)
        app.setFont(font)
    except:
        pass
    
    # 环境检测（仅在开发模式下启用）
    # 打包后的 exe 已包含所有依赖，无需检测
    if not getattr(sys, 'frozen', False):
        # 仅在非打包环境下进行环境检测
        try:
            from environment_checker import EnvironmentChecker
            checker = EnvironmentChecker()
            
            # 检查是否需要进行环境检测
            if not checker.config.get('environment_checked'):
                # 显示环境检测对话框
                from environment_dialog import EnvironmentDialog
                dialog = EnvironmentDialog()
                result = dialog.exec()
                
                # 如果环境设置失败，询问是否继续
                if not checker.config.get('environment_checked'):
                    from PyQt6.QtWidgets import QMessageBox
                    reply = QMessageBox.question(
                        None,
                        "环境设置",
                        "环境设置未完成，是否仍要继续启动？\n\n"
                        "注意：部分功能可能无法正常使用。",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return
        except Exception as e:
            print(f"环境检测跳过: {e}")
    
    # 创建主窗口
    window = PixivDownloaderGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
