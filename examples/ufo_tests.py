import aioufobit
import asyncio

wallet = aioufobit.Key("YOUR_PRIVATE_KEY")

outputs = [ # destination address
        ('UgdMm8b2WpGX5EdFxSry9VuJnyY8SWsZh3', 100, 'ufo'),
    ]

async def get_balance():
    data = await wallet.get_balance('ufo')

    print(data)

async def get_address():
    address = wallet.get_address()
    
    print(address)

async def send_ufo():
    utxos = await wallet.get_unspents()
    
    tx_data = await wallet.send(outputs, unspents=utxos)
    
    print(tx_data)

async def send_message():
    utxos = await wallet.get_unspents()
    
    tx_data = wallet.create_transaction(outputs, unspents=utxos, message="User Slabber")
    
    print(tx_data) # now you need broadcast it using https://explorer.ufobject.com/tx/send

if __name__ == "__main__":
    asyncio.run(get_balance())
    asyncio.run(get_address())
    asyncio.run(send_ufo())
    asyncio.run(send_message())