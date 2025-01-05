from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import *
from aiogram.types import *
from keyboards import *


startKB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Управление аккаунтами', callback_data='ManageAccs')],
    [InlineKeyboardButton(text='Подписка/отписка на канал/группу', callback_data='masssubscribe')],
    [InlineKeyboardButton(text='Панель', callback_data='adminka')]

 ])

manageAccKB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Добавить аккаунт', callback_data='addTgaccinHands')],
    [InlineKeyboardButton(text='Просмотр аккаунтов', callback_data='showTgacc')],
    [InlineKeyboardButton(text='Назад', callback_data='cancelMain')],
 ])


cancelKB = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
    ])