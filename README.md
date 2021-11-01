# EOSIO-blockchain-downloader

Project for the retrieval of transactions of a specific Smart Contract on the EOSIO blockchain. The information retrieval is done via EOSFLARE API (eosflare.io/api). 

The `main_download.py` takes as input the name of the smart contract, the position where to start the download and the offset. All the transactions/actions are saved in JSON format.
