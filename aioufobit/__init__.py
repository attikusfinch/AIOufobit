from .format import verify_sig
from .network.fees import set_fee_cache_time
from .network.rates import SUPPORTED_CURRENCIES, set_rate_cache_time
from .network.services import set_service_timeout
from .wallet import Key, PrivateKey, wif_to_key

__version__ = '0.8.4'