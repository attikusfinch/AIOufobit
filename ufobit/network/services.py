import re
from functools import wraps

import requests

from ufobit.network import currency_to_ufoshi
from ufobit.network.meta import Unspent

DEFAULT_TIMEOUT = 10
config = {'api_key': None}


class NoAPIKey(Exception):
    pass


def requires_key(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not config['api_key']:
            raise NoAPIKey('Set ufobit.config["api_key"] to your CryptoID API key.')
        return f(*args, **kwargs)
    return decorator


def set_service_timeout(seconds):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = seconds


class CryptoidAPI:
    MAIN_ENDPOINT = 'https://chainz.cryptoid.info/{coin}/api.dws'

    @classmethod
    @requires_key
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_ENDPOINT, params={'q': 'getbalance', 'a': address, 'key': config['api_key']})
        r.raise_for_status()
        return r.json()

    @classmethod
    @requires_key
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ENDPOINT, params={'q': 'multiaddr', 'active': address, 'key': config['api_key']})
        r.raise_for_status()
        return [tx['hash'] for tx in r.json()['txs']]

    @classmethod
    @requires_key
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_ENDPOINT, params={'q': 'unspent', 'active': address, 'key': config['api_key']})
        r.raise_for_status()
        return [
            Unspent(int(tx['value']),
                    tx['confirmations'],
                    tx['script'],
                    tx['tx_hash'],
                    tx['tx_ouput_n'])  # sic! typo in api itself
            for tx in r.json()['unspent_outputs']
        ][::-1]

    @classmethod
    def broadcast_tx(cls, tx_hex):
        raise NotImplementedError('Implement this method in the child class.')

    @classmethod
    @requires_key
    def get_tx(cls, txid):
        r = requests.get(cls.MAIN_ENDPOINT, params={'q': 'txinfo', 't': txid, 'key': config['api_key']})
        r.raise_for_status()
        return r.json()


class UFO(CryptoidAPI):
    MAIN_ENDPOINT = 'https://chainz.cryptoid.info/ufo/api.dws'
    MAIN_TX_PUSH_API = 'https://wallet.ufocoin.net/proxyAjax.php'
    PUSHTX_KEY = '32098462904584238923572'

    @classmethod
    def broadcast_tx(cls, tx_hex):
        r = requests.post(
            cls.MAIN_TX_PUSH_API,
            params={'module': 'sendrawtransaction', 'key': cls.PUSHTX_KEY},
            data={'rawtx': tx_hex}
        )
        r.raise_for_status()
        if r.text == '0':
            return False
        return re.search(r'[0-9a-f]{64}', r.text).group(0)


class NetworkAPI:
    IGNORED_ERRORS = (ConnectionError,
                      requests.exceptions.ConnectionError,
                      requests.exceptions.Timeout,
                      requests.exceptions.ReadTimeout)

    GET_BALANCE_MAIN = [UFO.get_balance]
    GET_TRANSACTIONS_MAIN = [UFO.get_transactions]
    GET_UNSPENT_MAIN = [UFO.get_unspent]
    BROADCAST_TX_MAIN = [UFO.broadcast_tx]

    @classmethod
    def get_balance(cls, address):
        """Gets the balance of an address in satoshi.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``int``
        """

        for api_call in cls.GET_BALANCE_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_transactions(cls, address):
        """Gets the ID of all transactions related to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of ``str``
        """

        for api_call in cls.GET_TRANSACTIONS_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_unspent(cls, address):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """

        for api_call in cls.GET_UNSPENT_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        """Broadcasts a transaction to the blockchain.

        :param tx_hex: A signed transaction in hex form.
        :type tx_hex: ``str``
        :raises ConnectionError: If all API services fail.
        """
        success = None

        for api_call in cls.BROADCAST_TX_MAIN:
            try:
                success = api_call(tx_hex)
                if not success:
                    continue
                return
            except cls.IGNORED_ERRORS:
                pass

        if success is False:
            raise ConnectionError('Transaction broadcast failed, or '
                                  'Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')
