class ChatUI {
  constructor(onSend) {
    this.onSend   = onSend;
    this.chatArea = document.getElementById('chat-area');
    this.msgInput = document.getElementById('msg-input');
    this.sendBtn  = document.getElementById('send-btn');
    this._bindEvents();
  }

  _bindEvents() {
    this.msgInput.addEventListener('input', () => {
      this.msgInput.style.height = 'auto';
      this.msgInput.style.height = Math.min(this.msgInput.scrollHeight, 120) + 'px';
    });
    this.msgInput.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); this._submit(); }
    });
    this.sendBtn.addEventListener('click', () => this._submit());
  }

  _submit() {
    const text = this.msgInput.value.trim();
    if (!text) return;
    this.onSend(text);
    this.msgInput.value = '';
    this.msgInput.style.height = 'auto';
  }

  // ── Enable chat after data is loaded ──────────────────────────────────────
  enable() {
    this.msgInput.disabled     = false;
    this.msgInput.placeholder  = 'Ask a question about your data…';
    this.sendBtn.disabled      = false;
    document.getElementById('suggestion-chips').style.display = 'flex';
  }

  setLoading(isLoading) {
    this.sendBtn.disabled  = isLoading;
    this.msgInput.disabled = isLoading;
  }

  // ── Remove welcome screen on first message ─────────────────────────────────
  clearWelcome() {
    const welcome = document.getElementById('welcome');
    if (welcome) welcome.remove();
  }

  // ── Message rendering ──────────────────────────────────────────────────────
  appendMessage(role, text) {
    const div = document.createElement('div');
    div.className = `msg ${role}`;

    const avatar = document.createElement('div');
    avatar.className   = 'msg-avatar';
    avatar.textContent = role === 'user' ? 'Y' : '◈';

    const body      = document.createElement('div');
    body.className  = 'msg-body';

    const roleLabel      = document.createElement('div');
    roleLabel.className  = 'msg-role';
    roleLabel.textContent = role === 'user' ? 'You' : 'Groq';

    const bubble      = document.createElement('div');
    bubble.className  = 'msg-text';
    bubble.innerHTML  = this.renderMarkdown(text);

    body.appendChild(roleLabel);
    body.appendChild(bubble);
    div.appendChild(avatar);
    div.appendChild(body);
    this.chatArea.appendChild(div);
    this.chatArea.scrollTop = this.chatArea.scrollHeight;
    return div;
  }

  appendThinking() {
    const div = document.createElement('div');
    div.className = 'msg assistant';
    div.innerHTML = `
      <div class="msg-avatar">◈</div>
      <div class="msg-body">
        <div class="msg-role">Groq</div>
        <div class="msg-text">
          <div class="thinking"><span></span><span></span><span></span></div>
        </div>
      </div>`;
    this.chatArea.appendChild(div);
    this.chatArea.scrollTop = this.chatArea.scrollHeight;
    return div;
  }

  showToast(msg) {
    const t = document.getElementById('toast');
    t.textContent    = msg;
    t.style.display  = 'block';
    setTimeout(() => t.style.display = 'none', 4000);
  }

  // ── Minimal Markdown Renderer ──────────────────────────────────────────────
  renderMarkdown(text) {
    return text
      .replace(/^\|(.+)\|$/gm, row =>
        '<tr>' + row.split('|')
          .filter((_, i, a) => i > 0 && i < a.length - 1)
          .map((c, i) => i === 0 && row.includes('---') ? '' : `<td>${c.trim()}</td>`)
          .join('') + '</tr>')
      .replace(/(<tr>.*<\/tr>\n?)+/gs, match => `<table><tbody>${match}</tbody></table>`)
      .replace(/<tr><\/tr>\n?/g, '')
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm,  '<h3>$1</h3>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g,    '<em>$1</em>')
      .replace(/`([^`]+)`/g,    '<code>$1</code>')
      .replace(/^[-•] (.+)$/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>\n?)+/gs, match => `<ul>${match}</ul>`)
      .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>');
  }
}