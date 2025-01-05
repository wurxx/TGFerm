import asyncio
import logging
import aiohttp
import random
from config import *
from pyrogram import Client
import aiofiles
from pyrogram import errors
import os
import time

async def createSession(acc, prox):
    try:
        print(acc[0], "loggining", str(acc[3]))
        
        client = Client(f"./hsess/{acc[0]}", acc[1], acc[2], phone_number=acc[0], password=acc[3], proxy=prox)
        await client.connect()
        print(7)
        hexi = await client.send_code(client.phone_number)
        await asyncio.sleep(3)
        print(0)
        async with Client(f"./sess/{acc[0]}", acc[1], acc[2], phone_number=acc[0], password=acc[3], proxy=prox) as clientMain:
            code = [s[:-1] for s in [x.text async for x in clientMain.get_chat_history(777000, 1)][0].split() if s[:-1].isdigit()][0]
            print(code)
        try:
            await client.sign_in(client.phone_number, hexi.phone_code_hash, code)
            print(10)
        except errors.SessionPasswordNeeded:print(20);await client.check_password(str(acc[3]))
        print(3)
        await client.disconnect()
        return True
    except Exception as e:print(acc, e)
    
async def OnlineSets():
    onlineData = {}
    while True:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{HOST}/accs") as r:
                accs= await r.json()

        if len(accs)==0:print('Нет аккаунтов');await asyncio.sleep(5);continue
        for acc in accs:
            if acc[5] == None:continue
            if acc[4] == None:prox = None
            else:prox = {
            "scheme": acc[4].split("://")[0],  # "socks4", "socks5" and "http" are supported
            "hostname": acc[4].split("://")[1].split("@")[1].split(':')[0],
            "port": int(acc[4].split("://")[1].split("@")[1].split(':')[1]),
            "username": acc[4].split("://")[1].split("@")[0].split(':')[0],
            "password": acc[4].split("://")[1].split("@")[0].split(':')[1]}
            
            
            if acc[0] not in onlineData:onlineData[acc[0]] = time.time()
            
            if onlineData[acc[0]] < time.time():
                print('online', acc)
                if not any([acc[0] in x for x in os.listdir('./hsess/')]):await createSession(acc, prox)
                try:
                    async with Client(f"./hsess/{acc[0]}", acc[1], acc[2], phone_number=acc[0], password=acc[3], proxy=prox) as client:       
                        await client.send_message('me', 'online')
                        await client.delete_messages('me', [x.id async for x in client.get_chat_history('me', 1)])
                except:os.remove(f"./hsess/{acc[0]}.session");continue
                if acc[5] not in [None, 'all']:onlineData[acc[0]]=time.time()+random.randint(int(int(acc[5])*60*0.9), int(int(acc[5])*60*1.1))
        await asyncio.sleep(1)    
            
            

async def main():
    t = []
    t.append(asyncio.create_task(OnlineSets()))
    await asyncio.gather(*t)
    



if __name__=="__main__":
    asyncio.run(main())