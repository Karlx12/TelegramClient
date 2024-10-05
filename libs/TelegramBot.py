import asyncio
import os
from libs.commands import CloseCommand, InfoCommand, SendCommand
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from telebot.types import Message
from telebot.asyncio_handler_backends import BaseMiddleware, CancelUpdate
from libs.logger import logger
from libs.config import config

TOKEN = os.getenv("BOT_TOKEN", "")
bot = AsyncTeleBot(TOKEN)
CHAT_ID_VALIDS = os.getenv("CHAT_ID", "").split(",")
CHAT_ID_VALIDS = list(map(int, CHAT_ID_VALIDS))
logger.debug(f"CHAT_ID_VALIDS: {CHAT_ID_VALIDS}")

COMMANDS = [
    types.BotCommand("start", "Start Bot"),
    types.BotCommand("help", "List of commands"),
    types.BotCommand("send", "Send order to server"),
    types.BotCommand("close", "Close an order"),
    types.BotCommand("info", "Get info of the account"),
]

commands = {
    "send": SendCommand.SendCommand(),
    "close": CloseCommand.CloseCommand(),
    "info": InfoCommand.InfoCommand(),
}


# Middleware para verificar la validez del chat
class CheckChatMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ["message"]

    async def pre_process(self, message: types.Message, data):
        if message.chat.id not in CHAT_ID_VALIDS:
            logger.warning(f"Chat no valido: {message.chat.id}")
            await bot.send_message(message.chat.id, "Chat no autorizado.")
            return CancelUpdate()
        return

    async def post_process(self, message, data, exception):
        pass


# Middleware para configurar el chat_id en config
class SetChatIDMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ["message"]

    async def pre_process(self, message: types.Message, data):
        if message.chat.id in CHAT_ID_VALIDS:
            logger.debug(f"Chat id: {message.chat.id}")
            config.chat_id = message.chat.id
        return

    async def post_process(self, message, data, exception):
        pass


# Función auxiliar para manejar el envío de mensajes
async def execute_command(command_key, message_text, reply_message: Message):
    if config.writer:
        try:
            if await commands[command_key].execute(message_text):
                await bot.reply_to(reply_message, "Mensaje enviado")
            else:
                await bot.reply_to(reply_message, "Error en el mensaje")
            logger.info("Mensaje enviado con éxito al servidor")
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {e}")
            await bot.reply_to(reply_message, "Error al enviar mensaje")
    else:
        await bot.reply_to(reply_message, "No estoy conectado al servidor.")


async def register_handlers():
    @bot.message_handler(commands=["start", "help"])
    async def send_welcome(message: types.Message):
        logger.info("response welcome")
        await bot.reply_to(message, "Howdy, how are you doing?")

    @bot.message_handler(commands=["send"])
    async def handle_send_message(message: types.Message):
        await execute_command("send", message.text, message)

    @bot.message_handler(commands=["close"])
    async def handle_close_message(message: types.Message):
        await execute_command("close", message.text, message)

    @bot.message_handler(commands=["info"])
    async def handle_info_message(message: types.Message):
        await execute_command("info", message.text, message)


async def start_bot():
    await config.set_bot(bot)

    # Registrar middlewares
    bot.setup_middleware(CheckChatMiddleware())
    bot.setup_middleware(SetChatIDMiddleware())

    # Registrar handlers
    await register_handlers()

    await bot.delete_my_commands(scope=None, language_code=None)
    await asyncio.wait_for(
        bot.set_my_commands(commands=COMMANDS),
        timeout=60,
    )
    try:
        await bot.polling(skip_pending=False)
    except Exception as e:
        logger.warning(f"Proceso detenido antes de tiempo: {e}")
    finally:
        logger.info("Cerrando sesión")
        await bot.close_session()


if __name__ == "__main__":
    asyncio.run(start_bot())
