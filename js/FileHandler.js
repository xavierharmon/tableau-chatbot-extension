class FileHandler {
  constructor(onFileLoaded) {
    this.onFileLoaded = onFileLoaded;
    this.dropZone   = document.getElementById('drop-zone');
    this.fileInput  = document.getElementById('file-input');
    this.dropLabel  = document.getElementById('drop-label');
    this._bindEvents();
  }

  _bindEvents() {
    this.dropZone.addEventListener('dragover', e => {
      e.preventDefault();
      this.dropZone.classList.add('drag-over');
    });
    this.dropZone.addEventListener('dragleave', () => {
      this.dropZone.classList.remove('drag-over');
    });
    this.dropZone.addEventListener('drop', e => {
      e.preventDefault();
      this.dropZone.classList.remove('drag-over');
      if (e.dataTransfer.files[0]) this.handleFile(e.dataTransfer.files[0]);
    });
    this.fileInput.addEventListener('change', e => {
      if (e.target.files[0]) this.handleFile(e.target.files[0]);
    });
  }

  handleFile(file) {
    const reader = new FileReader();
    reader.onload = e => {
      try {
        let rows, sheetName = '';
        if (file.name.endsWith('.csv')) {
          const wb = XLSX.read(e.target.result, { type: 'binary' });
          sheetName = wb.SheetNames[0];
          rows = XLSX.utils.sheet_to_json(wb.Sheets[sheetName], { defval: '' });
        } else {
          const wb = XLSX.read(new Uint8Array(e.target.result), { type: 'array' });
          sheetName = wb.SheetNames[0];
          rows = XLSX.utils.sheet_to_json(wb.Sheets[sheetName], { defval: '' });
        }

        if (!rows.length) throw new Error('File appears empty or unreadable.');

        const columns     = Object.keys(rows[0]);
        const dataContext = this.buildDataContext(rows, columns, file.name, sheetName);

        this.dropZone.classList.add('loaded');
        this.dropLabel.className   = 'drop-label loaded';
        this.dropLabel.textContent = `✓ ${file.name}`;

        this.onFileLoaded({ rows, columns, sheetName, fileName: file.name, dataContext });
      } catch (err) {
        this.onFileLoaded(null, err.message);
      }
    };
    if (file.name.endsWith('.csv')) reader.readAsBinaryString(file);
    else reader.readAsArrayBuffer(file);
  }

  sanitize(val) {
    return String(val)
      .substring(0, 60)
      .replace(/\\/g, '')
      .replace(/"/g, "'")
      .replace(/[\r\n\t]/g, ' ')
      .replace(/[^\x20-\x7E]/g, '')
      .trim();
  }

  buildDataContext(rows, cols, fileName, sheetName) {
    const totalRows = rows.length;

    const colStats = cols.map(col => {
      const vals = rows.map(r => r[col]).filter(v => v !== '' && v != null);
      const nums = vals.filter(v => !isNaN(Number(v)) && v !== '');
      const isNumeric = nums.length / vals.length > 0.8;
      if (isNumeric && nums.length) {
        const ns  = nums.map(Number);
        const sum = ns.reduce((a, b) => a + b, 0);
        const min = Math.min(...ns);
        const max = Math.max(...ns);
        const avg = (sum / ns.length).toFixed(2);
        return `${this.sanitize(col)} [numeric]: min=${min}, max=${max}, avg=${avg}, sum=${sum.toFixed(2)}, count=${ns.length}`;
      } else {
        const unique  = [...new Set(vals)];
        const preview = unique.slice(0, 8).map(v => String(v).substring(0, 30)).join(', ');
        return `${this.sanitize(col)} [text]: ${unique.length} unique values — e.g. ${preview}${unique.length > 8 ? '…' : ''}`;
      }
    });

    const sampleRows = totalRows <= 30 ? rows : [...rows.slice(0, 20), ...rows.slice(-5)];
    const sampleCsv  = [
      cols.map(c => this.sanitize(c)).join(' | '),
      ...sampleRows.map(r => cols.map(c => this.sanitize(r[c]).substring(0, 40)).join(' | '))
    ].join('\n');

    return `
FILE: ${fileName} (Sheet: "${sheetName}")
TOTAL ROWS: ${totalRows.toLocaleString()} | COLUMNS: ${cols.length}

COLUMN STATISTICS:
${colStats.join('\n')}

SAMPLE DATA (${sampleRows.length} rows shown):
${sampleCsv}
`.trim();
  }
}