# Troubleshooting Guide

## Codex Infinite Loop

**Symptoms:** Codex processes the same file infinitely

**Solutions:**
1. Check if `conflict.py` is enabled
2. Limit Codex max iterations
3. Use `--dry-run` to preview effects

## Sync Conflicts

**Symptoms:** Multiple sources modify the same file

**Solutions:**
1. Use Git branches for management
2. Enable conflict detection module
3. Regularly merge conflicts

## MCP Configuration Errors

**Symptoms:** MCP server connection fails

**Solutions:**
1. Check if port is occupied
2. Verify environment variable configuration
3. Check log files

## Knowledge Base Corruption

**Solutions:**
1. Restore from backup
2. Run `repair` command
3. Rebuild index page
