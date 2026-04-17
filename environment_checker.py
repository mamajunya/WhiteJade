#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境检测和自动安装模块
检测 Python 环境、依赖库，并在需要时自动安装
"""

import sys
import subprocess
import json
import os
from pathlib import Path


class EnvironmentChecker:
    """环境检测器"""
    
    def __init__(self, config_path="pixiv_downloader/config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.required_packages = [
            'PyQt6',
            'pixivpy3',
            'requests',
            'gppt',
            'deepdanbooru',
            'tensorflow',
            'tensorflow-io',
            'Pillow',
            'numpy'
        ]
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except:
            return {}
    
    def save_config(self):
        """保存配置文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def check_python(self):
        """检查 Python 环境"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                return True, f"Python {version.major}.{version.minor}.{version.micro}"
            else:
                return False, f"Python 版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)"
        except:
            return False, "Python 未安装"
    
    def check_pip(self):
        """检查 pip"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, "pip 未安装"
        except:
            return False, "pip 未安装"
    
    def check_package(self, package_name):
        """检查单个包是否已安装"""
        try:
            __import__(package_name.lower().replace('-', '_'))
            return True
        except ImportError:
            return False
    
    def check_all_packages(self):
        """检查所有必需的包"""
        missing = []
        installed = []
        
        for package in self.required_packages:
            if self.check_package(package):
                installed.append(package)
            else:
                missing.append(package)
        
        return installed, missing
    
    def install_package(self, package_name, callback=None):
        """安装单个包"""
        try:
            if callback:
                callback(f"正在安装 {package_name}...")
            
            process = subprocess.Popen(
                [sys.executable, '-m', 'pip', 'install', package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # 实时输出
            for line in process.stdout:
                if callback:
                    callback(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                if callback:
                    callback(f"✓ {package_name} 安装成功")
                return True
            else:
                if callback:
                    callback(f"✗ {package_name} 安装失败")
                return False
        except Exception as e:
            if callback:
                callback(f"✗ {package_name} 安装失败: {str(e)}")
            return False
    
    def install_all_packages(self, callback=None):
        """安装所有缺失的包"""
        installed, missing = self.check_all_packages()
        
        if not missing:
            if callback:
                callback("所有依赖已安装")
            return True
        
        if callback:
            callback(f"需要安装 {len(missing)} 个包: {', '.join(missing)}")
        
        success_count = 0
        for package in missing:
            if self.install_package(package, callback):
                success_count += 1
        
        if callback:
            callback(f"\n安装完成: {success_count}/{len(missing)} 个包")
        
        return success_count == len(missing)
    
    def check_environment(self):
        """完整的环境检查"""
        results = {
            'python': self.check_python(),
            'pip': self.check_pip(),
            'packages': self.check_all_packages()
        }
        
        # 检查是否已经检查过
        if self.config.get('environment_checked'):
            results['already_checked'] = True
        else:
            results['already_checked'] = False
        
        return results
    
    def mark_as_checked(self):
        """标记环境已检查"""
        self.config['environment_checked'] = True
        self.config['last_check_time'] = str(Path(__file__).stat().st_mtime)
        self.save_config()
    
    def install_chocolatey(self, callback=None):
        """安装 Chocolatey（Windows 包管理器）"""
        if callback:
            callback("正在安装 Chocolatey...")
        
        try:
            # Chocolatey 安装脚本
            script = '''
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
'''
            
            process = subprocess.Popen(
                ['powershell.exe', '-Command', script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                if callback:
                    callback(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                if callback:
                    callback("✓ Chocolatey 安装成功")
                return True
            else:
                if callback:
                    callback("✗ Chocolatey 安装失败")
                return False
        except Exception as e:
            if callback:
                callback(f"✗ Chocolatey 安装失败: {str(e)}")
            return False
    
    def install_python_via_choco(self, callback=None):
        """通过 Chocolatey 安装 Python"""
        if callback:
            callback("正在通过 Chocolatey 安装 Python...")
        
        try:
            process = subprocess.Popen(
                ['choco', 'install', 'python', '-y'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                if callback:
                    callback(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                if callback:
                    callback("✓ Python 安装成功")
                    callback("请重启应用程序以使用新安装的 Python")
                return True
            else:
                if callback:
                    callback("✗ Python 安装失败")
                return False
        except Exception as e:
            if callback:
                callback(f"✗ Python 安装失败: {str(e)}")
            return False
    
    def full_setup(self, callback=None):
        """完整的环境设置流程"""
        if callback:
            callback("="*50)
            callback("开始环境检测和设置")
            callback("="*50)
        
        # 1. 检查 Python
        python_ok, python_msg = self.check_python()
        if callback:
            callback(f"\n1. Python 检查: {python_msg}")
        
        if not python_ok:
            if callback:
                callback("Python 环境不满足要求，需要安装")
                callback("正在安装 Chocolatey...")
            
            # 安装 Chocolatey
            if not self.install_chocolatey(callback):
                if callback:
                    callback("\n✗ 环境设置失败：无法安装 Chocolatey")
                return False
            
            # 安装 Python
            if not self.install_python_via_choco(callback):
                if callback:
                    callback("\n✗ 环境设置失败：无法安装 Python")
                return False
            
            if callback:
                callback("\n请重启应用程序")
            return False
        
        # 2. 检查 pip
        pip_ok, pip_msg = self.check_pip()
        if callback:
            callback(f"\n2. pip 检查: {pip_msg}")
        
        if not pip_ok:
            if callback:
                callback("✗ pip 未安装，请手动安装 Python")
            return False
        
        # 3. 检查和安装依赖包
        if callback:
            callback("\n3. 检查依赖包...")
        
        installed, missing = self.check_all_packages()
        if callback:
            callback(f"   已安装: {len(installed)} 个")
            callback(f"   缺失: {len(missing)} 个")
        
        if missing:
            if callback:
                callback(f"\n开始安装缺失的包: {', '.join(missing)}")
            
            if not self.install_all_packages(callback):
                if callback:
                    callback("\n✗ 部分依赖安装失败")
                return False
        
        # 4. 标记为已检查
        self.mark_as_checked()
        
        if callback:
            callback("\n" + "="*50)
            callback("✓ 环境设置完成！")
            callback("="*50)
        
        return True


def main():
    """命令行测试"""
    checker = EnvironmentChecker()
    
    def print_callback(msg):
        print(msg)
    
    checker.full_setup(print_callback)


if __name__ == '__main__':
    main()
