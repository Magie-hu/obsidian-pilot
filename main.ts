/**
 * Obsidian LLM-Wiki Plugin - Main Entry Point
 * Calls local FastAPI backend for all operations
 */

import { Plugin, Notice } from 'obsidian';
import { LLMWikiModal } from './modal';

const API_BASE = 'http://127.0.0.1:8080';

export default class LLMWikiPlugin extends Plugin {
    async onload() {
        // Add ribbon icon
        this.addRibbonIcon('book-open', 'LLM-Wiki', () => {
            this.showSidebar();
        });

        // Add command
        this.addCommand({
            id: 'show-panel',
            name: 'Show LLM-Wiki Panel',
            callback: () => this.showSidebar(),
        });

        // Check API connection
        const connected = await this.checkConnection();
        if (!connected) {
            new Notice('LLM-Wiki API not running. Please start the backend service.', 5000);
        }
    }

    async checkConnection(): Promise<boolean> {
        try {
            const resp = await fetch(`${API_BASE}/`);
            return resp.ok;
        } catch {
            return false;
        }
    }

    async showSidebar() {
        const modal = new LLMWikiModal(this.app);
        modal.open();
    }
}
