import { ICredentialType, INodeProperties } from 'n8n-workflow';

export class PythonEnv implements ICredentialType {
	name = 'pythonEnv';
	displayName = 'Python Environment';
	properties: INodeProperties[] = [
		{
			displayName: 'Python Path',
			name: 'pythonPath',
			type: 'string',
			default: 'python3',
			description: 'Path to python executable',
		},
	];
}
