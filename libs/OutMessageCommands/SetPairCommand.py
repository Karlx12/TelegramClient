from libs.config import config
from libs.OutMessageCommands.ICommand import ICommand
from libs.logger import logger


class SetPairCommand(ICommand):

    async def execute(self, message: str) -> bool:
        try:
            logger.debug(f"Set pair: {message}")
            client_id, chat_id = message.split()
            config.chat_client_pairs[client_id] = chat_id
            logger.info(f"Set pair: {client_id} -> {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting chat-client pair: {e}")
            return False
