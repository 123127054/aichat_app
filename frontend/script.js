// 全局变量
let sessions = [];
let currentSessionId = "";
const API_BASE_URL = window.location.origin; // 自动获取当前域名作为API基础URL
// 添加一个变量来跟踪当前请求
let currentRequest = null;

// DOM 元素
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const newChatBtn = document.getElementById("new-chat-btn");
const chatContainer = document.getElementById("chat-container");
const sessionList = document.getElementById("session-list");
const currentSessionTitle = document.getElementById("current-session-title");

// 初始化函数
function init() {
  // 从本地存储加载会话
  loadSessionsFromStorage();
  
  // 如果没有会话，创建一个新会话
  if (sessions.length === 0) {
    createSession();
  } else {
    // 加载最近的会话
    currentSessionId = sessions[0].id;
    renderSessionList();
    loadSessionMessages(currentSessionId);
  }
  
  // 添加事件监听器
  userInput.addEventListener("keydown", handleInputKeydown);
  sendBtn.addEventListener("click", sendMessage);
  newChatBtn.addEventListener("click", createSession);
  
  // 自动聚焦输入框
  userInput.focus();
}

// 创建新会话
function createSession() {
  // 取消当前正在进行的请求
  cancelCurrentRequest();
  
  const sessionId = "session-" + Date.now();
  const sessionName = "新对话 " + new Date().toLocaleTimeString();
  
  const newSession = {
    id: sessionId,
    name: sessionName,
    messages: []
  };
  
  // 添加到会话列表的开头
  sessions.unshift(newSession);
  currentSessionId = sessionId;
  
  // 更新UI
  renderSessionList();
  clearChatContainer();
  showWelcomeMessage();
  
  // 保存到本地存储
  saveSessionsToStorage();
  
  // 更新标题
  updateSessionTitle(sessionName);
  
  // 向后端注册会话
  registerSessionWithBackend(sessionId);
  
  // 聚焦输入框
  userInput.focus();
}

// 向后端注册会话
function registerSessionWithBackend(sessionId) {
  fetch(`${API_BASE_URL}/session`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId
    })
  })
  .then(response => response.json())
  .then(data => {
    if (!data.success) {
      console.error("注册会话失败:", data.error);
    }
  })
  .catch(error => {
    console.error("注册会话请求错误:", error);
  });
}

// 渲染会话列表
function renderSessionList() {
  sessionList.innerHTML = "";
  
  sessions.forEach(session => {
    const sessionItem = document.createElement("div");
    sessionItem.className = `session-item ${session.id === currentSessionId ? 'active' : ''}`;
    sessionItem.dataset.id = session.id;
    
    sessionItem.innerHTML = `
      <div class="session-name">
        <i class="bi bi-chat-dots"></i>
        <span>${session.name}</span>
      </div>
      <button class="btn btn-sm delete-btn" data-id="${session.id}">
        <i class="bi bi-trash"></i>
      </button>
    `;
    
    sessionItem.addEventListener("click", (e) => {
      if (!e.target.closest('.delete-btn')) {
        switchSession(session.id);
      }
    });
    
    sessionList.appendChild(sessionItem);
  });
  
  // 添加删除按钮事件
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteSession(btn.dataset.id);
    });
  });
}

// 切换会话
function switchSession(sessionId) {
  if (currentSessionId === sessionId) return;
  
  // 取消当前正在进行的请求
  cancelCurrentRequest();
  
  currentSessionId = sessionId;
  renderSessionList();
  
  // 加载会话消息
  loadSessionMessages(sessionId);
  
  // 更新标题
  const session = sessions.find(s => s.id === sessionId);
  if (session) {
    updateSessionTitle(session.name);
  }
}

// 取消当前请求
function cancelCurrentRequest() {
  if (currentRequest && currentRequest.signal && !currentRequest.signal.aborted) {
    currentRequest.abort();
    removeLoadingIndicator();
  }
}

// 加载会话消息
function loadSessionMessages(sessionId) {
  clearChatContainer();
  
  const session = sessions.find(s => s.id === sessionId);
  if (!session) return;
  
  if (session.messages.length === 0) {
    showWelcomeMessage();
    return;
  }
  
  session.messages.forEach(msg => {
    appendMessage(msg.role, msg.content);
  });
  
  // 滚动到底部
  scrollToBottom();
}

// 删除会话
function deleteSession(sessionId) {
  if (confirm("确定要删除这个对话吗？")) {
    const index = sessions.findIndex(s => s.id === sessionId);
    if (index !== -1) {
      sessions.splice(index, 1);
      
      // 如果删除的是当前会话，切换到第一个会话或创建新会话
      if (sessionId === currentSessionId) {
        if (sessions.length > 0) {
          switchSession(sessions[0].id);
        } else {
          createSession();
        }
      } else {
        renderSessionList();
      }
      
      // 保存到本地存储
      saveSessionsToStorage();
    }
  }
}

