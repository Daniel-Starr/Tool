#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工程建设数据与三维模型自动挂接工具 - PyInstaller打包脚本
用于生成Windows可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_packages = [
        'PyInstaller',
        'pandas', 
        'openpyxl',
        'fuzzywuzzy',
        'py7zr',
        'python-Levenshtein'  # 用于提升fuzzywuzzy性能
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'python-Levenshtein':
                __import__('Levenshtein')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("缺少以下依赖包:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n请先安装这些包:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("所有依赖包检查通过")
    return True

def clean_build():
    """清理之前的构建文件"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name, ignore_errors=True)
    
    import glob
    for pattern in files_to_clean:
        for file in glob.glob(pattern):
            print(f"清理文件: {file}")
            os.remove(file)

def create_spec_file():
    """创建PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Pygui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pandas',
        'openpyxl',
        'fuzzywuzzy',
        'py7zr',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'threading',
        'logging',
        'weakref',
        'gc',
        'subprocess',
        'json',
        'concurrent.futures',
        'extract_ui',
        'transition_ui', 
        'parmeter_ui',
        'matcher_ui',
        'load_ui',
        'save_excel_ui',
        'compress_ui',
        'device_display_ui'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy.distutils',
        'scipy',
        'PIL',
        'IPython',
        'jupyter',
        'notebook'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='工程数据模型挂接工具',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version_file=None,
)
'''
    
    with open('工程数据模型挂接工具.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("已创建 PyInstaller spec 文件")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 使用spec文件构建
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '工程数据模型挂接工具.spec'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print("构建成功!")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("构建失败:")
        print(f"错误代码: {e.returncode}")
        print(f"错误输出: {e.stderr}")
        return False
    
    return True

def post_build_tasks():
    """构建后处理"""
    exe_path = Path("dist/工程数据模型挂接工具.exe")
    
    if exe_path.exists():
        file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
        print(f"可执行文件大小: {file_size:.1f} MB")
        print(f"可执行文件位置: {exe_path.absolute()}")
        
        # 创建快捷方式说明文件
        readme_content = """工程建设数据与三维模型自动挂接工具

使用说明:
1. 双击运行"工程数据模型挂接工具.exe"
2. 按照界面提示依次执行操作步骤
3. 支持的功能:
   - 导入GIM文件
   - 导出设备清单
   - 参数文件处理
   - 自动挂接匹配
   - 数据载入
   - 结果保存

注意事项:
- 确保有足够的磁盘空间处理大型文件
- 首次运行可能需要一些时间来初始化
- 如遇到问题，请检查输入文件格式是否正确

技术支持:
如有问题请联系开发团队
"""
        
        with open("dist/使用说明.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("已创建使用说明文件")
        
        # 尝试打开输出目录
        try:
            if os.name == 'nt':  # Windows
                os.startfile("dist")
            else:
                subprocess.run(["open", "dist"])
        except:
            pass
        
        return True
    else:
        print("未找到生成的可执行文件")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("工程数据模型挂接工具 - 打包脚本")
    print("=" * 60)
    
    # 检查当前目录
    if not os.path.exists("Pygui.py"):
        print("错误: 请在项目根目录下运行此脚本")
        return False
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 清理之前的构建
    clean_build()
    
    # 创建spec文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_executable():
        return False
    
    # 后处理
    if not post_build_tasks():
        return False
    
    print("\n" + "=" * 60)
    print("打包完成!")
    print("可执行文件位于 dist/ 目录中")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    print("\n按回车键退出..." if success else "\n打包失败，按回车键退出...")
    try:
        input()
    except:
        pass