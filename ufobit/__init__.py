from ufobit.format import verify_sig
from ufobit.network.fees import set_fee_cache_time
from ufobit.network.rates import SUPPORTED_CURRENCIES, set_rate_cache_time
from ufobit.network.services import set_service_timeout
from ufobit.wallet import Key, PrivateKey, wif_to_key
from ufobit.network.services import config

__version__ = '0.4.5'
