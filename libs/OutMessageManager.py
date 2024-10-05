from libs.logger import logger


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
        list_args = OutMessageManager.parse_message(message, 6)
        if not list_args:
            return {}

        command = "send_order"
        client_id = list_args[0] if len(list_args) > 0 else ""
        side = list_args[1] if len(list_args) > 1 else "buy"
        symbol = list_args[2] if len(list_args) > 2 else ""
        price = (
            float(list_args[3]) if len(list_args) > 3 and list_args[3] else 0.0
        )
        volume = (
            float(list_args[4]) if len(list_args) > 4 and list_args[4] else 0.0
        )
        takeprofit = (
            float(list_args[5]) if len(list_args) > 5 and list_args[5] else 0.0
        )
        stoploss = (
            float(list_args[6]) if len(list_args) > 6 and list_args[6] else 0.0
        )

        logger.debug(f"args: {list_args}")

        if side.lower() not in ["buy", "sell"]:
            logger.error("El 'side' de la orden no es válido")
            return {}

        side = 0 if side.lower() == "buy" else 1

        return {
            "command": command,
            "client_id": client_id,
            "type_client": "Telegram",
            "order": {
                "side": int(side),
                "symbol": symbol,
                "price": price,
                "volume": volume,
                "takeProfit": takeprofit,
                "stopLoss": stoploss,
                "slippage": 1.0,
                "commet": "Order from Telegram",
            },
        }

    @staticmethod
    def close_command_format(message: str) -> dict:
        """Formatea un mensaje de tipo 'close_order' a un diccionario válido"""
        list_args = OutMessageManager.parse_message(message, 4)
        if not list_args:
            return {}

        command = "close_order"
        client_id, symbol, trade_id = list_args[:3]

        if not client_id or not trade_id.isdigit() or not symbol:
            logger.error(
                "El 'client_id', 'trade_id' o 'symbol' no son válidos"
            )
            return {}

        return {
            "command": command,
            "client_id": client_id,
            "symbol": symbol.upper(),
            "trade_id": int(trade_id),
        }

    @staticmethod
    def info_command_format(message: str) -> dict:
        """Formatea un mensaje de tipo 'get_info_account' a un diccionario"""
        list_args = OutMessageManager.parse_message(message, 2)
        if not list_args:
            return {}

        command = "get_info_account"
        client_id = list_args[0]

        if not client_id:
            logger.error("El 'client_id' no es válido")
            return {}

        return {
            "command": command,
            "client_id": client_id,
        }
