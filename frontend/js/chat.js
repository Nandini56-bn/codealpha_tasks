/**
 * Gemini chatbot UI — natural language Assistant Panel matching reference design.
 */
class ChatController {
  constructor() {
    this.messagesContainer = null;
    this.inputEl = null;
    this.sendBtn = null;
    this.lastSpec = null;
    this.onGenerateSpec = null;
    this.onGenerateLyrics = null;
  }

  init(messagesId = "chat-messages", inputId = "chat-input", sendBtnId = "chat-send-btn") {
    this.messagesContainer = document.getElementById(messagesId);
    this.inputEl = document.getElementById(inputId);
    this.sendBtn = document.getElementById(sendBtnId);
    if (!this.inputEl || !this.sendBtn) return;
    this.sendBtn.addEventListener("click", () => this.sendMessage());
    this.inputEl.addEventListener("keypress", (e) => {
      if (e.key === "Enter") this.sendMessage();
    });
  }

  async sendMessage(customText = null, options = {}) {
    const text = customText || this.inputEl.value.trim();
    if (!text) return;
    if (!customText) this.inputEl.value = "";
    this.appendMessage("user", text);
    const typingId = this.appendTypingIndicator();
    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, interpret: true })
      });
      const data = await response.json();
      this.removeTypingIndicator(typingId);
      if (data.status === "error") {
        this.appendMessage("assistant", data.reply, true);
        return data;
      }
      this.appendMessage("assistant", data.reply, false, data.music_spec);
      if (data.music_spec) {
        this.lastSpec = data.music_spec;
      }
      if (options.autoGenerate && data.music_spec && this.onGenerateSpec) {
        await this.onGenerateSpec(text, data.music_spec);
      }
      if (options.autoLyrics && this.onGenerateLyrics) {
        await this.onGenerateLyrics(text, data.music_spec);
      }
      return data;
    } catch (err) {
      this.removeTypingIndicator(typingId);
      this.appendMessage("assistant", `Could not reach the backend: ${err.message}`, true);
      return null;
    }
  }

  appendMessage(sender, text, isError = false, spec = null) {
    if (!this.messagesContainer) return;
    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-bubble ${sender}-bubble ${isError ? "error-bubble" : ""}`;
    let extraHTML = "";
    if (spec) {
      const btnId = "msg-gen-btn-" + Date.now();
      extraHTML = `
        <div style="margin-top:10px; padding:10px; background:rgba(0,0,0,0.35); border-radius:12px; border:1px solid rgba(255,255,255,0.15); font-size:12px;">
          <div style="color:#06b6d4; font-weight:700; margin-bottom:4px;">Music Specification:</div>
          <div><strong>Style:</strong> ${this.escape(spec.genre || "Mass / Indian")}</div>
          <div><strong>Source:</strong> Lyria (AI Audio)</div>
          <div><strong>Mood:</strong> ${this.escape(spec.mood || "Energetic")}</div>
          <div style="margin-top:10px; display:flex; gap:8px;">
            <button type="button" class="btn-primary" id="${btnId}" style="padding:6px 14px; font-size:11px;">⚡ Play Music</button>
          </div>
        </div>
      `;
      setTimeout(() => {
        const btn = document.getElementById(btnId);
        if (btn && this.onGenerateSpec) {
          btn.addEventListener("click", () => this.onGenerateSpec(spec.original_request || text, spec));
        }
      }, 50);
    }
    msgDiv.innerHTML = `
      <div class="bubble-sender">${sender === "user" ? "You" : "AI Assistant"}</div>
      <div class="bubble-text">${this.formatText(text)}${extraHTML}</div>
    `;
    this.messagesContainer.appendChild(msgDiv);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  appendTypingIndicator() {
    const typingDiv = document.createElement("div");
    const id = "typing-" + Date.now();
    typingDiv.id = id;
    typingDiv.className = "chat-bubble assistant-bubble typing-bubble";
    typingDiv.innerHTML = `<span class="dot-typing">AI Assistant thinking...</span>`;
    this.messagesContainer.appendChild(typingDiv);
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    return id;
  }

  removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  formatText(text) {
    return this.escape(text).replace(/\n/g, "<br>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  }

  escape(text) {
    return String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }
}

window.chatController = new ChatController();
