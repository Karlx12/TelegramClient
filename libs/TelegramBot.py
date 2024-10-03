import asyncio
import os
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from libs.logger import logger
from libs.SocketManager import SocketManager


TOKEN = os.getenv("BOT_TOKEN", "")
bot: AsyncTeleBot = AsyncTeleBot(TOKEN)
CHAT_ID_VALIDS = os.getenv("CHAT_ID", "").split(",")
CHAT_ID_VALIDS = list(map(int, CHAT_ID_VALIDS))
logger.debug(f"CHAT_ID_VALIDS: {CHAT_ID_VALIDS}")
COMMANDS = [
    types.BotCommand("start", "Start Bot"),
    types.BotCommand("help", "List of commands"),
    types.BotCommand("send", "Send order to server"),
    types.BotCommand("close", "Close an order"),
    types.BotCommand("info", "Get info of the account"),
    # types.BotCommand("status", "Check status of server"),
    # types.BotCommand("list", "List all orders"),
    # types.BotCommand("list_open", "List all open orders"),
]

# Instancia global del SocketManager (la compartimos)
socket_manager = SocketManager()


@bot.message_handler(commands=["start", "help"])
async def send_welcome(message):
    logger.info("response welcome")
    await bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(commands=["send"])
async def handle_message(message: types.Message):
    if socket_manager.writer:
        # Enviar mensaje al servidor socket usando el SocketManager

        await message.reply(f"Mensaje enviado: {message.text}")
    else:
        await message.reply("No estoy conectado al servidor.")


async def start_bot():
    await bot.delete_my_commands(scope=None, language_code=None)
    await asyncio.wait_for(
        bot.set_my_commands(commands=COMMANDS),
        timeout=60,
    )
    try:
        await bot.polling(skip_pending=False)
    except Exception:
        logger.warning("Proceso detenido antes de tiempo")
    finally:
        logger.info("Cerrando sesion")
        await bot.close_session()
