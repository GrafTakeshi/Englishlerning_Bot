from telebot import TeleBot, StateMemoryStorage

TG_TOKEN = ''
state_storage = StateMemoryStorage()
token_bot = TG_TOKEN
bot = TeleBot(token_bot, state_storage=state_storage)

#Параметры БД

