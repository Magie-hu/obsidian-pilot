/**
 * Obsidian Pilot Plugin - Main Entry Point
 * Calls local FastAPI backend for all operations
 * Automatically detects current vault path
 */

import { Plugin, Notice, requestUrl, WorkspaceLeaf, App, Modal } from 'obsidian';

// ---- PilotModal (inline) ----
export class PilotModal extends Modal {
  private apiUrl: string;

  constructor(app: App, apiUrl: string) {
    super(app);
    this.apiUrl = apiUrl;
  }

  onOpen() {
    const { contentEl } = this;
    const vaultPath = this.app.vault.adapter.basePath;

    contentEl.createDiv({ cls: 'pilot-modal-header' }, el => {
      el.createEl('h2', { text: 'Pilot Assistant' });
      el.createEl('small', { text: `Vault: ${vaultPath}` });
    });

    contentEl.createDiv({ cls: 'pilot-btn-grid' }, grid => {
      this.addButton(grid, '📁 Init Vault', 'init', 'Create LLM-Wiki standard structure');
      this.addButton(grid, '📥 Import Notes', 'import', 'Scan and classify all notes');
      this.addButton(grid, '🔗 Auto Links', 'links', 'Analyze and suggest note links');
      this.addButton(grid, '🤖 AI Route', 'route', 'Route queries to the right AI model');
      this.addButton(grid, '🧹 Maintain', 'maintain', 'Check for expired/duplicate/orphaned notes');
      this.addButton(grid, '📊 Link Report', 'report', 'Detailed link analysis report');
    });

    contentEl.createDiv({ cls: 'pilot-result-area' }, el => {
      el.createEl('h3', { text: 'Result' });
      el.createEl('div', { cls: 'pilot-result-content', attr: { id: 'pilot-result' } });
    });
  }

  private addButton(parent: HTMLElement, label: string, action: string, desc: string) {
    parent.createEl('button', { cls: 'pilot-btn' }, btn => {
      btn.setText(label);
      btn.title = desc;
      btn.onclick = async () => {
        btn.disabled = true;
        btn.setText('⏳ Processing...');
        try {
          const response = await requestUrl({
            url: `${this.apiUrl}/${action}`,
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ vault_path: this.app.vault.adapter.basePath })
          });
          const result = response.json;
          this.showResult(result);
          new Notice(`✅ ${label} completed`);
        } catch (error) {
          const msg = `API not connected (${this.apiUrl})

Please start the API backend first:

1. Install dependencies: pip install fastapi uvicorn
2. Start the server:
   cd obsidian-pilot-api
   uvicorn obsidian_pilot_api.main:app --port 8080

3. Verify API is running: http://${this.apiUrl}/health`;
          this.showResult({ error: msg });
          new Notice(`❌ ${label} - Please start the API first`);
        } finally {
          btn.disabled = false;
          btn.setText(label);
        }
      };
    });
  }

  private showResult(data: any) {
    const resultEl = this.contentEl.querySelector('#pilot-result');
    if (resultEl) {
      resultEl.empty();
      if (data.error) {
        resultEl.createEl('p', { text: data.error, cls: 'pilot-error' });
      } else {
        for (const [key, value] of Object.entries(data)) {
          resultEl.createEl('p', { text: `${key}: ${JSON.stringify(value)}` });
        }
      }
    }
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
}

// ---- Plugin ----
export default class ObsidianPilotPlugin extends Plugin {
  private apiUrl = 'http://localhost:8080';

  async onload() {
    console.log('Loading Pilot Assistant plugin...');

    this.addRibbonIcon('book-open', 'Pilot Assistant', () => {
      this.openModal();
    });

    this.addCommand({
      id: 'open-pilot-panel',
      name: 'Open Pilot Panel',
      callback: () => {
        this.openModal();
      }
    });

    console.log('Pilot Assistant plugin loaded.');
  }

  async openModal() {
    const modal = new PilotModal(this.app, this.apiUrl);
    modal.open();
  }

  async onunload() {
    console.log('Unloading Pilot Assistant plugin...');
  }
}
