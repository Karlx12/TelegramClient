import os
import logging

log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logger = logging.getLogger("TelegramClient")
levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
# Configura el nivel de log
level_file = os.getenv("LOG_LEVEL_FILE", "INFO")
level_console = os.getenv("LOG_LEVEL_CONSOLE", "INFO")
logger.setLevel(levels[level_console])

# Configura el archivo de log
file_handler = logging.FileHandler("./logs/telegramserver.log")
file_handler.setLevel(levels[level_file])

# Configura un formato personalizado para los registros
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(levels[level_console])


console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
