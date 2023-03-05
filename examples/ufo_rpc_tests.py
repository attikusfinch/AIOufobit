from ufobit.network.rpc import RPCHost
import ufobit
import asyncio

rpc = RPCHost("ufomoon", "ufomoon", "127.0.0.1", 8444, False)

wallet = ufobit.Key("YOUR_PRIVATE_KEY")

outputs = [ # destination address
        ('UgdMm8b2WpGX5EdFxSry9VuJnyY8SWsZh3', 100, 'ufo'),
    ]

async def create_dict():
    addresses = {}
    for i in range(0, 25):
        address = await rpc.getnewaddress()
        addresses[address] = 1

    return addresses

async def send_many():
    await rpc.sendmany(await create_dict(), 1, "User Slabber")

async def send_message():
    unspent = await rpc.get_unspents([wallet.address, wallet.sw_address])

    message_tx = wallet.create_transaction(outputs, unspents=unspent, message="User Slabber")

    await rpc.broadcast_tx(message_tx)

    return message_tx

async def create_address():
    print(await rpc.getnewaddress("User Wallet", "legacy")) # return C start address
    print(await rpc.getaddressesbylabel("User Wallet"))

async def get_network():
    print(await rpc.getnetworkinfo())

async def get_balance():
    print(await rpc.get_balance(wallet.get_sw_address()))

async def main():
    await get_balance() # print balance
    await get_network() # print network info
    await create_address() # create address and get it by label
    await send_many() # send many into one transaction
    
    for i in range(0, 25):
        await send_message() # send transaction with message

if __name__ == '__main__':
    asyncio.run(main())