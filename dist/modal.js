"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// modal.ts
var modal_exports = {};
__export(modal_exports, {
  PilotModal: () => PilotModal
});
module.exports = __toCommonJS(modal_exports);
var import_obsidian = require("obsidian");
var PilotModal = class extends import_obsidian.Modal {
  constructor(app, apiUrl) {
    super(app);
    this.apiUrl = apiUrl;
  }
  onOpen() {
    const { contentEl } = this;
    const vaultPath = this.app.vault.adapter.basePath;
    contentEl.createDiv({ cls: "pilot-modal-header" }, (el) => {
      el.createEl("h2", { text: "Obsidian Pilot" });
      el.createEl("small", { text: `Vault: ${vaultPath}` });
    });
    contentEl.createDiv({ cls: "pilot-btn-grid" }, (grid) => {
      this.addButton(grid, "\u{1F4C1} Init Vault", "init", "Create LLM-Wiki standard structure");
      this.addButton(grid, "\u{1F4E5} Import Notes", "import", "Scan and classify all notes");
      this.addButton(grid, "\u{1F517} Auto Links", "links", "Analyze and suggest note links");
      this.addButton(grid, "\u{1F916} AI Route", "route", "Route queries to the right AI model");
      this.addButton(grid, "\u{1F9F9} Maintain", "maintain", "Check for expired/duplicate/orphaned notes");
      this.addButton(grid, "\u{1F4CA} Link Report", "report", "Detailed link analysis report");
    });
    contentEl.createDiv({ cls: "pilot-result-area" }, (el) => {
      el.createEl("h3", { text: "Result" });
      el.createEl("div", { cls: "pilot-result-content", attr: { id: "pilot-result" } });
    });
  }
  addButton(parent, label, action, desc) {
    parent.createEl("button", { cls: "pilot-btn" }, (btn) => {
      btn.setText(label);
      btn.title = desc;
      btn.onclick = async () => {
        btn.disabled = true;
        btn.setText("\u23F3 Processing...");
        try {
          const response = await (0, import_obsidian.requestUrl)({
            url: `${this.apiUrl}/${action}`,
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ vault_path: this.app.vault.adapter.basePath })
          });
          const result = response.json;
          this.showResult(result);
          new import_obsidian.Notice(`\u2705 ${label} completed`);
        } catch (error) {
          this.showResult({ error: `Connection failed. Is API running on ${this.apiUrl}?` });
          new import_obsidian.Notice(`\u274C ${label} failed`);
        } finally {
          btn.disabled = false;
          btn.setText(label);
        }
      };
    });
  }
  showResult(data) {
    const resultEl = this.contentEl.querySelector("#pilot-result");
    if (resultEl) {
      resultEl.empty();
      if (data.error) {
        resultEl.createEl("p", { text: data.error, cls: "pilot-error" });
      } else {
        for (const [key, value] of Object.entries(data)) {
          resultEl.createEl("p", { text: `${key}: ${JSON.stringify(value)}` });
        }
      }
    }
  }
  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
};
