
# Roll no. and Name of teammates
1. 230001055   - Mohit Katariya
2. 230001053   - Raja vardhan
3. 230041018   - Lunavath Praveen



# Bitcoin Transaction Creation & Validation Assignment

This project demonstrates how to create and validate Bitcoin transactions using Legacy (P2PKH) and SegWit (P2SH-P2WPKH) address formats. The assignment involves interacting with Bitcoin Core in regtest mode, creating transactions between addresses, and analyzing the underlying scripts.

## Setup & Execution
1. Install Bitcoin Core
   Download and install Bitcoin Core from the official website. Ensure that you are installing a version that supports regtest mode.

2. **Configure Bitcoin Core:**  
   Edit your `bitcoin.conf` with:

   server=1
   [regtest]
   txindex=1
   rpcuser=your_username
   rpcpassword=your_password
   rpcport=18443
   paytxfee=0.0001
   fallbackfee=0.0002
   mintxfee=0.00001
   txconfirmtarget=6

3. **Start the Node:**
  Run in command prompt:

     bitcoind -regtest


# Part-1:-

Part 1 of project demonstrates creating and validating Bitcoin transactions on a regtest network using legacy (P2PKH) addresses.

## Overview

- **Legacy_A_to_B.py:**  
  - **Purpose:** Connects to Bitcoin Core, sets up a wallet, and generates three legacy addresses (A, B, and C).
  - **Workflow:**  
    1. Connects to the Bitcoin Core node using RPC.
    2. Creates or loads a wallet named "testwallet."
    3. Funds the wallet by mining 101 blocks (each block awards 50 BTC in regtest).
    4. Generates three legacy addresses: A, B, and C.
    5. Funds Address A 
    6. Provides an interactive menu to create a transaction from Address A to Address B, decode the transaction, and display the transaction     scripts (locking and unlocking)

- **Legacy_B_to_C.py:**  
  - **Purpose:** Uses the UTXO from the A-to-B transaction to create a new transaction from Address B to C.
  - **Workflow:**  
    1. Connects to the wallet.
    2. Retrieves a UTXO for Address B.
    3. Creates, signs, and broadcasts a transaction sending coins from B to C.
    4. Decodes the transaction and compares the unlocking script with the previous locking script.


 **Run the Scripts:**

  - Execute Legacy_A_to_B.py to set up the wallet, fund Address A, and create a transaction from A to B.
  - After exiting, run Legacy_B_to_C.py to create and analyze the transaction from B to C.


# Part-2:-

# P2SH-SegWit Address Transactions

## Overview

This project demonstrates a practical implementation of P2SH-SegWit address transactions using Bitcoin's RPC interface. The program connects to a local bitcoind node in regtest mode, creates (or loads) a wallet, and performs a series of transactions between three generated P2SH-SegWit addresses:
- **Address A'**
- **Address B'**
- **Address C'**

The workflow includes funding Address A', creating and signing raw transactions from A' to B' and from B' to C', and finally decoding and analyzing the transaction scripts to understand the locking (challenge) and unlocking (response) mechanisms.

## Features

- **RPC Connection:** Connects to bitcoind via RPC using the `AuthServiceProxy` from the `bitcoinrpc` library.
- **Wallet Management:** Creates or loads a wallet named `segwitwallet`.
- **Address Generation:** Generates three new P2SH-SegWit addresses.
- **Funding Transactions:** Funds Address A' by sending coins using the `sendtoaddress` command and confirms the transaction by mining blocks.
- **Raw Transaction Creation:** Creates raw transactions for sending coins between addresses, signs them, and broadcasts them.
- **Transaction Decoding:** Decodes transactions to extract and analyze the script details.
- **User Interaction:** Provides a simple CLI menu to view wallet balance, list UTXOs, send coins, interpret transactions, and view detailed SegWit transaction properties.

## Prerequisites

Before running the program, ensure you have the following installed:

- **Python 3.x**  
- **bitcoind:** A Bitcoin Core node running in regtest mode.
- **Python Bitcoin RPC library:** Install with:

    pip install python-bitcoinrpc



Thank you !!!!!!