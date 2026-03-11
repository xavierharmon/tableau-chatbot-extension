# Data Chat — Tableau Extension (Claude AI)

An AI-powered chatbot extension for Tableau that lets you upload an Excel/CSV file and ask natural language questions about your data, powered by the Anthropic Claude API.

---

## Files

```
tableau-chat-extension/
├── index.html       ← The entire extension (self-contained, no build step)
├── data-chat.trex   ← Tableau manifest — load this in Desktop
└── README.md
```

---

## Quickstart — Tableau Desktop (today, no hosting needed)

```bash
# Option A: Python (built into macOS/Linux)
cd tableau-chat-extension
python -m http.server 8765

# Option B: Node (if installed)
npx serve . -p 8765
```

1. Edit `data-chat.trex` → uncomment the `localhost:8765` URL line, comment out the GitHub Pages line
2. Open Tableau Desktop → open a dashboard sheet
3. Drag **Extension** from the Objects panel onto the canvas
4. Click **"My Extensions"** → select `data-chat.trex`
5. Click **OK** to trust → extension loads

---

## GitHub Pages Hosting (free HTTPS — for sharing & POC)

### One-time setup
1. Create a new **public** GitHub repo (e.g. `tableau-data-chat`)
2. Push both files to the repo root:
   ```bash
   git init
   git add .
   git commit -m "Initial extension"
   git remote add origin https://github.com/YOUR_USERNAME/tableau-data-chat.git
   git push -u origin main
   ```
3. In GitHub: go to **Settings → Pages → Source: Deploy from main branch, / (root)**
4. Wait ~60 seconds → your extension is live at:
   `https://YOUR_USERNAME.github.io/tableau-data-chat/index.html`

5. Edit `data-chat.trex` → update the GitHub Pages `<url>` line with your actual URL
6. Commit & push the updated `.trex` file

### Loading in Tableau
- **Tableau Desktop**: drag Extension → My Extensions → select `data-chat.trex`
- **Tableau Public** (web authoring): currently requires network-enabled extensions to be allow-listed — use Desktop for the POC, see note below

---

## Tableau Server (production path)

1. Host `index.html` on any HTTPS server your Tableau Server can reach
2. Update `<url>` in `data-chat.trex` to your hosted URL
3. In Tableau Server Admin: **Settings → Extensions → Add Extension** → enter your URL → Allow
4. Users can now add the extension to any dashboard

---

## Using the Extension

1. **Paste your Anthropic API key** — get one at console.anthropic.com (sk-ant-api03-...)
2. **Upload your Excel or CSV file** — drag & drop or click to browse
3. **Click Apply** — the extension parses your data and builds a summary for Claude
4. **Start chatting** — ask anything in plain English:
   - *"What are the top 10 rows by revenue?"*
   - *"Summarize this dataset for me"*
   - *"Are there any outliers or missing values?"*
   - *"What's the average order value by region?"*

The chat is multi-turn — Claude remembers your conversation context.

---

## How it works

```
Your Excel file
      ↓ (parsed in browser via SheetJS — never leaves your machine)
Data Summary (column stats + sample rows)
      ↓ (sent as system context to Claude API)
Claude claude-sonnet-4-20250514
      ↓
Natural language answer → rendered in chat UI
```

**Privacy note**: Your raw data is parsed entirely in the browser. Only a statistical summary + up to 25 sample rows are sent to the Claude API with each query. No data is stored by this extension.

---

## Customizing

**Change the sample size** sent to Claude — edit `buildDataContext()` in `index.html`:
```javascript
const sampleRows = totalRows <= 30
  ? rows
  : [...rows.slice(0,20), ...rows.slice(-5)];   // ← adjust 20/5 as needed
```

**Change the Claude model** — edit the `callClaude()` function:
```javascript
model: 'claude-opus-4-20250514',   // more powerful, slower
model: 'claude-haiku-4-5-20251001', // faster, cheaper
```

**Add default suggestions** — edit the `.chip-btn` elements in `index.html`.

---

## POC → Production Checklist

- [ ] API key management: move to a backend proxy so users don't need their own keys
- [ ] Replace file upload with a live connection to your actual data source
- [ ] Add Tableau filter sync (`worksheet.getFiltersAsync()`) to auto-filter chat context
- [ ] Add allow-list entry on Tableau Server
- [ ] Consider Claude's context window for very large files (summarize more aggressively)