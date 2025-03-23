from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time
from decimal import Decimal

def connect_rpc():
    rpc_user = "Mohit_katariya_885"
    rpc_password = "Bitcoin12345core"
    rpc_ip = "127.0.0.1"
    rpc_port = 18443
    rpc_url = f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}"
    try:
        rpc_connection = AuthServiceProxy(rpc_url)
        rpc_connection.getblockchaininfo()
        print("Connected to bitcoind RPC.")
        return rpc_connection
    except Exception as e:
        print("Error connecting to bitcoind RPC:", e)
        exit(1)

def create_or_load_wallet(rpc_connection, wallet_name="testwallet"):
    try:
        wallets = rpc_connection.listwallets()
        if wallet_name in wallets:
            print(f"Wallet '{wallet_name}' already loaded.")
        else:
            rpc_connection.createwallet(wallet_name)
            print(f"Wallet '{wallet_name}' created and loaded.")
    except JSONRPCException as e:
        print("Error creating/loading wallet:", e)
    rpc_user = "Mohit_katariya_885"
    rpc_password = "Bitcoin12345core"
    rpc_ip = "127.0.0.1"
    rpc_port = 18443
    wallet_url = f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}/wallet/{wallet_name}"
    wallet_rpc = AuthServiceProxy(wallet_url)
    return wallet_rpc

def fund_wallet(wallet_rpc):
    mining_address = wallet_rpc.getnewaddress("", "legacy")
    print("Generating 101 blocks to fund the wallet...")
    block_hashes = wallet_rpc.generatetoaddress(101, mining_address)
    # In regtest the block reward is 50 BTC per block.
    reward = len(block_hashes) * Decimal("50")
    print("Blocks generated. Latest block hash:", block_hashes[-1])
    print("Approximate total block reward received: {} BTC".format(reward))
    time.sleep(1)

def generate_legacy_addresses(wallet_rpc):
    address_A = wallet_rpc.getnewaddress("", "legacy")
    address_B = wallet_rpc.getnewaddress("", "legacy")
    address_C = wallet_rpc.getnewaddress("", "legacy")
    print("Legacy addresses generated:")
    print("Address A:", address_A)
    print("Address B:", address_B)
    print("Address C:", address_C)
    return address_A, address_B, address_C

def fund_address(wallet_rpc, address, amount=1.0):
    try:
        txid = wallet_rpc.sendtoaddress(address, amount)
        print(f"Funding transaction sent to {address}. TXID: {txid}")
        mining_address = wallet_rpc.getnewaddress("", "legacy")
        block_hashes = wallet_rpc.generatetoaddress(1, mining_address)
        print("Block mined to confirm funding transaction. Block Hash:", block_hashes[0])
        time.sleep(1)
        return txid
    except JSONRPCException as e:
        print("Error funding address:", e)
        return None

def list_utxos(wallet_rpc):
    utxos = wallet_rpc.listunspent()
    if not utxos:
        print("No UTXOs available.")
    else:
        for i, utxo in enumerate(utxos, start=1):
            print(f"{i}. TXID: {utxo['txid']}, vout: {utxo['vout']}, Amount: {utxo['amount']}, Address: {utxo['address']}")
    return utxos

