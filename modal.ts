/**
 * Obsidian Pilot Plugin - Modal Panel
 * Full UI for all vault operations
 * Auto-detects vault path from Obsidian
 */

import { App, Modal, Notice, requestUrl } from 'obsidian';

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
      el.createEl('h2', { text: 'Obsidian Pilot' });
      el.createEl('small', { text: `Vault: ${vaultPath}` });
    });

    // Grid of buttons
    contentEl.createDiv({ cls: 'pilot-btn-grid' }, grid => {
      this.addButton(grid, '📁 Init Vault', 'init', 'Create LLM-Wiki standard structure');
      this.addButton(grid, '📥 Import Notes', 'import', 'Scan and classify all notes');
      this.addButton(grid, '🔗 Auto Links', 'links', 'Analyze and suggest note links');
      this.addButton(grid, '🤖 AI Route', 'route', 'Route queries to the right AI model');
      this.addButton(grid, '🧹 Maintain', 'maintain', 'Check for expired/duplicate/orphaned notes');
      this.addButton(grid, '📊 Link Report', 'report', 'Detailed link analysis report');
    });

    // Result area
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
          const msg = `API 未连接 (${this.apiUrl})\n\n请先启动 API 后端：\n\n1. 安装依赖：pip install fastapi uvicorn\n2. 启动服务：\n   cd obsidian-pilot-api\n   uvicorn obsidian_pilot_api.main:app --port 8080\n\n3. 确保 API 返回 http://${this.apiUrl}/health`;
          this.showResult({ error: msg });
          new Notice(`❌ ${label} - 请先启动 API`);
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
