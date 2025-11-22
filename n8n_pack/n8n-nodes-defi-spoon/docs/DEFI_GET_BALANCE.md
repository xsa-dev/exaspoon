# DeFi Get Balance - Usage Guide

## Overview

The **DeFi Get Balance** node allows you to get the balance of a native token (GAS for NeoX) or the balance of an ERC20 token on any EVM-compatible blockchain, including NeoX Chain.

## Supported Operations

1. **Native token balance** (GAS for NeoX) - leave the Token Address field empty
2. **ERC20 token balance** - specify the token contract address

## NeoX Chain Setup

### Step 1: RPC Credential Configuration

1. Open n8n and go to **Credentials** section
2. Create a new credential of type **"RPC Provider"**
3. Specify the following parameters:

   **RPC URL for NeoX Mainnet:**
   ```
   https://mainnet-1.rpc.banelabs.org
   ```

   **Alternative RPC URLs (if main one is unavailable):**
   - `https://rpc.banelabs.org`
   - `https://neox-mainnet.rpc.banelabs.org`

4. Save the credential with a clear name, for example: `NeoX Mainnet RPC`

### Step 2: NeoX Network Information

- **Network Name:** Neo X Chain
- **Chain ID:** 47763
- **Currency Symbol:** GAS
- **Explorer:** https://xexplorer.neo.org

## Using the Node

### Option 1: Getting Native Token Balance (GAS)

1. Add the **"DeFi Get Balance"** node to your workflow
2. In the **"RPC URL"** field, enter: `https://mainnet-1.rpc.banelabs.org`
   - Or use credential: select the previously created credential "NeoX Mainnet RPC"
3. In the **"Wallet Address"** field, specify the wallet address (e.g., `0x...`)
4. Leave the **"Token Address"** field **empty**
5. Run the workflow

**Result:**
```json
{
  "address": "0x...",
  "tokenAddress": "native",
  "balance": "1000000000000000000"
}
```

> **Note:** Balance is returned in wei (smallest unit). To convert to GAS, divide by 10^18.

### Option 2: Getting ERC20 Token Balance

To get the balance of a token from contract `0xBe8212624EAf3ed34EA68329481f004287ffF594`:

1. Add the **"DeFi Get Balance"** node to your workflow
2. In the **"RPC URL"** field, enter: `https://mainnet-1.rpc.banelabs.org`
   - Or use credential: select the previously created credential "NeoX Mainnet RPC"
3. In the **"Wallet Address"** field, specify the wallet address whose balance you want to check
4. In the **"Token Address"** field, specify the token contract address:
   ```
   0xBe8212624EAf3ed34EA68329481f004287ffF594
   ```
5. Run the workflow

**Result:**
```json
{
  "address": "0x...",
  "tokenAddress": "0xBe8212624EAf3ed34EA68329481f004287ffF594",
  "balance": "50000000000000000000"
}
```

> **Note:** ERC20 token balance is also returned in smallest units (usually 18 decimal places). Check the contract decimals for proper conversion.

## Usage Examples

### Example 1: Checking GAS Wallet Balance

```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
  "tokenAddress": "",
  "rpcUrl": "https://mainnet-1.rpc.banelabs.org"
}
```

### Example 2: Checking Token Balance from Contract 0xBe8212624EAf3ed34EA68329481f004287ffF594

```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
  "tokenAddress": "0xBe8212624EAf3ed34EA68329481f004287ffF594",
  "rpcUrl": "https://mainnet-1.rpc.banelabs.org"
}
```

### Example 3: Using in Workflow with Multiple Addresses

1. Add a **"Set"** or **"Code"** node to prepare an array of addresses
2. Connect the **"DeFi Get Balance"** node
3. The node will automatically process all items from the previous node
4. Each item should contain fields:
   - `address` - wallet address
   - `tokenAddress` - contract address (or empty for native token)
   - `rpcUrl` - RPC URL (or use credential)

## Working with Results

### Converting Balance to Readable Format

For native token (GAS):
```javascript
const balanceInWei = "1000000000000000000";
const balanceInGas = parseFloat(balanceInWei) / 1e18;
// Result: 1.0 GAS
```

