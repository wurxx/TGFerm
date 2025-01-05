from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import *
from aiogram.types import *
from aiogram.fsm.state import *
from aiogram.fsm.context import *
from keyboards import *
from pyrogram import Client
import aiofiles
from pyrogram import errors
from aiogram.types import FSInputFile
import aiohttp
import random
from config import *
from classes import *
import os
from clientFunc import *
import asyncio
import logging
import requests
# logging.basicConfig(level=logging.INFO)

globaltext= 'TG ferma v1.1'

@dp.message(CommandStart())
async def start(message:Message):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{HOST}/admins") as r:BaseAdmins = await r.json()
    # print(BaseAdmins)
    if message.from_user.id not in admins and str(message.from_user.id) not in BaseAdmins:return  
    
    if 'goacc' in message.text:await goacc(message.text.split('_')[1:], message.from_user.id);return
    if 'remove' in message.text:await dellacc(message.text.split('_')[-1], message.from_user.id);return
    if 'delAdmin' in message.text:await dellAdmin(message.text.split('_')[-1], message.from_user.id);return

    await message.answer(globaltext, reply_markup=startKB)
    
@dp.callback_query(F.data == 'cancelMain')
async def maincncl(callback:CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(globaltext, reply_markup=startKB)

@dp.callback_query(F.data == 'cancel')
async def goHome(callback:CallbackQuery, state:FSMContext):
    await state.clear()
    await callback.answer()
    try:await callback.message.delete()
    except:pass
    await bot.send_message(callback.from_user.id, globaltext, reply_markup=startKB)  
    
@dp.callback_query(F.data == 'ManageAccs')
async def manageAccs(callback:CallbackQuery):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{HOST}/admins") as r:BaseAdmins = await r.json()
    if callback.from_user.id not in admins and str(callback.from_user.id) not in BaseAdmins:return   
    await callback.answer()
    await callback.message.edit_text(globaltext, reply_markup=manageAccKB)
    
@dp.callback_query(F.data == 'addTgacc')
async def startaddAcc(callback:CallbackQuery):
    await callback.answer()
    kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ручной ввод', callback_data='addTgaccinHands')],
    [InlineKeyboardButton(text='Файл сессии', callback_data='addTgaccinSess')],
    [InlineKeyboardButton(text='Назад', callback_data='ManageAccs')],])
    await callback.message.edit_text(globaltext, reply_markup=kb)

