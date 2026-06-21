/**
 * 知识图谱智能问答系统 — 前端交互逻辑
 */

// ========== 状态 ==========
const state = {
  isLoading: false,
  messageCount: 0,
};

// ========== DOM 引用 ==========
const el = {
  messages: document.getElementById("messages"),
  form: document.getElementById("chat-form"),
  input: document.getElementById("question-input"),
  sendBtn: document.getElementById("send-btn"),
  entityCount: document.getElementById("entity-count"),
  relationCount: document.getElementById("relation-count"),
};

// ========== 初始化 ==========
document.addEventListener("DOMContentLoaded", () => {
  loadStats();
  setupEventListeners();
  autoResizeInput();
});

// ========== 统计信息加载 ==========
async function loadStats() {
  try {
    const res = await fetch("/stats");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    animateCounter(el.entityCount, data.entity_count);
    animateCounter(el.relationCount, data.relation_count);
  } catch (err) {
    console.warn("加载统计信息失败:", err.message);
  }
}

function animateCounter(element, target) {
  if (!element) return;
  const duration = 1000;
  const start = performance.now();

  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    // easeOutExpo
    const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
    const current = Math.round(eased * target);
    element.textContent = current;
    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

// ========== 事件绑定 ==========
function setupEventListeners() {
  // 发送消息
  el.form.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage();
  });

  // Enter 发送（Shift+Enter 换行）
  el.input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // 自动调整输入框高度
  el.input.addEventListener("input", autoResizeInput);

  // 建议问题点击
  document.querySelectorAll(".suggested-question").forEach((btn) => {
    btn.addEventListener("click", () => {
      el.input.value = btn.textContent;
      sendMessage();
    });
  });
}

function autoResizeInput() {
  el.input.style.height = "auto";
  el.input.style.height = Math.min(el.input.scrollHeight, 120) + "px";
}

// ========== 发送消息 ==========
async function sendMessage() {
  const question = el.input.value.trim();
  if (!question || state.isLoading) return;

  // 如果还有欢迎消息，清除它
  const welcome = document.getElementById("welcome-message");
  if (welcome) welcome.remove();

  // 显示用户消息
  appendMessage("user", question);
  el.input.value = "";
  el.input.style.height = "auto";

  // 显示加载状态
  state.isLoading = true;
  el.sendBtn.disabled = true;
  const loadingId = appendLoadingMessage();

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(`服务器错误 (${res.status}): ${errText}`);
    }

    const data = await res.json();

    // 移除加载状态，显示回答
    removeLoadingMessage(loadingId);
    appendMessage("assistant", data.answer);
  } catch (err) {
    // 移除加载状态，显示错误
    removeLoadingMessage(loadingId);
    appendMessage("system", `⚠️ ${err.message}`);
    console.error("请求失败:", err);
  } finally {
    state.isLoading = false;
    el.sendBtn.disabled = false;
    el.input.focus();
  }
}

// ========== 消息渲染 ==========
function appendMessage(role, content) {
  const div = document.createElement("div");
  div.className = `message ${role}`;

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";
  bubble.textContent = content;

  div.appendChild(bubble);
  el.messages.appendChild(div);

  state.messageCount++;
  scrollToBottom();
}

function appendLoadingMessage() {
  const id = "loading-" + Date.now();

  const div = document.createElement("div");
  div.className = "message assistant loading";
  div.id = id;

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  const loadingText = document.createElement("div");
  loadingText.className = "loading-text";
  loadingText.textContent = "正在查询知识图谱";

  const indicator = document.createElement("div");
  indicator.className = "typing-indicator";
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement("span");
    indicator.appendChild(dot);
  }

  bubble.appendChild(loadingText);
  bubble.appendChild(indicator);
  div.appendChild(bubble);
  el.messages.appendChild(div);

  scrollToBottom();
  return id;
}

function removeLoadingMessage(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    el.messages.scrollTop = el.messages.scrollHeight;
  });
}