For ERC20 token (usually 18 decimals):
```javascript
const balanceInWei = "50000000000000000000";
const balanceInTokens = parseFloat(balanceInWei) / 1e18;
// Result: 50.0 tokens
```

### Using in n8n Expression

In a **Code** or **Function** node you can use:

```javascript
// Get balance from previous node
const balance = $input.item.json.balance;
const address = $input.item.json.address;

// Convert to GAS
const balanceInGas = parseFloat(balance) / 1e18;

return {
  json: {
    address: address,
    balanceWei: balance,
    balanceGas: balanceInGas,
    formatted: `${balanceInGas} GAS`
  }
};
```

## Contract Information 0xBe8212624EAf3ed34EA68329481f004287ffF594

- **Contract Address:** `0xBe8212624EAf3ed34EA68329481f004287ffF594`
- **Network:** NeoX Mainnet
- **Explorer:** https://xexplorer.neo.org/address/0xBe8212624EAf3ed34EA68329481f004287ffF594
- **Type:** ERC20 token

To get additional token information (name, symbol, decimals), use standard ERC20 methods:
- `name()` - token name
- `symbol()` - token symbol
- `decimals()` - number of decimal places
- `totalSupply()` - total token supply

## Troubleshooting

### Error: "Invalid RPC URL"

**Solution:**
- Check RPC URL correctness
- Ensure RPC endpoint is accessible
- Try an alternative RPC URL

### Error: "Invalid address"

**Solution:**
- Ensure address starts with `0x`
- Check address correctness (42 characters for Ethereum/NeoX)
- Use a valid checksum address

### Error: "Contract not found" or "Invalid token address"

**Solution:**
- Check that the contract exists on NeoX network
- Ensure the contract supports ERC20 standard
- Verify contract address in explorer: https://xexplorer.neo.org

### Balance Returns as "0"

**Possible causes:**
- Wallet actually has no balance
- Incorrect wallet address
- Incorrect token contract address
- Token doesn't support `balanceOf()` method

### Slow Node Performance

**Solution:**
- Check RPC endpoint speed
- Try using a different RPC URL
- Ensure RPC endpoint is not overloaded

## Additional Resources

- [NeoX Explorer](https://xexplorer.neo.org)
- [NeoX Documentation](https://docs.neo.org)
- [ERC20 Standard](https://eips.ethereum.org/EIPS/eip-20)
- [Web3.js Documentation](https://web3js.readthedocs.io/)

## Complete Workflow Example

1. **Start** - workflow start
2. **Set** - set parameters:
   ```json
   {
     "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0",
     "tokenAddress": "0xBe8212624EAf3ed34EA68329481f004287ffF594",
     "rpcUrl": "https://mainnet-1.rpc.banelabs.org"
   }
   ```
3. **DeFi Get Balance** - get balance
4. **Code** - format result:
   ```javascript
   const balance = $input.item.json.balance;
   const balanceFormatted = parseFloat(balance) / 1e18;
   
   return {
     json: {
       ...$input.item.json,
       balanceFormatted: balanceFormatted,
       message: `Balance: ${balanceFormatted} tokens`
     }
   };
   ```
5. **Send Email** or **Webhook** - send result

## Technical Details

### Used ABI

The node uses minimal ERC20 ABI for `balanceOf` method:

```json
[
  {
    "constant": true,
    "inputs": [{ "name": "_owner", "type": "address" }],
    "name": "balanceOf",
    "outputs": [{ "name": "balance", "type": "uint256" }],
    "type": "function"
  }
]
```

### Return Data Format

```typescript
{
  address: string;        // Wallet address
  tokenAddress: string;   // Contract address or "native"
  balance: string;       // Balance in wei (string representation)
}
```

## Security

⚠️ **Important Recommendations:**

1. **Do not store private keys** in n8n workflows
2. **Use credentials** to store RPC URL instead of directly specifying in node
3. **Verify addresses** before using in production
4. **Restrict access** to workflows working with blockchain
5. **Use rate limiting** for bulk requests

## Support

If you encounter problems:
1. Check the "Troubleshooting" section above
2. Review n8n logs (enable debug mode)
3. Check documentation in `docs/TROUBLESHOOTING.md`
4. Ensure RPC endpoint is accessible and working correctly
