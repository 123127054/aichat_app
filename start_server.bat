@echo off
echo 正在启动聊天应用服务器...

REM 创建日志目录
if not exist logs mkdir logs

REM 使用 Gunicorn 启动应用
python -m gunicorn -c gunicorn_config.py run:app

echo 服务器已停止
pause