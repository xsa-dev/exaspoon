import type {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
} from 'n8n-workflow';

import Web3 from 'web3';

export class DefiGetTransaction implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'DeFi Get Transaction',
		name: 'defiGetTransaction',
		group: ['transform'],
		icon: 'fa:exchange-alt',
		version: 1,
		description: 'Get transaction details from Neo X (EVM) or any EVM-compatible chain',
		defaults: {
			name: 'DeFi Get Transaction',
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
				displayName: 'Operation',
				name: 'operation',
				type: 'options',
				noDataExpression: true,
				options: [
					{
						name: 'Get Transaction by Hash',
						value: 'getByHash',
						description: 'Get transaction details by transaction hash',
					},
					{
						name: 'Get Transaction Receipt',
						value: 'getReceipt',
						description: 'Get transaction receipt (includes logs and status)',
					},
					{
						name: 'Get Block Transactions',
						value: 'getBlockTransactions',
						description: 'Get all transactions from a block',
					},
					{
						name: 'Get Latest Block Transactions',
						value: 'getLatestBlock',
						description: 'Get all transactions from the latest block',
					},
				],
				default: 'getByHash',
				required: true,
			},
			{
				displayName: 'Transaction Hash',
				name: 'txHash',
				type: 'string',
				default: '',
				required: true,
				displayOptions: {
					show: {
						operation: ['getByHash', 'getReceipt'],
					},
				},
				description: 'The transaction hash (0x...)',
			},
			{
				displayName: 'Block Number',
				name: 'blockNumber',
				type: 'string',
				default: 'latest',
				required: true,
				displayOptions: {
					show: {
						operation: ['getBlockTransactions'],
					},
				},
				description: 'Block number (decimal) or "latest" for the latest block',
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
			const operation = this.getNodeParameter('operation', i) as string;

			try {
				let result: any;

				switch (operation) {
					case 'getByHash': {
						const txHash = this.getNodeParameter('txHash', i) as string;
						if (!txHash || !txHash.startsWith('0x')) {
							throw new Error('Invalid transaction hash. Must start with 0x');
						}
						const tx = await web3.eth.getTransaction(txHash);
						result = {
							operation: 'getByHash',
							transactionHash: txHash,
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
						};
						break;
					}

					case 'getReceipt': {
						const txHash = this.getNodeParameter('txHash', i) as string;
						if (!txHash || !txHash.startsWith('0x')) {
							throw new Error('Invalid transaction hash. Must start with 0x');
						}
						const receipt = await web3.eth.getTransactionReceipt(txHash);
						if (!receipt) {
							throw new Error('Transaction receipt not found. Transaction may be pending.');
						}
						result = {
							operation: 'getReceipt',
							transactionHash: txHash,
							receipt: {
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
							},
						};
						break;
					}

					case 'getBlockTransactions': {
						const blockNumber = this.getNodeParameter('blockNumber', i) as string;
						let blockNumberParam: string | number;
						
						if (blockNumber === 'latest') {
							blockNumberParam = 'latest';
						} else {
							blockNumberParam = parseInt(blockNumber, 10);
							if (isNaN(blockNumberParam)) {
								throw new Error('Invalid block number. Must be a number or "latest"');
							}
						}

						const block = await web3.eth.getBlock(blockNumberParam, true);
						if (!block) {
							throw new Error('Block not found');
						}

						const transactions = block.transactions.map((tx: any) => ({
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
						}));

						result = {
							operation: 'getBlockTransactions',
							blockNumber: block.number.toString(),
							blockHash: block.hash,
							timestamp: block.timestamp.toString(),
							transactionCount: transactions.length,
							transactions,
						};
						break;
					}

					case 'getLatestBlock': {
						const block = await web3.eth.getBlock('latest', true);
						if (!block) {
							throw new Error('Failed to get latest block');
						}

						const transactions = block.transactions.map((tx: any) => ({
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
						}));

						result = {
							operation: 'getLatestBlock',
							blockNumber: block.number.toString(),
							blockHash: block.hash,
							timestamp: block.timestamp.toString(),
							transactionCount: transactions.length,
							transactions,
						};
						break;
					}

					default:
						throw new Error(`Unknown operation: ${operation}`);
				}

				returnItems.push({
					json: {
						...items[i].json,
						...result,
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
