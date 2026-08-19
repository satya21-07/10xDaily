import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        r1 = await client.get('https://api.datamuse.com/words?sp=aberration&md=f')
        r2 = await client.get('https://api.datamuse.com/words?sp=apple&md=f')
        r3 = await client.get('https://api.datamuse.com/words?sp=abstruse&md=f')
        r4 = await client.get('https://api.datamuse.com/words?sp=the&md=f')
        print("aberration:", r1.json())
        print("apple:", r2.json())
        print("abstruse:", r3.json())
        print("the:", r4.json())

asyncio.run(main())
