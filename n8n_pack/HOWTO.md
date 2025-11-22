# Installation and Update Guide for n8n with n8n-nodes-defi-spoon

## Installing n8n

If n8n is not yet installed, follow these steps:

### Option 1: Installation via npm (recommended)

```bash
# Install n8n globally
npm install -g n8n

# Or via npx (without global installation)
npx n8n
```

### Verifying Installation

```bash
# Check n8n version
n8n --version

# Start n8n
n8n start
```

n8n will be available at: `http://localhost:5678`

---

## Installing n8n-nodes-defi-spoon Package

### Quick Installation (recommended)

Use the provided installation script:

```bash
cd n8n-nodes-defi-spoon
./install.sh
```

The script automatically:
- Creates the `~/.n8n/nodes` directory (if it doesn't exist)
- Removes the old package version (if installed)
- Installs the package to the correct location (`~/.n8n/nodes/node_modules/`)

### Manual Installation

If you want to install manually:

```bash
cd n8n-nodes-defi-spoon

# Make sure the package is built
npm run build
npm pack

# Install the package to ~/.n8n/nodes
npm install ./n8n-nodes-defi-spoon-1.0.0.tgz \
  --prefix ~/.n8n/nodes \
  --legacy-peer-deps
```

**Important:** Custom nodes must be installed in `~/.n8n/nodes/node_modules/`, NOT in n8n's own node_modules!

### After Installation

1. **Restart n8n:**
   ```bash
   # Stop n8n if it's running (Ctrl+C)
   # Then start it again:
   n8n start
   ```

2. **Verify Installation:**
   - Open n8n in your browser: `http://localhost:5678`
   - Create a new workflow
   - In the node list, look for:
     - **DeFi: Get Balance**
     - **DeFi: Get Transaction**
     - **DeFi: Get Wallet Transactions**
     - **DeFi: Monitor Wallet Transactions**
     - **Python Script (SpoonOS)**

3. **Configure RPC Credential:**
   - Go to **Credentials** section
   - Create a new credential of type **"RPC Provider"**
   - Specify the RPC URL (e.g., for Neo X: `https://mainnet-1.rpc.banelabs.org`)

### Verifying Installation via Logs

For detailed diagnostics, run n8n with debug logs:

```bash
# Option 1: Use the script
cd n8n-nodes-defi-spoon
./start-n8n-debug.sh

# Option 2: Manually
export N8N_LOG_LEVEL=debug
n8n start
```

In the logs, look for this line:
```
Loaded all credentials and nodes from n8n-nodes-defi-spoon { "credentials": 2, "nodes": 5 }
```

If you see fewer nodes than expected, check the installation.

---

## Updating n8n-nodes-defi-spoon Package

### Method 1: Use Installation Script (recommended)

The `install.sh` script automatically removes the old version before installing the new one:

```bash
cd n8n-nodes-defi-spoon

# Rebuild the package (if there were code changes)
npm run build
npm pack

# Run the installation script
./install.sh
```

### Method 2: Manual Update

```bash
cd n8n-nodes-defi-spoon

# 1. Rebuild the package
npm run build
npm pack

# 2. Remove the old version
rm -rf ~/.n8n/nodes/node_modules/n8n-nodes-defi-spoon

# 3. Install the new version
npm install ./n8n-nodes-defi-spoon-1.0.0.tgz \
  --prefix ~/.n8n/nodes \
  --legacy-peer-deps
```

### After Update

1. **Restart n8n:**
   ```bash
   # Stop n8n (Ctrl+C)
   # Start again:
   n8n start
   ```

2. **Verify the Update:**
   - Open n8n in your browser
   - Create a new workflow
   - Make sure all nodes are available and working correctly

---

## Updating n8n Itself

If you need to update n8n itself:

### Via npm

```bash
# Update n8n globally
npm update -g n8n

# Or install a specific version
npm install -g n8n@latest
```

### Via uv

```bash
# Update n8n via uv
uv pip install --upgrade n8n
```

### After Updating n8n

After updating n8n, it's recommended to reinstall the `n8n-nodes-defi-spoon` package:

```bash
cd n8n-nodes-defi-spoon
./install.sh
```

This ensures package compatibility with the new n8n version.

---

## Troubleshooting

### Nodes Don't Appear in the List

1. Check that the package is installed in the correct location:
   ```bash
   ls -la ~/.n8n/nodes/node_modules/n8n-nodes-defi-spoon
   ```

2. Check n8n logs on startup (see "Verifying Installation via Logs" section)

3. Make sure you restarted n8n after installation

### Installation Errors

1. Make sure the package is built:
   ```bash
   cd n8n-nodes-defi-spoon
   npm run build
   npm pack
   ```

2. Check that the `.tgz` file exists:
   ```bash
   ls -la n8n-nodes-defi-spoon-1.0.0.tgz
   ```

3. Try installing with the `--legacy-peer-deps` flag:
   ```bash
   npm install ./n8n-nodes-defi-spoon-1.0.0.tgz \
     --prefix ~/.n8n/nodes \
     --legacy-peer-deps
   ```

### Additional Help

- See documentation: `n8n-nodes-defi-spoon/docs/`
- Debug file: `n8n-nodes-defi-spoon/docs/DEBUG.md`
- Troubleshooting: `n8n-nodes-defi-spoon/docs/TROUBLESHOOTING.md`
