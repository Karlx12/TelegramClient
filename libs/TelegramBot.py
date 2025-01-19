import asyncio
import os

from aiohttp import ClientError
from libs.OutMessageCommands import (
    CloseCommand,
    InfoCommand,
    SendCommand,
    CloseAllCommand,
    MarginLevelCommand,
    OpenPositionsCommand,
    PingCommand,  # Add this line
    SetPairCommand,  # Add this line
)
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, BotCommand
from telebot.asyncio_handler_backends import BaseMiddleware, CancelUpdate
from libs.logger import logger
from libs.config import config

TOKEN = os.getenv("BOT_TOKEN", "")
bot = AsyncTeleBot(TOKEN)
CHAT_ID_VALIDS = os.getenv("CHAT_ID", "").split(",")
CHAT_ID_VALIDS = list(map(int, CHAT_ID_VALIDS))
logger.debug(f"CHAT_ID_VALIDS: {CHAT_ID_VALIDS}")
user_confirmation_state = {}
COMMANDS = [
    BotCommand("start", "Start Bot"),
    BotCommand("help", "List of commands"),
    BotCommand("setpair", "Set the pair of chat_id and client_id"),
    BotCommand("ping", "Ping the server"),
    BotCommand("send", "Send order to server"),
    BotCommand("close", "Close an order"),
    BotCommand("info", "Get info of the account"),
    BotCommand("marginlevel", "Get the margin level of the account"),
    BotCommand("closeall", "Close all orders"),
    BotCommand("openpositions", "Get the open orders"),
]

commands = {
    "ping": PingCommand.PingCommand(),
    "send": SendCommand.SendCommand(),
    "close": CloseCommand.CloseCommand(),
    "info": InfoCommand.InfoCommand(),
    "margin_level": MarginLevelCommand.MarginLevelCommand(),
    "close_all": CloseAllCommand.CloseAllCommand(),
    "open_positions": OpenPositionsCommand.OpenPositionsCommand(),
    "set_pair": SetPairCommand.SetPairCommand(),
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
        retries = 0
        delay = 2  # Tiempo inicial de espera antes de reintentar
        success = False
        max_retries = 3

        while retries < max_retries and not success:
            try:
                # Ejecuta el comando correspondiente
                if await commands[command_key].execute(message_text):
                    try:
                        # Intenta responder al mensaje
                        await bot.reply_to(reply_message, "Mensaje enviado")
                        success = True
                        logger.info("Mensaje enviado con éxito al servidor")
                        break  # Sale del ciclo si tiene éxito
                    except ClientError as e:
                        retries += 1  # Incrementa el número de reintentos
                        logger.warning(f"Error al enviar mensaje: {e}")
                        if retries == max_retries:
                            await bot.reply_to(
                                reply_message,
                                "Error al enviar mensaje tras varios intentos",
                            )
                        else:
                            await asyncio.sleep(
                                delay
                            )  # Espera antes de reintentar
                            delay *= (
                                2  # Aumenta el tiempo de espera (exponencial)
                            )
                else:
                    # Si la ejecución del comando falla
                    await bot.reply_to(reply_message, "Error en el mensaje")
                    break
            except Exception as e:
                logger.error(f"Error inesperado al ejecutar el comando: {e}")
                await bot.reply_to(
                    reply_message, "Error al ejecutar el comando"
                )
                break  # Sale del ciclo en caso de error no manejado
    else:
        # Si el servidor no está conectado
        await bot.reply_to(reply_message, "No estoy conectado al servidor.")


async def register_handlers():
    global user_confirmation_state

    @bot.message_handler(commands=["start"])
    async def send_welcome(message: Message):
        logger.info("response welcome")
        await bot.reply_to(message, "Bienvenido, todo en orden")

    @bot.message_handler(commands=["send"])
    async def handle_send_message(message: Message):
        await execute_command("send", message.text, message)

    @bot.message_handler(commands=["close"])
    async def handle_close_message(message: Message):
        await execute_command("close", message.text, message)

    @bot.message_handler(commands=["info"])
    async def handle_info_message(message: Message):
        await execute_command("info", message.text, message)

    @bot.message_handler(commands=["marginlevel"])
    async def handle_margin_level_message(message: Message):
        await execute_command("margin_level", message.text, message)

    @bot.message_handler(commands=["closeall"])
    async def handle_close_all_message(message: Message):
        await bot.reply_to(
            message,
            "¿Estás seguro de que deseas cerrar todas las órdenes?"
            + " Awnser: 'yes' or 'no'.",
        )
        # Guardar el estado de espera de confirmación para el usuario
        user_confirmation_state[message.chat.id] = {
            "state": "waiting_for_confirmation",
            "message": message,
        }

    @bot.message_handler(
        func=lambda msg: user_confirmation_state.get(msg.chat.id, {}).get(
            "state"
        )
        == "waiting_for_confirmation"
    )
    async def process_close_all_confirmation(message: Message):
        if message.text.lower() == "yes":
            original_message = user_confirmation_state[message.chat.id][
                "message"
            ]
            await execute_command(
                "close_all", original_message.text, original_message
            )
        else:
            await bot.reply_to(message, "Operación cancelada.")

        user_confirmation_state.pop(message.chat.id, None)

    @bot.message_handler(commands=["openpositions"])
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

    @bot.message_handler(commands=["ping"])
    async def handle_ping_message(message: Message):
        await execute_command("ping", message.text, message)

    @bot.message_handler(commands=["setpair"])
    async def handle_set_pair_message(message: Message):
        chat_id = message.chat.id
        await execute_command(
            "set_pair", message.text + " " + str(chat_id), message
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

    while True:
        try:
            await bot.polling(skip_pending=True, non_stop=True)
        except Exception as e:
            logger.warning(
                f"Error en la conexión, reintentando en 5 segundos: {e}"
            )
            await asyncio.sleep(5)  # Pausa antes de intentar reconectar
        finally:
            logger.info("Cerrando sesión")
            await bot.close_session()
