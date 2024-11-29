from web3 import Web3, AsyncWeb3
import requests, sys, time


from new_mints_scanner.scan_new_mints import start_scanning as eth_scanner
from config import *

eth_http_rpc, eth_wss_rpc = infura_node, None


# Etherem web3 client
eth_client = Web3(Web3.HTTPProvider(eth_http_rpc))
eth_async_client = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(eth_http_rpc))


"""Setting up Uniswap ethereum contract"""
        
# Get uniswap v2 abi
uniswap_v2_abi = requests.get(uniswap_v2_abi_link)

if uniswap_v2_abi.status_code == 200:
    uniswap_v2_abi = uniswap_v2_abi.json()['abi']
    print("Uniswap ABI fetched!")

# setting up contract
uniswap_v2_contract = eth_client.eth.contract(address=uniswap_v2_factory, abi=uniswap_v2_abi) 


def ethereum_tracker():
    print("Etherem Token Tracking Started!")

    # Scan new tokens
    eth_scanner(eth_client, uniswap_v2_contract)

ethereum_tracker()