import asyncio
from libs.SocketManager.SocketManager import SocketManager
from libs.config import config
from libs.TelegramBot import start_bot


async def main():
    await config.set_socket_manager(SocketManager())
    socket_manager = await config.get_socket_manager()

    # Conectar el cliente al servidor socket
    await socket_manager.connect("localhost", 8080)

    await asyncio.gather(
        socket_manager.receive_messages(),  # Recibe mensajes del socket
        start_bot(),  # Ejecuta el bot de Telegram
    )


if __name__ == "__main__":
    asyncio.run(main())
