import asyncio
from libs.SocketManager.SocketManager import SocketManager
from libs.config import config
from libs.TelegramBot import start_bot
from libs.logger import logger


async def main():
    config.chat_client_pairs = (
        {}
    )  # Initialize the chat-client pairs dictionary
    await config.set_socket_manager(SocketManager())
    socket_manager = await config.get_socket_manager()

    while True:
        try:
            # Conectar el cliente al servidor socket
            await socket_manager.connect("localhost", 8080)

            await asyncio.gather(
                socket_manager.receive_messages(),
                start_bot(),
            )
        except Exception as e:
            logger.warning(f"Connection lost, retrying in 5 seconds: {e}")
            await asyncio.sleep(5)  # Pausa antes de intentar reconectar


if __name__ == "__main__":
    asyncio.run(main())
