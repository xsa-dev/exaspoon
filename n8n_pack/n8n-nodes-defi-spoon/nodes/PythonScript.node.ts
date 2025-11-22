import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
} from 'n8n-workflow';

import { runPython } from '../helpers/runPython';

export class PythonScript implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Python Script (SpoonOS)',
		name: 'pythonScript',
		group: ['transform'],
		icon: 'fa:python',
		version: 1,
		description: 'Execute custom Python code',
		defaults: { name: 'Python Script' },
		inputs: ['main'],
		outputs: ['main'],
		credentials: [{ name: 'pythonEnv', required: false }],
		properties: [
			{
				displayName: 'Python Code',
				name: 'code',
				type: 'string',
				typeOptions: { rows: 12 },
				default:
`import json

# Input data from n8n:
# input_data = {{ JSON.stringify($json) }}

result = {"hello": "world"}
print(json.dumps(result))`,
				required: true,
			},
		],
	};

	async execute(this: IExecuteFunctions) {
		const items = this.getInputData();
		const results: INodeExecutionData[] = [];

		for (let i = 0; i < items.length; i++) {
			const code = this.getNodeParameter('code', i) as string;
			const creds = await this.getCredentials('pythonEnv');
			const pythonBin = (creds?.pythonPath as string) || 'python3';

			const inputJson = items[i].json;
			const output = await runPython(pythonBin, code, inputJson);

			results.push({ json: output });
		}

		return [results];
	}
}
