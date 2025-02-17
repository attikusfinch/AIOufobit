from .meta import Unspent

import aiohttp

from .api import RPCAPI

import logging
from decimal import Decimal, getcontext

from aioufobit.constants import UFO, UFOSHI
from aioufobit.network import currency_to_ufoshi
from aioufobit.network.meta import Unspent
from aioufobit.exceptions import UfoNodeException

class RPCHost(RPCAPI):
    def __init__(self, user: str, password: str, host: str, port: int, use_https: bool):
        self._url = f"http{'s' if use_https else ''}://{user}:{password}@{host}:{port}/"
        self._headers = {"content-type": "application/json"}
        self.http_verify = use_https

    async def rpc_call(self, method, args):
        """Send rpc call to UFO node

        Args:
            method (str): method for rpc-node
            args (list): [] list of args

        Raises:
            ConnectionError: If request failed
            UfoNodeException: If rpc call failed

        Returns:
            dict: rpc response
        """
        try:
            response = await self.make_request(method, args)
        except aiohttp.ClientConnectionError:
            raise ConnectionError
        if response.status not in (200, 500):
            raise UfoNodeException("RPC connection failure: " + str(response.status) + " " + await response.text())
        responseJSON = await response.json()
        if "error" in responseJSON and responseJSON["error"] is not None:
            raise UfoNodeException("Error in RPC call: " + str(responseJSON["error"]))
        return responseJSON["result"]

    async def getmempoolinfo(self):
        """Returns details on the active state of the TX memory pool."""
        return await self.rpc_call("getmempoolinfo", [])

    async def getmininginfo(self):
        """Returns a json object containing mining-related information."""
        return await self.rpc_call("getmininginfo", [])

    async def getnetworkinfo(self):
        """Returns an object containing various state info regarding P2P networking."""
        return await self.rpc_call("getnetworkinfo", [])

    async def getblockchaininfo(self):
        """Returns an object containing various state info regarding blockchain processing."""
        return await self.rpc_call("getblockchaininfo", [])

    async def getdifficulty(self):
        """Returns the proof-of-work difficulty as a multiple of the minimum difficulty."""
        return await self.rpc_call("getdifficulty", [])

    async def getbestblockhash(self):
        """Returns the hash of the best (tip) block in the longest blockchain."""
        return await self.rpc_call("getbestblockhash", [])

    async def getblockhash(self, height: int):
        """Returns hash of block in best-block-chain at height provided."""
        return await self.rpc_call("getblockhash", [height])

    async def getblockcount(self):
        """Returns the number of blocks in the longest blockchain."""
        return await self.rpc_call("getblockcount", [])

    async def getwalletinfo(self):
        """Returns an object containing various wallet state info."""
        return await self.rpc_call("getwalletinfo", [])
    
    async def getconnectioncount(self):
        """Returns the number of connections to other nodes."""
        return await self.rpc_call("getconnectioncount", [])

    async def sendmany(self, amounts: dict, minconf: int = 1, comment: str = ""):
        """Send multiple times. Amounts are double-precision floating point numbers."""
        return await self.rpc_call("sendmany", ["", amounts, minconf, comment])

    async def getnewaddress(self, label="", address_type="p2sh-segwit"):
        """
        Returns a new UFO address for receiving payments.
        If 'label' is specified, it is added to the address book 
        so payments received with the address will be associated with 'label'.

        Arguments:
        1. label           (string, optional, default="") The label name for the address to be linked to. It can also be set to the empty string "" to represent the default label. The label does not need to exist, it will be created if there is no label by the given name.
        2. address_type    (string, optional, default=set by -addresstype) The address type to use. Options are "legacy", "p2sh-segwit", and "bech32".

        Result:
        "address"    (string) The new ufo address
        """
        return await self.rpc_call("getnewaddress", [label, address_type])

    async def getaddressesbylabel(self, label=""):
        """
        Returns the list of addresses assigned the specified label.

        Arguments:
        1. label    (string, required) The label.

        Result:
        { (json object with addresses as keys)
        "address": { (json object with information about address)
            "purpose": "string" (string)  Purpose of address ("send" for sending address, "receive" for receiving address)
        },...
        }
        """
        return await self.rpc_call("getaddressesbylabel", [label])

    async def getaddressbalance(self, addresses: list):
        """
        Returns the balance for an address(es) (requires addressindex to be enabled).

        Arguments:
        1. addresses         (json array, required) The addresses
            [
            "address",    (string) The address
            ...
            ]

        Result:
        {
        "balance"  (string) The current balance in satoshis
        "received"  (string) The total number of satoshis received (including change)
        }
        """
        return await self.rpc_call("getaddressbalance", [addresses])
    
    async def get_balance(self, address):
        getcontext().prec = len(str(UFO))
        balance = Decimal(await self.rpc_call("getreceivedbyaddress", [address, 0]))
        return int(balance * UFO)

    async def get_balance_testnet(self, address):
        return await self.get_balance(address)

    async def get_transactions(self, address):
        response = await self.rpc_call("listreceivedbyaddress", [0, True, True, address])
        if len(response) > 0:
            response = response[0]["txids"]
        return response

    async def get_transactions_testnet(self, address):
        return await self.get_transactions(address)

    async def get_transaction_by_id(self, txid):
        return await self.rpc_call("getrawtransaction", [txid, False])

    async def get_transaction_by_id_testnet(self, txid):
        return await self.get_transaction_by_id(txid)

    async def get_unspents(self, addresses: list):
        unspents = []
        
        for address in addresses:
            unspents += (await self.get_unspent(address))

        return unspents

    async def get_unspent(self, address):
        response = await self.rpc_call("listunspent", [0, 9999999, [address]])
        return [
            Unspent(
                await currency_to_ufoshi(tx["amount"], "ufo"),
                tx["confirmations"],
                tx["scriptPubKey"],
                tx["txid"],
                tx["vout"],
                True if tx['address'][0] == 'U' else False
            )
            for tx in response
        ]

    async def get_unspent_testnet(self, address):
        return await self.rpc_call("get_unspent", [address])

    async def broadcast_tx(self, tx_hex):
        try:
            tx_hex = await self.rpc_call("sendrawtransaction", [tx_hex])
        except UfoNodeException as e:
            logging.warning(e)
            return None
        return tx_hex

    async def broadcast_tx_testnet(self, tx_hex):
        return await self.broadcast_tx(tx_hex)

