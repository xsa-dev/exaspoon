# n8n-nodes-defi-spoon

Custom Web3/DeFi nodes for n8n.

Includes:
✓ RPC credential  
✓ DeFi: Get Balance node (ETH & ERC20)
✓ DeFi: Get Transaction node (Neo X & EVM-compatible chains)
✓ DeFi: Get Wallet Transactions node (get all transactions for a wallet)
✓ DeFi: Monitor Wallet Transactions node (trigger for monitoring new transactions)
✓ Python Script (SpoonOS) node

## Installation (self-hosted n8n)

### Quick Install (Recommended)

Use the provided installation script:

```bash
cd n8n-nodes-defi-spoon
./install.sh
```

### Manual Installation

1. **Install the package to ~/.n8n/nodes (correct location for custom nodes):**
   ```bash
   npm install ./n8n-nodes-defi-spoon-1.0.0.tgz \
     --prefix ~/.n8n/nodes \
     --legacy-peer-deps
   ```
   
   **Important:** Custom nodes must be installed in `~/.n8n/nodes/node_modules/`, NOT in n8n's own node_modules!

2. **Restart n8n:**
   ```bash
   # Stop n8n if running (Ctrl+C)
   # Then start it again
   n8n start
   ```

### Method 2: Install from local directory (for development)

1. **Build the package:**
   ```bash
   cd n8n-nodes-defi-spoon
   npm run build
   ```

2. **Install using npm link (recommended for development):**
   ```bash
   # In the package directory
   npm link
   
   # In n8n directory
   npm link n8n-nodes-defi-spoon
   ```

3. **Or install directly to ~/.n8n/nodes:**
   ```bash
   npm install ./n8n-nodes-defi-spoon \
     --prefix ~/.n8n/nodes \
     --legacy-peer-deps
   ```

### Verify Installation

After restarting n8n, you should see the new nodes in the node list:
- **DeFi: Get Balance** - Get native token (GAS) and ERC20 token balances
- **DeFi: Get Transaction** - Get transaction details by hash, receipt, or block
- **DeFi: Get Wallet Transactions** - Get all transactions for a wallet address
- **DeFi: Monitor Wallet Transactions** - Monitor wallet for new transactions (trigger node)
- **Python Script (SpoonOS)** - Execute Python scripts

### Debug Logging

To see detailed logs of node loading when starting n8n:

**Option 1: Use the script**
```bash
cd n8n-nodes-defi-spoon
./start-n8n-debug.sh
```

**Option 2: Manual**
```bash
export N8N_LOG_LEVEL=debug
n8n start
```

In the logs, look for the line:
```
Loaded all credentials and nodes from n8n-nodes-defi-spoon { "credentials": 2, "nodes": 5 }
```

If you see fewer nodes than expected, some nodes failed to load.

## Documentation

- **[DeFi Get Balance - Complete Guide](docs/DEFI_GET_BALANCE.md)** - Detailed instructions for using the node to get native token (GAS) and ERC20 token balances on NeoX
- **[Installation](docs/INSTALL.md)** - Package installation instructions
- **[Debugging](docs/DEBUG.md)** - Debugging guide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Solutions to common problems

## Neo X (EVM) Testnet Configuration

### Network Information
- **Network Name:** Neo X Chain
- **Chain ID:** 47763
- **RPC URL:** https://mainnet-1.rpc.banelabs.org
- **Currency Symbol:** GAS
- **Explorer:** https://xexplorer.neo.org

### Setup Instructions

1. **Configure RPC Credentials:**
   - In n8n, go to Credentials
   - Create new "RPC Provider" credential
   - Set RPC URL: `https://mainnet-1.rpc.banelabs.org`

2. **Using DeFi Get Balance Node:**
   
   To get the balance of a native token (GAS) or ERC20 token:
   - See detailed documentation: [docs/DEFI_GET_BALANCE.md](docs/DEFI_GET_BALANCE.md)
   - Example usage with contract: `0xBe8212624EAf3ed34EA68329481f004287ffF594`

3. **Using DeFi Get Transaction Node:**
   
   The node supports 4 operations:
   
   - **Get Transaction by Hash:** Get full transaction details by hash
     - Input: Transaction hash (0x...)
     - Returns: Transaction details (from, to, value, gas, etc.)
   
   - **Get Transaction Receipt:** Get transaction receipt with logs
     - Input: Transaction hash (0x...)
     - Returns: Receipt with status, logs, gas used, contract address
   
   - **Get Block Transactions:** Get all transactions from a specific block
     - Input: Block number (decimal) or "latest"
     - Returns: Array of all transactions in the block
   
   - **Get Latest Block Transactions:** Get all transactions from the latest block
     - No input required
     - Returns: Array of all transactions from the latest block

4. **Using DeFi Get Wallet Transactions Node:**
   
   Get all transactions for a specific wallet address:
   - Input: Wallet address, block range (from/to), transaction type filter (all/sent/received)
   - Returns: Array of transactions with details (hash, from, to, value, gas, etc.)
   - Features: Configurable block range, transaction type filtering, limit, timeout protection

5. **Using DeFi Monitor Wallet Transactions Node:**
   
   Monitor a wallet for new transactions (trigger node):
   - Input: Wallet address, transaction type filter, poll interval
   - Behavior: Continuously polls for new blocks and emits transactions matching the wallet
   - Use case: Real-time monitoring, webhook triggers, automated workflows

### Example Workflow

1. Add "DeFi Get Transaction" node
2. Select credential: Your RPC Provider credential
3. Choose operation (e.g., "Get Latest Block Transactions")
4. The node will return transaction data in JSON format

### Transaction Data Structure

**Transaction Object:**
```json
{
  "hash": "0x...",
  "from": "0x...",
  "to": "0x...",
  "value": "1000000000000000000",
  "gas": "21000",
  "gasPrice": "20000000000",
  "nonce": "5",
  "blockNumber": "12345",
  "transactionIndex": "0"
}
```

**Transaction Receipt:**
```json
{
  "transactionHash": "0x...",
  "status": "success",
  "gasUsed": "21000",
  "contractAddress": null,
  "logs": []
}
```