@dp.callback_query(F.data=='addTgaccinHands', StateFilter(default_state))
async def addacchandes(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await state.set_state(AddTelegramAccount.phone)
    await callback.message.edit_text('Введите номер с кодом страны в формате 888777000', reply_markup=cancelKB)
        
@dp.message(StateFilter(AddTelegramAccount.phone))
async def newaccphone(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    if not message.text.isdigit():await message.answer('Вы неправильно указали телефон', reply_markup=cancelKB);return
    await state.update_data(phone = message.text) 
    await state.set_state(AddTelegramAccount.api_pair)
    await message.answer('Введите api_id:api_hash пару через ":" ', reply_markup=cancelKB)
    
@dp.message(StateFilter(AddTelegramAccount.api_pair))
async def newaccapi(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await state.update_data(api = message.text) 
    phone = (await state.get_data())['phone']
    client = Client(f"./sess/{phone}", message.text.split(":")[0], message.text.split(":")[1], phone_number=phone)
    await client.connect()
    try:
        sent_code_info = await client.send_code(phone)
        clients[phone] ={}
        clients[phone]['hash'] = sent_code_info.phone_code_hash
        clients[phone]['app'] = client
        await message.answer('Пришлите код, отправленный на ваше устройство', reply_markup=cancelKB)
        await state.set_state(AddTelegramAccount.code)
    except Exception as e:
        await message.answer(f'Ошибка: {e}')
        await state.clear()


@dp.message(StateFilter(AddTelegramAccount.code))
async def addingTGCOde(message:Message, state:FSMContext):
    
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await state.update_data(code = message.text)
    data = await state.get_data()
    client:Client = clients[data['phone']]['app']
    while True:
        try:
            
            await client.sign_in(client.phone_number, clients[data['phone']]['hash'], message.text)
            break
        except errors.SessionPasswordNeeded:
                await message.answer('Введите пароль для 2fa', reply_markup=cancelKB)
                await state.set_state(AddTelegramAccount.twofuck)
                return
        except errors.PhoneCodeInvalid:
            await message.answer("Неправильный код, попробуйте еще раз", reply_markup=cancelKB)
            return
        except Exception as e:
            await message.answer(f'Ошибка: {e}')
            await state.clear()
            return

    await client.disconnect()
    await state.clear()
    
    await successConnect(client, message, None)

    
@dp.message(StateFilter(AddTelegramAccount.twofuck))
async def addingTGCOde(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await state.update_data(passwd = message.text)
    data = await state.get_data()
    phone = (await state.get_data())['phone']
    client:Client = clients[phone]['app']
    try:
        await client.check_password(message.text)
    except errors.PasswordHashInvalid:
        await message.answer("Неправильный пароль, попробуйте еще раз", reply_markup=cancelKB)
        return
    except Exception as e:
            await message.answer(f'Ошибка: {e}')
            await state.clear()
            return

    await client.disconnect()
    await state.clear()
    
    await successConnect(client, message, message.text)

@dp.callback_query(F.data == 'addTgaccinSess', StateFilter(default_state))
async def addSession(message:Message, state:FSMContext):
    await state.set_state(AddtgBySession.sess)
    await message.answer('Пришлите файл сессии', reply_markup=cancelKB)
    
@dp.message(StateFilter(AddtgBySession.sess))
async def acceptSession(message:Message, state:FSMContext):
    # print(message)
    if message.document.file_name.split('.')[-1]=='session':
        await bot.download_file((await bot.get_file(message.document.file_id)).file_path, f"./sess/{message.document.file_name}")
        async with Client(f"./sess/{message.document.file_name}", apiid, apihash) as client:
            if client.is_connected:await message.answer('Успешно');return#ДОБАВИТЬ ВВОД КЛЮЧЕЙ И ТЕЛЕФОНА
        os.remove(f"./sess/{message.document.file_name}")
    else:await message.answer('Неправильный формат файла')
    
async def successConnect(client:Client, message:Message, fat):
    print('2FA', fat)
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(f"{HOST}/addTg?phone={client.phone_number}&api_id={client.api_id}&api_hash={client.api_hash}&twoFa={fat}&proxy={client.proxy}") as r:
                if await r.json():
                    await message.answer(f'Успешно', reply_markup=cancelKB)
                else:await message.answer(await r.text(), reply_markup=cancelKB)
    except Exception as e:await message.answer(f'{e}', reply_markup=cancelKB)
    
@dp.callback_query(F.data == 'showTgacc')
async def showaccs(callback:CallbackQuery):
    global clientListData
    await callback.message.edit_text('Создание статистики ...')
    async with aiohttp.ClientSession() as s:
            async with s.get(f"{HOST}/accs") as r:
                accs= await r.json()
                if type(accs)!= list:await callback.answer(accs);return
                await callback.answer()
    clientListData[callback.message.from_user.id] = {}
    clientListData[callback.message.from_user.id]['txt'] = ''
    clientListData[callback.message.from_user.id]['problem'] = 0
    clientListData[callback.message.from_user.id]['prem'] = 0
    t=[]
    for acc in accs:
        t.append(asyncio.create_task(MsgLAccInfo(acc, callback.message)))
    await asyncio.gather(*t)
    
    try:await callback.message.edit_text(
        f"Всего аккаунтов: <b>{len(accs)}</b>\nПроблемных: <b>{clientListData[callback.message.from_user.id]['problem']}</b>\nПремиум: <b>{clientListData[callback.message.from_user.id]['prem']}</b>\n{clientListData[callback.message.from_user.id]['txt']}"
        , reply_markup=cancelKB, parse_mode=ParseMode.HTML)
    except Exception as e:print(e)
        
@dp.callback_query(F.data.startswith('updateacc')) 
async def updateaccInfo(callback:CallbackQuery):
    try:await callback.message.delete();await bot.delete_message(callback.message.chat.id, callback.message.message_id-1)
    except:pass
    await callback.answer()
    await goacc([callback.data.split('_')[-1]], callback.from_user.id)

@dp.callback_query(F.data.startswith('goacccncstate')) 
async def updateaccInfo(callback:CallbackQuery, state:FSMContext):
    await state.clear()
    try:await callback.message.delete();await bot.delete_message(callback.message.chat.id, callback.message.message_id-1)
    except:pass
    await callback.answer()
    await goacc([callback.data.split('_')[-1]], callback.from_user.id)


         
async def goacc(phone, userid):
    
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{HOST}/accs") as r:
            accs= await r.json()
            if type(accs)!= list:await bot.send_message(userid, "Ошибка при получении аккаунта")
            acc = [x for x in accs if x[0] == phone[0]][0]
            if len(acc)<5:await bot.send_message(userid, "Ошибка при получении аккаунта")
    t = ''
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
            t+=f"👤: {client.me.first_name}"
            if client.me.is_premium:t+='🌟'
            t+=f"\n📱: {acc[0]}"
            if acc[3]:t+=f"\n👀: {acc[3]}"
            t+=f"\n👀 Статус: {client.me.status}"
            if prox!=None:t+=f"\n🌐 proxy: {acc[4]}"
            if acc[5]:t+=f"\n♻️ Online: {acc[5]}"
            
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text = 'Получить код для входа', callback_data=f"getcode_{phone[0]}")],
            [InlineKeyboardButton(text = 'Смена онлайна', callback_data=f"OnlineChange_{phone[0]}")],
            [InlineKeyboardButton(text = 'Изменить прокси', callback_data=f"setNewProxy_{phone[0]}")],
            [InlineKeyboardButton(text = '♻️ Обновить ♻️', callback_data=f"updateacc_{phone[0]}")],
            [InlineKeyboardButton(text = '❌ Выйти ❌', callback_data="ManageAccs")],
            
            
            ])   
        await bot.send_message(userid, t, reply_markup=kb) 
    except Exception as e:
        t=str(e)
        await bot.send_message(userid, t, reply_markup=cancelKB)
        
