/**
 * Obsidian Pilot Plugin - Main Entry Point
 * Calls local FastAPI backend for all operations
 * Automatically detects current vault path
 */

import { Plugin, Notice, requestUrl, WorkspaceLeaf } from 'obsidian';

export default class ObsidianPilotPlugin extends Plugin {
  private apiUrl = 'http://localhost:8080';

  async onload() {
    console.log('Loading Obsidian Pilot plugin...');

    // Add ribbon icon
    this.addRibbonIcon('book-open', 'Obsidian Pilot', () => {
      this.openModal();
    });

    // Add command
    this.addCommand({
      id: 'open-pilot-panel',
      name: 'Open Pilot Panel',
      callback: () => {
        this.openModal();
      }
    });

    console.log('Obsidian Pilot plugin loaded.');
  }

  async openModal() {
    const modal = new PilotModal(this.app, this.apiUrl);
    modal.open();
  }

  async onunload() {
    console.log('Unloading Obsidian Pilot plugin...');
  }
}
