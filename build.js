#!/usr/bin/env node
/**
 * Build script for Obsidian Pilot Plugin
 * Compiles TypeScript to JavaScript using esbuild
 */

const { build } = require('esbuild');
const fs = require('fs');
const path = require('path');

async function buildPlugin() {
  console.log('Building Obsidian Pilot Plugin...\n');

  // Ensure dist directory exists
  const distDir = path.join(__dirname, 'dist');
  if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
  }

  // Build main.js
  await build({
    entryPoints: [path.join(__dirname, 'main.ts')],
    bundle: true,
    outfile: path.join(distDir, 'main.js'),
    platform: 'browser',
    target: 'es2020',
    format: 'cjs',
    external: ['obsidian'],
    logLevel: 'info',
  });

  // Build modal.js
  await build({
    entryPoints: [path.join(__dirname, 'modal.ts')],
    bundle: true,
    outfile: path.join(distDir, 'modal.js'),
    platform: 'browser',
    target: 'es2020',
    format: 'cjs',
    external: ['obsidian'],
    logLevel: 'info',
  });

  // Copy manifest and styles to dist
  fs.copyFileSync(
    path.join(__dirname, 'manifest.json'),
    path.join(distDir, 'manifest.json')
  );
  fs.copyFileSync(
    path.join(__dirname, 'styles.css'),
    path.join(distDir, 'styles.css')
  );

  console.log('\nBuild complete! Output in dist/');
  console.log('Files:');
  console.log('  - main.js');
  console.log('  - modal.js');
  console.log('  - manifest.json');
  console.log('  - styles.css');
}

buildPlugin().catch(console.error);
