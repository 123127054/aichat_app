"""
数据库初始化脚本
用于创建数据库表结构
可能不可用，我把sql语句放在这里
“
CREATE DATABASE chatdb CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '多会话聊天数据库';
”
“
CREATE TABLE chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    session_id VARCHAR(64) NOT NULL UNIQUE COMMENT '会话唯一标识',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天会话表';
”
“
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    session_id VARCHAR(64) NOT NULL COMMENT '所属会话ID',
    role ENUM('human', 'system') NOT NULL COMMENT '角色（human:用户，system:模型）',
    content TEXT NOT NULL COMMENT '消息内容',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '消息时间戳',
    INDEX idx_session_id (session_id),
    CONSTRAINT fk_session FOREIGN KEY (session_id)
        REFERENCES chat_sessions(session_id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天消息表';
”
"""

from flask import Flask
from models import db
from config import Config

# 创建临时 Flask 应用
app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化数据库
db.init_app(app)

# 在应用上下文中创建所有表
with app.app_context():
    db.create_all()
    print("✅ 数据库表已创建")


