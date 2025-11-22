import {
    ICredentialType,
    INodeProperties,
} from 'n8n-workflow';

export class RpcApi implements ICredentialType {
    name = 'rpcApi';
    displayName = 'RPC Provider';
    documentationUrl = 'https://ethereum.org/en/developers/docs/apis/json-rpc/';
    properties: INodeProperties[] = [
        {
            displayName: 'RPC URL',
            name: 'rpcUrl',
            type: 'string',
            default: '',
            placeholder: 'https://mainnet.infura.io/v3/<KEY>',
        }
    ];
}
