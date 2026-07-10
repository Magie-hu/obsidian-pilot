#!/usr/bin/env node
/**
 * Build script for Obsidian Pilot Plugin
 * Compiles TypeScript to JavaScript using esbuild
 */

const { build } = require('esbuild');
const fs = require('fs');
const path = require('path');

async function buildPlugin() {
    console.log('Building Obsidian Pilot Plugin...');

    const manifest = JSON.parse(fs.readFileSync('manifest.json', 'utf8'));
    const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));

    // Clean dist
    const distDir = path.join(__dirname, 'dist');
    if (fs.existsSync(distDir)) {
        fs.rmSync(distDir, { recursive: true });
    }
    fs.mkdirSync(distDir);

    // Build main.ts
    await build({
        entryPoints: ['main.ts'],
        bundle: true,
        outfile: 'dist/main.js',
        external: ['obsidian'],
        format: 'cjs',
        target: 'es2020',
        platform: 'node',
        logLevel: 'info',
    });

    // Build modal.ts
    await build({
        entryPoints: ['modal.ts'],
        bundle: true,
        outfile: 'dist/modal.js',
        external: ['obsidian'],
        format: 'cjs',
        target: 'es2020',
        platform: 'node',
        logLevel: 'info',
    });

    // Copy manifest.json and styles.css
    fs.copyFileSync('manifest.json', 'dist/manifest.json');
    fs.copyFileSync('styles.css', 'dist/styles.css');

    console.log('Build complete! Output in dist/');
    console.log('Files:');
    fs.readdirSync('dist').forEach(f => console.log(`  - ${f}`));
}

buildPlugin().catch(err => {
    console.error('Build failed:', err);
    process.exit(1);
});
