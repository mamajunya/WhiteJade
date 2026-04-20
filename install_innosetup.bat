@echo off
chcp 65001 >nul

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo 需要管理员权限，正在请求提升...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

echo ========================================
echo 安装 Inno Setup
echo ========================================
echo.

choco install innosetup -y

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Inno Setup 安装成功！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 安装失败，请手动安装
    echo 下载地址: https://jrsoftware.org/isdl.php
    echo ========================================
)

pause
