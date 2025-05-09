@echo off
chcp 65001 >nul
echo 正在启动聊天应用服务器...

REM 创建日志目录
if not exist logs mkdir logs

REM 使用 Waitress 启动应用
python run.py

echo 服务器已停止
pause