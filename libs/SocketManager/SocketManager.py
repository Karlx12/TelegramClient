# socket_manager.py
import asyncio
import json
from libs.logger import logger
from libs.config import config
from libs.InMessageManager import InMessageManager


class SocketManager:

    async def connect(self, host: str, port: int):
        """Conecta al servidor socket y guarda el writer y reader"""
        reader, writer = await asyncio.open_connection(host, port)
        await config.set_reader(reader)
        await config.set_writer(writer)
        logger.debug("Connected to server")
        await self.send_register_command()

    async def receive_messages(self):
        """Lee mensajes desde el servidor socket"""
        while True:
            data = await config.reader.readline()
            logger.debug(f"Received: {data.decode()}")
            message_loaded = json.loads(data)
            new_message = await InMessageManager().format_recieved_messages(
                message_loaded
            )
            try:
                if new_message:
                    await config.bot.send_message(config.chat_id, new_message)
            except Exception as e:
                logger.error(f"Error al enviar mensaje: {e}")
            finally:
                await asyncio.sleep(0)

    async def send_message(self, message: str):
        """Envía un mensaje al servidor socket"""
        if config.writer:
            config.writer.write((message + "\n").encode("utf-8"))
            await config.writer.drain()

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
