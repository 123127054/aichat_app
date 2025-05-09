"""
数据模型模块
定义应用使用的数据库模型
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建 SQLAlchemy 实例
db = SQLAlchemy()

class ChatSession(db.Model):
    """
    聊天会话模型
    存储用户的聊天会话信息
    """
    __tablename__ = "chat_sessions"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    """
    聊天消息模型
    存储会话中的消息记录
    """
    __tablename__ = "chat_messages"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), nullable=False)
    role = db.Column(db.Enum("human", "system"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
