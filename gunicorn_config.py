# Gunicorn 配置文件
# 绑定的IP和端口
bind = "0.0.0.0:5000"

# 工作进程数
workers = 4

# 工作模式
worker_class = "sync"

# 超时时间
timeout = 120

# 日志级别
loglevel = "info"

# 是否后台运行
daemon = False

# 进程名称
proc_name = "chat_app"

# 访问日志文件
accesslog = "logs/access.log"

# 错误日志文件
errorlog = "logs/error.log"