import re
from functools import wraps

import aiohttp
from .api import API

from .meta import Unspent

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