// 发送消息
function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;
  
  // 清空输入框
  userInput.value = "";
  
  // 显示用户消息
  appendMessage("human", message);
  
  // 保存消息
  saveMessageToSession("human", message);
  
  // 显示加载指示器
  showLoadingIndicator();
  
  // 保存当前会话ID，用于后续验证
  const requestSessionId = currentSessionId;
  
  // 取消之前的请求
  cancelCurrentRequest();
  
  // 创建AbortController用于取消请求
  const controller = new AbortController();
  currentRequest = controller;
  
  // 发送到后端
  fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: requestSessionId,
      message: message,
    }),
    signal: controller.signal
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    // 移除加载指示器
    removeLoadingIndicator();
    
    // 检查当前会话ID是否与请求时的会话ID一致
    if (requestSessionId !== currentSessionId) {
      console.log("会话已切换，忽略响应");
      return;
    }
    
    if (data.reply) {
      // 显示系统回复
      appendMessage("system", data.reply);
      
      // 保存消息
      saveMessageToSession("system", data.reply);
      
      // 更新会话名称（如果是第一条消息）
      const session = sessions.find(s => s.id === currentSessionId);
      if (session && session.messages.length <= 2) {
        // 使用用户的第一条消息作为会话名称
        updateSessionName(currentSessionId, truncateString(message, 20));
      }
    } else {
      appendMessage("system", "错误: " + (data.error || "未知错误"));
    }
  })
  .catch(error => {
    // 如果是取消请求导致的错误，不显示错误信息
    if (error.name === 'AbortError') {
      console.log('请求已取消');
      return;
    }
    
    // 移除加载指示器
    removeLoadingIndicator();
    
    // 检查当前会话ID是否与请求时的会话ID一致
    if (requestSessionId !== currentSessionId) {
      console.log("会话已切换，忽略错误");
      return;
    }
    
    appendMessage("system", "请求错误: " + error.message);
  });
  
  // 调整输入框高度
  userInput.style.height = "auto";
}

// 显示加载指示器
function showLoadingIndicator() {
  const loadingDiv = document.createElement("div");
  loadingDiv.className = "message system loading";
  loadingDiv.innerHTML = `
    <div class="typing-indicator">
      <span></span>
      <span></span>
      <span></span>
    </div>
  `;
  chatContainer.appendChild(loadingDiv);
  scrollToBottom();
}

// 移除加载指示器
function removeLoadingIndicator() {
  const loadingIndicator = document.querySelector(".loading");
  if (loadingIndicator) {
    loadingIndicator.remove();
  }
}

// 添加消息到聊天容器
function appendMessage(role, content) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${role}`;
  
  // 使用marked.js解析Markdown
  messageDiv.innerHTML = marked.parse(content);
  
  chatContainer.appendChild(messageDiv);
  scrollToBottom();
}

// 保存消息到会话
function saveMessageToSession(role, content) {
  const session = sessions.find(s => s.id === currentSessionId);
  if (session) {
    session.messages.push({ role, content });
    saveSessionsToStorage();
  }
}

// 更新会话名称
function updateSessionName(sessionId, name) {
  const session = sessions.find(s => s.id === sessionId);
  if (session) {
    session.name = name;
    renderSessionList();
    updateSessionTitle(name);
    saveSessionsToStorage();
  }
}

// 更新会话标题
function updateSessionTitle(title) {
  currentSessionTitle.textContent = title;
}

// 清空聊天容器
function clearChatContainer() {
  chatContainer.innerHTML = "";
}

// 显示欢迎消息
function showWelcomeMessage() {
  const welcomeDiv = document.createElement("div");
  welcomeDiv.className = "welcome-message";
  welcomeDiv.innerHTML = `
    <h2>欢迎使用 AI 智能助手</h2>
    <p>我可以帮助您回答问题、提供建议或进行日常对话。</p>
  `;
  chatContainer.appendChild(welcomeDiv);
}

// 滚动到底部
function scrollToBottom() {
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 处理输入框按键事件
function handleInputKeydown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
  
  // 自动调整输入框高度
  setTimeout(() => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
  }, 0);
}

// 保存会话到本地存储
function saveSessionsToStorage() {
  localStorage.setItem("chat-sessions", JSON.stringify(sessions));
}

// 从本地存储加载会话
function loadSessionsFromStorage() {
  const storedSessions = localStorage.getItem("chat-sessions");
  if (storedSessions) {
    try {
      sessions = JSON.parse(storedSessions);
    } catch (e) {
      console.error("Failed to parse stored sessions:", e);
      sessions = [];
    }
  }
}

// 辅助函数：截断字符串
function truncateString(str, maxLength) {
  if (str.length <= maxLength) return str;
  return str.substring(0, maxLength) + "...";
}

// 初始化应用
document.addEventListener("DOMContentLoaded", init);
