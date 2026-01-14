"""

----- TELEGRAM NOTIFIER ----- paquete para enviar notificaciones a un bot de telegram

"""
#Importar clases/modulos que se van a exponer
from .notifier_main import TelegramNotifier
from .exceptions import TelegramError

#Definir lo que se importa con "from telegram_notifier import *"
__all__ = ['TelegramNotifier', 'TelegramError']

#Version del paquete
__version__ = '1.0.2'