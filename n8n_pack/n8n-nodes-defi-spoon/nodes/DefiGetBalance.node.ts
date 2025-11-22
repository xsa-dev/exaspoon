import type {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
} from 'n8n-workflow';

import Web3 from 'web3';

export class DefiGetBalance implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'DeFi Get Balance',
		name: 'defiGetBalance',
		group: ['transform'],
		icon: 'fa:sync',
		version: 1,
		description: 'Get native token balance',
		defaults: {
			name: 'DeFi Get Balance',
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
			},
			{
				displayName: 'Token Address (optional)',
				name: 'tokenAddress',
				type: 'string',
				default: '',
				description: 'Leave empty for native balance',
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
			const address = this.getNodeParameter('address', i) as string;
			const tokenAddress = this.getNodeParameter('tokenAddress', i) as string;

			let balance: string;

			// --- NATIVE TOKEN ---
			if (!tokenAddress) {
				const raw = await web3.eth.getBalance(address);
				balance = raw.toString();
			}

			// --- ERC20 TOKEN ---
			else {
				// Minimal ERC20 ABI
				const erc20Abi = [
					{
						constant: true,
						inputs: [{ name: '_owner', type: 'address' }],
						name: 'balanceOf',
						outputs: [{ name: 'balance', type: 'uint256' }],
						type: 'function',
					},
				];

				// create contract instance
				const token = new web3.eth.Contract(erc20Abi as any, tokenAddress);

				// call balanceOf(address)
				const rawBalance = await token.methods.balanceOf(address).call();

				// normalize to string
				balance = (rawBalance as any).toString();
			}

			returnItems.push({
				json: {
					address,
					tokenAddress: tokenAddress || 'native',
					balance,
				},
			});
		}

		return [returnItems];
	}
}
