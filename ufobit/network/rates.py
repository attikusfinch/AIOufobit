from collections import OrderedDict
from decimal import ROUND_DOWN
from functools import wraps
from time import time

import requests

from ufobit.utils import Decimal

DEFAULT_CACHE_TIME = 60

# Constant for use in deriving exchange
# rates when given in terms of 1 BTC.
ONE = Decimal(1)

SATOSHI = 1
BTC = 10 ** 8

SUPPORTED_CURRENCIES = OrderedDict([
    ('ufoshi', 'Ufoshi'),
    ('ufo', 'UFO'),
    ('satoshi', 'Satoshi'),
    ('btc', 'Bitcoin'),
    ('usd', 'United States Dollar'),
    ('rub', 'Russian Ruble'),
])

# https://en.wikipedia.org/wiki/ISO_4217
CURRENCY_PRECISION = {
    'ufoshi': 0,
    'ufo': 8,
    'satoshi': 0,
    'btc': 8,
    'usd': 2,
    'rub': 2,
}


def set_rate_cache_time(seconds):
    global DEFAULT_CACHE_TIME
    DEFAULT_CACHE_TIME = seconds


def ufoshi_to_ufoshi():
    return SATOSHI


def ufo_to_ufoshi():
    return BTC


class RatesAPI:
    """Each method converts exactly 1 unit of the currency to the equivalent
    number of ufoshi.
    """

    MAIN_ENDPOINT = 'https://api.coinmarketcap.com/v1/ticker/uniform-fiscal-object/'

    @classmethod
    def currency_to_ufoshi(cls, currency):
        r = requests.get(cls.MAIN_ENDPOINT, params={'convert': currency})
        rate = r.json()[0]['price_' + currency.lower()]
        return int(ONE / Decimal(rate) * BTC)

    @classmethod
    def usd_to_ufoshi(cls):
        return cls.currency_to_ufoshi('usd')

    @classmethod
    def rub_to_ufoshi(cls):
        return cls.currency_to_ufoshi('rub')

    @classmethod
    def btc_to_ufoshi(cls):
        return cls.currency_to_ufoshi('btc')

    @classmethod
    def satoshi_to_ufoshi(cls):
        return cls.currency_to_ufoshi('btc') / Decimal(BTC)


EXCHANGE_RATES = {
    'ufoshi': ufoshi_to_ufoshi,
    'ufo': ufo_to_ufoshi,
    'satoshi': RatesAPI.satoshi_to_ufoshi,
    'btc': RatesAPI.btc_to_ufoshi,
    'usd': RatesAPI.usd_to_ufoshi,
    'rub': RatesAPI.rub_to_ufoshi,
}


def currency_to_ufoshi(amount, currency):
    """Converts a given amount of currency to the equivalent number of
    ufoshi. The amount can be either an int, float, or string as long as
    it is a valid input to :py:class:`decimal.Decimal`.

    :param amount: The quantity of currency.
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``int``
    """
    ufoshis = EXCHANGE_RATES[currency]()
    return int(ufoshis * Decimal(amount))


class CachedRate:
    __slots__ = ('satoshis', 'last_update')

    def __init__(self, satoshis, last_update):
        self.satoshis = satoshis
        self.last_update = last_update


def currency_to_ufoshi_local_cache(f):
    start_time = time()

    cached_rates = dict([
        (currency, CachedRate(None, start_time)) for currency in EXCHANGE_RATES.keys()
    ])

    @wraps(f)
    def wrapper(amount, currency):
        now = time()

        cached_rate = cached_rates[currency]

        if not cached_rate.satoshis or now - cached_rate.last_update > DEFAULT_CACHE_TIME:
            cached_rate.satoshis = EXCHANGE_RATES[currency]()
            cached_rate.last_update = now

        return int(cached_rate.satoshis * Decimal(amount))

    return wrapper


@currency_to_ufoshi_local_cache
def currency_to_ufoshi_local_cached():
    pass  # pragma: no cover


def currency_to_ufoshi_cached(amount, currency):
    """Converts a given amount of currency to the equivalent number of
    satoshi. The amount can be either an int, float, or string as long as
    it is a valid input to :py:class:`decimal.Decimal`. Results are cached
    using a decorator for 60 seconds by default. See :ref:`cache times`.

    :param amount: The quantity of currency.
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``int``
    """
    return currency_to_ufoshi_local_cached(amount, currency)


def ufoshi_to_currency(num, currency):
    """Converts a given number of ufoshi to another currency as a formatted
    string rounded down to the proper number of decimal places.

    :param num: The number of ufoshi.
    :type num: ``int``
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``str``
    """
    return '{:f}'.format(
        Decimal(
            num / Decimal(EXCHANGE_RATES[currency]())
        ).quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION[currency]),
            rounding=ROUND_DOWN
        ).normalize()
    )


def ufoshi_to_currency_cached(num, currency):
    """Converts a given number of ufoshi to another currency as a formatted
    string rounded down to the proper number of decimal places. Results are
    cached using a decorator for 60 seconds by default. See :ref:`cache times`.

    :param num: The number of ufoshi.
    :type num: ``int``
    :param currency: One of the :ref:`supported currencies`.
    :type currency: ``str``
    :rtype: ``str``
    """
    return '{:f}'.format(
        Decimal(
            num / Decimal(currency_to_ufoshi_cached(1, currency))
        ).quantize(
            Decimal('0.' + '0' * CURRENCY_PRECISION[currency]),
            rounding=ROUND_DOWN
        ).normalize()
    )
