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

    >>> from ufobit import Key
    >>>
    >>> my_key = Key(...)
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