def create_and_broadcast_transaction(wallet_rpc, from_address, to_address, send_amount, fee=Decimal("0.001")):
    # Ensure send_amount is a Decimal
    if not isinstance(send_amount, Decimal):
        try:
            send_amount = Decimal(send_amount)
        except Exception as e:
            print("Error converting send_amount to Decimal:", e)
            return None, None

    # Get all available UTXOs (ignoring the from_address filter)
    utxos = wallet_rpc.listunspent(1, 9999999)
    if not utxos:
        print("No UTXOs available in the wallet.")
        return None, None

    selected_utxos = []
    total_selected = Decimal("0")
    for utxo in utxos:
        selected_utxos.append({"txid": utxo["txid"], "vout": utxo["vout"]})
        total_selected += Decimal(str(utxo["amount"]))
        if total_selected >= send_amount + fee:
            break

    if total_selected < send_amount + fee:
        print(f"Insufficient funds: Total selected is {total_selected} BTC, but required is {send_amount + fee} BTC.")
        return None, None

    # Calculate change output (if any)
    change = total_selected - send_amount - fee
    outputs = {to_address: float(send_amount)}
    if change > 0:
        change_address = wallet_rpc.getrawchangeaddress()
        outputs[change_address] = float(change)

    raw_tx = wallet_rpc.createrawtransaction(selected_utxos, outputs)
    print("Raw transaction created:", raw_tx)
    signed_tx = wallet_rpc.signrawtransactionwithwallet(raw_tx)
    if not signed_tx.get("complete", False):
        print("Transaction signing incomplete.")
        return None, None
    signed_hex = signed_tx["hex"]
    print("Signed transaction hex:", signed_hex)
    decoded_tx = wallet_rpc.decoderawtransaction(signed_hex)
    print("Decoded transaction:")
    print(decoded_tx)
    
    # The fee spent is the difference between total inputs and total outputs.
    total_outputs = Decimal("0")
    for vout in decoded_tx.get("vout", []):
        total_outputs += Decimal(str(vout.get("value", 0)))
    calculated_fee = total_selected - total_outputs

    print("Transaction fee spent: {} BTC".format(calculated_fee))
    
    txid = wallet_rpc.sendrawtransaction(signed_hex)
    print(f"Transaction broadcasted. TXID: {txid}")
    return txid, decoded_tx

def display_interpretation(decoded_tx, script_pubkey):
    print("\n--- Analysis ---")
    print("Locking script (challenge) for recipient address:")
    print(script_pubkey)
    script_sig = decoded_tx.get("vin", [{}])[0].get("scriptSig", {})
    print("\nUnlocking script (response) from spending transaction:")
    print(script_sig)
    print("\nInterpretation:")
    print("In a standard P2PKH transaction, the locking script requires a valid signature and matching public key hash.")
    print("The unlocking script provides these elements (signature and public key), thus proving ownership.")

def workflow_summary(fund_txid, txid_A_to_B, txid_B_to_C):
    print("\n--- Workflow Summary ---")
    print(f"Funding TXID for Address A: {fund_txid}")
    print(f"Transaction from A to B TXID: {txid_A_to_B}")
    print(f"Transaction from B to C TXID: {txid_B_to_C}")

def display_wallet_balance(wallet_rpc):
    try:
        balance = wallet_rpc.getbalance()
        print("\nCurrent wallet balance:", balance)
        return Decimal(str(balance))
    except Exception as e:
        print("Error retrieving wallet balance:", e)
        return None

def print_legacy_transaction_details(wallet_rpc, txid):
    try:
        tx_legacy = wallet_rpc.getrawtransaction(txid, True)
        print("\nLegacy (P2PKH) Transaction:")
        print(f"  Size: {tx_legacy.get('size', 'N/A')} bytes")
        print(f"  Virtual Size (vsize): {tx_legacy.get('vsize', 'N/A')} vbytes")
        print(f"  Weight: {tx_legacy.get('weight', 'N/A')}")
    except Exception as e:
        print("Error retrieving legacy transaction details:", e)

