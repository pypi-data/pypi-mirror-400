"""

Modulo principal para el bot que manda mensajes en Telegram

"""
import requests
import os

from typing import Optional, Dict, Any
from .exceptions import TelegramError

class TelegramNotifier:
    """CLASE PARA ENVIAR MENSAJES POR TELEGRAM"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("TOKEN_TELEGRAM_BOT") #Obtener variable de entorno del sistema

        if not self.token:
            raise TelegramError("Token no encontrado, establezaca TOKEN_TELEGRAM_BOT en variables de entorno del sistema")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        print(self.base_url)

    def send_message(self, text: str, **kwargs) -> Dict[str, Any]:
        chat_id = os.getenv("CHAT_ID_TELEGRAM")

        if not chat_id:
            raise TelegramError("Token no encontrado para chat_id")
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            **kwargs
        }


        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise TelegramError(f"Error al conectar con Telegram: {e}")
        except Exception as e:
            raise TelegramError(f"Error inesperado")
        
    def send_alert(self, message):
        formatted_message = message
        return self.send_message(formatted_message)