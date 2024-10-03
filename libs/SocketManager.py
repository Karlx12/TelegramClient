# socket_manager.py
import asyncio
from asyncio import StreamReader, StreamWriter
import json
from libs.logger import logger


class SocketManager:
    def __init__(self):
        self.writer: StreamWriter = None
        self.reader: StreamReader = None

    async def connect(self, host: str, port: int):
        """Conecta al servidor socket y guarda el writer y reader"""
        self.reader, self.writer = await asyncio.open_connection(host, port)
        await self.send_register_command()

    async def send_message(self, message: str):
        """Envía un mensaje al servidor socket"""
        if self.writer:
            self.writer.write((message + "\n").encode("utf-8"))
            await self.writer.drain()

    async def receive_messages(self):
        """Lee mensajes desde el servidor socket"""
        while True:
            data = await self.reader.readline()
            logger.debug(f"Received: {data.decode()}")
            await asyncio.sleep(0)

    async def send_register_command(self):
        """Envía el comando de registro al servidor socket"""
        LOGIN = json.dumps(
            {
                "command": "register",
                "type_client": "Telegram",
                "name": "Telegram_bot",
            }
        )
        await self.send_message(LOGIN)
