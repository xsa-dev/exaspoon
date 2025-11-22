# Running n8n with Debug Logging

## Quick Method

Use the ready-made script:
```bash
cd /Users/alxy/Desktop/1PROJ/SpoonOs/n8n_pack/n8n-nodes-defi-spoon
./start-n8n-debug.sh
```

## Manual Launch

### Option 1: Debug level logging only
```bash
export N8N_LOG_LEVEL=debug
n8n start
```

### Option 2: With additional debug for node loading
```bash
export N8N_LOG_LEVEL=debug
export DEBUG=n8n:*
n8n start
```

### Option 3: Maximum detail
```bash
export N8N_LOG_LEVEL=debug
export N8N_LOG_OUTPUT=console
export DEBUG=n8n:*
n8n start
```

## What to Look for in Logs

When starting n8n with debug logging, you will see:

1. **Package loading:**
   ```
   Lazy-loading nodes and credentials from n8n-nodes-defi-spoon
   ```

2. **Loading result:**
   ```
   Loaded all credentials and nodes from n8n-nodes-defi-spoon { "credentials": 2, "nodes": 3 }
   ```
   
   ⚠️ **Important:** Should be `"nodes": 3` (all three nodes):
   - DefiGetBalance
   - DefiGetTransaction
   - PythonScript

3. **Codex warnings (this is normal):**
   ```
   No codex available for: defiGetBalance
   No codex available for: defiGetTransaction
   No codex available for: pythonScript
   ```

4. **Loading errors (if any):**
   ```
   Error loading node: ...
   ```

## Saving Logs to File

To save logs to a file:
```bash
export N8N_LOG_LEVEL=debug
n8n start 2>&1 | tee n8n-debug.log
```

Or:
```bash
export N8N_LOG_LEVEL=debug
n8n start > n8n-debug.log 2>&1
```

## Logging Levels

Available levels:
- `error` - errors only
- `warn` - warnings and errors
- `info` - informational messages (default)
- `debug` - detailed debug information
- `verbose` - maximum detail

## Stopping n8n

To stop, press `Ctrl+C` in the terminal where n8n is running.
