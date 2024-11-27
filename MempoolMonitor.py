from sys import path
from web3 import Web3
import json
import os
# Connect to Ethereum node
alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/1LUT5IfaNun6JMz9pgqQ4B6KbxO3kJ0R"
web3 = Web3(Web3.HTTPProvider(alchemy_url))

# Check connection
if web3.is_connected():
    print("Connected to Ethereum Mainnet")
else:
    print("Failed to connect to Ethereum Mainnet")

# Create a filter for pending transactions
pending_filter = web3.eth.filter('pending')

print("Monitoring pending transactions...")


# Load the ABI file
with open("router_abi.json", "r") as abi_file:
    router_abi = json.load(abi_file)

# DEX Router Address (Uniswap V2 example)
router_address = web3.to_checksum_address("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
router_contract = web3.eth.contract(address=router_address, abi=router_abi)

def decode_transaction(tx_hash):
    try:
        tx = web3.eth.get_transaction(tx_hash)
        method, params = router_contract.decode_function_input(tx['input'])
        return method, params
    except Exception as e:
        return None, None

def is_large_buy_order(tx):
    method, params = decode_transaction(tx['hash'])
    if method and method.fn_name == "swapExactETHForTokens":
        eth_value = web3.from_wei(tx['value'], 'ether')
        return eth_value > 10  # Example: large if > 10 ETH
    return False
# Monitor the mempool
print("Monitoring mempool for large buy orders...")
while True:
    try:
        pending_transactions = pending_filter.get_new_entries()
        for tx_hash in pending_transactions:
            tx = web3.eth.get_transaction(tx_hash)
            if is_large_buy_order(tx):
                print(f"Large Buy Order Detected: {tx}")
                print(f"Large Buy Order Detected: {tx['hash']}")
            print(f"Transaction Value: {web3.from_wei(tx['value'], 'ether')} ETH")
            print(f"Transaction Gas Price: {web3.from_wei(tx['gasPrice'], 'gwei')} Gwei")
            print(f"Transaction Gas: {tx['gas']}")
        # print(f"Transaction Input: {tx['input']}")
    except KeyboardInterrupt:
        print("Stopped monitoring mempool.")
        break
    except Exception as e:
        print(f"Error: {e}")

def execute_buy_order(tx):
    try:
        # Replace with actual token details
        token_address = "0xC36983d3D9d379dDFB306DFB919099cB6730e355"  # Replace with the token you want to buy
        wallet_address = "0x38FEF2386B96f70c95d21bc0A37F477F340f0A6A "  # Replace with your wallet address
        deadline = int(web3.eth.get_block('latest')['timestamp']) + 300  # 5 minutes from now

        # Set the amountOutMin to 0 for simplicity, or calculate it for slippage tolerance
        amount_out_min = 0  # Replace with a calculated value for safety

        # Path: ETH -> Token
        path = [
            web3.to_checksum_address("0xC02aaa39b223FE8D0A0E5C4F27eAD9083C756Cc2"),  # WETH
            web3.to_checksum_address(token_address),
        ]

        # Create transaction
        txn = {
            'to': router_address,
            'value': web3.to_wei(0.01, 'ether'),  # Example: Buy with 0.01 ETH
            'gas': 200000,  # Adjust gas limit based on the transaction
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(wallet_address),
            'data': router_contract.encodeABI(
                fn_name="swapExactETHForTokens",
                args=[amount_out_min, path, wallet_address, deadline]
            ),
        }

        # Sign and send the transaction
        private_key = os.getenv('PRIVATE_KEY')  # Ensure your private key is securely stored
        signed_txn = web3.eth.account.sign_transaction(txn, private_key)
        txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"Trade Executed: {txn_hash.hex()}")

    except Exception as e:
        print(f"Error executing buy order: {e}")

def calculate_amount_out_min(amount_in_wei, path, slippage=1):
    try:
        amounts_out = router_contract.functions.getAmountsOut(amount_in_wei, path).call()
        amount_out = amounts_out[-1]  # Get the final output token amount
        amount_out_min = int(amount_out * (1 - slippage / 100))  # Apply slippage tolerance
        return amount_out_min
    except Exception as e:
        print(f"Error calculating amountOutMin: {e}")
        return 0
amount_in_wei = web3.to_wei(0.01, 'ether')  # Example ETH input
amount_out_min = calculate_amount_out_min(amount_in_wei, os.path)
def wallet_address():
    return wallet_address

# Calculate deadline
deadline = int(web3.eth.get_block('latest')['timestamp']) + 300  # Set to 5 minutes from now

# Define the transaction dictionary
txn = {
    'to': router_address,  # Address of the DEX router (e.g., Uniswap, PancakeSwap)
    'value': amount_in_wei,  # The amount of ETH to swap (in Wei)
    'gas': 200000,  # Gas limit for the transaction
    'gasPrice': web3.eth.gas_price,  # Use the current gas price
    'nonce': web3.eth.get_transaction_count(wallet_address),  # Current nonce for the wallet
    'data': router_contract.encodeABI(
        fn_name="swapExactETHForTokens",
        args=[
            calculate_amount_out_min(amount_in_wei, path, slippage=1),  # Calculate minimum output with slippage
            path,  # Path of the swap (e.g., [WETH, Token])
            wallet_address,  # Address receiving the swapped tokens
            deadline  # Deadline for the transaction
        ]
    ),
}

if is_large_buy_order(tx):
    print("Large buy order detected! Executing trade...")
    execute_buy_order(tx)
