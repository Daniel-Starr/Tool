@echo off
chcp 65001 >nul
echo ===============================================
echo 工程数据模型挂接工具 - 自动安装和打包脚本
echo ===============================================
echo.

echo 第一步：安装依赖包...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo 依赖包安装失败！
    pause
    exit /b 1
)
echo ✅ 依赖包安装完成
echo.

echo 第二步：开始打包可执行文件...
python build_exe.py
if %ERRORLEVEL% neq 0 (
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo ===============================================
echo 🎉 打包完成！
echo 可执行文件已生成在 dist 目录中
echo ===============================================
pause