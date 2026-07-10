/**
 * Obsidian Pilot Plugin - Main Entry Point
 * Calls local FastAPI backend for all operations
 * Automatically detects current vault path
 */

import { Plugin, Notice, requestUrl, WorkspaceLeaf, App, Modal } from 'obsidian';

// ---- SetupModal: API installation guide ----
class SetupModal extends Modal {
  private actionLabel: string;

  constructor(app: App, actionLabel: string) {
    super(app);
    this.actionLabel = actionLabel;
  }

  onOpen() {
    const { contentEl } = this;
    const title = contentEl.createEl('h2', { text: 'API Backend Required' });
    title.style.marginBottom = '12px';

    const body = contentEl.createDiv();
    body.style.marginBottom = '16px';
    body.createEl('p', { text: `To use "${this.actionLabel}", Pilot Assistant needs a lightweight API backend.` });
    body.createEl('p', { text: 'Please run these two commands in your terminal:' });

    // Command block
    const cmdBlock = contentEl.createDiv({ cls: 'pilot-cmd-block' });
    cmdBlock.createEl('code', { text: 'pip install obsidian-pilot-api' });
    cmdBlock.createEl('br');
    cmdBlock.createEl('code', { text: 'obsidian-pilot-api' });

    // Buttons
    const btnRow = contentEl.createDiv({ cls: 'pilot-setup-btns' });
    const copyBtn = btnRow.createEl('button', { text: 'Copy Commands' });
    copyBtn.addClass('mod-cta');
    copyBtn.onclick = () => {
      navigator.clipboard.writeText('pip install obsidian-pilot-api\nobsidian-pilot-api');
      copyBtn.setText('✓ Copied!');
      setTimeout(() => copyBtn.setText('Copy Commands'), 2000);
    };

    const guideBtn = btnRow.createEl('button', { text: 'View Full Guide' });
    guideBtn.onclick = () => {
      window.open('https://github.com/Magie-hu/obsidian-pilot/blob/main/INSTALL.md', '_blank');
    };
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
}

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
          // Show structured setup modal instead of raw error text
          new SetupModal(this.app, label).open();
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
