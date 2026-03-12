class TableauBridge {
  constructor() {
    this.ready = false;
  }

  async init() {
    try {
      await tableau.extensions.initializeAsync();
      this.ready = true;
    } catch (e) {
      // Standalone mode — works fine outside Tableau
      this.ready = false;
    }
    return this.ready;
  }

  getSetting(key) {
    if (!this.ready) return null;
    const settings = tableau.extensions.settings.getAll();
    return settings[key] ?? null;
  }

  async saveSetting(key, value) {
    if (!this.ready) return;
    tableau.extensions.settings.set(key, value);
    await tableau.extensions.settings.saveAsync();
  }
}