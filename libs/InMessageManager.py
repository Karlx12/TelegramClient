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
        elif command == "close_all_order_return":
            return await InMessageManager.format_close_all_return(message)
        elif command == "open_positions_return":
            return await InMessageManager.format_open_positions_return(message)
        elif command == "account_info_return":
            return await InMessageManager.format_account_info_return(message)
        elif command == "pong":
            return await InMessageManager.pong_return(message)
        elif command == "info":
            return await InMessageManager.info_message_format(message)
        elif command == "error":
            return await InMessageManager.format_error_message(message)
        else:
            return "Comando no reconocido."

    @staticmethod
    async def format_error_message(message: dict) -> str:
        """Formatea el mensaje de tipo error"""
        error_message = message.get("message", "Error desconocido")
        return f"❌ *Error*\nMensaje: {error_message}"

    @staticmethod
    async def pong_return(message: dict) -> str:
        """Recibe el pong de alguna aplicación"""
        client_id = message.get("client_id", "N/A")
        balance = message.get("balance", 0.0)
        responded = "Sí" if message.get("responded", {}) else "No"

        return (
            f"🏓 *Pong Recibido*\n"
            f"Cliente: `{client_id}`\n"
            f"Balance: `{balance}`\n"
            f"Respondido: `{responded}`"
        )

    @staticmethod
    async def format_send_order_return(message: dict) -> str:
        """Formatea el mensaje de tipo send_order_return"""
        client_id = message.get("client_id", "N/A")
        price = message.get("price", 0.0)
        side = int(message.get("side", None))
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
            f"Cliente: `{client_id}`\n"
            f"Símbolo: `{symbol}`\n"
            f"Precio: `{price}`\n"
            f"Volumen: `{volume}`\n"
            f"Número Mágico: `{magic}`\n"
            f"Fecha: `{trade_time}`\n"
            f"Estado: `{status_message}`"
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
        result = message.get("result", 0.0)
        side = int(message.get("side", None))

        close_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        status_message = (
            "Cierre exitoso" if status_code == 0 else "Error en cierre"
        )
        side_text = "Compra" if side == 0 else "Venta"

        return (
            f"🔒 *Orden de {side_text} Cerrada*\n"
            f"Cliente: `{client_id}`\n"
            f"Símbolo: `{symbol}`\n"
            f"Volumen: `{volume}`\n"
            f"Número Mágico: `{magic}`\n"
            f"Resultado: `{result} usd`\n"
            f"Fecha de cierre: `{close_time}`\n"
            f"Estado: `{status_message}`"
        )

    @staticmethod
    async def format_close_all_return(message: dict) -> str:
        """
        Formatea el mensaje de tipo close_all_return que incluye una
        lista de operaciones cerradas.
        """
        client_id = message.get("client_id", "N/A")
        orders = message.get("orders", [])
        close_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        order_summaries = []
        for order in orders:
            magic = order.get("magic", "N/A")
            symbol = order.get("symbol", "N/A")
            volume_closed = order.get("volume_closed", 0.0)
            close_price = order.get("price", 0.0)
            result = order.get("result", 0.0)
            order_summaries.append(
                f"Número Mágico: `{magic}`, Símbolo: `{symbol}`,"
                + f" Volumen cerrado: `{volume_closed}`,"
                + f" Precio de cierre: `{close_price}`,"
                + f" Resultado: `{result} usd`"
            )

        orders_text = "\n".join(order_summaries)

        return (
            f"🔒 *Cierre de Todas las Órdenes*\n"
            f"Cliente: `{client_id}`\n"
            f"Fecha de cierre: `{close_time}`\n"
            f"Órdenes cerradas:\n{orders_text}"
        )

    @staticmethod
    async def format_open_positions_return(message: dict) -> str:
        """Formatea el mensaje de tipo open_positions_return"""
        client_id = message.get("client_id", "N/A")
        positions = message.get("open_trades", [])
        timestamp = message.get("timestamp", 0)

        open_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        if not positions:
            return (
                f"📂 *Posiciones Abiertas*\n"
                f"Cliente: `{client_id}`\n"
                f"Fecha de consulta: `{open_time}`\n"
                f"No hay posiciones abiertas."
            )

        position_summaries = []
        for position in positions:
            magic = position.get("magic", "N/A")
            symbol = position.get("symbol", "N/A")
            volume = position.get("volume", 0.0)
            open_price = position.get("price", 0.0)
            side = position.get("type", "N/A")
            side_text = "Compra" if side == 0 else "Venta"

            position_summaries.append(
                f"Número Mágico: `{magic}`, Símbolo: `{symbol}`, "
                f"Volumen: `{volume}`, Precio de apertura: `{open_price}`, "
                f"Tipo: `{side_text}`"
            )

        positions_text = "\n".join(position_summaries)

        return (
            f"📂 *Posiciones Abiertas*\n"
            f"Cliente: `{client_id}`\n"
            f"Fecha de consulta: `{open_time}`\n"
            f"Posiciones:\n{positions_text}"
        )

    @staticmethod
    async def format_account_info_return(message: dict) -> str:
        """Formatea el mensaje de tipo account_info_return"""
        client_id = message.get("client_id", "N/A")
        balance = message.get("balance", 0.0)
        equity = message.get("equity", 0.0)
        margin = message.get("margin", 0.0)
        free_margin = message.get("freeMargin", 0.0)
        currency = message.get("currency", "USD")
        timestamp = message.get("timestamp", 0)

        account_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return (
            f"🏦 *Información de la Cuenta*\n"
            f"Cliente: `{client_id}`\n"
            f"Fecha: `{account_time}`\n"
            f"Balance: `{balance} {currency}`\n"
            f"Equidad: `{equity} {currency}`\n"
            f"Margen: `{margin} {currency}`\n"
            f"Margen Libre: `{free_margin} {currency}`"
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
                f"Número Mágico: `{magic}`, Símbolo: `{symbol}`,"
                + f" Volumen: `{volume}`, Precio de cierre: `{close_price}`,"
                + f" Ganancia: `{profit}`"
            )

        closed_positions_text = "\n".join(closed_summaries)

        return (
            f"🔒 *Posiciones Cerradas*\n"
            f"Cliente: `{client_id}`\n"
            f"Fecha de cierre: `{close_time}`\n"
            f"Posiciones cerradas:\n{closed_positions_text}"
        )

    @staticmethod
    def info_message_format(message: str) -> dict:
        message = message.get("message", "N/A")
        return message
