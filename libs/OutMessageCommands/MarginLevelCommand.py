from libs.config import config
import json
from libs.OutMessageCommands.ICommand import ICommand
from libs.logger import logger
from libs.OutMessageManager import OutMessageManager


class MarginLevelCommand(ICommand):

    async def execute(self, message: str) -> bool:
        try:
            message = OutMessageManager().margin_level_command_format(message)
            if message == {}:
                return False
            message_to_send = json.dumps(message) + "\n"
            config.writer.write(message_to_send.encode("utf-8"))
            await config.writer.drain()
            return True
        except Exception as e:
            logger.error(f"Error en Info Command: {e}")
            return False