def main_menu(wallet_rpc, addresses, fund_txid):
    address_A, address_B, address_C = addresses
    txid_A_to_B = None
    txid_B_to_C = None
    while True:
        print("\nPlease choose an option:")
        print("0. View Wallet Balance")
        print("1. View Wallet UTXOs")
        print("2. Send coins (choose sender, recipient, and amount)")
        print("3. View Final Transaction Interpretation")
        print("4. View Workflow Summary")
        print("5. Exit")
        print("6. View Legacy (P2PKH) Transaction Details")
        choice = input("Enter choice (0-6): ").strip()
        if choice == "0":
            display_wallet_balance(wallet_rpc)
        elif choice == "1":
            print("\nCurrent UTXOs:")
            list_utxos(wallet_rpc)
        elif choice == "2":
            print("\nSelect sending transaction:")
            print("a. Transaction from Address A to Address B")
            print("b. Transaction from Address B to Address C")
            subchoice = input("Enter a or b: ").strip().lower()
            if subchoice == "a":
                amount_str = input(f"Enter amount to send from Address A ({address_A}) to Address B ({address_B}): ")
                try:
                    amount = Decimal(amount_str)
                except Exception as e:
                    print("Invalid amount:", e)
                    continue
                prev_balance = display_wallet_balance(wallet_rpc)
                txid, decoded_tx = create_and_broadcast_transaction(wallet_rpc, address_A, address_B, amount)
                if txid:
                    txid_A_to_B = txid
                    new_balance = display_wallet_balance(wallet_rpc)
                    fee_spent = (prev_balance - new_balance) - amount
                    print("\nTransaction Summary:")
                    print(f"Sent {amount} BTC from Address A to Address B")
                    print(f"Transaction fee spent: {fee_spent} BTC")
                    for vout in decoded_tx.get("vout", []):
                        spk = vout.get("scriptPubKey", {})
                        if spk.get("address") == address_B:
                            print("\nLocking script (ScriptPubKey) for Address B:")
                            print(spk)
                            break
            elif subchoice == "b":
                amount_str = input(f"Enter amount to send from Address B ({address_B}) to Address C ({address_C}): ")
                try:
                    amount = Decimal(amount_str)
                except Exception as e:
                    print("Invalid amount:", e)
                    continue
                prev_balance = display_wallet_balance(wallet_rpc)
                txid, decoded_tx = create_and_broadcast_transaction(wallet_rpc, address_B, address_C, amount)
                if txid:
                    txid_B_to_C = txid
                    new_balance = display_wallet_balance(wallet_rpc)
                    fee_spent = (prev_balance - new_balance) - amount
                    print("\nTransaction Summary:")
                    print(f"Sent {amount} BTC from Address B to Address C")
                    print(f"Transaction fee spent: {fee_spent} BTC")
                    for vin in decoded_tx.get("vin", []):
                        if "scriptSig" in vin:
                            print("\nUnlocking script (ScriptSig) from transaction:")
                            print(vin["scriptSig"])
                            break
            else:
                print("Invalid subchoice.")
        elif choice == "3":
            print("\nEnter the TXID of the transaction to interpret (or press Enter to use the last transaction from option 2):")
            tx_input = input().strip()
            if tx_input:
                decoded = wallet_rpc.decoderawtransaction(wallet_rpc.getrawtransaction(tx_input))
            else:
                if txid_B_to_C:
                    decoded = wallet_rpc.decoderawtransaction(wallet_rpc.getrawtransaction(txid_B_to_C))
                elif txid_A_to_B:
                    decoded = wallet_rpc.decoderawtransaction(wallet_rpc.getrawtransaction(txid_A_to_B))
                else:
                    print("No transaction available for interpretation.")
                    continue
            locking_script = {'asm': 'OP_DUP OP_HASH160 ... OP_EQUALVERIFY OP_CHECKSIG'}  # placeholder
            display_interpretation(decoded, locking_script)
        elif choice == "4":
            workflow_summary(fund_txid, txid_A_to_B, txid_B_to_C)
        elif choice == "5":
            print("Exited.")
            break
        elif choice == "6":
            tx_input = input("Enter TXID for the legacy transaction (or press Enter to use Address A to B transaction): ").strip()
            if not tx_input:
                if txid_A_to_B is None:
                    print("No default legacy transaction available. Please send a transaction first.")
                    continue
                else:
                    tx_input = txid_A_to_B
            print_legacy_transaction_details(wallet_rpc, tx_input)
        else:
            print("Invalid choice. Please try again.")

def main():
    rpc_connection = connect_rpc()
    wallet_rpc = create_or_load_wallet(rpc_connection, "testwallet")
    fund_wallet(wallet_rpc)
    addresses = generate_legacy_addresses(wallet_rpc)
    # Fund Address A (e.g., sending 1.0 BTC)
    fund_txid = fund_address(wallet_rpc, addresses[0], 1.0)
    main_menu(wallet_rpc, addresses, fund_txid)

if __name__ == '__main__':
    main()
