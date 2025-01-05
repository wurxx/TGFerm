from pyrogram import Client
import aiofiles
from pyrogram import errors
from pyrogram.enums import *
import aiohttp
import random
from aiogram.filters import *
from aiogram.types import *
from config import *
from keyboards import *


async def MsgLAccInfo(acc, message:Message):
    t='\n'
    try:
        if acc[4] == None:prox = None
        else:prox = {
     "scheme": acc[4].split("://")[0],  # "socks4", "socks5" and "http" are supported
     "hostname": acc[4].split("://")[1].split("@")[1].split(':')[0],
     "port": int(acc[4].split("://")[1].split("@")[1].split(':')[1]),
     "username": acc[4].split("://")[1].split("@")[0].split(':')[0],
     "password": acc[4].split("://")[1].split("@")[0].split(':')[1]
 }
        async with Client(f"./sess/{acc[0]}", acc[1], acc[2], password=acc[3], proxy=prox) as client:
            me = await client.get_chat(client.me.id)
            t+=f'''💚 <a href="https://t.me/testerofprojbot?start=goacc_{acc[0]}">{acc[0]}</a> | {me.first_name}'''
            print(t)
            print(me, client.me)
            if client.me.is_premium:clientListData[message.from_user.id]['prem']+=1;t+=' | 🌟'
            
            
    except Exception as e:
        t+=f'''🖤 {acc[0]} | {e} <a href="https://t.me/testerofprojbot?start=remove_{acc[0]}">Удалить</a> ❌'''
        clientListData[message.from_user.id]['problem']+=1
    clientListData[message.from_user.id]['txt']+=t
    try:await message.edit_text(clientListData[message.from_user.id]['txt'], reply_markup=cancelKB)
    except:pass
    
async def chekSubs(acc, message:Message, channel):
    try:
        if acc[4] == None:prox = None
        else:prox = {
     "scheme": acc[4].split("://")[0],  # "socks4", "socks5" and "http" are supported
     "hostname": acc[4].split("://")[1].split("@")[1].split(':')[0],
     "port": int(acc[4].split("://")[1].split("@")[1].split(':')[1]),
     "username": acc[4].split("://")[1].split("@")[0].split(':')[0],
     "password": acc[4].split("://")[1].split("@")[0].split(':')[1]}
        
        async with Client(f"./sess/{acc[0]}", acc[1], acc[2], password=acc[3], proxy=prox) as client:
            d=[]
            async for x in client.get_dialogs():
                # print(x, channel)
                if channel == x.chat.username  and x.chat.type in [ChatType.CHANNEL, ChatType.GROUP, ChatType.SUPERGROUP]:d.append(x)
                if x.chat.usernames !=None:
                    for u in x.chat.usernames:
                        if u.username == channel:d.append(x)
            if d !=[]:
                channelsbufData[message.chat.id][channel]['subs'].append(acc)
                await message.edit_text(f"Подписанных: {len(channelsbufData[message.chat.id][channel]['subs'])}\nПроблем: {len(channelsbufData[message.chat.id][channel]['problem'])}")
            else:channelsbufData[message.chat.id][channel]['unsubs'].append(acc)
    except Exception as e:
        channelsbufData[message.chat.id][channel]['problem'].append(str(e))
        print(e) 
            
            
async def unsubs(acc, callback:CallbackQuery, channel):
    try:
        if acc[4] == None:prox = None
        else:prox = {
     "scheme": acc[4].split("://")[0],  # "socks4", "socks5" and "http" are supported
     "hostname": acc[4].split("://")[1].split("@")[1].split(':')[0],
     "port": int(acc[4].split("://")[1].split("@")[1].split(':')[1]),
     "username": acc[4].split("://")[1].split("@")[0].split(':')[0],
     "password": acc[4].split("://")[1].split("@")[0].split(':')[1]}
        
        async with Client(f"./sess/{acc[0]}", acc[1], acc[2], password=acc[3], proxy=prox) as client:
            await client.leave_chat(channel)
    except Exception as e:print('Unsubs ERRR', acc[0], e)
    
    