@dp.callback_query(F.data.startswith('getcode'))
async def showcode(callback:CallbackQuery):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{HOST}/accs") as r:
            accs= await r.json()
            if type(accs)!= list:await callback.message.edit_text("Ошибка при получении аккаунта", reply_markup=cancelKB)
            print(accs, callback.data.split('_')[-1])
            acc = [x for x in accs if x[0] == callback.data.split('_')[-1]][0]
            if len(acc)<5:await callback.message.edit_text("Ошибка при получении аккаунта", reply_markup=cancelKB)
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
            code = [t[:-1] for t in [x.text async for x in client.get_chat_history(777000, 1)][0].split() if t[:-1].isdigit()]
            if code:await callback.answer(code[0]) 
            else:await callback.answer('Последнее сообщение не содержит код')
    except Exception as e:await callback.message.edit_text(str(e), reply_markup=cancelKB)


@dp.callback_query(F.data.startswith('setNewProxy'), StateFilter(default_state))
async def newproxyfor(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await callback.message.edit_text("Введите новый прокси в формате:\n пртокол://login:password@ip:port", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='отмена', callback_data=f"goacccncstate_{callback.data.split('_')[-1]}")]]))
    await state.set_state(NewProxy.proxy)
    await state.update_data(phone = callback.data.split('_')[-1])
    
@dp.message(StateFilter(NewProxy.proxy))
async def proxUpdater(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    phone = (await state.get_data())['phone']
    await state.clear()
    if message.text=='none':message.text=None
    try:
        response = requests.get("http://httpbin.org/ip", proxies={"http": message.text, "https": message.text}, timeout=5)
        print(response)
        if response.json():
            async with aiohttp.ClientSession() as s:
                async with s.post(f"{HOST}/updateProxy?phone={phone}&proxy={message.text}") as r:
                    if await r.json():await message.answer('Успешно', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='назад', callback_data=f'updateacc_{phone}')]]))
                    else:await message.answer(await r.text(), reply_markup=cancelKB)
        else:await message.answer("неверный прокси", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='назад', callback_data=f'updateacc_{phone}')]]))

    except Exception as e:
        await message.answer("неверный прокси", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='назад', callback_data=f'updateacc_{phone}')]]))

        print(e)
        
@dp.callback_query(F.data.startswith('OnlineChange'), StateFilter(default_state))
async def newOnlinee(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await state.set_state(newOnline.online) 
    phone = callback.data.split('_')[-1]
    await state.update_data(phone=phone)
    await callback.message.edit_text('Введите раз в сколько минут аккаунт будет выходить в сеть\nall - Вечный онлайн\nnone -  без выхода в сеть\n<i>(При отправке сообщений пользователям, аккаунт будет выходить в сеть, не взярая на интервалы)</i>', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='назад', callback_data=f'goacccncstate_{phone}')]]))

@dp.message(StateFilter(newOnline.online))
async def updateOnline(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    phone = (await state.get_data())['phone']
    await state.clear()
    if not message.text.isdigit() and message.text not in ['all', 'none']:await message.answer('Указанное значение не является числом', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='назад', callback_data=f'updateacc_{phone}')]]) );return
    
    if message.text == 'none':online = None
    else:online = message.text
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{HOST}/updateOnline?phone={phone}&online={online}") as r:
                if await r.json():await message.answer('Успешно', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='назад', callback_data=f'updateacc_{phone}')]]))
                else:await message.answer(await r.text(), reply_markup=cancelKB)
            
