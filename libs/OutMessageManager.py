from libs.logger import logger
import json


class OutMessageManager:
    @staticmethod
    def parse_message(message: str, expected_args: int) -> list:
        """Convierte un mensaje en una lista de argumentos "
        "con una cantidad mínima esperada."""
        list_args = message.split(" ")
        if len(list_args) < expected_args:
            logger.debug(
                "El mensaje no tiene los campos mínimos esperados "
                + f"({expected_args})"
            )
            return []
        return list_args[1:]  # Excluir el comando inicial

    @staticmethod
    def send_command_format(message: str) -> dict:
        """Formatea un mensaje de tipo 'send_order' a un diccionario válido"""
        list_args = OutMessageManager.parse_message(message, 7)
        if not list_args:
            return {}

        command = "send_order"
        client_id = list_args[0] if len(list_args) > 0 else ""
        logger.debug(f"client_id: {client_id}")
        magic = (
            int(list_args[1])
            if len(list_args) > 1 and list_args[1].isdigit()
            else 0
        )
        side = list_args[2] if len(list_args) > 2 else "buy"
        symbol = list_args[3] if len(list_args) > 3 else ""
        price = (
            float(list_args[4]) if len(list_args) > 4 and list_args[4] else 0.0
        )
        volume = (
            float(list_args[5]) if len(list_args) > 5 and list_args[5] else 0.0
        )
        takeprofit = (
            float(list_args[6]) if len(list_args) > 6 and list_args[6] else 0.0
        )
        stoploss = (
            float(list_args[7]) if len(list_args) > 7 and list_args[7] else 0.0
        )

        logger.debug(f"args: {list_args}")

        if side.lower() not in ["buy", "sell"]:
            logger.error("El 'side' de la orden no es válido")
            return {}

        side = 0 if side.lower() == "buy" else 1

        return json.loads(
            json.dumps(
                {
                    "command": command,
                    "client_id": client_id,
                    "type_client": "Telegram",
                    "order": {
                        "side": int(side),
                        "magic": int(magic),
                        "symbol": str.upper(symbol),
                        "price": price,
                        "volume": volume,
                        "takeProfit": takeprofit,
                        "stopLoss": stoploss,
                        "slippage": 1.0,
                        "comment": "",
                    },
                },
                separators=(",", ":"),
            )
        )

    @staticmethod
    def close_command_format(message: str) -> dict:
        """Formatea un mensaje de tipo 'close_order' a un diccionario válido"""
        list_args = OutMessageManager.parse_message(message, 4)
        if not list_args:
            return {}

        command = "close_order"
        client_id, magic, symbol = list_args[:3]
        logger.debug(f"client_id: {client_id}")

        if not client_id or not magic.isdigit() or not symbol:
            logger.error("El 'client_id', 'magic' o 'symbol' no son válidos")
            return {}

        return json.loads(
            json.dumps(
                {
                    "command": command,
                    "client_id": client_id,
                    "magic": int(magic),
                    "symbol": symbol.upper(),
                },
                separators=(",", ":"),
            )
        )

    @staticmethod
    def info_command_format(message: str) -> dict:
        """Formatea un mensaje de tipo 'get_info_account' a un diccionario"""
        list_args = OutMessageManager.parse_message(message, 2)
        if not list_args:
            return {}

        command = "get_info_account"
        client_id = list_args[0]
        logger.debug(f"client_id: {client_id}")

        if not client_id:
            logger.error("El 'client_id' no es válido")
            return {}

        return json.loads(
            json.dumps(
                {
                    "command": command,
                    "client_id": client_id,
                },
                separators=(",", ":"),
            )
        )

    @staticmethod
    def open_positions_command_format(message: str) -> dict:
        """
        Formatea un mensaje de tipo 'open_positions' a un diccionario válido
        """
        list_args = OutMessageManager.parse_message(message, 2)
        if not list_args:
            return {}

        command = "get_open_positions"
        client_id = list_args[0]
        logger.debug(f"client_id: {client_id}")

        if not client_id:
            logger.error("El 'client_id' no es válido")
            return {}

        return json.loads(
            json.dumps(
                {
                    "command": command,
                    "client_id": client_id,
                },
                separators=(",", ":"),
            )
        )

    @staticmethod
    def margin_level_command_format(message: str) -> dict:
        """
        Formatea un mensaje de tipo 'margin_level' a un diccionario válido
        """
        list_args = OutMessageManager.parse_message(message, 2)
        if not list_args:
            return {}

        command = "margin_level"
        client_id = list_args[0]
        logger.debug(f"client_id: {client_id}")

        if not client_id:
            logger.error("El 'client_id' no es válido")
            return {}

        return json.loads(
            json.dumps(
                {
                    "command": command,
                    "client_id": client_id,
                },
                separators=(",", ":"),
            )
        )

    @staticmethod
    def close_all_command_format(message: str) -> dict:
        """Formatea un mensaje de tipo 'close_all' a un diccionario válido"""
        list_args = OutMessageManager.parse_message(message, 2)
        if not list_args:
            return {}

        command = "close_all_order"
        client_id = list_args[0]
        logger.debug(f"client_id: {client_id}")

        if not client_id:
            logger.error("El 'client_id' no es válido")
            return {}

        return json.loads(
            json.dumps(
                {
                    "command": command,
                    "client_id": client_id,
                },
                separators=(",", ":"),
            )
        )

    @staticmethod
    def ping_command_format() -> dict:
        """Formatea un mensaje de tipo 'ping' a un diccionario válido"""
        return json.loads(
            json.dumps(
                {
                    "command": "ping",
                    "name": "health_ping",
                },
                separators=(",", ":"),
            )
        )
