"""
主应用模块
提供 Flask 应用实例和 API 路由
"""
from flask import Flask, request, jsonify, send_from_directory
from config import Config
from models import db
from services import chat_with_model, get_session_exists, get_or_create_session
from flask_cors import CORS  # 添加CORS支持
import logging
import os
from datetime import datetime

# 创建日志目录
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
log_file = os.path.join(log_dir, f'chat_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建 Flask 应用实例
app = Flask(__name__)
# 从配置对象加载配置
app.config.from_object(Config)
# 初始化数据库
db.init_app(app)
# 添加CORS支持
CORS(app)

# 添加创建会话的API端点
@app.route("/session", methods=["POST"])
def create_session():
    """
    创建新会话 API 端点
    
    请求体:
    {
        "session_id": "会话ID"
    }
    
    响应:
    {
        "success": true
    }
    """
    data = request.json
    session_id = data.get("session_id")
    
    if not session_id:
        logger.warning("创建会话请求缺少会话ID")
        return jsonify({"error": "缺少会话ID"}), 400
    
    try:
        # 创建会话
        get_or_create_session(session_id)
        logger.info(f"成功创建会话: {session_id}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"创建会话时出错: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    """
    聊天 API 端点
    接收用户输入并返回模型回复
    
    请求体:
    {
        "session_id": "会话ID",
        "message": "用户消息"
    }
    
    响应:
    {
        "reply": "模型回复"
    }
    """
    data = request.json
    session_id = data.get("session_id")
    message = data.get("message")
    
    if not session_id or not message:
        logger.warning(f"请求缺少必要参数: {data}")
        return jsonify({"error": "缺少必要参数"}), 400
    
    # 记录用户输入
    logger.info(f"会话 [{session_id}] 用户输入: {message}")
    
    # 验证会话是否存在，如果不存在则自动创建
    if not get_session_exists(session_id):
        logger.warning(f"会话不存在，自动创建: {session_id}")
        get_or_create_session(session_id)
    
    try:
        reply = chat_with_model(session_id, message)
        # 记录模型回复
        logger.info(f"会话 [{session_id}] 模型回复: {reply}")
        return jsonify({"reply": reply})
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# 添加日志查看API
@app.route("/logs", methods=["GET"])
def get_logs():
    """获取日志列表"""
    logs = []
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            logs.append(filename)
    return jsonify({"logs": logs})

@app.route("/logs/<filename>", methods=["GET"])
def view_log(filename):
    """查看特定日志文件"""
    if not filename.endswith('.log'):
        return jsonify({"error": "无效的日志文件名"}), 400
    
    log_path = os.path.join(log_dir, filename)
    if not os.path.exists(log_path):
        return jsonify({"error": "日志文件不存在"}), 404
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        return jsonify({"content": content})
    except Exception as e:
        logger.error(f"读取日志文件时出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 添加静态文件服务
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('frontend', 'admin.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('frontend', path)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