@dp.callback_query(F.data == 'masssubscribe', StateFilter(default_state))
async def subs(callback:CallbackQuery, state:FSMContext):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{HOST}/admins") as r:BaseAdmins = await r.json()
    if callback.from_user.id not in admins and str(callback.from_user.id) not in BaseAdmins:return   
    await callback.answer()
    await callback.message.edit_text('Введите username канала/группы', reply_markup=cancelKB)
    await state.set_state(SubsChat.chat)
    
@dp.message(StateFilter(SubsChat.chat))
async def subscribe2(message:Message, state:FSMContext):
    if message.text[0] == '@':channel = message.text[1:]
    else:channel = message.text
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await state.clear()
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{HOST}/accs") as r:
            accs= await r.json()
            if type(accs)!= list:await message.answer("Ошибка при получении аккаунта", reply_markup=cancelKB);return
    try:
        chekacc = random.choice(accs)
        if chekacc[4] == None:prox = None
        else:prox = {
     "scheme": chekacc[4].split("://")[0],  # "socks4", "socks5" and "http" are supported
     "hostname": chekacc[4].split("://")[1].split("@")[1].split(':')[0],
     "port": int(chekacc[4].split("://")[1].split("@")[1].split(':')[1]),
     "username": chekacc[4].split("://")[1].split("@")[0].split(':')[0],
     "password": chekacc[4].split("://")[1].split("@")[0].split(':')[1]
 }
        async with Client(f"./sess/{chekacc[0]}", chekacc[1], chekacc[2], password=chekacc[3], proxy=prox) as client:
            chat = await client.get_chat(channel)
            if chat.type not in [ChatType.CHANNEL, ChatType.GROUP, ChatType.SUPERGROUP]:await message.answer("Юзернейм не принадлежит каналу/группе", reply_markup=cancelKB);return
        
        
        
        
        mesg = await bot.send_message(message.from_user.id, 'Проверка подписок...')
        channelsbufData[message.from_user.id] = {}
        channelsbufData[message.from_user.id][channel] = {}
        channelsbufData[message.from_user.id][channel]['subs'] = []
        channelsbufData[message.from_user.id][channel]['unsubs'] = []
        channelsbufData[message.from_user.id][channel]['problem']= []
        t = []
        for acc in accs:t.append(asyncio.create_task(chekSubs(acc, mesg, channel)))
        await asyncio.gather(*t)
        
        await mesg.edit_text(f"Всего: {len(accs)}\nПодписанных: {len(channelsbufData[message.from_user.id][channel]['subs'])}\nПроблем: {len(channelsbufData[message.from_user.id][channel]['problem'])}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Подписаться', callback_data=f"joinsgroup_{channel}")],
            [InlineKeyboardButton(text='Отписаться со всех', callback_data=f"leftgroup_{channel}")],
            [InlineKeyboardButton(text='выйти', callback_data='cancel')]
        ]))
    except errors.UsernameInvalid :await message.answer("Такого юзернейма нет", reply_markup=cancelKB);return
    except errors.UsernameNotOccupied:await message.answer("Такого юзернейма нет", reply_markup=cancelKB);return
    except Exception as e:await message.answer(str(e), reply_markup=cancelKB);return

