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
            if not data or data == b"":
                continue
            logger.debug(f"Received: {data.decode()}")
            try:
                message_loaded = json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"Error al decodificar mensaje: {e}")
                continue
            try:
                new_message = (
                    await InMessageManager().format_recieved_messages(
                        message_loaded
                    )
                )
            except Exception as e:
                logger.error(f"Error al formatear mensaje: {e}")
                continue
            logger.debug(
                "New message: " + new_message.encode("utf-8").decode("utf-8")
            )
            try:
                client_id = message_loaded.get("client_id")
                chat_id = config.chat_client_pairs.get(client_id)
                if new_message and chat_id:
                    await config.bot.send_message(chat_id, new_message)
            except Exception as e:
                logger.error(f"Error al enviar mensaje: {e}")

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
