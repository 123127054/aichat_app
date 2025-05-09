"""
服务层模块
提供业务逻辑处理函数
"""
from models import db, ChatSession, ChatMessage
from langchain.schema import HumanMessage, SystemMessage
# 修改导入路径，从 langchain_community 导入 ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
from config import Config
import logging

# 获取日志记录器
logger = logging.getLogger(__name__)

def get_or_create_session(session_id):
    """
    获取或创建聊天会话
    
    参数:
        session_id (str): 会话ID
        
    返回:
        ChatSession: 会话对象
    """
    session = ChatSession.query.filter_by(session_id=session_id).first()
    if not session:
        logger.info(f"创建新会话: {session_id}")
        session = ChatSession(session_id=session_id)
        db.session.add(session)
        db.session.commit()
    return session

def get_session_exists(session_id):
    """
    检查会话是否存在
    
    参数:
        session_id (str): 会话ID
        
    返回:
        bool: 会话是否存在
    """
    session = ChatSession.query.filter_by(session_id=session_id).first()
    return session is not None

def get_chat_history(session_id):
    """
    获取指定会话的聊天历史
    
    参数:
        session_id (str): 会话ID
        
    返回:
        list: 聊天消息列表，转换为 LangChain 消息格式
    """
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.id).all()
    history = []
    for m in messages:
        if m.role == "human":
            history.append(HumanMessage(content=m.content))
        else:
            history.append(SystemMessage(content=m.content))
    return history

def save_message(session_id, role, content):
    """
    保存聊天消息到数据库
    
    参数:
        session_id (str): 会话ID
        role (str): 消息角色 ("human" 或 "system")
        content (str): 消息内容
    """
    msg = ChatMessage(session_id=session_id, role=role, content=content)
    db.session.add(msg)
    db.session.commit()

def chat_with_model(session_id, user_input):
    """
    处理用户输入并获取模型回复
    
    参数:
        session_id (str): 会话ID
        user_input (str): 用户输入的消息
        
    返回:
        str: 模型的回复内容
    """
    # 确保会话存在
    get_or_create_session(session_id)
    # 获取历史消息
    history = get_chat_history(session_id)
    # 添加当前用户消息
    history.append(HumanMessage(content=user_input))

    logger.info(f"调用模型 [{Config.MODEL_NAME}] 处理会话 [{session_id}]")
    
    # 初始化 LLM
    llm = ChatOpenAI(
        openai_api_key=Config.OPENAI_API_KEY,
        openai_api_base=Config.OPENAI_API_BASE,
        model_name=Config.MODEL_NAME
    )

    # 调用模型获取回复
    response = llm.invoke(history)

    # 保存对话记录
    save_message(session_id, "human", user_input)
    save_message(session_id, "system", response.content)

    return response.content