@dp.callback_query(F.data.startswith('leftgroup'))
async def leftall(callback:CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Запущено в работу', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='выйти', callback_data='cancel')]]))
    channel = callback.data.split('_')[-1]
    t = []
    for acc in channelsbufData[callback.from_user.id][channel]['subs']:t.append(asyncio.create_task(unsubs(acc, callback, channel)))
    await asyncio.gather(*t)

@dp.callback_query(F.data.startswith('joinsgroup'), StateFilter(default_state))
async def joins(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await callback.message.edit_text(f"Введите количество аккаунтов для подписки\nМаксимум: {len(channelsbufData[callback.from_user.id][callback.data.split('_')[-1]]['unsubs'])}", reply_markup=cancelKB)
    await state.set_state(SubscribinhChat.count)
    await state.update_data(channel = callback.data.split('_')[-1])

@dp.message(StateFilter(SubscribinhChat.count))
async def subsgetcnt(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    if not message.text.isdigit() or message.text=='0' or '-' in message.text:await message.answer(f"Введите число от 1 до {len(channelsbufData[message.from_user.id][channel]['unsubs'])}", reply_markup=cancelKB);await state.clear();return
    channel  = (await state.get_data())['channel']
    if len(channelsbufData[message.from_user.id][channel]['unsubs']) < int(message.text):await message.answer("Указанное значение больше допустимого", reply_markup=cancelKB);await state.clear();return
    await state.update_data(count = message.text)
    await state.set_state(SubscribinhChat.interval)
    await message.answer("Введите интервал подписка между аккаунтами в секундах\nДля защиты аккаунтов значение интервала будет изменено в пределах 10%", reply_markup=cancelKB)

@dp.message(StateFilter(SubscribinhChat.interval))
async def subsgetint(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    if not message.text.isdigit() or '-' in message.text or message.text == '0':await message.answer(f"Введите число от 1 до {len(channelsbufData[message.from_user.id][data['channel']]['unsubs'])}", reply_markup=cancelKB);await state.clear();return
    data = await state.get_data()
    await state.clear()
    msg = await bot.send_message(message.from_user.id, "Запуск...")
    try:
        subs = 0
        froms = len(channelsbufData[message.from_user.id][data['channel']]['unsubs'])
        for acc in channelsbufData[message.from_user.id][data['channel']]['unsubs']:
            if acc[4] == None:prox = None
            else:prox = {
                "scheme": acc[4].split("://")[0],  # "socks4", "socks5" and "http" are supported
                "hostname": acc[4].split("://")[1].split("@")[1].split(':')[0],
                "port": int(acc[4].split("://")[1].split("@")[1].split(':')[1]),
                "username": acc[4].split("://")[1].split("@")[0].split(':')[0],
                "password": acc[4].split("://")[1].split("@")[0].split(':')[1]}
                    
            async with Client(f"./sess/{acc[0]}", acc[1], acc[2], password=acc[3], proxy=prox) as client:
                r = await client.join_chat(data['channel'])
                if r:
                    subs+=1
                    await msg.edit_text(f"{random.choice(['♻️', '🤍', '💙', '👀', '👾', '🤖'])} {subs}/{froms} подписалось")
            
            await asyncio.sleep(random.randint(int(int(message.text)*0.8), int(int(message.text)*1.2)))
        await msg.edit_text(f"{random.choice(['♻️', '🤍', '💙', '👀', '👾', '🤖'])} {subs}/{froms} подписалось", reply_markup=cancelKB)
    except Exception as e:print(e)
    
    

async def dellacc(acc, uid):
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{HOST}/delAcc?acc={acc}") as r:
            if await r.json():
                os.remove(f"./sess/{acc}.session")
                os.remove(f"./hsess/{acc}.session")
                await bot.send_message(uid, "Аккаунт удален", reply_markup=cancelKB)
            else:await bot.send_message(uid, await r.text(), reply_markup=cancelKB)


@dp.callback_query(F.data == 'adminka')
async def mainadm(callback:CallbackQuery):
    
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{HOST}/admins") as r:BaseAdmins = await r.json()
    if callback.from_user.id not in admins and str(callback.from_user.id) not in BaseAdmins:return     
    if callback.from_user.id not in admins:await callback.answer('У вас есть доступ к боту');return
    await callback.answer()
    t = 'Текущие администраторы:\n'
    t += '\n'.join([f'ID: {x} | ❌ <a href="https://t.me/testerofprojbot?start=delAdmin_{x}">Удалить</a> ❌' for x in BaseAdmins])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить админа', callback_data='addAdmin')],
        [InlineKeyboardButton(text='выход', callback_data='cancel')]
    ])
    await callback.message.edit_text(t, reply_markup=kb, parse_mode=ParseMode.HTML)
    
async def dellAdmin(admin, uid):

    async with aiohttp.ClientSession() as s:
        async with s.post(f"{HOST}/delAdmin?id={admin}") as r:
            if await r.json():await bot.send_message(uid, "Успешно", reply_markup= cancelKB)
            else:await bot.send_message(uid, await r.text(), reply_markup= cancelKB)
    
@dp.callback_query(F.data == 'addAdmin', StateFilter(default_state))
async def addNewAdmin(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await callback.message.edit_text("Введите id пользователя\nПример:1032884383", reply_markup=cancelKB)
    await state.set_state(NewAdmin.idi)

@dp.message(StateFilter(NewAdmin.idi))
async def addAdmin(message:Message, state:FSMContext):
    try:await message.delete();await bot.delete_message(message.chat.id, message.message_id-1)
    except:pass
    await state.clear()
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{HOST}/addAdmin?id={message.text}") as r:
            if await r.json():await message.answer("Успешно", reply_markup= cancelKB)
            else:await message.answer(await r.text(), reply_markup= cancelKB)
    
    
    
        
    
@dp.callback_query()
async def clearState(callback:CallbackQuery, state:FSMContext):
    await callback.answer()
    await state.clear()

if __name__ == "__main__":
    
    dp.run_polling(bot)
    