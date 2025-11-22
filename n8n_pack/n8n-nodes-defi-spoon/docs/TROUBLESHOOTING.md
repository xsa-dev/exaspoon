# Troubleshooting Node Display Issues in n8n

## Problem: New node is not visible in n8n

### Solution 1: Full n8n restart

1. **Stop n8n:**
   ```bash
   # Find n8n process
   ps aux | grep n8n
   
   # Stop it (Ctrl+C in terminal or kill PID)
   kill <PID>
   ```

2. **Clear n8n cache (optional):**
   ```bash
   # Remove node cache (if exists)
   rm -rf ~/.n8n/cache/*
   ```

3. **Start n8n again:**
   ```bash
   n8n start
   ```

4. **Check logs on startup:**
   You should see a line:
   ```
   Loaded all credentials and nodes from n8n-nodes-defi-spoon { "credentials": 2, "nodes": 3 }
   ```
   
   ⚠️ If you see `"nodes": 2` instead of `"nodes": 3`, the node is not loading.

### Solution 2: Installation check

Run the check:

```bash
cd /Users/alxy/Desktop/1PROJ/SpoonOs/n8n_pack/n8n-nodes-defi-spoon
node check-nodes.js
```

You should see all 3 nodes:
- ✓ DefiGetBalance
- ✓ DefiGetTransaction  
- ✓ PythonScript

### Solution 3: Package reinstallation

If the node is still not visible:

```bash
cd /Users/alxy/Desktop/1PROJ/SpoonOs/n8n_pack/n8n-nodes-defi-spoon

# Rebuild
npm run build

# Recreate package
npm pack

# Remove old installation
rm -rf ~/.n8n/nodes/node_modules/n8n-nodes-defi-spoon

# Install again
npm install ./n8n-nodes-defi-spoon-1.0.0.tgz \
  --prefix ~/.n8n/nodes \
  --legacy-peer-deps

# Restart n8n
```

### Solution 4: Check in n8n interface

1. Open n8n in browser
2. Create a new workflow
3. In node search, type: "DeFi Get Transaction"
4. Or find it in the "Transform" category

### Checking n8n logs

When starting n8n, check logs for errors:

```bash
# If n8n is running, logs can be seen in terminal
# Or check log file (if configured)
```

Look for lines:
- `Loaded all credentials and nodes from n8n-nodes-defi-spoon`
- `No codex available for: defiGetTransaction` (this is normal)
- Any errors mentioning `DefiGetTransaction`

### If nothing helped

Check n8n version:
```bash
n8n --version
```

Make sure you're using a compatible n8n version (>= 1.0.0).
