from aiogram.fsm.state import *
from aiogram.fsm.context import *

class AddTelegramAccount(StatesGroup):
    phone = State()
    code = State()
    api_pair = State()
    twofuck = State()

class AddtgBySession(StatesGroup):
    sess = State()

class NewProxy(StatesGroup):
    proxy=State()
    
class newOnline(StatesGroup):
    online = State()
    
class SubsChat(StatesGroup):
    chat = State()
    
    
class SubscribinhChat(StatesGroup):
    count= State()
    interval = State()
    
class NewAdmin(StatesGroup):
    idi = State()