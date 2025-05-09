"""
配置模块
存储应用的配置参数
"""
import os

class Config:
    """应用配置类"""
    # 数据库连接 URI
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://root:123456@localhost:3306/chatdb?charset=utf8mb4"
    )
    # 是否追踪数据库修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # OpenAI API 密钥
    OPENAI_API_KEY = "sk-csnkwjxdrxkxuhuxcqikdelgbhwyadipixeqwlgscpwdrlsx"
    # OpenAI API 基础 URL
    OPENAI_API_BASE = "https://api.siliconflow.cn/v1/"
    # 使用的模型名称
    MODEL_NAME = "Qwen/Qwen3-235B-A22B"