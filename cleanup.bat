@echo off
REM 打包后清理脚本 - 删除不需要的文件和文件夹

echo ============================================================
echo 清理打包临时文件...
echo ============================================================
echo.

if exist temp (
    echo 删除 temp 文件夹...
    rmdir /s /q temp
    echo ✓ temp 文件夹已删除
)

if exist build (
    echo 删除 build 文件夹...
    rmdir /s /q build
    echo ✓ build 文件夹已删除
)

if exist main_gui.spec (
    echo 删除 main_gui.spec 文件...
    del main_gui.spec
    echo ✓ main_gui.spec 已删除
)

echo.
echo ============================================================
echo 清理完成！现在工作目录只包含：
echo   - main_gui.exe (主程序)
echo   - 所有 .py 脚本文件
echo   - 配置和安装文件
echo ============================================================
echo.

pause
