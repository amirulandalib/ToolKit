import logging

from aiogram import Bot, Dispatcher, types
from pyrogram import Client
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import storage

import config

client = Client("bot", config.api_id, config.api_hash, bot_token=config.token)
bot = Bot(token=config.token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, no_throttle_error=True)

open("log.log", "w").close()
logging.basicConfig(level=logging.WARNING, filename="log.log", filemode="a")
