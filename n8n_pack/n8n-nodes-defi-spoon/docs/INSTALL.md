# Installation Guide

## ✅ Installation Complete!

The `n8n-nodes-defi-spoon` package has been successfully installed in your local n8n.

### Installed Components:

**Nodes:**
- ✅ DeFi: Get Balance
- ✅ DeFi: Get Transaction (new!)
- ✅ Python Script (SpoonOS)

**Credentials:**
- ✅ RPC Provider
- ✅ Python Environment

### Next Steps:

1. **Restart n8n:**
   ```bash
   # Stop n8n if it's running (Ctrl+C)
   # Then start again:
   n8n start
   ```

2. **Verify installation:**
   - Open n8n in browser
   - Create a new workflow
   - In the node list, find:
     - "DeFi: Get Balance"
     - "DeFi: Get Transaction"
     - "Python Script (SpoonOS)"

3. **Configure RPC Credential for Neo X:**
   - Go to Credentials
   - Create a new credential of type "RPC Provider"
   - Specify RPC URL: `https://mainnet-1.rpc.banelabs.org`

### To update the package in the future:

```bash
cd /Users/alxy/Desktop/1PROJ/SpoonOs/n8n_pack/n8n-nodes-defi-spoon

# Rebuild package
npm run build
npm pack

# Install updated version
rm -rf ~/.n8n/nodes/node_modules/n8n-nodes-defi-spoon
npm install ./n8n-nodes-defi-spoon-1.0.0.tgz \
  --prefix ~/.n8n/nodes \
  --legacy-peer-deps

# Restart n8n
```

### Or use the script:

```bash
cd /Users/alxy/Desktop/1PROJ/SpoonOs/n8n_pack/n8n-nodes-defi-spoon
./install.sh
```
