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
  LLMWikiModal: () => LLMWikiModal
});
module.exports = __toCommonJS(modal_exports);
var import_obsidian = require("obsidian");
var LLMWikiModal = class extends import_obsidian.Modal {
  constructor(app, apiConnected, apiBase) {
    super(app);
    this.vaultPath = "";
    this.apiConnected = apiConnected;
    this.apiBase = apiBase;
  }
  async onOpen() {
    const { contentEl } = this;
    contentEl.empty();
    contentEl.createEl("h2", { text: "Obsidian Pilot" });
    const statusDiv = contentEl.createDiv({ cls: "status-bar" });
    if (this.apiConnected) {
      statusDiv.createSpan({ text: "\u{1F7E2} API \u5DF2\u8FDE\u63A5" });
    } else {
      statusDiv.createSpan({ text: "\u{1F534} API \u672A\u8FDE\u63A5" }).style.color = "#eb4d4b";
    }
    const pathDiv = contentEl.createDiv({ cls: "vault-path" });
    pathDiv.createEl("span", { text: "Vault \u8DEF\u5F84: " });
    const pathSpan = pathDiv.createEl("span", { text: "\u52A0\u8F7D\u4E2D..." });
    pathSpan.style.color = "#7d8590";
    try {
      this.vaultPath = "";
    } catch {
      this.vaultPath = "";
    }
    const btnGroup = contentEl.createDiv({ cls: "btn-grid" });
    this.addButton(btnGroup, "\u{1F4C1} \u521D\u59CB\u5316\u77E5\u8BC6\u5E93", async () => {
      const path = await this.promptVaultPath();
      if (!path) return;
      await this.doInit(path);
    });
    this.addButton(btnGroup, "\u{1F4E5} \u5BFC\u5165\u5206\u7C7B", async () => {
      const path = await this.promptVaultPath();
      if (!path) return;
      await this.doImport(path);
    });
    this.addButton(btnGroup, "\u{1F517} \u81EA\u52A8\u94FE\u63A5", async () => {
      const path = await this.promptVaultPath();
      if (!path) return;
      await this.doLinks(path);
    });
    this.addButton(btnGroup, "\u{1F916} AI \u8DEF\u7531", async () => {
      await this.doRoute();
    });
    this.addButton(btnGroup, "\u{1F9F9} \u65E5\u5E38\u7EF4\u62A4", async () => {
      const path = await this.promptVaultPath();
      if (!path) return;
      await this.doMaintain(path);
    });
    this.addButton(btnGroup, "\u{1F4CA} \u94FE\u63A5\u62A5\u544A", async () => {
      const path = await this.promptVaultPath();
      if (!path) return;
      await this.doLinkReport(path);
    });
    contentEl.createEl("div", { cls: "result-area" }).attr("id", "result-area");
  }
  addButton(container, text, onClick) {
    const btn = container.createEl("button", { text });
    btn.addClass("pilot-btn");
    btn.onclick = async () => {
      btn.disabled = true;
      btn.text = "\u23F3 \u5904\u7406\u4E2D...";
      try {
        await onClick();
      } finally {
        btn.disabled = false;
        btn.text = text;
      }
    };
  }
  async promptVaultPath() {
    if (this.vaultPath) {
      return this.vaultPath;
    }
    try {
      const vault = this.app.vault.adapter;
      const basePath = vault.getBasePath?.() || vault.basePath;
      if (basePath) {
        this.vaultPath = basePath;
        return basePath;
      }
    } catch {
    }
    const input = prompt("\u8BF7\u8F93\u5165 Vault \u8DEF\u5F84:", "");
    if (!input) return "";
    this.vaultPath = input;
    return input;
  }
  async apiPost(endpoint, body) {
    const url = `${this.apiBase}${endpoint}`;
    const resp = await (0, import_obsidian.requestUrl)({
      url,
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });
    return resp.json;
  }
  async doInit(path) {
    try {
      const data = await this.apiPost("/init", { vault_path: path });
      if (data.status === "success") {
        new import_obsidian.Notice(`\u2705 ${data.message}`, 3e3);
      } else {
        new import_obsidian.Notice(`\u274C ${data.message}`, 3e3);
      }
    } catch (e) {
      new import_obsidian.Notice(`API \u9519\u8BEF: ${e}`, 3e3);
    }
  }
  async doImport(path) {
    try {
      const data = await this.apiPost("/import", { vault_path: path });
      let msg = `\u{1F4CA} \u5BFC\u5165\u7ED3\u679C:
`;
      msg += `\u603B\u7B14\u8BB0: ${data.total_notes}
`;
      msg += `\u5206\u7C7B\u5206\u5E03: ${JSON.stringify(data.category_counts)}
`;
      if (data.uncategorized.length > 0) {
        msg += `\u672A\u5206\u7C7B: ${data.uncategorized.length} \u7BC7
`;
      }
      new import_obsidian.Notice(msg, 5e3);
      this.showResult(msg);
    } catch (e) {
      new import_obsidian.Notice(`API \u9519\u8BEF: ${e}`, 3e3);
    }
  }
  async doLinks(path) {
    try {
      const data = await this.apiPost("/links/report", { vault_path: path });
      let msg = `\u{1F517} \u94FE\u63A5\u5206\u6790:
`;
      msg += `\u603B\u7B14\u8BB0: ${data.total_notes}
`;
      msg += `\u7F3A\u5931\u94FE\u63A5: ${data.missing_links.length}
`;
      msg += `\u5B64\u7ACB\u7B14\u8BB0: ${data.isolated_notes.filter((n) => !n.has_outgoing && !n.has_incoming).length}
`;
      if (data.missing_links.length > 0) {
        msg += `
\u5EFA\u8BAE\u6DFB\u52A0\u7684\u94FE\u63A5:
`;
        for (const link of data.missing_links.slice(0, 10)) {
          msg += `  ${link.current_file} \u2192 ${link.suggested}
`;
        }
      }
      new import_obsidian.Notice(msg, 5e3);
      this.showResult(msg);
    } catch (e) {
      new import_obsidian.Notice(`API \u9519\u8BEF: ${e}`, 3e3);
    }
  }
  async doRoute() {
    const query = prompt("\u8F93\u5165\u67E5\u8BE2\u95EE\u9898:", "How do I set up a new vault?");
    if (!query) return;
    try {
      const data = await this.apiPost("/route", { query });
      let msg = `\u{1F916} \u8DEF\u7531\u63A8\u8350:
`;
      msg += `\u63A8\u8350\u6A21\u578B: ${data.recommended_model}
`;
      msg += `\u7F6E\u4FE1\u5EA6: ${(data.confidence * 100).toFixed(0)}%
`;
      if (data.local_knowledge) {
        msg += `\u672C\u5730\u77E5\u8BC6: ${data.local_knowledge}
`;
      }
      new import_obsidian.Notice(msg, 5e3);
      this.showResult(msg);
    } catch (e) {
      new import_obsidian.Notice(`API \u9519\u8BEF: ${e}`, 3e3);
    }
  }
  async doMaintain(path) {
    try {
      const data = await this.apiPost("/maintain", { vault_path: path, archive: false });
      let msg = `\u{1F9F9} \u7EF4\u62A4\u62A5\u544A:
`;
      msg += `\u603B\u7B14\u8BB0: ${data.total_notes}
`;
      msg += `\u8FC7\u671F\u7B14\u8BB0: ${data.expired_count}
`;
      msg += `\u91CD\u590D\u6807\u9898: ${data.duplicate_count}
`;
      msg += `\u5B64\u7ACB\u94FE\u63A5: ${data.orphaned_count}
`;
      if (data.expired_notes.length > 0) {
        msg += `
\u8FC7\u671F\u7B14\u8BB0:
`;
        for (const n of data.expired_notes.slice(0, 5)) {
          msg += `  ${n.title} (${n.age_days} \u5929)
`;
        }
      }
      new import_obsidian.Notice(msg, 5e3);
      this.showResult(msg);
    } catch (e) {
      new import_obsidian.Notice(`API \u9519\u8BEF: ${e}`, 3e3);
    }
  }
  async doLinkReport(path) {
    try {
      const data = await this.apiPost("/links/report", { vault_path: path });
      let msg = `\u{1F4CA} \u5B8C\u6574\u94FE\u63A5\u62A5\u544A:
`;
      msg += `\u603B\u7B14\u8BB0: ${data.total_notes}
`;
      msg += `\u7F3A\u5931\u94FE\u63A5: ${data.missing_links.length}
`;
      const isolated = data.isolated_notes.filter((n) => !n.has_outgoing && !n.has_incoming);
      msg += `\u5B8C\u5168\u5B64\u7ACB: ${isolated.length}
`;
      if (data.missing_links.length > 0) {
        msg += `
\u5EFA\u8BAE\u94FE\u63A5:
`;
        for (const link of data.missing_links) {
          msg += `  [[${link.suggested}]] \u2190 ${link.current_file}
`;
        }
      }
      new import_obsidian.Notice(msg, 5e3);
      this.showResult(msg);
    } catch (e) {
      new import_obsidian.Notice(`API \u9519\u8BEF: ${e}`, 3e3);
    }
  }
  showResult(text) {
    const resultArea = document.getElementById("result-area");
    if (resultArea) {
      resultArea.textContent = text;
    }
  }
  onClose() {
  }
};
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  LLMWikiModal
});
