/**
 * Obsidian Pilot Plugin - Main Entry Point
 * Calls local FastAPI backend for all operations
 * Automatically detects current vault path
 */

import { Plugin, Notice, requestUrl, WorkspaceLeaf } from 'obsidian';
import { LLMWikiModal } from './modal';

const API_BASE = 'http://127.0.0.1:8080';

export default class LLMWikiPlugin extends Plugin {
    private apiConnected = false;

    async onload() {
        // Add ribbon icon
        this.addRibbonIcon('book-open', 'Obsidian Pilot', () => {
            this.openModal();
        });

        // Add command
        this.addCommand({
            id: 'show-panel',
            name: 'Show Obsidian Pilot Panel',
            callback: () => this.openModal(),
        });

        // Check API connection
        this.apiConnected = await this.checkConnection();
        if (!this.apiConnected) {
            new Notice('⚠️ API 未运行，请先启动后端服务', 5000);
        }
    }

    async checkConnection(): Promise<boolean> {
        try {
            const resp = await requestUrl(`${API_BASE}/health`);
            return resp.status === 200;
        } catch {
            return false;
        }
    }

    async getVaultPath(): Promise<string> {
        // Get current vault path from Obsidian app
        const vault = this.app.vault.adapter;
        const basePath = vault.getBasePath ? vault.getBasePath() : vault.basePath;
        return basePath || '';
    }

    async openModal() {
        const modal = new LLMWikiModal(this.app, this.apiConnected, API_BASE);
        modal.open();
    }
}
