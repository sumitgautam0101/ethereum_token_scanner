from web3 import Web3
from datetime import datetime, timedelta, timezone
import time
import json
import time
from config import *




# Token Creator
def get_creator(w3_client: Web3.HTTPProvider, token_address):

    try:
        # Get the transaction receipt of the contract creation transaction
        tx_hash = w3_client.eth.get_transaction_receipt(token_address)['transactionHash']
        tx = w3_client.eth.get_transaction(tx_hash)
        return tx['from']
    except Exception as Er:
        print(f"Error while fetching developer wallet : {Er}")
        
# Token meta
def get_token_details(w3_client: Web3.HTTPProvider, token_address: str):

    try:

        token_contract = w3_client.eth.contract(address=token_address, abi=json.load(open("ABIs\\erc20_abi.json")))

        name = token_contract.functions.name().call()
        decimals = token_contract.functions.decimals().call()
        symbol = token_contract.functions.symbol().call()
        totalSupply = token_contract.functions.totalSupply().call()

        return name, decimals, symbol, totalSupply / 10 ** decimals  
    
    except Exception as Er:
        print(f"Error while fetching token details : {Er}")

# Get Token info and add in temp list
def extract_pair_info(w3_client: Web3.HTTPProvider, event):

    found_at = datetime.now(timezone.utc)

    # Extract the first(base) token address (topics[2])
    token0_address = Web3.to_checksum_address(str(event['topics'][1].hex())[24:])
    
    # Extract the second(quote) token address (topics[1])
    token1_address = Web3.to_checksum_address(str(event['topics'][2].hex())[24:])  # strip first 26 characters (0x + padding)

    if token0_address == Web3.to_checksum_address(weth_address):
        token0_address = token1_address
        token1_address = Web3.to_checksum_address(weth_address)

    
    # Extract the pair address from 'data' field (first 64 hex characters of 'data')
    pair_address = Web3.to_checksum_address(str(event['data'].hex())[24:64])  # extract 20-byte pair address

    # Extract Transaction hash
    txn_hash = str(event['transactionHash'].hex())

    # fetch dev wallet
    dev_wallet = get_creator(w3_client, txn_hash)
    token_meta = get_token_details(w3_client, token0_address)

    if dev_wallet is not None and token_meta is not None:


        new_mint = {
            "found_at" : found_at,
            "pair" : str(pair_address),
            "base_mint" : str(token0_address),
            "quote_mint" : str(token1_address),
            "name" : str(token_meta[0]),
            "decimals" : token_meta[1],  
            "symbol" : token_meta[2],  
            "totalSupply" : token_meta[3],  
            "dev_wallet" : str(dev_wallet)
        }
        print(f"New Mint TXN @ {found_at} : https://etherscan.io/tx/0x{txn_hash}")

        file_data = None
        with open("mints.json", "r") as fp:
            try:
                file_data = json.load(fp)
                
            except json.decoder.JSONDecodeError:
                file_data = []

            except Exception as Er:
                print("Error while opening file : ", Er)
                return
        
        with open("mints.json", "w") as fp:

            if file_data is not None:
        
                # Write the file
                file_data.append(new_mint)
                json.dump(file_data, fp)
    


def start_scanning(w3_client: Web3.HTTPProvider, uniswap_client):

 
    # Create a filter for PairCreated events from the latest block
    event_filter = w3_client.eth.filter({
        'fromBlock': 'latest',
        'address': uniswap_v2_factory_contract_address,
        'topics': [uniswap_v2_pair_event_filter]
    })
    while True:
        try:
            # Get new events
            events = w3_client.eth.get_filter_changes(event_filter.filter_id)
            
            if len(events) > 0:
                for event in events:
                    extract_pair_info(w3_client, event)
        except Exception as e:
            print(f"An error occurred in ethereum mint scanning thread : {e}")
            time.sleep(10)




