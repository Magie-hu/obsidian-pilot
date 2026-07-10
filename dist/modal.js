/**
 * LLM-Wiki Plugin - Sidebar Modal
 * Simple UI for vault operations
 */
import { Modal, Notice } from 'obsidian';
const API_BASE = 'http://127.0.0.1:8080';
export class LLMWikiModal extends Modal {
    constructor(app, plugin) {
        super(app);
        this.plugin = plugin;
    }
    onOpen() {
        const { contentEl } = this;
        contentEl.createEl('h2', { text: 'LLM-Wiki Bridge' });
        // Vault path input
        const pathGroup = contentEl.createDiv({ cls: 'input-group' });
        pathGroup.createEl('label', { text: 'Vault Path:' });
        const pathInput = pathGroup.createEl('input', {
            type: 'text',
            placeholder: '/path/to/your/vault'
        });
        pathInput.classList.add('llm-wiki-input');
        // Buttons
        const btnGroup = contentEl.createDiv({ cls: 'btn-group' });
        // Init button
        const initBtn = btnGroup.createEl('button', { text: 'Initialize Vault' });
        initBtn.onclick = async () => {
            const path = pathInput.value.trim();
            if (!path) {
                new Notice('Please enter vault path', 3000);
                return;
            }
            try {
                const resp = await fetch(`${API_BASE}/init`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ vault_path: path, template: 'llm-wiki' }),
                });
                const data = await resp.json();
                if (data.success) {
                    new Notice(`✅ ${data.message}`, 3000);
                }
                else {
                    new Notice(`❌ ${data.message}`, 3000);
                }
            }
            catch (e) {
                new Notice(`API Error: ${e}`, 3000);
            }
        };
        // Import button
        const importBtn = btnGroup.createEl('button', { text: 'Import Notes' });
        importBtn.onclick = async () => {
            const path = pathInput.value.trim();
            if (!path) {
                new Notice('Please enter vault path', 3000);
                return;
            }
            try {
                const resp = await fetch(`${API_BASE}/import`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ vault_path: path, apply: true }),
                });
                const data = await resp.json();
                if (data.success) {
                    new Notice(`✅ ${data.message}`, 3000);
                }
                else {
                    new Notice(`❌ ${data.message}`, 3000);
                }
            }
            catch (e) {
                new Notice(`API Error: ${e}`, 3000);
            }
        };
        // Link button
        const linkBtn = btnGroup.createEl('button', { text: 'Auto Links' });
        linkBtn.onclick = async () => {
            const path = pathInput.value.trim();
            if (!path) {
                new Notice('Please enter vault path', 3000);
                return;
            }
            try {
                const resp = await fetch(`${API_BASE}/link`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ vault_path: path, apply: true }),
                });
                const data = await resp.json();
                if (data.success) {
                    new Notice(`✅ ${data.message}`, 3000);
                }
                else {
                    new Notice(`❌ ${data.message}`, 3000);
                }
            }
            catch (e) {
                new Notice(`API Error: ${e}`, 3000);
            }
        };
        // Maintain button
        const maintBtn = btnGroup.createEl('button', { text: 'Daily Maintenance' });
        maintBtn.onclick = async () => {
            const path = pathInput.value.trim();
            if (!path) {
                new Notice('Please enter vault path', 3000);
                return;
            }
            try {
                const resp = await fetch(`${API_BASE}/maintain`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ vault_path: path, archive: false }),
                });
                const data = await resp.json();
                if (data.success) {
                    new Notice(`✅ ${data.message}`, 3000);
                }
                else {
                    new Notice(`❌ ${data.message}`, 3000);
                }
            }
            catch (e) {
                new Notice(`API Error: ${e}`, 3000);
            }
        };
        // Style
        this.setupStyles();
    }
    setupStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .llm-wiki-input {
                width: 100%;
                padding: 8px;
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            .btn-group {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            .btn-group button {
                padding: 8px 16px;
                background: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            .btn-group button:hover {
                background: #005a9e;
            }
        `;
        document.head.appendChild(style);
    }
    onClose() {
        // Cleanup styles
        const styles = document.querySelectorAll('style');
        styles.forEach(s => s.remove());
    }
}
