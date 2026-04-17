#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检测对话框
显示环境检测和安装进度
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, 
    QLabel, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from environment_checker import EnvironmentChecker


class SetupThread(QThread):
    """环境设置线程"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.checker = EnvironmentChecker()
    
    def run(self):
        """运行环境设置"""
        def callback(msg):
            self.progress.emit(msg)
        
        try:
            success = self.checker.full_setup(callback)
            self.finished.emit(success)
        except Exception as e:
            self.progress.emit(f"\n错误: {str(e)}")
            self.finished.emit(False)


class EnvironmentDialog(QDialog):
    """环境检测对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_thread = None
        self.init_ui()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("环境检测和设置")
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("🔧 环境检测和自动设置")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFB6C1;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 说明
        info = QLabel(
            "正在检测 Python 环境和依赖库...\n"
            "如果缺少必要的组件，将自动安装。\n"
            "此过程可能需要几分钟，请耐心等待。"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; padding: 10px;")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度模式
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #FFB6C1;
                border-radius: 5px;
                text-align: center;
                background: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FFB6C1, stop:1 #FFC0CB);
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # 日志输出
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #F5F5F5;
                border: 1px solid #DDD;
                border-radius: 5px;
                padding: 10px;
                font-family: Consolas, monospace;
                font-size: 11px;
                color: #333;
            }
        """)
        layout.addWidget(self.log_text)
        
        # 按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.setFixedHeight(40)
        self.close_btn.setEnabled(False)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #FFB6C1;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #FFC0CB;
            }
            QPushButton:disabled {
                background: #CCC;
                color: #999;
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)
    
    def start_check(self):
        """开始环境检测"""
        self.log_text.clear()
        self.log_text.append("开始环境检测...\n")
        
        # 创建并启动线程
        self.setup_thread = SetupThread()
        self.setup_thread.progress.connect(self.on_progress)
        self.setup_thread.finished.connect(self.on_finished)
        self.setup_thread.start()
    
    def on_progress(self, message):
        """更新进度"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_finished(self, success):
        """完成"""
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if success else 0)
        self.close_btn.setEnabled(True)
        
        if success:
            self.log_text.append("\n✓ 环境设置完成！可以开始使用了。")
        else:
            self.log_text.append("\n✗ 环境设置未完全成功，请查看上方日志。")
    
    def showEvent(self, event):
        """对话框显示时自动开始检测"""
        super().showEvent(event)
        # 延迟启动，确保 UI 已经显示
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.start_check)


def main():
    """测试"""
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = EnvironmentDialog()
    dialog.exec()
    sys.exit(0)


if __name__ == '__main__':
    main()
