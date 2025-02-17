from aioufobit.network.rpc import OMNIRPCHost
import aioufobit
import asyncio

rpc = OMNIRPCHost("ufomoon", "ufomoon", "127.0.0.1", 8444, False)

wallet = aioufobit.Key("YOUR_PRIVATE_KEY")

async def create_token():
    fixed = await rpc.create_token(
        ecosystem=1, 
        type=2, 
        category="Fixed", 
        subcategory="User", 
        name="Dummy", 
        url="https://slabber.io/channels/@user", 
        data="", 
        fixed=True, 
        amount="1000")
    managed = await rpc.create_token(
        ecosystem=1, 
        type=2, 
        category="Managed", 
        subcategory="User", 
        name="Dummy", 
        url="https://slabber.io/channels/@user", 
        data="", 
        fixed=False) # if token isn't fixed, you haven't set amount. Later you'll print it
    
    fixed_txid = await rpc.omni_sendrawtx(wallet.sw_address, fixed)
    managed_txid = await rpc.omni_sendrawtx(wallet.sw_address, managed)
    
    return fixed_txid, managed_txid

async def print_tokens(txid):
    property_id = (await rpc.omni_gettransaction(txid))["propertyid"]

    await rpc.omni_sendgrant(wallet.sw_address, wallet.sw_address, property_id, "999")

async def create_nft():
    nft = await rpc.create_nft(
        ecosystem=1, 
        category="NFT", 
        subcategory="User", 
        name="Dummy", 
        url="https://slabber.io/channels/@user", 
        data="")
    
    txid = await rpc.omni_sendrawtx(wallet.sw_address, nft)
    
    return txid

if __name__ == "__main__":
    asyncio.run(create_token())
    asyncio.run(create_nft())
    asyncio.run(print_tokens("YOUR_TX_HASH"))