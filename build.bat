@echo off
chcp 65001 >nul
echo ========================================
echo WhiteJade 打包脚本
echo ========================================
echo.
echo 正在打包应用程序...
echo.

pyinstaller WhiteJade_simple.spec --clean --noconfirm

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 打包完成！
    echo 输出目录: dist\WhiteJade\
    echo ========================================
) else (
    echo.
    echo ========================================
    echo 打包失败！请检查错误信息。
    echo ========================================
)

pause
