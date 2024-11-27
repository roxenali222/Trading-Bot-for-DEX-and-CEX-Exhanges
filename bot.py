from web3 import Web3
import json
import os

# Connect to Alchemy Ethereum node
alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/1LUT5IfaNun6JMz9pgqQ4B6KbxO3kJ0R"
web3 = Web3(Web3.HTTPProvider(alchemy_url))

# Check if connected
if web3.is_connected():
    print("Connected to Ethereum network")

    # Get the latest block number
    latest_block = web3.eth.block_number
    print(f"Latest Block: {latest_block}")

    # Get details of the latest block
    block_details = web3.eth.get_block(latest_block)
    print(block_details)
else:
    print("Failed to connect to the network")

# Example address to check balance
address = "0xC36983d3D9d379dDFB306DFB919099cB6730e355"
balance = web3.eth.get_balance(address)
eth_balance = web3.from_wei(balance, 'ether')
print(f"Balance: {eth_balance} ETH")

# Send Transaction
# Store private key securely in an environment variable
private_key = os.getenv('PRIVATE_KEY')  # Export PRIVATE_KEY to your environment
if not private_key:
    print("Error: Private key not found in environment variables")
    exit()

sender_address = "0x38FEF2386B96f70c95d21bc0A37F477F340f0A6A"
receiver_address = "0x38FEF2386B96f70c95d21bc0A37F477F340f0A6A"  # Replace with a valid receiver address

# Create transaction
txn = {
    'to': receiver_address,
    'value': web3.to_wei(0.01, 'ether'),  # Amount in ETH
    'gas': 21000,
    'gasPrice': web3.eth.gas_price,  # Use dynamic gas price
    'nonce': web3.eth.get_transaction_count(sender_address),
}

# Sign transaction
signed_txn = web3.eth.account.sign_transaction(txn, private_key)

# Send transaction
txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"Transaction sent! Hash: {txn_hash.hex()}")

# Interact with Smart Contract
# Convert contract address to checksum format
contract_address = web3.to_checksum_address("0x791a5c2261823dbf69b27b63e851b7745532cfa2")

# Load ABI from a file
try:
    with open("contract_abi.json", "r") as abi_file:
        contract_abi = json.load(abi_file)
except FileNotFoundError:
    print("Error: contract_abi.json file not found")
    exit()

# Create a contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Example: Call the `balanceOf` function to get the balance of the sender
try:
    result = contract.functions.balanceOf(sender_address).call()
    print(f"Sender's token balance: {result}")
except Exception as e:
    print(f"Error calling balanceOf: {e}")

# Example: Call the `totalSupply` function to get the total supply of tokens
try:
    total_supply = contract.functions.totalSupply().call()
    print(f"Total supply of tokens: {total_supply}")
except Exception as e:
    print(f"Error calling totalSupply: {e}")

