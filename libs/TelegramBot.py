import asyncio
import os
from libs.OutMessageCommands import (
    CloseCommand,
    InfoCommand,
    SendCommand,
    CloseAllCommand,
    MarginLevelCommand,
    OpenPositionsCommand,
)
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, BotCommand
from telebot.asyncio_handler_backends import (
    BaseMiddleware,
    CancelUpdate,
    ContinueHandling,
)
from libs.logger import logger
from libs.config import config

TOKEN = os.getenv("BOT_TOKEN", "")
bot = AsyncTeleBot(TOKEN)
CHAT_ID_VALIDS = os.getenv("CHAT_ID", "").split(",")
CHAT_ID_VALIDS = list(map(int, CHAT_ID_VALIDS))
logger.debug(f"CHAT_ID_VALIDS: {CHAT_ID_VALIDS}")

COMMANDS = [
    BotCommand("start", "Start Bot"),
    BotCommand("help", "List of commands"),
    BotCommand("send", "Send order to server"),
    BotCommand("close", "Close an order"),
    BotCommand("info", "Get info of the account"),
    BotCommand("maginlevel", "Get the margin level of the account"),
    BotCommand("closeall", "Close all orders"),
    BotCommand("openpositions", "Get the open orders"),
]

commands = {
    "send": SendCommand.SendCommand(),
    "close": CloseCommand.CloseCommand(),
    "info": InfoCommand.InfoCommand(),
    "margin_level": MarginLevelCommand.MarginLevelCommand(),
    "close_all": CloseAllCommand.CloseAllCommand(),
    "open_positions": OpenPositionsCommand.OpenPositionsCommand(),
}


# Middleware para verificar la validez del chat
class CheckChatMiddleware(BaseMiddleware):
    def __init__(self):
        self.update_types = ["message"]

    async def pre_process(self, message: Message, data):
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

    async def pre_process(self, message: Message, data):
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
    async def send_welcome(message: Message):
        logger.info("response welcome")
        await bot.reply_to(message, "Bienvenido, todo en orden")
        return ContinueHandling()

    @bot.message_handler(commands=["send"])
    async def handle_send_message(message: Message):
        await execute_command("send", message.text, message)

    @bot.message_handler(commands=["close"])
    async def handle_close_message(message: Message):
        await execute_command("close", message.text, message)

    @bot.message_handler(commands=["info"])
    async def handle_info_message(message: Message):
        await execute_command("info", message.text, message)

    @bot.message_handler(commands=["margin_level"])
    async def handle_margin_level_message(message: Message):
        await execute_command("margin_level", message.text, message)

    @bot.message_handler(commands=["close_all"])
    async def handle_close_all_message(message: Message):
        confirmation_message = await bot.reply_to(
            message,
            "¿Estás seguro de que deseas cerrar todas las órdenes? "
            + "Responde con 'yes' o 'no'.",
        )
        bot.register_next_step_handler(
            confirmation_message, process_close_all_confirmation, message
        )

    async def process_close_all_confirmation(
        confirmation_message: Message, original_message: Message
    ):
        if confirmation_message.text.lower() == "yes":
            await execute_command(
                "close_all", original_message.text, original_message
            )
        else:
            await bot.reply_to(original_message, "Operación cancelada.")

    @bot.message_handler(commands=["open_positions"])
    async def handle_open_positions_message(message: Message):
        await execute_command("open_positions", message.text, message)

    @bot.message_handler(commands=["help"])
    async def handle_help_message(message: Message):
        await bot.reply_to(
            message,
            "/send [client_id] [magic] [side: buy/sell] [symbol] [price] "
            + "[volume] [takeprofit (opcional)] [stoploss (opcional)]\n"
            + "/close [client_id] [magic] [symbol]\n"
            + "/info [client_id]\n",
        )


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
        await bot.polling(skip_pending=True, non_stop=True)
    except Exception as e:
        logger.warning(f"Proceso detenido antes de tiempo: {e}")
    finally:
        logger.info("Cerrando sesión")
        await bot.close_session()


if __name__ == "__main__":
    asyncio.run(start_bot())
