import json

from libs.OutMessageCommands.ICommand import ICommand
from libs.logger import logger
from libs.config import config
from libs.OutMessageManager import OutMessageManager


class CloseCommand(ICommand):

    async def execute(self, message: str) -> bool:
        try:
            message = OutMessageManager().close_command_format(message)
            if message == {}:
                return False
            message_to_send = json.dumps(message) + "\n"
            config.writer.write(message_to_send.encode("utf-8"))
            await config.writer.drain()
            return True
        except Exception as e:
            logger.error(f"Error en Close Command: {e}")
            return False
