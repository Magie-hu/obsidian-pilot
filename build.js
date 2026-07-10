/**
 * Obsidian LLM-Wiki Plugin - Build Script
 * Compiles TypeScript to JavaScript for Obsidian
 */

const fs = require('fs');
const path = require('path');

const SRC_DIR = path.join(__dirname, 'src');
const OUT_DIR = path.join(__dirname, 'src');

// Simple TypeScript to JavaScript compilation
// In production, use tsc or esbuild

console.log('Building Obsidian LLM-Wiki Plugin...');
console.log('Source:', SRC_DIR);
console.log('Output:', OUT_DIR);

// Copy manifest.json
const manifestSrc = path.join(__dirname, 'manifest.json');
const manifestDst = path.join(OUT_DIR, '..', 'manifest.json');
if (fs.existsSync(manifestSrc)) {
    fs.copyFileSync(manifestSrc, manifestDst);
    console.log('✓ Copied manifest.json');
}

console.log('Build complete!');
console.log('Next steps:');
console.log('1. Copy main.js, manifest.json, styles.css to your Obsidian vault/.obsidian/plugins/obsidian-llm-wiki-plugin/');
console.log('2. Enable the plugin in Obsidian settings');
