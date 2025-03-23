from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal
import sys

# RPC connection parameters
RPC_USER = "Mohit_katariya_885"
RPC_PASSWORD = "Bitcoin12345core"
RPC_IP = "127.0.0.1"
RPC_PORT = 18443
WALLET_NAME = "testwallet"

def connect_wallet():
    """Connect to the Bitcoin Core wallet RPC."""
    wallet_url = f"http://{RPC_USER}:{RPC_PASSWORD}@{RPC_IP}:{RPC_PORT}/wallet/{WALLET_NAME}"
    try:
        wallet_rpc = AuthServiceProxy(wallet_url)
        # Test connection by getting wallet balance
        wallet_rpc.getbalance()
        print("Connected to wallet RPC.")
        return wallet_rpc
    except Exception as e:
        print("Error connecting to wallet RPC:", e)
        sys.exit(1)

def get_utxo_for_address(wallet_rpc, address):
    """
    Retrieve a UTXO for the given address.
    This UTXO should be from a previous transaction where Address B received coins from Address A.
    Note: We use 0 minimum confirmations to allow unconfirmed UTXOs.
    """
    try:
        # Using minConf=0 allows unconfirmed UTXOs to be returned.
        utxos = wallet_rpc.listunspent(0, 9999999, [address])
        if not utxos:
            print(f"No UTXOs found for address {address}.")
            sys.exit(1)
        # Use the first available UTXO
        return utxos[0]
    except Exception as e:
        print("Error retrieving UTXO for address", address, ":", e)
        sys.exit(1)

def create_tx_from_utxo(wallet_rpc, utxo, to_address, send_amount, fee=Decimal("0.0001")):
    """
    Create a raw transaction spending the UTXO (from Address B) to to_address (Address C).
    If there is change, it will be sent to a new change address.
    """
    send_amount = Decimal(send_amount)
    total_amount = Decimal(str(utxo["amount"]))
    
    if total_amount < send_amount + fee:
        print("UTXO does not have enough funds. Total available:", total_amount,
              "but required:", send_amount + fee)
        sys.exit(1)
    
    # Prepare inputs from the UTXO and outputs for the payment and change (if any)
    inputs = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
    outputs = {to_address: float(send_amount)}
    
    # Calculate change and assign a change address if needed.
    change = total_amount - send_amount - fee
    if change > 0:
        # Remove the empty string parameter to use the wallet default address type.
        change_address = wallet_rpc.getrawchangeaddress()
        outputs[change_address] = float(change)
    
    try:
        raw_tx = wallet_rpc.createrawtransaction(inputs, outputs)
        print("Raw transaction created:", raw_tx)
        return raw_tx
    except JSONRPCException as e:
        print("Error creating raw transaction:", e)
        sys.exit(1)

def sign_and_broadcast_tx(wallet_rpc, raw_tx):
    """
    Sign the raw transaction using the wallet's keys and broadcast it.
    """
    try:
        signed_tx = wallet_rpc.signrawtransactionwithwallet(raw_tx)
        if not signed_tx.get("complete", False):
            print("Transaction signing incomplete.")
            sys.exit(1)
        signed_hex = signed_tx["hex"]
        print("Signed transaction hex:", signed_hex)
        txid = wallet_rpc.sendrawtransaction(signed_hex)
        print("Transaction broadcasted. TXID:", txid)
        return txid, signed_hex
    except JSONRPCException as e:
        print("Error signing or broadcasting transaction:", e)
        sys.exit(1)

def decode_tx(wallet_rpc, tx_hex):
    """
    Decode the raw transaction.
    """
    try:
        decoded_tx = wallet_rpc.decoderawtransaction(tx_hex)
        return decoded_tx
    except JSONRPCException as e:
        print("Error decoding transaction:", e)
        sys.exit(1)

def get_locking_script(wallet_rpc, utxo):
    """
    Retrieve the locking script (ScriptPubKey) from the previous transaction that funded the UTXO.
    This is the challenge script from the A-to-B transaction.
    """
    try:
        prev_txid = utxo["txid"]
        vout = utxo["vout"]
        prev_tx = wallet_rpc.getrawtransaction(prev_txid, True)
        for output in prev_tx["vout"]:
            if output["n"] == vout:
                return output["scriptPubKey"]
        print("Locking script not found in previous transaction.")
        return None
    except Exception as e:
        print("Error retrieving locking script:", e)
        sys.exit(1)

def main():
    wallet_rpc = connect_wallet()

    # Prompt user for Address B and Address C
    address_B = input("Enter Address B (source UTXO address, funds from A-to-B): ").strip()
    address_C = input("Enter Address C (destination address): ").strip()
    send_amount_str = input("Enter amount to send from Address B to Address C: ").strip()
    try:
        send_amount = Decimal(send_amount_str)
    except Exception as e:
        print("Invalid send amount:", e)
        sys.exit(1)
    
    # Step 1: Get a UTXO that belongs to Address B (funded from previous transaction A-to-B)
    utxo = get_utxo_for_address(wallet_rpc, address_B)
    print("\nUsing the following UTXO for Address B:")
    print(utxo)
    
    # Step 2: Create a raw transaction from Address B to Address C using the selected UTXO
    raw_tx = create_tx_from_utxo(wallet_rpc, utxo, address_C, send_amount)
    
    # Step 3: Sign the transaction with the wallet (which uses Address B's private key) and broadcast it
    txid, signed_hex = sign_and_broadcast_tx(wallet_rpc, raw_tx)
    
    # Step 4: Decode the raw transaction to analyze its contents
    decoded_tx = decode_tx(wallet_rpc, signed_hex)
    print("\nDecoded Transaction:")
    print(decoded_tx)
    
    # Extract and display the unlocking script (ScriptSig) from the spending input.
    spending_input = decoded_tx.get("vin", [{}])[0]
    script_sig = spending_input.get("scriptSig", {})
    print("\nUnlocking Script (ScriptSig) from spending transaction:")
    print(script_sig)
    
    # Step 5: Retrieve the locking script (challenge) from the previous transaction (A-to-B)
    locking_script = get_locking_script(wallet_rpc, utxo)
    print("\nLocking Script (challenge) from previous transaction (A-to-B):")
    print(locking_script)
    
    # Step 6: Analysis and Validation
    print("\nAnalysis:")
    print("Compare the above locking script and unlocking script.")
    print("The unlocking script (provided in ScriptSig) should correctly satisfy the challenge script (locking script) from the funding transaction.")
    print("You can further validate the correctness using the Bitcoin Debugger or similar tools to step through script execution.")

if __name__ == '__main__':
    main()