class OMNIRPCHost(RPCHost):
    async def omni_createpayload_issuancefixed(self, ecosystem: int, type: int, previousid: int, category: str, subcategory: str, name: str, url: str, data: str, amount: str) -> str:
        """
        Arguments:
        1. ecosystem      (numeric, required) the ecosystem to create the tokens in (1 for main ecosystem, 2 for test ecosystem)
                        
        2. type           (numeric, required) the type of the tokens to create: (1 for indivisible tokens, 2 for divisible tokens)
                        
        3. previousid     (numeric, required) an identifier of a predecessor token (use 0 for new tokens)
                        
        4. category       (string, required) a category for the new tokens (can be "")
                        
        5. subcategory    (string, required) a subcategory for the new tokens  (can be "")
                        
        6. name           (string, required) the name of the new tokens to create
                        
        7. url            (string, required) a URL for further information about the new tokens (can be "")
                        
        8. data           (string, required) a description for the new tokens (can be "")
                        
        9. amount         (string, required) the number of tokens to create
        """
        return await self.rpc_call("omni_createpayload_issuancefixed", [ecosystem, type, previousid, category, subcategory, name, url, data, amount])

    async def omni_createpayload_issuancemanaged(self, ecosystem: int, type: int, previousid: int, category: str, subcategory: str, name: str, url: str, data: str) -> str:
        """
        omni_createpayload_issuancemanaged ecosystem type previousid "category" "subcategory" "name" "url" "data"

        Creates the payload for a new tokens issuance with manageable supply.

        Arguments:
        1. ecosystem      (numeric, required) the ecosystem to create the tokens in (1 for main ecosystem, 2 for test ecosystem)
                        
        2. type           (numeric, required) the type of the tokens to create: (1 for indivisible tokens, 2 for divisible tokens, 5 for non-fungible tokens)
                        
        3. previousid     (numeric, required) an identifier of a predecessor token (use 0 for new tokens)
                        
        4. category       (string, required) a category for the new tokens (can be "")
                        
        5. subcategory    (string, required) a subcategory for the new tokens  (can be "")
                        
        6. name           (string, required) the name of the new tokens to create
                        
        7. url            (string, required) a URL for further information about the new tokens (can be "")
                        
        8. data           (string, required) a description for the new tokens (can be "")
        """
        return await self.rpc_call("omni_createpayload_issuancemanaged", [ecosystem, type, previousid, category, subcategory, name, url, data])

    async def omni_getbalance(self, address: str, propertyid: int):
        """
        Returns the token balance for a given address and property.

        Arguments:
        1. address       (string, required) the address
                        
        2. propertyid    (numeric, required) the property identifier
        """
        return await self.rpc_call("omni_getbalance", [address, propertyid])

    async def omni_gettransaction(self, txid: str):
        return await self.rpc_call("omni_gettransaction", [txid])
    
    async def omni_getinfo(self):
        return await self.rpc_call("omni_getinfo", [])
    
    async def omni_send(self, from_address: str, to_address: str, propertyid: int, amount: str) -> str:
        """
        Create and broadcast a simple send transaction.

        Arguments:
        1. fromaddress        (string, required) the address to send from
                            
        2. toaddress          (string, required) the address of the receiver
                            
        3. propertyid         (numeric, required) the identifier of the tokens to send
                            
        4. amount             (string, required) the amount to send
        """
        return await self.rpc_call("omni_send", [from_address, to_address, propertyid, amount])
    
    async def omni_sendgrant(self, from_address: str, to_address: str, propertyid: int, amount: str):
        """
        Issue or grant new units of managed tokens.

        Arguments:
        1. from_address    (string, required) the address to send from
                        
        2. to_address      (string, required) the receiver of the tokens (sender by default, can be "")
                        
        3. propertyid     (numeric, required) the identifier of the tokens to grant
                        
        4. amount         (string, required) the amount of tokens to create                        
        """
        return await self.rpc_call("omni_sendgrant", [from_address, to_address, propertyid, str(amount)])

    async def create_nft(self, ecosystem: int, category: str, subcategory: str, name: str, url: str, data: str) -> str:
        """
        omni_createpayload_issuancemanaged ecosystem type previousid "category" "subcategory" "name" "url" "data"

        Creates the payload for a new tokens issuance with manageable supply.

        Arguments:
        1. ecosystem      (numeric, required) the ecosystem to create the tokens in (1 for main ecosystem, 2 for test ecosystem)

        2. category       (string, required) a category for the new tokens (can be "")
                        
        3. subcategory    (string, required) a subcategory for the new tokens  (can be "")
                        
        4. name           (string, required) the name of the new tokens to create
                        
        5. url            (string, required) a URL for further information about the new tokens (can be "")
                        
        6. data           (string, required) a description for the new tokens (can be "")
        """
        return await self.omni_createpayload_issuancemanaged(ecosystem, 5, 0, category, subcategory, name, url, data)

    async def create_token(self, ecosystem: int, type: int, category: str, subcategory: str, name: str, url: str, data: str, fixed: bool=True, amount: str="") -> str:
        """
        ecosystem: 1-main, 2-test
        type: 1-divisible, 2-non divisible
        fixed: (bool) -> tokens can be created or not
        """
        if fixed:
            return await self.omni_createpayload_issuancefixed(ecosystem, type, 0, category, subcategory, name, url, data, amount)
        
        return await self.omni_createpayload_issuancemanaged(ecosystem, type, 0, category, subcategory, name, url, data)
    
    async def print_token(self, from_address: str, to_address: str, propertyid: int, amount: str):
        """
        Issue or grant new units of managed tokens.

        Arguments:
        1. from_address    (string, required) the address to send from
                        
        2. to_address      (string, required) the receiver of the tokens (sender by default, can be "")
                        
        3. propertyid     (numeric, required) the identifier of the tokens to grant
                        
        4. amount         (string, required) the amount of tokens to create                        
        """
        return await self.omni_sendgrant(from_address, to_address, propertyid, amount)
    
    async def omni_sendrawtx(self, fromaddress, rawtransaction):
        return await self.rpc_call("omni_sendrawtx", [fromaddress, rawtransaction])