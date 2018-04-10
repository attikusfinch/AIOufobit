UFOBit: UFO made easy.
=======================

.. image:: https://img.shields.io/pypi/v/ufobit.svg?style=flat-square
    :target: https://pypi.org/project/ufobit

.. image:: https://img.shields.io/pypi/pyversions/ufobit.svg?style=flat-square
    :target: https://pypi.org/project/ufobit

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License

-----

UFOBit is Python's `fastest <https://ofek.github.io/bit/guide/intro.html#why-bit>`_
Uniform Fiscal Object library and was designed from the beginning to feel intuitive, be
effortless to use, and have readable source code. It is heavily inspired by
`Requests <https://github.com/requests/requests>`_ and
`Keras <https://github.com/keras-team/keras>`_. Based on Ofek's Bit code.

**UFOBit is so easy to use, in fact, you can do this:**

.. code-block:: python

    >>> import ufobit
    >>>
    >>> ufobit.config['api_key'] = 'cryptoid api key'
    >>> my_key = ufobit.Key(...)
    >>> my_key.get_balance('ufo')
    '378.623'
    >>>
    >>> outputs = [
    >>>     ('Bz9rtnrFgjEC6Tv6CWpHz8EYFwJJJnwwjq', 25, 'ufo'),
    >>>     ('Bu6rsw6ineEDUuH1Ph5CRzVqTt7s3skgDq', 50, 'satoshi'),
    >>>     ('C5urCiXUyAnsrnKf7RaB2oBpdKxo51Vkpc', 0.02, 'usd'),
    >>>     ('CFhf3Pk3T3MhFvAidRZJ9cxkJ8DurLYmo1', 1, 'rub'),
    >>> ]
    >>>
    >>> my_key.send(outputs)
    'cfecc199a5c6e6bc24610366e8eda36571162e9e3f7c419f0b6095c257acc5fc'
    >>>
    >>> ufobit.network.services.UFO.get_tx('cfecc199a5c6e6bc24610366e8eda36571162e9e3f7c419f0b6095c257acc5fc')
    {
    "hash": "cfecc199a5c6e6bc24610366e8eda36571162e9e3f7c419f0b6095c257acc5fc",
    "block": 1275211,
    "timestamp": 1522830963,
    "confirmations": 5493,
    "fees": 0.01,
    "total_input": 378.623,
    "inputs": [
        {
        "addr": "CA9GaxxUuhexg2hv14Ws1wkvoxLmfqT7HY",
        "amount": 3.0,
        "received_from": {
            "tx": "17290dcbb508f2c69b7ba552c88176e679865297fb090d7ef061cc37c4d9599a",
            "n": 0
        }
        },
        {
        "addr": "CA9GaxxUuhexg2hv14Ws1wkvoxLmfqT7HY",
        "amount": 375.623,
        "received_from": {
            "tx": "2334f2259f57207876a2b7364d2f7e306c18f0db2e76c8324f71f69ae587cebc",
            "n": 1
        }
        }
    ],
    "total_output": 378.613,
    "outputs": [
        {
        "addr": "Bz9rtnrFgjEC6Tv6CWpHz8EYFwJJJnwwjq",
        "amount": 25.0,
        "script": "76a9144d1519b9ab1934c5818239464fb734854c3051b488ac"
        },
        {
        "addr": "Bu6rsw6ineEDUuH1Ph5CRzVqTt7s3skgDq",
        "amount": 3.56887937,
        "script": "76a91415ab361a5c7df1f1f39f6b72caf81732f80e6aa788ac"
        },
        {
        "addr": "C5urCiXUyAnsrnKf7RaB2oBpdKxo51Vkpc",
        "amount": 19.45449593,
        "script": "76a9148c3f74782fdc29a214dd1b6168033801e46d146388ac"
        },
        {
        "addr": "CFhf3Pk3T3MhFvAidRZJ9cxkJ8DurLYmo1",
        "amount": 16.87786971,
        "script": "76a914f7a2679c125ae6d90da693dc5fb2b818f213116c88ac"
        },
        {
        "addr": "CA9GaxxUuhexg2hv14Ws1wkvoxLmfqT7HY",
        "amount": 313.71175499,
        "script": "76a914baa9b852078d0528379e97798693d2a71676c8c088ac"
        }
    ]
    }

Here is the transaction `<https://chainz.cryptoid.info/ufo/tx.dws?1576204.htm>`_.

Features
--------

- Python's fastest available implementation (100x faster than closest library)
- Seamless integration with existing server setups
- Supports keys in cold storage
- Fully supports 25 different currencies
- First class support for storing data in the blockchain
- Deterministic signatures via RFC 6979
- Access to the blockchain through multiple APIs for redundancy
- Exchange rate API, with optional caching
- Optimal transaction fee API, with optional caching
- Compressed public keys by default
- Multiple representations of private keys; WIF, PEM, DER, etc.
- Standard P2PKH transactions

If you are intrigued, continue reading. If not, continue all the same!

Installation
------------

Bit is distributed on `PyPI`_ as a universal wheel and is available on Linux/macOS
and Windows and supports Python 3.5+ and PyPy3.5-v5.7.1+. ``pip`` >= 8.1.2 is required.

.. code-block:: bash

    $ pip install ufobit

Documentation
-------------

Docs are `hosted by Github Pages`_ and are automatically built and published
by Travis after every successful commit to UFOBit's ``master`` branch.

Credits
-------

- Logo courtesy of `<https://textcraft.net>`_
- `Gregory Maxwell`_ (Bitcoin core dev) for teaching me a bit of `ECC`_ math
- `arubi`_ in #bitcoin for helping me understand transaction gotchas
- `fuzeman`_ for bestowing me the name ``bit`` on the `Python Package Index`_

.. _PyPI: https://pypi.org/project/ufobit
.. _hosted by Github Pages: https://ofek.github.io/bit
.. _Gregory Maxwell: https://github.com/gmaxwell
.. _ECC: https://en.wikipedia.org/wiki/Elliptic_curve_cryptography
.. _arubi: https://github.com/fivepiece
.. _fuzeman: https://github.com/fuzeman
.. _Python Package Index: https://pypi.org
