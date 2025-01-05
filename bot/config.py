from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

HOST = 'http://127.0.0.1:8855'
admins = [1032884383, 6769252698]
apiid=
apihash = ""
botToken = ''

bot = Bot(token=botToken, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
clients = {}
clientListData = {}
channelsbufData = {}