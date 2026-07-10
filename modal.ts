/**
 * Obsidian Pilot Plugin - Modal Panel
 * Full UI for all vault operations
 * Auto-detects vault path from Obsidian
 */

import { App, Modal, Notice, requestUrl } from 'obsidian';

export class LLMWikiModal extends Modal {
    private apiConnected: boolean;
    private apiBase: string;
    private vaultPath: string = '';

    constructor(app: App, apiConnected: boolean, apiBase: string) {
        super(app);
        this.apiConnected = apiConnected;
        this.apiBase = apiBase;
    }

    async onOpen() {
        const { contentEl } = this;
        contentEl.empty();

        // Title
        contentEl.createEl('h2', { text: 'Obsidian Pilot' });

        // Status indicator
        const statusDiv = contentEl.createDiv({ cls: 'status-bar' });
        if (this.apiConnected) {
            statusDiv.createSpan({ text: '🟢 API 已连接' });
        } else {
            statusDiv.createSpan({ text: '🔴 API 未连接' }).style.color = '#eb4d4b';
        }

        // Vault path display
        const pathDiv = contentEl.createDiv({ cls: 'vault-path' });
        pathDiv.createEl('span', { text: 'Vault 路径: ' });
        const pathSpan = pathDiv.createEl('span', { text: '加载中...' });
        pathSpan.style.color = '#7d8590';

        // Fetch vault path
        try {
            // We can't directly access the plugin instance, so we'll use a workaround
            // The actual path will be filled when user clicks an action
            this.vaultPath = '';
        } catch {
            this.vaultPath = '';
        }

        // Create action buttons
        const btnGroup = contentEl.createDiv({ cls: 'btn-grid' });

        // 1. Initialize Vault
        this.addButton(btnGroup, '📁 初始化知识库', async () => {
            const path = await this.promptVaultPath();
            if (!path) return;
            await this.doInit(path);
        });

        // 2. Import & Classify
        this.addButton(btnGroup, '📥 导入分类', async () => {
            const path = await this.promptVaultPath();
            if (!path) return;
            await this.doImport(path);
        });

        // 3. Auto Links
        this.addButton(btnGroup, '🔗 自动链接', async () => {
            const path = await this.promptVaultPath();
            if (!path) return;
            await this.doLinks(path);
        });

        // 4. AI Route
        this.addButton(btnGroup, '🤖 AI 路由', async () => {
            await this.doRoute();
        });

        // 5. Daily Maintenance
        this.addButton(btnGroup, '🧹 日常维护', async () => {
            const path = await this.promptVaultPath();
            if (!path) return;
            await this.doMaintain(path);
        });

        // 6. Link Report
        this.addButton(btnGroup, '📊 链接报告', async () => {
            const path = await this.promptVaultPath();
            if (!path) return;
            await this.doLinkReport(path);
        });

        // Result area
        contentEl.createEl('div', { cls: 'result-area' }).attr('id', 'result-area');
    }

    private addButton(container: HTMLElement, text: string, onClick: () => Promise<void>) {
        const btn = container.createEl('button', { text });
        btn.addClass('pilot-btn');
        btn.onclick = async () => {
            btn.disabled = true;
            btn.text = '⏳ 处理中...';
            try {
                await onClick();
            } finally {
                btn.disabled = false;
                btn.text = text;
            }
        };
    }

    private async promptVaultPath(): Promise<string> {
        if (this.vaultPath) {
            return this.vaultPath;
        }

        // Try to get from Obsidian
        try {
            const vault = this.app.vault.adapter;
            const basePath = (vault as any).getBasePath?.() || (vault as any).basePath;
            if (basePath) {
                this.vaultPath = basePath;
                return basePath;
            }
        } catch {}

        // Fallback: manual input
        const input = prompt('请输入 Vault 路径:', '');
        if (!input) return '';
        this.vaultPath = input;
        return input;
    }

