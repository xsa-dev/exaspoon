import Web3 from 'web3';

export function createWeb3Client(rpcUrl: string) {
    return new Web3(rpcUrl);
}
