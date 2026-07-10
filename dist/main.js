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

// main.ts
var main_exports = {};
__export(main_exports, {
  default: () => ObsidianPilotPlugin
});
module.exports = __toCommonJS(main_exports);
var import_obsidian = require("obsidian");
var ObsidianPilotPlugin = class extends import_obsidian.Plugin {
  constructor() {
    super(...arguments);
    this.apiUrl = "http://localhost:8080";
  }
  async onload() {
    console.log("Loading Pilot Assistant plugin...");
    this.addRibbonIcon("book-open", "Pilot Assistant", () => {
      this.openModal();
    });
    this.addCommand({
      id: "open-pilot-panel",
      name: "Open Pilot Panel",
      callback: () => {
        this.openModal();
      }
    });
    console.log("Pilot Assistant plugin loaded.");
  }
  async openModal() {
    const modal = new PilotModal(this.app, this.apiUrl);
    modal.open();
  }
  async onunload() {
    console.log("Unloading Obsidian Pilot plugin...");
  }
};