    private async apiPost(endpoint: string, body: any): Promise<any> {
        const url = `${this.apiBase}${endpoint}`;
        const resp = await requestUrl({
            url,
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        return resp.json;
    }

    private async doInit(path: string) {
        try {
            const data = await this.apiPost('/init', { vault_path: path });
            if (data.status === 'success') {
                new Notice(`✅ ${data.message}`, 3000);
            } else {
                new Notice(`❌ ${data.message}`, 3000);
            }
        } catch (e) {
            new Notice(`API 错误: ${e}`, 3000);
        }
    }

    private async doImport(path: string) {
        try {
            const data = await this.apiPost('/import', { vault_path: path });
            
            let msg = `📊 导入结果:\n`;
            msg += `总笔记: ${data.total_notes}\n`;
            msg += `分类分布: ${JSON.stringify(data.category_counts)}\n`;
            if (data.uncategorized.length > 0) {
                msg += `未分类: ${data.uncategorized.length} 篇\n`;
            }
            
            new Notice(msg, 5000);
            this.showResult(msg);
        } catch (e) {
            new Notice(`API 错误: ${e}`, 3000);
        }
    }

    private async doLinks(path: string) {
        try {
            const data = await this.apiPost('/links/report', { vault_path: path });
            
            let msg = `🔗 链接分析:\n`;
            msg += `总笔记: ${data.total_notes}\n`;
            msg += `缺失链接: ${data.missing_links.length}\n`;
            msg += `孤立笔记: ${data.isolated_notes.filter((n: any) => !n.has_outgoing && !n.has_incoming).length}\n`;
            
            if (data.missing_links.length > 0) {
                msg += `\n建议添加的链接:\n`;
                for (const link of data.missing_links.slice(0, 10)) {
                    msg += `  ${link.current_file} → ${link.suggested}\n`;
                }
            }
            
            new Notice(msg, 5000);
            this.showResult(msg);
        } catch (e) {
            new Notice(`API 错误: ${e}`, 3000);
        }
    }

    private async doRoute() {
        const query = prompt('输入查询问题:', 'How do I set up a new vault?');
        if (!query) return;

        try {
            const data = await this.apiPost('/route', { query });
            
            let msg = `🤖 路由推荐:\n`;
            msg += `推荐模型: ${data.recommended_model}\n`;
            msg += `置信度: ${(data.confidence * 100).toFixed(0)}%\n`;
            if (data.local_knowledge) {
                msg += `本地知识: ${data.local_knowledge}\n`;
            }
            
            new Notice(msg, 5000);
            this.showResult(msg);
        } catch (e) {
            new Notice(`API 错误: ${e}`, 3000);
        }
    }

    private async doMaintain(path: string) {
        try {
            const data = await this.apiPost('/maintain', { vault_path: path, archive: false });
            
            let msg = `🧹 维护报告:\n`;
            msg += `总笔记: ${data.total_notes}\n`;
            msg += `过期笔记: ${data.expired_count}\n`;
            msg += `重复标题: ${data.duplicate_count}\n`;
            msg += `孤立链接: ${data.orphaned_count}\n`;
            
            if (data.expired_notes.length > 0) {
                msg += `\n过期笔记:\n`;
                for (const n of data.expired_notes.slice(0, 5)) {
                    msg += `  ${n.title} (${n.age_days} 天)\n`;
                }
            }
            
            new Notice(msg, 5000);
            this.showResult(msg);
        } catch (e) {
            new Notice(`API 错误: ${e}`, 3000);
        }
    }

    private async doLinkReport(path: string) {
        try {
            const data = await this.apiPost('/links/report', { vault_path: path });
            
            let msg = `📊 完整链接报告:\n`;
            msg += `总笔记: ${data.total_notes}\n`;
            msg += `缺失链接: ${data.missing_links.length}\n`;
            
            const isolated = data.isolated_notes.filter((n: any) => !n.has_outgoing && !n.has_incoming);
            msg += `完全孤立: ${isolated.length}\n`;
            
            if (data.missing_links.length > 0) {
                msg += `\n建议链接:\n`;
                for (const link of data.missing_links) {
                    msg += `  [[${link.suggested}]] ← ${link.current_file}\n`;
                }
            }
            
            new Notice(msg, 5000);
            this.showResult(msg);
        } catch (e) {
            new Notice(`API 错误: ${e}`, 3000);
        }
    }

    private showResult(text: string) {
        const resultArea = document.getElementById('result-area');
        if (resultArea) {
            resultArea.textContent = text;
        }
    }

    onClose() {
        // Cleanup
    }
}
