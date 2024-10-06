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
