from sqlalchemy import URL
from telebot import TeleBot, StateMemoryStorage

TG_TOKEN = ''
state_storage = StateMemoryStorage()
bot = TeleBot(TG_TOKEN, state_storage=state_storage)

# Параметры БД

# db_connection = "dbname=postgres user=postgres password=postgres"
# DSN = URL.create(
#     "postgresql",
#     username="postgres",
#     password="postgres",
#     host="localhost",
#     port=5432,
#     database="postgres",
# )
DSN = "postgresql://postgres:postgres@localhost:5432/postgres"
