from datetime import datetime
import json


class InMessageManager:
    """
    Clase encargada de formatear los mensajes recibidos desde el servidor
    de sockets y redireccionarlos al bot de Telegram
    """

    # Cargar el archivo JSON con los códigos de error
    with open("error_codes.json") as f:
        ERROR_CODES = json.load(f)

    @staticmethod
    async def format_recieved_messages(message: dict) -> str:
        """Formatea los mensajes recibidos desde el servidor de socket"""

        command = message.get("command", "")

        if command == "send_order_return":
            return await InMessageManager.format_send_order_return(message)
        elif command == "close_order_return":
            return await InMessageManager.format_close_order_return(message)
        elif command == "close_all_return":
            return await InMessageManager.format_close_all_return(message)
        elif command == "open_positions_return":
            return await InMessageManager.format_open_positions_return(message)
        elif command == "get_info_account_return":
            return await InMessageManager.format_account_info_return(message)
        elif command == "margin_level_return":
            return await InMessageManager.format_margin_level_return(message)
        elif command == "closed_positions_return":
            return await InMessageManager.format_closed_positions_return(
                message
            )

        else:
            return "Comando no reconocido."

    @staticmethod
    async def format_send_order_return(message: dict) -> str:
        """Formatea el mensaje de tipo send_order_return"""
        client_id = message.get("client_id", "N/A")
        price = message.get("price", 0.0)
        side = message.get("side", "N/A")
        status_code = message.get("status_code", "N/A")
        status_message = InMessageManager.ERROR_CODES.get(
            str(status_code), "Código de estado no reconocido"
        )
        symbol = message.get("symbol", "N/A")
        timestamp = message.get("timestamp", 0)
        magic = message.get("magic", "N/A")
        volume = message.get("volume", 0.0)

        trade_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        side_text = "Compra" if side == 0 else "Venta"

        return (
            f"📊 *Orden {side_text}*\n"
            f"Cliente: {client_id}\n"
            f"Símbolo: {symbol}\n"
            f"Precio: {price}\n"
            f"Volumen: {volume}\n"
            f"Número Mágico: {magic}\n"
            f"Fecha: {trade_time}\n"
            f"Estado: {status_message}"
        )

    @staticmethod
    async def format_close_order_return(message: dict) -> str:
        """Formatea el mensaje de tipo close_order_return"""
        client_id = message.get("client_id", "N/A")
        symbol = message.get("symbol", "N/A")
        status_code = message.get("status_code", "N/A")
        timestamp = message.get("timestamp", 0)
        magic = message.get("magic", "N/A")
        volume = message.get("volume_closed", 0.0)

        close_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        status_message = (
            "Cierre exitoso" if status_code == 0 else "Error en cierre"
        )

        return (
            f"🔒 *Orden Cerrada*\n"
            f"Cliente: {client_id}\n"
            f"Símbolo: {symbol}\n"
            f"Volumen: {volume}\n"
            f"Número Mágico: {magic}\n"
            f"Fecha de cierre: {close_time}\n"
            f"Estado: {status_message}"
        )

    @staticmethod
    async def format_close_all_return(message: dict) -> str:
        """
        Formatea el mensaje de tipo close_all_return que incluye una
        lista de operaciones cerradas
        """
        client_id = message.get("client_id", "N/A")
        trades = message.get("trades", [])
        close_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        trade_summaries = []
        for trade in trades:
            magic = trade.get("magic", "N/A")
            symbol = trade.get("symbol", "N/A")
            volume = trade.get("volume", 0.0)
            close_price = trade.get("price", 0.0)
            trade_summaries.append(
                f"Número Mágico: {magic}, Símbolo: {symbol},"
                f" Volumen: {volume}, Precio de cierre: {close_price}"
            )

        trades_text = "\n".join(trade_summaries)

        return (
            f"🔒 *Cierre de Todas las Órdenes*\n"
            f"Cliente: {client_id}\n"
            f"Fecha de cierre: {close_time}\n"
            f"Órdenes cerradas:\n{trades_text}"
        )

    @staticmethod
    async def format_open_positions_return(message: dict) -> str:
        """Formatea el mensaje de tipo open_positions_return"""
        client_id = message.get("client_id", "N/A")
        positions = message.get("positions", [])
        timestamp = message.get("timestamp", 0)

        open_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        if not positions:
            return (
                f"📂 *Posiciones Abiertas*\n"
                f"Cliente: {client_id}\n"
                f"Fecha de consulta: {open_time}\n"
                f"No hay posiciones abiertas."
            )

        position_summaries = []
        for position in positions:
            magic = position.get("magic", "N/A")
            symbol = position.get("symbol", "N/A")
            volume = position.get("volume", 0.0)
            open_price = position.get("price", 0.0)
            side = position.get("side", "N/A")
            side_text = "Compra" if side == 0 else "Venta"

            position_summaries.append(
                f"Número Mágico: {magic}, Símbolo: {symbol}, "
                + f"Volumen: {volume}, Precio de apertura: {open_price},"
                + f" Tipo: {side_text}"
            )

        positions_text = "\n".join(position_summaries)

        return (
            f"📂 *Posiciones Abiertas*\n"
            f"Cliente: {client_id}\n"
            f"Fecha de consulta: {open_time}\n"
            f"Posiciones:\n{positions_text}"
        )

    @staticmethod
    async def format_account_info_return(message: dict) -> str:
        """Formatea el mensaje de tipo account_info_return"""
        client_id = message.get("client_id", "N/A")
        balance = message.get("balance", 0.0)
        equity = message.get("equity", 0.0)
        free_margin = message.get("free_margin", 0.0)
        currency = message.get("currency", "N/A")
        timestamp = message.get("timestamp", 0)

        account_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return (
            f"🏦 *Información de la Cuenta*\n"
            f"Cliente: {client_id}\n"
            f"Fecha: {account_time}\n"
            f"Balance: {balance} {currency}\n"
            f"Equidad: {equity} {currency}\n"
            f"Margen Libre: {free_margin} {currency}"
        )

    @staticmethod
    async def format_margin_level_return(message: dict) -> str:
        """Formatea el mensaje de tipo margin_level_return"""
        client_id = message.get("client_id", "N/A")
        margin_level = message.get("margin_level", 0.0)
        margin_used = message.get("margin_used", 0.0)
        free_margin = message.get("free_margin", 0.0)
        timestamp = message.get("timestamp", 0)

        margin_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return (
            f"📊 *Nivel de Margen*\n"
            f"Cliente: {client_id}\n"
            f"Fecha: {margin_time}\n"
            f"Nivel de Margen: {margin_level}%\n"
            f"Margen Usado: {margin_used}\n"
            f"Margen Libre: {free_margin}"
        )

    @staticmethod
    async def format_closed_positions_return(message: dict) -> str:
        """Formatea el mensaje de tipo closed_positions_return"""
        client_id = message.get("client_id", "N/A")
        closed_positions = message.get("closed_positions", [])
        timestamp = message.get("timestamp", 0)

        close_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        closed_summaries = []
        for position in closed_positions:
            magic = position.get("magic", "N/A")
            symbol = position.get("symbol", "N/A")
            volume = position.get("volume", 0.0)
            close_price = position.get("close_price", 0.0)
            profit = position.get("profit", 0.0)

            closed_summaries.append(
                f"Número Mágico: {magic}, Símbolo: {symbol},"
                + f" Volumen: {volume}, Precio de cierre: {close_price},"
                + f" Ganancia: {profit}"
            )

        closed_positions_text = "\n".join(closed_summaries)

        return (
            f"🔒 *Posiciones Cerradas*\n"
            f"Cliente: {client_id}\n"
            f"Fecha de cierre: {close_time}\n"
            f"Posiciones cerradas:\n{closed_positions_text}"
        )
