# 🚀 脚本管理工具 - 安装说明

## 首次安装步骤

### Windows 用户（推荐）

**方法一：双击安装（最简单）**
1. 双击 `install_requirements.bat`
2. 等待安装完成
3. 安装完后双击 `main_gui.exe` 使用

**方法二：命令行安装**
```powershell
python install_requirements.py
```

### Mac / Linux 用户

```bash
bash install_requirements.sh
# 或
python3 install_requirements.py
```

### 手动安装（如果上述方法失败）

```powershell
pip install -r requirements.txt
```

## 运行应用

### 方式一：双击运行（推荐）
- Windows: 双击 `main_gui.exe`
- 其他系统: 运行 `python main_gui.py`

### 方式二：命令行运行
```powershell
streamlit run main_gui.py
```

## 文件说明

| 文件 | 说明 |
|-----|------|
| `main_gui.exe` | Windows 可执行文件（仅包含Python运行时，不包含库） |
| `main_gui.py` | Python 源程序 |
| `install_requirements.bat` | Windows 自动安装脚本 |
| `install_requirements.py` | Python 跨平台安装脚本 |
| `install_requirements.sh` | Linux/Mac 安装脚本 |
| `requirements.txt` | 依赖库列表（pip使用） |
| `*.py` | 所有功能脚本 |
| `README.md` | 详细使用说明 |

## 系统要求

- **Python 3.8+** （自动包含在 .exe 中）
- **网络连接**（首次安装需要下载库文件，约300-500MB）
- **磁盘空间**：至少 500MB 可用空间

## 常见问题

**Q: 为什么要单独安装库？**  
A: 这样 .exe 文件会很小（只有 50-100MB），如果打包所有库会很大（150-200MB）

**Q: 安装后能离线使用吗？**  
A: 是的，安装完后完全不需要网络就能运行

**Q: 如果不小心删除了脚本文件怎么办？**  
A: 重新解压下载的文件即可

## 技术细节

- `.exe` 文件仅包含 Python 运行时环境
- 所有第三方库（streamlit、pandas等）需要用户首次安装
- 库文件安装在用户的 Python site-packages 中，与 .exe 独立
- 这样做的好处是 .exe 体积小，更易分发和传输
