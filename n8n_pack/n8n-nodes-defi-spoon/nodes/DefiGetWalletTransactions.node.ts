import type {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
} from 'n8n-workflow';

import Web3 from 'web3';

export class DefiGetWalletTransactions implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'DeFi Get Wallet Transactions',
		name: 'defiGetWalletTransactions',
		group: ['transform'],
		icon: 'fa:history',
		version: 1,
		description: 'Get all transactions for a wallet address',
		defaults: {
			name: 'DeFi Get Wallet Transactions',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'rpcApi',
				required: true,
			},
		],
		properties: [
			{
				displayName: 'Wallet Address',
				name: 'address',
				type: 'string',
				default: '',
				required: true,
				description: 'The wallet address to get transactions for',
			},
			{
				displayName: 'From Block',
				name: 'fromBlock',
				type: 'string',
				default: '',
				description: 'Start scanning from this block number. Leave empty to scan last 1000 blocks. Use "latest" for current block, or specific block number.',
			},
			{
				displayName: 'To Block',
				name: 'toBlock',
				type: 'string',
				default: 'latest',
				description: 'Scan up to this block number (latest = current block)',
			},
			{
				displayName: 'Transaction Type',
				name: 'transactionType',
				type: 'options',
				options: [
					{
						name: 'All Transactions',
						value: 'all',
						description: 'Both sent and received transactions',
					},
					{
						name: 'Sent Only',
						value: 'sent',
						description: 'Only transactions sent from this address',
					},
					{
						name: 'Received Only',
						value: 'received',
						description: 'Only transactions received by this address',
					},
				],
				default: 'all',
				description: 'Filter transactions by type',
			},
			{
				displayName: 'Limit',
				name: 'limit',
				type: 'number',
				default: 100,
				description: 'Maximum number of transactions to return (0 = no limit)',
			},
			{
				displayName: 'Max Blocks to Scan',
				name: 'maxBlocks',
				type: 'number',
				default: 1000,
				description: 'Maximum number of blocks to scan (to prevent timeout). Default: 1000',
			},
			{
				displayName: 'Timeout (seconds)',
				name: 'timeout',
				type: 'number',
				default: 60,
				description: 'Maximum execution time in seconds. Default: 60',
			},
		],
	};

	async execute(this: IExecuteFunctions) {
		const items = this.getInputData();
		const returnItems: INodeExecutionData[] = [];

		// Get RPC URL from credentials
		const credentials = await this.getCredentials('rpcApi');
		const rpcUrl = credentials.rpcUrl as string;

		if (!rpcUrl) {
			throw new Error('RPC URL is required in credentials');
		}

		// Initialize Web3
		const web3 = new Web3(rpcUrl);

		for (let i = 0; i < items.length; i++) {
			try {
				const address = this.getNodeParameter('address', i) as string;
				const fromBlock = this.getNodeParameter('fromBlock', i) as string;
				const toBlock = this.getNodeParameter('toBlock', i) as string;
				const transactionType = this.getNodeParameter('transactionType', i) as string;
				const limit = this.getNodeParameter('limit', i) as number;
				const maxBlocks = this.getNodeParameter('maxBlocks', i, 1000) as number;
				const timeoutSeconds = this.getNodeParameter('timeout', i, 60) as number;

				if (!address || !web3.utils.isAddress(address)) {
					throw new Error('Invalid wallet address');
				}

				// Normalize address to checksum format
				const normalizedAddress = web3.utils.toChecksumAddress(address);

				// Parse block numbers
				let fromBlockNum: number | string = fromBlock;
				let toBlockNum: number | string = toBlock === 'latest' ? 'latest' : toBlock;

				if (fromBlockNum !== 'latest' && fromBlockNum !== 'pending') {
					fromBlockNum = parseInt(fromBlockNum, 10);
					if (isNaN(fromBlockNum as number)) {
						throw new Error('Invalid fromBlock number');
					}
				}

				if (toBlockNum !== 'latest' && toBlockNum !== 'pending') {
					toBlockNum = parseInt(toBlockNum, 10);
					if (isNaN(toBlockNum as number)) {
						throw new Error('Invalid toBlock number');
					}
				}

				// Get current block number
				const currentBlock = Number(await web3.eth.getBlockNumber());
				
				// Handle 'latest' for both fromBlock and toBlock
				// If fromBlock is empty or 'latest', scan last 1000 blocks by default
				if (fromBlockNum === 'latest' || fromBlock === '') {
					fromBlockNum = Math.max(0, currentBlock - 1000);
				}
				if (toBlockNum === 'latest') {
					toBlockNum = currentBlock;
				}

				// Collect all transactions
				const allTransactions: any[] = [];
				const addressLower = normalizedAddress.toLowerCase();

				// Scan blocks
				const startBlock = typeof fromBlockNum === 'number' ? fromBlockNum : 0;
				let endBlock = typeof toBlockNum === 'number' ? toBlockNum : startBlock;

				// Ensure endBlock doesn't exceed current block
				if (endBlock > currentBlock) {
					endBlock = currentBlock;
				}

				// Ensure startBlock is not greater than endBlock
				if (startBlock > endBlock) {
					throw new Error(
						`Invalid block range: fromBlock (${startBlock}) is greater than toBlock (${endBlock})`,
					);
				}

				// Calculate blocks to scan
				const totalBlocks = endBlock - startBlock + 1;
				const blocksToScan = Math.min(totalBlocks, maxBlocks);

				if (totalBlocks > maxBlocks) {
					throw new Error(
						`Too many blocks to scan (${totalBlocks}). Maximum allowed: ${maxBlocks}. Please reduce the range or increase maxBlocks parameter.`,
					);
				}

				// Set timeout
				const startTime = Date.now();
				const timeoutMs = timeoutSeconds * 1000;

				// Scan blocks in batches with timeout checking
				const batchSize = 50; // Reduced batch size for better responsiveness
				let scannedBlocks = 0;

				for (let blockNum = startBlock; blockNum <= endBlock; blockNum += batchSize) {
					// Check timeout
					if (Date.now() - startTime > timeoutMs) {
						throw new Error(
							`Timeout after ${timeoutSeconds} seconds. Scanned ${scannedBlocks} blocks, found ${allTransactions.length} transactions.`,
						);
					}

					const batchEnd = Math.min(blockNum + batchSize - 1, endBlock);
					const blockPromises: Promise<any>[] = [];

					// Create promises with individual error handling
					for (let b = blockNum; b <= batchEnd; b++) {
						blockPromises.push(
							web3.eth
								.getBlock(b, true)
								.catch((err) => {
									// Log error but don't fail completely
									console.warn(`Failed to get block ${b}:`, err.message);
									return null;
								}),
						);
					}

					// Wait for batch with timeout
					const batchTimeout = Promise.race([
						Promise.all(blockPromises),
						new Promise<any[]>((_, reject) =>
							setTimeout(() => reject(new Error('Batch timeout')), 30000),
						),
					]).catch(() => {
						// If batch times out, return nulls
						return new Array(blockPromises.length).fill(null) as any[];
					});

					const blocks: any[] = await batchTimeout;

					for (const block of blocks) {
						if (!block || !block.transactions) {
							scannedBlocks++;
							continue;
						}

						// Process transactions - handle both full objects and hashes
						const txPromises: Promise<any>[] = [];
						
						for (const tx of block.transactions) {
							// If transaction is a hash string, fetch full transaction
							if (typeof tx === 'string') {
								txPromises.push(
									web3.eth.getTransaction(tx).catch(() => null)
								);
							} else {
								// Already a full transaction object
								txPromises.push(Promise.resolve(tx));
							}
						}

						// Wait for all transactions to be resolved
						const resolvedTxs = await Promise.all(txPromises);

						for (const tx of resolvedTxs) {
							if (!tx) continue; // Skip failed fetches

							const txFrom = (tx.from || '').toLowerCase();
							const txTo = (tx.to || '').toLowerCase();

							let includeTx = false;

							if (transactionType === 'all') {
								includeTx = txFrom === addressLower || txTo === addressLower;
							} else if (transactionType === 'sent') {
								includeTx = txFrom === addressLower;
							} else if (transactionType === 'received') {
								includeTx = txTo === addressLower;
							}

							if (includeTx) {
								allTransactions.push({
									hash: tx.hash,
									nonce: tx.nonce.toString(),
									blockHash: tx.blockHash,
									blockNumber: tx.blockNumber?.toString(),
									transactionIndex: tx.transactionIndex?.toString(),
									from: tx.from,
									to: tx.to,
									value: tx.value.toString(),
									gas: tx.gas.toString(),
									gasPrice: tx.gasPrice?.toString(),
									input: tx.input,
									chainId: tx.chainId?.toString(),
									type: txFrom === addressLower ? 'sent' : 'received',
								});
							}

							// Apply limit if set
							if (limit > 0 && allTransactions.length >= limit) {
								break;
							}
						}

						scannedBlocks++;

						if (limit > 0 && allTransactions.length >= limit) {
							break;
						}
					}

					if (limit > 0 && allTransactions.length >= limit) {
						break;
					}
				}

				// Sort by block number (newest first)
				allTransactions.sort((a, b) => {
					const aNum = parseInt(a.blockNumber || '0', 10);
					const bNum = parseInt(b.blockNumber || '0', 10);
					return bNum - aNum;
				});

				// Apply limit after sorting
				const finalTransactions = limit > 0 
					? allTransactions.slice(0, limit)
					: allTransactions;

				const executionTime = ((Date.now() - startTime) / 1000).toFixed(2);

				returnItems.push({
					json: {
						address: normalizedAddress,
						fromBlock: startBlock,
						toBlock: endBlock,
						blocksScanned: scannedBlocks,
						transactionType,
						totalFound: allTransactions.length,
						returned: finalTransactions.length,
						executionTimeSeconds: executionTime,
						transactions: finalTransactions,
					},
				});
			} catch (error: any) {
				if (this.continueOnFail()) {
					returnItems.push({
						json: {
							...items[i].json,
							error: error.message || 'Unknown error',
						},
					});
					continue;
				}
				throw error;
			}
		}

		return [returnItems];
	}
}

