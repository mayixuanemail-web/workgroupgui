#!/bin/bash
# 脚本管理工具 - Linux/Mac 依赖库安装脚本

echo "============================================================"
echo "脚本管理工具 - 依赖库安装程序"
echo "============================================================"
echo ""

echo "升级 pip..."
python3 -m pip install --upgrade pip

echo "安装依赖库..."
python3 -m pip install streamlit==1.53.1 pandas openpyxl Pillow PyMuPDF altair

echo ""
echo "============================================================"
echo "安装完成！"
echo "============================================================"
echo ""
echo "下一步运行：python3 main_gui.py"
echo ""
