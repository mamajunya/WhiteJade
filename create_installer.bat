@echo off
chcp 65001 >nul
echo ========================================
echo WhiteJade 安装包制作脚本
echo ========================================
echo.

REM 检查 Inno Setup 是否安装
set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist "%ISCC%" (
    echo [错误] 未找到 Inno Setup 编译器
    echo.
    echo 请先安装 Inno Setup:
    echo 1. 访问: https://jrsoftware.org/isdl.php
    echo 2. 下载并安装 Inno Setup 6
    echo 3. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo [1/2] 检查打包文件...
if not exist "dist\WhiteJade\WhiteJade.exe" (
    echo [错误] 未找到打包文件
    echo 请先运行 build.bat 进行打包
    pause
    exit /b 1
)

echo [2/2] 创建安装包...
"%ISCC%" installer.iss

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 安装包创建成功！
    echo 输出目录: installer_output\
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 安装包创建失败！
    echo ========================================
)

pause
