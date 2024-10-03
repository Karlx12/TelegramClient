import asyncio
from libs.TelegramBot import socket_manager
from libs.TelegramBot import start_bot

socket_manager = socket_manager


async def main():
    # Instancia del SocketManager ya creada en telegram_bot
    global socket_manager

    # Conectar el cliente al servidor socket
    await socket_manager.connect("localhost", 8080)

    await asyncio.gather(
        socket_manager.receive_messages(),  # Recibe mensajes del socket
        start_bot(),  # Ejecuta el bot de Telegram
    )


if __name__ == "__main__":
    asyncio.run(main())
