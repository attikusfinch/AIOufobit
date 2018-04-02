import requests

from ufobit.network import currency_to_satoshi
from ufobit.network.meta import Unspent

DEFAULT_TIMEOUT = 10


def set_service_timeout(seconds):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = seconds


class CryptoidAPI:
    MAIN_ENDPOINT = 'https://chainz.cryptoid.info/{coin}/api.dws'
    KEY = '52700acdf523'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_ENDPOINT, params={'q': 'getbalance', 'a': address, 'key': cls.KEY})
        r.raise_for_status()
        return r.json()

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ENDPOINT, params={'q': 'lasttxs', 'a': address, 'key': cls.KEY})
        r.raise_for_status()
        return [tx['hash'] for tx in r.json()]

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_ENDPOINT, params={'q': 'unspent', 'active': address, 'key': cls.KEY})
        r.raise_for_status()
        print(r.json())
        return [
            Unspent(tx['value'],
                    tx['confirmations'],
                    tx['script'],
                    tx['tx_hash'],
                    tx['tx_ouput_n'])  # sic! typo in api itself
            for tx in r.json()['unspent_outputs']
        ][::-1]


class UFO(CryptoidAPI):
    MAIN_ENDPOINT = 'https://chainz.cryptoid.info/ufo/api.dws'


class InsightAPI:
    MAIN_ENDPOINT = ''
    MAIN_ADDRESS_API = ''
    MAIN_BALANCE_API = ''
    MAIN_UNSPENT_API = ''
    MAIN_TX_PUSH_API = ''
    TX_PUSH_PARAM = ''

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['transactions']

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return [
            Unspent(currency_to_satoshi(tx['amount'], 'btc'),
                    tx['confirmations'],
                    tx['scriptPubKey'],
                    tx['txid'],
                    tx['vout'])
            for tx in r.json()
        ]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class BitpayAPI(InsightAPI):
    MAIN_ENDPOINT = 'https://insight.bitpay.com/api/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'addr/'
    MAIN_BALANCE_API = MAIN_ADDRESS_API + '{}/balance'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '{}/utxo'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'tx/send'
    TEST_ENDPOINT = 'https://test-insight.bitpay.com/api/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'addr/'
    TEST_BALANCE_API = TEST_ADDRESS_API + '{}/balance'
    TEST_UNSPENT_API = TEST_ADDRESS_API + '{}/utxo'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'tx/send'
    TX_PUSH_PARAM = 'rawtx'

    @classmethod
    def get_balance_testnet(cls, address):
        r = requests.get(cls.TEST_BALANCE_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_transactions_testnet(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['transactions']

    @classmethod
    def get_unspent_testnet(cls, address):
        r = requests.get(cls.TEST_UNSPENT_API.format(address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return [
            Unspent(currency_to_satoshi(tx['amount'], 'btc'),
                    tx['confirmations'],
                    tx['scriptPubKey'],
                    tx['txid'],
                    tx['vout'])
            for tx in r.json()
        ]

    @classmethod
    def broadcast_tx_testnet(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TEST_TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class BlockchainAPI:
    ENDPOINT = 'https://blockchain.info/'
    ADDRESS_API = ENDPOINT + 'address/{}?format=json'
    UNSPENT_API = ENDPOINT + 'unspent?active='
    TX_PUSH_API = ENDPOINT + 'pushtx'
    TX_PUSH_PARAM = 'tx'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.ADDRESS_API.format(address) + '&limit=0', timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['final_balance']

    @classmethod
    def get_transactions(cls, address):
        endpoint = cls.ADDRESS_API

        transactions = []
        offset = 0
        payload = {'offset': str(offset)}
        txs_per_page = 50

        response = requests.get(endpoint.format(address), timeout=DEFAULT_TIMEOUT).json()
        total_txs = response['n_tx']

        while total_txs > 0:
            transactions.extend(tx['hash'] for tx in response['txs'])

            total_txs -= txs_per_page
            offset += txs_per_page
            payload['offset'] = str(offset)
            response = requests.get(endpoint.format(address),
                                    params=payload,
                                    timeout=DEFAULT_TIMEOUT).json()

        return transactions

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.UNSPENT_API + address, timeout=DEFAULT_TIMEOUT)

        if r.status_code == 500:
            return []
        elif r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        return [
            Unspent(tx['value'],
                    tx['confirmations'],
                    tx['script'],
                    tx['tx_hash_big_endian'],
                    tx['tx_output_n'])
            for tx in r.json()['unspent_outputs']
        ][::-1]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TX_PUSH_API, data={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class SmartbitAPI:
    MAIN_ENDPOINT = 'https://api.smartbit.com.au/v1/blockchain/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'address/'
    MAIN_UNSPENT_API = MAIN_ADDRESS_API + '{}/unspent'
    MAIN_TX_PUSH_API = MAIN_ENDPOINT + 'pushtx'
    TEST_ENDPOINT = 'https://testnet-api.smartbit.com.au/v1/blockchain/'
    TEST_ADDRESS_API = TEST_ENDPOINT + 'address/'
    TEST_UNSPENT_API = TEST_ADDRESS_API + '{}/unspent'
    TEST_TX_PUSH_API = TEST_ENDPOINT + 'pushtx'
    TX_PUSH_PARAM = 'hex'

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address + '?limit=1', timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['address']['total']['balance_int']

    @classmethod
    def get_balance_testnet(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address + '?limit=1', timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['address']['total']['balance_int']

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        data = r.json()['address']

        transactions = []

        if 'transactions' in data:
            transactions.extend(t['hash'] for t in data['transactions'])

        return transactions

    @classmethod
    def get_transactions_testnet(cls, address):
        r = requests.get(cls.TEST_ADDRESS_API + address + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError

        data = r.json()['address']

        transactions = []

        if 'transactions' in data:
            transactions.extend(t['hash'] for t in data['transactions'])

        return transactions

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(address) + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return [
            Unspent(currency_to_satoshi(tx['value'], 'btc'),
                    tx['confirmations'],
                    tx['script_pub_key']['hex'],
                    tx['txid'],
                    tx['n'])
            for tx in r.json()['unspent']
        ]

    @classmethod
    def get_unspent_testnet(cls, address):
        r = requests.get(cls.TEST_UNSPENT_API.format(address) + '?limit=1000', timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return [
            Unspent(currency_to_satoshi(tx['value'], 'btc'),
                    tx['confirmations'],
                    tx['script_pub_key']['hex'],
                    tx['txid'],
                    tx['n'])
            for tx in r.json()['unspent']
        ]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, json={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False

    @classmethod
    def broadcast_tx_testnet(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.TEST_TX_PUSH_API, json={cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


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
