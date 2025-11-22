import type {
	ITriggerFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	ITriggerResponse,
} from 'n8n-workflow';

import Web3 from 'web3';

export class DefiMonitorWalletTransactions implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'DeFi Monitor Wallet Transactions',
		name: 'defiMonitorWalletTransactions',
		group: ['trigger'],
		icon: 'fa:eye',
		version: 1,
		description: 'Monitor wallet for new transactions (webhook/trigger)',
		defaults: {
			name: 'DeFi Monitor Wallet',
		},
		inputs: [],
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
				description: 'The wallet address to monitor',
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
				displayName: 'Poll Interval (seconds)',
				name: 'pollInterval',
				type: 'number',
				default: 5,
				description: 'How often to check for new blocks (in seconds)',
			},
			{
				displayName: 'Start Block',
				name: 'startBlock',
				type: 'string',
				default: 'latest',
				description: 'Block number to start monitoring from (latest = current block)',
			},
		],
	};

	async trigger(this: ITriggerFunctions): Promise<ITriggerResponse> {
		const address = this.getNodeParameter('address', 0) as string;
		const transactionType = this.getNodeParameter('transactionType', 0) as string;
		const pollInterval = (this.getNodeParameter('pollInterval', 0) as number) * 1000; // Convert to ms
		const startBlockParam = this.getNodeParameter('startBlock', 0) as string;

		// Get RPC URL from credentials
		const credentials = await this.getCredentials('rpcApi');
		const rpcUrl = credentials.rpcUrl as string;

		if (!rpcUrl) {
			throw new Error('RPC URL is required in credentials');
		}

		// Initialize Web3
		const web3 = new Web3(rpcUrl);

		if (!address || !web3.utils.isAddress(address)) {
			throw new Error('Invalid wallet address');
		}

		// Normalize address to checksum format
		const normalizedAddress = web3.utils.toChecksumAddress(address);
		const addressLower = normalizedAddress.toLowerCase();

		// Determine starting block
		let lastProcessedBlock: number;
		if (startBlockParam === 'latest') {
			lastProcessedBlock = Number(await web3.eth.getBlockNumber());
		} else {
			const parsed = parseInt(startBlockParam, 10);
			if (isNaN(parsed)) {
				throw new Error('Invalid startBlock number');
			}
			lastProcessedBlock = parsed;
		}

		// Polling function
		const pollForNewTransactions = async () => {
			try {
				const currentBlock = Number(await web3.eth.getBlockNumber());

				// Process new blocks since last check
				if (currentBlock > lastProcessedBlock) {
					const transactionsToEmit: INodeExecutionData[] = [];

					for (let blockNum = lastProcessedBlock + 1; blockNum <= currentBlock; blockNum++) {
						try {
							const block = await web3.eth.getBlock(blockNum, true);
							if (!block || !block.transactions) continue;

							for (const tx of block.transactions) {
								if (typeof tx === 'string') continue; // Skip transaction hashes

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
									// Get transaction receipt for status
									let receipt = null;
									try {
										receipt = await web3.eth.getTransactionReceipt(tx.hash);
									} catch (e) {
										// Receipt might not be available yet
									}

									const transactionData: INodeExecutionData = {
										json: {
											address: normalizedAddress,
											transactionType: txFrom === addressLower ? 'sent' : 'received',
											transaction: {
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
											},
											receipt: receipt
												? {
														transactionHash: receipt.transactionHash,
														transactionIndex: receipt.transactionIndex.toString(),
														blockHash: receipt.blockHash,
														blockNumber: receipt.blockNumber.toString(),
														from: receipt.from,
														to: receipt.to,
														gasUsed: receipt.gasUsed.toString(),
														cumulativeGasUsed: receipt.cumulativeGasUsed.toString(),
														contractAddress: receipt.contractAddress,
														status: receipt.status ? 'success' : 'failed',
														logs: receipt.logs.map((log) => ({
															address: log.address,
															topics: log.topics,
															data: log.data,
															logIndex: log.logIndex?.toString(),
															transactionIndex: log.transactionIndex?.toString(),
															transactionHash: log.transactionHash,
															blockHash: log.blockHash,
															blockNumber: log.blockNumber?.toString(),
														})),
													}
												: null,
											timestamp: new Date().toISOString(),
										},
									};

									transactionsToEmit.push(transactionData);
								}
							}
						} catch (blockError: any) {
							// Log error but continue with next block
							console.error(`Error processing block ${blockNum}:`, blockError.message);
						}
					}

					// Emit all found transactions at once
					if (transactionsToEmit.length > 0) {
						this.emit([transactionsToEmit]);
					}

					lastProcessedBlock = currentBlock;
				}
			} catch (error: any) {
				console.error('Error in pollForNewTransactions:', error.message);
			}
		};

		// Start polling
		const intervalId = setInterval(pollForNewTransactions, pollInterval);

		// Initial poll
		pollForNewTransactions();

		// Cleanup function
		const closeFunction = async () => {
			clearInterval(intervalId);
		};

		return {
			closeFunction,
		};
	}
}

