#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pixiv 下载器 + 图片审核工具 - GUI 版本
简洁的淡粉色+白色配色，圆角边框，支持自定义背景
"""

import sys
import os
import json
import time
import threading
import queue
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QCheckBox, QTextEdit,
    QProgressBar, QFileDialog, QMessageBox, QGroupBox,
    QComboBox, QFrame, QScrollArea, QTabWidget, QRadioButton, QButtonGroup,
    QColorDialog, QSystemTrayIcon, QGridLayout
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
        "open_folder": "打开",
        "theme_changed": "主题已切换！",
        "language_changed": "语言已切换！\n\n重启应用后生效。",
        # 下载与过滤
        "download_settings": "📥 下载设置",
        "download_mode": "下载模式:",
        "mode_search": "关键词搜索",
        "mode_bookmarks": "我的收藏夹",
        "search_keyword": "搜索关键词:",
        "keyword_placeholder": "例如: 小萝莉",
        "download_count": "下载数量:",
        "min_bookmarks": "最小收藏:",
        "skip_r18": "跳过 R-18 内容",
        "skip_ai": "去除 AI 作品",
        "skip_ugoira": "跳过动图",
        "only_ugoira": "只下载动图",
        "moderate_settings": "🔍 审核设置",
        "enable_moderate": "启用图片审核（下载完成后自动审核）",
        "detection_threshold": "检测阈值:",
        "filter_tags": "过滤标签:",
        "advanced_filter": "高级过滤选项",
        "custom_tags_hint": "自定义过滤标签（用逗号分隔）",
        "default_tags": "默认: penis, sex",
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
        "developer": "开发: mamajunya",
        "star_request": "如果喜欢请给点一个 Star ⭐",
        "change_folder": "更改目录",
        "select_folder": "选择下载目录",
        "transfer_data": "转移数据",
        "transfer_data_msg": "检测到原目录中有数据，是否转移到新目录？",
        "transfer_failed": "数据转移失败",
        "folder_changed": "下载目录已更改",
        "success": "成功",
        "error": "错误",
        "warning": "警告",
        "show_window": "显示窗口",
        "quit": "退出",
        "close_window": "关闭窗口",
        "close_window_msg": "您想要？",
        "exit_app": "完全退出",
        "minimize_to_tray": "最小化到托盘",
        "cancel": "取消",
        "remember_choice": "记住我的选择",
        "minimized_to_tray": "已最小化到系统托盘",
        "close_behavior": "关闭行为:",
        "ask_on_close": "每次询问",
        "exit_directly": "直接退出",
        "minimize_to_tray_option": "最小化到托盘",
        "close_behavior_changed": "关闭行为已更改",
        "download_threads": "下载线程数:",
        "download_threads_hint": "同时下载的作品数量（1-10）",
        "ugoira_format": "动图格式:",
        "ugoira_format_hint": "动图自动转换格式",
        "enable_debug_log": "启用调试日志",
        "debug_log_hint": "记录详细的审核过程和数值",
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
        "open_folder": "開く",
        "theme_changed": "テーマが変更されました！",
        "language_changed": "言語が変更されました！\n\nアプリを再起動してください。",
        "download_settings": "📥 ダウンロード設定",
        "download_mode": "ダウンロードモード:",
        "mode_search": "キーワード検索",
        "mode_bookmarks": "マイブックマーク",
        "search_keyword": "検索キーワード:",
        "keyword_placeholder": "例: 小さなロリ",
        "download_count": "ダウンロード数:",
        "min_bookmarks": "最小ブックマーク:",
        "skip_r18": "R-18 コンテンツをスキップ",
        "skip_ai": "AI 作品を除外",
        "skip_ugoira": "動画をスキップ",
        "only_ugoira": "動画のみダウンロード",
        "moderate_settings": "🔍 審査設定",
        "enable_moderate": "画像審査を有効にする（ダウンロード後に自動審査）",
        "detection_threshold": "検出しきい値:",
        "filter_tags": "フィルタータグ:",
        "advanced_filter": "高度なフィルターオプション",
        "custom_tags_hint": "カスタムフィルタータグ（カンマ区切り）",
        "default_tags": "デフォルト: penis, sex",
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
        "developer": "開発者: mamajunya",
        "star_request": "気に入ったら Star ⭐ をお願いします",
        "change_folder": "フォルダ変更",
        "select_folder": "ダウンロードフォルダを選択",
        "transfer_data": "データ転送",
        "transfer_data_msg": "元のフォルダにデータが検出されました。新しいフォルダに転送しますか？",
        "transfer_failed": "データ転送に失敗しました",
        "folder_changed": "ダウンロードフォルダが変更されました",
        "success": "成功",
        "error": "エラー",
        "warning": "警告",
        "show_window": "ウィンドウを表示",
        "quit": "終了",
        "close_window": "ウィンドウを閉じる",
        "close_window_msg": "どうしますか？",
        "exit_app": "完全に終了",
        "minimize_to_tray": "トレイに最小化",
        "cancel": "キャンセル",
        "remember_choice": "選択を記憶する",
        "minimized_to_tray": "システムトレイに最小化されました",
        "close_behavior": "閉じる動作:",
        "ask_on_close": "毎回確認",
        "exit_directly": "直接終了",
        "minimize_to_tray_option": "トレイに最小化",
        "close_behavior_changed": "閉じる動作が変更されました",
        "download_threads": "ダウンロードスレッド数:",
        "download_threads_hint": "同時にダウンロードする作品数（1-10）",
        "ugoira_format": "動画形式:",
        "ugoira_format_hint": "動画自動変換形式",
        "enable_debug_log": "デバッグログを有効化",
        "debug_log_hint": "詳細な審査プロセスと数値を記録",
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
        "open_folder": "열기",
        "theme_changed": "테마가 변경되었습니다！",
        "language_changed": "언어가 변경되었습니다！\n\n앱을 다시 시작하세요。",
        "download_settings": "📥 다운로드 설정",
        "download_mode": "다운로드 모드:",
        "mode_search": "키워드 검색",
        "mode_bookmarks": "내 북마크",
        "search_keyword": "검색 키워드:",
        "keyword_placeholder": "예: 꼬마 로리",
        "download_count": "다운로드 수:",
        "min_bookmarks": "최소 북마크:",
        "skip_r18": "R-18 콘텐츠 건너뛰기",
        "skip_ai": "AI 작품 제외",
        "skip_ugoira": "동영상 건너뛰기",
        "only_ugoira": "동영상만 다운로드",
        "moderate_settings": "🔍 심사 설정",
        "enable_moderate": "이미지 심사 활성화（다운로드 후 자동 심사）",
        "detection_threshold": "감지 임계값:",
        "filter_tags": "필터 태그:",
        "advanced_filter": "고급 필터 옵션",
        "custom_tags_hint": "사용자 정의 필터 태그（쉼표로 구분）",
        "default_tags": "기본값: penis, sex",
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
        "developer": "개발자: mamajunya",
        "star_request": "마음에 드시면 Star ⭐ 를 눌러주세요",
        "change_folder": "폴더 변경",
        "select_folder": "다운로드 폴더 선택",
        "transfer_data": "데이터 전송",
        "transfer_data_msg": "원본 폴더에 데이터가 감지되었습니다. 새 폴더로 전송하시겠습니까？",
        "transfer_failed": "데이터 전송 실패",
        "folder_changed": "다운로드 폴더가 변경되었습니다",
        "success": "성공",
        "error": "오류",
        "warning": "경고",
        "show_window": "창 표시",
        "quit": "종료",
        "close_window": "창 닫기",
        "close_window_msg": "어떻게 하시겠습니까?",
        "exit_app": "완전히 종료",
        "minimize_to_tray": "트레이로 최소화",
        "cancel": "취소",
        "remember_choice": "선택 기억",
        "minimized_to_tray": "시스템 트레이로 최소화되었습니다",
        "close_behavior": "닫기 동작:",
        "ask_on_close": "매번 확인",
        "exit_directly": "직접 종료",
        "minimize_to_tray_option": "트레이로 최소화",
        "close_behavior_changed": "닫기 동작이 변경되었습니다",
        "download_threads": "다운로드 스레드 수:",
        "download_threads_hint": "동시에 다운로드할 작품 수（1-10）",
        "ugoira_format": "동영상 형식:",
        "ugoira_format_hint": "동영상 자동 변환 형식",
        "enable_debug_log": "디버그 로그 활성화",
        "debug_log_hint": "상세한 심사 과정과 수치 기록",
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
        "open_folder": "Open",
        "theme_changed": "Theme changed!",
        "language_changed": "Language changed!\n\nPlease restart the app.",
        "download_settings": "📥 Download Settings",
        "download_mode": "Download Mode:",
        "mode_search": "Keyword Search",
        "mode_bookmarks": "My Bookmarks",
        "search_keyword": "Search Keyword:",
        "keyword_placeholder": "e.g.: loli",
        "download_count": "Download Count:",
        "min_bookmarks": "Min Bookmarks:",
        "skip_r18": "Skip R-18 Content",
        "skip_ai": "Skip AI Artworks",
        "skip_ugoira": "Skip Animations",
        "only_ugoira": "Only Animations",
        "moderate_settings": "🔍 Moderation Settings",
        "enable_moderate": "Enable Image Moderation (Auto-moderate after download)",
        "detection_threshold": "Detection Threshold:",
        "filter_tags": "Filter Tags:",
        "advanced_filter": "Advanced Filter Options",
        "custom_tags_hint": "Custom filter tags (comma-separated)",
        "default_tags": "Default: penis, sex",
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
        "developer": "Developer: mamajunya",
        "star_request": "If you like it, please give it a Star ⭐",
        "change_folder": "Change Folder",
        "select_folder": "Select Download Folder",
        "transfer_data": "Transfer Data",
        "transfer_data_msg": "Data detected in the original folder. Transfer to the new folder?",
        "transfer_failed": "Data transfer failed",
        "folder_changed": "Download folder changed",
        "success": "Success",
        "error": "Error",
        "warning": "Warning",
        "show_window": "Show Window",
        "quit": "Quit",
        "close_window": "Close Window",
        "close_window_msg": "What would you like to do?",
        "exit_app": "Exit Completely",
        "minimize_to_tray": "Minimize to Tray",
        "cancel": "Cancel",
        "remember_choice": "Remember my choice",
        "minimized_to_tray": "Minimized to system tray",
        "close_behavior": "Close Behavior:",
        "ask_on_close": "Ask every time",
        "exit_directly": "Exit directly",
        "minimize_to_tray_option": "Minimize to tray",
        "close_behavior_changed": "Close behavior changed",
        "download_threads": "Download Threads:",
        "download_threads_hint": "Number of concurrent downloads (1-10)",
        "ugoira_format": "Animation Format:",
        "ugoira_format_hint": "Auto-convert animation format",
        "enable_debug_log": "Enable Debug Log",
        "debug_log_hint": "Record detailed moderation process and values",
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
        "open_folder": "Ouvrir",
        "theme_changed": "Thème changé!",
        "language_changed": "Langue changée!\n\nVeuillez redémarrer l'application.",
        "download_settings": "📥 Paramètres de téléchargement",
        "download_mode": "Mode de téléchargement:",
        "mode_search": "Recherche par mot-clé",
        "mode_bookmarks": "Mes signets",
        "search_keyword": "Mot-clé de recherche:",
        "keyword_placeholder": "par ex.: loli",
        "download_count": "Nombre de téléchargements:",
        "min_bookmarks": "Signets minimum:",
        "skip_r18": "Ignorer le contenu R-18",
        "skip_ai": "Exclure les œuvres IA",
        "skip_ugoira": "Ignorer les animations",
        "only_ugoira": "Animations uniquement",
        "moderate_settings": "🔍 Paramètres de modération",
        "enable_moderate": "Activer la modération d'image (Modération automatique après téléchargement)",
        "detection_threshold": "Seuil de détection:",
        "filter_tags": "Tags de filtre:",
        "advanced_filter": "Options de filtre avancées",
        "custom_tags_hint": "Tags de filtre personnalisés (séparés par des virgules)",
        "default_tags": "Par défaut: penis, sex",
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
        "developer": "Développeur: mamajunya",
        "star_request": "Si vous l'aimez, donnez-lui une Star ⭐",
        "change_folder": "Changer le dossier",
        "select_folder": "Sélectionner le dossier de téléchargement",
        "transfer_data": "Transférer les données",
        "transfer_data_msg": "Données détectées dans le dossier d'origine. Transférer vers le nouveau dossier?",
        "transfer_failed": "Échec du transfert de données",
        "folder_changed": "Dossier de téléchargement modifié",
        "success": "Succès",
        "error": "Erreur",
        "warning": "Avertissement",
        "show_window": "Afficher la fenêtre",
        "quit": "Quitter",
        "close_window": "Fermer la fenêtre",
        "close_window_msg": "Que voulez-vous faire?",
        "exit_app": "Quitter complètement",
        "minimize_to_tray": "Réduire dans la barre",
        "cancel": "Annuler",
        "remember_choice": "Se souvenir de mon choix",
        "minimized_to_tray": "Réduit dans la barre système",
        "close_behavior": "Comportement de fermeture:",
        "ask_on_close": "Demander à chaque fois",
        "exit_directly": "Quitter directement",
        "minimize_to_tray_option": "Réduire dans la barre",
        "close_behavior_changed": "Comportement de fermeture modifié",
        "download_threads": "Threads de téléchargement:",
        "download_threads_hint": "Nombre de téléchargements simultanés (1-10)",
        "ugoira_format": "Format d'animation:",
        "ugoira_format_hint": "Format de conversion automatique",
        "enable_debug_log": "Activer le journal de débogage",
        "debug_log_hint": "Enregistrer le processus détaillé et les valeurs",
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
        "open_folder": "Öffnen",
        "theme_changed": "Thema geändert!",
        "language_changed": "Sprache geändert!\n\nBitte starten Sie die App neu.",
        "download_settings": "📥 Download-Einstellungen",
        "download_settings": "📥 Download-Einstellungen",
        "download_mode": "Download-Modus:",
        "mode_search": "Stichwortsuche",
        "mode_bookmarks": "Meine Lesezeichen",
        "search_keyword": "Suchbegriff:",
        "keyword_placeholder": "z.B.: loli",
        "download_count": "Download-Anzahl:",
        "min_bookmarks": "Min. Lesezeichen:",
        "skip_r18": "R-18-Inhalte überspringen",
        "skip_ai": "KI-Kunstwerke ausschließen",
        "skip_ugoira": "Animationen überspringen",
        "only_ugoira": "Nur Animationen",
        "moderate_settings": "🔍 Moderationseinstellungen",
        "enable_moderate": "Bildmoderation aktivieren (Automatische Moderation nach Download)",
        "detection_threshold": "Erkennungsschwelle:",
        "filter_tags": "Filter-Tags:",
        "advanced_filter": "Erweiterte Filteroptionen",
        "custom_tags_hint": "Benutzerdefinierte Filter-Tags (durch Kommas getrennt)",
        "default_tags": "Standard: penis, sex",
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
        "developer": "Entwickler: mamajunya",
        "star_request": "Wenn es Ihnen gefällt, geben Sie bitte einen Star ⭐",
        "change_folder": "Ordner ändern",
        "select_folder": "Download-Ordner auswählen",
        "transfer_data": "Daten übertragen",
        "transfer_data_msg": "Daten im ursprünglichen Ordner erkannt. In den neuen Ordner übertragen?",
        "transfer_failed": "Datenübertragung fehlgeschlagen",
        "folder_changed": "Download-Ordner geändert",
        "success": "Erfolg",
        "error": "Fehler",
        "warning": "Warnung",
        "show_window": "Fenster anzeigen",
        "quit": "Beenden",
        "close_window": "Fenster schließen",
        "close_window_msg": "Was möchten Sie tun?",
        "exit_app": "Vollständig beenden",
        "minimize_to_tray": "In Taskleiste minimieren",
        "cancel": "Abbrechen",
        "remember_choice": "Meine Wahl merken",
        "minimized_to_tray": "In Taskleiste minimiert",
        "close_behavior": "Schließverhalten:",
        "ask_on_close": "Jedes Mal fragen",
        "exit_directly": "Direkt beenden",
        "minimize_to_tray_option": "In Taskleiste minimieren",
        "close_behavior_changed": "Schließverhalten geändert",
        "download_threads": "Download-Threads:",
        "download_threads_hint": "Anzahl gleichzeitiger Downloads (1-10)",
        "ugoira_format": "Animationsformat:",
        "ugoira_format_hint": "Automatisches Konvertierungsformat",
        "enable_debug_log": "Debug-Protokoll aktivieren",
        "debug_log_hint": "Detaillierten Prozess und Werte aufzeichnen",
    },
}


class WorkThread(QThread):
    """工作线程 - 处理下载和审核（支持多线程下载和并行审核）"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, query, max_count, min_bookmarks, skip_r18, skip_ai,
                 enable_moderate, threshold, delete_filtered, download_folder="downloads",
                 download_mode="search", custom_tags=None, download_threads=3,
                 skip_ugoira=False, only_ugoira=False, debug_log=False):
        super().__init__()
        self.query = query
        self.max_count = max_count
        self.min_bookmarks = min_bookmarks
        self.skip_r18 = skip_r18
        self.skip_ai = skip_ai
        self.skip_ugoira = skip_ugoira
        self.only_ugoira = only_ugoira
        self.enable_moderate = enable_moderate
        self.debug_log = debug_log
        self.threshold = threshold
        self.delete_filtered = delete_filtered
        self.download_folder = download_folder
        self.download_mode = download_mode  # "search" 或 "bookmarks"
        self.custom_tags = custom_tags if custom_tags else ["penis", "sex"]  # 自定义过滤标签
        self.download_threads = download_threads  # 下载线程数
        self._is_paused = False
        self._is_stopped = False
        
        # 用于多线程下载和审核的队列
        import queue
        self.download_queue = queue.Queue()  # 待下载队列
        self.moderate_queue = queue.Queue()  # 待审核队列
        self.download_lock = threading.Lock()  # 下载统计锁
        self.moderate_lock = threading.Lock()  # 审核统计锁
        
        # 统计信息
        self.downloaded_count = 0
        self.moderated_count = 0
        self.kept_count = 0
        self.filtered_count = 0
        
        # 日志文件
        self.log_file = None
        if self.debug_log:
            # 创建日志目录
            log_dir = Path(self.download_folder) / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成日志文件名（带时间戳）
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = "".join(c for c in self.query if c.isalnum() or c in (' ', '-', '_'))[:30]
            log_filename = f"debug_{safe_query}_{timestamp}.log"
            self.log_file_path = log_dir / log_filename
            
            try:
                self.log_file = open(self.log_file_path, 'w', encoding='utf-8')
                self.write_log(f"=== WhiteJade 调试日志 ===")
                self.write_log(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.write_log(f"关键词: {self.query}")
                self.write_log(f"目标数量: {self.max_count}")
                self.write_log(f"阈值: {self.threshold}")
                self.write_log(f"过滤标签: {', '.join(self.custom_tags)}")
                self.write_log(f"下载线程数: {self.download_threads}")
                self.write_log(f"=" * 50)
                self.write_log("")
            except Exception as e:
                print(f"创建日志文件失败: {e}")
                self.log_file = None
    
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
    
    def write_log(self, message):
        """写入日志到文件和GUI"""
        # 发送到GUI
        self.progress.emit(message)
        
        # 写入文件
        if self.log_file:
            try:
                self.log_file.write(message + '\n')
                self.log_file.flush()  # 立即刷新到磁盘
            except Exception as e:
                print(f"写入日志失败: {e}")
    
    def close_log(self):
        """关闭日志文件"""
        if self.log_file:
            try:
                from datetime import datetime
                self.log_file.write(f"\n{'='*50}\n")
                self.log_file.write(f"日志结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                self.log_file.close()
                self.log_file = None
            except Exception as e:
                print(f"关闭日志文件失败: {e}")
    
    def download_worker(self, downloader, illust_list):
        """下载工作线程"""
        import time
        
        while not self._is_stopped:
            try:
                # 从队列获取作品信息
                if not illust_list:
                    break
                
                with self.download_lock:
                    if not illust_list:
                        break
                    illust = illust_list.pop(0)
                
                # 下载作品
                try:
                    full_illust = downloader.get_illustration_details(illust['id'])
                    if full_illust and downloader.download_illustration(full_illust, project_name=self.query):
                        with self.download_lock:
                            self.downloaded_count += 1
                        
                        # 将下载完成的作品放入审核队列
                        if self.enable_moderate:
                            self.moderate_queue.put(illust['id'])
                        else:
                            with self.moderate_lock:
                                self.kept_count += 1
                        
                        self.progress.emit(f"[下载] 已下载: {self.downloaded_count} 个作品")
                except Exception as e:
                    self.progress.emit(f"[下载] 下载失败 ID {illust['id']}: {str(e)}")
                
                time.sleep(0.5)  # 避免请求过快
                
            except Exception as e:
                self.progress.emit(f"[下载] 工作线程错误: {str(e)}")
                break
    
    def moderate_worker(self, moderator, picture_dir):
        """审核工作线程"""
        from pathlib import Path
        import shutil
        
        while not self._is_stopped:
            try:
                # 从队列获取待审核的作品ID
                try:
                    illust_id = self.moderate_queue.get(timeout=2)
                except:
                    # 队列为空，检查下载是否完成
                    # 如果所有下载线程都已完成且队列为空，退出
                    continue
                
                # 等待文件写入完成
                time.sleep(0.5)
                
                # 查找该作品的文件
                illust_files = []
                ugoira_dirs = []
                
                for item in picture_dir.iterdir():
                    if item.is_file() and str(illust_id) in item.name:
                        illust_files.append(item)
                    elif item.is_dir() and str(illust_id) in item.name:
                        if item.name.endswith('_ugoira'):
                            ugoira_dirs.append(item)
                        else:
                            # 漫画目录
                            illust_files.extend([f for f in item.iterdir() if f.is_file()])
                
                # 如果没找到文件，可能还在下载中，放回队列
                if not illust_files and not ugoira_dirs:
                    self.moderate_queue.put(illust_id)
                    time.sleep(1)
                    continue
                
                # 审核文件
                should_keep = True
                reason = ""
                
                # 审核动图
                for ugoira_dir in ugoira_dirs:
                    keep, result = moderator.check_ugoira(str(ugoira_dir), verbose=self.debug_log)
                    if not keep:
                        should_keep = False
                        reason = result.get('reason', '未通过审核')
                    
                    # 输出详细调试日志
                    if self.debug_log:
                        self.write_log(f"[调试] 动图 {ugoira_dir.name}:")
                        self.write_log(f"  - 状态: {'✗ 不通过' if not keep else '✓ 通过'}")
                        self.write_log(f"  - 总帧数: {result.get('total_frames', 'N/A')}")
                        self.write_log(f"  - 审核帧数: {result.get('frames_checked', 'N/A')}")
                        self.write_log(f"  - 审核比例: {result.get('check_ratio', 0)*100:.0f}%")
                        self.write_log(f"  - 原始阈值: {result.get('original_threshold', 'N/A')}")
                        self.write_log(f"  - 动图阈值: {result.get('ugoira_threshold', 'N/A')}")
                        
                        if not keep:
                            filtered_tags = result.get('filtered_tags', {})
                            if filtered_tags:
                                self.write_log(f"  - 过滤标签:")
                                for tag, score in sorted(filtered_tags.items(), key=lambda x: x[1], reverse=True):
                                    self.write_log(f"    • {tag}: {score:.2%}")
                            self.write_log(f"  - 失败帧: {result.get('frame', 'N/A')}")
                        
                        self.write_log("")  # 空行分隔
                    
                    if not keep:
                        break
                
                # 审核图片
                if should_keep:
                    for img_file in illust_files:
                        keep, result = moderator.check_image(str(img_file), verbose=self.debug_log)
                        if not keep:
                            should_keep = False
                            reason = result.get('reason', '未通过审核')
                            break
                        
                        # 输出详细调试日志
                        if self.debug_log:
                            all_tags = result.get('all_tags', {})
                            filtered_tags = result.get('filtered_tags', {})
                            
                            self.write_log(f"[调试] 图片 {img_file.name}:")
                            self.write_log(f"  - 状态: {'✗ 不通过' if not keep else '✓ 通过'}")
                            self.write_log(f"  - 检测到的标签总数: {len(all_tags)} 个")
                            self.write_log(f"  - 当前阈值: {moderator.threshold:.2f}")
                            
                            # 显示过滤标签的检测结果（无论是否超过阈值）
                            filter_tag_results = {}
                            for tag in self.custom_tags:
                                if tag in all_tags:
                                    filter_tag_results[tag] = all_tags[tag]
                            
                            if filter_tag_results:
                                self.write_log(f"  - 过滤标签检测结果:")
                                for tag, score in sorted(filter_tag_results.items(), key=lambda x: x[1], reverse=True):
                                    status = "超过阈值 ✗" if tag in filtered_tags else "未超过阈值 ✓"
                                    self.write_log(f"    • {tag}: {score:.2%} ({status})")
                            else:
                                self.write_log(f"  - 过滤标签检测结果: 未检测到任何过滤标签")
                            
                            # 显示所有检测到的标签（按置信度排序，只显示前10个）
                            if all_tags:
                                self.write_log(f"  - 检测到的标签 (前10个，按置信度排序):")
                                sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10]
                                for tag, score in sorted_tags:
                                    marker = "⚠" if tag in filtered_tags else " "
                                    self.write_log(f"    {marker} {tag}: {score:.2%}")
                            
                            self.write_log("")  # 空行分隔
                
                # 处理审核结果
                with self.moderate_lock:
                    self.moderated_count += 1
                    
                    if should_keep:
                        self.kept_count += 1
                        self.progress.emit(f"[审核] ✓ 保留 ID {illust_id} ({self.kept_count}/{self.moderated_count})")
                        
                        # 转换 ugoira 为 GIF/MP4
                        if ugoira_dirs:
                            try:
                                from image_moderator.ugoira_converter import UgoiraConverter
                                
                                # 获取转换格式设置
                                config_path = "pixiv_downloader/config.json"
                                with open(config_path, 'r', encoding='utf-8') as f:
                                    config = json.load(f)
                                ugoira_format = config.get('ugoira_format', 'gif')
                                
                                converter = UgoiraConverter(output_format=ugoira_format)
                                
                                for ugoira_dir in ugoira_dirs:
                                    self.progress.emit(f"[转换] 正在转换动图 ID {illust_id} 为 {ugoira_format.upper()}...")
                                    success, message = converter.convert_ugoira(str(ugoira_dir), delete_source=True)
                                    
                                    if success:
                                        # 转换成功，将输出文件移动到picture目录
                                        output_file = Path(message)
                                        if output_file.exists():
                                            # 移动到picture目录
                                            dest_file = picture_dir / output_file.name
                                            shutil.move(str(output_file), str(dest_file))
                                            self.progress.emit(f"[转换] ✓ 转换成功: {output_file.name}")
                                            
                                            # 删除 ugoira 目录
                                            if ugoira_dir.exists():
                                                shutil.rmtree(ugoira_dir)
                                        else:
                                            self.progress.emit(f"[转换] ✗ 输出文件不存在: {message}")
                                    else:
                                        self.progress.emit(f"[转换] ✗ 转换失败: {message}")
                            except Exception as e:
                                self.progress.emit(f"[转换] 转换错误: {str(e)}")
                    else:
                        self.filtered_count += 1
                        self.progress.emit(f"[审核] ✗ 过滤 ID {illust_id}: {reason} ({self.filtered_count}/{self.moderated_count})")
                        
                        # 移动到ban目录
                        ban_dir = picture_dir.parent / 'ban'
                        ban_dir.mkdir(exist_ok=True)
                        
                        for ugoira_dir in ugoira_dirs:
                            dest = ban_dir / ugoira_dir.name
                            try:
                                if self.delete_filtered:
                                    shutil.move(str(ugoira_dir), str(dest))
                                else:
                                    shutil.copytree(ugoira_dir, dest, dirs_exist_ok=True)
                            except Exception as e:
                                self.progress.emit(f"[审核] 移动文件失败: {e}")
                        
                        for img_file in illust_files:
                            dest = ban_dir / img_file.name
                            try:
                                if self.delete_filtered:
                                    shutil.move(str(img_file), str(dest))
                                else:
                                    shutil.copy2(img_file, dest)
                            except Exception as e:
                                self.progress.emit(f"[审核] 移动文件失败: {e}")
                
                self.moderate_queue.task_done()
                
            except Exception as e:
                self.progress.emit(f"[审核] 工作线程错误: {str(e)}")
                continue
    
    def run(self):
        try:
            # 步骤 1: 初始化
            from pixiv_downloader import PixivDownloader
            from pathlib import Path
            import threading
            
            if self.check_pause():
                self.finished.emit(False, "任务已停止")
                return
            
            config_path = "pixiv_downloader/config.json"
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            token = config.get('refresh_token')
            
            self.progress.emit("[登录] 正在连接 Pixiv 服务器...")
            downloader = PixivDownloader(refresh_token=token, download_dir=self.download_folder)
            
            if self.check_pause():
                self.finished.emit(False, "任务已停止")
                return
            
            if not downloader.login():
                self.finished.emit(False, "登录失败：无法连接到 Pixiv 服务器")
                return
            
            self.progress.emit("[登录] 登录成功")
            
            if self.download_mode == "search":
                self.progress.emit(f"[下载] 开始搜索关键词: {self.query}")
            else:
                self.progress.emit(f"[下载] 开始下载收藏夹作品")
            
            self.progress.emit(f"[下载] 目标保留数量: {self.max_count} 张图片")
            self.progress.emit(f"[下载] 下载线程数: {self.download_threads}")
            self.progress.emit(f"[下载] 最小收藏数: {self.min_bookmarks}")
            self.progress.emit(f"[下载] 跳过 R-18: {'是' if self.skip_r18 else '否'}")
            self.progress.emit(f"[下载] 跳过 AI 作品: {'是' if self.skip_ai else '否'}")
            
            if self.enable_moderate:
                self.progress.emit(f"[下载] 启用审核模式: 下载和审核将同时进行")
                # 如果启用审核，下载 2 倍数量以确保足够
                download_count = int(self.max_count * 2)
            else:
                download_count = self.max_count
            
            if self.check_pause():
                self.finished.emit(False, "任务已停止")
                return
            
            self.progress.emit(f"[下载] 初始下载数量: {download_count} 个作品")
            
            # 步骤 2: 获取作品列表
            self.progress.emit("[搜索] 正在获取作品列表...")
            
            illust_list = []
            page = 1
            max_pages = 20  # 最多搜索20页
            
            while len(illust_list) < download_count and page <= max_pages:
                if self._is_stopped:
                    self.finished.emit(False, "任务已停止")
                    return
                
                # 获取一页作品
                if self.download_mode == "search":
                    illusts = downloader.search_illustrations(query=self.query, page=page)
                else:  # bookmarks mode
                    illusts = downloader.get_user_bookmarks(offset=(page-1)*30)
                
                if not illusts:
                    self.progress.emit(f"[搜索] 第 {page} 页没有更多作品")
                    break
                
                # 筛选作品
                for illust in illusts:
                    if len(illust_list) >= download_count:
                        break
                    
                    # 跳过R-18作品（可选）
                    if self.skip_r18 and illust.get('x_restrict', 0) > 0:
                        continue
                    
                    # 跳过AI作品（可选）
                    if self.skip_ai and illust.get('illust_ai_type', 0) == 2:
                        continue
                    
                    # 动图过滤
                    is_ugoira = illust.get('type') == 'ugoira'
                    if self.skip_ugoira and is_ugoira:
                        continue
                    if self.only_ugoira and not is_ugoira:
                        continue
                    
                    # 收藏数过滤
                    if illust.get('total_bookmarks', 0) < self.min_bookmarks:
                        continue
                    
                    # 跳过已下载的作品
                    if illust['id'] in downloader.downloaded_ids:
                        continue
                    
                    illust_list.append(illust)
                
                self.progress.emit(f"[搜索] 已找到 {len(illust_list)} 个符合条件的作品...")
                page += 1
                time.sleep(1)  # 避免请求过快
            
            if not illust_list:
                self.finished.emit(False, "未找到符合条件的作品")
                return
            
            self.progress.emit(f"[搜索] 找到 {len(illust_list)} 个作品，开始下载...")
            
            # 步骤 3: 启动审核线程（如果启用）
            moderator = None
            moderate_thread = None
            
            if self.enable_moderate:
                self.progress.emit("[审核] 正在加载 DeepDanbooru AI 模型...")
                self.progress.emit("[审核] 提示: 模型加载需要约 10-30 秒，请耐心等待")
                self.progress.emit(f"[审核] 检测阈值: {self.threshold} (阈值越低越严格)")
                
                try:
                    self.progress.emit("[审核] 步骤 1/3: 导入 DeepDanbooru 模块...")
                    from image_moderator.deepdanbooru_moderator import DeepDanbooruModerator
                    
                    self.progress.emit("[审核] 步骤 2/3: 初始化模型...")
                    moderator = DeepDanbooruModerator(
                        threshold=self.threshold,
                        filter_tags=self.custom_tags,
                        ugoira_threshold_offset=-0.1  # 动图阈值偏移，降低阈值使审核更严格
                    )
                    
                    self.progress.emit(f"[审核] 过滤标签: {', '.join(self.custom_tags)}")
                    self.progress.emit(f"[审核] 动图阈值偏移: -0.1 (更严格，因画质较低可能误判)")
                    self.progress.emit("[审核] 步骤 3/3: 模型加载成功 ✓")
                    
                    # 获取图片目录
                    safe_name = "".join(c for c in self.query if c.isalnum() or c in (' ', '-', '_', '。', '！', '？')).strip()
                    if len(safe_name) > 50:
                        safe_name = safe_name[:50]
                    picture_dir = Path(self.download_folder) / safe_name / "picture"
                    
                    # 启动审核线程
                    moderate_thread = threading.Thread(
                        target=self.moderate_worker,
                        args=(moderator, picture_dir),
                        daemon=True
                    )
                    moderate_thread.start()
                    self.progress.emit("[审核] 审核线程已启动，将实时审核下载的图片")
                    
                except Exception as e:
                    import traceback
                    error_detail = traceback.format_exc()
                    self.progress.emit(f"[审核] 错误详情: {error_detail}")
                    self.finished.emit(False, f"模型加载失败: {str(e)}")
                    return
            
            # 步骤 4: 启动多线程下载
            self.progress.emit(f"[下载] 启动 {self.download_threads} 个下载线程...")
            
            download_threads = []
            for i in range(self.download_threads):
                t = threading.Thread(
                    target=self.download_worker,
                    args=(downloader, illust_list),
                    daemon=True
                )
                t.start()
                download_threads.append(t)
            
            # 步骤 5: 监控下载进度
            while not self._is_stopped:
                # 检查所有下载线程是否完成
                all_done = all(not t.is_alive() for t in download_threads)
                
                if all_done:
                    self.progress.emit(f"[下载] 所有下载线程已完成")
                    break
                
                # 定期更新进度
                self.msleep(1000)
                
                if self.check_pause():
                    self.finished.emit(False, "任务已停止")
                    return
            
            if self._is_stopped:
                self.finished.emit(False, "任务已停止")
                return
            
            self.progress.emit(f"[下载] 下载完成，成功下载 {self.downloaded_count} 个作品")
            
            # 步骤 6: 等待审核完成
            if self.enable_moderate and moderate_thread:
                self.progress.emit("[审核] 等待所有图片审核完成...")
                
                # 等待审核队列清空
                while not self._is_stopped:
                    if self.moderate_queue.empty() and self.moderated_count >= self.downloaded_count:
                        break
                    self.msleep(500)
                
                if self._is_stopped:
                    self.finished.emit(False, "任务已停止")
                    return
                
                self.progress.emit("[审核] 所有审核完成")
                self.progress.emit(f"[审核] 最终保留: {self.kept_count} 张图片")
                self.progress.emit(f"[审核] 总计过滤: {self.filtered_count} 张图片")
                
                # 检查是否需要继续下载
                if self.kept_count < self.max_count:
                    needed = self.max_count - self.kept_count
                    self.progress.emit(f"[提示] 还需 {needed} 张图片才能达到目标")
                    self.progress.emit(f"[提示] 可以再次运行下载任务以获取更多图片")
                    
                    result = (f"任务完成（未达到目标）\n\n"
                             f"目标数量: {self.max_count} 张\n"
                             f"实际保留: {self.kept_count} 张\n"
                             f"下载作品: {self.downloaded_count} 个\n"
                             f"审核图片: {self.moderated_count} 张\n"
                             f"过滤图片: {self.filtered_count} 张\n"
                             f"过滤率: {self.filtered_count/self.moderated_count*100:.1f}%\n\n"
                             f"提示: 可尝试降低筛选条件或更换关键词")
                else:
                    result = (f"任务完成\n\n"
                             f"目标数量: {self.max_count} 张\n"
                             f"实际保留: {self.kept_count} 张\n"
                             f"下载作品: {self.downloaded_count} 个\n"
                             f"审核图片: {self.moderated_count} 张\n"
                             f"过滤图片: {self.filtered_count} 张\n"
                             f"过滤率: {self.filtered_count/self.moderated_count*100:.1f}%")
                
                self.finished.emit(True, result)
            else:
                self.progress.emit("[完成] 所有任务已完成")
                result = f"下载完成\n\n成功下载 {self.downloaded_count} 个作品"
                self.finished.emit(True, result)
            
            # 关闭日志文件并提示位置
            if self.debug_log and self.log_file:
                self.progress.emit(f"[日志] 调试日志已保存到: {self.log_file_path}")
            self.close_log()
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            self.progress.emit(f"[错误] {error_detail}")
            self.close_log()  # 确保异常时也关闭日志
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
        # 先初始化默认值，确保属性存在
        self.config = {}
        self.theme_color = (255, 182, 193)
        self.current_language = "zh_CN"
        self.close_behavior = "ask"
        
        try:
            config_path = "pixiv_downloader/config.json"
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    # 加载主题色
                    if 'theme_color' in self.config:
                        self.theme_color = tuple(self.config['theme_color'])
                    # 加载语言
                    if 'language' in self.config:
                        self.current_language = self.config['language']
                    # 加载关闭行为
                    if 'close_behavior' in self.config:
                        self.close_behavior = self.config['close_behavior']
        except Exception as e:
            print(f"加载配置失败: {e}")
            # 保持默认值
    
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
            config['close_behavior'] = self.close_behavior
            
            # 合并 self.config 中的其他设置（如 download_threads）
            config.update(self.config)
            
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
        
        # 初始化过滤标签显示（从配置加载）
        self.update_filter_tags_label()
        
        # 创建系统托盘图标
        self.create_tray_icon()
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
        from PyQt6.QtGui import QIcon, QAction
        
        # 创建托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        
        # 设置图标（使用应用图标）
        if os.path.exists("icon.png"):
            self.tray_icon.setIcon(QIcon("icon.png"))
        else:
            # 如果没有图标文件，使用默认图标
            self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # 创建托盘菜单
        tray_menu = QMenu()
        
        # 显示/隐藏窗口
        show_action = QAction(self.tr("show_window", "显示窗口"), self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        # 退出
        quit_action = QAction(self.tr("quit", "退出"), self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
        
        # 设置托盘提示
        self.tray_icon.setToolTip("WhiteJade - Pixiv 下载器")
    
    def on_tray_activated(self, reason):
        """托盘图标被激活"""
        from PyQt6.QtWidgets import QSystemTrayIcon
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()
    
    def show_window(self):
        """显示窗口"""
        self.show()
        self.activateWindow()
        self.raise_()
    
    def quit_application(self):
        """完全退出应用"""
        self.tray_icon.hide()
        QApplication.quit()
    
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
        
        # 下载模式选择
        mode_layout = QHBoxLayout()
        mode_label = QLabel(self.tr("download_mode", "下载模式:"))
        mode_label.setFixedWidth(100)
        mode_label.setStyleSheet("color: #666; background: transparent;")
        
        self.mode_search_radio = QRadioButton(self.tr("mode_search", "关键词搜索"))
        self.mode_search_radio.setChecked(True)
        self.mode_search_radio.setStyleSheet("color: #666; background: transparent;")
        self.mode_search_radio.toggled.connect(self.toggle_download_mode)
        
        self.mode_bookmarks_radio = QRadioButton(self.tr("mode_bookmarks", "我的收藏夹"))
        self.mode_bookmarks_radio.setStyleSheet("color: #666; background: transparent;")
        
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_search_radio)
        mode_layout.addWidget(self.mode_bookmarks_radio)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        # 关键词（仅在搜索模式下显示）
        keyword_layout = QHBoxLayout()
        self.keyword_label = QLabel(self.tr("search_keyword", "搜索关键词:"))
        self.keyword_label.setFixedWidth(100)
        self.keyword_label.setStyleSheet("color: #666; background: transparent;")
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText(self.tr("keyword_placeholder", "例如: 小萝莉"))
        keyword_layout.addWidget(self.keyword_label)
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
        
        # AI和动图过滤选项（一行）
        filter_layout = QHBoxLayout()
        
        self.skip_ai_check = QCheckBox(self.tr("skip_ai", "去除 AI 作品"))
        self.skip_ai_check.setStyleSheet("color: #666; background: transparent;")
        
        self.skip_ugoira_check = QCheckBox(self.tr("skip_ugoira", "跳过动图"))
        self.skip_ugoira_check.setStyleSheet("color: #666; background: transparent;")
        
        self.only_ugoira_check = QCheckBox(self.tr("only_ugoira", "只下载动图"))
        self.only_ugoira_check.setStyleSheet("color: #666; background: transparent;")
        
        # 互斥逻辑：选中一个时取消另一个
        self.skip_ugoira_check.stateChanged.connect(lambda state: self.only_ugoira_check.setChecked(False) if state else None)
        self.only_ugoira_check.stateChanged.connect(lambda state: self.skip_ugoira_check.setChecked(False) if state else None)
        
        filter_layout.addWidget(self.skip_ai_check)
        filter_layout.addWidget(self.skip_ugoira_check)
        filter_layout.addWidget(self.only_ugoira_check)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
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
        
        # 高级过滤选项 - 改为按钮+文本显示
        advanced_filter_layout = QHBoxLayout()
        
        # 显示已选标签的文本框（只读）
        self.selected_tags_label = QLabel(self.tr("default_tags", "默认: penis, sex"))
        self.selected_tags_label.setStyleSheet("""
            color: #666; 
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 182, 193, 0.5);
            border-radius: 5px;
            padding: 5px 10px;
            font-size: 11px;
        """)
        self.selected_tags_label.setWordWrap(True)
        
        # 展开按钮
        self.advanced_filter_btn = QPushButton(self.tr("advanced_filter", "高级过滤选项"))
        self.advanced_filter_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 182, 193, 0.8);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 182, 193, 1);
            }
        """)
        self.advanced_filter_btn.clicked.connect(self.show_advanced_filter_dialog)
        
        advanced_filter_layout.addWidget(QLabel(self.tr("filter_tags", "过滤标签:")))
        advanced_filter_layout.addWidget(self.selected_tags_label, 1)
        advanced_filter_layout.addWidget(self.advanced_filter_btn)
        moderate_options_layout.addLayout(advanced_filter_layout)
        
        # 初始化标签复选框字典（用于对话框）
        self.filter_tag_checkboxes = {}
        
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
        
        # 关闭行为设置
        close_layout = QHBoxLayout()
        close_label = QLabel(self.tr("close_behavior", "关闭行为:"))
        close_label.setFixedWidth(80)
        close_label.setStyleSheet("color: #666; background: transparent; font-weight: bold;")
        
        self.close_behavior_combo = QComboBox()
        self.close_behavior_combo.addItem(self.tr("ask_on_close", "每次询问"), "ask")
        self.close_behavior_combo.addItem(self.tr("exit_directly", "直接退出"), "exit")
        self.close_behavior_combo.addItem(self.tr("minimize_to_tray_option", "最小化到托盘"), "tray")
        
        # 设置当前关闭行为
        for i in range(self.close_behavior_combo.count()):
            if self.close_behavior_combo.itemData(i) == self.close_behavior:
                self.close_behavior_combo.setCurrentIndex(i)
                break
        
        self.close_behavior_combo.currentIndexChanged.connect(self.on_close_behavior_changed)
        self.close_behavior_combo.setFixedHeight(40)
        
        close_layout.addWidget(close_label)
        close_layout.addWidget(self.close_behavior_combo)
        close_layout.addStretch()
        layout.addLayout(close_layout)
        
        # 下载线程数设置
        threads_layout = QHBoxLayout()
        threads_label = QLabel(self.tr("download_threads", "下载线程数:"))
        threads_label.setFixedWidth(80)
        threads_label.setStyleSheet("color: #666; background: transparent; font-weight: bold;")
        
        self.download_threads_spin = QSpinBox()
        self.download_threads_spin.setRange(1, 10)
        self.download_threads_spin.setValue(self.config.get('download_threads', 3))
        self.download_threads_spin.setFixedWidth(80)
        self.download_threads_spin.setFixedHeight(40)
        self.download_threads_spin.valueChanged.connect(self.on_download_threads_changed)
        
        threads_hint = QLabel(self.tr("download_threads_hint", "同时下载的作品数量（1-10）"))
        threads_hint.setStyleSheet("color: #999; background: transparent; font-size: 11px;")
        
        threads_layout.addWidget(threads_label)
        threads_layout.addWidget(self.download_threads_spin)
        threads_layout.addWidget(threads_hint)
        threads_layout.addStretch()
        layout.addLayout(threads_layout)
        
        # Ugoira 转换格式设置
        ugoira_layout = QHBoxLayout()
        ugoira_label = QLabel(self.tr("ugoira_format", "动图格式:"))
        ugoira_label.setFixedWidth(80)
        ugoira_label.setStyleSheet("color: #666; background: transparent; font-weight: bold;")
        
        self.ugoira_format_combo = QComboBox()
        self.ugoira_format_combo.addItems(["GIF", "MP4"])
        current_format = self.config.get('ugoira_format', 'gif').upper()
        self.ugoira_format_combo.setCurrentText(current_format)
        self.ugoira_format_combo.setFixedWidth(80)
        self.ugoira_format_combo.setFixedHeight(40)
        self.ugoira_format_combo.currentTextChanged.connect(self.on_ugoira_format_changed)
        
        ugoira_hint = QLabel(self.tr("ugoira_format_hint", "动图自动转换格式"))
        ugoira_hint.setStyleSheet("color: #999; background: transparent; font-size: 11px;")
        
        ugoira_layout.addWidget(ugoira_label)
        ugoira_layout.addWidget(self.ugoira_format_combo)
        ugoira_layout.addWidget(ugoira_hint)
        ugoira_layout.addStretch()
        layout.addLayout(ugoira_layout)
        
        # 调试日志开关
        debug_layout = QHBoxLayout()
        self.debug_log_check = QCheckBox(self.tr("enable_debug_log", "启用调试日志"))
        self.debug_log_check.setChecked(self.config.get('debug_log', False))
        self.debug_log_check.setStyleSheet("color: #666; background: transparent; font-weight: bold;")
        self.debug_log_check.stateChanged.connect(self.on_debug_log_changed)
        
        debug_hint = QLabel(self.tr("debug_log_hint", "记录详细的审核过程和数值"))
        debug_hint.setStyleSheet("color: #999; background: transparent; font-size: 11px;")
        
        debug_layout.addWidget(self.debug_log_check)
        debug_layout.addWidget(debug_hint)
        debug_layout.addStretch()
        layout.addLayout(debug_layout)
        
        # 目录设置
        folder_layout = QHBoxLayout()
        folder_label = QLabel(self.tr("download_dir", "下载目录:"))
        folder_label.setFixedWidth(80)
        folder_label.setStyleSheet("color: #666; background: transparent;")
        
        # 显示当前下载目录
        self.download_path_label = QLabel(str(self.get_download_folder()))
        self.download_path_label.setStyleSheet("""
            color: #333; 
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(255, 182, 193, 0.5);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 12px;
        """)
        self.download_path_label.setWordWrap(False)
        
        change_folder_btn = QPushButton(self.tr("change_folder", "更改目录"))
        change_folder_btn.clicked.connect(self.change_download_folder)
        change_folder_btn.setFixedHeight(40)
        change_folder_btn.setFixedWidth(100)
        change_folder_btn.setStyleSheet("""
            QPushButton {
                color: #333;
            }
        """)
        
        open_folder_btn = QPushButton(self.tr("open_folder", "打开目录"))
        open_folder_btn.clicked.connect(self.open_download_folder)
        open_folder_btn.setFixedHeight(40)
        open_folder_btn.setFixedWidth(100)
        open_folder_btn.setStyleSheet("""
            QPushButton {
                color: #333;
            }
        """)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.download_path_label, 1)  # 占据剩余空间
        folder_layout.addWidget(change_folder_btn)
        folder_layout.addWidget(open_folder_btn)
        layout.addLayout(folder_layout)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background: rgba(255, 182, 193, 0.3); margin: 10px 0;")
        layout.addWidget(separator)
        
        # 开发者信息和 GitHub 链接
        dev_layout = QHBoxLayout()
        dev_label = QLabel(self.tr("developer", "开发: mamajunya"))
        dev_label.setStyleSheet("color: #666; background: transparent; font-size: 13px;")
        
        star_label = QLabel(self.tr("star_request", "如果喜欢请给点一个 Star ⭐"))
        star_label.setStyleSheet("color: #999; background: transparent; font-size: 12px; margin-left: 10px;")
        
        github_btn = QPushButton("🌟 GitHub")
        github_btn.clicked.connect(self.open_github)
        github_btn.setFixedHeight(35)
        github_btn.setFixedWidth(120)
        github_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #24292e, stop:1 #2f363d);
                color: white;
                border: 2px solid #444d56;
                border-radius: 8px;
                padding: 5px 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2f363d, stop:1 #444d56);
                border: 2px solid #586069;
            }
            QPushButton:pressed {
                background: #1b1f23;
            }
        """)
        
        dev_layout.addWidget(dev_label)
        dev_layout.addWidget(star_label)
        dev_layout.addStretch()
        dev_layout.addWidget(github_btn)
        layout.addLayout(dev_layout)
        
        group.setLayout(layout)
        return group
    
    def toggle_moderate_options(self, checked):
        """切换审核选项的可见性"""
        self.moderate_options.setVisible(checked)
    
    def toggle_download_mode(self, checked):
        """切换下载模式时显示/隐藏关键词输入框"""
        # checked为True表示选中了搜索模式
        self.keyword_label.setVisible(checked)
        self.keyword_input.setVisible(checked)
    
    def show_advanced_filter_dialog(self):
        """显示高级过滤选项对话框"""
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle(self.tr("advanced_filter", "高级过滤选项"))
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet("""
            QDialog {
                background: white;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # 说明文字
        hint_label = QLabel(self.tr("custom_tags_hint", "选择需要过滤的NSFW标签"))
        hint_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        layout.addWidget(hint_label)
        
        # 创建标签复选框网格
        tags_grid = QGridLayout()
        tags_grid.setSpacing(10)
        
        # 定义常用的NSFW标签（按严重程度分类）
        nsfw_tags = [
            # 第一行：默认选中（最严重）
            ("penis", "男性生殖器"),
            ("sex", "性交"),
            ("vaginal", "阴道性交"),
            ("anal", "肛交"),
            # 第二行：口交相关
            ("fellatio", "口交(男)"),
            ("cunnilingus", "口交(女)"),
            ("pussy", "女性生殖器"),
            ("nude", "裸体"),
            # 第三行：其他性行为
            ("masturbation", "自慰"),
            ("cum", "精液"),
            ("orgasm", "高潮"),
            ("ejaculation", "射精"),
            # 第四行：身体部位
            ("nipples", "乳头"),
            ("pussy_juice", "爱液"),
            ("sex_from_behind", "后入"),
            ("female_ejaculation", "潮吹"),
        ]
        
        # 从配置加载历史选择
        saved_tags = self.config.get('filter_tags', ['penis', 'sex'])
        
        # 清空并重新创建复选框
        self.filter_tag_checkboxes = {}
        
        row = 0
        col = 0
        for tag, label in nsfw_tags:
            checkbox = QCheckBox(f"{label} ({tag})")
            # 根据配置设置选中状态
            checkbox.setChecked(tag in saved_tags)
            checkbox.setStyleSheet("""
                QCheckBox {
                    color: #666;
                    font-size: 12px;
                    padding: 5px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)
            self.filter_tag_checkboxes[tag] = checkbox
            tags_grid.addWidget(checkbox, row, col)
            col += 1
            if col >= 2:  # 每行2个，更宽松
                col = 0
                row += 1
        
        layout.addLayout(tags_grid)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(lambda: self.apply_filter_tags(dialog))
        button_box.rejected.connect(dialog.reject)
        button_box.setStyleSheet("""
            QPushButton {
                background: rgba(255, 182, 193, 0.8);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background: rgba(255, 182, 193, 1);
            }
        """)
        layout.addWidget(button_box)
        
        dialog.exec()
    
    def apply_filter_tags(self, dialog):
        """应用过滤标签选择"""
        # 获取选中的标签
        selected_tags = [tag for tag, checkbox in self.filter_tag_checkboxes.items() if checkbox.isChecked()]
        
        # 更新显示
        self.update_filter_tags_label(selected_tags)
        
        # 保存到配置
        self.config['filter_tags'] = selected_tags
        self.save_config()
        
        # 日志确认
        self.log_text.append(f"✓ 过滤标签已保存: {', '.join(selected_tags) if selected_tags else '无'}")
        
        dialog.accept()
    
    def update_filter_tags_label(self, tags=None):
        """更新过滤标签显示
        
        Args:
            tags: 标签列表，如果为None则从配置读取
        """
        if tags is None:
            tags = self.config.get('filter_tags', ['penis', 'sex'])
        
        if tags:
            self.selected_tags_label.setText(f"已选: {', '.join(tags)}")
        else:
            self.selected_tags_label.setText("未选择任何标签")
    
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
        # 获取下载模式
        download_mode = "search" if self.mode_search_radio.isChecked() else "bookmarks"
        
        # 如果是搜索模式，检查关键词
        if download_mode == "search":
            keyword = self.keyword_input.text().strip()
            if not keyword:
                QMessageBox.warning(self, "提示", "请输入搜索关键词！")
                return
        else:
            keyword = "my_bookmarks"  # 收藏夹模式使用固定名称
        
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.log_text.clear()
        self.log_text.append("=" * 50)
        self.log_text.append(f"[任务] 开始新任务")
        
        if download_mode == "search":
            self.log_text.append(f"[任务] 下载模式: 关键词搜索")
            self.log_text.append(f"[任务] 搜索关键词: {keyword}")
        else:
            self.log_text.append(f"[任务] 下载模式: 我的收藏夹")
        
        self.log_text.append(f"[任务] 下载数量: {self.count_spin.value()}")
        self.log_text.append(f"[任务] 最小收藏: {self.bookmark_spin.value()}")
        self.log_text.append("=" * 50)
        self.status_label.setText(f"准备开始: {keyword if download_mode == 'search' else '收藏夹'}")
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        self.progress_bar.setFormat("处理中...")
        
        # 获取阈值
        threshold = 0.4  # 默认使用非常严格模式
        if self.enable_moderate_check.isChecked():
            threshold_text = self.threshold_combo.currentText()
            threshold = float(threshold_text.split()[0])
        
        # 获取下载模式
        download_mode = "search" if self.mode_search_radio.isChecked() else "bookmarks"
        
        # 获取自定义标签（从复选框）
        custom_tags = []
        if hasattr(self, 'filter_tag_checkboxes'):
            for tag, checkbox in self.filter_tag_checkboxes.items():
                if checkbox.isChecked():
                    custom_tags.append(tag)
        
        # 如果没有选择任何标签，使用默认值
        if not custom_tags:
            custom_tags = ["penis", "sex"]
        
        # 创建工作线程
        self.work_thread = WorkThread(
            query=keyword,
            max_count=self.count_spin.value(),
            min_bookmarks=self.bookmark_spin.value(),
            skip_r18=self.skip_r18_check.isChecked(),
            skip_ai=self.skip_ai_check.isChecked(),
            enable_moderate=self.enable_moderate_check.isChecked(),
            threshold=threshold,
            delete_filtered=self.delete_filtered_check.isChecked(),
            download_folder=str(self.get_download_folder()),
            download_mode=download_mode,
            custom_tags=custom_tags,
            download_threads=self.config.get('download_threads', 3),
            skip_ugoira=self.skip_ugoira_check.isChecked(),
            only_ugoira=self.only_ugoira_check.isChecked(),
            debug_log=self.config.get('debug_log', False)
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
        download_dir = self.get_download_folder()
        if download_dir.exists():
            os.startfile(str(download_dir)) if sys.platform == "win32" else os.system(f'open "{download_dir}"')
        else:
            QMessageBox.information(self, "提示", "下载目录还不存在")
    
    def get_download_folder(self):
        """获取当前下载目录（返回绝对路径）"""
        config_file = Path("config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    download_path = config.get('download_folder', 'downloads')
                    return Path(download_path).resolve()  # 转换为绝对路径
            except:
                pass
        return Path("downloads").resolve()  # 转换为绝对路径
    
    def save_download_folder(self, folder_path):
        """保存下载目录到配置（保存绝对路径）"""
        config_file = Path("config.json")
        config = {}
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except:
                pass
        
        # 保存绝对路径
        config['download_folder'] = str(Path(folder_path).resolve())
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    def change_download_folder(self):
        """更改下载目录"""
        from PyQt6.QtWidgets import QFileDialog
        
        # 获取当前下载目录（绝对路径）
        current_folder = self.get_download_folder().resolve()
        
        # 选择新目录
        new_folder = QFileDialog.getExistingDirectory(
            self,
            self.tr("select_folder", "选择下载目录"),
            str(current_folder.parent),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not new_folder:
            return
        
        # 转换为绝对路径
        new_folder_path = Path(new_folder).resolve()
        
        # 如果选择的是同一个目录，不做任何操作
        if new_folder_path == current_folder:
            return
        
        # 询问是否转移数据
        if current_folder.exists() and any(current_folder.iterdir()):
            reply = QMessageBox.question(
                self,
                self.tr("transfer_data", "转移数据"),
                self.tr("transfer_data_msg", f"检测到原目录中有数据，是否转移到新目录？\n\n原目录: {current_folder}\n新目录: {new_folder_path}"),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            
            if reply == QMessageBox.StandardButton.Yes:
                # 转移数据
                try:
                    self.log_text.append(f"[系统] 开始转移数据...")
                    self.log_text.append(f"[系统] 从: {current_folder}")
                    self.log_text.append(f"[系统] 到: {new_folder_path}")
                    
                    # 创建新目录
                    new_folder_path.mkdir(parents=True, exist_ok=True)
                    
                    # 转移所有文件和文件夹
                    import shutil
                    transferred_count = 0
                    errors = []
                    
                    for item in current_folder.iterdir():
                        try:
                            dest = new_folder_path / item.name
                            self.log_text.append(f"[系统] 转移: {item.name}")
                            
                            if item.is_dir():
                                if dest.exists():
                                    # 如果目标已存在，合并内容
                                    shutil.copytree(str(item), str(dest), dirs_exist_ok=True)
                                    # 复制后删除原目录
                                    shutil.rmtree(str(item))
                                else:
                                    shutil.move(str(item), str(dest))
                            else:
                                if dest.exists():
                                    dest.unlink()  # 删除已存在的文件
                                shutil.move(str(item), str(dest))
                            
                            transferred_count += 1
                        except Exception as e:
                            error_msg = f"转移 {item.name} 失败: {str(e)}"
                            errors.append(error_msg)
                            self.log_text.append(f"[错误] {error_msg}")
                    
                    if errors:
                        self.log_text.append(f"[系统] 转移完成，但有 {len(errors)} 个错误")
                    else:
                        self.log_text.append(f"[系统] 成功转移 {transferred_count} 个项目")
                    
                    # 删除原目录（如果为空）
                    try:
                        if not any(current_folder.iterdir()):
                            current_folder.rmdir()
                            self.log_text.append(f"[系统] 已删除空的原目录")
                        else:
                            remaining = list(current_folder.iterdir())
                            self.log_text.append(f"[系统] 原目录还有 {len(remaining)} 个项目未转移")
                    except Exception as e:
                        self.log_text.append(f"[系统] 删除原目录失败: {str(e)}")
                    
                    if errors:
                        QMessageBox.warning(
                            self,
                            self.tr("warning", "警告"),
                            f"数据转移完成，但有 {len(errors)} 个错误。\n请查看日志了解详情。"
                        )
                    
                except Exception as e:
                    import traceback
                    error_detail = traceback.format_exc()
                    self.log_text.append(f"[错误] 数据转移失败: {error_detail}")
                    QMessageBox.critical(
                        self,
                        self.tr("error", "错误"),
                        self.tr("transfer_failed", f"数据转移失败: {str(e)}")
                    )
                    return
        
        # 保存新目录
        self.save_download_folder(new_folder_path)
        
        # 更新显示
        self.download_path_label.setText(str(new_folder_path))
        
        QMessageBox.information(
            self,
            self.tr("success", "成功"),
            self.tr("folder_changed", f"下载目录已更改为:\n{new_folder_path}")
        )
        
        self.log_text.append(f"[系统] 下载目录已更改为: {new_folder_path}")
    
    def open_github(self):
        """打开 GitHub 仓库"""
        import webbrowser
        webbrowser.open("https://github.com/mamajunya/WhiteJade")
    
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
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.close_behavior == "exit":
            # 直接退出
            self.quit_application()
            event.accept()
        elif self.close_behavior == "tray":
            # 最小化到托盘
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "WhiteJade",
                self.tr("minimized_to_tray", "已最小化到系统托盘"),
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            # 询问用户
            from PyQt6.QtWidgets import QMessageBox, QCheckBox
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(self.tr("close_window", "关闭窗口"))
            msg_box.setText(self.tr("close_window_msg", "您想要？"))
            msg_box.setIcon(QMessageBox.Icon.Question)
            
            # 添加按钮
            exit_btn = msg_box.addButton(self.tr("exit_app", "完全退出"), QMessageBox.ButtonRole.AcceptRole)
            tray_btn = msg_box.addButton(self.tr("minimize_to_tray", "最小化到托盘"), QMessageBox.ButtonRole.RejectRole)
            cancel_btn = msg_box.addButton(self.tr("cancel", "取消"), QMessageBox.ButtonRole.RejectRole)
            
            # 添加"记住我的选择"复选框
            remember_checkbox = QCheckBox(self.tr("remember_choice", "记住我的选择"))
            msg_box.setCheckBox(remember_checkbox)
            
            msg_box.exec()
            
            clicked_button = msg_box.clickedButton()
            remember = remember_checkbox.isChecked()
            
            if clicked_button == exit_btn:
                if remember:
                    self.close_behavior = "exit"
                    self.save_config()
                self.quit_application()
                event.accept()
            elif clicked_button == tray_btn:
                if remember:
                    self.close_behavior = "tray"
                    self.save_config()
                event.ignore()
                self.hide()
                self.tray_icon.showMessage(
                    "WhiteJade",
                    self.tr("minimized_to_tray", "已最小化到系统托盘"),
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            else:
                # 取消
                event.ignore()
    
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
    
    def on_close_behavior_changed(self, index):
        """关闭行为改变时触发"""
        new_behavior = self.close_behavior_combo.itemData(index)
        if new_behavior != self.close_behavior:
            self.close_behavior = new_behavior
            self.save_config()
            QMessageBox.information(
                self,
                self.tr("success", "成功"),
                self.tr("close_behavior_changed", "关闭行为已更改")
            )
    
    def on_download_threads_changed(self, value):
        """下载线程数改变时触发"""
        self.config['download_threads'] = value
        self.save_config()
    
    def on_ugoira_format_changed(self, value):
        """动图格式改变时触发"""
        self.config['ugoira_format'] = value.lower()
        self.save_config()
    
    def on_debug_log_changed(self, state):
        """调试日志开关改变时触发"""
        self.config['debug_log'] = bool(state)
        self.save_config()
    
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
