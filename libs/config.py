# config.py
import asyncio
from telebot.async_telebot import AsyncTeleBot


class Config:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._global_writer = None
        self._global_reader = None
        self._chat_id = None
        self._bot = None
        self._socket_manager = None

    @property
    def writer(self) -> asyncio.StreamWriter:
        return self._global_writer

    @writer.setter
    def writer(self, value):
        self._global_writer = value

    @property
    def reader(self) -> asyncio.StreamReader:
        return self._global_reader

    @reader.setter
    def reader(self, value):
        self._global_reader = value

    @property
    def chat_id(self):
        return self._chat_id

    @chat_id.setter
    def chat_id(self, value):
        self._chat_id = value

    @property
    def bot(self):
        return self._bot

    @bot.setter
    def bot(self, value) -> AsyncTeleBot:
        self._bot = value

    @property
    def lock(self):
        return self._lock

    async def set_socket_manager(self, value):
        async with self._lock:
            self._socket_manager = value

    async def get_socket_manager(self):
        return self._socket_manager

    async def set_writer(self, value):
        async with self._lock:
            self.writer = value

    async def set_reader(self, value):
        async with self._lock:
            self.reader = value

    async def set_bot(self, value):
        async with self._lock:
            self.bot = value

    async def set_chat_id(self, value):
        async with self._lock:
            self.chat_id = value


config = Config()
