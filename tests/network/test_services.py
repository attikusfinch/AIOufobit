import pytest

import aioufobit
from aioufobit.network.services import (
    NetworkAPI, set_service_timeout
)
from tests.utils import (
    raise_connection_error
)

MAIN_ADDRESS_USED1 = 'Bs9EsQi1EnR5gAca148MJiYGx7SyaYN7uA'
MAIN_ADDRESS_USED2 = '17SkEw2md5avVNyYgj6RiXuQKNwkXaxFyQ'
MAIN_ADDRESS_UNUSED = '1DvnoW4vsXA1H9KDgNiMqY7iNkzC187ve1'
TEST_ADDRESS_USED1 = 'n2eMqTT929pb1RDNuqEnxdaLau1rxy3efi'
TEST_ADDRESS_USED2 = 'mmvP3mTe53qxHdPqXEvdu8WdC7GfQ2vmx5'
TEST_ADDRESS_USED3 = 'mpnrLMH4m4e6dS8Go84P1r2hWwTiFTXmtW'
TEST_ADDRESS_UNUSED = 'mp1xDKvvZ4yd8h9mLC4P76syUirmxpXhuk'


def all_items_common(seq):
    initial_set = set(seq[0])
    intersection_lengths = [len(set(s) & initial_set) for s in seq]
    return all_items_equal(intersection_lengths)


def all_items_equal(seq):
    initial_item = seq[0]
    return all(item == initial_item for item in seq if item is not None)


def test_set_service_timeout():
    original = aioufobit.network.services.DEFAULT_TIMEOUT
    set_service_timeout(3)
    updated = aioufobit.network.services.DEFAULT_TIMEOUT

    assert original != updated
    assert updated == 3

    set_service_timeout(original)


class MockBackend(NetworkAPI):
    IGNORED_ERRORS = NetworkAPI.IGNORED_ERRORS
    GET_BALANCE_MAIN = [raise_connection_error]
    GET_TRANSACTIONS_MAIN = [raise_connection_error]
    GET_UNSPENT_MAIN = [raise_connection_error]
    GET_BALANCE_TEST = [raise_connection_error]
    GET_TRANSACTIONS_TEST = [raise_connection_error]
    GET_UNSPENT_TEST = [raise_connection_error]


class TestNetworkAPI:
    async def test_get_balance_main_equal(self):
        results = [call(MAIN_ADDRESS_USED2) for call in await NetworkAPI.GET_BALANCE_MAIN]
        assert all(result == results[0] for result in results)

    async def test_get_balance_main_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_balance(MAIN_ADDRESS_USED2)

    async def test_get_balance_test_equal(self):
        results = [call(TEST_ADDRESS_USED2) for call in await NetworkAPI.GET_BALANCE_TEST]
        assert all(result == results[0] for result in results)

    async def test_get_balance_test_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_balance_testnet(TEST_ADDRESS_USED2)

    async def test_get_transactions_main_equal(self):
        results = [call(MAIN_ADDRESS_USED1)[:100] for call in await NetworkAPI.GET_TRANSACTIONS_MAIN]
        assert all_items_common(results)

    async def test_get_transactions_main_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_transactions(MAIN_ADDRESS_USED1)

    async def test_get_transactions_test_equal(self):
        results = [call(TEST_ADDRESS_USED2)[:100] for call in await NetworkAPI.GET_TRANSACTIONS_TEST]
        assert all_items_common(results)

    async def test_get_transactions_test_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_transactions_testnet(TEST_ADDRESS_USED2)

    async def test_get_unspent_main_equal(self):
        results = [call(MAIN_ADDRESS_USED2) for call in await NetworkAPI.GET_UNSPENT_MAIN]
        assert all_items_equal(results)

    async def test_get_unspent_main_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_unspent(MAIN_ADDRESS_USED1)

    async def test_get_unspent_test_equal(self):
        results = [call(TEST_ADDRESS_USED3) for call in await NetworkAPI.GET_UNSPENT_TEST]
        assert all_items_equal(results)

    async def test_get_unspent_test_failure(self):
        with pytest.raises(ConnectionError):
            MockBackend.get_unspent_testnet(TEST_ADDRESS_USED2)