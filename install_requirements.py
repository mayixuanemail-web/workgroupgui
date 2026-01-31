#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
脚本依赖库安装工具
自动安装所有必需的Python库
"""
import subprocess
import sys

def install_requirements():
    """安装所有依赖"""
    print("=" * 60)
    print("🚀 脚本管理工具 - 依赖库安装程序")
    print("=" * 60)
    print()
    
    requirements = [
        "streamlit==1.53.1",
        "pandas",
        "openpyxl",
        "Pillow",
        "PyMuPDF",
        "altair",
    ]
    
    print("📦 准备安装以下库：")
    for lib in requirements:
        print(f"  ✓ {lib}")
    print()
    
    input("按 Enter 键开始安装... (按 Ctrl+C 可取消)")
    print()
    
    try:
        # 升级 pip
        print("⬆️  升级 pip...")
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip",
            "-i",
            "https://pypi.tuna.tsinghua.edu.cn/simple",
        ])
        print("✅ pip 升级完成\n")
        
        # 安装所有库
        for lib in requirements:
            print(f"📥 正在安装: {lib}...")
            subprocess.check_call([
                sys.executable,
                "-m",
                "pip",
                "install",
                lib,
                "-i",
                "https://pypi.tuna.tsinghua.edu.cn/simple",
            ])
            print(f"✅ {lib} 安装成功\n")
        
        print("=" * 60)
        print("✨ 所有依赖库安装完成！")
        print("=" * 60)
        print()
        print("下一步：")
        print("  1. 在此目录运行：python main_gui.py")
        print("  或")
        print("  2. 双击 main_gui.exe 运行")
        print()
        
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print(f"❌ 安装出错: {e}")
        print("=" * 60)
        print()
        print("请检查：")
        print("  1. 网络连接是否正常")
        print("  2. Python 是否正确安装")
        print("  3. 尝试手动运行：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple streamlit pandas openpyxl Pillow PyMuPDF altair")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print()
        print("⚠️  安装已取消")
        sys.exit(0)

if __name__ == "__main__":
    install_requirements()
    
    # 保持窗口打开
    input("\n按 Enter 键关闭窗口...")
