// ── App — wires all modules together ────────────────────────────────────────
class App {
  constructor() {
    this.state = {
      apiKey:      '',
      dataReady:   false,
      dataContext: '',
      rawRows:     [],
      columns:     [],
      fileName:    '',
      sheetName:   '',
      history:     [],
      thinking:    false
    };

    this.tableau = new TableauBridge();
    this.groq    = new GroqClient();
    this.ui      = new ChatUI(text => this.sendMessage(text));
    this.files   = new FileHandler(
      (data, err) => err ? this.ui.showToast(err) : this.onFileLoaded(data)
    );

    this._bindSetupEvents();
  }

  async init() {
    await this.tableau.init();
    const savedKey = this.tableau.getSetting('apiKey');
    if (savedKey) {
      document.getElementById('api-key').value = savedKey;
      this.checkApplyReady();
    }
  }

  // ── Setup panel ────────────────────────────────────────────────────────────
  _bindSetupEvents() {
    document.getElementById('api-key').addEventListener('input', () => this.checkApplyReady());
    document.getElementById('apply-btn').addEventListener('click', () => this.applyConfig());
    document.getElementById('toggle-setup-btn').addEventListener('click', () => {
      const panel = document.getElementById('setup-panel');
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    });
  }

  onFileLoaded({ rows, columns, sheetName, fileName, dataContext }) {
    this.state.rawRows     = rows;
    this.state.columns     = columns;
    this.state.sheetName   = sheetName;
    this.state.fileName    = fileName;
    this.state.dataContext = dataContext;
    this.checkApplyReady();
  }

  checkApplyReady() {
    const key = document.getElementById('api-key').value.trim();
    document.getElementById('apply-btn').disabled = !(key && this.state.rawRows.length);
  }

  applyConfig() {
    this.state.apiKey   = document.getElementById('api-key').value.trim();
    this.state.dataReady = true;
    this.state.history  = [];

    this.groq.setApiKey(this.state.apiKey);

    // Update data summary strip
    document.getElementById('data-summary').style.display  = 'block';
    document.getElementById('stat-rows').textContent       = this.state.rawRows.length.toLocaleString();
    document.getElementById('stat-cols').textContent       = this.state.columns.length;
    document.getElementById('stat-sheet').textContent      = this.state.sheetName;
    document.getElementById('stat-col-names').textContent  = this.state.columns.join(', ');

    // Update header pill
    const pill = document.getElementById('data-pill');
    pill.classList.add('loaded');
    document.getElementById('data-pill-name').textContent = this.state.fileName;

    // Persist API key
    this.tableau.saveSetting('apiKey', this.state.apiKey);

    // Collapse setup, enable chat
    document.getElementById('setup-panel').style.display = 'none';
    this.ui.enable();
  }

  // ── Chat ───────────────────────────────────────────────────────────────────
  async sendMessage(text) {
    if (!text || this.state.thinking || !this.state.dataReady) return;

    this.ui.clearWelcome();
    this.ui.appendMessage('user', text);
    this.state.history.push({ role: 'user', content: text });

    this.state.thinking = true;
    this.ui.setLoading(true);
    const thinkingEl = this.ui.appendThinking();

    try {
      const reply = await this.groq.chat(this.state.history, this.state.dataContext);
      thinkingEl.remove();
      this.ui.appendMessage('assistant', reply);
      this.state.history.push({ role: 'assistant', content: reply });
    } catch (err) {
      thinkingEl.remove();
      this.ui.showToast(err.message);
      this.state.history.pop();
    } finally {
      this.state.thinking = false;
      this.ui.setLoading(false);
      document.getElementById('msg-input').focus();
    }
  }
}

// ── Bootstrap ────────────────────────────────────────────────────────────────
const app = new App();
app.init();

// Global hook for suggestion chips in HTML
function sendSuggestion(btn) {
  if (!app.state.dataReady) return;
  app.sendMessage(btn.textContent.trim());
}