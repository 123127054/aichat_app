# 应用启动脚本
# 用于启动 Flask 应用
# Windows 系统使用 Waitress，Linux/Unix 系统可使用 Gunicorn

from app import app
import platform
import os

# 检测操作系统类型
if __name__ == "__main__":
    system = platform.system()
    if system == "Windows":
        # Windows 系统使用 Waitress
        from waitress import serve
        print("在 Windows 系统上使用 Waitress 启动应用...")
        serve(app, host='0.0.0.0', port=5000)
    else:
        # Linux/Unix 系统可以使用 Gunicorn
        print("在非 Windows 系统上使用 Flask 开发服务器启动应用...")
        app.run(host='0.0.0.0', port=5000)