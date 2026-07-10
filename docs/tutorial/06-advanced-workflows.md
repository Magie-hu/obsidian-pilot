# Advanced Workflows

## Automation Pipeline

```bash
# 1. Initialize knowledge base
obsidian-pilot init ~/my-vault -t llm-wiki

# 2. Import raw materials
obsidian-pilot import ~/my-vault --apply

# 3. Automate links
obsidian-pilot link ~/my-vault --apply

# 4. Check AI routing
obsidian-pilot route ~/my-vault -q "Docker"

# 5. Daily maintenance
obsidian-pilot maintain ~/my-vault --archive
```

## Scheduled Tasks

Use cron for daily automated maintenance:

```bash
# Run maintenance daily at 2 AM
0 2 * * * obsidian-pilot maintain ~/vault --archive >> /var/log/obsidian-pilot.log
```

## Team Collaboration

1. Use Git to sync knowledge base
2. Assign roles (editor, reviewer)
3. Regularly merge branches

## Performance Optimization

1. Limit note count (< 10,000)
2. Regularly clean attachments
3. Use SSD storage
