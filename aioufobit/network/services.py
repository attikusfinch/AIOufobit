import aiohttp
from .api import API

from .meta import Unspent

from .rpc import RPCHost

DEFAULT_TIMEOUT = 10

class NoAPIKey(Exception):
    pass

def set_service_timeout(seconds):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = seconds


class UFO(API):
    MAIN_ENDPOINT = 'https://explorer.ufobject.com/api'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    @classmethod
    async def broadcast_tx(self, tx_hex):
        response = await self.make_request(
            url=self.MAIN_ENDPOINT + '/tx/send',
            method="post",
            headers=self.headers,
            data={'rawtx': tx_hex},
        )
        if response.status >= 400:
            raise Exception(f"Error with status code: {response.status}")
        
        if (await response.text()) == '0':
            return False
        
        return (await response.json())['txid']

    @classmethod
    async def get_tx(self, txid):
        response = await self.make_request(
            url=self.MAIN_ENDPOINT + f'/tx/{txid}')
        if response.status >= 400:
            raise Exception(f"Error with status code: {response.status}")
        if (await response.text()) == '0':
            return False
        return await response.json()

    @classmethod
    async def get_unspent(self, address):
        response = await self.make_request(self.MAIN_ENDPOINT + f'/addr/{address}/utxo')
        if response.status >= 400:
            raise Exception(f"Error with status code: {response.status}")
        return [
                   Unspent(int(tx['satoshis']),
                           tx['confirmations'],
                           tx['scriptPubKey'],
                           tx['txid'],
                           tx['vout'],
                           True if tx['address'][0] == 'U' else False)  # sic! typo in api itself
                   for tx in (await response.json())
               ][::-1]

    @classmethod
    async def get_balance(self, address):
        response = await self.make_request(self.MAIN_ENDPOINT + f'/addr/{address}/balance')
        if response.status >= 400:
            raise Exception(f"Error with status code: {response.status}")
        return await response.json()

    @classmethod
    async def get_transactions(self, address):
        response = await self.make_request(self.MAIN_ENDPOINT + f'addr/{address}')
        if response.status >= 400:
            raise Exception(f"Error with status code: {response.status}")
        return [tx['txid'] for tx in (await response.json())['txs']]


class NetworkAPI:
    IGNORED_ERRORS = (ConnectionError,
                      aiohttp.ClientConnectorError,
                      aiohttp.ServerTimeoutError)

    GET_BALANCE_MAIN = [UFO.get_balance]
    GET_TRANSACTIONS_MAIN = [UFO.get_transactions]
    GET_UNSPENT_MAIN = [UFO.get_unspent]
    BROADCAST_TX_MAIN = [UFO.broadcast_tx]
    GET_TX_MAIN = [UFO.get_tx]

    @classmethod
    async def get_tx(self, txid):
        for api_call in self.GET_TX_MAIN:
            try:
                return await api_call(txid)
            except self.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    async def get_balance(self, address):
        """Gets the balance of an address in satoshi.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``int``
        """

        for api_call in self.GET_BALANCE_MAIN:
            try:
                return await api_call(address)
            except self.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    async def get_transactions(self, address):
        """Gets the ID of all transactions related to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of ``str``
        """

        for api_call in self.GET_TRANSACTIONS_MAIN:
            try:
                return await api_call(address)
            except self.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    async def get_unspent(self, address):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """

        for api_call in self.GET_UNSPENT_MAIN:
            try:
                return await api_call(address)
            except self.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    async def broadcast_tx(self, tx_hex):  # pragma: no cover
        """Broadcasts a transaction to the blockchain.

        :param tx_hex: A signed transaction in hex form.
        :type tx_hex: ``str``
        :raises ConnectionError: If all API services fail.
        """
        success = None

        for api_call in self.BROADCAST_TX_MAIN:
            try:
                call = await api_call(tx_hex)
                if not call:
                    continue
                return call
            except self.IGNORED_ERRORS:
                pass

        if success is False:
            raise ConnectionError('Transaction broadcast failed, or '
                                  'Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def connect_to_node(self, user, password, host='localhost', port=8332, use_https=False, testnet=False, path=""):
        """Connect to a remote Bitcoin node instead of using web APIs.
        Allows to connect to a testnet and mainnet Bitcoin node simultaneously.
        :param user: The RPC user to a Bitcoin node
        :type user: ``str``
        :param password: The RPC password to a Bitcoin node
        :type password: ``str``
        :param host: The host to a Bitcoin node
        :type host: ``str``
        :param port: The port to a Bitcoin node
        :type port: ``int``
        :param use_https: Connect to the Bitcoin node via HTTPS. Either a
            boolean, in which case it controls whether we connect to the node
            via HTTP or HTTPS, or a string, in which case we connect via HTTPS
            and it must be a path to the CA bundle to use. Defaults to False.
        :type use_https: ``bool`` or ``string``
        :param testnet: Defines if the node should be used for testnet
        :type testnet: ``bool``
        :returns: The node exposing its RPCs for direct interaction.
        :rtype: ``RPCHost``
        """
        node = RPCHost(user=user, password=password, host=host, port=port, use_https=use_https, path=path)

        # Inject remote node into NetworkAPI
        if testnet is False:
            self.GET_BALANCE_MAIN = [node.get_balance]
            self.GET_TRANSACTIONS_MAIN = [node.get_transactions]
            self.GET_TRANSACTION_BY_ID_MAIN = [node.get_transaction_by_id]
            self.GET_UNSPENT_MAIN = [node.get_unspent]
            self.BROADCAST_TX_MAIN = [node.broadcast_tx]
        else:
            self.GET_BALANCE_TEST = [node.get_balance_testnet]
            self.GET_TRANSACTIONS_TEST = [node.get_transactions_testnet]
            self.GET_TRANSACTION_BY_ID_TEST = [node.get_transaction_by_id_testnet]
            self.GET_UNSPENT_TEST = [node.get_unspent_testnet]
            self.BROADCAST_TX_TEST = [node.broadcast_tx_testnet]

        return node