@echo off
chcp 65001 >nul
setlocal

echo ============================================================
echo 脚本管理工具 - 依赖库安装程序
echo ============================================================
echo.
echo 正在安装所有必需的Python库...
echo.

python -m pip install --upgrade pip
python -m pip install streamlit==1.53.1 pandas openpyxl Pillow PyMuPDF altair

echo.
echo ============================================================
echo 安装完成！
echo ============================================================
echo.
echo 下一步：
echo   1. 在此目录运行：python main_gui.py
echo   或
echo   2. 双击 main_gui.exe 运行
echo.

pause
