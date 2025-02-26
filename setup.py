from setuptools import find_packages, setup

with open('aioufobit/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('= ')[1].strip("'")
            break

setup(
    name='AIOufobit',
    version=version,
    description='Async UFO made easy.',
    long_description=open('README.rst', 'r').read(),
    author='Ofek Lev',
    author_email='ofekmeister@gmail.com',
    maintainer='Ofek Lev',
    maintainer_email='ofekmeister@gmail.com',
    url='https://github.com/ofek/bit',
    download_url='https://github.com/ofek/bit',
    license='MIT',

    keywords=(
        'async',
        'ufo',
        'bitcoin',
        'cryptocurrency',
        'payments',
        'tools',
        'wallet',
    ),

    classifiers=(
        'Development Status :: 8 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),

    install_requires=('coincurve>=4.3.0', 'aiohttp', 'asyncio'),
    extras_require={
        'cli': ('appdirs', 'click', 'privy', 'tinydb'),
        'cache': ('lmdb', ),
    },
    tests_require=['pytest'],

    packages=find_packages(),
    entry_points={
        'console_scripts': (
            'aioufobit = aioufobit.cli:bit',
        ),
    },
)
